"""
bpptkg-meteo vaisala app.

It download meteorology data from Pasarbubar station web service at 192.168.9.47
and insert it to database. Schema table is defined in 'meteo.models.cr6.CR6'
class.

You can add another schema table in bpptkg-meteo package by submitting
pull/merge request to the project repository.

You can also write another app using bpptkg-meteo package.

Usage:

Just provide SQLAlchemy database engine to the script argument and add the
script to system crontab by 30 minutes or so. For example:

    $ python /path/to/app.py 'mysql://iori:secret@127.0.0.1/meteo'

Add -v option to run the app in debugging mode.

It will create 'last' file that store the latest data timestamp in data
directory. You can view runtime log in logs directory.
"""

import os
import io
import csv
import sys
import pytz
import argparse
import datetime
import logging

from urllib.request import urlopen
from urllib.parse import urlencode

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from meteo.db import sessions
from meteo.models import cr6


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

TIME_ZONE = 'Asia/Jakarta'
UTC_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='SQLAlchemy database engine URL.')
    parser.add_argument('-d', '--dry', action='store_true',
                        help='Do not insert data to database (dry run).')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Run in debugging mode.')
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

    Response is actually CSV data, we decode it and return CSV string.
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
    with open(path) as f:
        date_string = f.read()
    return date_string


def parse_last_timestamp(df):
    if df.empty:
        return None
    date_string = df['timestamp'].iloc[-1]

    # We add one minutes forward to prevent data duplication at the edge.
    date_obj = to_datetime(date_string) + datetime.timedelta(minutes=1)
    return date_obj.strftime(UTC_DATE_FORMAT)


def get_last_timestamp_from_buffer(buf):
    df = read_csv(io.StringIO(buf), header=None, names=COLUMNS)
    return parse_last_timestamp(df)


def get_last_timestamp_from_df(df):
    return parse_last_timestamp(df)


def write_last_timestamp(path, date_string):
    with open(path, 'w+') as f:
        f.write(date_string)


def check_ltfile(path):
    now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
    if not os.path.exists(path):
        logger.debug('LT_FILE is not exists. Creating LT_FILE...')
        with open(path, 'w+') as f:
            f.write(now.strftime(UTC_DATE_FORMAT))
    else:
        logger.debug('LT_FILE already exists.')


def get_csv_from_queue(path):
    with open(path, 'a+') as f:
        data = f.read()
    return data


def erase_file_content(path):
    with open(path, 'w') as f:
        pass


def insert_to_db(url, entries):
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


def process_csv(url, buf, **kwargs):
    df = read_csv(io.StringIO(buf), header=None, names=COLUMNS)
    logger.info('Number of entries: %s', len(df))

    logger.debug('First 10 records:')
    logger.debug(df.head())
    logger.debug('Last 10 records:')
    logger.debug(df.tail())

    dry = kwargs.get('dry')
    if not dry:
        ok = insert_to_db(url, df.to_dict(orient='records'))
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
            logger.info('Data failed to be inserted to database.')
    else:
        logger.debug('Running in dry mode. Not inserting to database.')


def main():
    args = parse_args()
    now = datetime.datetime.now(pytz.timezone(TIME_ZONE))

    log_format = '%(asctime)s %(name)s %(levelname)-8s %(message)s'
    log_datefmt = '%b %d %Y %H:%M:%S'
    log_filename = os.path.join(
        LOG_DIR,
        now.strftime('vaisala_%Y-%m-%d.log')
    )

    if args.verbose:
        log_mode = logging.DEBUG
    else:
        log_mode = logging.INFO

    logging.basicConfig(
        level=log_mode,
        format=log_format,
        datefmt=log_datefmt,
        filename=log_filename,
        filemode='a'
    )

    console = logging.StreamHandler()
    console.setLevel(log_mode)
    formatter = logging.Formatter(log_format)
    console.setFormatter(formatter)
    logger.addHandler(console)

    logger.info('-' * 80)
    logger.info('Processing start at: %s', datetime.datetime.now(
        pytz.timezone(TIME_ZONE)).isoformat())

    check_ltfile(LT_FILE)

    end = now.strftime(UTC_DATE_FORMAT)
    start = get_last_timestamp(LT_FILE)
    logger.info('Last time from file: %s', start)

    if not start:
        start = now.strftime(UTC_DATE_FORMAT)
        end = (now + datetime.timedelta(minutes=30)).strftime(UTC_DATE_FORMAT)

    logger.info('Request start time: %s', start)
    logger.info('Request end time: %s', end)

    logger.info('Requesting meteo data from web service...')
    response = get_meteo_data(start, end)
    if not response:
        logger.info('Response is empty. Skipping...')
        sys.exit()

    buf = parse_data(response)
    process_csv(args.url, buf, dry=args.verbose)

    logger.info('Processing end at: %s', datetime.datetime.now(
        pytz.timezone(TIME_ZONE)).isoformat())
    logger.info('-' * 80)


if __name__ == '__main__':
    main()
