"""Fixed, human-reviewed examples for each output shape."""

import json
import re
from pathlib import Path

from refs.render import render_text
from refs.results import emit


def plain(value: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', value)


RECORD = {
    'citation_key': 'fleuret2023little',
    'metadata': {'type': 'book', 'title': 'The Little Book of Deep Learning', 'author': [{'family': 'Fleuret', 'given': 'François'}], 'issued': {'date-parts': [[2023]]}},
    'matches': [{'field': 'title'}], 'resources': [], 'projects': [], 'revision': 3,
}


def test_record_list_at_fixed_width():
    output = plain(render_text('search', {'items': [RECORD]}, [], terminal=True, width=62))
    assert output == ' fleuret2023little  2023  Fleuret  The Little Book    title \n                                   of Deep Learning         \n1 source'
    assert '\x1b[1m' in render_text('search', {'items': [RECORD]}, [], terminal=True, width=62)


def test_one_record_at_fixed_width():
    output = plain(render_text('show', RECORD, [], terminal=True, width=62))
    assert output == ' Key       fleuret2023little                \n Type      book                             \n Authors   François Fleuret                 \n Year      2023                             \n Title     The Little Book of Deep Learning \n issued    2023                             \n Files     (none)                           \n Projects  (none)                           \n Revision  3                                '


def test_short_rows_at_fixed_width():
    data = {'items': [{'import_id': 'abcdef1234567890', 'origin': 'zotero', 'created': '2026-09-24T12:34:56', 'counts': {'applied': 2, 'unchanged': 1, 'conflict': 0, 'invalid': 0}}]}
    output = plain(render_text('import list', data, [], terminal=True, width=80))
    assert output == ' abcdef12  zotero                   2026-09-24 12:34:56  applied 2, unchanged 1 '


def test_report_at_fixed_width():
    data = {'dry_run': True, 'moves': [{'resource_id': '0123456789abcdef', 'old_path': '/old/paper.pdf', 'new_path': 'lib/papers/paper-b.pdf', 'old_name': 'paper.pdf', 'new_name': 'paper-b.pdf', 'state': 'planned'}], 'unlinked_paths': []}
    output = plain(render_text('reorg', data, [], terminal=True, width=72))
    assert output == '1 file would move, 1 renamed on collision.\n 01234567  /old/paper.pdf          planned \n           lib/papers/paper-b.pdf  renamed '
    assert '\x1b[33m' in render_text('reorg', data, [], terminal=True, width=72)


def test_confirmation_at_fixed_width():
    assert plain(render_text('update', {'citation_key': 'fleuret2023little', 'revision': 3}, [], terminal=True, width=62)) == 'Updated fleuret2023little (revision 3)'


def test_pipe_output_is_unstyled_and_one_row_per_record():
    output = render_text('search', {'items': [RECORD, RECORD | {'citation_key': 'second'}]}, [], terminal=False, width=40)
    assert output.splitlines() == [
        'fleuret2023little\t2023\tFleuret\tbook\t0\tThe Little Book of Deep Learning\ttitle',
        'second\t2023\tFleuret\tbook\t0\tThe Little Book of Deep Learning\ttitle',
        '2 sources',
    ]
    assert '\x1b' not in output and ' | ' not in output


def test_long_path_wraps_only_between_segments():
    old = '/archive/collection/nested/papers/citation-paper.pdf'
    new = '/library/research/articles/citation-paper.pdf'
    data = {'dry_run': True, 'moves': [{'resource_id': '0123456789abcdef', 'old_path': old, 'new_path': new, 'old_name': 'citation-paper.pdf', 'new_name': 'citation-paper.pdf', 'state': 'planned'}], 'unlinked_paths': []}
    output = plain(render_text('reorg', data, [], terminal=True, width=58))
    lines = output.splitlines()[1:]
    assert len(lines) > 2
    for segment in ('archive', 'collection', 'nested', 'papers', 'citation-paper.pdf', 'library', 'research', 'articles'):
        assert any(segment in line for line in lines), segment
    assert '\u200b' not in output


def test_home_path_is_shortened_only_for_human_output(capsys):
    path = str(Path.home() / 'catalog' / 'paper.pdf')
    record = RECORD | {'resources': [{'resolved_path': path}]}
    assert '~/catalog/paper.pdf' in render_text('show', record, [], terminal=False)
    assert '~/catalog/paper.pdf' in plain(render_text('show', record, [], terminal=True, width=72))
    emit('show', record, json_output=True)
    assert json.loads(capsys.readouterr().out)['data']['resources'][0]['resolved_path'] == path
