// FormatFactory.Netpbm -- Commercial .NET Netpbm Parser
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: NOT_STARTED (R85 first slice)
// commercial_product_ready: false

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FormatFactory.Netpbm;

/// <summary>
/// Parser for Netpbm image family (PBM P1/P4, PGM P2/P5, PPM P3/P6).
///
/// Spec: https://netpbm.sourceforge.net/doc/ (public domain)
///
/// Security posture:
///   - File size guard (MaxFileSizeBytes, default 64 MB)
///   - Dimension guard (MaxDimension, default 65536)
///   - Pixel count guard (MaxPixels = 1 billion)
/// </summary>
public static class NetpbmParser
{
    public const long DefaultMaxFileSizeBytes = 64L * 1024 * 1024;
    public const int DefaultMaxDimension = 65536;
    public const long DefaultMaxPixels = 1_000_000_000L;

    /// <summary>
    /// Parse a Netpbm file from disk. Supports P1, P2, P3, P4, P5, P6.
    /// </summary>
    public static NetpbmImage Parse(
        string filePath,
        long maxFileSizeBytes = DefaultMaxFileSizeBytes,
        int maxDimension = DefaultMaxDimension)
    {
        if (!File.Exists(filePath))
            throw new NetpbmException($"File not found: {filePath}");

        var info = new FileInfo(filePath);
        if (info.Length > maxFileSizeBytes)
            throw new NetpbmSizeException(
                $"File size {info.Length} exceeds limit {maxFileSizeBytes}.");

        using var stream = File.OpenRead(filePath);
        return ParseStream(stream, filePath, maxFileSizeBytes, maxDimension);
    }

    /// <summary>Parse from a stream (e.g. for testing).</summary>
    public static NetpbmImage ParseStream(
        Stream stream,
        string? sourcePath = null,
        long maxFileSizeBytes = DefaultMaxFileSizeBytes,
        int maxDimension = DefaultMaxDimension)
    {
        // Read all bytes — PBM/PGM/PPM are small in practice
        using var ms = new MemoryStream();
        stream.CopyTo(ms);
        var data = ms.ToArray();

        if (data.Length == 0)
            throw new NetpbmException("Empty file.");

        // Parse magic number (first 2 bytes, ASCII)
        if (data.Length < 2)
            throw new NetpbmFormatException("File too short for magic number.");

        char p = (char)data[0];
        char n = (char)data[1];
        if (p != 'P' || n < '1' || n > '6')
            throw new NetpbmFormatException(
                $"Invalid magic number: '{p}{n}'. Expected P1-P6.");

        var format = n switch
        {
            '1' => NetpbmFormat.PBM_P1,
            '4' => NetpbmFormat.PBM_P4,
            '2' => NetpbmFormat.PGM_P2,
            '5' => NetpbmFormat.PGM_P5,
            '3' => NetpbmFormat.PPM_P3,
            '6' => NetpbmFormat.PPM_P6,
            _ => throw new NetpbmFormatException($"Unsupported magic: P{n}")
        };

        // Parse ASCII header: magic, [comments], width, height, [maxval]
        var (comments, width, height, maxValue, pixelDataOffset) =
            ParseHeader(data, format, maxDimension);

        // Validate pixel count
        long pixelCount = (long)width * height;
        if (pixelCount > DefaultMaxPixels)
            throw new NetpbmSizeException(
                $"Image {width}x{height} = {pixelCount} pixels exceeds limit.");

        var image = new NetpbmImage
        {
            Format = format,
            Width = width,
            Height = height,
            MaxValue = maxValue,
            SourcePath = sourcePath,
        };
        image.Comments.AddRange(comments);

        // Parse pixels
        bool isBinary = format is NetpbmFormat.PBM_P4
                               or NetpbmFormat.PGM_P5
                               or NetpbmFormat.PPM_P6;

        if (isBinary)
            ParseBinaryPixels(image, data, pixelDataOffset);
        else
            ParseAsciiPixels(image, data, pixelDataOffset);

        return image;
    }

    // -------------------------------------------------------------------------
    // Header parsing
    // -------------------------------------------------------------------------

    private static (List<string> comments, int width, int height, int maxValue, int offset)
        ParseHeader(byte[] data, NetpbmFormat format, int maxDimension)
    {
        var comments = new List<string>();
        int pos = 2; // skip magic

        int[] headerInts = new int[3]; // width, height, maxval (maxval absent for PBM)
        int intCount = 0;
        bool needsMaxVal = format is not (NetpbmFormat.PBM_P1 or NetpbmFormat.PBM_P4);
        int requiredInts = needsMaxVal ? 3 : 2;

        while (intCount < requiredInts && pos < data.Length)
        {
            // Skip whitespace
            while (pos < data.Length && IsWhitespace(data[pos]))
                pos++;
            if (pos >= data.Length) break;

            // Comment
            if (data[pos] == '#')
            {
                var sb = new StringBuilder();
                pos++; // skip #
                while (pos < data.Length && data[pos] != '\n' && data[pos] != '\r')
                    sb.Append((char)data[pos++]);
                comments.Add(sb.ToString().Trim());
                continue;
            }

            // Read integer token
            if (!IsDigit(data[pos]))
                throw new NetpbmFormatException(
                    $"Expected integer in header at offset {pos}, got '{(char)data[pos]}'.");

            int val = 0;
            while (pos < data.Length && IsDigit(data[pos]))
            {
                val = val * 10 + (data[pos] - '0');
                pos++;
            }
            headerInts[intCount++] = val;
        }

        if (intCount < requiredInts)
            throw new NetpbmFormatException("Incomplete header — missing width/height/maxval.");

        int width = headerInts[0];
        int height = headerInts[1];
        int maxValue = needsMaxVal ? headerInts[2] : 1;

        if (width <= 0 || width > maxDimension)
            throw new NetpbmSizeException($"Invalid width: {width}");
        if (height <= 0 || height > maxDimension)
            throw new NetpbmSizeException($"Invalid height: {height}");
        if (needsMaxVal && (maxValue <= 0 || maxValue > 65535))
            throw new NetpbmFormatException($"Invalid maxval: {maxValue}");

        // For binary formats: pixel data starts after exactly one whitespace byte after header
        if (format is NetpbmFormat.PBM_P4 or NetpbmFormat.PGM_P5 or NetpbmFormat.PPM_P6)
        {
            // The one whitespace byte separating header from data
            if (pos < data.Length && IsWhitespace(data[pos]))
                pos++;
        }

        return (comments, width, height, maxValue, pos);
    }

