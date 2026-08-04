# Security

Report vulnerabilities via the repository's security policy.

OpenRaster archives are untrusted input. This package validates the ZIP member
directory before any payload is decompressed: member names that could escape an
extraction root are refused, duplicate names are refused rather than resolved,
and declared sizes and compression ratios are checked against caller-supplied
`ResourceLimits` from `format_factory.core`.

Parsing never executes archive content and never resolves network resources.
