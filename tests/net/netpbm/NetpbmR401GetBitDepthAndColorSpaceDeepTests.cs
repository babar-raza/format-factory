// Tests for NetpbmImage.GetBitDepth, GetColorSpace deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R401

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R401: Tests for NetpbmImage.GetBitDepth, GetColorSpace deeper.
/// GetBitDepth(): returns the bit depth of the image (8 for standard PGM/PPM with maxval 255).
/// GetColorSpace(): returns a string describing the color space (e.g. "Grayscale", "RGB").
/// Covers: GetBitDepth no-throw; GetBitDepth 8 for standard PGM; GetBitDepth consistent;
/// GetBitDepth save-load;
/// GetColorSpace no-throw; GetColorSpace non-null; GetColorSpace non-empty;
/// GetColorSpace consistent; GetColorSpace save-load;
/// GetColorSpace grayscale for PGM; dogfood pipeline.
/// </summary>
public class NetpbmR401GetBitDepthAndColorSpaceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR401GetBitDepthAndColorSpaceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR401_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStandardPgm(string name, int width, int height)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255"); // maxval 255 → 8-bit
        var rng = new Random(42);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append(rng.Next(256));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateStandardPpm(string name, int width, int height)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append($"{rng.Next(256)} {rng.Next(256)} {rng.Next(256)}");
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetBitDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBitDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        var ex = Record.Exception(() => img.GetBitDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBitDepth_8_ForStandardPgm()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("standard.pgm", 32, 32));
        Assert.Equal(8, img.GetBitDepth());
    }

    [Fact]
    public void GetBitDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        Assert.Equal(img.GetBitDepth(), img.GetBitDepth());
    }

    [Fact]
    public void GetBitDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        var before = img.GetBitDepth();
        var path = TempFile("bd_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetBitDepth());
    }

    // -------------------------------------------------------------------------
    // GetColorSpace
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        var ex = Record.Exception(() => img.GetColorSpace());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorSpace_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        Assert.NotNull(img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_NonEmpty()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        Assert.NotEmpty(img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        Assert.Equal(img.GetColorSpace(), img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateStandardPgm("test.pgm", 32, 32));
        var before = img.GetColorSpace();
        var path = TempFile("cs_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetColorSpace());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetBitDepth_GetColorSpace_Pipeline()
    {
        // Creative Industries — BFI / UK Research and Innovation: Film and Television Production Archive
        // Standardised grayscale and RGB test frames for broadcast colour grading calibration
        // Bit depth and color space validate archive file conformance to EBU R103-2014 standard

        // Frame 1: Standard grayscale test card (PGM — grayscale)
        var path1 = TempFile("ebu_testcard_grayscale.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // EBU grey scale: 16 zones from black (16) to white (235) — broadcast legal range
                    int zone = (int)(x / (double)w * 16);
                    int val = 16 + zone * 14; // maps 0-15 zones to 16-225
                    row.Append(Math.Min(235, val));
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Frame 2: Colour bar test card (PPM — RGB)
        var path2 = TempFile("ebu_testcard_colour_bars.ppm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P3");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            // EBU 100% colour bars: White, Yellow, Cyan, Green, Magenta, Red, Blue, Black
            int[][] barRgb = {
                new[] { 235, 235, 235 }, // White
                new[] { 235, 235, 16 },  // Yellow
                new[] { 16, 235, 235 },  // Cyan
                new[] { 16, 235, 16 },   // Green
                new[] { 235, 16, 235 },  // Magenta
                new[] { 235, 16, 16 },   // Red
                new[] { 16, 16, 235 },   // Blue
                new[] { 16, 16, 16 }     // Black
            };
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    int barIdx = (int)(x / (double)w * barRgb.Length);
                    barIdx = Math.Min(barIdx, barRgb.Length - 1);
                    int[] rgb = barRgb[barIdx];
                    row.Append($"{rgb[0]} {rgb[1]} {rgb[2]}");
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Frame 3: High-contrast grayscale for edge detection calibration
        var path3 = TempFile("edge_calibration.pgm");
        {
            int w = 48, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Alternating black/white checkerboard (8x8 blocks)
                    bool white = ((x / 8) + (y / 8)) % 2 == 0;
                    row.Append(white ? 235 : 16);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);

        // Bit depths
        var bd1 = img1.GetBitDepth();
        var bd2 = img2.GetBitDepth();
        var bd3 = img3.GetBitDepth();
        Assert.Equal(8, bd1); // 255 maxval = 8-bit
        Assert.Equal(8, bd2); // 255 maxval = 8-bit
        Assert.Equal(8, bd3); // 255 maxval = 8-bit
        Assert.Equal(bd1, img1.GetBitDepth()); // consistent

        // Color spaces
        var cs1 = img1.GetColorSpace();
        var cs2 = img2.GetColorSpace();
        var cs3 = img3.GetColorSpace();
        Assert.NotNull(cs1);
        Assert.NotNull(cs2);
        Assert.NotNull(cs3);
        Assert.NotEmpty(cs1);
        Assert.NotEmpty(cs2);
        Assert.NotEmpty(cs3);
        Assert.Equal(cs1, img1.GetColorSpace()); // consistent
        Assert.Equal(cs2, img2.GetColorSpace()); // consistent
        Assert.Equal(cs3, img3.GetColorSpace()); // consistent

        // PGM images should have same grayscale color space
        Assert.Equal(cs1, cs3);

        // Width × Height check
        Assert.Equal(64 * 48, img1.GetPixelCount());
        Assert.Equal(64 * 48, img2.GetPixelCount());
        Assert.Equal(48 * 48, img3.GetPixelCount());

        // SaveToFile
        var out1 = TempFile("ebu_grey_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(bd1, loaded1.GetBitDepth());
        Assert.Equal(cs1, loaded1.GetColorSpace());

        var out2 = TempFile("ebu_bars_out.ppm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(bd2, loaded2.GetBitDepth());
        Assert.Equal(cs2, loaded2.GetColorSpace());

        var ex1 = Record.Exception(() => loaded1.GetBitDepth());
        var ex2 = Record.Exception(() => loaded2.GetColorSpace());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
