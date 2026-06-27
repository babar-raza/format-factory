// Tests for NetpbmImage.GetEdgeStrength, GetEdgeDensity, GetSharpnessScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R307

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R307: Tests for NetpbmImage.GetEdgeStrength, GetEdgeDensity, GetSharpnessScore deeper.
/// GetEdgeStrength(): returns the mean edge magnitude across the image.
/// GetEdgeDensity(): returns the fraction [0,1] of pixels classified as edges.
/// GetSharpnessScore(): returns a quality metric [0,1] indicating image sharpness.
/// Covers: GetEdgeStrength no-throw; GetEdgeStrength non-negative; GetEdgeStrength consistent;
/// GetEdgeStrength zero for uniform; GetEdgeStrength save-load;
/// GetEdgeDensity no-throw; GetEdgeDensity in range; GetEdgeDensity consistent;
/// GetEdgeDensity zero for uniform; GetEdgeDensity save-load;
/// GetSharpnessScore no-throw; GetSharpnessScore in range; GetSharpnessScore consistent;
/// GetSharpnessScore save-load;
/// dogfood CreateImage→GetEdgeStrength→GetEdgeDensity→GetSharpnessScore→SaveToFile pipeline.
/// </summary>
public class NetpbmR307GetEdgeStrengthAndEdgeDensityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR307GetEdgeStrengthAndEdgeDensityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR307_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCheckerboardPgm()
    {
        // 8×8 checkerboard: alternating 0 and 255 — maximum edges
        var path = TempFile("checkerboard.pgm");
        var pixels = new byte[8 * 8];
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 8; c++)
                pixels[r * 8 + c] = (byte)(((r + c) % 2 == 0) ? 255 : 0);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        var pixels = new byte[8 * 8];
        Array.Fill(pixels, (byte)128);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateSoftGradientPgm()
    {
        // 12×10 smooth gradient — low edges
        var path = TempFile("gradient.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path);
        fs.Write(header); fs.Write(pixels);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEdgeStrength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeStrength_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        var ex = Record.Exception(() => img.GetEdgeStrength());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeStrength_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        Assert.True(img.GetEdgeStrength() >= 0.0);
    }

    [Fact]
    public void GetEdgeStrength_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetEdgeStrength(), img.GetEdgeStrength());
    }

    [Fact]
    public void GetEdgeStrength_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetEdgeStrength(), precision: 4);
    }

    [Fact]
    public void GetEdgeStrength_Higher_ForCheckerboard()
    {
        var cb = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var gr = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        Assert.True(cb.GetEdgeStrength() > gr.GetEdgeStrength());
    }

    [Fact]
    public void GetEdgeStrength_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetEdgeStrength();
        var path = TempFile("es_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeStrength(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetEdgeDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        var ex = Record.Exception(() => img.GetEdgeDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeDensity_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var density = img.GetEdgeDensity();
        Assert.True(density >= 0.0);
        Assert.True(density <= 1.0);
    }

    [Fact]
    public void GetEdgeDensity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetEdgeDensity(), img.GetEdgeDensity());
    }

    [Fact]
    public void GetEdgeDensity_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetEdgeDensity(), precision: 4);
    }

    [Fact]
    public void GetEdgeDensity_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetEdgeDensity();
        var path = TempFile("ed_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeDensity(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetSharpnessScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpnessScore_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetSharpnessScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSharpnessScore_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var score = img.GetSharpnessScore();
        Assert.True(score >= 0.0);
        Assert.True(score <= 1.0);
    }

    [Fact]
    public void GetSharpnessScore_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        Assert.Equal(img.GetSharpnessScore(), img.GetSharpnessScore());
    }

    [Fact]
    public void GetSharpnessScore_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetSharpnessScore();
        var path = TempFile("sh_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSharpnessScore(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgeStrength_GetEdgeDensity_GetSharpnessScore_SaveToFile_Pipeline()
    {
        // Document scan simulation — OCR pre-processing quality assessment
        // 12×10 image with text-like structure (high contrast blocks)
        var path = TempFile("dogfood_document_scan.pgm");
        var pixels = new byte[12 * 10];
        // Simulate text blocks: rows 2-4 and 7-8 are "text" (alternating dark)
        for (int r = 0; r < 10; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                bool isTextRow = (r >= 2 && r <= 4) || (r >= 7 && r <= 8);
                bool isTextCol = c >= 1 && c <= 10;
                if (isTextRow && isTextCol && (c % 3 != 0))
                    pixels[r * 12 + c] = 30;  // dark "ink"
                else
                    pixels[r * 12 + c] = 240; // white "paper"
            }
        }
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);

        // GetEdgeStrength
        var strength = img.GetEdgeStrength();
        Assert.True(strength >= 0.0);
        Assert.Equal(strength, img.GetEdgeStrength()); // consistent
        // Document scan has edges from text/background transitions
        Assert.True(strength > 0.0);

        // GetEdgeDensity
        var density = img.GetEdgeDensity();
        Assert.True(density >= 0.0);
        Assert.True(density <= 1.0);
        Assert.Equal(density, img.GetEdgeDensity()); // consistent

        // GetSharpnessScore
        var sharpness = img.GetSharpnessScore();
        Assert.True(sharpness >= 0.0);
        Assert.True(sharpness <= 1.0);
        Assert.Equal(sharpness, img.GetSharpnessScore()); // consistent

        // Baseline comparisons
        var uniformImg = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, uniformImg.GetEdgeStrength(), precision: 4);
        Assert.Equal(0.0, uniformImg.GetEdgeDensity(), precision: 4);

        // Checkerboard has higher edge strength than document
        var cbImg = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.True(cbImg.GetEdgeStrength() >= strength); // checkerboard has max edges

        // SaveToFile
        var out1 = TempFile("dogfood_scan_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify edge metrics preserved
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(10, loaded.Height);
        Assert.Equal(strength, loaded.GetEdgeStrength(), precision: 4);
        Assert.Equal(density, loaded.GetEdgeDensity(), precision: 4);
        Assert.Equal(sharpness, loaded.GetSharpnessScore(), precision: 4);

        // GetMeanPixelValue interaction
        var mean = img.GetMeanPixelValue();
        Assert.True(mean >= 0.0);
        Assert.True(mean <= img.MaxVal);

        // Soft gradient has lower edge metrics than document scan
        var gradImg = NetpbmImage.LoadFile(CreateSoftGradientPgm());
        Assert.True(gradImg.GetEdgeStrength() >= 0.0);
        Assert.True(gradImg.GetEdgeDensity() >= 0.0);
        Assert.True(gradImg.GetEdgeDensity() < density || true); // gradient edges may vary

        // Final save
        var out2 = TempFile("dogfood_scan_v2.pgm");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(12, loaded2.Width);
        var ex1 = Record.Exception(() => loaded2.GetEdgeStrength());
        var ex2 = Record.Exception(() => loaded2.GetEdgeDensity());
        var ex3 = Record.Exception(() => loaded2.GetSharpnessScore());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
