from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy.ext.automap import automap_base

Base = automap_base()


class CR6(Base):
    """
    CR6 digitizer data model.

    Weather data from station using CR6 digitizer are saved in this model.
    """
    __tablename__ = 'cr6'

    timestamp = Column('record_timestamp', DateTime, primary_key=True, index=True)
    wind_direction = Column('wind_direction', Float, index=True, nullable=True, comment='Wind direction in degrees.')
    wind_speed = Column('wind_speed', Float, index=True, nullable=True, comment='Average wind speed in km/hour.')
    air_temperature = Column('air_temperature', Float, index=True, nullable=True,
                             comment='Average air temperature in degrees Celsius.')
    air_humidity = Column('air_humidity', Float, index=True, nullable=True, comment='Average air humidity in percent.')
    air_pressure = Column('air_pressure', Float, index=True, nullable=True, comment='Average air pressure in kPa.')
    rainfall = Column('rainfall', Float, index=True, nullable=True, comment='Rainfall in mm.')
    amount = Column('amount', Float, index=True, nullable=True, comment='Average hit amount in hits/cm^2.')
    battery_voltage = Column('battery_voltage', Float, index=True, nullable=True,
                             comment='Average battery voltage in Volt.')
    power_temperature = Column('power_temperature', Float, index=True, nullable=True,
                               comment='Power temperature in degrees Celsius.')
