// FormatFactory.Fodt -- Exception hierarchy for FODT document format operations.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

namespace FormatFactory.Fodt;

/// <summary>
/// Thrown by <see cref="FodtDocument.Load"/> when the file cannot be parsed or loaded safely.
/// </summary>
public sealed class FodtDocumentException : Exception
{
    public FodtDocumentException(string message) : base(message) { }
    public FodtDocumentException(string message, Exception inner) : base(message, inner) { }
}
