import os
import subprocess

from refs import importing


def test_readable_inspection_and_reconciliation(initialized,tmp_path):
    catalog=tmp_path/'cat'
    importing.run(catalog,b'@book{one,title={First},publisher={Old}}','synthetic.bib')
    batch=importing.run(catalog,b'@book{one,title={Second},publisher={New},unmapped={Preserved}}','synthetic.bib')['import_id']
    env=dict(os.environ,REFS_CONFIG=str(tmp_path/'config.toml'),REFS_CATALOG=str(catalog))
    shown=subprocess.run(['refs','import','show',batch],env=env,capture_output=True,text=True)
    assert shown.returncode==0,shown.stderr
    assert shown.stdout.startswith('Import '+batch)
    assert 'one: conflict (source revision' in shown.stdout
    assert 'current "First"; incoming "Second"' in shown.stdout
    assert 'Candidates:' in shown.stdout and 'unmapped' in shown.stdout
    preview=subprocess.run(['refs','import','reconcile',batch,'--take-incoming','one.metadata.title'],env=env,capture_output=True,text=True)
    assert preview.returncode==0,preview.stderr
    assert preview.stdout.startswith('Preview: Reconciled import '+batch)
    assert 'Take incoming metadata.title: "Second"' in preview.stdout
    assert 'metadata.publisher: current "Old"; incoming "New"' in preview.stdout
    revision=importing.show(catalog,batch)['batch_revision']
    accepted=subprocess.run(['refs','import','reconcile',batch,'--take-incoming','one','--execute','--if-batch-revision',str(revision)],env=env,capture_output=True,text=True)
    assert accepted.returncode==0 and accepted.stdout.startswith('Reconciled import')
    failed=subprocess.run(['refs','import','show','missing'],env=env,capture_output=True,text=True)
    assert failed.returncode==3 and 'Use the import_id' in failed.stderr
