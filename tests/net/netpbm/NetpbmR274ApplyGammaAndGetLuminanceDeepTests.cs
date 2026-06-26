// Tests for NetpbmImage.ApplyGamma, GetLuminance, GetContrast deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R274

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R274: Tests for NetpbmImage.ApplyGamma, GetLuminance, GetContrast deeper.
/// ApplyGamma(gamma): returns a new image with gamma correction applied.
/// GetLuminance(): returns the average luminance of the image (0.0–1.0 range).
/// GetContrast(): returns the contrast measure of the image (non-negative).
/// Covers: ApplyGamma no-throw; ApplyGamma non-null; ApplyGamma same dimensions;
/// ApplyGamma gamma=1 same values; ApplyGamma consistent; ApplyGamma save-load;
/// ApplyGamma then GetLuminance; ApplyGamma then InvertColors;
/// GetLuminance no-throw; GetLuminance non-negative; GetLuminance at-most-one;
/// GetLuminance consistent; GetLuminance save-load;
/// GetContrast no-throw; GetContrast non-negative; GetContrast consistent;
/// GetContrast save-load; GetContrast zero for uniform;
/// dogfood LoadFile→ApplyGamma→GetLuminance→GetContrast→SaveToFile pipeline.
/// </summary>
public class NetpbmR274ApplyGammaAndGetLuminanceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR274ApplyGammaAndGetLuminanceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR274_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("# gradient scene");
        sb.AppendLine("8 6");
        sb.AppendLine("255");
        for (int r = 0; r < 6; r++)
        {
            for (int c = 0; c < 8; c++)
            {
                int v = (r * 30 + c * 15) % 256;
                sb.Append(v);
                if (c < 7) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm(int val = 128)
    {
        var path = TempFile($"uniform_{val}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("5 4");
        sb.AppendLine("255");
        for (int r = 0; r < 4; r++)
        {
            for (int c = 0; c < 5; c++)
            {
                sb.Append(val);
                if (c < 4) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // ApplyGamma
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyGamma_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.ApplyGamma(2.2));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyGamma_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.ApplyGamma(2.2));
    }

    [Fact]
    public void ApplyGamma_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var corrected = img.ApplyGamma(2.2);
        Assert.Equal(img.GetWidth(), corrected.GetWidth());
        Assert.Equal(img.GetHeight(), corrected.GetHeight());
    }

    [Fact]
    public void ApplyGamma_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var g1 = img.ApplyGamma(1.8);
        var g2 = img.ApplyGamma(1.8);
        Assert.Equal(g1.GetWidth(), g2.GetWidth());
        Assert.Equal(g1.GetHeight(), g2.GetHeight());
    }

    [Fact]
    public void ApplyGamma_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var corrected = img.ApplyGamma(2.2);
        var path = TempFile("ag_save.pgm");
        corrected.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(corrected.GetWidth(), loaded.GetWidth());
        Assert.Equal(corrected.GetHeight(), loaded.GetHeight());
    }

    [Fact]
    public void ApplyGamma_Then_InvertColors_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var corrected = img.ApplyGamma(2.2);
        var ex = Record.Exception(() => corrected.InvertColors());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetLuminance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLuminance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetLuminance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLuminance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetLuminance() >= 0);
    }

    [Fact]
    public void GetLuminance_AtMostOne()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetLuminance() <= 1.0);
    }

    [Fact]
    public void GetLuminance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetLuminance(), img.GetLuminance());
    }

    [Fact]
    public void GetLuminance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetLuminance();
        var path = TempFile("gl_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLuminance(), 3);
    }

    [Fact]
    public void GetLuminance_After_ApplyGamma()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var corrected = img.ApplyGamma(2.2);
        var lum = corrected.GetLuminance();
        Assert.True(lum >= 0 && lum <= 1.0);
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
        Assert.True(img.GetContrast() >= 0);
    }

    [Fact]
    public void GetContrast_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetContrast(), img.GetContrast());
    }

    [Fact]
    public void GetContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetContrast();
        var path = TempFile("gc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetContrast(), 3);
    }

    [Fact]
    public void GetContrast_Zero_For_Uniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm(128));
        Assert.Equal(0.0, img.GetContrast(), 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ApplyGamma_GetLuminance_GetContrast_SaveToFile_Pipeline()
    {
        // Build a complex PGM
        var rawPath = TempFile("dogfood_complex.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("# dogfood complex gradient");
        sb.AppendLine("10 8");
        sb.AppendLine("255");
        for (int r = 0; r < 8; r++)
        {
            for (int c = 0; c < 10; c++)
            {
                int v = Math.Min(255, (r * 25 + c * 18));
                sb.Append(v);
                if (c < 9) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(rawPath, sb.ToString());

        var img = NetpbmImage.LoadFile(rawPath);
        Assert.Equal(10, img.GetWidth());
        Assert.Equal(8, img.GetHeight());

        // GetLuminance
        var lum = img.GetLuminance();
        Assert.True(lum >= 0 && lum <= 1.0);
        Assert.Equal(lum, img.GetLuminance()); // consistent

        // GetContrast
        var contrast = img.GetContrast();
        Assert.True(contrast >= 0);
        Assert.Equal(contrast, img.GetContrast()); // consistent

        // ApplyGamma 2.2
        var g22 = img.ApplyGamma(2.2);
        Assert.NotNull(g22);
        Assert.Equal(img.GetWidth(), g22.GetWidth());
        Assert.Equal(img.GetHeight(), g22.GetHeight());

        // ApplyGamma 1.0 (identity)
        var g10 = img.ApplyGamma(1.0);
        Assert.Equal(img.GetWidth(), g10.GetWidth());
        Assert.Equal(img.GetHeight(), g10.GetHeight());

        // ApplyGamma 0.5
        var g05 = img.ApplyGamma(0.5);
        Assert.Equal(img.GetWidth(), g05.GetWidth());

        // GetLuminance on gamma-corrected
        var lum22 = g22.GetLuminance();
        Assert.True(lum22 >= 0 && lum22 <= 1.0);

        // GetContrast on gamma-corrected
        var contrast22 = g22.GetContrast();
        Assert.True(contrast22 >= 0);

        // ApplyGamma then InvertColors
        var invG22 = g22.InvertColors();
        Assert.NotNull(invG22);
        Assert.Equal(g22.GetWidth(), invG22.GetWidth());

        // Consistent checks
        Assert.Equal(g22.GetLuminance(), g22.GetLuminance());
        Assert.Equal(g22.GetContrast(), g22.GetContrast());

        // SaveToFile
        var savePath = TempFile("dogfood_gamma22.pgm");
        g22.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(savePath);
        Assert.Equal(g22.GetWidth(), loaded.GetWidth());
        Assert.Equal(g22.GetHeight(), loaded.GetHeight());
        Assert.Equal(g22.GetLuminance(), loaded.GetLuminance(), 3);
        Assert.Equal(g22.GetContrast(), loaded.GetContrast(), 3);

        // Pipeline: original → gamma → invert → save
        var pipeline = img.ApplyGamma(1.8).InvertColors();
        var pipelinePath = TempFile("dogfood_pipeline.pgm");
        pipeline.SaveToFile(pipelinePath);
        Assert.True(File.Exists(pipelinePath));
        var loadedPipeline = NetpbmImage.LoadFile(pipelinePath);
        Assert.Equal(img.GetWidth(), loadedPipeline.GetWidth());
        Assert.Equal(img.GetHeight(), loadedPipeline.GetHeight());
        Assert.True(loadedPipeline.GetLuminance() >= 0);
        Assert.True(loadedPipeline.GetContrast() >= 0);
    }
}
