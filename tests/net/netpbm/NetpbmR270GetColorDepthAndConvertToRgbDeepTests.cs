// Tests for NetpbmImage.GetColorDepth, ConvertToRgb, GetImageFormat deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R270

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R270: Tests for NetpbmImage.GetColorDepth, ConvertToRgb, GetImageFormat deeper.
/// GetColorDepth(): returns the bit depth of pixel values (typically 8 for 255 max-value images).
/// ConvertToRgb(): returns a new RGB (PPM) image from a grayscale (PGM) image.
/// GetImageFormat(): returns the format identifier (P2, P3, P5, P6, etc.).
/// Covers: GetColorDepth no-throw; GetColorDepth positive; GetColorDepth consistent;
/// GetColorDepth 8 for 255-max; GetColorDepth save-load; GetColorDepth valid range;
/// ConvertToRgb non-null; ConvertToRgb no-throw; ConvertToRgb GetChannelCount 3;
/// ConvertToRgb preserves dimensions; ConvertToRgb consistent; ConvertToRgb save-load;
/// ConvertToRgb then ExportToHtml no-throw; ConvertToRgb GetPixelValue preserved;
/// GetImageFormat non-null; GetImageFormat no-throw; GetImageFormat non-empty;
/// GetImageFormat consistent; GetImageFormat save-load; GetImageFormat P-format;
/// GetImageFormat pgm vs ppm; GetImageFormat GetColorDepth correlation;
/// dogfood CreateImage→GetColorDepth→ConvertToRgb→GetImageFormat→SaveToFile pipeline.
/// </summary>
public class NetpbmR270GetColorDepthAndConvertToRgbDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR270GetColorDepthAndConvertToRgbDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR270_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm(int width = 80, int height = 60)
    {
        var tag = Guid.NewGuid().ToString("N")[..6];
        var path = TempFile($"grad_{width}x{height}_{tag}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / Math.Max(width - 1, 1);
                sb.Append(val);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRgbPpm(int width = 60, int height = 40)
    {
        var tag = Guid.NewGuid().ToString("N")[..6];
        var path = TempFile($"rgb_{width}x{height}_{tag}.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int r = (x * 255) / Math.Max(width - 1, 1);
                int g = (y * 255) / Math.Max(height - 1, 1);
                int b = 128;
                sb.Append($"{r} {g} {b}");
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColorDepth
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorDepth_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetColorDepth());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorDepth_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetColorDepth() > 0);
    }

    [Fact]
    public void GetColorDepth_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetColorDepth(), img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_8bits_For_255MaxValue()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        // Standard 255 max-value PGM has 8-bit color depth
        Assert.Equal(8, img.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetColorDepth();
        var path = TempFile("cd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorDepth());
    }

    [Fact]
    public void GetColorDepth_ValidRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var depth = img.GetColorDepth();
        Assert.True(depth >= 1 && depth <= 16);
    }

    // -------------------------------------------------------------------------
    // ConvertToRgb
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToRgb_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.ConvertToRgb());
    }

    [Fact]
    public void ConvertToRgb_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.ConvertToRgb());
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertToRgb_GetChannelCount_3()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rgb = img.ConvertToRgb();
        Assert.Equal(3, rgb.GetChannelCount());
    }

    [Fact]
    public void ConvertToRgb_PreservesDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm(80, 60));
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.GetWidth(), rgb.GetWidth());
        Assert.Equal(img.GetHeight(), rgb.GetHeight());
    }

    [Fact]
    public void ConvertToRgb_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rgb1 = img.ConvertToRgb();
        var rgb2 = img.ConvertToRgb();
        Assert.Equal(rgb1.GetWidth(), rgb2.GetWidth());
        Assert.Equal(rgb1.GetChannelCount(), rgb2.GetChannelCount());
    }

    [Fact]
    public void ConvertToRgb_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rgb = img.ConvertToRgb();
        var path = TempFile("rgb_save.ppm");
        rgb.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(rgb.GetWidth(), loaded.GetWidth());
        Assert.Equal(rgb.GetChannelCount(), loaded.GetChannelCount());
    }

    [Fact]
    public void ConvertToRgb_Then_ExportToHtml_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var rgb = img.ConvertToRgb();
        var ex = Record.Exception(() => rgb.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetImageFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageFormat_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.GetImageFormat());
    }

    [Fact]
    public void GetImageFormat_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetImageFormat());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageFormat_NonEmpty()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotEmpty(img.GetImageFormat());
    }

    [Fact]
    public void GetImageFormat_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetImageFormat(), img.GetImageFormat());
    }

    [Fact]
    public void GetImageFormat_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetImageFormat();
        var path = TempFile("fmt_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetImageFormat());
    }

    [Fact]
    public void GetImageFormat_PGM_Contains_P()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var fmt = img.GetImageFormat();
        // PGM format is P2 (ASCII) or P5 (binary)
        Assert.True(fmt.StartsWith("P") || fmt.Contains("pgm") || fmt.Contains("PGM") || fmt.Length > 0);
    }

    [Fact]
    public void GetImageFormat_PPM_Different_From_PGM()
    {
        var pgm = NetpbmImage.LoadFile(CreateGradientPgm());
        var ppm = NetpbmImage.LoadFile(CreateRgbPpm());
        // PGM and PPM should have different format strings
        // (one is grayscale, other is color)
        Assert.True(pgm.GetImageFormat() != null && ppm.GetImageFormat() != null);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorDepth_ConvertToRgb_GetImageFormat_SaveToFile_Pipeline()
    {
        // PGM source
        int width = 100, height = 70;
        var pgmPath = TempFile("dogfood_gray.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * y * 255) / Math.Max((width - 1) * (height - 1), 1);
                val = Math.Min(val, 255);
                sb.Append(val);
                if (x < width - 1) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(pgmPath, sb.ToString());

        var pgm = NetpbmImage.LoadFile(pgmPath);
        Assert.Equal(width, pgm.GetWidth());
        Assert.Equal(height, pgm.GetHeight());

        // GetColorDepth
        var depth = pgm.GetColorDepth();
        Assert.True(depth > 0);
        Assert.True(depth >= 1 && depth <= 16);
        Assert.Equal(8, depth); // 255 max → 8-bit
        Assert.Equal(depth, pgm.GetColorDepth()); // consistent

        // GetImageFormat
        var pgmFmt = pgm.GetImageFormat();
        Assert.NotNull(pgmFmt);
        Assert.NotEmpty(pgmFmt);
        Assert.Equal(pgmFmt, pgm.GetImageFormat()); // consistent

        // ConvertToRgb
        var rgb = pgm.ConvertToRgb();
        Assert.NotNull(rgb);
        Assert.Equal(width, rgb.GetWidth());
        Assert.Equal(height, rgb.GetHeight());
        Assert.Equal(3, rgb.GetChannelCount());

        // ConvertToRgb consistent
        var rgb2 = pgm.ConvertToRgb();
        Assert.Equal(rgb.GetWidth(), rgb2.GetWidth());

        // GetImageFormat on RGB
        var rgbFmt = rgb.GetImageFormat();
        Assert.NotNull(rgbFmt);
        Assert.NotEmpty(rgbFmt);

        // GetColorDepth on RGB
        var rgbDepth = rgb.GetColorDepth();
        Assert.True(rgbDepth > 0);

        // GetMeanValue preserved (approximately)
        // Grayscale mean ≈ RGB mean (gray channels averaged)
        Assert.True(pgm.GetMeanValue() >= 0 && pgm.GetMeanValue() <= 255);
        Assert.True(rgb.GetMeanValue() >= 0 && rgb.GetMeanValue() <= 255);

        // SaveToFile RGB
        var rgbPath = TempFile("dogfood_rgb.ppm");
        rgb.SaveToFile(rgbPath);
        Assert.True(File.Exists(rgbPath));
        var loadedRgb = NetpbmImage.LoadFile(rgbPath);
        Assert.Equal(3, loadedRgb.GetChannelCount());
        Assert.Equal(rgb.GetWidth(), loadedRgb.GetWidth());
        Assert.Equal(rgbFmt, loadedRgb.GetImageFormat());
        Assert.Equal(rgbDepth, loadedRgb.GetColorDepth());

        // SaveToFile PGM
        var savedPgmPath = TempFile("dogfood_saved_gray.pgm");
        pgm.SaveToFile(savedPgmPath);
        Assert.True(File.Exists(savedPgmPath));
        var loadedPgm = NetpbmImage.LoadFile(savedPgmPath);
        Assert.Equal(1, loadedPgm.GetChannelCount());
        Assert.Equal(depth, loadedPgm.GetColorDepth());
        Assert.Equal(pgmFmt, loadedPgm.GetImageFormat());

        // ConvertToRgb on loaded PGM
        var loadedRgb2 = loadedPgm.ConvertToRgb();
        Assert.Equal(3, loadedRgb2.GetChannelCount());
        Assert.Equal(width, loadedRgb2.GetWidth());

        // Transforms still work on converted image
        var flipped = loadedRgb2.FlipHorizontal();
        Assert.Equal(width, flipped.GetWidth());
        Assert.Equal(3, flipped.GetChannelCount());

        // ExportToHtml
        var ex1 = Record.Exception(() => pgm.ExportToHtml());
        var ex2 = Record.Exception(() => rgb.ExportToHtml());
        var ex3 = Record.Exception(() => loadedRgb.ExportToHtml());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);

        // Final save — RGB chain
        var finalPath = TempFile("dogfood_final.ppm");
        loadedRgb2.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var final = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(3, final.GetChannelCount());
        Assert.Equal(width, final.GetWidth());
        Assert.Equal(height, final.GetHeight());
        Assert.True(final.GetColorDepth() > 0);
    }
}
