"""Admission and mapping of the published Zotero JSON directory."""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from pydantic import ValidationError

from refs.models import REGISTRY, Date, SourceCreate, normalize_arxiv, normalize_doi
from refs.results import RefError

CHILDREN = {'attachment', 'note', 'annotation'}
KEY = re.compile(r'[A-Z0-9]{8}')
SCHEMES = {'arxiv': 'extensions.identifiers.arxiv', 'oclc': 'extensions.identifiers.oclc',
           'doi': 'metadata.DOI', 'pmid': 'metadata.PMID', 'pmcid': 'metadata.PMCID', 'issn': 'metadata.ISSN'}


def read(directory: Path) -> dict:
    try:
        manifest = json.loads((directory / 'manifest.json').read_bytes())
        if manifest.get('format') != 'refs-zotero-input' or manifest.get('version') != 1 or manifest.get('api_version') != 3:
            raise ValueError('Unsupported manifest version')
        if not re.fullmatch(r'users/(?:[0-9]+|local/[A-Za-z0-9]+)', manifest['library_uri']):
            raise ValueError('Invalid library identity')
        for field in ('zotero_version', 'userdata_version', 'global_version', 'extractor_version', 'data_directory'):
            if not manifest.get(field):
                raise ValueError(f'Missing {field}')
        if not Path(manifest['data_directory']).is_absolute() or manifest.get('base_path') and not Path(manifest['base_path']).is_absolute():
            raise ValueError('Original data and base paths must be absolute')
        collections = json.loads((directory / 'collections.json').read_bytes())
        collection_map = {entry['key']: entry['data'] for entry in collections}
        if len(collection_map) != len(collections):
            raise ValueError('Duplicate collection identity')
        for key, data in collection_map.items():
            if not KEY.fullmatch(key) or data.get('key', key) != key or not isinstance(data.get('name'), str) or not data['name']:
                raise ValueError('Invalid collection')
            visited, parent = {key}, data.get('parentCollection')
            while parent:
                if parent in visited or parent not in collection_map:
                    raise ValueError('Missing or cyclic collection parent')
                visited.add(parent)
                parent = collection_map[parent].get('parentCollection')
        items: list[dict] = []
        for path in sorted((directory / 'items').glob('*.json')):
            raw = path.read_bytes()
            try:
                item: dict = json.loads(raw)
            except ValueError:
                item = {'key':path.stem,'data':{'itemType':'invalid_json'}}
            key, data = item['key'], item['data']
            if not KEY.fullmatch(key) or path.stem != key or data.get('key', key) != key or not isinstance(data.get('itemType'), str):
                raise ValueError(f'Invalid item identity: {path.name}')
            items.append(dict(key=key, data=data, item=item, raw=raw, locator=str(path)))
        excluded = {item['key'] for item in items if item['data'].get('deleted')}
        while children := {item['key'] for item in items if item['data'].get('parentItem') in excluded} - excluded:
            excluded.update(children)
        items = [item for item in items if item['key'] not in excluded]
        manifest.setdefault('skipped', {})['trash'] = manifest.get('skipped', {}).get('trash',0)+len(excluded)
        by_key = {item['key']: item for item in items}
        for item in items:
            data = item['data']
            parent = data.get('parentItem')
            if parent and (parent not in by_key or by_key[parent]['data']['itemType'] not in ({'attachment'} if data['itemType'] == 'annotation' else set(row['zotero'] for row in REGISTRY['type_mappings']))):
                raise ValueError(f"Unresolved parent for {item['key']}")
            if any(key not in collection_map for key in data.get('collections', [])):
                raise ValueError(f"Unresolved collection for {item['key']}")
        return dict(manifest=manifest, collections=collections, items=items)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RefError('invalid_zotero_input', f'Inspect the Zotero JSON directory: {exc}', 2) from exc


def assign(target: dict, path: str, value) -> None:
    if path == 'metadata.DOI':
        value = normalize_doi(value)
    elif path == 'extensions.identifiers.arxiv':
        value = normalize_arxiv(value)
    parts = path.split('.')
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    if parts[-1] in target and target[parts[-1]] != value:
        raise RefError('alias_conflict', f'Competing values for {path}; inspect the original item', 3)
    target[parts[-1]] = value


