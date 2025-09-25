from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from .http import HttpClient, HttpClientOptions
from .types import (
    DatasetGenerationRequest,
    TextDatasetGenerationRequest,
    GenerationStrategy,
    TabularExportFormat,
    SyntheticTextDatasetResponse,
)


class TabularClient:
    def __init__(self, http: HttpClient):
        self.http = http

    def generate(
        self,
        req: DatasetGenerationRequest,
        *,
        strategy: GenerationStrategy = "adaptive_flow",
        format: TabularExportFormat = "json",
        batch_size: int = 256,
    ) -> Any:
        return self.http.request(
            "POST",
            "/api/v1/tabular/generate",
            body={
                "num_rows": req.num_rows,
                "topic": req.topic,
                "columns": [vars(c) for c in req.columns],
                **({"seed": req.seed} if req.seed is not None else {}),
                **(
                    {"additional_constraints": req.additional_constraints}
                    if req.additional_constraints is not None
                    else {}
                ),
            },
            query={
                "strategy": strategy,
                "format": format,
                "batch_size": batch_size,
            },
        )

    def strategies(self) -> Dict[str, Any]:
        return self.http.request("GET", "/api/v1/tabular/strategies")

    def analyze(self, req: DatasetGenerationRequest) -> Dict[str, Any]:
        return self.http.request(
            "POST",
            "/api/v1/tabular/analyze",
            body={
                "num_rows": req.num_rows,
                "topic": req.topic,
                "columns": [vars(c) for c in req.columns],
            },
        )

    def validate(self, data: List[Dict[str, Any]], columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.http.request(
            "POST",
            "/api/v1/tabular/validate",
            body={"data": data, "schema": {"columns": columns}},
        )

    def status(self) -> Dict[str, Any]:
        return self.http.request("GET", "/api/v1/tabular/status")


class TextClient:
    def __init__(self, http: HttpClient):
        self.http = http

    def generate(self, req: TextDatasetGenerationRequest) -> SyntheticTextDatasetResponse:
        return self.http.request("POST", "/api/v1/text/generate", body=vars(req))

    def info(self) -> Dict[str, Any]:
        return self.http.request("GET", "/api/v1/text/info")

    def validate(self, req: TextDatasetGenerationRequest) -> Dict[str, Any]:
        return self.http.request("POST", "/api/v1/text/validate", body=vars(req))

    def examples(self) -> Dict[str, Any]:
        return self.http.request("GET", "/api/v1/text/examples")


class SynthikClient:
    def __init__(self, *, base_url: str | None = None, api_key: str | None = None, timeout: float = 60.0, retries: int = 2, retry_backoff: float = 0.5):
        base = (base_url or "https://moral-danice-poeai-c2f6213c.koyeb.app/").rstrip("/")
        self.http = HttpClient(HttpClientOptions(base_url=base, api_key=api_key, timeout=timeout, retries=retries, retry_backoff=retry_backoff))
        self.tabular = TabularClient(self.http)
        self.text = TextClient(self.http)
