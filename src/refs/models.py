"""Strict records narrowed by the packaged bibliographic registry."""

import calendar
import hashlib
import json
import math
import re
from copy import deepcopy
from importlib.resources import files
from typing import Annotated, Literal, Self
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from refs import languages
from refs.results import RefError

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
MONTHS = tuple((calendar.month_abbr[number].lower(), calendar.month_name[number].lower()) for number in range(1, 13))
IDENTIFIER_FIELDS = ('DOI', 'URL', 'ISBN', 'ISSN', 'PMID', 'PMCID')


def person_name(name: dict, parts: tuple[str, ...] = ('given', 'dropping-particle', 'non-dropping-particle', 'family', 'suffix'), *, strip: bool = False) -> str:
    return ' '.join(name[part].strip() if strip else name[part] for part in parts if name.get(part))


def normalize_doi(value: str) -> str:
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I).lower()


def normalize_arxiv(value: str) -> str:
    value = re.sub(r'^arxiv:\s*','',value.strip(),flags=re.I)
    return re.sub(r'\s*\[[^\]]+\]\s*$','',value).strip()


def portable_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)


def assign_path(target: dict, path: str, value) -> None:
    if path == 'metadata.DOI':
        value = normalize_doi(value)
    elif path == 'extensions.identifiers.arxiv':
        value = normalize_arxiv(value)
    parts = path.split('.')
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    if parts[-1] in target and target[parts[-1]] != value:
        raise RefError('alias_conflict', f'Conflicting aliases for {path}; Competing values in the original item', 3)
    target[parts[-1]] = value


def doi_arxiv(value: str) -> str | None:
    doi = normalize_doi(value)
    return normalize_arxiv(doi[len('10.48550/arxiv.'):]) if doi.startswith('10.48550/arxiv.') else None


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


REGISTRY_BYTES = files("refs").joinpath("data/bibliographic-coverage.json").read_bytes()
REGISTRY = json.loads(REGISTRY_BYTES)
REGISTRY_PROVENANCE = json.loads(files("refs").joinpath("data/provenance.json").read_text())
if hashlib.sha256(REGISTRY_BYTES).hexdigest() != REGISTRY_PROVENANCE["registry"]["sha256"]:
    raise RuntimeError("Packaged mapping registry failed its provenance hash check")


class Name(StrictModel):
    family: Text | None = None
    given: Text | None = None
    literal: Text | None = None
    dropping_particle: Text | None = Field(default=None, alias="dropping-particle")
    non_dropping_particle: Text | None = Field(default=None, alias="non-dropping-particle")
    suffix: Text | None = None
    comma_suffix: bool | None = Field(default=None, alias="comma-suffix")
    static_ordering: bool | None = Field(default=None, alias="static-ordering")
    parse_names: bool | None = Field(default=None, alias="parse-names")

    @model_validator(mode="after")
    def name_form(self) -> Self:
        if self.literal is not None:
            if any(value is not None for key, value in self.model_dump().items() if key != "literal"):
                raise ValueError("A literal name cannot contain personal name fields")
        elif self.family is None and self.given is None:
            raise ValueError("A name needs family, given or literal")
        return self


class Date(StrictModel):
    date_parts: list[list[int]] | None = Field(default=None, alias="date-parts")
    literal: Text | None = None
    season: int | None = None
    circa: bool | None = None

    @model_validator(mode="after")
    def valid_date(self) -> Self:
        if self.date_parts is None and self.literal is None:
            raise ValueError("A date needs date-parts or literal text")
        if self.season is not None and self.season not in range(1, 5):
            raise ValueError("Season must be 1 through 4")
        if self.date_parts is not None:
            if len(self.date_parts) not in (1, 2):
                raise ValueError("A date has one date or a two-date range")
            for part in self.date_parts:
                if not 1 <= len(part) <= 3 or not 1 <= part[0] <= 9999:
                    raise ValueError("Invalid calendar year or date precision")
                if len(part) > 1 and not 1 <= part[1] <= 12:
                    raise ValueError("Invalid calendar month")
                if len(part) > 2 and not 1 <= part[2] <= calendar.monthrange(part[0], part[1])[1]:
                    raise ValueError("Invalid calendar day")
            if len(self.date_parts) == 2 and self.date_parts[0] > self.date_parts[1]:
                raise ValueError("Date range is reversed")
        return self


