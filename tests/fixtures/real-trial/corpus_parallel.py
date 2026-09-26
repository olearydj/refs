"""Run a corpus gate in parallel by file: shard the manifest, run one gate process per shard, merge the reports.

Each shard gets its own working directory and its own copy of the owner's sample, so the gates never share a catalog;
the shared-catalog history mode remains the serial gate on a small sample. The gate scripts are unchanged; this driver
only writes shard manifests, launches the existing scripts, and merges their JSON reports in manifest order.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = {'json': 'corpus_round_three.py', 'bib': 'move_rehearsal.py'}


def shard_manifest(manifest: dict, workers: int) -> list[dict]:
    """Round-robin the manifest's files over the workers; every other manifest key is copied to each shard."""
    if workers < 1:
        raise ValueError('workers must be at least 1')
    files = manifest['files']
    shards = []
    for index in range(min(workers, len(files)) or 1):
        shard = {key: value for key, value in manifest.items() if key != 'files'}
        shard['files'] = files[index::workers]
        shard['shard'] = dict(index=index, of=workers)
        shards.append(shard)
    return shards


def command_for(script: str, sample: Path, work: Path, manifest: Path) -> list[str]:
    path = HERE / SCRIPTS[script]
    if script == 'json':
        return [sys.executable, str(path), '--sample', str(sample), '--work', str(work), '--manifest', str(manifest)]
    return [sys.executable, str(path), '--sample', str(sample), '--phase6-work', str(work), '--corpus-manifest', str(manifest)]


def merge_reports(manifest: dict, reports: list[dict]) -> dict:
    """Merge shard reports into one report in manifest order; outcomes and disk peaks sum, wall time is the slowest shard."""
    order = {entry['path']: index for index, entry in enumerate(manifest['files'])}
    results = sorted((result for report in reports for result in report.get('results', [])), key=lambda result: order[result['path']])
    classification = sorted((row for report in reports for row in report.get('classification', [])), key=lambda row: order[row['path']])
    outcomes = sum((Counter(report.get('outcomes', {})) for report in reports), Counter())
    per_file = sorted(((result.get('seconds', 0), result['path']) for result in results), reverse=True)
    return dict(classification=classification, results=results, total_entries=sum(report.get('total_entries', 0) for report in reports),
                outcomes=dict(outcomes),
                post_resource_check=[report.get('post_resource_check') for report in reports],
                restore=[report.get('restore') for report in reports],
                wall_seconds=max((report.get('wall_seconds', 0) for report in reports), default=0),
                shard_wall_seconds=[report.get('wall_seconds', 0) for report in reports],
                peak_temporary_bytes=sum(report.get('peak_temporary_bytes', 0) for report in reports),
                slowest_files=[dict(seconds=seconds, path=path) for seconds, path in per_file[:10]],
                ceilings=manifest.get('ceilings'), workers=len(reports))


def run(script: str, sample: Path, work: Path, manifest_path: Path, workers: int, launcher=subprocess.run) -> dict:
    manifest = json.loads(manifest_path.read_text())
    work.mkdir(parents=True, exist_ok=True)
    shards = shard_manifest(manifest, workers)
    processes = []
    started = time.monotonic()
    for shard in shards:
        index = shard['shard']['index']
        shard_dir = work / f'shard-{index}'
        shard_dir.mkdir(exist_ok=True)
        shard_manifest_path = shard_dir / 'manifest.json'
        shard_manifest_path.write_text(json.dumps(shard, indent=2))
        processes.append((index, shard_dir, command_for(script, sample, shard_dir / 'work', shard_manifest_path)))
    if launcher is subprocess.run:
        running = [(index, shard_dir, subprocess.Popen(command, stdout=(shard_dir / 'report.json').open('w'), stderr=(shard_dir / 'stderr.txt').open('w'))) for index, shard_dir, command in processes]
        failures = [(index, process.wait()) for index, _, process in running if process.wait() != 0]
    else:
        failures = []
        for index, shard_dir, command in processes:
            completed = launcher(command, capture_output=True, text=True)
            (shard_dir / 'report.json').write_text(completed.stdout)
            (shard_dir / 'stderr.txt').write_text(completed.stderr)
            if completed.returncode != 0:
                failures.append((index, completed.returncode))
    if failures:
        raise RuntimeError('Shards failed: ' + ', '.join(f'shard {index} exit {code}' for index, code in failures))
    reports = [json.loads((shard_dir / 'report.json').read_text()) for _, shard_dir, _ in processes]
    merged = merge_reports(manifest, reports)
    merged['driver_wall_seconds'] = round(time.monotonic() - started, 2)
    return merged


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--script', choices=sorted(SCRIPTS), required=True)
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = parser.parse_args()
    print(json.dumps(run(args.script, args.sample.resolve(), args.work.resolve(), args.manifest.resolve(), args.workers), indent=2, ensure_ascii=False))
