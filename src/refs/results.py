"""Application-owned results, independent of the command framework."""

import json
import sys
from contextvars import ContextVar
from typing import Any

upgrade_notices: ContextVar[list[dict]] = ContextVar("upgrade_notices", default=[])


def notice(code: str, message: str, *, path: str | None = None, details: dict | None = None, retryable: bool = False) -> dict:
    return dict(code=code, message=message, path=path, details=details or {}, retryable=retryable)


class RefError(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 3, *,
                 path: str | None = None, details: dict | None = None,
                 retryable: bool = False, data: dict | None = None):
        super().__init__(message)
        if code == 'integrity_error':
            exit_code = 5
        if exit_code not in {2, 3, 4, 5, 6}:
            raise ValueError("Invalid application exit code")
        self.data = data
        self.exit_code = exit_code
        self.issue: dict[str, Any] = notice(code, message, path=path, details=details, retryable=retryable)


def emit(command: str, data: dict[str, Any] | None = None, *,
         error: RefError | None = None, json_output: bool = False,
         warnings: list[dict] | None = None, text_context: dict | None = None) -> None:
    notices = upgrade_notices.get()
    upgrade_notices.set([])
    warnings = [*(warnings or []), *notices]
    result = dict(schema_version="1.0", command=command,
                  status="partial" if error and error.exit_code == 4 else "error" if error else "ok",
                  data=error.data if error else data, warnings=warnings or [], errors=[error.issue] if error else [])
    if json_output:
        print(json.dumps(result, ensure_ascii=False))
    else:
        from refs.render import render_error, render_notice, render_text
        for notice in notices:
            print(render_notice(notice, terminal=sys.stderr.isatty()), file=sys.stderr)
        visible_warnings = [item for item in warnings if item not in notices]
        if error:
            output, problem = render_error(command, error.issue, error.data, terminal=sys.stderr.isatty())
            if output:
                print(output, flush=True)
            print(problem, file=sys.stderr)
        else:
            print(render_text(command, (data or {}) | (text_context or {}), visible_warnings))
