// FormatFactory.Netpbm -- Commercial .NET Netpbm Image Model
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: NOT_STARTED (R85 first slice — POC_TARGET_CONFIRMED)
// Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
//
// commercial_product_ready: false
// Do NOT package or publish.

using System;
using System.Collections.Generic;

namespace FormatFactory.Netpbm;

/// <summary>
/// Editable image model for Netpbm family (PBM/PGM/PPM).
///
/// PBM (P1/P4): 1-bit bitmap. Pixels = 0 (white) or 1 (black).
/// PGM (P2/P5): 8-bit grayscale. Pixels = 0..MaxValue.
/// PPM (P3/P6): 24-bit color. Pixels = (R,G,B) each 0..MaxValue.
///
/// This model uses a unified pixel representation:
///   - PBM: each pixel is a single byte (0 or 1)
///   - PGM: each pixel is a single byte (0..MaxValue)
///   - PPM: each pixel is 3 bytes (R, G, B)
///
/// Stored as flat arrays for efficiency:
///   - PBM/PGM: Pixels[row * Width + col] = pixel value
///   - PPM:     Pixels[row * Width + col] = R, then G channel, then B channel (separate arrays)
///
/// Spec: https://netpbm.sourceforge.net/doc/pbm.html (public domain)
/// </summary>
public sealed class NetpbmImage
{
    /// <summary>Netpbm format variant.</summary>
    public NetpbmFormat Format { get; set; }

    /// <summary>Image width in pixels.</summary>
    public int Width { get; set; }

    /// <summary>Image height in pixels.</summary>
    public int Height { get; set; }

    /// <summary>
    /// Maximum pixel value. For PBM: always 1. For PGM/PPM: typically 255.
    /// </summary>
    public int MaxValue { get; set; } = 255;

    /// <summary>
    /// Flat pixel array. For PBM/PGM: one byte per pixel.
    /// For PPM: use RedChannel/GreenChannel/BlueChannel properties.
    /// </summary>
    public byte[] Pixels { get; set; } = Array.Empty<byte>();

    // For PPM only
    public byte[]? RedChannel { get; set; }
    public byte[]? GreenChannel { get; set; }
    public byte[]? BlueChannel { get; set; }

    /// <summary>Comments from the original file header.</summary>
    public List<string> Comments { get; } = new List<string>();

    /// <summary>Source file path (if loaded from disk).</summary>
    public string? SourcePath { get; set; }

    // -------------------------------------------------------------------------
    // Pixel accessors
    // -------------------------------------------------------------------------

    /// <summary>
    /// Get a pixel value at (row, col) for PBM or PGM.
    /// For PPM, use GetPixelColor.
    /// </summary>
    public byte GetPixel(int row, int col)
    {
        ValidateCoordinates(row, col);
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetPixelColor for PPM images.");
        return Pixels[row * Width + col];
    }

    /// <summary>
    /// Set a pixel value at (row, col) for PBM or PGM.
    /// For PPM, use SetPixelColor.
    /// </summary>
    public void SetPixel(int row, int col, byte value)
    {
        ValidateCoordinates(row, col);
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use SetPixelColor for PPM images.");
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            if (value != 0 && value != 1)
                throw new ArgumentOutOfRangeException(nameof(value), "PBM pixels must be 0 or 1.");
        }
        Pixels[row * Width + col] = value;
    }

    /// <summary>
    /// Get (R, G, B) at (row, col) for PPM.
    /// </summary>
    public (byte R, byte G, byte B) GetPixelColor(int row, int col)
    {
        ValidateCoordinates(row, col);
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetPixel for PBM/PGM images.");
        int idx = row * Width + col;
        return (RedChannel![idx], GreenChannel![idx], BlueChannel![idx]);
    }

    /// <summary>
    /// Set (R, G, B) at (row, col) for PPM.
    /// </summary>
    public void SetPixelColor(int row, int col, byte r, byte g, byte b)
    {
        ValidateCoordinates(row, col);
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use SetPixel for PBM/PGM images.");
        int idx = row * Width + col;
        RedChannel![idx] = r;
        GreenChannel![idx] = g;
        BlueChannel![idx] = b;
    }

    // -------------------------------------------------------------------------
    // Image statistics
    // -------------------------------------------------------------------------

    /// <summary>Compute simple pixel statistics for PBM/PGM.</summary>
    public (double Mean, int Min, int Max) GetStats()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetChannelStats for PPM.");
        if (Pixels.Length == 0)
            return (0, 0, 0);
        long sum = 0;
        int min = Pixels[0], max = Pixels[0];
        foreach (var p in Pixels)
        {
            sum += p;
            if (p < min) min = p;
            if (p > max) max = p;
        }
        return ((double)sum / Pixels.Length, min, max);
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private void ValidateCoordinates(int row, int col)
    {
        if (row < 0 || row >= Height)
            throw new ArgumentOutOfRangeException(nameof(row));
        if (col < 0 || col >= Width)
            throw new ArgumentOutOfRangeException(nameof(col));
    }
}

/// <summary>Netpbm format variants.</summary>
public enum NetpbmFormat
{
    PBM_P1,  // ASCII bitmap
    PBM_P4,  // Binary bitmap
    PGM_P2,  // ASCII grayscale
    PGM_P5,  // Binary grayscale
    PPM_P3,  // ASCII color
    PPM_P6   // Binary color
}
