import datetime
import logging
import telnetlib
import threading

import pytz

from meteo.singleton import SingleInstance

from . import settings
from .worker import process_lines

logger = logging.getLogger(__name__)


class App(SingleInstance):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):

        data = []
        last_read = datetime.datetime.now(pytz.timezone(settings.TIMEZONE))
        while True:
            with telnetlib.Telnet(
                    host=settings.TELNET_HOST,
                    port=settings.TELNET_PORT,
                    timeout=settings.TELNET_CONNECT_TIMEOUT) as tn:

                line = tn.read_until(b'\n')
                data.append(line)

                now = datetime.datetime.now(pytz.timezone(settings.TIMEZONE))
                if last_read + datetime.timedelta(seconds=60) < now:
                    last_read = now
                    lines = []
                    worker = threading.Thread(
                        target=process_lines, args=(now, lines))
                    worker.start()