class MetadataBase(StrictModel):
    @model_validator(mode="before")
    @classmethod
    def normalize_and_check(cls, value):
        if not isinstance(value, dict):
            return value
        value = dict(value)
        if isinstance(value.get("DOI"), str):
            value["DOI"] = normalize_doi(value["DOI"])
        if isinstance(value.get("language"), str):
            value["language"] = languages.normalize(value["language"])
        kind = value.setdefault("type", "document")
        if kind not in REGISTRY["core_fields"]["type"]["schema"]["enum"]:
            raise ValueError("Unsupported source type")
        for key, item in value.items():
            if item is None:
                raise ValueError(f"{key} cannot be null; omit or explicitly clear it")
            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError("Numeric values must be finite")
        edition = value.get("edition")
        if isinstance(edition, str) and re.fullmatch(r"[0-9]+(?:\.0+)?", edition):
            value["edition"] = int(edition.split(".")[0])
        if isinstance(value.get("edition"), (int, float)) and (value["edition"] <= 0 or int(value["edition"]) != value["edition"]):
            raise ValueError("Numeric edition must be a positive integer")
        if isinstance(value.get("edition"), float):
            value["edition"] = int(value["edition"])
        if "URL" in value:
            if not portable_url(value["URL"]):
                raise ValueError("URL must be absolute HTTP(S)")
        if not value.get("title") and not value.get("URL") and not (kind == "chapter" and value.get("container-title") and (value.get("page") or value.get("chapter-number"))):
            raise ValueError("A source needs a title, URL or identified traditional book part")
        return value


class Metadata(MetadataBase):
    type: Literal['article', 'article-journal', 'article-magazine', 'article-newspaper', 'book', 'chapter', 'document', 'manuscript', 'paper-conference', 'patent', 'post-weblog', 'report', 'software', 'speech', 'standard', 'thesis', 'webpage'] = "document"
    language: Text | None = None
    author: list[Name] | None = None
    collection_editor: list[Name] | None = Field(default=None, alias='collection-editor')
    container_author: list[Name] | None = Field(default=None, alias='container-author')
    contributor: list[Name] | None = None
    editor: list[Name] | None = None
    translator: list[Name] | None = None
    accessed: Date | None = None
    event_date: Date | None = Field(default=None, alias='event-date')
    issued: Date | None = None
    original_date: Date | None = Field(default=None, alias='original-date')
    submitted: Date | None = None
    abstract: Text | None = None
    archive: Text | None = None
    archive_place: Text | None = Field(default=None, alias='archive-place')
    authority: Text | None = None
    collection_number: Text | int | float | None = Field(default=None, alias='collection-number')
    collection_title: Text | None = Field(default=None, alias='collection-title')
    container_title: Text | None = Field(default=None, alias='container-title')
    container_title_short: Text | None = Field(default=None, alias='container-title-short')
    DOI: Text | None = None
    edition: Text | int | float | None = None
    event_title: Text | None = Field(default=None, alias='event-title')
    event_place: Text | None = Field(default=None, alias='event-place')
    genre: Text | None = None
    ISBN: Text | None = None
    ISSN: Text | None = None
    issue: Text | int | float | None = None
    jurisdiction: Text | None = None
    medium: Text | None = None
    note: Text | None = None
    number: Text | int | float | None = None
    number_of_pages: Text | int | float | None = Field(default=None, alias='number-of-pages')
    number_of_volumes: Text | int | float | None = Field(default=None, alias='number-of-volumes')
    page: Text | int | float | None = None
    part_title: Text | None = Field(default=None, alias='part-title')
    PMCID: Text | None = None
    PMID: Text | None = None
    publisher: Text | None = None
    publisher_place: Text | None = Field(default=None, alias='publisher-place')
    section: Text | None = None
    status: Text | None = None
    title: Text | None = None
    title_short: Text | None = Field(default=None, alias='title-short')
    URL: Text | None = None
    version: Text | None = None
    volume: Text | int | float | None = None
    chapter_number: Text | int | float | None = Field(default=None, alias='chapter-number')

    # Remaining variables from the pinned CSL schema; export coverage is separate.
    chair: list[Name] | None = None
    compiler: list[Name] | None = None
    composer: list[Name] | None = None
    curator: list[Name] | None = None
    director: list[Name] | None = None
    editorial_director: list[Name] | None = Field(default=None, alias='editorial-director')
    executive_producer: list[Name] | None = Field(default=None, alias='executive-producer')
    guest: list[Name] | None = None
    host: list[Name] | None = None
    interviewer: list[Name] | None = None
    illustrator: list[Name] | None = None
    narrator: list[Name] | None = None
    organizer: list[Name] | None = None
    original_author: list[Name] | None = Field(default=None, alias='original-author')
    performer: list[Name] | None = None
    producer: list[Name] | None = None
    recipient: list[Name] | None = None
    reviewed_author: list[Name] | None = Field(default=None, alias='reviewed-author')
    script_writer: list[Name] | None = Field(default=None, alias='script-writer')
    series_creator: list[Name] | None = Field(default=None, alias='series-creator')
    available_date: Date | None = Field(default=None, alias='available-date')
    annote: Text | None = None
    archive_collection: Text | None = None
    archive_location: Text | None = None
    call_number: Text | None = Field(default=None, alias='call-number')
    citation_number: Text | int | float | None = Field(default=None, alias='citation-number')
    citation_label: Text | None = Field(default=None, alias='citation-label')
    dimensions: Text | None = None
    division: Text | None = None
    first_reference_note_number: Text | int | float | None = Field(default=None, alias='first-reference-note-number')
    keyword: Text | None = None
    locator: Text | int | float | None = None
    original_publisher: Text | None = Field(default=None, alias='original-publisher')
    original_publisher_place: Text | None = Field(default=None, alias='original-publisher-place')
    original_title: Text | None = Field(default=None, alias='original-title')
    page_first: Text | int | float | None = Field(default=None, alias='page-first')
    part: Text | int | float | None = None
    printing: Text | int | float | None = None
    references: Text | None = None
    reviewed_genre: Text | None = Field(default=None, alias='reviewed-genre')
    reviewed_title: Text | None = Field(default=None, alias='reviewed-title')
    scale: Text | None = None
    source: Text | None = None
    supplement: Text | int | float | None = None
    volume_title: Text | None = Field(default=None, alias='volume-title')
    volume_title_short: Text | None = Field(default=None, alias='volume-title-short')
    year_suffix: Text | None = Field(default=None, alias='year-suffix')

