// FormatFactory.Fods -- Commercial .NET FODS → PNG Thumbnail Exporter
// DEC-033 Option B: .NET Commercial Only
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// Sprint: product-deepening-fods-png-export-20260616
// PROTOTYPE STATUS: design_complete_in_progress
// commercial_product_ready: false
// Do NOT package or publish.
//
// Pure .NET PNG 1.0 writer — no NuGet dependencies.
// Produces a thumbnail grid image where each cell is a colored 16×16 pixel block.
// Non-empty cells: light blue (173,216,230). Empty cells: white (255,255,255).
// Grid lines: gray (128,128,128), 1 pixel.

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Text;

namespace FormatFactory.Fods;

/// <summary>
/// Result returned by <see cref="FodsPngExporter.ExportToPng"/>.
/// </summary>
public sealed class FodsPngExportResult
{
    /// <summary>Path to the generated PNG file.</summary>
    public string OutputPath { get; init; } = string.Empty;

    /// <summary>Width of the PNG image in pixels.</summary>
    public int WidthPx { get; init; }

    /// <summary>Height of the PNG image in pixels.</summary>
    public int HeightPx { get; init; }

    /// <summary>Number of rows rendered.</summary>
    public int RowsRendered { get; init; }

    /// <summary>Number of columns rendered.</summary>
    public int ColsRendered { get; init; }
}

/// <summary>
/// G11-E Expanded Prototype: Exports a FODS spreadsheet sheet to a PNG thumbnail image.
///
/// Scope:
///   - Each cell rendered as a 16×16 pixel colored block.
///   - Non-empty cells: light blue (R=173,G=216,B=230).
///   - Empty cells: white (R=255,G=255,B=255).
///   - 1-pixel gray (R=128,G=128,B=128) grid lines between cells.
///   - Output: 24-bit RGB PNG 1.0.
///   - Uses System.IO.Compression.ZLibStream for PNG IDAT compression (.NET 6+).
///
/// Limitations (prototype):
///   - No text rendering in cells (thumbnail overview only).
///   - No colors, fonts, or styling — data-presence visualization only.
///   - Single sheet per PNG file.
///
/// Security: input size guarded at 50 MiB file size.
///
/// ODF basis: §9.1.4 table:table (ODF 1.3)
///
/// Gate 11 status: g11e_prototype_complete — NOT release-ready. G11-G not approved.
/// commercial_product_ready: false
/// </summary>
public static class FodsPngExporter
{
    private const int CellPx = 16;  // pixels per cell (width and height)
    private const int BorderPx = 1; // grid line width in pixels

    // Cell colours (RGB)
    private static readonly byte[] ColorEmpty = { 255, 255, 255 };    // white
    private static readonly byte[] ColorFilled = { 173, 216, 230 };   // light blue
    private static readonly byte[] ColorGrid = { 128, 128, 128 };     // gray grid lines

    // -------------------------------------------------------------------------
    // Public API
    // -------------------------------------------------------------------------

    /// <summary>
    /// Load <paramref name="fodsPath"/> and export sheet <paramref name="sheetIndex"/> to a PNG at <paramref name="pngPath"/>.
    /// </summary>
    public static FodsPngExportResult ExportToPng(
        string fodsPath,
        string pngPath,
        int sheetIndex = 0,
        long maxFileSizeBytes = 50L * 1024 * 1024)
    {
        if (string.IsNullOrWhiteSpace(fodsPath))
            throw new ArgumentNullException(nameof(fodsPath));
        if (string.IsNullOrWhiteSpace(pngPath))
            throw new ArgumentNullException(nameof(pngPath));

        var doc = FodsDocument.Load(fodsPath, maxFileSizeBytes);
        return ExportToPng(doc, pngPath, sheetIndex);
    }