def date(value: str, parsed: str | None = None) -> dict:
    multipart = re.fullmatch(r'(\d{4}-\d{2}-\d{2}) (.+)', value)
    if multipart and not re.fullmatch(r'\d{2}:\d{2}(?::\d{2})?', multipart[2]):
        value, parsed = multipart[2], parsed or multipart[1]
    candidate = parsed or value
    candidate = re.sub(r'[ T]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?$', '', candidate)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}',candidate):
        candidate = candidate.removesuffix('-00').removesuffix('-00')
    if re.fullmatch(r'\d{4}(?:-\d{2}){0,2}', candidate):
        try:
            result = Date.model_validate({'date-parts': [[int(part) for part in candidate.split('-')]]}).model_dump(by_alias=True, exclude_none=True)
        except ValidationError:
            return date(value) if parsed else {'literal':value}
        if parsed:
            explicit = re.fullmatch(r'(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?',value)
            years = set(re.findall(r'(?<!\d)([1-9]\d{3})(?!\d)',value))
            parts = result['date-parts'][0]
            if explicit and any(int(component) != part for component,part in zip(explicit.groups(),parts) if component) or len(years)==1 and int(next(iter(years))) != parts[0]:
                raise RefError('date_conflict','Parsed date contradicts the supplied date; inspect the original item',3)
            if explicit:
                return date(value)
            if len(years)>1 or re.search(r'\b(?:circa|about|before|after)\b|[?~]',value,re.I):
                return {'literal':value}
        return result
    return {'literal': value}


def parse(item: dict, manifest: dict) -> dict:
    data = item['data']
    kind = data['itemType']
    types = {row['zotero']: row['canonical'] for row in REGISTRY['type_mappings']}
    if kind not in types:
        raise RefError('unknown_zotero_type', f'No assessed mapping for {kind}; inspect the preserved item', 2)
    source: dict = dict(schema_version='1.0', metadata={'type': types[kind]}, native_type={'namespace': 'zotero', 'value': kind},
                  provenance=[dict(origin='import', source_identity=dict(namespace='zotero', library_uri=manifest['library_uri'], item_key=item['key']))],
                  legacy_tags=[tag['tag'] for tag in data.get('tags', [])])
    rows = {row['source_field']: row['canonical_path'] for row in REGISTRY['rows'] if row['input_format'] == 'zotero-json' and kind in row['type_scope']}
    limitations = []
    ignored = {'key', 'version', 'itemType', 'dateAdded', 'dateModified', 'creators', 'tags', 'collections', 'relations', 'extra', 'citationKey', 'deleted'}
    for field, value in data.items():
        if not value or field in ignored:
            continue
        path = rows.get(field)
        if path:
            if field in ('date', 'issueDate', 'accessDate', 'filingDate', 'priorityDate'):
                value = date(value, item.get('meta', {}).get('parsedDate') if field == 'date' else None)
                if 'literal' in value:
                    limitations.append(dict(field=field,reason='Date retained literally; verify its precision'))
            elif field == 'assignee':
                value = [{'literal': value}]
            elif field == 'url' and (urlparse(value).scheme not in ('http', 'https') or not urlparse(value).netloc):
                path = None
        if path:
            assign(source, path, value)
        else:
            limitations.append(dict(field=field, reason=f'Preserved from import: {field}'))
    for creator in data.get('creators', []):
        role = creator['creatorType']
        path = rows.get('creators.' + role)
        if not path:
            raise RefError('unknown_creator_role', f'No assessed mapping for creator role {role}; inspect the preserved item', 2)
        name = {'literal': creator['name']} if creator.get('name') else {target: creator[field] for field, target in [('lastName', 'family'), ('firstName', 'given')] if creator.get(field)}
        source['metadata'].setdefault(path.split('.')[1], []).append(name)
    extra_key = None
    for line in data.get('extra', '').splitlines():
        label, separator, value = line.partition(':')
        label, value = label.strip().casefold(), value.strip()
        if separator and label == 'citation key':
            if extra_key and extra_key != value:
                raise RefError('alias_conflict', 'Conflicting Citation Key lines; inspect Extra', 3)
            extra_key = value
        elif separator and label in SCHEMES and value:
            assign(source, SCHEMES[label], value)
        elif line.strip() and not any(entry['field'] == 'extra' for entry in limitations):
            limitations.append(dict(field='extra', reason='Preserved from import: extra'))
    key = data.get('citationKey') or extra_key or manifest.get('legacy_keys', {}).get(item['key'])
    try:
        validated = SourceCreate.model_validate(source)
        if key:
            validated.citation_key = key
        return dict(source=validated, limitations=limitations)
    except ValidationError as exc:
        raise RefError('invalid_zotero_item', 'Item cannot satisfy the record profile; inspect its preserved original', 2,
                       details={'issues': exc.errors(include_url=False, include_context=False, include_input=False)}) from exc
