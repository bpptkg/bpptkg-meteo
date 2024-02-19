import logging

from meteo.db.ops import bulk_insert
from meteo.parser.fields import FIELDS_MAPPING
from meteo.parser.vaisala import VaisalaParser

from . import models
from .settings import Station

logger = logging.getLogger(__name__)


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

    # Create entry container.
    entry = dict([(v["name"], None) for k, v in FIELDS_MAPPING.items()])

    parser = VaisalaParser()
    for line in lines:
        s = parser.parse(line)
        for comp in s["components"]:
            # Get only the latest value for each field by replacing the value if
            # number of each field captured is more than one.
            entry[comp["name"]] = comp["value"]

    entry["timestamp"] = timestamp

    logger.info("Raw lines: %s", lines)

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
