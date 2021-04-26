from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from meteo.models.bbd import Base, Babadan

from . import settings

engine = create_engine(settings.DATABASE_ENGINE, poolclass=NullPool)

if settings.MIGRATED:
    Base.prepare(engine, reflect=True)
