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
    PPM_P6,
    /// <summary>Alias for PGM_P2 (grayscale ASCII).</summary>
    Pgm = PGM_P2,
    /// <summary>Alias for PBM_P1 (bitmap ASCII).</summary>
    Pbm = PBM_P1,
    /// <summary>Alias for PPM_P3 (color ASCII).</summary>
    Ppm = PPM_P3
}