class NativeType(StrictModel):
    namespace: Text
    value: Text


class Patent(StrictModel):
    assignees: list[Name] | None = None
    application_number: Text | None = None
    priority_date: Date | None = None


class Identifiers(StrictModel):
    arxiv: Text | None = None
    oclc: Text | None = None

    @field_validator('arxiv',mode='before')
    @classmethod
    def normalized_arxiv(cls,value):
        return normalize_arxiv(value) if isinstance(value,str) else value


class Extensions(StrictModel):
    identifiers: Identifiers | None = None
    patent: Patent | None = None
    journal_series: Text | None = None


class TitleParts(StrictModel):
    main_title: Text | None = None


class Overrides(StrictModel):
    sort_title: Text | None = None


class Protection(StrictModel):
    protected_terms: list[Text] = Field(default_factory=list)
    preserve_case: bool = False


class SourceIdentity(StrictModel):
    namespace: Text | None = None
    library_uri: Text | None = None
    item_key: Text | None = None


class Context(StrictModel):
    text: Text
    origin: Literal["user", "agent", "import"]
    source_url: Text | None = None
    original_ref: Text | None = None


class Provenance(StrictModel):
    origin: Literal["user", "agent", "import", "derived"]
    access: Literal["metadata", "abstract", "full_text", "unknown"] = "unknown"
    source_url: Text | None = None
    observed_at: Text | None = None
    original_ref: Text | None = None
    source_identity: SourceIdentity | None = None


def normalize_loc(value: str | None) -> str | None:
    from unicodedata import normalize
    if value is None or value == '':
        return None
    if value.startswith('/') or any(part in ('', '.', '..') for part in value.split('/')) or '\x00' in value:
        raise ValueError('loc must be a relative folder path without empty or parent segments')
    return normalize('NFC', value)


