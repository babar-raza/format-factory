# Security policy

Notebook files are untrusted JSON and can contain active MIME output. Loading,
probing, validating, and writing never execute notebook code or render active
content. Default limits cap input size and structural depth.

`sanitize()` provides explicit lossless-report, remove, quarantine, and
preserve-but-mark modes for Markdown, active MIME payloads, and external
references. The implementation never fetches references or renders payloads.
Remove and quarantine modes treat the whole classified renderable payload as
unsafe; this avoids presenting a partial markup rewrite as a complete browser
security boundary. Quarantined payloads remain untrusted data and must not be
rendered directly by consumers.

Notebook trust uses a caller-supplied secret, a strong HMAC algorithm, and an
external signature store. Parsing and validation never sign content, and
verification never writes `trusted` flags into cells. A valid notebook is not
therefore a trusted notebook. The built-in memory store is process-local;
applications needing durable trust must inject a protected persistent store
and manage secret rotation outside notebook files.

Report suspected vulnerabilities privately to the repository maintainers.
