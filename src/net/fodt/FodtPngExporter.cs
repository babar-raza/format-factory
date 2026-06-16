// FormatFactory.Fodt -- Commercial .NET FODT → PNG Document Outline Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: product-deepening-fodt-png-export-20260616
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
//
// Pure .NET PNG 1.0 writer — no NuGet dependencies.
// Renders FODT document as a paragraph-outline thumbnail image.
// Each paragraph is a horizontal bar; heading paragraphs use a distinct color.

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Text;

namespace FormatFactory.Fodt;

/// <summary>
/// Result returned by <see cref="FodtPngExporter.ExportToPng"/>.
/// </summary>
public sealed class FodtPngExportResult
{
    /// <summary>Path to the generated PNG file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Width of the PNG image in pixels.</summary>
    public int WidthPx { get; init; }

    /// <summary>Height of the PNG image in pixels.</summary>
    public int HeightPx { get; init; }

    /// <summary>Number of paragraphs rendered.</summary>
    public int ParagraphsRendered { get; init; }
}

/// <summary>
/// G11-E Expanded Prototype: Exports a FODT text document to a PNG document-outline thumbnail.
///
/// Scope:
///   - Each paragraph rendered as a horizontal bar (4 px high, 1 px gap).
///   - Heading paragraphs: medium blue (R=68,G=114,B=196), full width.
///   - Body paragraphs: light gray (R=224,G=224,B=224), width proportional to word count.
///   - Background: white (R=255,G=255,B=255).
///   - Image width: 200 px. Max paragraphs rendered: 100.
///   - Output: 24-bit RGB PNG 1.0 using System.IO.Compression.ZLibStream (.NET 6+).
///
/// Limitations (prototype):
///   - No text rendering — paragraph outline visualization only.
///   - Bar length proportional to word count (min 8 px, max 200 px).
///
/// Security: input size guarded at 50 MiB file size.
///
/// ODF basis: §5.1.2 text:h, §5.1.3 text:p (ODF 1.3)
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodtPngExporter
{
    private const int ImgWidth = 200;   // image width in pixels
    private const int BarHeight = 4;    // paragraph bar height
    private const int BarGap = 1;       // gap between bars
    private const int MaxParas = 100;   // max paragraphs rendered
    private const int MinBarWidth = 8;  // minimum bar width for any paragraph

    private static readonly byte[] ColorHeading = { 68, 114, 196 };  // medium blue
    private static readonly byte[] ColorBody = { 224, 224, 224 };    // light gray
    private static readonly byte[] ColorBg = { 255, 255, 255 };      // white background

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodtPath"/> and export to PNG at <paramref name="pngPath"/>.
    /// </summary>
    public static FodtPngExportResult ExportToPng(
        string fodtPath,
        string pngPath,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodtPath))
            throw new ArgumentNullException(nameof(fodtPath));
        if (string.IsNullOrWhiteSpace(pngPath))
            throw new ArgumentNullException(nameof(pngPath));

        var doc = FodtDocument.Load(fodtPath, maxFileSizeBytes);
        return ExportToPng(doc, pngPath);
    }

    /// <summary>
    /// Export <paramref name="document"/> to a PNG at <paramref name="pngPath"/>.
    /// </summary>
    public static FodtPngExportResult ExportToPng(FodtDocument document, string pngPath)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        if (string.IsNullOrWhiteSpace(pngPath))
            throw new ArgumentNullException(nameof(pngPath));

        byte[] bytes = ExportToPngBytes(document);
        File.WriteAllBytes(pngPath, bytes);

        var lines = BuildRenderLines(document);
        int rendered = Math.Min(lines.Count, MaxParas);
        int h = rendered == 0 ? 1 : rendered * (BarHeight + BarGap);
        return new FodtPngExportResult
        {
            OutputPath = pngPath,
            WidthPx = rendered == 0 ? 1 : ImgWidth,
            HeightPx = h,
            ParagraphsRendered = rendered,
        };
    }

    /// <summary>
    /// Export <paramref name="document"/> to a PNG byte array (no file I/O).
    /// </summary>
    public static byte[] ExportToPngBytes(FodtDocument document)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        var lines = BuildRenderLines(document);
        return WritePng(lines);
    }

    // -------------------------------------------------------------------------
    // Internal: render line extraction
    // -------------------------------------------------------------------------

    private sealed class RenderLine
    {
        public bool IsHeading { get; init; }
        public int WordCount { get; init; }
    }

    private static List<RenderLine> BuildRenderLines(FodtDocument doc)
    {
        var paragraphs = doc.GetParagraphTexts();
        var headingSet = new HashSet<string>(doc.GetHeadingTexts(), StringComparer.Ordinal);
        var lines = new List<RenderLine>();

        foreach (var para in paragraphs)
        {
            if (lines.Count >= MaxParas) break;
            if (string.IsNullOrWhiteSpace(para)) continue;
            lines.Add(new RenderLine
            {
                IsHeading = headingSet.Contains(para),
                WordCount = para.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length,
            });
        }
        return lines;
    }

    // -------------------------------------------------------------------------
    // Internal: PNG writer
    // -------------------------------------------------------------------------

    private static byte[] WritePng(List<RenderLine> lines)
    {
        int rendered = Math.Min(lines.Count, MaxParas);
        int imgW = rendered == 0 ? 1 : ImgWidth;
        int imgH = rendered == 0 ? 1 : rendered * (BarHeight + BarGap);

        byte[] pixels = BuildPixelData(lines, imgW, imgH, rendered);

        using var ms = new MemoryStream();

        // PNG signature
        ms.Write(new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A });

        // IHDR
        WriteChunk(ms, "IHDR", BuildIhdr(imgW, imgH));

        // IDAT
        byte[] idatData;
        using (var idatMs = new MemoryStream())
        {
            using (var zlib = new ZLibStream(idatMs, CompressionLevel.Fastest, leaveOpen: true))
                zlib.Write(pixels, 0, pixels.Length);
            idatData = idatMs.ToArray();
        }
        WriteChunk(ms, "IDAT", idatData);

        // IEND
        WriteChunk(ms, "IEND", Array.Empty<byte>());

        return ms.ToArray();
    }

    private static byte[] BuildIhdr(int width, int height)
    {
        var b = new byte[13];
        WriteUInt32Be(b, 0, (uint)width);
        WriteUInt32Be(b, 4, (uint)height);
        b[8] = 8;  // bit depth
        b[9] = 2;  // color type: RGB
        return b;
    }

    private static int ComputeBarWidth(RenderLine line)
    {
        if (line.IsHeading) return ImgWidth;
        // proportional to word count: 1 word → MinBarWidth, 20+ words → ImgWidth
        int w = MinBarWidth + (line.WordCount - 1) * (ImgWidth - MinBarWidth) / 20;
        return Math.Clamp(w, MinBarWidth, ImgWidth);
    }

    private static byte[] BuildPixelData(List<RenderLine> lines, int imgW, int imgH, int rendered)
    {
        byte[] data = new byte[imgH * (1 + imgW * 3)];
        int pos = 0;

        if (rendered == 0)
        {
            // 1×1 white pixel
            data[pos++] = 0; // filter None
            data[pos++] = ColorBg[0];
            data[pos++] = ColorBg[1];
            data[pos++] = ColorBg[2];
            return data;
        }

        for (int i = 0; i < rendered; i++)
        {
            var line = lines[i];
            int barW = ComputeBarWidth(line);
            byte[] barColor = line.IsHeading ? ColorHeading : ColorBody;

            for (int row = 0; row < BarHeight; row++)
            {
                data[pos++] = 0; // filter None
                for (int px = 0; px < imgW; px++)
                {
                    byte[] c = px < barW ? barColor : ColorBg;
                    data[pos++] = c[0];
                    data[pos++] = c[1];
                    data[pos++] = c[2];
                }
            }
            // Gap row (white)
            data[pos++] = 0;
            for (int px = 0; px < imgW; px++)
            {
                data[pos++] = ColorBg[0];
                data[pos++] = ColorBg[1];
                data[pos++] = ColorBg[2];
            }
        }
        return data;
    }

    // -------------------------------------------------------------------------
    // PNG chunk utilities (duplicated from FodsPngExporter — no shared dep)
    // -------------------------------------------------------------------------

    private static void WriteChunk(Stream stream, string type, byte[] data)
    {
        var typeBytes = Encoding.ASCII.GetBytes(type);
        var lenBytes = new byte[4];
        WriteUInt32Be(lenBytes, 0, (uint)data.Length);
        stream.Write(lenBytes);
        stream.Write(typeBytes);
        stream.Write(data);
        uint crc = Crc32(typeBytes);
        crc = Crc32Continue(crc, data);
        var crcBytes = new byte[4];
        WriteUInt32Be(crcBytes, 0, crc);
        stream.Write(crcBytes);
    }

    private static void WriteUInt32Be(byte[] buf, int offset, uint value)
    {
        buf[offset] = (byte)(value >> 24);
        buf[offset + 1] = (byte)(value >> 16);
        buf[offset + 2] = (byte)(value >> 8);
        buf[offset + 3] = (byte)value;
    }

    private static readonly uint[] CrcTable = BuildCrcTable();

    private static uint[] BuildCrcTable()
    {
        var table = new uint[256];
        for (uint i = 0; i < 256; i++)
        {
            uint c = i;
            for (int k = 0; k < 8; k++)
                c = (c & 1) != 0 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            table[i] = c;
        }
        return table;
    }

    private static uint Crc32(byte[] data)
    {
        uint crc = 0xFFFFFFFF;
        foreach (byte b in data)
            crc = CrcTable[(crc ^ b) & 0xFF] ^ (crc >> 8);
        return crc ^ 0xFFFFFFFF;
    }

    private static uint Crc32Continue(uint crc, byte[] data)
    {
        uint c = crc ^ 0xFFFFFFFF;
        foreach (byte b in data)
            c = CrcTable[(c ^ b) & 0xFF] ^ (c >> 8);
        return c ^ 0xFFFFFFFF;
    }
}
