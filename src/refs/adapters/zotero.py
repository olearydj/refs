"""Admission and mapping of the published Zotero JSON directory."""

import html
import json
import re
from pathlib import Path

from pydantic import ValidationError

from refs.models import (
    MONTHS,
    REGISTRY,
    Date,
    SourceCreate,
    assign_path,
    deferred_type,
    portable_url,
)
from refs.results import RefError

CHILDREN = {'attachment', 'note', 'annotation'}
KEY = re.compile(r'[A-Z0-9]{8}')
SCHEMES = {'arxiv': 'extensions.identifiers.arxiv', 'oclc': 'extensions.identifiers.oclc',
           'doi': 'metadata.DOI', 'pmid': 'metadata.PMID', 'pmcid': 'metadata.PMCID', 'issn': 'metadata.ISSN'}


def attachment_path(item: dict, manifest: dict) -> Path:
    data = item['data']
    mode = data.get('linkMode')
    expression = data.get('path', '')
    if mode in ('imported_file', 'imported_url'):
        suffix = Path(data.get('filename') or '')
        if not suffix.name or suffix.is_absolute() or '..' in suffix.parts:
            raise RefError('invalid_attachment_path', 'Inspect the stored attachment filename')
        return Path(manifest['data_directory']) / 'storage' / item['key'] / suffix
    if mode == 'linked_file':
        if expression.startswith('attachments:'):
            if not manifest.get('base_path'):
                raise RefError('attachment_base_missing', 'Supply the original linked-attachment base path')
            suffix = Path(expression.removeprefix('attachments:'))
            if suffix.is_absolute() or '..' in suffix.parts:
                raise RefError('invalid_attachment_path', 'Inspect the base-relative attachment path')
            return Path(manifest['base_path']) / suffix
        path = Path(expression)
        if path.is_absolute():
            return path
        raise RefError('invalid_attachment_path', 'Supply an absolute or base-relative attachment path')
    raise RefError('unsupported_attachment', 'Inspect the attachment link mode')


def context(item: dict) -> str | None:
    data = item['data']
    if data['itemType'] == 'note':
        return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', data.get('note', ''))).split()) or None
    if data['itemType'] == 'attachment' and data.get('linkMode') == 'linked_url':
        return data.get('url')
    return None


def relations(item: dict) -> list[str]:
    values = item['data'].get('relations', {}).get('dc:relation', [])
    return [target.removeprefix('http://zotero.org/').removeprefix('https://zotero.org/') for target in ([values] if isinstance(values, str) else values)]


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
            if parent and (parent not in by_key or data['itemType'] == 'annotation' and by_key[parent]['data']['itemType'] != 'attachment'):
                raise ValueError(f"Unresolved parent for {item['key']}")
            if any(key not in collection_map for key in data.get('collections', [])):
                raise ValueError(f"Unresolved collection for {item['key']}")
        return dict(manifest=manifest, collections=collections, items=items)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RefError('invalid_zotero_input', f'Inspect the Zotero JSON directory: {exc}', 2) from exc


def date_range(value: str) -> dict | None:
    """Read explicit endpoints before considering Zotero's parsed start date."""
    parts = None
    if match := re.fullmatch(r'(\d{4})\s*[-–—/]\s*(\d{4})', value):
        parts = [[int(match[1])], [int(match[2])]]
    elif match := re.fullmatch(r'(\d{4}(?:-\d{1,2}){0,2})\s*(?:/|–|—| to | - )\s*(\d{4}(?:-\d{1,2}){0,2})', value):
        parts = [[int(n) for n in endpoint.split('-')] for endpoint in match.groups()]
    elif match := re.fullmatch(r'(\d{1,2})\s*[-–—]\s*(\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{4})', value):
        months = {alias:number for number,pair in enumerate(MONTHS,1) for alias in pair}
        month = months.get(match[3].lower())
        if month:
            parts = [[int(match[4]), month, int(match[index])] for index in (1,2)]
    if parts:
        try:
            return Date.model_validate({'date-parts': parts}).model_dump(by_alias=True, exclude_none=True)
        except ValidationError:
            return {'literal':value}
    single = re.fullmatch(r'\d{4}(?:-\d{1,2}){0,2}(?:[ T]\d{2}:\d{2}.*)?|\d{4}/\d{1,2}(?:/\d{1,2})?|\d{1,2}/\d{4}|\d{1,2}/\d{1,2}/\d{2,4}', value)
    if not single and re.search(r'[-–—/]|\b(?:to|through|until)\b', value, re.I):
        return {'literal':value}
    return None


