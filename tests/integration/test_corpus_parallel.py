"""The parallel corpus driver shards a manifest, runs one gate per shard, and merges reports in manifest order."""

import json
import runpy
import subprocess
from pathlib import Path

HARNESS = Path(__file__).parents[1] / 'fixtures' / 'real-trial' / 'corpus_parallel.py'
driver = runpy.run_path(str(HARNESS))


def manifest_with(n: int) -> dict:
    return dict(ceilings=dict(files=100, entries=10000, seconds=600, temporary_bytes=10**9),
                files=[dict(path=f'/corpus/file-{i}.bib', source='synthetic', entries=i + 1) for i in range(n)])


def test_shards_round_robin_and_keep_every_other_key():
    shards = driver['shard_manifest'](manifest_with(5), 2)
    assert [f['path'] for f in shards[0]['files']] == ['/corpus/file-0.bib', '/corpus/file-2.bib', '/corpus/file-4.bib']
    assert [f['path'] for f in shards[1]['files']] == ['/corpus/file-1.bib', '/corpus/file-3.bib']
    assert all(shard['ceilings'] == manifest_with(5)['ceilings'] for shard in shards)
    assert len(driver['shard_manifest'](manifest_with(1), 8)) == 1


def fake_gate(command, capture_output, text):
    """Stand in for a gate script: report one result per file in its shard manifest, with a wall time."""
    manifest = json.loads(Path(command[command.index('--manifest') + 1] if '--manifest' in command else command[command.index('--corpus-manifest') + 1]).read_text())
    files = manifest['files']
    report = dict(classification=[dict(f) for f in files],
                  results=[f | dict(outcomes=dict(applied=f['entries']), seconds=float(f['entries'])) for f in files],
                  total_entries=sum(f['entries'] for f in files), outcomes=dict(applied=sum(f['entries'] for f in files)),
                  post_resource_check={'recorded:available': len(files)}, restore=dict(tables=16),
                  wall_seconds=float(sum(f['entries'] for f in files)), peak_temporary_bytes=1000 * len(files))
    return subprocess.CompletedProcess(command, 0, json.dumps(report), '')


def test_two_workers_merge_to_the_same_report_as_one(tmp_path):
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest_with(4)))
    one = driver['run']('json', tmp_path / 'sample', tmp_path / 'one', manifest_path, 1, launcher=fake_gate)
    two = driver['run']('bib', tmp_path / 'sample', tmp_path / 'two', manifest_path, 2, launcher=fake_gate)
    for key in ('classification', 'results', 'total_entries', 'outcomes'):
        assert one[key] == two[key], key
    assert [r['path'] for r in two['results']] == [f['path'] for f in manifest_with(4)['files']]
    assert one['workers'] == 1 and two['workers'] == 2
    assert two['wall_seconds'] == max(two['shard_wall_seconds']) and two['wall_seconds'] < one['wall_seconds']
    assert two['peak_temporary_bytes'] == one['peak_temporary_bytes']
    assert two['slowest_files'][0]['path'] == '/corpus/file-3.bib'
    assert (tmp_path / 'two' / 'shard-1' / 'manifest.json').exists()


def test_failed_shard_is_reported_by_index(tmp_path):
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest_with(3)))

    def failing(command, capture_output, text):
        completed = fake_gate(command, capture_output, text)
        return subprocess.CompletedProcess(command, 3, completed.stdout, 'boom') if 'shard-1' in ' '.join(command) else completed

    try:
        driver['run']('json', tmp_path / 'sample', tmp_path / 'work', manifest_path, 3, launcher=failing)
    except RuntimeError as exc:
        assert 'shard 1 exit 3' in str(exc)
    else:
        raise AssertionError('a failed shard must fail the run')
