# tls-fingerprint-scraper-demo

**By Feedsmith.**

> Empty results behind Cloudflare are often a **TLS fingerprint check before the
> page even renders**, not a CAPTCHA.

When you read a public site with a plain Python client and get a blank body, the
common assumption is "CAPTCHA" or "I got blocked." Frequently the real cause is
earlier and quieter: your client was flagged during the **TLS handshake** by its
fingerprint (JA3 / JA4), before any HTML was served. A browser-like TLS handshake
(via `curl_cffi` with `impersonate="chrome"`) lets a legitimate client read the
same public page a normal visitor sees.

This demo proves the difference safely. It reflects **our own** TLS fingerprint
off a public echo service with two clients and compares the JA3 hashes.

## Quickstart

```bash
pip install -e '.[dev,impersonate]'
pytest
python scripts/live_demo.py
```

- `pytest` runs fully **offline and deterministic** (httpx is mocked; the
  impersonated path is tested without requiring `curl_cffi`).
- `scripts/live_demo.py` is the **only** file that touches the network.

## Sample output

```text
Reading public TLS echo service: https://tls.peet.ws/api/all

Default client (httpx):
  user_agent : python-httpx/0.27.0
  ja3_hash   : 9c673fd64a32c8dc1b1e3a8f3a9c1c44

Browser-like client (curl_cffi, impersonate='chrome'):
  user_agent : Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ... Chrome/124.0.0.0 Safari/537.36
  ja3_hash   : 773906b0efdefa24a7f2b8eb6985bf37

Comparison:
  plain  ja3_hash : 9c673fd64a32c8dc1b1e3a8f3a9c1c44
  chrome ja3_hash : 773906b0efdefa24a7f2b8eb6985bf37
  differ          : True

Takeaway: The two clients present different TLS fingerprints during the
handshake, so a public site can distinguish a default client from a normal
browser before the page renders.
```

## How it works

- `tlsdemo/fingerprint.py` — `parse_fingerprint`, `fetch_plain` (httpx),
  `fetch_impersonated` (lazy `curl_cffi`).
- `tlsdemo/compare.py` — `compare` two parsed fingerprints and report `differ`.
- `docs/why-tls-fingerprint.md` — the full explanation of JA3 / TLS ClientHello
  fingerprinting and why a default Python client is easy to distinguish from a
  browser.

## Scope

This project is educational and **legal-safe**:

- It reads **public sources** only — the same factual, non-PII data a normal
  visitor sees in a browser.
- It **respects robots.txt and rate limits** and behaves like a normal visitor.
- The demo only reflects **your own** fingerprint off a public echo service.
- A matching TLS fingerprint is used to **reliably read public data like a normal
  visitor**, never to reach anything private or authenticated, and never to
  collect private personal data. Use it only on data **you operate and own** or
  data that is plainly public and factual.
