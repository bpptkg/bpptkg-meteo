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
    data = {}
    parser = VaisalaParser()
    for line in lines:
        s = parser.parse(line)
        for comp in s['components']:
            data[comp['name']] = comp['value']

    data['timestamp'] = timestamp

    logger.debug('Payload to insert: %s', data)
    try:
        bulk_insert(models.engine, models.Babadan, data)
        logger.debug('Insert to database succeed.')
    except Exception as e:
        # For now, if insert failed, just ignore the error.
        logger.error('Database insert error.')
        logger.error(e)
