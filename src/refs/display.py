"""Shared record text helpers for human output."""

from refs.models import person_name

def authors(record: dict) -> list[str]:
    return [name.get('literal') or person_name(name, strip=True)
            for name in record['metadata'].get('author', [])]



def metadata_text(value) -> str:
    if isinstance(value, list):
        return '; '.join(metadata_text(item) for item in value)
    if isinstance(value, dict):
        if any(key in value for key in ('family', 'given', 'literal')):
            return authors({'metadata': {'author': [value]}})[0]
        if 'date-parts' in value:
            dates = ' – '.join('-'.join(str(number).zfill(4 if index == 0 else 2) for index,number in enumerate(parts)) for parts in value['date-parts'])
            extras = {key:item for key,item in value.items() if key != 'date-parts'}
            return dates + ('; ' + metadata_text(extras) if extras else '')
        return '; '.join(f'{key}: {metadata_text(item)}' for key,item in sorted(value.items()))
    return str(value)

def resource_path(resource: dict) -> str:
    return str(resource.get('resolved_path') or resource.get('path') or resource.get('relative') or resource.get('id', '(unavailable)'))
