"""Explicit path selection without creating data directories."""

import copy
import json
import os
import re
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

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


def policies(user: dict, config: Path, explicit: str | None, disabled: bool) -> tuple[dict,dict]:
    from refs import naming
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
            allowed={'project','export'} if project else {'schema_version','catalog','resources','keys','titles','sorting','export','project'}
            if set(values)-allowed:
                raise ValueError('Unsupported configuration section')
            for section in ('catalog','resources','keys','titles','sorting','export'):
                if section in values and not isinstance(values[section],dict):
                    raise ValueError(f'{section} must be a table')
            if 'catalog' in values and set(values['catalog'])-{'path'}:
                raise ValueError('Unsupported catalog setting')
            if 'resources' in values and set(values['resources'])-{'library_root','roots'}:
                raise ValueError('Unsupported resource setting')
            for section in ('keys','titles','sorting','export'):
                for key,value in values.get(section,{}).items():
                    permitted=set(defaults[section]) | ({'output','consumers'} if section=='export' else set())
                    if key not in permitted:
                        raise ValueError(f'Unsupported {section}.{key}')
                    if key=='corporate_aliases':
                        if not isinstance(value,dict):
                            raise ValueError('Corporate aliases must be a table')
                        if any(not name.strip() or not isinstance(token,str) for name,token in value.items()):
                            raise ValueError('Corporate aliases require nonblank names and string tokens')
                        value={unicodedata.normalize('NFC',name):naming.creator_token(token) for name,token in value.items() if name.strip()}
                    elif key in ('stopwords','minor_words','protected_terms','ignore_leading_articles','consumers'):
                        if not isinstance(value,list) or any(not isinstance(item,str) or not item.strip() for item in value):
                            raise ValueError(f'{key} must be a list of nonblank strings')
                        seen=set()
                        deduplicated=[]
                        for item in value:
                            if item.casefold() not in seen:
                                deduplicated.append(item)
                                seen.add(item.casefold())
                        value=deduplicated
                    elif key=='title_words':
                        if type(value) is not int or value not in (1,2):
                            raise ValueError('title_words must be 1 or 2')
                    elif not isinstance(value,str) or not value.strip():
                        raise ValueError(f'{key} must be a nonblank string')
                    if key in ('template','without_creator'):
                        assert isinstance(value,str)
                        tokens=re.findall(r'\{([^{}]+)\}',value)
                        allowed_tokens={'year','title'} | ({'author'} if key=='template' else set())
                        separators=re.sub(r'\{[^{}]+\}','',value)
                        if not tokens or set(tokens)-allowed_tokens or re.search(r'[^\W_]|[\s{},()=\\#%"]',separators):
                            raise ValueError('Templates allow documented tokens and literal separators only')
                    if key in ('policy','transliteration_policy','profile') and value!=defaults[section][key]:
                        raise ValueError(f'Unsupported {key}: {value}')
                    if key=='missing_year' and isinstance(value,str) and re.search(r'[\s,{}()=\\#%"]',value):
                        raise ValueError('missing_year must be a valid citation-key token')
                    if key=='output':
                        assert isinstance(value,str)
                        value=str(absolute(value,path.parent))
                    effective.setdefault(section,{})[key]=value
                    origins[section+'.'+key]=str(path)
            if 'project' in values:
                if not isinstance(values['project'],str) or not values['project'].strip():
                    raise ValueError('project must be a nonblank name or ID')
                effective['project']=values['project']
                origins['project']=str(path)
        except (ValueError,TypeError,AttributeError,RefError) as exc:
            raise RefError('invalid_config',str(exc),2,path=str(path),details={'origin':str(path),'values':values}) from exc
    return effective,origins
