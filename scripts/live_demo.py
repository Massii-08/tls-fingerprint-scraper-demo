"""Live demo: reflect our own TLS fingerprint off a public echo service.

THIS IS THE ONLY FILE IN THE REPO THAT TOUCHES THE NETWORK.

Run it manually:

    python scripts/live_demo.py

It fetches https://tls.peet.ws/api/all twice: once with a default httpx
client and once with curl_cffi impersonating Chrome. It then prints both JA3
hashes and whether they differ. We only read public data like a normal visitor
and reflect our OWN fingerprint; we never access anything private or authed.
"""
from __future__ import annotations

from tlsdemo.compare import compare
from tlsdemo.fingerprint import (
    FpError,
    fetch_impersonated,
    fetch_plain,
    parse_fingerprint,
)

ECHO_URL = "https://tls.peet.ws/api/all"


def main() -> None:
    """Fetch with both clients, parse, and print the comparison."""
    print("Reading public TLS echo service: {0}".format(ECHO_URL))
    print()

    # 1) Default Python client (httpx).
    try:
        plain_raw = fetch_plain(ECHO_URL)
        plain_fp = parse_fingerprint(plain_raw)
    except FpError as exc:
        print("Plain (httpx) fetch failed: {0}".format(exc))
        return

    print("Default client (httpx):")
    print("  user_agent : {0}".format(plain_fp.get("user_agent")))
    print("  ja3_hash   : {0}".format(plain_fp.get("ja3_hash")))
    print()

    # 2) Browser-like client (curl_cffi impersonating Chrome).
    chrome_fp = None
    try:
        chrome_raw = fetch_impersonated(ECHO_URL, impersonate="chrome")
        chrome_fp = parse_fingerprint(chrome_raw)
        print("Browser-like client (curl_cffi, impersonate='chrome'):")
        print("  user_agent : {0}".format(chrome_fp.get("user_agent")))
        print("  ja3_hash   : {0}".format(chrome_fp.get("ja3_hash")))
        print()
    except FpError as exc:
        print("Browser-like client unavailable: {0}".format(exc))
        print("Install the optional dependency to run the full demo:")
        print("    pip install '.[impersonate]'")
        print()

    if chrome_fp is None:
        return

    result = compare(plain_fp, chrome_fp)
    print("Comparison:")
    print("  plain  ja3_hash : {0}".format(result["plain_ja3_hash"]))
    print("  chrome ja3_hash : {0}".format(result["chrome_ja3_hash"]))
    print("  differ          : {0}".format(result["differ"]))
    print()
    print("Takeaway: {0}".format(result["note"]))


if __name__ == "__main__":
    main()
