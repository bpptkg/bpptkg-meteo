import argparse
import csv
import datetime
import io
import logging
import logging.config
import os
import sys
import tempfile
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd
import pytz
import sentry_sdk
from decouple import config
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from meteo.db import sessions
from meteo.models import cr6

if sys.platform != 'win32':
    import fcntl

COLUMNS = [
    'timestamp',
    'record_id',
    'wind_direction',
    'wind_speed',
    'air_temperature',
    'air_humidity',
    'air_pressure',
    'rainfall',
    'amount',
    'battery_voltage',
    'power_temperature',
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LT_FILE = os.path.join(DATA_DIR, 'last')
LOCKFILE = os.path.join(DATA_DIR, 'vaisala.lock')

DEBUG = config('DEBUG', cast=bool, default=False)
SENTRY_DSN = config('SENTRY_DSN', default='')
DATABASE_ENGINE = config('DATABASE_ENGINE', default='')

TIME_ZONE = 'Asia/Jakarta'
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

logger = logging.getLogger(__name__)

# Initialize sentry integrations.
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[SqlalchemyIntegration(), ]
)


class VaisalaAppError(Exception):
    pass


def force_str(s, encoding='utf-8', errors='strict'):
    """
    Force string or bytes s to text string.
    """
    if issubclass(type(s), str):
        return s
    try:
        if isinstance(s, bytes):
            s = str(s, encoding, errors)
        else:
            s = str(s)
    except UnicodeDecodeError as e:
        raise e
    return s


def get_current_time():
    """
    Get time aware now.
    """
    return datetime.datetime.now(pytz.timezone(TIME_ZONE))


class SingleInstanceException(Exception):
    pass


class SingleInstance(object):
    """
    A singleton object that can be instantiated once.

    It is useful if the script is executed by crontab at small amounts of time.

    Reference: https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
    """

    def __init__(self, flavor_id='', lockfile=''):
        self.initialized = False
        if lockfile:
            self.lockfile = lockfile
        else:
            basename = os.path.splitext(os.path.abspath(sys.argv[0]))[0].replace(
                "/", "-").replace(":", "").replace("\\", "-") + '-%s' % flavor_id + '.lock'
            self.lockfile = os.path.normpath(
                tempfile.gettempdir() + '/' + basename)

        logger.debug('SingleInstance lockfile: %s', self.lockfile)
        if sys.platform == 'win32':
            try:
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(self.lockfile, os.O_CREAT |
                                  os.O_EXCL | os.O_RDWR)
            except OSError:
                type, e, tb = sys.exc_info()
                if os.errno == 13:
                    logger.error(
                        'Another instance is already running. Quitting.')
                    raise SingleInstanceException()
                raise
        else:
            self.fp = open(self.lockfile, 'w')
            self.fp.flush()
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, BlockingIOError):
                logger.error('Another instance is already running. Quitting.')
                raise SingleInstanceException()

        self.initialized = True

    def __del__(self):
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            if logger:
                logger.error(e)
            else:
                print('Unloggable error: %s', e)
            sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--engine-url',
        dest='engine_url',
        default='',
        help='SQLAlchemy database engine URL to store meteorology data '
        'e.g. mysql://user:password@127.0.0.1/meteo'
    )
    parser.add_argument(
        '-d', '--dry',
        action='store_true',
        help='Do not insert data to database (dry run).'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Run in debugging mode.'
    )
    return parser.parse_args()


def decode_bytes(data):
    try:
        return data.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        return data


def to_datetime(date_string, date_format=r'%Y-%m-%d %H:%M:%S'):
    date_obj = datetime.datetime.strptime(date_string, date_format)
    return date_obj


def is_valid_date(date_string, **kwargs):
    try:
        date_obj = to_datetime(date_string, **kwargs)
        if date_obj:
            return True
        return False
    except ValueError:
        return False


