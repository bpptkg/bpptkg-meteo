import os

from .settings import LOG_LEVEL, LOGGING_ROOT


def create_log_config(filename="vb.log"):
    return {
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
                "filename": os.path.join(LOGGING_ROOT, filename),
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