def date(value: str, parsed: str | None = None) -> dict:
    multipart = re.fullmatch(r'(\d{4}-\d{2}-\d{2}) (.+)', value)
    if multipart and not re.fullmatch(r'\d{2}:\d{2}(?::\d{2})?', multipart[2]):
        value, parsed = multipart[2], parsed or multipart[1]
    if interval := date_range(value):
        return interval
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


def extra_lines(data: dict, source: dict, limitations: list[dict]) -> str | None:
    extra_key = None
    for line in data.get('extra', '').splitlines():
        label, separator, value = line.partition(':')
        label, value = label.strip().casefold(), value.strip()
        if separator and label == 'citation key':
            if extra_key and extra_key != value:
                raise RefError('alias_conflict', 'Conflicting Citation Key lines; inspect Extra', 3)
            extra_key = value
        elif separator and label in SCHEMES and value:
            assign_path(source, SCHEMES[label], value)
        elif line.strip() and not any(entry['field'] == 'extra' for entry in limitations):
            limitations.append(dict(field='extra', reason='Preserved from import: extra'))
    return extra_key


def parse(item: dict, manifest: dict) -> dict:
    data = item['data']
    kind = data['itemType']
    types = {row['zotero']: row['canonical'] for row in REGISTRY['type_mappings']}
    if kind not in types:
        details = deferred_type('zotero', kind)
        message = f'No assessed mapping for {kind}; inspect the preserved item'
        if details:
            message += '. ' + details['recommendation']
        raise RefError('unknown_zotero_type', message, 2, details=details)
    source: dict = dict(schema_version='1.0', metadata={'type': types[kind]}, native_type={'namespace': 'zotero', 'value': kind},
                  provenance=[dict(origin='import', source_identity=dict(namespace='zotero', library_uri=manifest['library_uri'], item_key=item['key']))],
                  legacy_tags=[tag['tag'] for tag in data.get('tags', [])])
    rows = {row['source_field']: row['canonical_path'] for row in REGISTRY['rows'] if row['input_format'] == 'zotero-json' and kind in row['type_scope']}
    limitations = []
    ignored = {'key', 'version', 'itemType', 'dateAdded', 'dateModified', 'creators', 'tags', 'collections', 'relations', 'extra', 'citationKey', 'deleted'}
    for field, value in data.items():
        if not value or field in ignored:
            continue
        preserved = REGISTRY.get('preserved_only', {}).get('zotero-json', {})
        if field in preserved:
            limitations.append(dict(field=field, reason=preserved[field]))
            continue
        path = rows.get(field)
        if path:
            if field in ('date', 'issueDate', 'accessDate', 'filingDate', 'priorityDate'):
                value = date(value, item.get('meta', {}).get('parsedDate') if field == 'date' else None)
                if 'literal' in value:
                    limitations.append(dict(field=field,reason='Date retained literally; verify its precision'))
            elif field == 'assignee':
                value = [{'literal': value}]
            elif field == 'url' and not portable_url(value):
                path = None
        if path:
            assign_path(source, path, value)
        else:
            limitations.append(dict(field=field, reason=f'Preserved from import: {field}'))
    for creator in data.get('creators', []):
        role = creator['creatorType']
        path = rows.get('creators.' + role)
        if not path:
            raise RefError('unknown_creator_role', f'No assessed mapping for creator role {role}; inspect the preserved item', 2)
        name = {'literal': creator['name']} if creator.get('name') else {target: creator[field] for field, target in [('lastName', 'family'), ('firstName', 'given')] if creator.get(field)}
        source['metadata'].setdefault(path.split('.')[1], []).append(name)
    extra_key = extra_lines(data, source, limitations)
    key = data.get('citationKey') or extra_key or manifest.get('legacy_keys', {}).get(item['key'])
    try:
        validated = SourceCreate.model_validate(source)
        if key:
            validated.citation_key = key
        return dict(source=validated, limitations=limitations)
    except ValidationError as exc:
        raise RefError('invalid_zotero_item', 'Item cannot satisfy the record profile; inspect its preserved original', 2,
                       details={'issues': exc.errors(include_url=False, include_context=False, include_input=False)}) from exc
