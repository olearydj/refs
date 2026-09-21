import sys, json, dataclasses, warnings
warnings.simplefilter("error")
import pydantic, pydantic_core
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError
print(sys.version.split()[0], pydantic.VERSION, pydantic_core.__version__)
# PEP 649/749 deferred annotations: forward ref without quotes or __future__
class Node(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    key: str
    children: list[Node] = []
    when: Later | None = None
class Later(BaseModel):
    y: int
Node.model_rebuild()
print(Node.model_validate_json('{"key":"a","children":[{"key":"b"}],"when":{"y":1}}'))
try: Node.model_validate_json('{"key":1}')
except ValidationError as e: print("strict ok:", e.errors(include_url=False)[0]["type"])
@dataclasses.dataclass(frozen=True, slots=True)
class Plain:
    key: str
    n: int = 0
ta = TypeAdapter(Plain)
print("stdlib dataclass schema via TypeAdapter:", json.dumps(ta.json_schema()))
print(ta.validate_json('{"key":"k","n":2}'))
