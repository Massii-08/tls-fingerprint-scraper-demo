"""Compare two parsed TLS fingerprints (a default client vs a browser-like one)."""
from __future__ import annotations

from typing import Any, Dict


def compare(plain_fp: Dict[str, Any], chrome_fp: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two parsed fingerprints and report whether they differ.

    Both fingerprints reflect our own client off a public echo service. When
    the JA3 hashes differ, the two clients present different TLS fingerprints
    during the handshake, which is what lets a public site tell a default
    Python client apart from a normal browser before any page renders.
    """
    plain_hash = plain_fp.get("ja3_hash")
    chrome_hash = chrome_fp.get("ja3_hash")
    return {
        "plain_ja3_hash": plain_hash,
        "chrome_ja3_hash": chrome_hash,
        "differ": plain_hash != chrome_hash,
        "note": (
            "The two clients present different TLS fingerprints during the "
            "handshake, so a public site can distinguish a default client from "
            "a normal browser before the page renders."
        ),
    }
