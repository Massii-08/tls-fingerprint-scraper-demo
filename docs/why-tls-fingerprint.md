# Why a TLS fingerprint, not a CAPTCHA

When you read a public site with a plain script and get an empty page or blank
results, the reflex is to assume a CAPTCHA or a "you've been blocked" wall. Very
often the truth is earlier and quieter: your client was flagged **before the page
ever rendered**, during the TLS handshake, by its **fingerprint**.

## The TLS ClientHello and JA3

Every HTTPS request starts with a TLS handshake. The first message your client
sends is the **ClientHello**, which advertises:

- the TLS version it supports,
- the ordered list of cipher suites,
- the TLS extensions it offers (and their order),
- supported elliptic curves and point formats.

These details are not secret, but they are **specific to the library that built
the request**. A browser's TLS stack (BoringSSL in Chrome, NSS in Firefox)
produces a very different ClientHello than Python's default stack.

**JA3** is a popular way to summarize that ClientHello: it concatenates those
fields into a string and hashes it. The result is a short fingerprint like
`773906b0efdefa24a7f2b8eb6985bf37`. **JA4** is a newer, more robust variant of
the same idea. A site (or a CDN in front of it) can compute this fingerprint on
every connection and decide what to serve.

## Why a default Python client stands out

A real Chrome on macOS produces one well-known JA3. A default `httpx` or
`requests` client produces a different, equally well-known one. So even with a
perfectly browser-like `User-Agent` header, the **handshake itself** still says
"this is a scripting library." Header spoofing happens *after* the handshake and
cannot change the fingerprint that was already sent.

That is why the same public URL can return a full page in your browser and an
empty body to your script: the decision was made at the TLS layer, not at a
CAPTCHA.

## How curl_cffi mirrors a real browser handshake

[`curl_cffi`](https://github.com/lexiforest/curl_cffi) wraps a build of curl
linked against a TLS library configured to **replicate a real browser's
ClientHello**. With `impersonate="chrome"` it sends the same cipher order and
extensions a current Chrome would, so the JA3/JA4 fingerprint matches a normal
visitor's browser. The public page then renders for you the way it renders for
any other visitor.

In this demo we prove the difference safely: we reflect **our own** fingerprint
off a public echo service (`tls.peet.ws/api/all`) with both clients and compare
the two JA3 hashes. The hashes differ, which is exactly the signal a site uses
to tell a default client apart from a browser.

## Legal-safe framing

This technique is about **reliably reading public, factual, non-PII data like a
normal visitor would**. It is not about getting at anything private or
authenticated.

- We read **public sources** only, the same data any visitor sees in a browser.
- We **respect robots.txt and rate limits** and behave like a normal visitor.
- We use it on data **you operate and own**, or data that is plainly public and
  factual.
- We never use it to reach behind a login, and we never collect private personal
  data.

A matching TLS fingerprint simply lets a legitimate, well-behaved client receive
the same public page a browser receives, instead of being silently dropped at the
handshake.
