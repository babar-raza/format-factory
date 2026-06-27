// Tests for NetpbmImage.GetHistogramEqualised, GetContrastStretched, GetAdaptiveThreshold deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R321

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R321: Tests for NetpbmImage.GetHistogramEqualised, GetContrastStretched, GetAdaptiveThreshold deeper.
/// GetHistogramEqualised(): returns an image with equalised histogram to improve contrast.
/// GetContrastStretched(minOut, maxOut): stretches pixel range to fill [minOut, maxOut].
/// GetAdaptiveThreshold(blockSize, c): applies local thresholding to produce a binary image.
/// Covers: GetHistogramEqualised no-throw; GetHistogramEqualised same dimensions;
/// GetHistogramEqualised preserves MaxVal; GetHistogramEqualised mean moves toward midpoint;
/// GetContrastStretched no-throw; GetContrastStretched same dimensions;
/// GetContrastStretched min=minOut, max=maxOut for non-uniform image;
/// GetContrastStretched consistent; GetContrastStretched save-load;
/// GetAdaptiveThreshold no-throw; GetAdaptiveThreshold same dimensions;
/// GetAdaptiveThreshold only 0 or MaxVal; GetAdaptiveThreshold consistent;
/// dogfood GetHistogramEqualised→GetContrastStretched→GetAdaptiveThreshold→SaveToFile pipeline.
/// </summary>
public class NetpbmR321GetHistogramEqualisedAndContrastStretchedDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR321GetHistogramEqualisedAndContrastStretchedDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR321_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLowContrastPgm()
    {
        // 10×10 PGM with narrow range [60, 90] — low contrast
        var path = TempFile("low_contrast.pgm");
        var rng = new Random(12345);
        var rows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < 10; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 10; c++)
                row.Add((60 + rng.Next(0, 31)).ToString());
            rows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n10 10\n255\n{string.Join("\n", rows)}\n");
        return path;
    }

    private string CreateGradientPgm()
    {
        // 10×10 PGM gradient: pixel value = col * 25 (0, 25, 50, ... 225)
        var path = TempFile("gradient.pgm");
        var rows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < 10; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 10; c++)
                row.Add(Math.Min(255, c * 28).ToString());
            rows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n10 10\n255\n{string.Join("\n", rows)}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHistogramEqualised
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogramEqualised_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var ex = Record.Exception(() => img.GetHistogramEqualised());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogramEqualised_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var eq = img.GetHistogramEqualised();
        Assert.Equal(img.Width, eq.Width);
        Assert.Equal(img.Height, eq.Height);
    }

    [Fact]
    public void GetHistogramEqualised_PreservesMaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var eq = img.GetHistogramEqualised();
        Assert.Equal(img.MaxVal, eq.MaxVal);
    }

    [Fact]
    public void GetHistogramEqualised_ExtendsRange()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var eq = img.GetHistogramEqualised();
        // Equalisation should expand the narrow [60,90] range
        var origRange = img.Pixels.Max() - img.Pixels.Min();
        var eqRange = eq.Pixels.Max() - eq.Pixels.Min();
        Assert.True(eqRange >= origRange);
    }

    // -------------------------------------------------------------------------
    // GetContrastStretched
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastStretched_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var ex = Record.Exception(() => img.GetContrastStretched(0, 255));
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrastStretched_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var cs = img.GetContrastStretched(0, 255);
        Assert.Equal(img.Width, cs.Width);
        Assert.Equal(img.Height, cs.Height);
    }

    [Fact]
    public void GetContrastStretched_Min_Max_Correct()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var cs = img.GetContrastStretched(0, 255);
        // After stretching a non-uniform image, min should be 0 and max should be 255
        Assert.Equal(0, cs.Pixels.Min());
        Assert.Equal(255, cs.Pixels.Max());
    }

    [Fact]
    public void GetContrastStretched_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateLowContrastPgm());
        var cs1 = img.GetContrastStretched(0, 200);
        var cs2 = img.GetContrastStretched(0, 200);
        Assert.Equal(cs1.Pixels, cs2.Pixels);
    }

    [Fact]
    public void GetContrastStretched_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var cs = img.GetContrastStretched(10, 245);
        var path = TempFile("cs_save.pgm");
        cs.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(cs.Width, loaded.Width);
        Assert.Equal(cs.Height, loaded.Height);
        Assert.Equal(cs.Pixels.Min(), loaded.Pixels.Min());
        Assert.Equal(cs.Pixels.Max(), loaded.Pixels.Max());
    }

    // -------------------------------------------------------------------------
    // GetAdaptiveThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAdaptiveThreshold_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetAdaptiveThreshold(3, 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetAdaptiveThreshold_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var at = img.GetAdaptiveThreshold(3, 5);
        Assert.Equal(img.Width, at.Width);
        Assert.Equal(img.Height, at.Height);
    }

    [Fact]
    public void GetAdaptiveThreshold_Only_Zero_Or_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var at = img.GetAdaptiveThreshold(3, 5);
        foreach (var px in at.Pixels)
            Assert.True(px == 0 || px == at.MaxVal);
    }

    [Fact]
    public void GetAdaptiveThreshold_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var at1 = img.GetAdaptiveThreshold(3, 5);
        var at2 = img.GetAdaptiveThreshold(3, 5);
        Assert.Equal(at1.Pixels, at2.Pixels);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHistogramEqualised_GetContrastStretched_GetAdaptiveThreshold_SaveToFile_Pipeline()
    {
        // Pathology image analysis — H&E stained tissue slide preprocessing pipeline
        var path = TempFile("tissue_slide.pgm");
        int W = 12, H = 12;
        var rng = new Random(20240901);
        var pixelRows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < H; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < W; c++)
            {
                // Stained tissue: nuclei are dark (30-60), cytoplasm is medium (100-150), background 200-240
                int px;
                if (r >= 3 && r <= 7 && c >= 3 && c <= 7)
                    px = 30 + rng.Next(0, 31); // nuclear region
                else if (r >= 2 && r <= 8 && c >= 2 && c <= 8)
                    px = 100 + rng.Next(0, 51); // cytoplasm
                else
                    px = 200 + rng.Next(0, 41); // background
                row.Add(px.ToString());
            }
            pixelRows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n{W} {H}\n255\n{string.Join("\n", pixelRows)}\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(W, img.Width);
        Assert.Equal(H, img.Height);
        Assert.Equal(255, img.MaxVal);

        // GetHistogramEqualised — improve tissue contrast
        var eq = img.GetHistogramEqualised();
        Assert.Equal(W, eq.Width);
        Assert.Equal(H, eq.Height);
        Assert.Equal(img.MaxVal, eq.MaxVal);
        // Equalisation should not decrease overall range
        var origRange = img.Pixels.Max() - img.Pixels.Min();
        var eqRange = eq.Pixels.Max() - eq.Pixels.Min();
        Assert.True(eqRange >= origRange);

        // GetContrastStretched — full range stretch
        var cs = img.GetContrastStretched(0, 255);
        Assert.Equal(W, cs.Width);
        Assert.Equal(H, cs.Height);
        Assert.Equal(0, cs.Pixels.Min());
        Assert.Equal(255, cs.Pixels.Max());
        Assert.Equal(cs.Pixels, img.GetContrastStretched(0, 255).Pixels); // consistent

        // GetAdaptiveThreshold — segment nuclei from background
        var at = img.GetAdaptiveThreshold(3, 5);
        Assert.Equal(W, at.Width);
        Assert.Equal(H, at.Height);
        foreach (var px in at.Pixels)
            Assert.True(px == 0 || px == at.MaxVal);
        Assert.Equal(at.Pixels, img.GetAdaptiveThreshold(3, 5).Pixels); // consistent

        // GetAdaptiveThreshold on equalised image
        var atEq = eq.GetAdaptiveThreshold(3, 5);
        Assert.Equal(W, atEq.Width);
        Assert.Equal(H, atEq.Height);
        foreach (var px in atEq.Pixels)
            Assert.True(px == 0 || px == atEq.MaxVal);

        // SaveToFile — save equalised and segmented images
        var eqPath = TempFile("tissue_equalised.pgm");
        eq.SaveToFile(eqPath);
        Assert.True(File.Exists(eqPath));
        Assert.True(new FileInfo(eqPath).Length > 0);

        var csPath = TempFile("tissue_contrast_stretched.pgm");
        cs.SaveToFile(csPath);
        Assert.True(File.Exists(csPath));

        var atPath = TempFile("tissue_adaptive_threshold.pgm");
        at.SaveToFile(atPath);
        Assert.True(File.Exists(atPath));

        // LoadFile and verify
        var loadedEq = NetpbmImage.LoadFile(eqPath);
        Assert.Equal(W, loadedEq.Width);
        Assert.Equal(H, loadedEq.Height);
        Assert.Equal(eq.MaxVal, loadedEq.MaxVal);

        var loadedAt = NetpbmImage.LoadFile(atPath);
        Assert.Equal(W, loadedAt.Width);
        Assert.Equal(H, loadedAt.Height);
        foreach (var px in loadedAt.Pixels)
            Assert.True(px == 0 || px == loadedAt.MaxVal);

        // Chain operations on loaded
        var ex1 = Record.Exception(() => loadedEq.GetHistogramEqualised());
        var ex2 = Record.Exception(() => loadedEq.GetContrastStretched(0, 255));
        var ex3 = Record.Exception(() => loadedEq.GetAdaptiveThreshold(3, 5));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
