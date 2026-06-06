// FormatFactory.Netpbm -- Exception types
// Gate 11 approved by Babar Raza 2026-06-05.

using System;

namespace FormatFactory.Netpbm;

/// <summary>Base exception for Netpbm parsing and writing errors.</summary>
public class NetpbmException : Exception
{
    /// <summary>Initializes a new instance with a descriptive message.</summary>
    public NetpbmException(string message) : base(message) { }
    /// <summary>Initializes a new instance with a message and inner exception.</summary>
    public NetpbmException(string message, Exception inner) : base(message, inner) { }
}

/// <summary>Exception thrown when the Netpbm file format is invalid or unrecognized.</summary>
public class NetpbmFormatException : NetpbmException
{
    /// <summary>Initializes a new instance with a descriptive message.</summary>
    public NetpbmFormatException(string message) : base(message) { }
}

/// <summary>Exception thrown when image dimensions or pixel count exceed the configured safety limits.</summary>
public class NetpbmSizeException : NetpbmException
{
    /// <summary>Initializes a new instance with a descriptive message.</summary>
    public NetpbmSizeException(string message) : base(message) { }
}
