"""Strict walking-skeleton input. T013 broadens this bounded profile."""

import re
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from refs.results import RefError

Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Name(StrictModel):
    family: Text | None = None
    given: Text | None = None
    literal: Text | None = None

    @model_validator(mode="after")
    def name_form(self) -> Self:
        if self.literal is not None:
            if self.family is not None or self.given is not None:
                raise ValueError("A literal name cannot contain personal name fields")
        elif self.family is None:
            raise ValueError("This milestone requires family or literal for each name")
        return self


class Year(StrictModel):
    date_parts: list[list[int]] = Field(alias="date-parts")

    @field_validator("date_parts")
    @classmethod
    def one_year(cls, value: list[list[int]]) -> list[list[int]]:
        if len(value) != 1 or len(value[0]) != 1 or not 1 <= value[0][0] <= 9999:
            raise ValueError("This milestone supports a single issued year; richer dates follow in T013")
        return value


class Article(StrictModel):
    type: Literal["article-journal"]
    title: Text
    author: list[Name] = Field(default_factory=list)
    issued: Year | None = None
    container_title: Text | None = Field(default=None, alias="container-title")
    volume: Text | None = None
    issue: Text | None = None
    page: Text | None = None
    DOI: Text | None = None
    URL: Text | None = None
    language: Literal["en", "en-US", "en-GB"] = "en"


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


class SourceCreate(StrictModel):
    schema_version: Literal["1.0"]
    citation_key: Text
    metadata: Article
    context: list[Context] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    title_protection: dict[Literal["title", "container-title"], Protection] = Field(default_factory=dict)
    native_type: None = None
    extensions: dict = Field(default_factory=dict)
    overrides: dict = Field(default_factory=dict)
    title_parts: dict = Field(default_factory=dict)
    legacy_tags: list[Text] = Field(default_factory=list)
    key_author: None = None

    @field_validator("citation_key")
    @classmethod
    def valid_key(cls, value: str) -> str:
        if re.search(r'[\s\x00-\x1f\x7f,{}()=\\#%"]', value):
            raise ValueError("Citation key contains whitespace, controls or BibTeX delimiters")
        return value

    @field_validator("extensions", "overrides", "title_parts", "legacy_tags")
    @classmethod
    def later_values(cls, value):
        if value:
            raise ValueError("This field is not supported by the walking skeleton; see T013")
        return value

    def canonical(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


def parse(raw: bytes) -> SourceCreate:
    try:
        return SourceCreate.model_validate_json(raw)
    except ValidationError as exc:
        raise RefError("invalid_record", "Input is outside the supported milestone record profile", 2,
                       details={"issues": exc.errors(include_url=False, include_context=False, include_input=False)}) from exc
