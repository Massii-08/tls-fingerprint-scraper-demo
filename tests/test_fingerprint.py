"""Offline tests for fingerprint parsing and fetching.

No network access. httpx is exercised via httpx.MockTransport, and the
impersonated path is tested by simulating curl_cffi being unavailable, so the
suite passes whether or not curl_cffi is installed.
"""
from __future__ import annotations

import builtins
import json
import os
from typing import Any, Dict

import httpx
import pytest

from tlsdemo.fingerprint import (
    FpError,
    fetch_impersonated,
    fetch_plain,
    parse_fingerprint,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name: str) -> Dict[str, Any]:
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_parse_fingerprint_extracts_fields() -> None:
    echo = _load("peet_plain.json")
    parsed = parse_fingerprint(echo)
    assert parsed["ja3"] == echo["tls"]["ja3"]
    assert parsed["ja3_hash"] == "9c673fd64a32c8dc1b1e3a8f3a9c1c44"
    assert parsed["user_agent"] == "python-httpx/0.27.0"
    assert parsed["http_version"] == "h2"


def test_parse_fingerprint_is_defensive_with_missing_nested() -> None:
    parsed = parse_fingerprint({})
    assert parsed["ja3"] is None
    assert parsed["ja3_hash"] is None
    assert parsed["user_agent"] is None
    assert parsed["http_version"] is None


def test_fetch_plain_success_with_mock_transport() -> None:
    echo = _load("peet_plain.json")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=echo)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        result = fetch_plain("https://tls.peet.ws/api/all", client=client)

    assert result == echo
    parsed = parse_fingerprint(result)
    assert parsed["ja3_hash"] == "9c673fd64a32c8dc1b1e3a8f3a9c1c44"


def test_fetch_plain_raises_fperror_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        with pytest.raises(FpError):
            fetch_plain("https://tls.peet.ws/api/all", client=client)


def test_fetch_impersonated_raises_when_curl_cffi_missing() -> None:
    real_import = builtins.__import__

    def blocking_import(name, *args, **kwargs):
        if name == "curl_cffi" or name.startswith("curl_cffi."):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)

    builtins.__import__ = blocking_import
    try:
        with pytest.raises(FpError) as exc_info:
            fetch_impersonated("https://tls.peet.ws/api/all")
        assert "curl_cffi not installed" in str(exc_info.value)
    finally:
        builtins.__import__ = real_import
