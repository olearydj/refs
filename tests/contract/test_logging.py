"""Durable log invariants, exercised only against disposable catalogs."""

import hashlib
import json
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest
from conftest import REFS_COMMAND


def lines(catalog):
    return [json.loads(line) for line in (catalog/'refs.log').read_text().splitlines()]


def mutations(catalog, name):
    return [line for line in lines(catalog) if line['event'] == name]


def mutation_count(catalog):
    return sum(line['event'] not in {'command.open','command.close','diagnostic'} for line in lines(catalog))


def test_every_mutating_command_emits_a_registered_mutation(initialized, tmp_path, reference_path):
    from refs.logging import EVENTS

    catalog = tmp_path/'cat'
    assert mutations(catalog,'catalog.init')
    assert [line['event'] for line in lines(catalog)[:3]] == ['command.open','catalog.init','command.close']

    def check(command, *args):
        before = mutation_count(catalog)
        result = initialized(*args)['data']
        assert mutation_count(catalog) > before, command
        assert {line['event'] for line in lines(catalog)} <= EVENTS
        return result

    source = check('add','add','--format','refs','--input',reference_path,'--loc','Papers')
    updated = check('update','update',source['id'],'--if-revision',source['revision'],'--set','metadata.title="Changed Title"')
    keyed = check('key set','key','set',source['id'],'--key','changed-key','--if-revision',updated['revision'],'--execute')
    removed = check('remove','remove',source['id'],'--if-revision',keyed['revision'],'--execute')
    check('reactivate','reactivate',source['id'],'--if-revision',removed['revision'],'--execute')
    check('project create','project','create','demo')
    check('project cite','project','cite','demo',source['id'])
    check('export','export','--project','demo','--output',tmp_path/'references.bib')
    check('project uncite','project','uncite','demo',source['id'])
    linked_file = tmp_path/'linked.pdf'
    linked_file.write_bytes(b'linked')
    linked = check('resource add link','resource','add',source['id'],'--path',linked_file)
    check('resource unlink','resource','unlink',linked['id'],'--execute')
    copied_file = tmp_path/'copied.pdf'
    copied_file.write_bytes(b'copy')
    check('resource add copy','resource','add',source['id'],'--path',copied_file,'--copy')
    move_file = tmp_path/'moved.pdf'
    move_file.write_bytes(b'move')
    check('resource add move','resource','add',source['id'],'--path',move_file,'--move','--keep-name')
    reorg_file = tmp_path/'reorg.pdf'
    reorg_file.write_bytes(b'reorg')
    check('resource add link for reorg','resource','add',source['id'],'--path',reorg_file)
    check('reorg','reorg','--source',source['id'],'--execute')
    bib = tmp_path/'input.bib'
    bib.write_bytes(b'@article{other,title={Other Work},year={2020}}')
    check('import','import','--format','bib','--input',bib)
    check('backup','backup','--output',tmp_path/'snapshot')


