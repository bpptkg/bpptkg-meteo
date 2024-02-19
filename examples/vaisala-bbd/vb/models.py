import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from meteo.models.base import Base  # noqa
from meteo.models.bbd import Babadan  # noqa
from meteo.models.jro import JurangJero  # noqa
from meteo.models.lbh import Labuhan  # noqa
from meteo.models.kla import Klatakan  # noqa

from . import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_ENGINE, poolclass=NullPool)

RECONNECT_TIMEOUT = 30

if settings.MIGRATED:
    while True:
        try:
            Base.prepare(engine, reflect=True)
            break
        except Exception:
            logger.error(
                "Can't connect to MySQL server {}. Trying in {}s...".format(
                    settings.DATABASE_ENGINE, RECONNECT_TIMEOUT
                )
            )
            time.sleep(RECONNECT_TIMEOUT)
