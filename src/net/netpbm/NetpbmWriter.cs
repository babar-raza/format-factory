// FormatFactory.Netpbm -- Commercial .NET Netpbm Writer
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: NOT_STARTED (R85 first slice)
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;

namespace FormatFactory.Netpbm;

/// <summary>
/// Writer for Netpbm image family (PBM P1, PGM P2, PPM P3 — ASCII variants).
///
/// Writes ASCII Netpbm format (P1/P2/P3). Binary variants (P4/P5/P6) are future work.
/// </summary>
public static class NetpbmWriter
{
    /// <summary>
    /// Write a NetpbmImage to disk as ASCII Netpbm (P1/P2/P3).
    /// </summary>
    public static void Write(NetpbmImage image, string outputPath)
    {
        string ascii = ToAsciiString(image);
        File.WriteAllText(outputPath, ascii, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }

    /// <summary>
    /// Serialize a NetpbmImage to an ASCII Netpbm string.
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
}
