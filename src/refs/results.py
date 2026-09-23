"""Application-owned results, independent of the command framework."""

import json
import sys
from typing import Any


class RefError(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 3, *,
                 path: str | None = None, details: dict | None = None,
                 retryable: bool = False, data: dict | None = None):
        super().__init__(message)
        if exit_code not in {2, 3, 4, 5, 6}:
            raise ValueError("Invalid application exit code")
        self.data = data
        self.exit_code = exit_code
        self.issue: dict[str, Any] = dict(code=code, message=message, path=path,
                          details=details or {}, retryable=retryable)


def emit(command: str, data: dict[str, Any] | None = None, *,
         error: RefError | None = None, json_output: bool = False,
         warnings: list[dict] | None = None, text_context: dict | None = None) -> None:
    result = dict(schema_version="1.0", command=command,
                  status="partial" if error and error.exit_code == 4 else "error" if error else "ok",
                  data=error.data if error else data, warnings=warnings or [], errors=[error.issue] if error else [])
    if json_output:
        print(json.dumps(result, ensure_ascii=False))
    elif error:
        if error.data and error.data.get('moves'):
            from refs.render import move_text
            print(move_text(error.data), file=sys.stderr)
        if error.issue['code'] == 'import_partial' and error.data:
            from refs.render import render_text
            print(render_text('import', error.data, warnings or []), flush=True)
        if error.issue['code'] == 'export_blocked':
            print(f"Not written: {error.issue['path'] or '(destination)'}", file=sys.stderr)
            for entry in error.issue['details'].get('entries', []):
                print(f"{entry.get('citation_key') or entry.get('details', {}).get('citation_key', '(source)')}: {entry['message']}", file=sys.stderr)
        if error.data and error.data.get('outcome') == 'needs_attention':
            print(f"Needs attention: {error.data.get('citation_key') or '(input)'}", file=sys.stderr)
        issues = error.issue['details'].get('issues', [])
        message = error.issue['message']
        if issues:
            first = issues[0]
            path = '.'.join(str(part) for part in first['loc']) or '(record)'
            message = f"{path}: {first['msg']}; correct the input and retry"
        print(' '.join(message.splitlines()), file=sys.stderr)
    elif command == 'schema':
        print('\n'.join(data['schemas']) if data and 'schemas' in data else json.dumps(result, ensure_ascii=False, indent=2))
    else:
        from refs.render import render_text
        print(render_text(command, (data or {}) | (text_context or {}), warnings or []))
