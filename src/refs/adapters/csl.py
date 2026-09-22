"""One CSL record enters the same authority as refs JSON."""

import json

from pydantic import ValidationError

from refs.models import SourceCreate
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
        provenance = {'origin': 'import', 'access': 'unknown'}
        if external_id is not None:
            provenance['source_identity'] = {'namespace': 'csljson', 'item_key': str(external_id)}
        return SourceCreate.model_validate({'schema_version': '1.0', 'metadata': metadata, 'provenance': [provenance]})
    except (ValueError, ValidationError) as exc:
        raise RefError('invalid_record', str(exc), 2) from exc
