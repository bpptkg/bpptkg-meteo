from meteo.parser.fields import FIELDS_MAPPING
from meteo.parser.vaisala import VaisalaParser


def process_lines(timestamp, lines):
    """
    Process lines block associated with sampled data.
    """
    data = {}
    parser = VaisalaParser()
    for line in lines:
        s = parser.parse(line)
        for comp in s['components']:
            data[comp['name']] = comp['value']

    data['timestamp'] = timestamp

    # TODO(indra): Implement insert to database.
    print(data)
