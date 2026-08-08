# Security policy

Notebook files are untrusted JSON and can contain active MIME output. Loading,
probing, validating, and writing never execute notebook code or render active
content. Default limits cap input size and structural depth.

A separate, explicitly opt-in adapter, `execute_notebook()`, exists for
callers who want to actually run a notebook's code cells; it is never called
by load/probe/validate/diff/save. It runs code in one isolated OS
subprocess (not the caller's own process), refuses a notebook declaring a
non-Python kernel rather than silently running it as Python, and bounds the
whole run with a caller-configurable wall-clock timeout. Callers who never
invoke `execute_notebook()` are unaffected by its existence; callers who do
invoke it are running untrusted code by their own explicit choice, with the
same trust implications as running any other untrusted script.

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
