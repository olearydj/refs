"""One CSL record enters the same authority as refs JSON."""

import json
import re

from pydantic import ValidationError

from refs.models import Metadata, SourceCreate, assign_path, deferred_type, portable_url
from refs.results import RefError

NOCASE = re.compile(r'''<span\s+class=(["'])nocase\1>(.*?)</span>''', re.DOTALL)


def parse(raw: bytes, *, with_limitations: bool = False):
    try:
        metadata = json.loads(raw)
        if isinstance(metadata, list) and len(metadata) == 1:
            metadata = metadata[0]
        if not isinstance(metadata, dict):
            raise ValueError('Supply exactly one CSL object')
        details = deferred_type('csl', metadata.get('type', ''))
        if details:
            raise RefError('invalid_record', 'Input does not match the supported record profile. ' + details['recommendation'], 2, details=details)
        external_id = metadata.pop('id', None)
        if external_id is not None and (isinstance(external_id, bool) or not isinstance(external_id, (str, int))):
            raise ValueError('CSL id must be a string or integer')
        for alias, canonical in [('shortTitle', 'title-short'), ('journalAbbreviation', 'container-title-short'), ('event', 'event-title')]:
            if alias in metadata:
                assign_path(metadata, canonical, metadata.pop(alias))
        fields = {field.alias or name for name, field in Metadata.model_fields.items()}
        limitations = [dict(field=key, reason=f'Preserved from import: {key}') for key in metadata if key not in fields]
        if 'URL' in metadata and not portable_url(metadata['URL']):
            limitations.append(dict(field='URL', reason='Non-HTTP(S) or relative URL preserved verbatim; supply an absolute URL to use it'))
            metadata.pop('URL')
        metadata = {key: value for key, value in metadata.items() if key in fields}
        protection = {}
        for field in ('title', 'container-title'):
            value = metadata.get(field)
            if not isinstance(value, str):
                continue
            spans = list(NOCASE.finditer(value))
            if spans:
                whole = len(spans) == 1 and spans[0].span() == (0, len(value))
                terms = [] if whole else list(dict.fromkeys(span[2] for span in spans))
                protection[field] = dict(protected_terms=terms, preserve_case=whole)
            metadata[field] = NOCASE.sub(r'\2', value)
        provenance = {'origin': 'import', 'access': 'unknown'}
        if external_id is not None:
            provenance['source_identity'] = {'namespace': 'csljson', 'item_key': str(external_id)}
        source = SourceCreate.model_validate({'schema_version': '1.0', 'metadata': metadata, 'title_protection': protection, 'provenance': [provenance]})
        return (source, limitations) if with_limitations else source
    except ValidationError as exc:
        raise RefError('invalid_record', 'Input does not match the supported record profile', 2, details={'issues':exc.errors(include_url=False,include_context=False,include_input=False)}) from exc
    except ValueError as exc:
        raise RefError('invalid_record', str(exc), 2) from exc
