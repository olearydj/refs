"""Run one CSL array through the public add command in a single sandboxed process."""

import json
import sys
from collections import Counter
from pathlib import Path

from typer.testing import CliRunner

from refs import catalog
from refs.cli import app
from refs.results import RefError


def run(config: Path, catalog_path: Path, source: Path, project: str) -> dict:
    items = json.loads(source.read_bytes())
    if not isinstance(items, list):
        raise ValueError('CSL fixture must be an array')
    runner = CliRunner()
    prefix = ['--json', '--no-project-config', '--config', str(config), '--catalog', str(catalog_path)]

    def call(*args: str, input: str | None = None) -> tuple[int, dict]:
        result = runner.invoke(app, [*prefix, *args], input=input)
        if isinstance(result.exception, RefError):
            error = result.exception
            return error.exit_code, dict(data=error.data, errors=[error.issue])
        if result.exception is not None:
            raise result.exception
        try:
            return result.exit_code, json.loads(result.stdout)
        except ValueError as exc:
            raise AssertionError(f'No JSON from {args}: {result.exit_code} {result.stdout} {result.stderr}') from exc

    code, created = call('project', 'create', project)
    if code:
        raise AssertionError(f'Could not create the CSL fixture project: {created}')
    with catalog.connect(catalog_path) as connection:
        before = connection.execute('SELECT count(*) FROM sources').fetchone()[0]
    first, first_codes, repeat, repeat_codes = Counter(), Counter(), Counter(), Counter()
    examples: dict[str, list[dict]] = {}
    source_ids = set()
    for pass_number in (1, 2):
        outcomes, codes = (first, first_codes) if pass_number == 1 else (repeat, repeat_codes)
        for index, item in enumerate(items):
            code, envelope = call('add', '--format', 'csljson', '--input', '-', input=json.dumps(item, ensure_ascii=False))
            if code not in (0, 2, 3):
                raise AssertionError(f'Unexpected CSL add exit at {source.name}:{index}: {code}: {envelope.get("errors")}')
            data = envelope.get('data') or {}
            errors = envelope.get('errors') or []
            outcome = data.get('outcome') if code else data.get('outcome', 'invalid')
            outcome = outcome or 'invalid'
            if outcome not in ('created', 'already_present', 'needs_attention', 'invalid'):
                raise AssertionError(f'Unexpected CSL add outcome at {source.name}:{index}: {outcome}')
            outcomes[outcome] += 1
            if code:
                issue = errors[0] if errors else {'code': 'missing_error', 'message': 'No error in envelope'}
                codes[issue['code']] += 1
                if pass_number == 1 and len(examples.setdefault(issue['code'], [])) < 3:
                    examples[issue['code']].append(dict(index=index, id=item.get('id') if isinstance(item, dict) else None,
                                                         reason=issue['message'], details=issue.get('details', {})))
            elif pass_number == 1 and data.get('id'):
                source_ids.add(data['id'])
        if pass_number == 1:
            for source_id in sorted(source_ids):
                cite_code, cited = call('project', 'cite', project, source_id)
                if cite_code:
                    raise AssertionError(f'Could not cite CSL source {source_id}: {cited}')
    with catalog.connect(catalog_path) as connection:
        after = connection.execute('SELECT count(*) FROM sources').fetchone()[0]
    if repeat['created'] or after - before != first['created']:
        raise AssertionError(f'CSL re-add created records: {source.name}: {dict(repeat)}')
    return dict(outcomes=dict(first), entry_codes=dict(first_codes), examples=examples, reimport=dict(repeat), reimport_codes=dict(repeat_codes), cited_sources=len(source_ids), source_rows_added=after-before)


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]), ensure_ascii=False))
