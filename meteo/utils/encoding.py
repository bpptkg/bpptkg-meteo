def decode_string(s):
    """
    Decode bytes s to string. Return original if decode failed.
    """
    try:
        return s.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        return s


def force_text(s, encoding='utf-8', errors='strict'):
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


def get_value_or_none(data, index):
    """
    Get value at certain index from list. Return None if index outside data
    range.
    """
    try:
        return data[index]
    except IndexError:
        return None
