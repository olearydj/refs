import pytest
from pydantic import ValidationError

from refs.models import SourceCreate, SourcePatch


def source(**metadata):
    return SourceCreate.model_validate({'schema_version': '1.0', 'metadata': {'title': 'A Synthetic Work', **metadata}})


@pytest.mark.parametrize('metadata', [
    {'type': 'book', 'edition': '2'},
    {'type': 'book', 'edition': 2.0},
    {'type': 'book', 'edition': '2.0'},
    {'type': 'patent', 'author': [{'family': 'Smith', 'given': 'Alex'}]},
    {'type': 'speech', 'author': [{'literal': 'Research and Development'}]},
    {'issued': {'date-parts': [[2024, 2, 29]]}},
    {'issued': {'literal': 'Spring 2024'}},
    {'author': [{'family': 'Gogh', 'given': 'Vincent', 'non-dropping-particle': 'van'}]},
])
def test_valid_values(metadata):
    value = source(**metadata).canonical()
    if 'edition' in metadata:
        assert value['metadata']['edition'] == 2


@pytest.mark.parametrize('metadata', [
    {'issued': {'date-parts': [[2023, 2, 29]]}},
    {'issued': {'date-parts': [[2024, 13]]}},
    {'issued': {'date-parts': [[2025], [2024]]}},
    {'issued': {'date-parts': [['2024']]}},
    {'author': [{'family': 'Smith', 'literal': 'Company'}]},
    {'author': [{'family': 'Smith', 'parse-names': 'yes'}]},
    {'type': 'mystery'},
    {'unexpected': 'value'},
])
def test_invalid_values(metadata):
    with pytest.raises(ValidationError):
        source(**metadata)


def test_native_type_extensions_and_title_boundary():
    value = {'schema_version': '1.0', 'metadata': {'type': 'patent', 'title': 'Synthetic Device'},
             'native_type': {'namespace': 'zotero', 'value': 'patent'},
             'extensions': {'patent': {'assignees': [{'literal': 'Lab and Company'}], 'application_number': 'APP1', 'priority_date': {'date-parts': [[2020]]}}}}
    SourceCreate.model_validate(value)
    value['metadata']['type'] = 'book'
    with pytest.raises(ValidationError):
        SourceCreate.model_validate(value)
    with pytest.raises(ValidationError):
        SourceCreate.model_validate({'schema_version': '1.0', 'metadata': {'title': 'Learning Python'}, 'title_parts': {'main_title': 'Learn'}})


def test_patch_is_strict_and_clear_is_explicit():
    SourcePatch.model_validate({'schema_version': '1.0', 'set': {'metadata.title': 'Changed'}, 'clear': ['metadata.abstract']})
    for value in [None, {'schema_version': '1.0', 'set': {'metadata.title': None}},
                  {'schema_version': '1.0', 'set': {'metadata.title': 'X'}, 'clear': ['metadata.title']}]:
        with pytest.raises(ValidationError):
            SourcePatch.model_validate(value)


def test_metadata_model_matches_packaged_registry():
    from refs.models import REGISTRY, Metadata
    assert {field.alias or name for name, field in Metadata.model_fields.items()} >= set(REGISTRY['core_fields'])


@pytest.mark.parametrize('kind, field, value', [('article','publisher','Repository'), ('book','page','17–42'), ('speech','edition',2)])
def test_csl_variables_are_not_restricted_by_type(kind, field, value):
    assert source(type=kind, **{field:value}).canonical()['metadata'][field] == value


def test_all_pinned_csl_variables_have_a_model_field():
    import json
    from pathlib import Path

    from refs.models import Metadata
    properties = json.loads((Path(__file__).parents[1]/'fixtures/mappings/csl-data.json').read_text())['items']['properties']
    auxiliary = {'id','citation-key','categories','custom','journalAbbreviation','shortTitle','event'}
    assert set(properties)-auxiliary == {field.alias or name for name,field in Metadata.model_fields.items()}


def test_datacite_producer_fields_do_not_reject_capture():
    import json

    from refs.adapters import csl
    value = {'type':'article','title':'Attention Study','publisher':'Repository','categories':['Computing'],'copyright':'Owner','license':'CC0'}
    metadata = csl.parse(json.dumps(value).encode()).canonical()['metadata']
    assert metadata == {'type':'article','title':'Attention Study','publisher':'Repository'}
