# R65 Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Delivery package protocol new and untested | HIGH | Synthetic tests + extraction validation |
| Sidecar SHA drift during two-pass cycle | HIGH | Sidecar is authoritative; final-verdict records approximate SHA |
| Invariant checker dict-format regression | MEDIUM | Regression test added |
| DIF/PPM Windows path quirk | MEDIUM | Use long nonexistent paths |
| AI gateway unavailable | LOW | Fixture fallback with AI_NOT_LIVE |
| Package rebuild from R65 HEAD | LOW | Same build script as R64 |
