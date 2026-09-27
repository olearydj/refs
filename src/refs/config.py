"""Explicit path selection without creating data directories."""

import copy
import json
import os
import re
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from refs.results import RefError


def toml_text(values: dict) -> str:
    """Write refs configuration tables with bare keys wherever TOML permits."""
    def key(value):
        return value if re.fullmatch(r'[A-Za-z0-9_-]+', value) else json.dumps(value)

    def lines(table, prefix=()):
        output = ['[' + '.'.join(key(part) for part in prefix) + ']'] if prefix else []
        output += [key(name) + ' = ' + json.dumps(value, ensure_ascii=False) for name, value in table.items() if not isinstance(value, dict)]
        for name, value in table.items():
            if isinstance(value, dict):
                output += lines(value, (*prefix, name))
        return output

    return '\n'.join(lines(values)) + '\n'


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
    values: dict = field(default_factory=dict)
    value_origins: dict = field(default_factory=dict)

    def catalog_path(self) -> Path:
        if self.catalog is None:
            raise RefError("invalid_config", "Select a catalog with --catalog or REFS_CATALOG", 2)
        return self.catalog

    def describe(self) -> dict:
        return {name: dict(path=str(value) if value is not None else None,
                           origin=self.origins[name])
                for name, value in (("config", self.config), ("catalog", self.catalog),
                                    ("library", self.library))}

    def inspect(self) -> dict:
        values=flatten(self.values)
        origins={name:next((self.value_origins[prefix] for prefix in sorted(self.value_origins,key=len,reverse=True) if name==prefix or name.startswith(prefix+'.')),'default') for name in values}
        for name,path in [('catalog.path',self.catalog),('resources.library_root',self.library),*[('resources.roots.'+name,path) for name,path in self.roots.items()]]:
            values[name]=str(path) if path is not None else None
            origins[name]=self.origins['catalog'] if name=='catalog.path' else str(self.config)
        return dict(config=str(self.config),values=values,origins=origins,paths=self.describe(),diagnostics=[])


def export_options(settings: Settings, project: str | None, output: Path | None, profile: str | None) -> tuple[str, list[tuple[Path, str]], bool]:
    project = project if project is not None else settings.values.get('project')
    export = settings.values['export']
    targets = export.get('targets')
    if not project:
        raise RefError('invalid_invocation', 'Supply export project or configured default', 2)
    if targets and output is None:
        selected = [t for t in targets if profile is None or t['profile'] == profile]
        if profile is not None and len(selected) != 1:
            raise RefError('invalid_invocation', 'Profile must select exactly one configured target; supply --output', 2)
        return project, [(Path(t['output']), t['profile']) for t in selected], profile is None
    if output is not None and profile is None and targets:
        match = next((t for t in targets if Path(t['output']) == absolute(str(output))), None)
        profile = match['profile'] if match else None
    configured_output = export.get('output')
    output = output if output is not None else Path(configured_output) if configured_output else None
    if output is None:
        raise RefError('invalid_invocation', 'Supply export output or configured default', 2)
    return project, [(output, profile if profile is not None else export.get('profile', 'portable-bibtex-v1'))], False


def select(config: str | None, catalog: str | None, *, project_file: str | None = None, no_project_config: bool = False) -> Settings:
    config_value = config if config is not None else os.environ.get("REFS_CONFIG", "~/.config/refs/config.toml")
    config_path = absolute(config_value)
    values = {}
    if config_path.exists():
        try:
            values = tomllib.loads(config_path.read_text())
        except (tomllib.TOMLDecodeError, UnicodeError) as exc:
            raise RefError("invalid_config", str(exc), 2, path=str(config_path)) from exc
        if type(values.get("schema_version")) is not int or values.get("schema_version") != 1:
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
    effective, origins = policies(values,config_path,project_file,no_project_config)
    return Settings(config_path, catalog_path, library_path,
                    dict(config="--config" if config is not None else "REFS_CONFIG" if "REFS_CONFIG" in os.environ else "default",
                         catalog=origin, library="config" if library_path else "unset"),
                    roots | ({"library": library_path} if library_path else {}),effective,origins)