class SourceCreate(StrictModel):
    schema_version: Literal["1.0"]
    citation_key: Text | None = None
    loc: str | None = None

    _loc = field_validator("loc")(normalize_loc)
    metadata: Metadata
    context: list[Context] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    title_protection: dict[str, Protection] = Field(default_factory=dict)
    native_type: NativeType | None = None
    extensions: Extensions = Field(default_factory=Extensions)
    overrides: Overrides = Field(default_factory=Overrides)
    title_parts: TitleParts = Field(default_factory=TitleParts)
    legacy_tags: list[Text] = Field(default_factory=list)
    key_author: Text | None = None

    @model_validator(mode='before')
    @classmethod
    def collapse_identifier_aliases(cls,value):
        if not isinstance(value,dict) or not isinstance(value.get('metadata'),dict):
            return value
        value = dict(value)
        metadata = value['metadata'] = dict(value['metadata'])
        if not isinstance(value.get('extensions',{}),dict):
            return value
        extensions = value['extensions'] = dict(value.get('extensions',{}))
        if not isinstance(extensions.get('identifiers',{}),dict):
            return value
        identifiers = dict(extensions.get('identifiers',{}))
        explicit = identifiers.get('arxiv')
        if isinstance(explicit,str):
            identifiers['arxiv'] = normalize_arxiv(explicit)
        number = metadata.get('number')
        if metadata.get('type') in ('article','manuscript') and isinstance(number,str) and str(metadata.get('archive','')).casefold()=='arxiv':
            number = metadata['number'] = normalize_arxiv(number)
            if not explicit or identifiers.get('arxiv') == number:
                identifiers['arxiv'] = number
                metadata.pop('number')
        doi = metadata.get('DOI')
        if isinstance(doi,str) and (derived := doi_arxiv(doi)) and not identifiers.get('arxiv'):
            identifiers['arxiv'] = derived
        if identifiers:
            extensions['identifiers'] = identifiers
        return value

    @field_validator("key_author")
    @classmethod
    def valid_key_author(cls, value: str | None) -> str | None:
        if value is not None:
            from refs.naming import creator_token
            creator_token(value)
        return value

    @field_validator("citation_key")
    @classmethod
    def valid_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if re.search(r'[\s\x00-\x1f\x7f,{}()=\\#%"]', value):
            raise ValueError("Citation key contains whitespace, controls or BibTeX delimiters")
        return value

    @model_validator(mode="after")
    def compatible(self) -> Self:
        metadata = self.metadata.model_dump(by_alias=True, exclude_none=True)
        kind = metadata["type"]
        if self.native_type is not None:
            label = self.native_type
            mappings = {row["zotero"]: row["canonical"] for row in REGISTRY["type_mappings"]} if label.namespace == "zotero" else REGISTRY["bib_type_aliases"] if label.namespace in ("bibtex", "biblatex") else {}
            if mappings.get(label.value) != kind:
                raise ValueError("Native label contradicts the canonical type or uses an unknown namespace")
        if self.extensions.patent is not None and kind != "patent":
            raise ValueError("Patent extensions require type patent")
        if self.extensions.journal_series is not None and kind != "article-journal":
            raise ValueError("Journal series requires article-journal")
        allowed = {field.alias or name for name, field in Metadata.model_fields.items() if "title" in (field.alias or name)}
        if set(self.title_protection) - allowed:
            raise ValueError("Protection applies only to supported title fields")
        main = self.title_parts.main_title
        title = metadata.get("title", "")
        if main and (not title.startswith(main) or len(title) > len(main) and title[len(main)].isalnum()):
            raise ValueError("main_title must be a complete-word prefix of title")
        self.legacy_tags = list(dict.fromkeys(self.legacy_tags))
        return self

    def canonical(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


def editable(record: dict) -> dict:
    return deepcopy({name:record[name] for name in SourceCreate.model_fields if name in record and record[name] is not None})


def revalidate(canonical: dict) -> dict:
    return SourceCreate.model_validate(canonical | {'citation_key':None}).canonical() | {'citation_key':canonical['citation_key']}


def parse(raw: bytes) -> SourceCreate:
    try:
        return SourceCreate.model_validate_json(raw)
    except ValidationError as exc:
        raise RefError("invalid_record", "Input does not match the supported record profile", 2,
                       details={"issues": exc.errors(include_url=False, include_context=False, include_input=False)}) from exc


class SourcePatch(StrictModel):
    schema_version: Literal["1.0"]
    set: dict = Field(default_factory=dict)
    clear: list[Text] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_paths(self) -> Self:
        if any(value is None for value in self.set.values()):
            raise ValueError("Use clear instead of null")
        if set(self.set) & set(self.clear):
            raise ValueError("A path cannot be set and cleared together")
        allowed = {"metadata", "native_type", "extensions", "title_protection", "title_parts", "overrides", "legacy_tags", "context", "provenance", "key_author", "loc"}
        paths = list(self.set) + self.clear
        if any(path.split(".")[0] not in allowed for path in paths):
            raise ValueError("Identity, files and internal state cannot be patched")
        if any(a != b and b.startswith(a + ".") for a in paths for b in paths):
            raise ValueError("Overlapping patch paths are ambiguous")
        return self


class OriginalReference(StrictModel):
    id: str
    sha256: str
    byte_length: int
    format: str
    origin: str
    locator: str


class SourceRecord(SourceCreate):
    @field_validator('citation_key')
    @classmethod
    def valid_key(cls, value: str | None) -> str | None:
        # Imported legacy keys remain readable; creation and export validate them.
        return value

    id: str
    citation_key: Text
    state: Literal['active', 'removed']
    revision: int = Field(ge=1)
    created_at: str
    updated_at: str
    corrected_fields: list[str]
    key_provenance: dict
    originals: list[OriginalReference]
    resources: list[dict]
    limitations: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)


class Issue(StrictModel):
    code: str
    message: str
    path: str | None
    details: dict
    retryable: bool


class Result(StrictModel):
    schema_version: Literal['1.0']
    command: str
    status: Literal['ok', 'partial', 'error']
    data: dict | None
    warnings: list[Issue]
    errors: list[Issue]


def schema(name: str) -> dict:
    models = {'source-create': SourceCreate, 'source-patch': SourcePatch, 'source-record': SourceRecord, 'result': Result}
    if name not in models:
        raise RefError('unknown_schema', 'Choose source-create, source-patch, source-record or result', 2)
    return models[name].model_json_schema(by_alias=True)
