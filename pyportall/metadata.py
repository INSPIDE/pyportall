import os
import httpx
from datetime import date
from typing import Dict, List, Optional, Union
from enum import Enum
from pydantic.main import BaseModel


class Aggregate(str, Enum):
    avg = "avg"
    count = "count"
    max = "max"
    min = "min"
    sum = "sum"


class DataType(str, Enum):
    integer = "integer"
    decimal = "decimal"
    text = "text"
    json = "json"


class IndicatorMetadata(BaseModel):
    code: str
    name: str
    description: str
    unit: Optional[str] = None
    format: Optional[str] = None
    coverage: Optional[str] = None
    resolution: Optional[str] = None
    data_source: str
    computed_date: date
    aggregate_fn: Aggregate
    data_type: DataType


class MetadataHelper:
    def __init__(self, metadata_url: Optional[str] = None) -> None:
        self.metadata_url: str = metadata_url or os.getenv("METADATA_URL", "https://portall-api.inspide.com/v0/metadata/indicators/")
        self.metadata: Dict[str, IndicatorMetadata] = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in httpx.get(self.metadata_url).json()}

    def all(self) -> List[IndicatorMetadata]:
        return [indicator for indicator in self.metadata.values()]

    def get(self, indicator_code: str) -> Union[IndicatorMetadata, None]:
        return self.metadata.get(indicator_code)

    def refresh(self) -> None:
        self.metadata = {indicator["code"]: IndicatorMetadata(**indicator) for indicator in httpx.get(self.metadata_url).json()}
