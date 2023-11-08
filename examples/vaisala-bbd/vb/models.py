from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from meteo.models.base import Base  # noqa
from meteo.models.bbd import Babadan  # noqa
from meteo.models.jro import JurangJero  # noqa

from . import settings

engine = create_engine(settings.DATABASE_ENGINE, poolclass=NullPool)

if settings.MIGRATED:
    Base.prepare(engine, reflect=True)
