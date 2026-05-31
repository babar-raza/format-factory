// FormatFactory.Netpbm -- Exception types
// commercial_product_ready: false

using System;

namespace FormatFactory.Netpbm;

public class NetpbmException : Exception
{
    public NetpbmException(string message) : base(message) { }
    public NetpbmException(string message, Exception inner) : base(message, inner) { }
}

public class NetpbmFormatException : NetpbmException
{
    public NetpbmFormatException(string message) : base(message) { }
}

public class NetpbmSizeException : NetpbmException
{
    public NetpbmSizeException(string message) : base(message) { }
}
