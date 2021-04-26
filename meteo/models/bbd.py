from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.ext.automap import automap_base

Base = automap_base()


class Babadan(Base):
    """
    Model to store Vaisala weather data from Babadan station.
    """

    __tablename__ = 'babadan'

    timestamp = Column('timestamp', DateTime, primary_key=True,
                       index=True, autoincrement=False)

    air_temperature = Column('air_temperature', Float,
                             index=True, nullable=True)
    relative_humidity = Column(
        'relative_humidity', Float, index=True, nullable=True)
    air_pressure = Column('air_pressure', Float, index=True, nullable=True)
    internal_temperature = Column(
        'internal_temperature', Float, index=True, nullable=True)

    wind_direction_min = Column(
        'wind_direction_min', Float, index=True, nullable=True)
    wind_direction_avg = Column(
        'wind_direction_avg', Float, index=True, nullable=True)
    wind_direction_max = Column(
        'wind_direction_max', Float, index=True, nullable=True)
    wind_speed_min = Column('wind_speed_min', Float, index=True, nullable=True)
    wind_speed_avg = Column('wind_speed_avg', Float, index=True, nullable=True)
    wind_speed_max = Column('wind_speed_max', Float, index=True, nullable=True)

    rain_acc = Column('rain_acc', Float, index=True, nullable=True)
    rain_duration = Column('rain_duration', Float, index=True, nullable=True)
    rain_intensity = Column('rain_intensity', Float, index=True, nullable=True)
    rain_peak_intensity = Column(
        'rain_peak_intensity', Float, index=True, nullable=True)

    hail_acc = Column('hail_acc', Float, index=True, nullable=True)
    hail_duration = Column('hail_duration', Float, index=True, nullable=True)
    hail_intensity = Column('hail_intensity', Float, index=True, nullable=True)
    hail_peak_intensity = Column(
        'hail_peak_intensity', Float, index=True, nullable=True)

    heating_temperature = Column(
        'heating_temperature', Float, index=True, nullable=True)
    supply_voltage = Column('supply_voltage', Float, index=True, nullable=True)
    ref_voltage = Column('ref_voltage', Float, index=True, nullable=True)
    heating_voltage = Column('heating_voltage', Float,
                             index=True, nullable=True)
    id = Column('id', String(64), index=True, nullable=True)
