# Synthik Python SDK Changelog

## 0.2.0
- Added `api_version` parameter (v1 default, v2 recommended).
- Added explicit `v1_generate` / `v2_generate` methods for Tabular and Text clients with deprecation warnings for v1.
- Added MIGRATION.md reference.
- Unified `generate()` now dispatches based on configured `api_version`.
- Added `AuthClient` with `register`, `login`, token lifecycle helpers (default v2, deprecated v1 helpers retained with warnings).

## 0.1.0
- Initial release.
