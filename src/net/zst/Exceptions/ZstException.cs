// FormatFactory.Zst -- Exception hierarchy for Zstandard (.zst) file processing.
// Gate 11 status: commercial_readiness_in_progress (NOT approved)

namespace FormatFactory.Zst.Exceptions;

/// <summary>Base exception for all ZST processing errors.</summary>
public class ZstException : Exception
{
    /// <inheritdoc/>
    public ZstException(string message) : base(message) { }
    /// <inheritdoc/>
    public ZstException(string message, Exception inner) : base(message, inner) { }
}

/// <summary>Raised when the file does not contain a valid Zstandard magic sequence.</summary>
public class ZstInvalidMagicException : ZstException
{
    /// <inheritdoc/>
    public ZstInvalidMagicException(string message) : base(message) { }
}

/// <summary>Raised when a file exceeds the configured size guard.</summary>
public class ZstFileSizeException : ZstException
{
    /// <inheritdoc/>
    public ZstFileSizeException(string message) : base(message) { }
}

/// <summary>Raised when a file does not exist.</summary>
public class ZstFileNotFoundException : ZstException
{
    /// <inheritdoc/>
    public ZstFileNotFoundException(string message) : base(message) { }
}
