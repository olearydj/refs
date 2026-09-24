"""A long reorg must not depend on garbage collection to release SQLite files."""
import subprocess
import sys


def run_process(tmp_path, script):
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_forty_moves_under_64_descriptors(initialized, tmp_path, reference_path):
    initialized('add', '--format', 'refs', '--input', reference_path, '--loc', 'topic')
    run_process(tmp_path, '''
import gc, resource, sys
from pathlib import Path
from refs import moves, resources
from refs.catalog import connect
from refs.config import select
home = Path(sys.argv[1])
settings = select(str(home/'config.toml'), str(home/'cat'), no_project_config=True)
resource.setrlimit(resource.RLIMIT_NOFILE, (64, resource.getrlimit(resource.RLIMIT_NOFILE)[1]))
gc.disable()
with connect(home/'cat') as c:
    source = c.execute('SELECT id FROM sources').fetchone()[0]
for index in range(40):
    path = home/f'original-{index}.pdf'
    path.write_bytes(f'synthetic PDF {index}'.encode())
    resources.link(settings, source, path=path)
report = moves.reorg(settings, execute=True)
assert len(report['moves']) == 40
with connect(home/'cat') as c:
    assert c.execute("SELECT count(*) FROM file_operations WHERE state='removed'").fetchone()[0] == 40
for index in range(40):
    assert not (home/f'original-{index}.pdf').exists()
    assert (home/f'lib/topic/original-{index}.pdf').read_bytes() == f'synthetic PDF {index}'.encode()
''')


def test_hundred_connections_keep_descriptor_count(initialized, tmp_path):
    run_process(tmp_path, '''
import fcntl, gc, resource, sys
from pathlib import Path
from refs.catalog import connect
home = Path(sys.argv[1])
resource.setrlimit(resource.RLIMIT_NOFILE, (64, resource.getrlimit(resource.RLIMIT_NOFILE)[1]))
def count():
    found = 0
    for fd in range(64):
        try:
            fcntl.fcntl(fd, fcntl.F_GETFD)
            found += 1
        except OSError:
            pass
    return found
gc.collect()
gc.disable()
before = count()
for _ in range(100):
    with connect(home/'cat') as c:
        c.execute('SELECT schema_version FROM catalog_meta').fetchone()
assert count() == before, (before, count())
''')
