from collections import namedtuple


IdentifierParseResult = namedtuple(
    'IdentifierParseResult',
    ('scheme', 'provider', 'identifier')
)


def parse_indentifier(identifier):
    scheme, body = identifier.split('://')
    provider, _, identifier = body.split(':')
    return IdentifierParseResult(scheme, provider, identifier)
