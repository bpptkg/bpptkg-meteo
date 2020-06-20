import os
import unittest
import tempfile

import app


def get_random_tempfile():
    with tempfile.NamedTemporaryFile() as f:
        path = f.name
    return path


class LastTimestampFileTest(unittest.TestCase):
    def test_read_lt_file_basic(self):
        path = get_random_tempfile()

        with open(path, 'w') as f:
            f.write('2020-01-01T00:00:00')

        date = app.get_last_timestamp(path)
        self.assertEqual(date, '2020-01-01T00:00:00')

    def test_read_lt_file_with_trailing_characters(self):
        path = get_random_tempfile()

        with open(path, 'w') as f:
            f.write('2020-01-01T00:00:00\n \n \t')

        date = app.get_last_timestamp(path)
        self.assertEqual(date, '2020-01-01T00:00:00')

    def test_read_lt_file_with_bytes_characters(self):
        path = get_random_tempfile()

        with open(path, 'wb') as f:
            f.write(b'2020-01-01T00:00:00')

        date = app.get_last_timestamp(path)
        self.assertEqual(date, '2020-01-01T00:00:00')


if __name__ == '__main__':
    unittest.main()
