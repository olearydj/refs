import json

import pytest
from test_zotero_mapping import extracted

from refs import importing
from refs.catalog import connect


def test_batch_rerun_and_dry_run(initialized,zotero_fixture,tmp_path):
    directory = tmp_path/'input'
    extracted(zotero_fixture,directory)
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    preview = initialized('import','--format','zotero','--input',directory,'--dry-run')['data']
    assert preview['counts']['applied'] == 6
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
    first = initialized('import','--format','zotero','--input',directory,'--origin','synthetic')['data']
    assert first['counts'] == dict(applied=6,unchanged=0,conflict=0,invalid=0)
    second = initialized('import','--format','zotero','--input',directory)['data']
    assert second['counts']['unchanged'] == 6
    with connect(tmp_path/'cat') as c:
        assert c.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 12
        assert c.execute('SELECT count(*) FROM sources').fetchone()[0] == 6
        original = c.execute("SELECT raw_bytes FROM originals WHERE format='zotero-json' AND locator LIKE '%ITEM0001.json' LIMIT 1").fetchone()[0]
        assert original == (directory/'items/ITEM0001.json').read_bytes()
        assert c.execute('SELECT count(*) FROM origin_identities').fetchone()[0] == 6


def test_partial_and_bib_accounting(initialized,zotero_fixture,tmp_path):
    directory = tmp_path/'input'
    extracted(zotero_fixture,directory)
    p = directory/'items/ITEM0002.json'
    value=json.loads(p.read_bytes())
    value['data']['itemType']='unsupported'
    p.write_text(json.dumps(value))
    result=initialized('import','--format','zotero','--input',directory,expected=4)['data']
    assert result['counts']['invalid'] == 1 and result['counts']['applied'] == 5
    importing.run(tmp_path/'cat',b'@book{bib,title={Separate Book}}','synthetic.bib')
    with connect(tmp_path/'cat') as c:
        assert c.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 7
        assert c.execute("SELECT count(*) FROM import_entries WHERE status='invalid'").fetchone()[0] == 1


def test_libraries_cannot_steal_binding(initialized,zotero_fixture,tmp_path):
    directory=tmp_path/'input'
    extracted(zotero_fixture,directory)
    initialized('import','--format','zotero','--input',directory)
    path=directory/'manifest.json'
    manifest=json.loads(path.read_bytes())
    manifest['library_uri']='users/456'
    path.write_text(json.dumps(manifest))
    for path in (directory/'items').glob('ITEM*.json'):
        item=json.loads(path.read_bytes())
        item['data']['title']='Different Title'
        path.write_text(json.dumps(item))
    result=initialized('import','--format','zotero','--input',directory,expected=4)['data']
    assert result['counts']['conflict']==6
    with connect(tmp_path/'cat') as c:
        original = {r['item_key']:r['source_id'] for r in c.execute("SELECT * FROM origin_identities WHERE library_uri='users/123'")}
        assert len(original) == 6
        for row in c.execute("SELECT * FROM origin_identities WHERE library_uri='users/456'"):
            assert row['source_id'] == original[row['item_key']]


def test_interrupted_run_keeps_accounting_and_reruns(initialized,zotero_fixture,tmp_path,monkeypatch):
    directory=tmp_path/'input'
    extracted(zotero_fixture,directory)
    apply=importing.apply_zotero
    def interrupted(connection,entry,*args,**kwargs):
        if entry['key']=='ITEM0003':
            raise RuntimeError('interrupted')
        return apply(connection,entry,*args,**kwargs)
    monkeypatch.setattr(importing,'apply_zotero',interrupted)
    with pytest.raises(RuntimeError):
        importing.run_zotero(tmp_path/'cat',directory)
    with connect(tmp_path/'cat') as c:
        assert c.execute('SELECT applied FROM imports').fetchone()[0]==2
        assert c.execute('SELECT count(*) FROM import_entries').fetchone()[0]==2
    monkeypatch.setattr(importing,'apply_zotero',apply)
    result=importing.run_zotero(tmp_path/'cat',directory)
    assert result['counts']['unchanged']==2 and result['counts']['applied']==4
