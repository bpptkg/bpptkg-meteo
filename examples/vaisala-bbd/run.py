#!/usr/bin/env python

import logging
import logging.config

from vb import settings
from vb.app import App

from meteo.singleton import SingleInstanceException

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(settings.LOGGING)

    try:
        app = App(lockfile=settings.LOCKFILE)
        app.run()
    except (ConnectionError, OSError) as e:
        logger.debug(e)
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
