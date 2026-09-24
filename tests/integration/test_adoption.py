import pytest

from refs import bibliography, importing, projects
from refs.results import RefError


def test_adoption_requires_exact_completed_import(initialized, tmp_path):
    catalog = tmp_path/'cat'
    path = tmp_path/'adopt.bib'
    raw = b'@book{x,title={Synthetic Book},author={Smith, Alex},year={2024}}'
    path.write_bytes(raw)
    projects.create(catalog, 'adoption', '')
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, 'adoption', path, adopt=True, overwrite=True)
    assert error.value.issue['code'] == 'adoption_requires_import'
    assert path.read_bytes() == raw
    importing.run(catalog, raw, str(path))
    projects.cite(catalog, 'adoption', 'x')
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, 'adoption', path, adopt=True)
    assert error.value.issue['code'] == 'adoption_requires_overwrite'
    assert path.read_bytes() == raw
    path.write_bytes(raw+b'\n% outside change')
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, 'adoption', path, adopt=True, overwrite=True)
    assert error.value.issue['code'] == 'adoption_requires_import'
    assert path.read_bytes() == raw+b'\n% outside change'
    path.write_bytes(raw)
    result = bibliography.export(catalog, 'adoption', path, adopt=True, overwrite=True)
    assert result['count'] == 1
    assert path.read_bytes().startswith(b'@book{x,')
    assert b'author = {Smith, Alex}' in path.read_bytes()
    assert b'year = {2024}' in path.read_bytes()
