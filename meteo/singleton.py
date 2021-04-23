import logging
import os
import sys
import tempfile

logger = logging.getLogger(__name__)

if sys.platform != 'win32':
    import fcntl


class SingleInstanceException(Exception):
    pass


class SingleInstance(object):
    """
    A singleton object that can only be instantiated once.

    It is useful if the script is executed by crontab at small amounts of time.

    Reference:
    https://github.com/pycontribs/tendo/blob/master/tendo/singleton.py
    """

    def __init__(self, flavor_id='', lockfile=''):
        self.initialized = False
        if lockfile:
            self.lockfile = lockfile
        else:
            basepath = os.path.abspath(sys.argv[0])
            basename = os.path.splitext(basepath)[0].replace(
                "/", "-").replace(":", "").replace(
                    "\\", "-") + '-%s' % flavor_id + '.lock'
            self.lockfile = os.path.normpath(
                tempfile.gettempdir() + '/' + basename)

        logger.debug('SingleInstance lockfile: %s', self.lockfile)
        if sys.platform == 'win32':
            try:
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(
                    self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
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