    // -------------------------------------------------------------------------
    // Pixel parsing: ASCII
    // -------------------------------------------------------------------------

    private static void ParseAsciiPixels(NetpbmImage image, byte[] data, int offset)
    {
        long count = (long)image.Width * image.Height;
        bool isPpm = image.Format is NetpbmFormat.PPM_P3;

        if (isPpm)
        {
            long colorCount = count * 3;
            image.RedChannel = new byte[count];
            image.GreenChannel = new byte[count];
            image.BlueChannel = new byte[count];

            long pixel = 0;
            int channel = 0;
            int pos = offset;
            while (pixel < count && pos < data.Length)
            {
                // skip whitespace + comments
                while (pos < data.Length && (IsWhitespace(data[pos]) || data[pos] == '#'))
                {
                    if (data[pos] == '#')
                        while (pos < data.Length && data[pos] != '\n') pos++;
                    else
                        pos++;
                }
                if (pos >= data.Length) break;

                if (!IsDigit(data[pos]))
                    throw new NetpbmFormatException($"Expected pixel digit at offset {pos}.");
                int val = 0;
                while (pos < data.Length && IsDigit(data[pos]))
                    val = val * 10 + (data[pos++] - '0');

                byte bval = (byte)Math.Min(val, 255);
                switch (channel)
                {
                    case 0: image.RedChannel[pixel] = bval; break;
                    case 1: image.GreenChannel[pixel] = bval; break;
                    case 2: image.BlueChannel[pixel] = bval; pixel++; break;
                }
                channel = (channel + 1) % 3;
            }
        }
        else
        {
            image.Pixels = new byte[count];
            long pixel = 0;
            int pos = offset;
            while (pixel < count && pos < data.Length)
            {
                while (pos < data.Length && (IsWhitespace(data[pos]) || data[pos] == '#'))
                {
                    if (data[pos] == '#')
                        while (pos < data.Length && data[pos] != '\n') pos++;
                    else
                        pos++;
                }
                if (pos >= data.Length) break;

                if (!IsDigit(data[pos]))
                    throw new NetpbmFormatException($"Expected pixel digit at offset {pos}.");
                int val = 0;
                while (pos < data.Length && IsDigit(data[pos]))
                    val = val * 10 + (data[pos++] - '0');

                image.Pixels[pixel++] = (byte)Math.Min(val, 255);
            }
        }
    }

    // -------------------------------------------------------------------------
    // Pixel parsing: binary
    // -------------------------------------------------------------------------

    private static void ParseBinaryPixels(NetpbmImage image, byte[] data, int offset)
    {
        long count = (long)image.Width * image.Height;

        if (image.Format == NetpbmFormat.PPM_P6)
        {
            image.RedChannel = new byte[count];
            image.GreenChannel = new byte[count];
            image.BlueChannel = new byte[count];
            long needed = count * 3;
            if (data.Length - offset < needed)
                throw new NetpbmFormatException(
                    $"Binary PPM: need {needed} bytes, have {data.Length - offset}.");
            for (long i = 0; i < count; i++)
            {
                image.RedChannel[i] = data[offset + i * 3];
                image.GreenChannel[i] = data[offset + i * 3 + 1];
                image.BlueChannel[i] = data[offset + i * 3 + 2];
            }
        }
        else if (image.Format == NetpbmFormat.PGM_P5)
        {
            if (data.Length - offset < count)
                throw new NetpbmFormatException(
                    $"Binary PGM: need {count} bytes, have {data.Length - offset}.");
            image.Pixels = new byte[count];
            Array.Copy(data, offset, image.Pixels, 0, count);
        }
        else // PBM_P4: packed bits, 1 bit per pixel, rows padded to byte boundary
        {
            image.Pixels = new byte[count];
            int rowBytes = (image.Width + 7) / 8;
            long needed = (long)rowBytes * image.Height;
            if (data.Length - offset < needed)
                throw new NetpbmFormatException(
                    $"Binary PBM: need {needed} bytes, have {data.Length - offset}.");
            for (int row = 0; row < image.Height; row++)
            {
                for (int col = 0; col < image.Width; col++)
                {
                    int byteIdx = offset + row * rowBytes + col / 8;
                    int bitIdx = 7 - (col % 8);
                    image.Pixels[row * image.Width + col] =
                        (byte)((data[byteIdx] >> bitIdx) & 1);
                }
            }
        }
    }

    private static bool IsWhitespace(byte b) =>
        b == ' ' || b == '\t' || b == '\n' || b == '\r' || b == '\f' || b == '\v';

    private static bool IsDigit(byte b) => b >= '0' && b <= '9';
}
