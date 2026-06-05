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
    /// Rotate the image 270° clockwise (90° counter-clockwise). Returns a NEW image (dimensions swap).
    /// Equivalent to three Rotate90Cw() calls but done in a single pass for efficiency.
    /// R100 Train D: counter-clockwise rotation.
    /// </summary>
    public NetpbmImage Rotate270Cw()
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
                    int dstRow = Width - 1 - c;
                    int dstCol = r;
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
                    int dstRow = Width - 1 - c;
                    int dstCol = r;
                    result.Pixels[dstRow * newW + dstCol] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Rotate the image 180°. Returns a NEW image (dimensions unchanged).
    /// Equivalent to reversing pixel order. More efficient than two Rotate90Cw() calls.
    /// R101 Train D: transform completion (Rotate90/270 exist, Rotate180 was missing).
    /// </summary>
    public NetpbmImage Rotate180()
    {
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        int len = Width * Height;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int i = 0; i < len; i++)
            {
                int mirrorIdx = len - 1 - i;
                result.RedChannel[i] = RedChannel![mirrorIdx];
                result.GreenChannel[i] = GreenChannel![mirrorIdx];
                result.BlueChannel[i] = BlueChannel![mirrorIdx];
            }
        }
        else
        {
            result.Pixels = new byte[len];
            for (int i = 0; i < len; i++)
            {
                result.Pixels[i] = Pixels[len - 1 - i];
            }
        }

        return result;
    }

    /// <summary>
    /// Adjust brightness by adding a delta to all pixel values, clamped to [0, MaxValue].
    /// For PPM, applies to all three channels. For PBM, this is a no-op (returns clone).
    /// Returns a NEW image.
    /// R104 Wave 1: pixel intensity adjustment for image processing pipeline.
    /// </summary>
    public NetpbmImage AdjustBrightness(int delta)
    {
        var result = Clone();
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return result;

        int max = MaxValue;
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp(result.RedChannel[i] + delta, 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp(result.GreenChannel[i] + delta, 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp(result.BlueChannel[i] + delta, 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp(result.Pixels[i] + delta, 0, max);
        }
        return result;
    }

    /// <summary>
    /// Merge another image horizontally (place <paramref name="other"/> to the right).
    /// Both images must have the same Height and Format. Returns a NEW image.
    /// R104 Wave 1: image composition for tiling/panorama workflows.
    /// </summary>
    public NetpbmImage MergeHorizontal(NetpbmImage other)
    {
        if (other is null) throw new ArgumentNullException(nameof(other));
        if (other.Height != Height)
            throw new ArgumentException($"Height mismatch: {Height} vs {other.Height}.", nameof(other));
        if (other.Format != Format)
            throw new ArgumentException($"Format mismatch: {Format} vs {other.Format}.", nameof(other));

        int newW = Width + other.Width;
        var result = new NetpbmImage
        {
            Format = Format,
            Width = newW,
            Height = Height,
            MaxValue = Math.Max(MaxValue, other.MaxValue),
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = newW * Height;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                {
                    int dstIdx = r * newW + c;
                    int srcIdx = r * Width + c;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
                for (int c = 0; c < other.Width; c++)
                {
                    int dstIdx = r * newW + Width + c;
                    int srcIdx = r * other.Width + c;
                    result.RedChannel[dstIdx] = other.RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = other.GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = other.BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newW * Height];
            for (int r = 0; r < Height; r++)
            {
                for (int c = 0; c < Width; c++)
                    result.Pixels[r * newW + c] = Pixels[r * Width + c];
                for (int c = 0; c < other.Width; c++)
                    result.Pixels[r * newW + Width + c] = other.Pixels[r * other.Width + c];
            }
        }
        return result;
    }

    /// <summary>
    /// Merge another image vertically (place <paramref name="other"/> below).
    /// Both images must have the same Width and Format. Returns a NEW image.
    /// R105 Wave 2: image composition for vertical tiling/stacking workflows.
    /// </summary>
    public NetpbmImage MergeVertical(NetpbmImage other)
    {
        if (other is null) throw new ArgumentNullException(nameof(other));
        if (other.Width != Width)
            throw new ArgumentException($"Width mismatch: {Width} vs {other.Width}.", nameof(other));
        if (other.Format != Format)
            throw new ArgumentException($"Format mismatch: {Format} vs {other.Format}.", nameof(other));

        int newH = Height + other.Height;
        var result = new NetpbmImage
        {
            Format = Format,
            Width = Width,
            Height = newH,
            MaxValue = Math.Max(MaxValue, other.MaxValue),
            SourcePath = SourcePath
        };
        result.Comments.AddRange(Comments);

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            int len = Width * newH;
            result.RedChannel = new byte[len];
            result.GreenChannel = new byte[len];
            result.BlueChannel = new byte[len];
            result.Pixels = Array.Empty<byte>();

            int topLen = Width * Height;
            Array.Copy(RedChannel!, 0, result.RedChannel, 0, topLen);
            Array.Copy(GreenChannel!, 0, result.GreenChannel, 0, topLen);
            Array.Copy(BlueChannel!, 0, result.BlueChannel, 0, topLen);
            int bottomLen = Width * other.Height;
            Array.Copy(other.RedChannel!, 0, result.RedChannel, topLen, bottomLen);
            Array.Copy(other.GreenChannel!, 0, result.GreenChannel, topLen, bottomLen);
            Array.Copy(other.BlueChannel!, 0, result.BlueChannel, topLen, bottomLen);
        }
        else
        {
            int topLen = Width * Height;
            int bottomLen = Width * other.Height;
            result.Pixels = new byte[topLen + bottomLen];
            Array.Copy(Pixels, 0, result.Pixels, 0, topLen);
            Array.Copy(other.Pixels, 0, result.Pixels, topLen, bottomLen);
        }
        return result;
    }

    /// <summary>
    /// Adjust contrast by scaling pixel values around the midpoint (MaxValue/2).
    /// A factor &gt; 1.0 increases contrast, &lt; 1.0 decreases it. 1.0 is no-op.
    /// For PBM, this is a no-op (returns clone). Returns a NEW image.
    /// R105 Wave 2: contrast adjustment for image processing pipeline.
    /// </summary>
    public NetpbmImage AdjustContrast(double factor)
    {
        if (factor < 0)
            throw new ArgumentOutOfRangeException(nameof(factor), "Contrast factor must not be negative.");

        var result = Clone();
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return result;

        double mid = MaxValue / 2.0;
        int max = MaxValue;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp((int)Math.Round(mid + (result.RedChannel[i] - mid) * factor), 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp((int)Math.Round(mid + (result.GreenChannel[i] - mid) * factor), 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp((int)Math.Round(mid + (result.BlueChannel[i] - mid) * factor), 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp((int)Math.Round(mid + (result.Pixels[i] - mid) * factor), 0, max);
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

    /// <summary>
    /// Create a new image resized to the specified dimensions using nearest-neighbor interpolation.
    /// Both dimensions must be positive. The format and MaxValue are preserved.
    /// R94 Train O: basic resize for image processing pipeline.
    /// </summary>
    public NetpbmImage Resize(int newWidth, int newHeight)
    {
        if (newWidth <= 0) throw new ArgumentOutOfRangeException(nameof(newWidth), "Width must be positive.");
        if (newHeight <= 0) throw new ArgumentOutOfRangeException(nameof(newHeight), "Height must be positive.");

        var result = new NetpbmImage
        {
            Format = Format,
            Width = newWidth,
            Height = newHeight,
            MaxValue = MaxValue,
        };

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            result.RedChannel = new byte[newWidth * newHeight];
            result.GreenChannel = new byte[newWidth * newHeight];
            result.BlueChannel = new byte[newWidth * newHeight];
            for (int row = 0; row < newHeight; row++)
            {
                int srcRow = (int)((long)row * Height / newHeight);
                if (srcRow >= Height) srcRow = Height - 1;
                for (int col = 0; col < newWidth; col++)
                {
                    int srcCol = (int)((long)col * Width / newWidth);
                    if (srcCol >= Width) srcCol = Width - 1;
                    int srcIdx = srcRow * Width + srcCol;
                    int dstIdx = row * newWidth + col;
                    result.RedChannel[dstIdx] = RedChannel![srcIdx];
                    result.GreenChannel[dstIdx] = GreenChannel![srcIdx];
                    result.BlueChannel[dstIdx] = BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            result.Pixels = new byte[newWidth * newHeight];
            for (int row = 0; row < newHeight; row++)
            {
                int srcRow = (int)((long)row * Height / newHeight);
                if (srcRow >= Height) srcRow = Height - 1;
                for (int col = 0; col < newWidth; col++)
                {
                    int srcCol = (int)((long)col * Width / newWidth);
                    if (srcCol >= Width) srcCol = Width - 1;
                    result.Pixels[row * newWidth + col] = Pixels[srcRow * Width + srcCol];
                }
            }
        }
        return result;
    }

    /// <summary>
    /// Convert a PPM (color) image to a PGM (grayscale) image using standard luminance weights.
    /// Formula: gray = 0.299*R + 0.587*G + 0.114*B (ITU-R BT.601).
    /// Throws InvalidOperationException if the image is not PPM format.
    /// R95 Train N: color-to-grayscale conversion for image pipeline.
    /// </summary>
    public NetpbmImage ToGrayscale()
    {
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException($"ToGrayscale requires PPM format, got {Format}.");

        if (RedChannel == null || GreenChannel == null || BlueChannel == null)
            throw new InvalidOperationException("PPM image has null color channels.");

        var result = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            Pixels = new byte[Width * Height],
        };

        for (int i = 0; i < Width * Height; i++)
        {
            int gray = (int)(0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i]);
            result.Pixels[i] = (byte)Math.Clamp(gray, 0, MaxValue);
        }

        return result;
    }

    /// <summary>
    /// Convert a PGM (grayscale) image to a PPM (color) image.
    /// Each gray value is replicated across R, G, B channels.
    /// Throws InvalidOperationException if the image is not PGM format.
    /// R99 Train D: grayscale-to-color conversion for dogfood export pipeline.
    /// </summary>
    public NetpbmImage ToColor()
    {
        if (Format != NetpbmFormat.PGM_P2 && Format != NetpbmFormat.PGM_P5)
            throw new InvalidOperationException($"ToColor requires PGM format, got {Format}.");

        int len = Width * Height;
        var result = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[len],
            GreenChannel = new byte[len],
            BlueChannel = new byte[len],
        };

        for (int i = 0; i < len; i++)
        {
            byte g = Pixels[i];
            result.RedChannel[i] = g;
            result.GreenChannel[i] = g;
            result.BlueChannel[i] = g;
        }

        return result;
    }

    /// <summary>
    /// Compute the average brightness of the image as a value in [0.0, 1.0].
    /// For PBM/PGM: mean pixel value / MaxValue.
    /// For PPM: mean luminance / MaxValue using ITU-R BT.601 weights.
    /// Returns 0.0 for empty images.
    /// R96 Train N: image brightness metric for analysis pipeline.
    /// </summary>
    public double GetBrightness()
    {
        int totalPixels = Width * Height;
        if (totalPixels == 0 || MaxValue == 0) return 0.0;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return 0.0;
            double sum = 0;
            for (int i = 0; i < totalPixels; i++)
            {
                sum += 0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i];
            }
            return sum / totalPixels / MaxValue;
        }
        else
        {
            long sum = 0;
            foreach (var p in Pixels)
                sum += p;
            return (double)sum / totalPixels / MaxValue;
        }
    }

    /// <summary>
    /// Extract a single color channel from a PPM image as a PGM grayscale image.
    /// Channel: 0 = Red, 1 = Green, 2 = Blue.
    /// Throws if the image is not PPM format or channel index is invalid.
    /// R103 Train C: channel separation for color analysis pipeline.
    /// </summary>
    /// <param name="channel">Channel index: 0=Red, 1=Green, 2=Blue.</param>
    public NetpbmImage ExtractChannel(int channel)
    {
        if (Format != NetpbmFormat.PPM_P3 && Format != NetpbmFormat.PPM_P6)
            throw new InvalidOperationException($"ExtractChannel requires PPM format, got {Format}.");
        if (channel < 0 || channel > 2)
            throw new ArgumentOutOfRangeException(nameof(channel), "Channel must be 0 (R), 1 (G), or 2 (B).");
        if (RedChannel == null || GreenChannel == null || BlueChannel == null)
            throw new InvalidOperationException("PPM image has null color channels.");

        int len = Width * Height;
        var source = channel switch
        {
            0 => RedChannel,
            1 => GreenChannel,
            2 => BlueChannel,
            _ => throw new ArgumentOutOfRangeException(nameof(channel))
        };

        var result = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            Pixels = new byte[len],
        };
        Array.Copy(source, result.Pixels, len);
        return result;
    }

    /// <summary>
    /// Save this image to a file in its current format.
    /// ASCII formats (P1/P2/P3) produce text files; binary (P4/P5/P6) produce raw bytes.
    /// R98 Train N: same-format save for edit persistence.
    /// </summary>
    /// <param name="path">Absolute or relative path to write.</param>
    public void SaveToFile(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("Path must not be null or empty.", nameof(path));
        NetpbmWriter.Write(this, path);
    }

    /// <summary>
    /// Create a deep copy of this image. All pixel data is duplicated.
    /// R97 Train N: image cloning for non-destructive editing pipeline.
    /// </summary>
    public NetpbmImage Clone()
    {
        var copy = new NetpbmImage
        {
            Format = Format,
            Width = Width,
            Height = Height,
            MaxValue = MaxValue,
            SourcePath = SourcePath,
        };
        copy.Comments.AddRange(Comments);

        if (Pixels != null)
            copy.Pixels = (byte[])Pixels.Clone();
        if (RedChannel != null)
            copy.RedChannel = (byte[])RedChannel.Clone();
        if (GreenChannel != null)
            copy.GreenChannel = (byte[])GreenChannel.Clone();
        if (BlueChannel != null)
            copy.BlueChannel = (byte[])BlueChannel.Clone();

        return copy;
    }

    /// <summary>
    /// Compute a histogram of pixel intensities.
    /// For PBM: returns int[2] (index 0 = white count, index 1 = black count).
    /// For PGM: returns int[MaxValue+1] with frequency of each gray level.
    /// For PPM: returns the luminance histogram int[MaxValue+1] using BT.601 weights.
    /// R101 Train C: pixel distribution analysis for image quality pipeline.
    /// </summary>
    public int[] GetHistogram()
    {
        int totalPixels = Width * Height;
        if (totalPixels == 0)
            return Array.Empty<int>();

        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
        {
            var hist = new int[2];
            foreach (var p in Pixels)
                hist[Math.Clamp((int)p, 0, 1)]++;
            return hist;
        }

        int bins = MaxValue + 1;
        var histogram = new int[bins];

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return histogram;
            for (int i = 0; i < totalPixels; i++)
            {
                int lum = (int)(0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i]);
                histogram[Math.Clamp(lum, 0, MaxValue)]++;
            }
        }
        else
        {
            foreach (var p in Pixels)
                histogram[Math.Clamp((int)p, 0, MaxValue)]++;
        }

        return histogram;
    }

    /// <summary>
    /// Convert an image to a 1-bit PBM bitmap by thresholding.
    /// For PGM: pixels &gt;= threshold become 1 (black), else 0 (white).
    /// For PPM: luminance (BT.601) is compared against the threshold.
    /// Throws if the image is already PBM format.
    /// R102 Train C: binarization for document scanning pipeline.
    /// </summary>
    /// <param name="threshold">Intensity threshold (0..MaxValue). Pixels &gt;= threshold become black (1).</param>
    public NetpbmImage Threshold(int threshold)
    {
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            throw new InvalidOperationException("Cannot threshold an already-binary PBM image.");

        if (threshold < 0 || threshold > MaxValue)
            throw new ArgumentOutOfRangeException(nameof(threshold),
                $"Threshold must be 0..{MaxValue}, got {threshold}.");

        int totalPixels = Width * Height;
        var result = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = Width,
            Height = Height,
            MaxValue = 1,
            Pixels = new byte[totalPixels],
        };

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            if (RedChannel == null || GreenChannel == null || BlueChannel == null)
                return result;
            for (int i = 0; i < totalPixels; i++)
            {
                int lum = (int)(0.299 * RedChannel[i] + 0.587 * GreenChannel[i] + 0.114 * BlueChannel[i]);
                result.Pixels[i] = lum >= threshold ? (byte)1 : (byte)0;
            }
        }
        else
        {
            for (int i = 0; i < totalPixels; i++)
                result.Pixels[i] = Pixels[i] >= threshold ? (byte)1 : (byte)0;
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Transpose / Overlay
    // -------------------------------------------------------------------------

    /// <summary>
    /// Transpose the image: swap rows and columns (flip along main diagonal).
    /// Width becomes Height and vice versa. Pixel at (r,c) moves to (c,r).
    /// R106 Wave 2: diagonal flip for image transformation.
    /// </summary>
    public NetpbmImage FlipDiagonal()
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

        int newW = Height;
        int newH = Width;

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
                    int dstIdx = c * newW + r;
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
                    result.Pixels[c * newW + r] = Pixels[r * Width + c];
                }
            }
        }

        return result;
    }

    /// <summary>
    /// Overlay another image on top of this image at the given offset.
    /// The overlay image must have the same Format. Pixels from the overlay
    /// replace pixels in this image within the overlap region.
    /// Does not modify the original — returns a new image.
    /// Throws if formats don't match or offset is negative.
    /// R106 Wave 2: image compositing for editing workflows.
    /// </summary>
    public NetpbmImage Overlay(NetpbmImage overlay, int topOffset, int leftOffset)
    {
        if (overlay.Format != Format)
            throw new InvalidOperationException("Overlay format must match base image format.");
        if (topOffset < 0 || leftOffset < 0)
            throw new ArgumentOutOfRangeException("Offsets must not be negative.");

        var result = Clone();

        int overlapTop = topOffset;
        int overlapLeft = leftOffset;
        int overlapBottom = Math.Min(Height, topOffset + overlay.Height);
        int overlapRight = Math.Min(Width, leftOffset + overlay.Width);

        if (overlapTop >= overlapBottom || overlapLeft >= overlapRight)
            return result; // No overlap

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            for (int r = overlapTop; r < overlapBottom; r++)
            {
                for (int c = overlapLeft; c < overlapRight; c++)
                {
                    int srcIdx = (r - topOffset) * overlay.Width + (c - leftOffset);
                    int dstIdx = r * Width + c;
                    result.RedChannel![dstIdx] = overlay.RedChannel![srcIdx];
                    result.GreenChannel![dstIdx] = overlay.GreenChannel![srcIdx];
                    result.BlueChannel![dstIdx] = overlay.BlueChannel![srcIdx];
                }
            }
        }
        else
        {
            for (int r = overlapTop; r < overlapBottom; r++)
            {
                for (int c = overlapLeft; c < overlapRight; c++)
                {
                    int srcIdx = (r - topOffset) * overlay.Width + (c - leftOffset);
                    int dstIdx = r * Width + c;
                    result.Pixels[dstIdx] = overlay.Pixels[srcIdx];
                }
            }
        }

        return result;
    }

    // -------------------------------------------------------------------------
    // Histogram Equalization / Format Conversion
    // -------------------------------------------------------------------------

    /// <summary>
    /// Perform histogram equalization on PGM images to improve contrast.
    /// Remaps pixel intensities so that the cumulative distribution is approximately uniform.
    /// For PPM: equalizes the luminance channel (converts to PGM first, equalizes, result is PGM).
    /// For PBM: returns unchanged (only 2 values).
    /// R107 Wave 2: image enhancement for processing pipeline depth.
    /// </summary>
    public NetpbmImage Equalize()
    {
        if (Format == NetpbmFormat.PBM_P1 || Format == NetpbmFormat.PBM_P4)
            return Clone();

        // For PPM, convert to grayscale first then equalize
        NetpbmImage source = this;
        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
            source = ToGrayscale();

        int totalPixels = source.Width * source.Height;
        if (totalPixels == 0) return source.Clone();

        // Build histogram
        var hist = new int[source.MaxValue + 1];
        foreach (var p in source.Pixels)
            hist[Math.Clamp((int)p, 0, source.MaxValue)]++;

        // Build CDF
        var cdf = new int[hist.Length];
        cdf[0] = hist[0];
        for (int i = 1; i < hist.Length; i++)
            cdf[i] = cdf[i - 1] + hist[i];

        // Find minimum non-zero CDF value
        int cdfMin = 0;
        for (int i = 0; i < cdf.Length; i++)
        {
            if (cdf[i] > 0) { cdfMin = cdf[i]; break; }
        }

        // Build lookup table
        var lut = new byte[hist.Length];
        int denom = totalPixels - cdfMin;
        if (denom <= 0) return source.Clone();
        for (int i = 0; i < lut.Length; i++)
        {
            lut[i] = (byte)Math.Clamp(
                (int)Math.Round((double)(cdf[i] - cdfMin) / denom * source.MaxValue),
                0, source.MaxValue);
        }

        var result = new NetpbmImage
        {
            Format = source.Format,
            Width = source.Width,
            Height = source.Height,
            MaxValue = source.MaxValue,
            Pixels = new byte[totalPixels],
        };

        for (int i = 0; i < totalPixels; i++)
            result.Pixels[i] = lut[Math.Clamp((int)source.Pixels[i], 0, source.MaxValue)];

        return result;
    }

    /// <summary>
    /// Convert between ASCII and binary variants of the same Netpbm type.
    /// P1↔P4 (PBM), P2↔P5 (PGM), P3↔P6 (PPM).
    /// Does not alter pixel data — only changes the Format field.
    /// Returns a new image; does not modify the original.
    /// R107 Wave 2: format conversion for save pipeline flexibility.
    /// </summary>
    public NetpbmImage ConvertFormat(NetpbmFormat targetFormat)
    {
        // Validate same type family
        bool samePbm = IsPbm(Format) && IsPbm(targetFormat);
        bool samePgm = IsPgm(Format) && IsPgm(targetFormat);
        bool samePpm = IsPpm(Format) && IsPpm(targetFormat);
        if (!samePbm && !samePgm && !samePpm)
            throw new InvalidOperationException(
                $"Cannot convert {Format} to {targetFormat}: must be same type family (PBM↔PBM, PGM↔PGM, PPM↔PPM).");

        var result = Clone();
        result.Format = targetFormat;
        return result;
    }

    /// <summary>
    /// Apply gamma correction to the image. Gamma &lt; 1 brightens, gamma &gt; 1 darkens.
    /// For PBM, returns a clone (no continuous values to correct).
    /// For PPM, applies to all three channels.
    /// Returns a NEW image; does not modify the original.
    /// R108 Lane E: gamma correction for image processing pipeline.
    /// </summary>
    public NetpbmImage ApplyGamma(double gamma)
    {
        if (gamma <= 0)
            throw new ArgumentOutOfRangeException(nameof(gamma), "Gamma must be positive.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.RedChannel[i] / (double)max, gamma)), 0, max);
                result.GreenChannel![i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.GreenChannel[i] / (double)max, gamma)), 0, max);
                result.BlueChannel![i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.BlueChannel[i] / (double)max, gamma)), 0, max);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = (byte)Math.Clamp(
                    (int)Math.Round(max * Math.Pow(result.Pixels[i] / (double)max, gamma)), 0, max);
        }
        return result;
    }

    /// <summary>
    /// Posterize the image by reducing pixel values to a fixed number of levels.
    /// Each channel value is quantized to the nearest of <paramref name="levels"/> evenly-spaced values.
    /// For PBM, returns a clone (already binary). For PPM, applies to all three channels.
    /// Returns a NEW image; does not modify the original.
    /// R109 Lane E: posterization for artistic/reduced-palette image processing.
    /// </summary>
    /// <param name="levels">Number of distinct output levels (must be >= 2).</param>
    public NetpbmImage Posterize(int levels)
    {
        if (levels < 2)
            throw new ArgumentOutOfRangeException(nameof(levels), "Levels must be at least 2.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                result.RedChannel[i] = Quantize(result.RedChannel[i], max, levels);
                result.GreenChannel![i] = Quantize(result.GreenChannel[i], max, levels);
                result.BlueChannel![i] = Quantize(result.BlueChannel[i], max, levels);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
                result.Pixels[i] = Quantize(result.Pixels[i], max, levels);
        }
        return result;
    }

    private static byte Quantize(byte value, int max, int levels)
    {
        double normalized = value / (double)max;
        int bucket = (int)Math.Floor(normalized * (levels - 1) + 0.5);
        bucket = Math.Clamp(bucket, 0, levels - 1);
        return (byte)Math.Clamp((int)Math.Round(bucket * max / (double)(levels - 1)), 0, max);
    }

    /// <summary>
    /// Create a solarized copy of this image. Pixels above the threshold are inverted.
    /// For PBM images, returns a clone (no solarization effect on 1-bit images).
    /// For PGM: pixels > threshold become (MaxValue - pixel).
    /// For PPM: each channel value > threshold becomes (MaxValue - value).
    /// R110 Wave 4: artistic image processing depth.
    /// </summary>
    public NetpbmImage Solarize(byte threshold)
    {
        var result = Clone();
        if (IsPbm(Format)) return result;

        int max = MaxValue;
        if (IsPpm(Format))
        {
            for (int i = 0; i < result.RedChannel!.Length; i++)
            {
                if (result.RedChannel[i] > threshold)
                    result.RedChannel[i] = (byte)(max - result.RedChannel[i]);
                if (result.GreenChannel![i] > threshold)
                    result.GreenChannel[i] = (byte)(max - result.GreenChannel[i]);
                if (result.BlueChannel![i] > threshold)
                    result.BlueChannel[i] = (byte)(max - result.BlueChannel[i]);
            }
        }
        else
        {
            for (int i = 0; i < result.Pixels.Length; i++)
            {
                if (result.Pixels[i] > threshold)
                    result.Pixels[i] = (byte)(max - result.Pixels[i]);
            }
        }
        return result;
    }

    /// <summary>
    /// Create a sepia-toned copy of this image. Only applies to PPM images.
    /// For PBM/PGM images, returns a clone (no sepia effect).
    /// Sepia formula: convert to luminance then apply warm tint (R*1.0, G*0.8, B*0.6).
    /// R110 Wave 4: color tone processing for image manipulation.
    /// </summary>
    public NetpbmImage Sepia()
    {
        var result = Clone();
        if (!IsPpm(Format)) return result;

        int max = MaxValue;
        for (int i = 0; i < result.RedChannel!.Length; i++)
        {
            // Compute luminance
            double lum = 0.299 * result.RedChannel[i] + 0.587 * result.GreenChannel![i] + 0.114 * result.BlueChannel![i];
            result.RedChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 1.0), 0, max);
            result.GreenChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 0.8), 0, max);
            result.BlueChannel[i] = (byte)Math.Clamp((int)Math.Round(lum * 0.6), 0, max);
        }
        return result;
    }

    /// <summary>
    /// Apply a 3x3 sharpening kernel to the image. Returns a new sharpened image.
    /// For PBM images, returns a clone (no sharpening on 1-bit images).
    /// Kernel: center=5, edges=-1 (unsharp mask style).
    /// R111 Wave 5: image processing depth for enhancement workflows.
    /// </summary>
    public NetpbmImage Sharpen()
    {
        var result = Clone();
        if (IsPbm(Format)) return result;

        int w = Width, h = Height, max = MaxValue;
        // Kernel: [0,-1,0; -1,5,-1; 0,-1,0]
        if (IsPpm(Format))
        {
            var srcR = (byte[])RedChannel!.Clone();
            var srcG = (byte[])GreenChannel!.Clone();
            var srcB = (byte[])BlueChannel!.Clone();
            for (int y = 1; y < h - 1; y++)
            for (int x = 1; x < w - 1; x++)
            {
                int idx = y * w + x;
                int rVal = 5 * srcR[idx] - srcR[(y-1)*w+x] - srcR[(y+1)*w+x] - srcR[y*w+x-1] - srcR[y*w+x+1];
                int gVal = 5 * srcG[idx] - srcG[(y-1)*w+x] - srcG[(y+1)*w+x] - srcG[y*w+x-1] - srcG[y*w+x+1];
                int bVal = 5 * srcB[idx] - srcB[(y-1)*w+x] - srcB[(y+1)*w+x] - srcB[y*w+x-1] - srcB[y*w+x+1];
                result.RedChannel![idx] = (byte)Math.Clamp(rVal, 0, max);
                result.GreenChannel![idx] = (byte)Math.Clamp(gVal, 0, max);
                result.BlueChannel![idx] = (byte)Math.Clamp(bVal, 0, max);
            }
        }
        else // PGM
        {
            var src = (byte[])Pixels.Clone();
            for (int y = 1; y < h - 1; y++)
            for (int x = 1; x < w - 1; x++)
            {
                int idx = y * w + x;
                int val = 5 * src[idx] - src[(y-1)*w+x] - src[(y+1)*w+x] - src[y*w+x-1] - src[y*w+x+1];
                result.Pixels[idx] = (byte)Math.Clamp(val, 0, max);
            }
        }
        return result;
    }

    /// <summary>
    /// Apply an NxN box blur to the image. Returns a new blurred image.
    /// For PBM images, returns a clone (no blur on 1-bit images).
    /// The radius parameter defines the half-size: kernel is (2*radius+1) x (2*radius+1).
    /// R111 Wave 5: image processing depth for smoothing workflows.
    /// </summary>
    public NetpbmImage BlurBox(int radius)
    {
        if (radius < 1)
            throw new ArgumentOutOfRangeException(nameof(radius), "Radius must be at least 1.");

        var result = Clone();
        if (IsPbm(Format)) return result;

        int w = Width, h = Height, max = MaxValue;
        int kernelSize = (2 * radius + 1) * (2 * radius + 1);

        if (IsPpm(Format))
        {
            for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int sumR = 0, sumG = 0, sumB = 0, count = 0;
                for (int dy = -radius; dy <= radius; dy++)
                for (int dx = -radius; dx <= radius; dx++)
                {
                    int ny = y + dy, nx = x + dx;
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w)
                    {
                        int ni = ny * w + nx;
                        sumR += RedChannel![ni];
                        sumG += GreenChannel![ni];
                        sumB += BlueChannel![ni];
                        count++;
                    }
                }
                int idx = y * w + x;
                result.RedChannel![idx] = (byte)Math.Clamp(sumR / count, 0, max);
                result.GreenChannel![idx] = (byte)Math.Clamp(sumG / count, 0, max);
                result.BlueChannel![idx] = (byte)Math.Clamp(sumB / count, 0, max);
            }
        }
        else // PGM
        {
            for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int sum = 0, count = 0;
                for (int dy = -radius; dy <= radius; dy++)
                for (int dx = -radius; dx <= radius; dx++)
                {
                    int ny = y + dy, nx = x + dx;
                    if (ny >= 0 && ny < h && nx >= 0 && nx < w)
                    {
                        sum += Pixels[ny * w + nx];
                        count++;
                    }
                }
                result.Pixels[y * w + x] = (byte)Math.Clamp(sum / count, 0, max);
            }
        }
        return result;
    }

    /// <summary>
    /// Create a tiled image by repeating this image in an NxM grid.
    /// R113: governed /add-dotnet-api.
    /// </summary>
    /// <param name="tilesX">Number of horizontal tiles (must be >= 1).</param>
    /// <param name="tilesY">Number of vertical tiles (must be >= 1).</param>
    /// <returns>A new image with dimensions (Width*tilesX, Height*tilesY).</returns>
    public NetpbmImage Tile(int tilesX, int tilesY)
    {
        if (tilesX < 1) throw new ArgumentOutOfRangeException(nameof(tilesX), "Must be >= 1.");
        if (tilesY < 1) throw new ArgumentOutOfRangeException(nameof(tilesY), "Must be >= 1.");

        int newW = Width * tilesX;
        int newH = Height * tilesY;
        int bpp = IsPpm(Format) ? 3 : 1;

        var result = new NetpbmImage
        {
            Format = Format,
            Width = newW,
            Height = newH,
            MaxValue = MaxValue,
            Pixels = new byte[newW * newH * bpp]
        };
        if (IsPpm(Format))
        {
            result.RedChannel = new byte[newW * newH];
            result.GreenChannel = new byte[newW * newH];
            result.BlueChannel = new byte[newW * newH];
        }

        for (int ty = 0; ty < tilesY; ty++)
        for (int tx = 0; tx < tilesX; tx++)
        {
            for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                int dstY = ty * Height + y;
                int dstX = tx * Width + x;
                if (IsPpm(Format))
                {
                    int srcIdx = y * Width + x;
                    int dstIdx = dstY * newW + dstX;
                    if (RedChannel != null)
                    {
                        result.RedChannel![dstIdx] = RedChannel[srcIdx];
                        result.GreenChannel![dstIdx] = GreenChannel![srcIdx];
                        result.BlueChannel![dstIdx] = BlueChannel![srcIdx];
                    }
                    result.Pixels[dstIdx * 3] = Pixels[srcIdx * 3];
                    result.Pixels[dstIdx * 3 + 1] = Pixels[srcIdx * 3 + 1];
                    result.Pixels[dstIdx * 3 + 2] = Pixels[srcIdx * 3 + 2];
                }
                else
                {
                    result.Pixels[dstY * newW + dstX] = Pixels[y * Width + x];
                }
            }
        }
        return result;
    }

    // -------------------------------------------------------------------------
    // R114: Pipeline — sequential image transformation
    // -------------------------------------------------------------------------

    /// <summary>
    /// Apply a sequence of transformation steps to this image, threading the
    /// result of each step into the next. Returns the final transformed image.
    ///
    /// R114: governed /add-dotnet-api.
    ///
    /// Example:
    /// <code>
    ///   var result = image.Pipeline(new Func&lt;NetpbmImage, NetpbmImage&gt;[] {
    ///       img => img.ToGrayscale(),
    ///       img => img.AdjustBrightness(20),
    ///       img => img.Threshold(128),
    ///   });
    /// </code>
    /// </summary>
    /// <param name="steps">
    /// Ordered sequence of transformation functions. Each receives the image
    /// produced by the previous step (or this image for the first step).
    /// Must not be null; individual steps must not be null.
    /// </param>
    /// <returns>
    /// The image produced after all steps have been applied in order.
    /// If <paramref name="steps"/> is empty, returns this image unchanged.
    /// </returns>
    /// <exception cref="ArgumentNullException">
    /// Thrown if <paramref name="steps"/> is null or any step function is null.
    /// </exception>
    public NetpbmImage Pipeline(IEnumerable<Func<NetpbmImage, NetpbmImage>> steps)
    {
        if (steps is null) throw new ArgumentNullException(nameof(steps));

        NetpbmImage current = this;
        int index = 0;
        foreach (var step in steps)
        {
            if (step is null)
                throw new ArgumentNullException(nameof(steps),
                    $"Step at index {index} must not be null.");
            current = step(current);
            index++;
        }
        return current;
    }

    /// <summary>
    /// Apply a box-based median filter with the given radius (1 = 3×3 kernel).
    /// Each pixel is replaced by the median of all values in its rectangular neighborhood.
    /// For PGM images the grayscale channel is filtered; for PPM all three channels.
    /// Radius 0 returns a clone unchanged.
    /// R114 Train C: noise-reduction median filter for image processing pipelines.
    /// </summary>
    public NetpbmImage MedianFilter(int radius)
    {
        if (radius < 0)
            throw new ArgumentOutOfRangeException(nameof(radius), "Radius must be >= 0.");
        if (radius == 0) return Clone();

        bool color = IsPpm(Format);
        var result = Clone();

        if (color)
        {
            result.RedChannel = FilterChannel(RedChannel ?? Array.Empty<byte>(), Width, Height, radius);
            result.GreenChannel = FilterChannel(GreenChannel ?? Array.Empty<byte>(), Width, Height, radius);
            result.BlueChannel = FilterChannel(BlueChannel ?? Array.Empty<byte>(), Width, Height, radius);
            // Rebuild Pixels from channels
            var px = new byte[Width * Height * 3];
            var r = result.RedChannel;
            var g = result.GreenChannel;
            var b = result.BlueChannel;
            for (int i = 0; i < Width * Height; i++)
            {
                px[i * 3] = r[i];
                px[i * 3 + 1] = g[i];
                px[i * 3 + 2] = b[i];
            }
            result.Pixels = px;
        }
        else
        {
            result.Pixels = FilterChannel(Pixels, Width, Height, radius);
        }

        return result;
    }

    private static byte[] FilterChannel(byte[] src, int w, int h, int radius)
    {
        var dst = new byte[src.Length];
        var window = new List<byte>((2 * radius + 1) * (2 * radius + 1));
        for (int row = 0; row < h; row++)
        {
            for (int col = 0; col < w; col++)
            {
                window.Clear();
                for (int dr = -radius; dr <= radius; dr++)
                {
                    int nr = Math.Clamp(row + dr, 0, h - 1);
                    for (int dc = -radius; dc <= radius; dc++)
                    {
                        int nc = Math.Clamp(col + dc, 0, w - 1);
                        window.Add(src[nr * w + nc]);
                    }
                }
                window.Sort();
                dst[row * w + col] = window[window.Count / 2];
            }
        }
        return dst;
    }

    /// <summary>
    /// Create a blank canvas of the specified dimensions and format, filled with the given value.
    /// For PPM format, all three channels are set to <paramref name="fill"/>.
    /// R114 Train C: blank canvas factory for image composition pipelines.
    /// </summary>
    public static NetpbmImage Create(int width, int height, NetpbmFormat format, byte fill = 0)
    {
        if (width <= 0)
            throw new ArgumentOutOfRangeException(nameof(width), "Width must be > 0.");
        if (height <= 0)
            throw new ArgumentOutOfRangeException(nameof(height), "Height must be > 0.");

        bool color = IsPpm(format);
        var pixels = color
            ? new byte[width * height * 3]
            : new byte[width * height];

        if (fill != 0)
        {
            for (int i = 0; i < pixels.Length; i++)
                pixels[i] = fill;
        }

        var img = new NetpbmImage
        {
            Format = format,
            Width = width,
            Height = height,
            MaxValue = 255,
            Pixels = pixels,
        };

        if (color)
        {
            var channel = new byte[width * height];
            if (fill != 0)
                for (int i = 0; i < channel.Length; i++)
                    channel[i] = fill;
            img.RedChannel = (byte[])channel.Clone();
            img.GreenChannel = (byte[])channel.Clone();
            img.BlueChannel = (byte[])channel.Clone();
        }

        return img;
    }

    private static bool IsPbm(NetpbmFormat f) => f == NetpbmFormat.PBM_P1 || f == NetpbmFormat.PBM_P4;
    private static bool IsPgm(NetpbmFormat f) => f == NetpbmFormat.PGM_P2 || f == NetpbmFormat.PGM_P5;
    private static bool IsPpm(NetpbmFormat f) => f == NetpbmFormat.PPM_P3 || f == NetpbmFormat.PPM_P6;

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

    // ─── R115 — Drawing primitives + brightness map ────────────────────────────

    /// <summary>
    /// Draw a filled or outlined rectangle on a PGM image.
    /// <paramref name="top"/>/<paramref name="left"/> are 0-based. Clipped to image bounds.
    /// R115 Train A: drawing primitive for image composition pipelines.
    /// </summary>
    /// <param name="top">Top row (0-based).</param>
    /// <param name="left">Left column (0-based).</param>
    /// <param name="rectHeight">Height in pixels.</param>
    /// <param name="rectWidth">Width in pixels.</param>
    /// <param name="fill">Pixel value to fill with (0–255).</param>
    /// <param name="filled">True = filled rect; false = outline only (1 pixel border).</param>
    /// <exception cref="InvalidOperationException">Image is not grayscale (PGM).</exception>
    public void DrawRectangle(int top, int left, int rectHeight, int rectWidth, byte fill, bool filled = true)
    {
        if (Format != NetpbmFormat.PGM_P2 && Format != NetpbmFormat.PGM_P5)
            throw new InvalidOperationException("DrawRectangle is supported on PGM images only.");
        if (rectHeight <= 0 || rectWidth <= 0) return;

        int rowEnd = Math.Min(top + rectHeight, Height);
        int colEnd = Math.Min(left + rectWidth, Width);

        for (int r = Math.Max(top, 0); r < rowEnd; r++)
        {
            for (int c = Math.Max(left, 0); c < colEnd; c++)
            {
                bool isBorder = !filled &&
                    (r == top || r == rowEnd - 1 || c == Math.Max(left, 0) || c == colEnd - 1);
                if (filled || isBorder)
                    Pixels[r * Width + c] = fill;
            }
        }
    }

    /// <summary>
    /// Return a flattened array of per-pixel brightness values (0.0–1.0).
    /// For PGM images, brightness = pixel / MaxValue.
    /// For PPM images, brightness = 0.299R + 0.587G + 0.114B (Rec. 601 luma).
    /// R115 Train B: brightness map for image analysis pipeline.
    /// </summary>
    public double[] GetBrightnessMap()
    {
        int n = Width * Height;
        var map = new double[n];
        double maxVal = MaxValue > 0 ? MaxValue : 255.0;

        if (Format == NetpbmFormat.PPM_P3 || Format == NetpbmFormat.PPM_P6)
        {
            var r = RedChannel ?? Array.Empty<byte>();
            var g = GreenChannel ?? Array.Empty<byte>();
            var b = BlueChannel ?? Array.Empty<byte>();
            for (int i = 0; i < n; i++)
                map[i] = (0.299 * (i < r.Length ? r[i] : 0)
                        + 0.587 * (i < g.Length ? g[i] : 0)
                        + 0.114 * (i < b.Length ? b[i] : 0)) / maxVal;
        }
        else
        {
            for (int i = 0; i < n && i < Pixels.Length; i++)
                map[i] = Pixels[i] / maxVal;
        }
        return map;
    }

    /// <summary>
    /// Draw a line between two points using Bresenham's algorithm (PGM only).
    /// Clips to image bounds. Throws InvalidOperationException for PPM images.
    /// R116 Train A: drawing primitives.
    /// </summary>
    public void DrawLine(int x0, int y0, int x1, int y1, byte fill)
    {
        if (Format != NetpbmFormat.PGM_P2 && Format != NetpbmFormat.PGM_P5)
            throw new InvalidOperationException("DrawLine is supported on PGM images only.");

        // Bresenham's line algorithm
        int dx = Math.Abs(x1 - x0);
        int dy = Math.Abs(y1 - y0);
        int sx = x0 < x1 ? 1 : -1;
        int sy = y0 < y1 ? 1 : -1;
        int err = dx - dy;

        while (true)
        {
            // Set pixel if in bounds (x=col, y=row)
            if (x0 >= 0 && x0 < Width && y0 >= 0 && y0 < Height)
                Pixels[y0 * Width + x0] = fill;

            if (x0 == x1 && y0 == y1) break;
            int e2 = 2 * err;
            if (e2 > -dy) { err -= dy; x0 += sx; }
            if (e2 < dx)  { err += dx; y0 += sy; }
        }
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
