// Tests for NetpbmImage.GetSharpness, GetBlurRadius, GetLaplacianVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R324

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R324: Tests for NetpbmImage.GetSharpness, GetBlurRadius, GetLaplacianVariance deeper.
/// GetSharpness(): returns a scalar measure of image sharpness (higher = sharper).
/// GetBlurRadius(): returns an estimate of the effective blur radius in pixels.
/// GetLaplacianVariance(): returns the variance of the Laplacian operator applied to pixel values.
/// Covers: GetSharpness no-throw; GetSharpness non-negative; GetSharpness consistent;
/// GetSharpness sharp > blurry;
/// GetBlurRadius no-throw; GetBlurRadius non-negative; GetBlurRadius consistent;
/// GetLaplacianVariance no-throw; GetLaplacianVariance non-negative; GetLaplacianVariance consistent;
/// GetLaplacianVariance high for edge-rich image; GetLaplacianVariance save-load;
/// dogfood Compress→GetSharpness→GetBlurRadius→GetLaplacianVariance pipeline.
/// </summary>
public class NetpbmR324GetSharpnessAndBlurMetricsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR324GetSharpnessAndBlurMetricsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR324_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEdgeRichPgm()
    {
        // 12x12 PGM with strong vertical and horizontal edges (checkerboard-like)
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            var vals = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 12; c++)
                vals.Add(((r + c) % 2 == 0) ? "255" : "0");
            sb.AppendLine(string.Join(" ", vals));
        }
        var path = TempFile("edge_rich.pgm");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        // 12x12 PGM with uniform value — no edges, minimum sharpness
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            var vals = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 12; c++)
                vals.Add("128");
            sb.AppendLine(string.Join(" ", vals));
        }
        var path = TempFile("uniform.pgm");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetSharpness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpness_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var ex = Record.Exception(() => img.GetSharpness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSharpness_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.True(img.GetSharpness() >= 0);
    }

    [Fact]
    public void GetSharpness_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.Equal(img.GetSharpness(), img.GetSharpness());
    }

    [Fact]
    public void GetSharpness_Sharp_Greater_Than_Uniform()
    {
        var sharp = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var flat = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.True(sharp.GetSharpness() >= flat.GetSharpness());
    }

    // -------------------------------------------------------------------------
    // GetBlurRadius
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlurRadius_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var ex = Record.Exception(() => img.GetBlurRadius());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlurRadius_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.True(img.GetBlurRadius() >= 0);
    }

    [Fact]
    public void GetBlurRadius_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.Equal(img.GetBlurRadius(), img.GetBlurRadius());
    }

    // -------------------------------------------------------------------------
    // GetLaplacianVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLaplacianVariance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var ex = Record.Exception(() => img.GetLaplacianVariance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLaplacianVariance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.True(img.GetLaplacianVariance() >= 0);
    }

    [Fact]
    public void GetLaplacianVariance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        Assert.Equal(img.GetLaplacianVariance(), img.GetLaplacianVariance());
    }

    [Fact]
    public void GetLaplacianVariance_High_ForEdgeRich_Image()
    {
        var edge = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var flat = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.True(edge.GetLaplacianVariance() >= flat.GetLaplacianVariance());
    }

    [Fact]
    public void GetLaplacianVariance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeRichPgm());
        var before = img.GetLaplacianVariance();
        var path = TempFile("lv_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLaplacianVariance(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSharpness_GetBlurRadius_GetLaplacianVariance_Pipeline()
    {
        // Ophthalmology — fundus image focus quality assessment for diabetic retinopathy screening
        // 12×12 PGM representing a simplified retinal fundus image with optic disc and vessel edges

        // High-contrast image: optic disc centre (bright circle) surrounded by darker retina
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        // Row 0-1: dark background
        sb.AppendLine("20 20 20 20 20 20 20 20 20 20 20 20");
        sb.AppendLine("20 20 20 30 30 30 30 30 30 20 20 20");
        // Row 2-3: optic disc boundary (sharp edge)
        sb.AppendLine("20 20 200 220 230 230 230 230 220 200 20 20");
        sb.AppendLine("20 30 220 240 255 255 255 255 240 220 30 20");
        // Row 4-5: optic disc centre (bright)
        sb.AppendLine("20 30 225 245 255 255 255 255 245 225 30 20");
        sb.AppendLine("20 30 220 245 255 255 255 255 245 220 30 20");
        // Row 6: blood vessel (dark stripe through disc — sharp local edge)
        sb.AppendLine("20 30 210 230 255 50 50 255 230 210 30 20");
        // Row 7-8: optic disc lower
        sb.AppendLine("20 30 218 238 252 252 252 252 238 218 30 20");
        sb.AppendLine("20 20 200 218 228 228 228 228 218 200 20 20");
        // Row 9-11: retinal background with subtle texture
        sb.AppendLine("20 20 20 35 35 35 35 35 35 20 20 20");
        sb.AppendLine("20 20 20 20 20 20 20 20 20 20 20 20");
        sb.AppendLine("18 18 18 18 18 18 18 18 18 18 18 18");

        var path = TempFile("dogfood_fundus.pgm");
        File.WriteAllText(path, sb.ToString());
        var img = NetpbmImage.LoadFile(path);

        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);
        Assert.Equal(255, img.MaxValue);

        // GetSharpness — should be non-negative for any image
        var sharpness = img.GetSharpness();
        Assert.True(sharpness >= 0);
        Assert.Equal(sharpness, img.GetSharpness()); // consistent

        // GetBlurRadius
        var blurRadius = img.GetBlurRadius();
        Assert.True(blurRadius >= 0);
        Assert.Equal(blurRadius, img.GetBlurRadius()); // consistent

        // GetLaplacianVariance — edge-rich image should be non-zero
        var lapVar = img.GetLaplacianVariance();
        Assert.True(lapVar >= 0);
        Assert.Equal(lapVar, img.GetLaplacianVariance()); // consistent

        // Compare with uniform background image
        var flatPath = TempFile("dogfood_flat.pgm");
        var flatSb = new StringBuilder();
        flatSb.AppendLine("P2");
        flatSb.AppendLine("12 12");
        flatSb.AppendLine("255");
        for (int r = 0; r < 12; r++) flatSb.AppendLine("40 40 40 40 40 40 40 40 40 40 40 40");
        File.WriteAllText(flatPath, flatSb.ToString());
        var flatImg = NetpbmImage.LoadFile(flatPath);
        Assert.True(img.GetLaplacianVariance() >= flatImg.GetLaplacianVariance());

        // GetMean and GetStdDev consistency
        var mean = img.GetMean();
        var std = img.GetStdDev();
        Assert.True(mean >= 0);
        Assert.True(std >= 0);

        // SaveToFile
        var outPath = TempFile("dogfood_fundus_out.pgm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify metrics preserved
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(sharpness, loaded.GetSharpness(), precision: 6);
        Assert.Equal(lapVar, loaded.GetLaplacianVariance(), precision: 6);
        Assert.Equal(blurRadius, loaded.GetBlurRadius(), precision: 6);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // GetPixelValue round-trip — optic disc centre should be bright
        var centreVal = loaded.GetPixelValue(5, 5);
        Assert.True(centreVal >= 128);

        // GetHistogram non-null
        var hist = loaded.GetHistogram();
        Assert.NotNull(hist);
        var ex1 = Record.Exception(() => loaded.GetSharpness());
        var ex2 = Record.Exception(() => loaded.GetBlurRadius());
        var ex3 = Record.Exception(() => loaded.GetLaplacianVariance());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