def get_meteo_data(start, end):
    """
    Get meteorology data from web service.

    Web service IP address is 192.168.9.47. We request the data with toa5 format
    (CSV data format) and using data range mode.
    """
    params = {
        'command': 'DataQuery',
        'uri': 'dl:Table1',
        'format': 'toa5',
        'mode': 'date-range',
        'p1': start,
        'p2': end
    }
    base_url = 'http://192.168.9.47/'
    url = base_url + '?' + urlencode(params)

    logger.debug('Meteorology data web service URL: %s', url)

    with urlopen(url) as url:
        response = url.read()
    return response


def parse_data(path):
    """
    Parse CSV data from response.

    Test the first item in the line if it contains valid date time string. If
    not, ignore the line.
    """
    try:
        path_or_buffer = path.decode('utf-8')
        buf = io.StringIO(path_or_buffer)
        lines = []
        while True:
            line = buf.readline()
            if not line:
                break
            date_string = line.split(',')[0].strip('"')
            if is_valid_date(date_string):
                lines.append(line)
    except (UnicodeDecodeError, AttributeError):
        path_or_buffer = path
        lines = []
        with open(path_or_buffer) as buf:
            while True:
                line = buf.readline()
                if not line:
                    break
                date_string = line.split(',')[0].strip('"')
                if is_valid_date(date_string):
                    lines.append(line)
    return ''.join(lines)


def read_csv(path, **kwargs):
    return pd.read_csv(path, **kwargs)


def get_last_timestamp(path):
    """
    Get last timestamp from lastfile.

    It reads the content of the file and return the content as string.
    """
    with open(path) as f:
        date_string = f.read()
    return date_string.rstrip()


def parse_last_timestamp(df):
    """
    Parse last timestamp from dataframe.

    Add one minute forward to prevent the script from fetching the same value.
    The last timestamp already in database, so we need to fetch the weather data
    one minute forward.
    """
    if df.empty:
        return None
    date_string = df['timestamp'].iloc[-1]

    # We add one minute forward to prevent data duplication at the edge.
    date_obj = to_datetime(date_string) + datetime.timedelta(minutes=1)
    return date_obj.strftime(ISO_DATE_FORMAT)


def get_last_timestamp_from_buffer(buf):
    df = read_csv(io.StringIO(buf), header=None, names=COLUMNS)
    return parse_last_timestamp(df)


def get_last_timestamp_from_df(df):
    return parse_last_timestamp(df)


def write_last_timestamp(path, date_string):
    with open(path, 'w+') as f:
        f.write(date_string)


def check_ltfile(path):
    """
    Check whether lastfile is exists or not. If not exists, create the file with
    empty content.
    """
    if not os.path.exists(path):
        logger.debug(
            'Last timestamp file (LT_FILE) is not exists. Creating LT_FILE...')
        with open(path, 'w+') as f:
            pass
    else:
        logger.debug('Last timestamp file (LT_FILE) already exists.')


def get_csv_from_queue(path):
    with open(path, 'a+') as f:
        data = f.read()
    return data


def erase_file_content(path):
    with open(path, 'w') as f:
        pass


def insert_to_db(url, entries):
    """
    Insert weather data to the database.

    :param url: SQLAlchemy engine URL.
    :param entries: List of dictionary of weather data.
    :return: True if data successfully inserted to the database,
             otherwise False.
    """
    engine = create_engine(url)
    cr6.Base.prepare(engine, reflect=True)

    try:
        with sessions.session_scope(engine) as session:
            session.bulk_insert_mappings(cr6.CR6, entries)
            session.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(e)
        return False


def sanitize_nan(entries):
    """
    Convert NaN to None for item in entries.
    """
    return [
        dict([
            (key, value) if not pd.isna(value) else (key, None)
            for key, value in item.items()
        ])
        for item in entries
    ]


