# Security policy

Treat every tensor file as untrusted. The default limits cap total input,
header size, and tensor count. Increase limits only for trusted workloads.
Parsing never imports tensor frameworks and never executes serialized code.

Report suspected vulnerabilities privately to the repository maintainers.