def test_source_create_update_key_remove_reactivate_log_database_values(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    created = initialized('add','--format','refs','--input',reference_path)['data']
    event = mutations(catalog,'source.create')[-1]
    assert event['target'] == {'id':created['id'],'citation_key':created['citation_key']}
    assert event['after']['revision'] == created['revision'] == 1
    assert event['changes']['record']['new']['metadata'] == created['metadata']
    changed = initialized('update',created['id'],'--if-revision',1,'--set','metadata.title="A Revised Title"')['data']
    event = mutations(catalog,'source.update')[-1]
    assert event['before']['revision'] == 1 and event['after']['revision'] == changed['revision'] == 2
    assert event['changes']['metadata.title'] == {'old':created['metadata']['title'],'new':changed['metadata']['title']}
    keyed = initialized('key','set',created['id'],'--key','revised-key','--if-revision',2,'--execute')['data']
    event = mutations(catalog,'source.key_set')[-1]
    assert event['changes']['citation_key'] == {'old':created['citation_key'],'new':keyed['citation_key']}
    removed = initialized('remove',created['id'],'--if-revision',3,'--execute')['data']
    assert mutations(catalog,'source.remove')[-1]['after']['revision'] == removed['revision']
    active = initialized('reactivate',created['id'],'--if-revision',4,'--execute')['data']
    assert mutations(catalog,'source.reactivate')[-1]['after']['revision'] == active['revision']
    assert initialized('show',created['id'])['data']['state'] == 'active'


def test_later_original_is_logged_without_its_bytes(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    created = initialized('add','--format','refs','--input',reference_path)['data']
    raw = json.dumps(json.loads(reference_path.read_text()),indent=4).encode()
    alternate = tmp_path/'alternate.json'
    alternate.write_bytes(raw)
    initialized('add','--format','refs','--input',alternate)
    event = mutations(catalog,'source.original')[-1]
    assert event['target']['source_id'] == created['id']
    assert event['after']['sha256'] == hashlib.sha256(raw).hexdigest()
    assert raw not in (catalog/'refs.log').read_bytes()
    with sqlite3.connect(catalog/'catalog.sqlite') as connection:
        assert connection.execute('SELECT count(*) FROM originals WHERE source_id=?',(created['id'],)).fetchone()[0] == 2


def test_resource_link_unlink_copy_log_database_values(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'linked.pdf'
    path.write_bytes(b'linked file')
    linked = initialized('resource','add',source['id'],'--path',path)['data']
    event = mutations(catalog,'resource.link')[-1]
    assert event['target']['id'] == linked['id'] and event['after']['path'] == linked['path']
    initialized('resource','unlink',linked['id'],'--execute')
    assert mutations(catalog,'resource.unlink')[-1]['before']['revision'] == linked['revision']
    assert initialized('show',source['id'])['data']['resources'] == []
    copied = initialized('resource','add',source['id'],'--path',path,'--copy')['data']
    event = mutations(catalog,'resource.copy')[-1]
    assert event['target']['id'] == copied['id'] and event['new_path'] == copied['destination']
    assert Path(copied['destination']).read_bytes() == path.read_bytes()


def test_move_log_is_fsynced_before_original_unlink(initialized, tmp_path, reference_path, monkeypatch):
    from refs import logging as action_log
    from refs import moves
    from refs.config import select

    catalog = tmp_path/'cat'
    source = initialized('add','--format','refs','--input',reference_path,'--loc','Papers')['data']
    original = tmp_path/'original.pdf'
    original.write_bytes(b'move sample')
    resource = initialized('resource','add',source['id'],'--path',original)['data']
    settings = select(str(tmp_path/'config.toml'), str(catalog), no_project_config=True)
    target = tmp_path/'lib/Papers/original.pdf'
    checkpoints = []
    monkeypatch.setattr(moves,'checkpoint',lambda point,row: checkpoints.append(point))
    real_unlink = Path.unlink
    real_fsync = os.fsync
    syncs = []

    def watched_fsync(descriptor):
        if os.fstat(descriptor).st_ino == (catalog/'refs.log').stat().st_ino:
            syncs.append('log')
        else:
            syncs.append('other')
        return real_fsync(descriptor)

    monkeypatch.setattr(action_log.os,'fsync',watched_fsync)

    def checked_unlink(path, *args, **kwargs):
        if path == original:
            assert 'recorded' in checkpoints
            assert original.exists()
            event = mutations(catalog,'resource.move')[-1]
            assert event['after']['state'] == 'unlinked' and event['old_path'] == str(original)
            assert event['new_path'] == str(target) and event['digest']
            assert syncs[-1] == 'log'
        return real_unlink(path,*args,**kwargs)

    monkeypatch.setattr(Path,'unlink',checked_unlink)
    moves.move(settings,resource['id'],target)
    assert not original.exists() and target.read_bytes() == b'move sample'
    assert [event['after']['state'] for event in mutations(catalog,'resource.move')] == ['staged','published','recorded','unlinked','removed']
    with sqlite3.connect(catalog/'catalog.sqlite') as connection:
        assert connection.execute('SELECT state FROM file_operations').fetchone()[0] == 'removed'


def test_import_batch_and_entry_log_counts_match_database(initialized, tmp_path):
    from refs import importing

    catalog = tmp_path/'cat'
    raw = b'@article{demo,title={Logged Entry},year={2024}}\n@book{next,title={Another Entry},year={2025}}'
    result = importing.run(catalog,raw,str(tmp_path/'input.bib'))
    batch = result['import_id']
    assert len(mutations(catalog,'import.batch_open')) == len(mutations(catalog,'import.batch_close')) == 1
    assert len(mutations(catalog,'import.entry')) == result['counts']['applied'] == 2
    assert mutations(catalog,'import.batch_open')[-1]['target']['batch_id'] == batch
    assert [event['target']['source_id'] for event in mutations(catalog,'import.entry')] == [entry['source_id'] for entry in result['entries']]
    assert mutations(catalog,'import.batch_close')[-1]['after']['counts'] == result['counts']
    with sqlite3.connect(catalog/'catalog.sqlite') as connection:
        assert connection.execute('SELECT applied FROM imports WHERE id=?',(batch,)).fetchone()[0] == 2


def test_import_reconcile_log_matches_updated_source(initialized, tmp_path):
    from refs import importing, sources

    catalog = tmp_path/'cat'
    importing.run(catalog,b'@book{one,title={First},publisher={Old}}','first.bib')
    batch = importing.run(catalog,b'@book{one,title={Second},publisher={Old}}','second.bib')['import_id']
    revision = importing.show(catalog,batch)['batch_revision']
    importing.reconcile(catalog,batch,['one.metadata.title'],execute=True,revision=revision)
    event = mutations(catalog,'import.reconcile')[-1]
    assert event['target']['batch_id'] == batch
    assert event['changes']['metadata.title'] == {'old':'First','new':'Second'}
    assert sources.show(catalog,'one')['metadata']['title'] == 'Second'


def test_project_export_and_backup_log_matches_outputs(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    source = initialized('add','--format','refs','--input',reference_path)['data']
    project = initialized('project','create','demo')['data']
    assert mutations(catalog,'project.create')[-1]['after']['id'] == project['id']
    initialized('project','cite','demo',source['id'])
    assert mutations(catalog,'project.cite')[-1]['target']['source_id'] == source['id']
    output = tmp_path/'references.bib'
    exported = initialized('export','--project','demo','--output',output)['data']
    assert mutations(catalog,'export.write')[-1]['after']['digest'] == exported['sha256']
    assert output.exists()
    initialized('project','uncite','demo',source['id'])
    assert mutations(catalog,'project.uncite')[-1]['after']['cited'] is False
    backup = tmp_path/'snapshot'
    initialized('backup','--output',backup)
    assert mutations(catalog,'backup.write')[-1]['target']['path'] == str(backup)
    assert (backup/'manifest.json').is_file()


def test_export_adoption_log_matches_target_binding(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    source = initialized('add','--format','refs','--input',reference_path)['data']
    initialized('project','create','demo')
    initialized('project','cite','demo',source['id'])
    produced = tmp_path/'produced.bib'
    initialized('export','--project','demo','--output',produced)
    adopted = tmp_path/'adopted.bib'
    adopted.write_bytes(produced.read_bytes())
    initialized('import','--format','bib','--input',adopted,expected=4)
    initialized('export','--project','demo','--output',adopted,'--adopt')
    event = mutations(catalog,'export.adopt')[-1]
    with sqlite3.connect(catalog/'catalog.sqlite') as connection:
        row = connection.execute('SELECT baseline_digest FROM export_targets WHERE destination=?',(str(adopted),)).fetchone()
    assert event['after']['baseline_digest'] == row[0]


def test_unwritable_log_refuses_mutation_without_database_change(initialized, tmp_path, reference_path):
    catalog = tmp_path/'cat'
    log = catalog/'refs.log'
    before = (catalog/'catalog.sqlite').read_bytes()
    log.chmod(0o400)
    try:
        result = subprocess.run([*REFS_COMMAND,'--json','add','--format','refs','--input',str(reference_path)],
                                env=dict(os.environ,REFS_CONFIG=str(tmp_path/'config.toml'),REFS_CATALOG=str(catalog)),
                                cwd=tmp_path,capture_output=True,text=True)
        assert result.returncode == 5
        assert json.loads(result.stdout)['errors'][0]['code'] == 'log_unwritable'
        assert result.stderr == ''
        assert (catalog/'catalog.sqlite').read_bytes() == before
    finally:
        log.chmod(0o600)


def test_verbose_writes_rich_stderr_while_piped_json_stays_parseable(initialized, tmp_path, cli_env, cli_cwd):
    normal = subprocess.run([*REFS_COMMAND,'--json','paths'],env=cli_env,cwd=cli_cwd,capture_output=True,text=True)
    assert normal.returncode == 0 and normal.stderr == ''
    verbose = subprocess.run([*REFS_COMMAND,'--json','--verbose','paths'],env=cli_env,cwd=cli_cwd,capture_output=True,text=True)
    assert verbose.returncode == 0
    assert json.loads(verbose.stdout)['command'] == 'paths'
    assert 'command.open' in verbose.stderr and 'command.close' in verbose.stderr
    assert all(line['event'] in {'command.open','command.close','catalog.init'} for line in lines(tmp_path/'cat'))


def test_original_input_bytes_never_appear_in_log(initialized, tmp_path):
    raw = b'@article{proof,title={Never Embed Original Bytes},year={2024}}'
    path = tmp_path/'input.bib'
    path.write_bytes(raw)
    initialized('import','--format','bib','--input',path)
    assert raw not in (tmp_path/'cat/refs.log').read_bytes()


@pytest.mark.parametrize('command', [
    ('show', 'smith-2024-learningPython'), ('list',), ('search', 'Python'),
    ('summary',), ('kinds',), ('resource', 'check'), ('schema',),
    ('config', 'show'), ('paths',), ('project', 'show'), ('import', 'list'),
    ('collection', 'list'),
])
def test_read_only_commands_succeed_with_unwritable_log(initialized, tmp_path, reference_path, command):
    initialized('add', '--format', 'refs', '--input', reference_path)
    log = tmp_path / 'cat/refs.log'
    before_log = log.read_bytes()
    before_db = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    log.chmod(0o400)
    try:
        result = initialized(*command)
        assert result['errors'] == []
        assert result['data']
        assert log.read_bytes() == before_log
        assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before_db
    finally:
        log.chmod(0o600)


@pytest.mark.parametrize('command', [('--help',), ('add', '--help'), ('resource', '--help'), ('resource', 'add', '--help')])
@pytest.mark.parametrize('log_state', ['absent', 'writable', 'unwritable'])
def test_help_exits_zero_without_touching_log(initialized, tmp_path, cli_env, cli_cwd, command, log_state):
    log = tmp_path / 'cat/refs.log'
    before = log.read_bytes()
    if log_state == 'absent':
        log.unlink()
    elif log_state == 'unwritable':
        log.chmod(0o400)
    try:
        result = subprocess.run([*REFS_COMMAND, *command], env=cli_env, cwd=cli_cwd, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'Usage:' in result.stdout
        assert result.stderr == ''
        if log_state == 'absent':
            assert not log.exists()
        else:
            assert log.read_bytes() == before
    finally:
        if log.exists():
            log.chmod(0o600)
