"""tlsdemo: educational TLS fingerprint comparison for reading public data.

This package demonstrates that many "empty page / blank results" cases when
reading a public site are a TLS handshake fingerprint check (e.g. JA3) that
flags non-browser clients before the page renders, not a CAPTCHA.
"""
from __future__ import annotations

__version__ = "0.1.0"
