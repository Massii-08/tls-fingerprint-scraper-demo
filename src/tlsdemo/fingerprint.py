"""TLS fingerprint extraction and fetching from a public echo service.

We read public data like a normal visitor and reflect our own TLS
fingerprint off a public echo service. A default Python HTTP client presents
a different TLS ClientHello than a real browser, which some public sites use
to decide whether to render the page at all.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class FpError(Exception):
    """Raised when a fingerprint cannot be fetched or parsed."""


def parse_fingerprint(echo_json: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the relevant TLS fields from a public echo response.

    Defensive with nested ``.get`` so a partially shaped response does not
    raise; missing values become ``None``.
    """
    tls = echo_json.get("tls") or {}
    return {
        "ja3": tls.get("ja3"),
        "ja3_hash": tls.get("ja3_hash"),
        "user_agent": echo_json.get("user_agent"),
        "http_version": echo_json.get("http_version"),
    }


def fetch_plain(
    url: str,
    client: Optional[Any] = None,
    timeout: float = 20.0,
) -> Dict[str, Any]:
    """GET ``url`` with a default httpx client and return parsed JSON.

    If ``client`` is provided it is used as-is (useful for tests via
    ``httpx.MockTransport``); otherwise a short-lived client is created.
    Raises :class:`FpError` on any failure.
    """
    try:
        if client is not None:
            response = client.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        with httpx.Client(timeout=timeout) as owned_client:
            response = owned_client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as exc:  # noqa: BLE001 - surface a single error type
        raise FpError("plain fetch failed: {0}".format(exc)) from exc


def fetch_impersonated(
    url: str,
    impersonate: str = "chrome",
    timeout: float = 20.0,
) -> Dict[str, Any]:
    """GET ``url`` while presenting a real browser's TLS ClientHello.

    ``curl_cffi`` mirrors a browser's TLS handshake so a public page renders
    for you like it would for a normal visitor. The import is lazy so the rest
    of the package (and the test suite) works without ``curl_cffi`` installed.
    Raises :class:`FpError` if the dependency is missing or the request fails.
    """
    try:
        from curl_cffi import requests as curl_requests
    except ImportError as exc:
        raise FpError(
            "curl_cffi not installed; pip install '.[impersonate]'"
        ) from exc

    try:
        response = curl_requests.get(url, impersonate=impersonate, timeout=timeout)
        return response.json()
    except Exception as exc:  # noqa: BLE001 - surface a single error type
        raise FpError("impersonated fetch failed: {0}".format(exc)) from exc
