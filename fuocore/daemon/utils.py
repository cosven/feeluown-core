def to_identifier(path):
    if 'fuo://' in path:
        return path
    return 'fuo://' + path


def get_provider_name(path):
    return path.split('/')[1]