def process_csv(url, buf, **kwargs):
    df = read_csv(io.StringIO(buf), header=None, names=COLUMNS)

    # Change non-number (except timestamp) to NaN if any.
    df = df.where(pd.notnull(df), np.nan)
    df.replace('NAN', np.nan, inplace=True)

    logger.info('Number of entries: %s', len(df))

    logger.debug('First 10 records:')
    logger.debug(df.head())
    logger.debug('Last 10 records:')
    logger.debug(df.tail())

    dry = kwargs.get('dry')
    if not dry:
        entries = df.to_dict(orient='records')
        ok = insert_to_db(url, sanitize_nan(entries))
        if ok:
            logger.info('Data successfully inserted to database.')

            last = get_last_timestamp_from_df(df)
            if last is None:
                return

            logger.info('Last data timestamp (+1 minute from last timestamp '
                        'in database): %s', last)
            logger.info('Writing request end time to LT_FILE...')
            write_last_timestamp(LT_FILE, last)
        else:
            logger.error('Data failed to be inserted to database.')
    else:
        logger.debug('Running in dry mode. Not inserting to database.')


class VaisalaApp(SingleInstance):
    """
    Vaisala app class that allow only one instance to be run.

    It prevents race condition when running multiple instance of classes. So, we
    only run the instance in one process only. We can make sure that only one
    process write a content to the lastfile.
    """

    def __init__(self, lastfile='', **kwargs):
        if lastfile:
            self.lastfile = lastfile
        else:
            # TODO(indra): create lastfile in data directory.
            self.lastfile = LT_FILE
        super().__init__(**kwargs)

    def run(self):
        args = parse_args()

        db_engine_url = args.engine_url or DATABASE_ENGINE
        if not db_engine_url:
            raise VaisalaAppError('Database engine URL is not configured yet')

        log_level = 'INFO'
        if args.verbose or DEBUG:
            log_level = 'DEBUG'

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '{asctime} {levelname} {name} {message}',
                    'style': '{',
                },
                'verbose': {
                    'format': '{asctime} {levelname} {name} {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                },
                'production': {
                    'level': log_level,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(LOG_DIR, 'vaisala.log'),
                    'maxBytes': 1024 * 1024 * 5,
                    'backupCount': 7,
                    'formatter': 'verbose',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'production'],
                    'level': log_level,
                },
                '__main__': {
                    'handlers': ['console', 'production'],
                    'level': log_level,
                    'propagate': False,
                }
            }
        }

        logging.config.dictConfig(logging_config)

        now = get_current_time()

        logger.info('-' * 80)
        logger.info('Processing start at: %s',
                    get_current_time().strftime(ISO_DATE_FORMAT))

        logger.debug('App base directory: %s', BASE_DIR)
        logger.debug('App cache directory: %s', CACHE_DIR)
        logger.debug('App data directory: %s', DATA_DIR)
        logger.debug('App log directory: %s', LOG_DIR)
        logger.debug('Sentry DSN: %s', SENTRY_DSN)

        logger.debug('Last timestamp file (LT_FILE): %s', self.lastfile)

        check_ltfile(self.lastfile)

        end = now.strftime(ISO_DATE_FORMAT)
        start = get_last_timestamp(self.lastfile)
        logger.info('Last time from file: %s', start)

        if not start:
            logger.info('Last timestamp will default to one hour ago.')
            one_hour_ago = now - datetime.timedelta(hours=1)
            start = one_hour_ago.strftime(ISO_DATE_FORMAT)

        logger.info('Request start time: %s', start)
        logger.info('Request end time: %s', end)

        logger.info('Requesting meteo data from web service...')
        try:
            response = get_meteo_data(start, end)
        except URLError as e:
            logger.error(e)
            sys.exit(1)

        if not response:
            logger.info('Response is empty. Skipping...')
            sys.exit(1)

        buf = parse_data(response)
        process_csv(db_engine_url, buf, dry=args.dry)

        logger.info('Processing end at: %s',
                    get_current_time().strftime(ISO_DATE_FORMAT))
        logger.info('-' * 80)


if __name__ == '__main__':
    try:
        app = VaisalaApp(lastfile=LT_FILE, lockfile=LOCKFILE)
        app.run()
    except SingleInstanceException:
        sys.exit(1)
