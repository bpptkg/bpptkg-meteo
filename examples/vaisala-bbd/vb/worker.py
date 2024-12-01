import logging

from meteo.db.ops import bulk_insert
from meteo.parser.fields import FIELDS_MAPPING
from meteo.parser.vaisala import VaisalaParser

from . import models
from .settings import Station

logger = logging.getLogger(__name__)


def parse_entry(timestamp, lines, mode="accumulate"):
    """
    Parse lines block associated with sampled data.

    Parameters
    ----------
    timestamp : str
        Timestamp of the data.
    lines : list
        List of lines that contains the data.
    mode : str
        Rain accumulation mode. Either "replace" or "accumulate".
    """
    # Create entry container.
    entry = dict([(v["name"], None) for k, v in FIELDS_MAPPING.items()])
    parser = VaisalaParser(errors="ignore")
    for line in lines:
        s = parser.parse(line)
        for comp in s["components"]:
            if comp["name"] == "rain_acc":
                if mode == "replace":
                    entry[comp["name"]] = comp["value"]
                else:
                    current_value = comp["value"]
                    if current_value is None:
                        current_value = 0
                    else:
                        current_value = float(current_value)
                    previous_value = entry.get(comp["name"], 0)
                    if previous_value is None:
                        previous_value = 0
                    else:
                        previous_value = float(previous_value)
                    entry[comp["name"]] = previous_value + current_value
            else:
                entry[comp["name"]] = comp["value"]

    entry["timestamp"] = timestamp
    return entry


def process_lines(timestamp, lines, station):
    """
    Process lines block associated with sampled data.
    """
    if station == Station.LABUHAN.value:
        model = models.Labuhan
    elif station == Station.JURANGJERO.value:
        model = models.JurangJero
    elif station == Station.BABADAN.value:
        model = models.Babadan
    elif station == Station.KLATAKAN.value:
        model = models.Klatakan
    elif station == Station.NGEPOS.value:
        model = models.Ngepos
    elif station == Station.SELO.value:
        model = models.Selo
    elif station == Station.JRAKAH.value:
        model = models.Jrakah
    elif station == Station.KALIURANG.value:
        model = models.Kaliurang

    logger.info("Raw lines: %s", repr(lines))
    entry = parse_entry(timestamp, lines, mode="replace")

    logger.info("Payload to insert: %s", entry)
    try:
        bulk_insert(
            models.engine,
            model,
            [
                entry,
            ],
        )
        logger.info("Insert to database succeed.")
    except Exception as e:
        # For now, if insert failed, just ignore the error.
        logger.error("Database insert error.")
        logger.error(e)
