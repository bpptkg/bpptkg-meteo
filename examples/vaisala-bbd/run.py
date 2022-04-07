#!/usr/bin/env python

import logging
import logging.config

from vb import settings
from vb.app import App

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(settings.LOGGING)

    logger.info('Initiating app...')
    app = App(lockfile=settings.LOCKFILE)
    app.run()

    logger.info('App exiting.')


if __name__ == '__main__':
    main()
