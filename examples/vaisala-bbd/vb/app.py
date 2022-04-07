import datetime
import logging
import telnetlib
import time

import pytz

from meteo.singleton import SingleInstance

from . import settings
from .worker import process_lines

logger = logging.getLogger(__name__)

TELNET_RECONNECT_TIMEOUT = 30


class App(SingleInstance):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        """
        Run the app.
        """
        lines = []
        localtz = pytz.timezone(settings.TIMEZONE)

        last_read = datetime.datetime.now(localtz)
        last_heartbeat = datetime.datetime.now(localtz)

        logger.info(
            "Using telnet server on {host} port {port}".format(
                host=settings.TELNET_HOST,
                port=settings.TELNET_PORT,
            )
        )
        logger.info("Last read timestamp: %s", last_read.isoformat())

        while True:
            try:
                with telnetlib.Telnet(
                    host=settings.TELNET_HOST,
                    port=settings.TELNET_PORT,
                    timeout=settings.TELNET_CONNECT_TIMEOUT,
                ) as tn:

                    line = tn.read_until(b"\n", timeout=60)
                    lines.append(line)

                    logger.debug("Data: %s", line)

                    now = datetime.datetime.now(localtz)

                    if last_heartbeat + datetime.timedelta(seconds=30) < now:
                        try:
                            tn.write(b"\r\n")
                            logger.info("Heartbeat message sent")
                        except Exception as e:
                            logger.error("Error when sending heartbeat message")
                            logger.error(e)
                        last_heartbeat = now

                    if last_read + datetime.timedelta(seconds=60) < now:
                        process_lines(now, lines)

                        lines = []
                        last_read = now
                        logger.info("Last read timestamp: %s", last_read.isoformat())
            except (ConnectionError, OSError) as e:
                logger.error(e)
                logger.info("Reconnecting in {}s".format(TELNET_RECONNECT_TIMEOUT))
                time.sleep(TELNET_RECONNECT_TIMEOUT)
            except Exception as e:
                logger.error(e)
