"""Explicit path selection without creating data directories."""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from refs.results import RefError


def absolute(value: str, base: Path | None = None) -> Path:
    if not value.strip():
        raise RefError("invalid_config", "An explicit path cannot be empty", 2)
    path = Path(value).expanduser()
    return ((base or Path.cwd()) / path).resolve()


@dataclass(frozen=True)
class Settings:
    config: Path
    catalog: Path | None
    library: Path | None
    origins: dict[str, str]
    roots: dict[str, Path] = field(default_factory=dict)

    def catalog_path(self) -> Path:
        if self.catalog is None:
            raise RefError("invalid_config", "Select a catalog with --catalog or REFS_CATALOG", 2)
        return self.catalog

    def describe(self) -> dict:
        return {name: dict(path=str(value) if value is not None else None,
                           origin=self.origins[name])
                for name, value in (("config", self.config), ("catalog", self.catalog),
                                    ("library", self.library))}


def select(config: str | None, catalog: str | None) -> Settings:
    config_value = config if config is not None else os.environ.get("REFS_CONFIG", "~/.config/refs/config.toml")
    config_path = absolute(config_value)
    values = {}
    if config_path.exists():
        try:
            values = tomllib.loads(config_path.read_text())
        except (tomllib.TOMLDecodeError, UnicodeError) as exc:
            raise RefError("invalid_config", str(exc), 2, path=str(config_path)) from exc
        if values.get("schema_version") != 1:
            raise RefError("invalid_config", "Unsupported configuration version", 2)
    try:
        configured_catalog = values.get("catalog", {}).get("path")
        catalog_value = catalog if catalog is not None else os.environ.get("REFS_CATALOG", configured_catalog)
        library_value = values.get("resources", {}).get("library_root")
        roots = {name: absolute(value, config_path.parent) for name, value in values.get('resources', {}).get('roots', {}).items()}
        named_library = values.get("resources", {}).get("roots", {}).get("library")
        origin = "--catalog" if catalog is not None else "REFS_CATALOG" if "REFS_CATALOG" in os.environ else "config"
        catalog_path = absolute(catalog_value, config_path.parent if origin == "config" else None) if catalog_value is not None else None
        library_path = absolute(library_value, config_path.parent) if library_value is not None else None
        if named_library is not None and absolute(named_library, config_path.parent) != library_path:
            raise RefError("invalid_config", "library_root and roots.library must agree", 2)
    except (AttributeError, TypeError) as exc:
        raise RefError("invalid_config", "Paths and configuration sections have invalid types", 2) from exc
    return Settings(config_path, catalog_path, library_path,
                    dict(config="--config" if config is not None else "REFS_CONFIG" if "REFS_CONFIG" in os.environ else "default",
                         catalog=origin, library="config" if library_path else "unset"),
                    roots | ({"library": library_path} if library_path else {}))
