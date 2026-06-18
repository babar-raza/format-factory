// FormatFactory.Fods -- office:document error hierarchy
// Separated from FodsDocument.cs per TC-NET-001 (QName-based split).

namespace FormatFactory.Fods;

/// <summary>
/// Thrown by <see cref="FodsDocument.Load"/> when the file cannot be parsed or loaded safely.
/// </summary>
public sealed class FodsDocumentException : Exception
{
    public FodsDocumentException(string message) : base(message) { }
    public FodsDocumentException(string message, Exception inner) : base(message, inner) { }
}
