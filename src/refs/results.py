"""Application-owned results, independent of the command framework."""

import json
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
        self.issue = dict(code=code, message=message, path=path,
                          details=details or {}, retryable=retryable)


def emit(command: str, data: dict[str, Any] | None = None, *,
         error: RefError | None = None, json_output: bool = False,
         warnings: list[dict] | None = None) -> None:
    result = dict(schema_version="1.0", command=command,
                  status="partial" if error and error.exit_code == 4 else "error" if error else "ok",
                  data=error.data if error else data, warnings=warnings or [], errors=[error.issue] if error else [])
    if json_output:
        print(json.dumps(result, ensure_ascii=False))
    elif not error and command in ("show", "search", "list"):
        from refs.display import readable
        print(readable(command, data or {}))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
