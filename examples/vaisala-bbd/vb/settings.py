import enum
import os

import sentry_sdk
from decouple import config
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DATA_DIR = os.path.join(STORAGE_DIR, "data")
RUN_DIR = os.path.join(STORAGE_DIR, "run")

DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_ENGINE = config("DATABASE_ENGINE")
MIGRATED = config("MIGRATED", default=True, cast=bool)
TELNET_HOST = config("TELNET_HOST", default="localhost")
TELNET_PORT = config("TELNET_PORT", default=23, cast=int)
TELNET_JURANGJERO_HOST = config("TELNET_JURANGJERO_HOST", default="localhost")
TELNET_JURANGJERO_PORT = config("TELNET_JURANGJERO_PORT", default=23, cast=int)
TELNET_LABUHAN_HOST = config("TELNET_LABUHAN_HOST", default="localhost")
TELNET_LABUHAN_PORT = config("TELNET_LABUHAN_PORT", default=23, cast=int)
TELNET_KLATAKAN_HOST = config("TELNET_KLATAKAN_HOST", default="localhost")
TELNET_KLATAKAN_PORT = config("TELNET_KLATAKAN_PORT", default=23, cast=int)
TELNET_TIMEOUT = config("TELNET_TIMEOUT", default=300, cast=int)
TELNET_CONNECT_TIMEOUT = config("TELNET_CONNECT_TIMEOUT", default=60, cast=int)
TELNET_RECONNECT_LIMIT = config("TELNET_RECONNECT_LIMIT", default=10, cast=int)
TELNET_RECONNECT_TIMEOUT = config("TELNET_RECONNECT_TIMEOUT", default=5, cast=int)

TIMEZONE = config("TIMEZONE", default="Asia/Jakarta")

LOGGING_ROOT = config("LOGGING_ROOT", default=os.path.join(STORAGE_DIR, "logs"))

LOG_LEVEL = config("LOG_LEVEL", default="info").upper()

if DEBUG:
    LOG_LEVEL = "DEBUG"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{asctime} {levelname} {name} {process:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "production": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGGING_ROOT, "vb.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {"handlers": ["console", "production"], "level": LOG_LEVEL},
        "__main__": {
            "handlers": ["console", "production"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

sentry_sdk.init(
    dsn=config("SENTRY_DSN", default=""),
    integrations=[
        SqlalchemyIntegration(),
    ],
)

LOCKFILE = os.path.join(RUN_DIR, "vb.lock")


class Station(enum.Enum):
    """
    List of supported station names.
    """

    BABADAN = "babadan"
    JURANGJERO = "jurangjero"
    LABUHAN = "labuhan"
    KLATAKAN = "klatakan"

    CHOICES = [
        BABADAN,
        JURANGJERO,
        LABUHAN,
        KLATAKAN,
    ]
