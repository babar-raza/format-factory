// FormatFactory.Netpbm -- Commercial .NET Netpbm Writer
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: NOT_STARTED (R85 first slice, R86 binary write)
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;

namespace FormatFactory.Netpbm;

/// <summary>
/// Writer for Netpbm image family.
/// ASCII variants: PBM P1, PGM P2, PPM P3.
/// Binary variants: PBM P4, PGM P5, PPM P6 (added R86 ).
/// </summary>
public static class NetpbmWriter
{
    /// <summary>
    /// Write a NetpbmImage to disk in its native format.
    /// ASCII formats (P1/P2/P3) use UTF-8 text; binary formats (P4/P5/P6) use raw bytes.
    /// </summary>
    public static void Write(NetpbmImage image, string outputPath)
    {
        if (image.Format is NetpbmFormat.PBM_P4 or NetpbmFormat.PGM_P5 or NetpbmFormat.PPM_P6)
        {
            byte[] bytes = ToBinaryBytes(image);
            File.WriteAllBytes(outputPath, bytes);
        }
        else
        {
            string ascii = ToAsciiString(image);
            File.WriteAllText(outputPath, ascii, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        }
    }

    /// <summary>
    /// Serialize a NetpbmImage to an ASCII Netpbm string (P1/P2/P3).
    /// For binary format images, this produces the ASCII equivalent.
    /// </summary>
    public static string ToAsciiString(NetpbmImage image)
    {
        return image.Format switch
        {
            NetpbmFormat.PBM_P1 or NetpbmFormat.PBM_P4 => WritePbm(image),
            NetpbmFormat.PGM_P2 or NetpbmFormat.PGM_P5 => WritePgm(image),
            NetpbmFormat.PPM_P3 or NetpbmFormat.PPM_P6 => WritePpm(image),
            _ => throw new NetpbmException($"Unsupported format: {image.Format}")
        };
    }

    /// <summary>
    /// Serialize a NetpbmImage to binary Netpbm bytes (P4/P5/P6).
    /// </summary>
    public static byte[] ToBinaryBytes(NetpbmImage image)
    {
        return image.Format switch
        {
            NetpbmFormat.PBM_P4 or NetpbmFormat.PBM_P1 => WriteBinaryPbm(image),
            NetpbmFormat.PGM_P5 or NetpbmFormat.PGM_P2 => WriteBinaryPgm(image),
            NetpbmFormat.PPM_P6 or NetpbmFormat.PPM_P3 => WriteBinaryPpm(image),
            _ => throw new NetpbmException($"Unsupported format for binary write: {image.Format}")
        };
    }

    private static string WritePbm(NetpbmImage image)
    {
        var sb = new StringBuilder();
        sb.AppendLine("P1");
        foreach (var comment in image.Comments)
            sb.AppendLine($"# {comment}");
        sb.AppendLine($"{image.Width} {image.Height}");
        for (int row = 0; row < image.Height; row++)
        {
            var rowTokens = new string[image.Width];
            for (int col = 0; col < image.Width; col++)
                rowTokens[col] = image.Pixels[row * image.Width + col].ToString();
            sb.AppendLine(string.Join(" ", rowTokens));
        }
        return sb.ToString();
    }

    private static string WritePgm(NetpbmImage image)
    {
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        foreach (var comment in image.Comments)
            sb.AppendLine($"# {comment}");
        sb.AppendLine($"{image.Width} {image.Height}");
        sb.AppendLine($"{image.MaxValue}");
        for (int row = 0; row < image.Height; row++)
        {
            var rowTokens = new string[image.Width];
            for (int col = 0; col < image.Width; col++)
                rowTokens[col] = image.Pixels[row * image.Width + col].ToString();
            sb.AppendLine(string.Join(" ", rowTokens));
        }
        return sb.ToString();
    }

    private static string WritePpm(NetpbmImage image)
    {
        if (image.RedChannel == null || image.GreenChannel == null || image.BlueChannel == null)
            throw new NetpbmException("PPM image missing channel data.");
        var sb = new StringBuilder();
        sb.AppendLine("P3");
        foreach (var comment in image.Comments)
            sb.AppendLine($"# {comment}");
        sb.AppendLine($"{image.Width} {image.Height}");
        sb.AppendLine($"{image.MaxValue}");
        long count = (long)image.Width * image.Height;
        for (long i = 0; i < count; i++)
        {
            sb.Append(image.RedChannel[i]);
            sb.Append(' ');
            sb.Append(image.GreenChannel[i]);
            sb.Append(' ');
            sb.AppendLine(image.BlueChannel[i].ToString());
        }
        return sb.ToString();
    }

 // --- Binary writers (P4/P5/P6) — added R86 ---

    private static byte[] BuildBinaryHeader(string magic, NetpbmImage image, bool includeMaxVal)
    {
        var sb = new StringBuilder();
        sb.Append(magic);
        sb.Append('\n');
        foreach (var comment in image.Comments)
        {
            sb.Append("# ");
            sb.Append(comment);
            sb.Append('\n');
        }
        sb.Append(image.Width);
        sb.Append(' ');
        sb.Append(image.Height);
        sb.Append('\n');
        if (includeMaxVal)
        {
            sb.Append(image.MaxValue);
            sb.Append('\n');
        }
        return Encoding.ASCII.GetBytes(sb.ToString());
    }

    private static byte[] WriteBinaryPbm(NetpbmImage image)
    {
        byte[] header = BuildBinaryHeader("P4", image, includeMaxVal: false);
        int rowBytes = (image.Width + 7) / 8;
        byte[] pixelData = new byte[rowBytes * image.Height];

        for (int row = 0; row < image.Height; row++)
        {
            for (int col = 0; col < image.Width; col++)
            {
                byte pixel = image.Pixels[row * image.Width + col];
                if (pixel != 0)
                {
                    int byteIdx = row * rowBytes + col / 8;
                    int bitIdx = 7 - (col % 8);
                    pixelData[byteIdx] |= (byte)(1 << bitIdx);
                }
            }
        }

        byte[] result = new byte[header.Length + pixelData.Length];
        Buffer.BlockCopy(header, 0, result, 0, header.Length);
        Buffer.BlockCopy(pixelData, 0, result, header.Length, pixelData.Length);
        return result;
    }

    private static byte[] WriteBinaryPgm(NetpbmImage image)
    {
        byte[] header = BuildBinaryHeader("P5", image, includeMaxVal: true);
        long count = (long)image.Width * image.Height;
        byte[] pixelData = new byte[count];
        Array.Copy(image.Pixels, 0, pixelData, 0, count);

        byte[] result = new byte[header.Length + pixelData.Length];
        Buffer.BlockCopy(header, 0, result, 0, header.Length);
        Buffer.BlockCopy(pixelData, 0, result, header.Length, pixelData.Length);
        return result;
    }

    private static byte[] WriteBinaryPpm(NetpbmImage image)
    {
        if (image.RedChannel == null || image.GreenChannel == null || image.BlueChannel == null)
            throw new NetpbmException("PPM image missing channel data.");

        byte[] header = BuildBinaryHeader("P6", image, includeMaxVal: true);
        long count = (long)image.Width * image.Height;
        byte[] pixelData = new byte[count * 3];

        for (long i = 0; i < count; i++)
        {
            pixelData[i * 3] = image.RedChannel[i];
            pixelData[i * 3 + 1] = image.GreenChannel[i];
            pixelData[i * 3 + 2] = image.BlueChannel[i];
        }

        byte[] result = new byte[header.Length + pixelData.Length];
        Buffer.BlockCopy(header, 0, result, 0, header.Length);
        Buffer.BlockCopy(pixelData, 0, result, header.Length, pixelData.Length);
        return result;
    }
}
