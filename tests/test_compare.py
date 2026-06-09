"""Offline tests for fingerprint comparison."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from tlsdemo.compare import compare
from tlsdemo.fingerprint import parse_fingerprint

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name: str) -> Dict[str, Any]:
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


def test_compare_different_fingerprints_differ_true() -> None:
    plain_fp = parse_fingerprint(_load("peet_plain.json"))
    chrome_fp = parse_fingerprint(_load("peet_chrome.json"))

    result = compare(plain_fp, chrome_fp)

    assert result["plain_ja3_hash"] == "9c673fd64a32c8dc1b1e3a8f3a9c1c44"
    assert result["chrome_ja3_hash"] == "773906b0efdefa24a7f2b8eb6985bf37"
    assert result["differ"] is True


def test_compare_identical_fingerprints_differ_false() -> None:
    chrome_fp = parse_fingerprint(_load("peet_chrome.json"))

    result = compare(chrome_fp, chrome_fp)

    assert result["differ"] is False
    assert result["plain_ja3_hash"] == result["chrome_ja3_hash"]


def test_compare_note_is_non_empty_legal_safe_string() -> None:
    plain_fp = parse_fingerprint(_load("peet_plain.json"))
    chrome_fp = parse_fingerprint(_load("peet_chrome.json"))

    result = compare(plain_fp, chrome_fp)
    note = result["note"]

    assert isinstance(note, str)
    assert note.strip()
    lowered = note.lower()
    for forbidden in ("bypass", "evade", "defeat", "break"):
        assert forbidden not in lowered
