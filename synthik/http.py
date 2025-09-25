from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

import requests


class HttpError(RuntimeError):
    def __init__(self, status: int, message: str, body: Any | None = None):
        super().__init__(f"HTTP {status} {message}")
        self.status = status
        self.message = message
        self.body = body


@dataclass
class HttpClientOptions:
    base_url: str
    api_key: Optional[str] = None
    timeout: float = 60.0
    retries: int = 2
    retry_backoff: float = 0.5
    default_headers: Optional[Mapping[str, str]] = None


class HttpClient:
    def __init__(self, opts: HttpClientOptions):
        self.base_url = opts.base_url.rstrip("/")
        self.api_key = opts.api_key
        self.timeout = opts.timeout
        self.retries = max(0, opts.retries)
        self.retry_backoff = max(0.0, opts.retry_backoff)
        self.default_headers: Dict[str, str] = {
            "Content-Type": "application/json",
        }
        if opts.default_headers:
            self.default_headers.update(dict(opts.default_headers))
        if self.api_key and "Authorization" not in self.default_headers:
            self.default_headers["Authorization"] = f"Bearer {self.api_key}"

    def request(self, method: str, path: str, *, body: Any | None = None, query: Optional[Mapping[str, Any]] = None, headers: Optional[Mapping[str, str]] = None):
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        hdrs = dict(self.default_headers)
        if headers:
            hdrs.update(dict(headers))

        params: Dict[str, str] = {}
        if query:
            for k, v in query.items():
                if v is not None:
                    params[k] = str(v)

        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                resp = requests.request(method, url, headers=hdrs, params=params, data=json.dumps(body) if body is not None else None, timeout=self.timeout)
                if 200 <= resp.status_code < 300:
                    ctype = resp.headers.get("content-type", "")
                    if "application/json" in ctype:
                        return resp.json()
                    return resp.content
                try:
                    err_body = resp.json()
                except Exception:
                    err_body = resp.text
                raise HttpError(resp.status_code, resp.reason, err_body)
            except (requests.Timeout, requests.ConnectionError, HttpError) as e:
                last_err = e
                retryable = isinstance(e, (requests.Timeout, requests.ConnectionError)) or (isinstance(e, HttpError) and e.status >= 500)
                if attempt == self.retries or not retryable:
                    break
                time.sleep(self.retry_backoff * (2 ** attempt))
        assert last_err is not None
        raise last_err
