// FormatFactory.Ndjson — Custom Exception
// commercial_product_ready: false

namespace FormatFactory.Ndjson;

/// <summary>
/// Thrown when NDJSON parsing or writing fails.
/// </summary>
public sealed class NdjsonException : Exception
{
    public NdjsonException(string message) : base(message) { }
    public NdjsonException(string message, Exception inner) : base(message, inner) { }
}
