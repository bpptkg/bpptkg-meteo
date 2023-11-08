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
    Run Vaisala Jurang Jero acquisition.
    """
    logging.config.dictConfig(create_log_config("jurangjero.log"))

    logger.info("Initiating app...")
    lockfile = os.path.join(settings.RUN_DIR, "jurangjero.lock")
    app = App(lockfile=lockfile, station=settings.Station.JURANGJERO.value)
    app.run()

    logger.info("App exiting.")


if __name__ == "__main__":
    main()
