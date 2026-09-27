"""Registry names for rules over current record fields, never independent facts."""

from refs.models import REGISTRY
from refs.results import RefError, notice


def value_at(record: dict, path: str):
    value = record
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def row(name: str) -> dict:
    for definition in REGISTRY['kinds']:
        if definition['name'] == name:
            return definition
    raise RefError('invalid_invocation', 'Unknown kind; use refs kinds to see the names', 2, details={'kind': name})


def identify(record: dict) -> str | None:
    for definition in REGISTRY['kinds']:
        if record['metadata']['type'] == definition['type'] and all(value_at(record, path) == value for path, value in definition['fields'].items()):
            return definition['name']
    return None


def assign(record: dict, name: str) -> dict:
    definition = row(name)
    fields = {'metadata.type': definition['type']} | definition['fields']
    conflicts = [dict(path=path, current=value_at(record, path), incoming=value) for path, value in fields.items()
                 if value_at(record, path) is not None and value_at(record, path) != value]
    if conflicts:
        raise RefError('value_conflict', 'Kind defining fields differ; clear or correct them explicitly before assigning the kind',
                       details={'kind': name, 'conflicts': conflicts})
    for path, value in fields.items():
        node = record
        parts = path.split('.')
        for part in parts[:-1]:
            if node.get(part) is None:
                node[part] = {}
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    if 'native_type.value' in fields:
        record['native_type'].setdefault('namespace', 'biblatex')
    return record


def from_origin(record: dict, route: str, label: str) -> dict:
    for definition in REGISTRY['kinds']:
        if label in definition.get('origins', {}).get(route, []):
            return assign(record, definition['name'])
    return record


def warnings(record: dict) -> list[dict]:
    choices = [definition['name'] for definition in REGISTRY['kinds'] if definition['type'] == record['metadata']['type'] and definition.get('announce', True)]
    if choices and identify(record) is None:
        return [notice('kind_unassigned', 'Available kinds: ' + ', '.join(choices), details={'kinds': choices})]
    return []


def matches(record: dict, name: str | None) -> bool:
    if name is None:
        return True
    if name == 'unassigned':
        return bool(warnings(record))
    return identify(record) == name
