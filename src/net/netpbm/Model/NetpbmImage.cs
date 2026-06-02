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

    /// <summary>
    /// Flip the image horizontally (mirror left-right) in place.
    /// R87 Train J: simple transform API.
    /// </summary>
    public void FlipHorizontal()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int row = 0; row < Height; row++)
            {
                for (int left = 0, right = Width - 1; left < right; left++, right--)
                {
                    int li = row * Width + left;
                    int ri = row * Width + right;
                    (RedChannel![li], RedChannel[ri]) = (RedChannel[ri], RedChannel[li]);
                    (GreenChannel![li], GreenChannel[ri]) = (GreenChannel[ri], GreenChannel[li]);
                    (BlueChannel![li], BlueChannel[ri]) = (BlueChannel[ri], BlueChannel[li]);
                }
            }
        }
        else
        {
            for (int row = 0; row < Height; row++)
            {
                for (int left = 0, right = Width - 1; left < right; left++, right--)
                {
                    int li = row * Width + left;
                    int ri = row * Width + right;
                    (Pixels[li], Pixels[ri]) = (Pixels[ri], Pixels[li]);
                }
            }
        }
    }

    /// <summary>
    /// Flip the image vertically (mirror top-bottom) in place.
    /// R88 Train J: vertical transform API.
    /// </summary>
    public void FlipVertical()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int top = 0, bot = Height - 1; top < bot; top++, bot--)
            {
                for (int col = 0; col < Width; col++)
                {
                    int ti = top * Width + col;
                    int bi = bot * Width + col;
                    (RedChannel![ti], RedChannel[bi]) = (RedChannel[bi], RedChannel[ti]);
                    (GreenChannel![ti], GreenChannel[bi]) = (GreenChannel[bi], GreenChannel[ti]);
                    (BlueChannel![ti], BlueChannel[bi]) = (BlueChannel[bi], BlueChannel[ti]);
                }
            }
        }
        else
        {
            for (int top = 0, bot = Height - 1; top < bot; top++, bot--)
            {
                for (int col = 0; col < Width; col++)
                {
                    int ti = top * Width + col;
                    int bi = bot * Width + col;
                    (Pixels[ti], Pixels[bi]) = (Pixels[bi], Pixels[ti]);
                }
            }
        }
    }

    /// <summary>
    /// Invert all pixel values in place.
    /// PBM: 0↔1. PGM: v → MaxValue - v. PPM: each channel inverted.
    /// R88 Train J: invert transform API.
    /// </summary>
    public void Invert()
    {
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            byte max = (byte)MaxValue;
            int len = Width * Height;
            for (int i = 0; i < len; i++)
            {
                RedChannel![i] = (byte)(max - RedChannel[i]);
                GreenChannel![i] = (byte)(max - GreenChannel[i]);
                BlueChannel![i] = (byte)(max - BlueChannel[i]);
            }
        }
        else if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            for (int i = 0; i < Pixels.Length; i++)
                Pixels[i] = (byte)(1 - Pixels[i]);
        }
        else
        {
            byte max = (byte)MaxValue;
            for (int i = 0; i < Pixels.Length; i++)
                Pixels[i] = (byte)(max - Pixels[i]);
        }
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

    /// <summary>
    /// Compute per-channel pixel statistics for PPM.
    /// Returns (R, G, B) where each is (Mean, Min, Max).
    /// R89 Train H: PPM statistics API.
    /// </summary>
    public ((double Mean, int Min, int Max) R, (double Mean, int Min, int Max) G, (double Mean, int Min, int Max) B) GetChannelStats()
    {
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException("Use GetStats for PBM/PGM.");
        int len = Width * Height;
        if (len == 0)
            return ((0, 0, 0), (0, 0, 0), (0, 0, 0));

        static (double Mean, int Min, int Max) ComputeStats(byte[] ch, int count)
        {
            long sum = 0;
            int min = ch[0], max = ch[0];
            for (int i = 0; i < count; i++)
            {
                sum += ch[i];
                if (ch[i] < min) min = ch[i];
                if (ch[i] > max) max = ch[i];
            }
            return ((double)sum / count, min, max);
        }

        return (
            ComputeStats(RedChannel!, len),
            ComputeStats(GreenChannel!, len),
            ComputeStats(BlueChannel!, len)
        );
    }

    /// <summary>
    /// Rotate the image 90° clockwise. Returns a NEW image (dimensions swap).
    /// R89 Train H: rotation transform.
    /// </summary>
    public NetpbmImage Rotate90Cw()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Height,
            Height = Width,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int newW = result.Width;
        int newH = result.Height;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int srcIdx = r * Width + c;
                    int dstRow = c;
                    int dstCol = Height - 1 - r;
                    int dstIdx = dstRow * newW + dstCol;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * newH];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int dstRow = c;
                    int dstCol = Height - 1 - r;
                    result.Pixels[dstRow * newW + dstCol] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Extract a rectangular sub-region. Returns a NEW image.
    /// R89 Train H: crop API.
    /// </summary>
    public NetpbmImage Crop(int top, int left, int cropHeight, int cropWidth)
    {
        if (top < 0 || left < 0 || cropHeight <= 0 || cropWidth <= 0)
            throw new ArgumentOutOfRangeException("Crop dimensions must be positive.");
        if (top + cropHeight > Height || left + cropWidth > Width)
            throw new ArgumentOutOfRangeException("Crop region exceeds image bounds.");

        var result = new NetpbmImage
        {
            Format = Format,
            Width = cropWidth,
            Height = cropHeight,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = cropWidth * cropHeight;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < cropHeight; r++)
            {
                int srcBase = (top + r) * Width + left;
                int dstBase = r * cropWidth;
                Array.Copy(RedChannel!, srcBase, result.RedChannel, dstBase, cropWidth);
                Array.Copy(GreenChannel!, srcBase, result.GreenChannel, dstBase, cropWidth);
                Array.Copy(BlueChannel!, srcBase, result.BlueChannel, dstBase, cropWidth);
            }
        }
        else
        {
            result.Pixels = new byte[cropWidth * cropHeight];
            for (int r = 0; r < cropHeight; r++)
            {
                Array.Copy(Pixels, (top + r) * Width + left, result.Pixels, r * cropWidth, cropWidth);
            }
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Region operations
    // -------------------------------------------------------------------------

    /// <summary>
    /// Fill a rectangular region with a uniform value (PBM/PGM) or color (PPM).
    /// For PBM, value must be 0 or 1. For PPM, all three channel values are used.
    /// R92 Train N: region fill API for image editing workflows.
    /// </summary>
    /// <param name="top">Top row (inclusive).</param>
    /// <param name="left">Left column (inclusive).</param>
    /// <param name="regionHeight">Number of rows to fill.</param>
    /// <param name="regionWidth">Number of columns to fill.</param>
    /// <param name="value">Fill value for PBM/PGM (ignored for PPM).</param>
    /// <param name="r">Red channel fill value (PPM only).</param>
    /// <param name="g">Green channel fill value (PPM only).</param>
    /// <param name="b">Blue channel fill value (PPM only).</param>
    public void FillRegion(int top, int left, int regionHeight, int regionWidth,
        byte value = 0, byte r = 0, byte g = 0, byte b = 0)
    {
        if (top < 0 || left < 0 || regionHeight <= 0 || regionWidth <= 0)
            throw new ArgumentOutOfRangeException("Region dimensions must be positive.");
        if (top + regionHeight > Height || left + regionWidth > Width)
            throw new ArgumentOutOfRangeException("Fill region exceeds image bounds.");

        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            if (value != 0 && value != 1)
                throw new ArgumentOutOfRangeException(nameof(value), "PBM pixels must be 0 or 1.");
        }

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int row = top; row < top + regionHeight; row++)
            {
                int rowBase = row * Width + left;
                for (int col = 0; col < regionWidth; col++)
                {
                    RedChannel![rowBase + col] = r;
                    GreenChannel![rowBase + col] = g;
                    BlueChannel![rowBase + col] = b;
                }
            }
        }
        else
        {
            for (int row = top; row < top + regionHeight; row++)
            {
                int rowBase = row * Width + left;
                for (int col = 0; col < regionWidth; col++)
                    Pixels[rowBase + col] = value;
            }
        }
    }

    /// <summary>
    /// Copy a rectangular region from <paramref name="source"/> into this image at
    /// (<paramref name="destTop"/>, <paramref name="destLeft"/>).
    /// Both images must have the same format. Region dimensions are clamped to the
    /// smaller of source and destination available bounds.
    /// R93 Train M: region copy for image compositing.
    /// </summary>
    /// <param name="source">Source image to copy from.</param>
    /// <param name="srcTop">Top row of the source region (zero-based).</param>
    /// <param name="srcLeft">Left column of the source region (zero-based).</param>
    /// <param name="regionHeight">Number of rows to copy.</param>
    /// <param name="regionWidth">Number of columns to copy.</param>
    /// <param name="destTop">Top row in this image to paste to (zero-based).</param>
    /// <param name="destLeft">Left column in this image to paste to (zero-based).</param>
    public void CopyRegion(NetpbmImage source, int srcTop, int srcLeft,
        int regionHeight, int regionWidth, int destTop, int destLeft)
    {
        if (source == null) throw new ArgumentNullException(nameof(source));
        if (source.Format != Format)
            throw new ArgumentException("Source and destination formats must match.", nameof(source));
        if (srcTop < 0 || srcLeft < 0 || regionHeight <= 0 || regionWidth <= 0 || destTop < 0 || destLeft < 0)
            throw new ArgumentOutOfRangeException("Region dimensions must be positive and coordinates non-negative.");

        // Clamp to available bounds
        int availSrcH = source.Height - srcTop;
        int availSrcW = source.Width - srcLeft;
        int availDstH = Height - destTop;
        int availDstW = Width - destLeft;
        int copyH = Math.Min(regionHeight, Math.Min(availSrcH, availDstH));
        int copyW = Math.Min(regionWidth, Math.Min(availSrcW, availDstW));

        if (copyH <= 0 || copyW <= 0) return; // Nothing to copy after clamping

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int row = 0; row < copyH; row++)
            {
                int srcRowBase = (srcTop + row) * source.Width + srcLeft;
                int dstRowBase = (destTop + row) * Width + destLeft;
                for (int col = 0; col < copyW; col++)
                {
                    RedChannel![dstRowBase + col] = source.RedChannel![srcRowBase + col];
                    GreenChannel![dstRowBase + col] = source.GreenChannel![srcRowBase + col];
                    BlueChannel![dstRowBase + col] = source.BlueChannel![srcRowBase + col];
                }
            }
        }
        else
        {
            for (int row = 0; row < copyH; row++)
            {
                int srcRowBase = (srcTop + row) * source.Width + srcLeft;
                int dstRowBase = (destTop + row) * Width + destLeft;
                for (int col = 0; col < copyW; col++)
                    Pixels[dstRowBase + col] = source.Pixels[srcRowBase + col];
            }
        }
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
