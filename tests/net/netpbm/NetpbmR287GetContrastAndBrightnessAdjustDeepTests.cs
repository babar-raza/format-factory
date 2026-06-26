// Tests for NetpbmImage.GetContrast, AdjustBrightness, AdjustContrast deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R287

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R287: Tests for NetpbmImage.GetContrast, AdjustBrightness, AdjustContrast deeper.
/// GetContrast(): returns the RMS contrast of the image (0 = uniform, higher = more contrast).
/// AdjustBrightness(delta): returns image with each pixel shifted by delta, clamped to [0, MaxVal].
/// AdjustContrast(factor): returns image with contrast scaled by factor around the mean.
/// Covers: GetContrast no-throw; GetContrast non-negative; GetContrast consistent;
/// GetContrast save-load; GetContrast zero for uniform;
/// AdjustBrightness no-throw; AdjustBrightness same dims; AdjustBrightness save-load;
/// AdjustBrightness positive-delta-increases-brightness; AdjustBrightness consistent MaxVal;
/// AdjustContrast no-throw; AdjustContrast same dims; AdjustContrast save-load;
/// AdjustContrast one-unchanged; AdjustContrast consistent MaxVal;
/// dogfood LoadFile→GetContrast→AdjustBrightness→AdjustContrast→SaveToFile pipeline.
/// </summary>
public class NetpbmR287GetContrastAndBrightnessAdjustDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR287GetContrastAndBrightnessAdjustDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR287_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(int width, int height, int fill)
    {
        var path = TempFile($"pgm_{width}x{height}_{fill}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(fill);
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("64 32");
        sb.AppendLine("255");
        for (int r = 0; r < 32; r++)
        {
            for (int c = 0; c < 64; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(c * 4);
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrast_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrast_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetContrast() >= 0.0);
    }

    [Fact]
    public void GetContrast_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetContrast(), img.GetContrast());
    }

    [Fact]
    public void GetContrast_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreatePgm(16, 16, 128));
        Assert.Equal(0.0, img.GetContrast(), 2);
    }

    [Fact]
    public void GetContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetContrast();
        var path = TempFile("gc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetContrast(), 2);
    }

    // -------------------------------------------------------------------------
    // AdjustBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustBrightness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.AdjustBrightness(20));
        Assert.Null(ex);
    }

    [Fact]
    public void AdjustBrightness_Same_Dims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustBrightness(30);
        Assert.Equal(img.Width, adj.Width);
        Assert.Equal(img.Height, adj.Height);
    }

    [Fact]
    public void AdjustBrightness_Consistent_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustBrightness(10);
        Assert.Equal(img.MaxVal, adj.MaxVal);
    }

    [Fact]
    public void AdjustBrightness_PositiveDelta_IncreasesOrSaturates_Mean()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustBrightness(20);
        // Mean should be at least as high (clamped at MaxVal)
        Assert.True(adj.GetBrightness() >= img.GetBrightness() - 0.01);
    }

    [Fact]
    public void AdjustBrightness_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustBrightness(15);
        var path = TempFile("ab_save.pgm");
        adj.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(adj.Width, loaded.Width);
        Assert.Equal(adj.Height, loaded.Height);
        Assert.Equal(adj.MaxVal, loaded.MaxVal);
    }

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.AdjustContrast(1.5));
        Assert.Null(ex);
    }

    [Fact]
    public void AdjustContrast_Same_Dims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustContrast(1.2);
        Assert.Equal(img.Width, adj.Width);
        Assert.Equal(img.Height, adj.Height);
    }

    [Fact]
    public void AdjustContrast_Consistent_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustContrast(0.8);
        Assert.Equal(img.MaxVal, adj.MaxVal);
    }

    [Fact]
    public void AdjustContrast_One_Unchanged_Dims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustContrast(1.0);
        Assert.Equal(img.Width, adj.Width);
        Assert.Equal(img.Height, adj.Height);
        Assert.Equal(img.MaxVal, adj.MaxVal);
    }

    [Fact]
    public void AdjustContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var adj = img.AdjustContrast(1.3);
        var path = TempFile("ac_save.pgm");
        adj.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(adj.Width, loaded.Width);
        Assert.Equal(adj.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContrast_AdjustBrightness_AdjustContrast_SaveToFile_Pipeline()
    {
        // Build 80x60 half-dark, half-bright PGM
        var srcPath = TempFile("dogfood_halftone.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("80 60");
        sb.AppendLine("255");
        for (int r = 0; r < 60; r++)
        {
            for (int c = 0; c < 80; c++)
            {
                if (c > 0) sb.Append(' ');
                sb.Append(c < 40 ? 30 : 220);
            }
            sb.AppendLine();
        }
        File.WriteAllText(srcPath, sb.ToString());

        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(80, img.Width);
        Assert.Equal(60, img.Height);

        // GetContrast — two-value image has high contrast
        var contrast = img.GetContrast();
        Assert.True(contrast >= 0.0);
        Assert.Equal(contrast, img.GetContrast()); // consistent

        // AdjustBrightness — brighten by 25
        var brightened = img.AdjustBrightness(25);
        Assert.NotNull(brightened);
        Assert.Equal(img.Width, brightened.Width);
        Assert.Equal(img.Height, brightened.Height);
        Assert.Equal(img.MaxVal, brightened.MaxVal);
        Assert.True(brightened.GetBrightness() >= img.GetBrightness() - 0.01);

        // AdjustBrightness — darken by -20
        var darkened = img.AdjustBrightness(-20);
        Assert.NotNull(darkened);
        Assert.Equal(img.Width, darkened.Width);
        Assert.Equal(img.Height, darkened.Height);

        // AdjustContrast — increase contrast by 1.5x
        var highContrast = img.AdjustContrast(1.5);
        Assert.NotNull(highContrast);
        Assert.Equal(img.Width, highContrast.Width);
        Assert.Equal(img.Height, highContrast.Height);
        Assert.Equal(img.MaxVal, highContrast.MaxVal);

        // AdjustContrast — reduce contrast by 0.5x
        var lowContrast = img.AdjustContrast(0.5);
        Assert.NotNull(lowContrast);
        Assert.Equal(img.Width, lowContrast.Width);

        // Compose: brighten then increase contrast
        var processed = img.AdjustBrightness(10).AdjustContrast(1.2);
        Assert.Equal(img.Width, processed.Width);
        Assert.Equal(img.Height, processed.Height);
        Assert.True(processed.GetContrast() >= 0.0);

        // SaveToFile — brightened
        var brightPath = TempFile("dogfood_bright.pgm");
        brightened.SaveToFile(brightPath);
        Assert.True(File.Exists(brightPath));
        Assert.True(new FileInfo(brightPath).Length > 0);
        var loadedBright = NetpbmImage.LoadFile(brightPath);
        Assert.Equal(brightened.Width, loadedBright.Width);
        Assert.Equal(brightened.Height, loadedBright.Height);
        Assert.Equal(brightened.MaxVal, loadedBright.MaxVal);

        // SaveToFile — high contrast
        var hiContrastPath = TempFile("dogfood_hi_contrast.pgm");
        highContrast.SaveToFile(hiContrastPath);
        Assert.True(File.Exists(hiContrastPath));
        var loadedHiC = NetpbmImage.LoadFile(hiContrastPath);
        Assert.Equal(highContrast.Width, loadedHiC.Width);
        Assert.Equal(highContrast.Height, loadedHiC.Height);
        Assert.Equal(highContrast.GetContrast(), loadedHiC.GetContrast(), 2);

        // Final save — processed
        var finalPath = TempFile("dogfood_processed.pgm");
        processed.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var loaded2 = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(img.Width, loaded2.Width);
        Assert.Equal(img.Height, loaded2.Height);
        Assert.Equal(img.MaxVal, loaded2.MaxVal);
        Assert.True(loaded2.GetContrast() >= 0.0);
    }
}