    /// <summary>
    /// Export sheet <paramref name="sheetIndex"/> of <paramref name="document"/> to a PNG at <paramref name="pngPath"/>.
    /// </summary>
    public static FodsPngExportResult ExportToPng(FodsDocument document, string pngPath, int sheetIndex = 0)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));
        if (string.IsNullOrWhiteSpace(pngPath))
            throw new ArgumentNullException(nameof(pngPath));

        // Compute dimensions before writing so we can populate result
        var (rows, cols) = GetSheetDimensions(document, sheetIndex);
        byte[] bytes = ExportToPngBytes(document, sheetIndex);
        File.WriteAllBytes(pngPath, bytes);
        int w = cols * (CellPx + BorderPx) + BorderPx;
        int h = rows * (CellPx + BorderPx) + BorderPx;
        return new FodsPngExportResult
        {
            OutputPath = pngPath,
            WidthPx = w,
            HeightPx = h,
            RowsRendered = rows,
            ColsRendered = cols,
        };
    }

    /// <summary>
    /// Export sheet <paramref name="sheetIndex"/> of <paramref name="document"/> to a PNG byte array (no file I/O).
    /// </summary>
    public static byte[] ExportToPngBytes(FodsDocument document, int sheetIndex = 0)
    {
        if (document is null) throw new ArgumentNullException(nameof(document));

        var grid = BuildCellGrid(document, sheetIndex);
        return WritePng(grid);
    }

    // -------------------------------------------------------------------------
    // Internal: grid extraction
    // -------------------------------------------------------------------------

    private static (int Rows, int Cols) GetSheetDimensions(FodsDocument doc, int sheetIndex)
    {
        var sheets = doc.Sheets;
        if (sheetIndex < 0 || sheetIndex >= sheets.Count)
            return (0, 0);
        var sheet = sheets[sheetIndex];
        int rows = sheet.Rows.Count;
        if (rows == 0) return (0, 0);
        int cols = 0;
        foreach (var row in sheet.Rows)
            cols = Math.Max(cols, row.Cells.Count);
        return (rows, cols);
    }

    /// <summary>Returns a bool[rows][cols] grid: true = cell has data.</summary>
    private static bool[][] BuildCellGrid(FodsDocument doc, int sheetIndex)
    {
        var (rows, cols) = GetSheetDimensions(doc, sheetIndex);
        if (rows == 0 || cols == 0)
            return Array.Empty<bool[]>();

        var sheet = doc.Sheets[sheetIndex];
        var grid = new bool[rows][];
        for (int r = 0; r < rows; r++)
        {
            grid[r] = new bool[cols];
            var row = sheet.Rows[r];
            for (int c = 0; c < row.Cells.Count && c < cols; c++)
            {
                var cell = row.Cells[c];
                grid[r][c] = !string.IsNullOrEmpty(cell?.Value);
            }
        }
        return grid;
    }

    // -------------------------------------------------------------------------
    // Internal: PNG writer
    // -------------------------------------------------------------------------

    private static byte[] WritePng(bool[][] grid)
    {
        int rows = grid.Length;
        int cols = rows > 0 ? grid[0].Length : 0;

        // Minimum 1×1 pixel image for empty doc
        int imgW = rows == 0 ? 1 : cols * (CellPx + BorderPx) + BorderPx;
        int imgH = rows == 0 ? 1 : rows * (CellPx + BorderPx) + BorderPx;

        // Build raw scanlines: each row is (filter_byte=0) + (imgW * 3 bytes RGB)
        byte[] pixels = BuildPixelData(grid, imgW, imgH, rows, cols);

        using var ms = new MemoryStream();

        // PNG signature
        ms.Write(new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A });

        // IHDR
        WriteChunk(ms, "IHDR", BuildIhdr(imgW, imgH));

        // IDAT: zlib-compress the filtered scanlines
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
        // b[10]=0 compression, b[11]=0 filter, b[12]=0 interlace
        return b;
    }

    private static byte[] BuildPixelData(bool[][] grid, int imgW, int imgH, int rows, int cols)
    {
        // Each scanline: 1 filter byte + imgW*3 RGB bytes
        byte[] data = new byte[imgH * (1 + imgW * 3)];
        int pos = 0;
        for (int py = 0; py < imgH; py++)
        {
            data[pos++] = 0; // filter type None
            for (int px = 0; px < imgW; px++)
            {
                byte[] color = GetPixelColor(px, py, grid, rows, cols);
                data[pos++] = color[0];
                data[pos++] = color[1];
                data[pos++] = color[2];
            }
        }
        return data;
    }

    private static byte[] GetPixelColor(int px, int py, bool[][] grid, int rows, int cols)
    {
        if (rows == 0) return ColorEmpty;

        int step = CellPx + BorderPx;

        // Check if on a grid line
        if (px % step == 0 || py % step == 0)
            return ColorGrid;

        int col = px / step;
        int row = py / step;

        if (row < rows && col < cols && grid[row][col])
            return ColorFilled;
        return ColorEmpty;
    }

    // -------------------------------------------------------------------------
    // PNG chunk utilities
    // -------------------------------------------------------------------------

    private static void WriteChunk(Stream stream, string type, byte[] data)
    {
        var typeBytes = Encoding.ASCII.GetBytes(type);

        // Length
        var lenBytes = new byte[4];
        WriteUInt32Be(lenBytes, 0, (uint)data.Length);
        stream.Write(lenBytes);

        // Type + Data (for CRC)
        stream.Write(typeBytes);
        stream.Write(data);

        // CRC32 over type + data
        uint crc = Crc32(typeBytes);
        crc = Crc32Continue(crc, data);
        var crcBytes = new byte[4];
        WriteUInt32Be(crcBytes, 0, crc);
        stream.Write(crcBytes);
    }

    private static void WriteUInt32Be(byte[] buf, int offset, uint value)
    {
        buf[offset + 0] = (byte)(value >> 24);
        buf[offset + 1] = (byte)(value >> 16);
        buf[offset + 2] = (byte)(value >> 8);
        buf[offset + 3] = (byte)value;
    }

    // -------------------------------------------------------------------------
    // CRC32 (PNG standard polynomial 0xEDB88320 reflected)
    // -------------------------------------------------------------------------

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
        // crc comes in already partially computed from Crc32(), so we need to work
        // with the internal state (un-finalized)
        uint c = crc ^ 0xFFFFFFFF; // undo finalization
        foreach (byte b in data)
            c = CrcTable[(c ^ b) & 0xFF] ^ (c >> 8);
        return c ^ 0xFFFFFFFF;
    }
}
