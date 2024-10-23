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
    Run Vaisala Pos Selo acquisition.
    """
    logging.config.dictConfig(create_log_config("selo.log"))

    logger.info("Initiating app...")
    lockfile = os.path.join(settings.RUN_DIR, "selo.lock")
    app = App(lockfile=lockfile, station=settings.Station.SELO.value)
    app.run()

    logger.info("App exiting.")


if __name__ == "__main__":
    main()
