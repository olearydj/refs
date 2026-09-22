"""Plain command confirmations; structured output remains the result envelope."""

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
        group = warning['code'] if warning.get('details', {}).get('class') == 'documented_fallback' else str(len(groups))
        groups.setdefault(group, []).append(warning)
    lines = []
    descriptions = {
        'unassessed_import': 'have imported fields preserved only in the catalog',
        'field_omitted': 'have fields without a portable slot',
        'name_particle_fallback': 'use portable names with consumer-defined particle behavior',
        'literal_issued_year': 'use literal issued dates; check the rendered dates',
        'container_title_case': 'use catalog casing for container titles; check proper names',
        'tex_decoded': 'use decoded TeX name forms; check the rendered spelling',
        'literal_publisher': 'treat the publisher as one institution',
        'issued_day_in_note': 'retain the issued day in a note',
        'field_in_note': 'retain citation fields in notes',
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
        lines.append(f"Warning: {len(keys)} {noun} {description} ({', '.join(keys)})")
    return lines

def render_text(command: str, data: dict, warnings: list[dict]) -> str:
    key = data.get('citation_key', '')
    revision = data.get('revision', '')
    renderers = {
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
        'import show': lambda: f"Import {data['import_id']} ({len(data['entries'])} entries)",
        'import reconcile': lambda: f"Reconciled import {data['import_id']} ({len(data['entries'])} selected entries)",
        'import': lambda: f"Imported {data['counts']['applied']}, unchanged {data['counts']['unchanged']}, conflicts {data['counts']['conflict']}, invalid {data['counts']['invalid']} from {data['input']}",
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
