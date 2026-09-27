"""Human output shapes; structured output remains the result envelope."""

import json
import shutil
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.text import Text

from refs.display import authors, metadata_text, resource_path
from refs.naming import issued_year


def project_text(data: dict) -> str:
    if 'items' in data:
        return '\n'.join(item['name'] for item in data['items']) or '(no projects)'
    return f"Project: {data['name']}\n" + record_list('list', {'items': data['sources']}, False, 80)



def warning_lines(command: str, warnings: list[dict]) -> list[str]:
    if command != 'export':
        return ['Warning: ' + warning['message'] for warning in warnings]
    groups = {}
    for warning in warnings:
        if warning['code'] == 'empty_selection':
            warning = dict(warning)
            warning['message'] = 'No cited active sources were selected'
        if warning.get('details', {}).get('class') == 'info':
            continue
        group = warning['code']
        groups.setdefault(group, []).append(warning)
    lines = []
    descriptions = {
        'unassessed_import': 'have imported fields preserved only in the catalog',
        'field_omitted': 'have fields without a portable slot',
        'name_particle_fallback': 'use portable names with consumer-defined particle behavior',
        'literal_issued_year': 'use literal issued dates; check the rendered dates',
        'container_title_case': 'use catalog casing for container titles; check proper names',
        'tex_decoded': 'use decoded TeX name forms; check the rendered spelling',
        'missing_author': 'have no supplied author or editor',
        'missing_journal': 'have no supplied journal',
        'missing_issued': 'have no supplied issued date',
        'language_unspecified': 'need their title language checked',
        'date_range_projected': 'project issued ranges to the start year and shared month',
        'arxiv_fallback': 'use portable arXiv fields',
        'journal_series_fallback': 'use series with consumer-dependent support',
        'collection_editor_fallback': 'emit collection editors as editors',
        'oclc_omission': 'retain OCLC identifiers only in the catalog',
        'container_author_omission': 'use bookauthor, which classic styles may omit',
    }
    for group, notices in groups.items():
        keys = sorted({notice.get('details', {}).get('citation_key', '(selection)') for notice in notices})
        if len(notices) == 1:
            lines.append(f"Warning: {keys[0]}: {notices[0]['message']}")
            continue
        description = descriptions.get(group, 'use a documented fallback: ' + group.replace('_', ' '))
        if group == 'type_fallback':
            description = 'use the portable @misc fallback' if all('@misc' in notice['message'] for notice in notices) else 'use portable type fallbacks'
        noun = 'entry' if len(keys) == 1 else 'entries'
        examples = ', '.join(keys[:5])
        if len(keys)>5:
            examples += f'; {len(keys)-5} more, see --json'
        lines.append(f"Warning: {len(keys)} {noun} {description} ({examples})")
    return lines

def import_text(command: str, data: dict, terminal: bool, width: int) -> str:
    if command == 'import':
        counts = data['counts']
        summary = f"Imported {counts['applied']}, unchanged {counts['unchanged']}, conflicts {counts['conflict']}, invalid {counts['invalid']} from {data['input']}"
    else:
        verb = 'Import' if command == 'import show' else 'Reconciled import'
        summary = f"{verb} {data['import_id'][:8]} (batch revision {data['batch_revision']})"
    rows = []
    for entry in data['entries']:
        key = entry.get('citation_key') or entry.get('item_key') or '(unreadable key)'
        binding = entry.get('binding', {})
        if command != 'import' or entry.get('status') in ('conflict', 'invalid'):
            status = entry.get('status', 'selected')
            if entry.get('source_revision'):
                status += f" (source revision {entry['source_revision']})"
            rows.append([key, status, entry.get('message') or ''])
            candidates = entry.get('candidates', entry.get('details', {}).get('source_ids', []))
            if candidates:
                rows.append(['', 'Candidates', ', '.join(candidates)])
            for change in binding.get('conflicts', []) if command != 'import reconcile' else entry.get('remaining_conflicts', []):
                rows.append(['', change['path'], f"current {json.dumps(change['current'], ensure_ascii=False)}; incoming {json.dumps(change['incoming'], ensure_ascii=False)}"])
        if binding.get('bound') and (binding.get('incoming_key') != binding.get('catalog_key') or binding.get('filled')):
            detail = f"Bound {key} to {binding['catalog_key']}"
            if binding.get('filled'):
                detail += '; filled ' + ', '.join(binding['filled'])
            rows.append(['', 'Binding', detail])
        for decision in entry.get('decisions', []):
            label, value = ('Keep current', decision['current']) if decision['action'] == 'keep_current' else ('Take incoming', decision['incoming'])
            rows.append(['', label + ' ' + decision['path'], json.dumps(value, ensure_ascii=False)])
        for limitation in entry.get('limitations', []):
            rows.append(['', limitation['field'], limitation['reason']])
        for warning in entry.get('warnings', []):
            rows.append(['', 'Warning', f"{key}: {warning['message']}"])
    for kind, count in data.get('preservation', {}).items():
        if count:
            rows.append(['', 'Preservation', f"{count} {kind.replace('_', ' ')} skipped as catalog content; retain the original Zotero archive"])
    return summary + '\n' + (table_rows(rows, wrap=2, styles={0: 'bold', 1: 'dim'}, terminal=terminal, width=width) if rows else '(no entries)')


