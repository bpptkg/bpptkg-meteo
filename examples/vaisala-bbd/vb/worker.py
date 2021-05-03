import logging

from meteo.db.ops import bulk_insert
from meteo.parser.fields import FIELDS_MAPPING
from meteo.parser.vaisala import VaisalaParser

from . import models

logger = logging.getLogger(__name__)


def process_lines(timestamp, lines):
    """
    Process lines block associated with sampled data.
    """

    # Create entry container.
    entry = dict([
        (v['name'], None) for k, v in FIELDS_MAPPING.items()
    ])

    parser = VaisalaParser()
    for line in lines:
        s = parser.parse(line)
        for comp in s['components']:
            entry[comp['name']] = comp['value']

    entry['timestamp'] = timestamp

    logger.debug('Payload to insert: %s', entry)
    try:
        bulk_insert(models.engine, models.Babadan, [entry, ])
        logger.info('Insert to database succeed.')
    except Exception as e:
        # For now, if insert failed, just ignore the error.
        logger.error('Database insert error.')
        logger.error(e)
