# Security policy

Treat every XLIFF document as untrusted input. The reader rejects DTD/entity
declarations, applies byte/node/depth limits, does not fetch schemas or external
resources, and keeps skeleton/resource references passive.

Report suspected parser bypasses, resource-exhaustion issues, extension
namespace corruption, or inline-code data loss through the repository security
channel.
