// FormatFactory.Netpbm -- NetpbmFormat enum (extracted from NetpbmImage.cs via TC-NET-H3).

namespace FormatFactory.Netpbm;

/// <summary>Netpbm format variants.</summary>
public enum NetpbmFormat
{
    /// <summary>PBM ASCII bitmap (magic P1).</summary>
    PBM_P1,
    /// <summary>PBM binary bitmap (magic P4).</summary>
    PBM_P4,
    /// <summary>PGM ASCII grayscale (magic P2).</summary>
    PGM_P2,
    /// <summary>PGM binary grayscale (magic P5).</summary>
    PGM_P5,
    /// <summary>PPM ASCII color (magic P3).</summary>
    PPM_P3,
    /// <summary>PPM binary color (magic P6).</summary>
    PPM_P6
}
