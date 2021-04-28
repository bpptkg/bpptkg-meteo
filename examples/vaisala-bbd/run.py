#!/usr/bin/env python

import logging
import logging.config
import os
import sys
import time

from vb import settings
from vb.app import App

from meteo.singleton import SingleInstanceException

logger = logging.getLogger(__name__)


TELNET_RECONNECT_TIMEOUT = 30


def main():
    logging.config.dictConfig(settings.LOGGING)

    try:
        app = App(lockfile=settings.LOCKFILE)
        app.run()
    except (ConnectionError, OSError) as e:
        logger.debug(e)
        logger.error(e)
        logger.info('Reconnecting in {}s'.format(TELNET_RECONNECT_TIMEOUT))
        time.sleep(TELNET_RECONNECT_TIMEOUT)
    except Exception as e:
        logger.error(e)

    os.execv(__file__, sys.argv)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
