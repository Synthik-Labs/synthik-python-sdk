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
    def __init__(self, http: HttpClient, api_version: str, warn: bool):
        self.http = http
        self._api_version = api_version
        self._warn = warn
        if warn and api_version == "v1":
            import warnings
            warnings.warn("Tabular v1 endpoints are deprecated and will sunset 2025-09-26. Switch to api_version='v2'.", DeprecationWarning, stacklevel=2)

    # ----- Explicit versioned helpers -----
    def v1_generate(self, req: DatasetGenerationRequest, *, strategy: GenerationStrategy = "adaptive_flow", format: TabularExportFormat = "json", batch_size: int = 256):
        import warnings; warnings.warn("v1_generate() deprecated; use v2_generate()", DeprecationWarning, stacklevel=2)
        return self._generate(req, strategy=strategy, format=format, batch_size=batch_size, version="v1")

    def v2_generate(self, req: DatasetGenerationRequest, *, strategy: GenerationStrategy = "adaptive_flow", format: TabularExportFormat = "json", batch_size: int = 256):
        return self._generate(req, strategy=strategy, format=format, batch_size=batch_size, version="v2")

    def _generate(self, req: DatasetGenerationRequest, *, strategy: GenerationStrategy, format: TabularExportFormat, batch_size: int, version: str):
        return self.http.request(
            "POST",
            f"/api/{version}/tabular/generate",
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

    def generate(self, *args, **kwargs):
        """Backward-compatible alias that dispatches based on configured api_version."""
        if self._api_version == "v1":
            return self.v1_generate(*args, **kwargs)
        return self.v2_generate(*args, **kwargs)

    def strategies(self) -> Dict[str, Any]:
        return self.http.request("GET", f"/api/{self._api_version}/tabular/strategies")

    def analyze(self, req: DatasetGenerationRequest) -> Dict[str, Any]:
        return self.http.request(
            "POST",
            f"/api/{self._api_version}/tabular/analyze",
            body={
                "num_rows": req.num_rows,
                "topic": req.topic,
                "columns": [vars(c) for c in req.columns],
            },
        )

    def validate(self, data: List[Dict[str, Any]], columns: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.http.request(
            "POST",
            f"/api/{self._api_version}/tabular/validate",
            body={"data": data, "schema": {"columns": columns}},
        )

    def status(self) -> Dict[str, Any]:
        return self.http.request("GET", f"/api/{self._api_version}/tabular/status")


class TextClient:
    def __init__(self, http: HttpClient, api_version: str, warn: bool):
        self.http = http
        self._api_version = api_version
        self._warn = warn
        if warn and api_version == "v1":
            import warnings
            warnings.warn("Text v1 endpoints are deprecated and will sunset 2025-09-26. Switch to api_version='v2'.", DeprecationWarning, stacklevel=2)

    def v1_generate(self, req: TextDatasetGenerationRequest):
        import warnings; warnings.warn("v1_generate() deprecated; use v2_generate()", DeprecationWarning, stacklevel=2)
        return self.http.request("POST", "/api/v1/text/generate", body=vars(req))

    def v2_generate(self, req: TextDatasetGenerationRequest):
        return self.http.request("POST", "/api/v2/text/generate", body=vars(req))

    def generate(self, req: TextDatasetGenerationRequest) -> SyntheticTextDatasetResponse:
        if self._api_version == "v1":
            return self.v1_generate(req)
        return self.v2_generate(req)

    def info(self) -> Dict[str, Any]:
        # info endpoint only exists in v1 (deprecated) and v2 path may differ; fallback gracefully
        path = f"/api/{self._api_version}/text/info"
        return self.http.request("GET", path)

    def validate(self, req: TextDatasetGenerationRequest) -> Dict[str, Any]:
        return self.http.request("POST", f"/api/{self._api_version}/text/validate", body=vars(req))

    def examples(self) -> Dict[str, Any]:
        return self.http.request("GET", f"/api/{self._api_version}/text/examples")


class SynthikClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
        retries: int = 2,
        retry_backoff: float = 0.5,
        api_version: str = "v1",
        warn_on_deprecated: bool = True,
    ):
        base = (base_url or "https://moral-danice-poeai-c2f6213c.koyeb.app/").rstrip("/")
        self.http = HttpClient(HttpClientOptions(base_url=base, api_key=api_key, timeout=timeout, retries=retries, retry_backoff=retry_backoff))
        if api_version not in {"v1", "v2"}:
            raise ValueError("api_version must be 'v1' or 'v2'")
        self.api_version = api_version
        self.tabular = TabularClient(self.http, api_version, warn_on_deprecated)
        self.text = TextClient(self.http, api_version, warn_on_deprecated)
        self.auth = AuthClient(self.http, api_version, warn_on_deprecated)


class AuthClient:
    """Authentication helper methods (register, login, token ops)."""
    def __init__(self, http: HttpClient, api_version: str, warn: bool):
        self.http = http
        self._api_version = api_version
        if warn and api_version == "v1":
            import warnings
            warnings.warn("Auth v1 endpoints are deprecated; switch to /api/v2/auth.", DeprecationWarning, stacklevel=2)

    # Explicit versioned helpers
    def v1_register(self, email: str, password: str):
        import warnings; warnings.warn("v1_register deprecated; use v2_register", DeprecationWarning, stacklevel=2)
        return self.http.request("POST", "/api/v1/auth/register", body={"email": email, "password": password})

    def v2_register(self, email: str, password: str):
        return self.http.request("POST", "/api/v2/auth/register", body={"email": email, "password": password})

    def v1_login(self, email: str, password: str):
        import warnings; warnings.warn("v1_login deprecated; use v2_login", DeprecationWarning, stacklevel=2)
        return self.http.request("POST", "/api/v1/auth/login", body={"email": email, "password": password})

    def v2_login(self, email: str, password: str):
        return self.http.request("POST", "/api/v2/auth/login", body={"email": email, "password": password})

    def register(self, email: str, password: str):
        return self.v1_register(email, password) if self._api_version == "v1" else self.v2_register(email, password)

    def login(self, email: str, password: str):
        return self.v1_login(email, password) if self._api_version == "v1" else self.v2_login(email, password)

    def validate_token(self, token: str):
        path = f"/api/{self._api_version}/auth/token/validate"
        # Use explicit Authorization header override to test arbitrary token
        return self.http.request("GET", path, headers={"Authorization": f"Bearer {token}"})

    def list_tokens(self, include_revoked: bool = False, include_expired: bool = False):
        path = f"/api/{self._api_version}/auth/tokens"
        return self.http.request("GET", path, query={
            "include_revoked": include_revoked,
            "include_expired": include_expired,
        })

    def revoke(self, token: str):
        path = f"/api/{self._api_version}/auth/revoke"
        return self.http.request("POST", path, body={"token": token})

    def revoke_by_id(self, token_id: int):
        path = f"/api/{self._api_version}/auth/revoke/by-id"
        return self.http.request("POST", path, body={"token_id": token_id})

    def me(self):
        path = f"/api/{self._api_version}/auth/me"
        return self.http.request("GET", path)