def home_paths(value: str) -> str:
    home = str(Path.home()) + '/'
    return value.replace(home, '~/')


def path_lines(value: str, width: int) -> str:
    """Give Rich explicit breaks at separators, leaving each path segment intact."""
    parts = value.replace('/', '/\u200b').split('\u200b')
    lines, current = [], ''
    for part in parts:
        if current and len(current.replace('\u200b', '')) + len(part) > width:
            lines.append(current)
            current = part + ('\u200b' if part.endswith('/') else '')
        else:
            current += part + ('\u200b' if part.endswith('/') else '')
    return '\n'.join([*lines, current])


def table_rows(rows: list[list[str]], *, wrap: int | None = None, styles: dict[int, str] | None = None, limits: dict[int, int] | None = None, fixed: set[int] | None = None, expand: bool = False, key_cells: set[tuple[int, int]] | None = None, path_cells: set[tuple[int, int]] | None = None, terminal: bool = False, width: int = 80) -> str:
    """One boxless, headerless table; pipe output is one TSV row per record."""
    if not rows:
        return ''
    if not terminal:
        return '\n'.join('\t'.join(home_paths(str(cell)).replace('\n', ' ') if (row_index, index) in (path_cells or set()) else str(cell).replace('\n', ' ') for index, cell in enumerate(row)) for row_index, row in enumerate(rows))
    output = StringIO()
    console = Console(file=output, force_terminal=True, color_system='standard', no_color=False, width=width, highlight=False, legacy_windows=False, _environ={})
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1), expand=expand)
    for index in range(len(rows[0])):
        table.add_column(no_wrap=index != wrap, overflow='fold' if index == wrap else 'ellipsis', style=(styles or {}).get(index), max_width=(limits or {}).get(index), min_width=12 if index == wrap else (limits or {}).get(index, 0) if index in (fixed or set()) else 0, ratio=1 if index == wrap else None)
    for row_index, row in enumerate(rows):
        cells = []
        for index, cell in enumerate(row):
            is_path = (row_index, index) in (path_cells or set())
            value = home_paths(str(cell)) if is_path else str(cell).replace('\n', ' ')
            if is_path:
                value = path_lines(value, (limits or {}).get(index, width))
            style = 'bold' if (row_index, index) in (key_cells or set()) else 'yellow' if value == 'renamed' or 'Warning' in row else 'red' if value.startswith('Error:') else ''
            cells.append(Text(value, style=style))
        table.add_row(*cells)
    console.print(table)
    return output.getvalue().replace('\u200b', '').rstrip('\n')


def styled_line(value: str, style: str, terminal: bool, width: int) -> str:
    if not terminal:
        return value
    output = StringIO()
    Console(file=output, force_terminal=True, color_system='standard', no_color=False, width=width, highlight=False, _environ={}).print(Text(value, style=style))
    return output.getvalue().rstrip('\n')


def style_key(value: str, key: str, terminal: bool, width: int) -> str:
    if not terminal or not key or key not in value:
        return value
    before, after = value.split(key, 1)
    output = StringIO()
    Console(file=output, force_terminal=True, color_system='standard', no_color=False, width=width, highlight=False, _environ={}).print(Text.assemble(before, (key, 'bold'), after))
    return output.getvalue().rstrip('\n')


