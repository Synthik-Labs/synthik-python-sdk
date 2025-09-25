from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

# Mirror backend request types

GenerationStrategy = Literal["neural_argn", "llm_structured", "adaptive_flow"]
TabularExportFormat = Literal["json", "csv", "parquet", "arrow", "excel"]
TextOutputFormat = Literal["instruction", "conversation", "json"]


@dataclass
class ColumnDescription:
    name: str
    dtype: str
    description: Optional[str] = None
    sample_values: Optional[List[Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    max_length: Optional[int] = None


class ColumnBuilder:
    def __init__(self, name: str, dtype: str):
        self._col = ColumnDescription(name=name, dtype=dtype)

    @staticmethod
    def string(name: str, *, description: Optional[str] = None, max_length: Optional[int] = None, constraints: Optional[Dict[str, Any]] = None, sample_values: Optional[List[Any]] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "string")
        b._col.description = description
        b._col.max_length = max_length
        b._col.constraints = constraints
        b._col.sample_values = sample_values
        return b

    @staticmethod
    def int(name: str, *, description: Optional[str] = None, constraints: Optional[Dict[str, Any]] = None, sample_values: Optional[List[int]] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "integer")
        b._col.description = description
        b._col.constraints = constraints
        b._col.sample_values = sample_values # type: ignore
        return b

    @staticmethod
    def float(name: str, *, description: Optional[str] = None, constraints: Optional[Dict[str, Any]] = None, sample_values: Optional[List[float]] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "float")
        b._col.description = description
        b._col.constraints = constraints
        b._col.sample_values = sample_values # type: ignore
        return b

    @staticmethod
    def categorical(name: str, categories: List[str], *, description: Optional[str] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "string")
        b._col.description = description
        b._col.sample_values = categories
        if b._col.constraints is None:
            b._col.constraints = {}
        b._col.constraints["one_of"] = categories
        return b

    @staticmethod
    def email(name: str = "email", *, description: Optional[str] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "string")
        b._col.description = description or "Valid email address"
        b._col.constraints = (b._col.constraints or {})
        b._col.constraints["regex"] = r"^[^@\n\s]+@[^@\n\s]+\.[^@\n\s]+$"
        return b

    @staticmethod
    def uuid(name: str = "id", *, description: Optional[str] = None) -> "ColumnBuilder":
        b = ColumnBuilder(name, "string")
        b._col.description = description or "UUID v4"
        b._col.constraints = (b._col.constraints or {})
        b._col.constraints["regex"] = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
        return b

    def desc(self, description: str) -> "ColumnBuilder":
        self._col.description = description
        return self

    def samples(self, values: List[Any]) -> "ColumnBuilder":
        self._col.sample_values = values
        return self

    def constrain(self, key: str, value: Any) -> "ColumnBuilder":
        if self._col.constraints is None:
            self._col.constraints = {}
        self._col.constraints[key] = value
        return self

    def build(self) -> ColumnDescription:
        return ColumnDescription(**vars(self._col))


@dataclass
class DatasetGenerationRequest:
    num_rows: int
    columns: List[ColumnDescription]
    topic: str
    seed: Optional[int] = None
    additional_constraints: Optional[Dict[str, Any]] = None


@dataclass
class TextDatasetGenerationRequest:
    num_samples: int
    task_definition: str
    data_domain: str
    data_description: str
    output_format: TextOutputFormat
    sample_examples: Optional[List[Dict[str, Any]]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class SyntheticTextSample:
    data: Union[Dict[str, Any], List[Dict[str, Any]]]


@dataclass
class SyntheticTextDatasetResponse:
    data: List[SyntheticTextSample]
    metadata: Optional[Dict[str, Any]] = None
