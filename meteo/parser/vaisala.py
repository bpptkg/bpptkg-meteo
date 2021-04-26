import logging
import re

from ..utils.encoding import force_text
from .fields import FIELDS_MAPPING

logger = logging.getLogger(__name__)


class ParserError(Exception):
    pass


class VaisalaParser(object):
    """
    Class to parse data from Vaisala weather device.
    """

    def __init__(self, delimiter=',', encoding='utf-8', errors='strict'):
        self.delimiter = delimiter
        self.encoding = encoding
        self.errors = errors

    def parse_value(self, s):
        """
        Parse field value.
        """
        pattern = re.compile(
            r'''
                (?P<field>\w+)
                =
                (?P<value>\d*[.,]?\d*)
                (?P<unit>\w+)
            ''',
            re.X,
        )

        m = pattern.match(s)
        if m is not None:
            components = m.groupdict()
            field = components['field']
            if field == 'Id':
                value = components['unit']
                unit = None
            else:
                if components['value']:
                    try:
                        converter = FIELDS_MAPPING[field]['type']
                        value = converter(components['value'])
                    except Exception:
                        value = None
                else:
                    value = None

                unit = components['unit']

            parsed_value = {
                'text': s,
                'field': field,
                'name': FIELDS_MAPPING[field]['name'],
                'value': value,
                'unit': unit,
            }
        else:
            parsed_value = {}

        return parsed_value

    def parse(self, s):
        """
        Parse one line of data string. Return dictionary of parsed value.
        """
        text = force_text(s, self.encoding, self.errors)
        components = text.split(self.delimiter)
        ident = components[0]
        parsed_value = []
        for text in components[1:]:
            value = self.parse_value(text)
            if value:
                parsed_value.append(value)

        return {'ident': ident, 'components': parsed_value}