def flatten(values: dict, prefix='') -> dict:
    result={}
    for key,value in values.items():
        path=prefix+'.'+key if prefix else key
        if isinstance(value,dict):
            result.update(flatten(value,path))
        else:
            result[path]=value
    return result


def project_path(explicit: str | None, disabled: bool) -> Path | None:
    if explicit is not None and disabled:
        raise RefError('invalid_config','Choose --project-file or --no-project-config',2)
    if disabled:
        return None
    if explicit is not None:
        path=absolute(explicit)
        if not path.is_file():
            raise RefError('invalid_config','Selected project configuration is missing',2,path=str(path))
        return path
    cwd=Path.cwd()
    root=next((path for path in [cwd,*cwd.parents] if (path/'.git').exists()),None)
    candidates=[cwd] if root is None else [cwd,*cwd.parents[:list(cwd.parents).index(root)+1]] if cwd!=root else [cwd]
    return next((path/'.refs.toml' for path in candidates if (path/'.refs.toml').is_file()),None)


class ConfigTable(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class KeyTable(ConfigTable):
    template: str = ''
    without_creator: str = ''
    missing_year: str = ''
    title_words: int = 0
    stopwords: list[str] = Field(default_factory=list)
    transliteration_policy: str = ''
    corporate_aliases: dict[str, str] = Field(default_factory=dict)


class TitleTable(ConfigTable):
    policy: str = ''
    minor_words: list[str] = Field(default_factory=list)
    protected_terms: list[str] = Field(default_factory=list)


class SortingTable(ConfigTable):
    ignore_leading_articles: list[str] = Field(default_factory=list)


class ExportTarget(ConfigTable):
    output: str
    profile: str


class ExportTable(ConfigTable):
    profile: str = ''
    output: str = ''
    consumers: list[str] = Field(default_factory=list)
    targets: list[ExportTarget] = Field(default_factory=list)


class PolicyTables(ConfigTable):
    schema_version: int = 1
    catalog: dict = Field(default_factory=dict)
    resources: dict = Field(default_factory=dict)
    keys: KeyTable = Field(default_factory=KeyTable)
    titles: TitleTable = Field(default_factory=TitleTable)
    sorting: SortingTable = Field(default_factory=SortingTable)
    export: ExportTable = Field(default_factory=ExportTable)
    project: str = ''


def policies(user: dict, config: Path, explicit: str | None, disabled: bool) -> tuple[dict,dict]:
    from refs import naming
    from refs.bibliography import PROFILES
    defaults: dict={'keys':{'template':'{author}-{year}-{title}','without_creator':'{title}-{year}','missing_year':'ND','title_words':2,'stopwords':sorted(naming.STOPWORDS),'transliteration_policy':'creator-latin-v1','corporate_aliases':{}},
              'titles':{'policy':'english-title-case-v1','minor_words':sorted(naming.MINOR),'protected_terms':list(naming.GLOBAL_TERMS)},
              'sorting':{'ignore_leading_articles':['a','an','the']},'export':{'profile':'portable-bibtex-v1'}}
    effective: dict=copy.deepcopy(defaults)
    origins={key:'default' for key in flatten(defaults)}
    selected=project_path(explicit,disabled)
    layers=[(user,config,False)]
    if selected:
        try:
            layers.append((tomllib.loads(selected.read_text()),selected,True))
        except (OSError,ValueError) as exc:
            raise RefError('invalid_config','Cannot read project configuration; correct the selected file',2,path=str(selected),details={'cause':str(exc)}) from exc
    for values,path,project in layers:
        try:
            if project and set(values)-{'project','export'}:
                raise ValueError('Unsupported configuration section')
            if 'catalog' in values and set(values['catalog'])-{'path'}:
                raise ValueError('Unsupported catalog setting')
            if 'resources' in values and set(values['resources'])-{'library_root','roots'}:
                raise ValueError('Unsupported resource setting')
            values=PolicyTables.model_validate(values).model_dump(exclude_unset=True)
            export = values.get('export', {})
            if 'targets' in export:
                if {'output', 'profile'} & export.keys():
                    raise ValueError('Choose [export] output/profile or [[export.targets]], not both')
                if not export['targets']:
                    raise ValueError('export.targets must contain at least one target')
                for key in ('output', 'profile'):
                    effective['export'].pop(key, None)
                    origins.pop('export.' + key, None)
            elif {'output', 'profile'} & export.keys():
                effective['export'].pop('targets', None)
                origins.pop('export.targets', None)
            for section in ('keys','titles','sorting','export'):
                for key,value in values.get(section,{}).items():
                    if key=='targets':
                        outputs = set()
                        for target in value:
                            if not target['output'].strip() or target['profile'] not in PROFILES:
                                raise ValueError('Each export target needs a nonblank output and supported profile')
                            target['output'] = str(absolute(target['output'], path.parent))
                            if target['output'] in outputs:
                                raise ValueError('Export targets must have distinct output paths')
                            outputs.add(target['output'])
                    elif key=='corporate_aliases':
                        if any(not name.strip() for name in value):
                            raise ValueError('Corporate aliases require nonblank names and string tokens')
                        value={unicodedata.normalize('NFC',name):naming.creator_token(token) for name,token in value.items() if name.strip()}
                    elif key in ('stopwords','minor_words','protected_terms','ignore_leading_articles','consumers'):
                        if any(not item.strip() for item in value):
                            raise ValueError(f'{key} must be a list of nonblank strings')
                        seen=set()
                        deduplicated=[]
                        for item in (defaults[section][key] if key!='consumers' else []) + value:
                            if item.casefold() not in seen:
                                deduplicated.append(item)
                                seen.add(item.casefold())
                        value=deduplicated
                    elif key=='title_words':
                        if value not in (1,2):
                            raise ValueError('title_words must be 1 or 2')
                    elif not value.strip():
                        raise ValueError(f'{key} must be a nonblank string')
                    if key in ('template','without_creator'):
                        if not isinstance(value,str):
                            raise ValueError(f'{key} must be a nonblank string')
                        tokens=re.findall(r'\{([^{}]+)\}',value)
                        allowed_tokens={'year','title'} | ({'author'} if key=='template' else set())
                        separators=re.sub(r'\{[^{}]+\}','',value)
                        if not tokens or set(tokens)-allowed_tokens or re.search(r'[^\W_]|[\s{},()=\\#%"]',separators):
                            raise ValueError('Templates allow documented tokens and literal separators only')
                    if key=='profile' and value not in PROFILES:
                        raise ValueError(f'Unsupported profile: {value}; choose ' + ', '.join(PROFILES))
                    if key in ('policy','transliteration_policy') and value!=defaults[section][key]:
                        raise ValueError(f'Unsupported {key}: {value}')
                    if key=='missing_year' and isinstance(value,str) and re.search(r'[\s,{}()=\\#%"]',value):
                        raise ValueError('missing_year must be a valid citation-key token')
                    if key=='output':
                        if not isinstance(value,str):
                            raise ValueError('output must be a nonblank string')
                        value=str(absolute(value,path.parent))
                    effective.setdefault(section,{})[key]=value
                    origins[section+'.'+key]=('default+config: ' if key in ('stopwords','minor_words','protected_terms','ignore_leading_articles') else '')+str(path)
            if 'project' in values:
                if not values['project'].strip():
                    raise ValueError('project must be a nonblank name or ID')
                effective['project']=values['project']
                origins['project']=str(path)
        except (ValueError,TypeError,AttributeError,ValidationError,RefError) as exc:
            raise RefError('invalid_config',str(exc),2,path=str(path),details={'origin':str(path),'values':values}) from exc
    return effective,origins
