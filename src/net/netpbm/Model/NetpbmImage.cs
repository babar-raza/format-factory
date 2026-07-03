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
public sealed partial class NetpbmImage
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
    /// <summary>Red channel pixel data (PPM only). Null for PBM/PGM images.</summary>
    public byte[]? RedChannel { get; set; }
    /// <summary>Green channel pixel data (PPM only). Null for PBM/PGM images.</summary>
    public byte[]? GreenChannel { get; set; }
    /// <summary>Blue channel pixel data (PPM only). Null for PBM/PGM images.</summary>
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
    // Region operations
    // -------------------------------------------------------------------------

    /// <summary>
    /// Fill a rectangular region with a uniform value (PBM/PGM) or color (PPM).
    /// For PBM, value must be 0 or 1. For PPM, all three channel values are used.
    /// region fill API for image editing workflows.
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
    /// region copy for image compositing.
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
    /// Convert a PPM (color) image to a PGM (grayscale) image using standard luminance weights.
    /// Formula: gray = 0.299*R + 0.587*G + 0.114*B (ITU-R BT.601).
    /// Throws InvalidOperationException if the image is not PPM format.
    /// color-to-grayscale conversion for image pipeline.
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
    /// grayscale-to-color conversion for dogfood export pipeline.
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
            byte gv = Pixels[i];
            result.RedChannel[i] = gv;
            result.GreenChannel[i] = gv;
            result.BlueChannel[i] = gv;
        }

        return result;
    }

    /// <summary>
    /// Extract a single color channel from a PPM image as a PGM grayscale image.
    /// Channel: 0 = Red, 1 = Green, 2 = Blue.
    /// Throws if the image is not PPM format or channel index is invalid.
    /// channel separation for color analysis pipeline.
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
    /// same-format save for edit persistence.
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
    /// image cloning for non-destructive editing pipeline.
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
    /// Convert between ASCII and binary variants of the same Netpbm type.
    /// P1↔P4 (PBM), P2↔P5 (PGM), P3↔P6 (PPM).
    /// Does not alter pixel data — only changes the Format field.
    /// Returns a new image; does not modify the original.
    /// format conversion for save pipeline flexibility.
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

    // ─── R114: Pipeline — sequential image transformation ──────────────────────

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
    /// Create a blank canvas of the specified dimensions and format, filled with the given value.
    /// For PPM format, all three channels are set to <paramref name="fill"/>.
    /// blank canvas factory for image composition pipelines.
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

    // ─── R115 — Drawing primitives ────────────────────────────────────────────

    /// <summary>
    /// Draw a filled or outlined rectangle on a PGM image.
    /// <paramref name="top"/>/<paramref name="left"/> are 0-based. Clipped to image bounds.
    /// drawing primitive for image composition pipelines.
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
    /// Draw a line between two points using Bresenham's algorithm (PGM only).
    /// Clips to image bounds. Throws InvalidOperationException for PPM images.
    /// drawing primitives.
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
