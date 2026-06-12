// FormatFactory.Tsv — Custom exception type
// commercial_product_ready: false

namespace FormatFactory.Tsv;

/// <summary>Thrown by TSV reader/writer/document operations on invalid input or I/O errors.</summary>
public sealed class TsvException : Exception
{
    public TsvException(string message) : base(message) { }
    public TsvException(string message, Exception inner) : base(message, inner) { }
}
