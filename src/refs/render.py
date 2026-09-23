"""Plain command confirmations; structured output remains the result envelope."""

import json

from refs.display import readable


def project_text(data: dict) -> str:
    if 'items' in data:
        return '\n'.join(item['name'] for item in data['items']) or '(no projects)'
    return f"Project: {data['name']}\n" + readable('list', {'items': data['sources']})



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

def import_text(command: str, data: dict) -> str:
    if command == 'import':
        counts = data['counts']
        lines = [f"Imported {counts['applied']}, unchanged {counts['unchanged']}, conflicts {counts['conflict']}, invalid {counts['invalid']} from {data['input']}"]
    else:
        verb = 'Import' if command == 'import show' else 'Reconciled import'
        lines = [f"{verb} {data['import_id']} (batch revision {data['batch_revision']})"]
    for entry in data['entries']:
        key = entry.get('citation_key') or entry.get('item_key') or '(unreadable key)'
        binding = entry.get('binding', {})
        if command != 'import' or entry.get('status') in ('conflict','invalid'):
            lines.append(f"{key}: {entry.get('status','selected')}" + (f" (source revision {entry['source_revision']})" if entry.get('source_revision') else ''))
            if entry.get('message'):
                lines.append('  '+entry['message'])
            candidates = entry.get('candidates',entry.get('details',{}).get('source_ids',[]))
            if candidates:
                lines.append('  Candidates: '+', '.join(candidates))
            for change in binding.get('conflicts',[]) if command != 'import reconcile' else entry.get('remaining_conflicts',[]):
                lines.append(f"  {change['path']}: current {json.dumps(change['current'],ensure_ascii=False)}; incoming {json.dumps(change['incoming'],ensure_ascii=False)}")
        if binding.get('bound') and (binding.get('incoming_key') != binding.get('catalog_key') or binding.get('filled')):
            lines.append(f"  Bound {key} to {binding['catalog_key']}" + ('; filled '+', '.join(binding['filled']) if binding.get('filled') else ''))
        for decision in entry.get('decisions',[]):
            keeping = decision['action']=='keep_current'
            label, value = ('Keep current',decision['current']) if keeping else ('Take incoming',decision['incoming'])
            lines.append(f"  {label} {decision['path']}: {json.dumps(value,ensure_ascii=False)}")
        for limitation in entry.get('limitations',[]):
            lines.append(f"  {key}: {limitation['field']}: {limitation['reason']}")
        for warning in entry.get('warnings',[]):
            lines.append(f"  Warning: {key}: {warning['message']}")
    for kind, count in data.get('preservation',{}).items():
        if count:
            lines.append(f"Preservation: {count} {kind.replace('_',' ')} skipped as catalog content; retain the original Zotero archive")
    if not data['entries']:
        lines.append('(no entries)')
    return '\n'.join(lines)


def render_text(command: str, data: dict, warnings: list[dict]) -> str:
    key = data.get('citation_key', '')
    revision = data.get('revision', '')
    renderers = {
        'collection list': lambda: '\n'.join(f"{item['path']} ({item['count']} active sources) [{item['library_uri']}]" for item in data['items']) or '(no collections)',
        'paths': lambda: '\n'.join(f"{label}: {data[name]['path'] or '(not configured)'}" for name, label in [('config', 'Configuration'), ('catalog', 'Catalog'), ('library', 'Library')]),
        'config show': lambda: f"Configuration: {data['config']}" + ''.join(f"\n{name} = {value} ({data['origins'].get(name, 'default')})" for name,value in data['values'].items()),
        'backup': lambda: f"Wrote snapshot {data['output']} (external file bytes excluded)",
        'init': lambda: f"Initialized catalog at {data['catalog_path']} (library: {data.get('library') or 'none'})",
        'add': lambda: f"Already present: {key} (revision {revision})" if data.get('outcome') == 'already_present' else f"Created {key}",
        'update': lambda: f"Updated {key} (revision {revision})",
        'key set': lambda: f"Renamed {data['previous_key']} to {key}",
        'remove': lambda: f"Removed {key}",
        'reactivate': lambda: f"Reactivated {key}",
        'project create': lambda: f"Created project {data['name']}",
        'project cite': lambda: f"Cited {data['cited']} in {data['project_name']} ({data['already_cited']} already cited)" if 'already_cited' in data else f"Cited {key} in {data['project_name']}",
        'project uncite': lambda: f"Uncited {key} from {data['project_name']}",
        'project show': lambda: project_text(data),
        'resource add': lambda: f"Copied {data['copied_from'].get('path') or data['copied_from'].get('relative')} to {data['destination']} for {key}" if 'destination' in data else f"Linked {data.get('resolved_path') or data.get('path') or data.get('relative')} to {key}",
        'resource unlink': lambda: f"Resource {data['id']} is already unlinked" if data.get('unchanged') else f"Unlinked {data.get('resolved_path') or data.get('path') or data.get('relative')} from {key}",
        'resource check': lambda: '\n'.join(f"{item['status']}: {item.get('resolved_path') or item.get('relative') or item['id']}" for item in data['items']) or '(no resources)',
        'open': lambda: 'Choose a resource with --resource:\n' + '\n'.join(f"{item['id']}: {item.get('resolved_path') or item.get('relative')}" for item in data['choices']) if 'choices' in data else f"Opened {data['path']} for {key}",
        'import list': lambda: '\n'.join(f"{item['import_id']} {item['origin']} {item['created']} " + ', '.join(f'{name} {count}' for name,count in item['counts'].items()) + f" (batch revision {item['batch_revision']})" for item in data['items']) or '(no imports)',
        'import show': lambda: import_text(command,data),
        'import reconcile': lambda: import_text(command,data),
        'import': lambda: import_text(command,data),
        'export': lambda: f"Wrote {data['output']} (0 entries)" if not data['count'] else f"Wrote {data['output']} ({data['count']} entries, {len(warnings)} warnings)",
        'show': lambda: readable(command, data),
        'search': lambda: readable(command, data),
        'list': lambda: readable(command, data),
    }
    text = renderers[command]()
    if command == 'add' and data.get('file_action'):
        action = data['file_action'] | {'citation_key': key}
        action.pop('dry_run', None)
        text += '\n' + render_text('resource add', action, [])
    if data.get('dry_run'):
        text = 'Preview: ' + text
    elif data.get('unchanged') and command != 'add':
        text = 'Unchanged: ' + text
    for entry in data.get('import_conflicts', []):
        text += '\nConflict: ' + str(entry.get('citation_key') or entry.get('message') or entry.get('code'))
    return '\n'.join([text, *warning_lines(command, warnings)])
