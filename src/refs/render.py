"""Plain command confirmations; structured output remains the result envelope."""

from refs.display import readable


def project_text(data: dict) -> str:
    if 'items' in data:
        return '\n'.join(item['name'] for item in data['items']) or '(no projects)'
    return '\n'.join([f"Project: {data['name']}", *[source['citation_key'] for source in data['sources']]])


def render_text(command: str, data: dict, warnings: list[dict]) -> str:
    key = data.get('citation_key', '')
    revision = data.get('revision', '')
    renderers = {
        'backup': lambda: f"Wrote snapshot {data['output']} (external file bytes excluded)",
        'init': lambda: f"Initialized catalog at {data['catalog_path']} (library: {data.get('library') or 'none'})",
        'add': lambda: f"Already present: {key} (revision {revision})" if data.get('outcome') == 'already_present' else f"Created {key}",
        'update': lambda: f"Updated {key} (revision {revision})",
        'key set': lambda: f"Renamed {data['previous_key']} to {key}",
        'remove': lambda: f"Removed {key}",
        'reactivate': lambda: f"Reactivated {key}",
        'project create': lambda: f"Created project {data['name']}",
        'project cite': lambda: f"Cited {key} in {data['project_name']}",
        'project uncite': lambda: f"Uncited {key} from {data['project_name']}",
        'project show': lambda: project_text(data),
        'resource add': lambda: f"Copied {data['copied_from'].get('path') or data['copied_from'].get('relative')} to {data['destination']} for {key}" if 'destination' in data else f"Linked {data.get('resolved_path') or data.get('path') or data.get('relative')} to {key}",
        'resource unlink': lambda: f"Unlinked {data.get('resolved_path') or data.get('path') or data.get('relative')} from {key}",
        'resource check': lambda: '\n'.join(f"{item['status']}: {item.get('resolved_path') or item.get('relative') or item['id']}" for item in data['items']) or '(no resources)',
        'open': lambda: 'Choose a resource with --resource:\n' + '\n'.join(f"{item['id']}: {item.get('resolved_path') or item.get('relative')}" for item in data['choices']) if 'choices' in data else f"Opened {data['path']} for {key}",
        'import': lambda: f"Imported {data['counts']['applied']}, unchanged {data['counts']['unchanged']}, conflicts {data['counts']['conflict']}, invalid {data['counts']['invalid']} from {data['input']}",
        'export': lambda: f"Wrote {data['output']} ({data['count']} entries, {len(warnings)} warnings)",
        'show': lambda: readable(command, data),
        'search': lambda: readable(command, data),
        'list': lambda: readable(command, data),
    }
    text = renderers[command]()
    if data.get('dry_run'):
        text = 'Preview: ' + text
    elif data.get('unchanged') and command != 'add':
        text = 'Unchanged: ' + text
    for entry in data.get('import_conflicts', []):
        text += '\nConflict: ' + str(entry.get('citation_key') or entry.get('message') or entry.get('code'))
    return '\n'.join([text, *['Warning: ' + warning['message'] for warning in warnings]])
