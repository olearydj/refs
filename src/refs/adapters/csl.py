"""One CSL record enters the same authority as refs JSON."""

import json

from pydantic import ValidationError

from refs.models import Metadata, SourceCreate
from refs.results import RefError


def parse(raw: bytes) -> SourceCreate:
    try:
        metadata = json.loads(raw)
        if isinstance(metadata, list) and len(metadata) == 1:
            metadata = metadata[0]
        if not isinstance(metadata, dict):
            raise ValueError('Supply exactly one CSL object')
        external_id = metadata.pop('id', None)
        if external_id is not None and (isinstance(external_id, bool) or not isinstance(external_id, (str, int))):
            raise ValueError('CSL id must be a string or integer')
        for alias, canonical in [('shortTitle', 'title-short'), ('journalAbbreviation', 'container-title-short'), ('event', 'event-title')]:
            if alias in metadata:
                if canonical in metadata and metadata[canonical] != metadata[alias]:
                    raise ValueError(f'Conflicting aliases for {canonical}')
                metadata[canonical] = metadata.pop(alias)
        fields = {field.alias or name for name, field in Metadata.model_fields.items()}
        metadata = {key: value for key, value in metadata.items() if key in fields}
        provenance = {'origin': 'import', 'access': 'unknown'}
        if external_id is not None:
            provenance['source_identity'] = {'namespace': 'csljson', 'item_key': str(external_id)}
        return SourceCreate.model_validate({'schema_version': '1.0', 'metadata': metadata, 'provenance': [provenance]})
    except (ValueError, ValidationError) as exc:
        raise RefError('invalid_record', str(exc), 2) from exc