def type_label(record: dict) -> str:
    native = record.get('native_type', {}).get('value')
    return record['metadata']['type'] + (f' ({native})' if native else '')


def record_list(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    items = data['items'] if 'items' in data else data['sources']
    if not items:
        return '(no sources)'
    matches = command == 'search' and any(item.get('matches') for item in items)
    # Keep the title useful first; comparison extras disappear at narrower widths.
    extras = width >= 100 if terminal else True
    count = width >= 120 if terminal else True
    rows = []
    for item in items:
        first = next(iter(item['metadata'].get('author', [])), {})
        creator = first.get('family') or first.get('literal') or next(iter(authors(item)), '(no author)')
        row = [item['citation_key'], issued_year(item), creator]
        if extras:
            row.append(type_label(item))
        if count:
            row.append(str(len(item.get('resources', []))))
        title_index = len(row)
        row.append(item['metadata'].get('title', '(no title)'))
        if matches:
            row.append(', '.join(dict.fromkeys(match['field'] for match in item.get('matches', []))))
        rows.append(row)
    styles = {0: 'bold'}
    for index in range(3, len(rows[0])):
        if index == title_index:
            continue
        styles[index] = 'dim'
    limits = {0: max(len(row[0]) for row in rows), 1: 4, 2: 13}
    fixed = {0}
    if extras:
        limits[3] = max(len(row[3]) for row in rows)
        fixed.add(3)
    if count:
        limits[title_index - 1] = 4
        fixed.add(title_index - 1)
    if matches:
        limits[len(rows[0]) - 1] = max(len(row[-1]) for row in rows)
    if terminal:
        occupied = sum(min(max(len(str(row[index])) for row in rows), limits.get(index, width)) for index in range(len(rows[0])) if index != title_index)
        limits[title_index] = max(12, width - occupied - 2 * len(rows[0]) - 2)
    rendered = table_rows(rows, wrap=title_index, styles=styles, limits=limits, fixed=fixed, terminal=terminal, width=width)
    shown, total, offset = len(items), data.get('total'), data.get('offset', 0)
    footer = f"{shown} {'source' if shown == 1 else 'sources'}"
    if total is not None and total > offset + shown:
        footer = f"{shown} of {total} sources shown; --offset {offset + shown} for the next page, --limit 1000 for up to 1000 at once"
    return rendered + '\n' + styled_line(footer, 'dim', terminal, width)


def one_record(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    metadata = data['metadata']
    rows = [
        ['Key', data['citation_key']], ['Type', type_label(data)],
        ['Authors', '; '.join(authors(data)) or '(not supplied)'],
        ['Year', issued_year(data)], ['Title', metadata.get('title', '(not supplied)')],
    ]
    rows.extend([field, metadata_text(metadata[field])] for field in sorted(set(metadata) - {'type', 'author', 'title'}) if metadata[field] not in (None, '', [], {}))
    if data.get('loc'):
        rows.append(['loc', data['loc']])
    for limitation in data.get('limitations', []):
        rows.append(['Limitations', limitation['reason'] if limitation['reason'].startswith('Preserved from import:') else f"{limitation['field']}: {limitation['reason']}"])
    for resource in data.get('resources', []):
        rows.append(['Files', resource_path(resource) + (f"  {resource['label']}" if resource.get('label') else '')])
    if not data.get('resources'):
        rows.append(['Files', '(none)'])
    rows.append(['Projects', ', '.join(item['name'] for item in data.get('projects', [])) or '(none)'])
    rows.append(['Revision', str(data.get('revision', ''))])
    return table_rows(rows, wrap=1, styles={0: 'dim'}, limits={1: max(20, width - 22)} if terminal else None, fixed={1}, key_cells={(0, 1)}, path_cells={(index, 1) for index, row in enumerate(rows) if row[0] == 'Files' and row[1] != '(none)'}, terminal=terminal, width=width)


def short_rows(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    rows = []
    if command == 'import list':
        for item in data['items']:
            counts = ', '.join(f'{name} {count}' for name, count in item['counts'].items() if count) or '0 entries'
            created = datetime.fromisoformat(item['created']).strftime('%Y-%m-%d %H:%M:%S')
            rows.append([item['import_id'][:8], item['origin'], created, counts])
    elif command == 'collection list':
        rows = [[item['path'], str(item['count']) + ' active sources', item['library_uri']] for item in data['items']]
    elif command == 'resource check':
        from refs.resources import PLACEMENT_KINDS
        for item in data['items']:
            label = PLACEMENT_KINDS.get(item.get('kind'), item['status'])
            if item.get('kind') and item['status'] not in ('available', 'unfinished'):
                label += f" ({item['status']})"
            path = resource_path(item)
            rows.append([label, path, item.get('hint', '')])
            if item.get('kind') == 'unfinished':
                rows.append(['', item['new_path'], item['state']])
    elif command == 'open':
        rows = [[item['id'], resource_path(item)] for item in data['choices']]
    elif command == 'reorg':
        for item in data['moves']:
            rows.append([(item.get('resource_id') or '')[:8], item['old_path'], item.get('state', '')])
            rows.append(['', item['new_path'], 'renamed' if item.get('old_name') != item.get('new_name') else item.get('error') or ''])
        rows.extend([['', path, 'unlinked'] for path in data.get('unlinked_paths', [])])
    else:
        raise KeyError(command)
    empty = {'import list': '(no imports)', 'collection list': '(no collections)', 'resource check': '(no resources)', 'open': '(no resources)', 'reorg': '(no moves)'}[command]
    if not rows:
        return empty
    styles = {0: 'dim'} if command == 'resource check' else {}
    wrap = 1 if command in ('reorg', 'resource check', 'import list') else None
    limits = None
    if terminal and wrap is not None:
        limits = {wrap: max(16, width - 30)}
        if command == 'import list':
            count_width = max(len(row[3]) for row in rows)
            limits = {0: 8, 1: max(12, width - 8 - 19 - count_width - 10), 2: 19, 3: count_width}
        elif command == 'reorg':
            limits[0] = 8
            limits[2] = 12
        else:
            limits[0] = 28
            limits[2] = 24
    paths = command in ('import list', 'resource check', 'open', 'reorg')
    fixed = ({0, 2, 3} if command == 'import list' else set()) | ({1} if paths and terminal and wrap == 1 else set())
    body = table_rows(rows, wrap=wrap, styles=styles, limits=limits, fixed=fixed, expand=command == 'import list', path_cells={(index, 1) for index in range(len(rows))} if paths else None, terminal=terminal, width=width)
    if command == 'open':
        return 'Choose a resource with --resource:\n' + body
    if command == 'reorg':
        renamed = sum(item.get('old_name') != item.get('new_name') for item in data['moves'])
        verb = 'would move' if data.get('dry_run') else 'moved'
        number = len(data['moves'])
        return f"{number} {'file' if number == 1 else 'files'} {verb}, {renamed} renamed on collision.\n" + body
    return body


def report_text(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    if command == 'reorg':
        return short_rows(command, data, terminal, width)
    if command == 'export':
        if 'forgotten' in data:
            return ('Would forget ' if data['dry_run'] else 'Forgot ') + data['output'] + ' (file unchanged)'
        if 'targets' in data:
            return table_rows([[r['output'], r['profile'], r['outcome'], r.get('error', {}).get('message', str(r.get('count', 0)) + ' entries')] for r in data['targets']], terminal=terminal, width=width)
        count = data['count']
        return f"Wrote {data['output']} ({count} entries, {len(warnings or [])} warnings)" if count else f"Wrote {data['output']} (0 entries)"
    if command.startswith('import'):
        return import_text(command, data, terminal, width)
    raise KeyError(command)


def confirmation(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    key, revision = data.get('citation_key', ''), data.get('revision', '')
    if command == 'paths':
        return table_rows([[label, data[name]['path'] or '(not configured)'] for name, label in [('config', 'Configuration'), ('catalog', 'Catalog'), ('library', 'Library')]], wrap=1, limits={1: max(20, width - 20)} if terminal else None, fixed={1}, path_cells={(0, 1), (1, 1), (2, 1)}, terminal=terminal, width=width)
    if command == 'config show':
        return 'Configuration: ' + str(data['config']) + ''.join(f"\n{name} = {value} ({data['origins'].get(name, 'default')})" for name, value in data['values'].items())
    if command == 'kinds':
        return table_rows([['Kind', 'Type', 'Defining fields', 'Announce'], *[[item['name'], item['type'], ', '.join(f'{path}={value}' for path, value in item['fields'].items()) or '(type alone)', str(item.get('announce', True)).lower()] for item in data['items']]], terminal=terminal, width=width)
    if command == 'schema':
        return '\n'.join(data['schemas']) if 'schemas' in data else json.dumps(data, ensure_ascii=False, indent=2)
    if command == 'project show' and 'items' in data:
        return project_text(data)
    if command == 'project create':
        return f"Created project {data['name']}"
    if command == 'project cite':
        return f"Cited {data['cited']} in {data['project_name']} ({data['already_cited']} already cited)" if 'already_cited' in data else f"Cited {key} in {data['project_name']}"
    if command == 'project uncite':
        return f"Uncited {key} from {data['project_name']}"
    if command == 'add':
        return f"Already present: {key} (revision {revision})" if data.get('outcome') == 'already_present' else f"Created {key}"
    if command == 'resource add':
        if data.get('duplicate_resource_id'):
            return f"Not copied: {data['path']} is already attached to {key}"
        if 'destination' in data:
            return f"{'Moved' if data.get('moved') else 'Copied'} {resource_path(data['copied_from'])} to {data['destination']} for {key}"
        return f"Linked {resource_path(data)} to {key}"
    if command == 'resource unlink':
        return f"Resource {data['id']} is already unlinked" if data.get('unchanged') else f"Unlinked {resource_path(data)} from {key}"
    if command == 'open':
        return f"Opened {data['path']} for {key}"
    templates = {
        'backup': lambda: f"Wrote snapshot {data['output']} (external file bytes excluded)",
        'init': lambda: f"Initialized catalog at {data['catalog_path']} (library: {data.get('library') or 'none'})",
        'update': lambda: f"Updated {key} (revision {revision})",
        'key set': lambda: f"Renamed {data['previous_key']} to {key}",
        'remove': lambda: f"Removed {key}",
        'reactivate': lambda: f"Reactivated {key}",
    }
    return templates[command]()


def summary_text(command: str, data: dict, terminal: bool, width: int, warnings: list[dict] | None = None) -> str:
    def section(title, rows):
        return styled_line(title, 'bold', terminal, width) + '\n' + (table_rows(rows, wrap=None, styles={0: 'dim'}, terminal=terminal, width=width) if rows else '  (none)')
    catalog, sources, files_, imports = data['catalog'], data['sources'], data['files'], data['imports']
    parts = [section('Catalog', [
        ['Path', catalog['path']], ['Schema', str(catalog['schema_version'])], ['Revision', str(catalog['revision'])],
        ['Sources', f"{sources['active']} active, {sources['removed']} removed; {sources['with_files']} with files, {sources['without_files']} without"],
        ['Files', f"{files_['managed']} managed ({files_['unfiled']} under unfiled), {files_['linked']} linked, {files_['missing']} missing, {files_['unrecorded']} unrecorded"],
        ['Imports', (f"{imports['batches']} batches, {imports['open_conflicts']} open conflicts" + (f"; last {imports['last']['origin']} at {imports['last']['started'][:19]}" if imports['last'] else ''))],
    ])]
    parts.append(section('Sources by type', [[kind, str(count)] for kind, count in data['types'].items()]))
    kind_rows = [[name, str(count)] for name, count in data['kinds']['assigned'].items()]
    kind_rows += [[f'unassigned {kind}', str(count)] for kind, count in data['kinds']['unassigned'].items()]
    parts.append(section('Kinds', kind_rows))
    parts.append(section('Locations', [[item['loc'], str(item['count'])] for item in data['locs']]))
    parts.append(section('Collections', [[item['path'], str(item['count'])] for item in data['collections'] if '/' not in item['path']] + ([[f"({len(data['collections'])} in all)", '']] if data['collections'] else [])))
    project_rows = []
    for project in data['projects']:
        project_rows.append([project['name'], f"{project['cited']} cited", ', '.join(f"{target['destination']} ({target['profile']}, {target['state']})" for target in project['targets']) or '(no export target)'])
    parts.append(section('Projects', project_rows))
    return '\n\n'.join(parts)


COMMAND_CLASS = {
    'search': 'record_list', 'list': 'record_list', 'project show': 'record_list',
    'show': 'one_record',
    'import list': 'short_rows', 'resource check': 'short_rows', 'collection list': 'short_rows',
    'reorg': 'report', 'import': 'report', 'import show': 'report', 'import reconcile': 'report', 'export': 'report',
    'open': 'short_rows', 'summary': 'summary',
}
CLASS_RENDERERS = {
    'record_list': record_list, 'one_record': one_record, 'short_rows': short_rows,
    'report': report_text, 'confirmation': confirmation, 'summary': summary_text,
}


def render_text(command: str, data: dict, warnings: list[dict], *, terminal: bool | None = None, width: int | None = None) -> str:
    terminal = sys.stdout.isatty() if terminal is None else terminal
    width = shutil.get_terminal_size((80, 24)).columns if width is None else width
    kind = COMMAND_CLASS.get(command, 'confirmation')
    if command == 'project show' and 'items' in data or command == 'open' and 'choices' not in data:
        kind = 'confirmation'
    renderer = CLASS_RENDERERS[kind]
    text = renderer(command, data, terminal, width, warnings)
    if kind == 'confirmation':
        text = style_key(text, data.get('citation_key', ''), terminal, width)
    if command == 'project show' and 'sources' in data:
        text = f"Project: {data['name']}\n" + record_list('list', {'items': data['sources']}, terminal, width)
    if command == 'add' and data.get('file_action'):
        text += '\n' + confirmation('resource add', data['file_action'] | {'citation_key': data['citation_key']}, terminal, width)
    if data.get('dry_run') and command != 'reorg':
        text = 'Preview: ' + text
    elif data.get('unchanged') and command != 'add':
        text = 'Unchanged: ' + text
    for entry in data.get('import_conflicts', []):
        text += '\nConflict: ' + str(entry.get('citation_key') or entry.get('message') or entry.get('code'))
    return home_paths('\n'.join([text, *(styled_line(line, 'yellow', terminal, width) for line in warning_lines(command, warnings))]))


def render_error(command: str, issue: dict, data: dict | None = None, *, terminal: bool = False, width: int = 80) -> tuple[str, str]:
    """Return stdout for a partial import and stderr for the failure."""
    output = ''
    lines = []
    if data and data.get('moves'):
        lines.append(short_rows('reorg', data, terminal, width))
    if issue['code'] == 'import_partial' and data:
        output = render_text('import', data, [], terminal=terminal, width=width)
    if issue['code'] == 'export_partial' and data:
        output = render_text('export', data, data.get('warnings', []), terminal=terminal, width=width)
    if issue['code'] == 'export_blocked':
        lines.append(f"Not written: {issue['path'] or '(destination)'}")
        lines.extend(f"{entry.get('citation_key') or entry.get('details', {}).get('citation_key', '(source)')}: {entry['message']}" for entry in issue['details'].get('entries', []))
    if data and data.get('outcome') == 'needs_attention':
        lines.append(f"Needs attention: {data.get('citation_key') or '(input)'}")
    if issue['details'].get('kind'):
        for conflict in issue['details'].get('conflicts', []):
            lines.append(f"{conflict['path']}: current {json.dumps(conflict['current'], ensure_ascii=False)}; incoming {json.dumps(conflict['incoming'], ensure_ascii=False)}")
    issues = issue['details'].get('issues', [])
    message = issue['message']
    if issues:
        first = issues[0]
        path = '.'.join(str(part) for part in first['loc']) or '(record)'
        message = f"{path}: {first['msg']}; correct the input and retry"
    lines.append(styled_line(' '.join(message.splitlines()), 'red', terminal, width))
    return home_paths(output), home_paths('\n'.join(lines))


def render_notice(notice: dict, *, terminal: bool = False, width: int = 80) -> str:
    return styled_line(home_paths(notice['message']), 'yellow', terminal, width)


def move_text(data: dict) -> str:
    return short_rows('reorg', data, False, 80)


def placement_text(data: dict) -> str:
    return short_rows('resource check', data, False, 80)
