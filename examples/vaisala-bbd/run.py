#!/usr/bin/env python

import logging
import logging.config
import os

from vb import settings
from vb.app import App
from vb.utils import create_log_config

logger = logging.getLogger(__name__)


def main():
    """
    Run Vaisala Babadan acquisition.
    """
    logging.config.dictConfig(create_log_config("babadan.log"))

    logger.info("Initiating app...")
    lockfile = os.path.join(settings.RUN_DIR, "babadan.lock")
    app = App(lockfile=lockfile, station=settings.Station.BABADAN.value)
    app.run()

    logger.info("App exiting.")


if __name__ == "__main__":
    main()
