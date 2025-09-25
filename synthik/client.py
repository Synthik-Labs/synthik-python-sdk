from __future__ import annotations

from .endpoints import SynthikClient as _SynthikClient

# Thin re-export to keep a stable API surface
class SynthikClient(_SynthikClient):
    pass
