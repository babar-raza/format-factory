// Tests for NetpbmImage.GetTextureFeature, GetGaborResponse, GetGLCMContrast deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R331

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R331: Tests for NetpbmImage.GetTextureFeature, GetGaborResponse, GetGLCMContrast deeper.
/// GetTextureFeature(featureName): returns a scalar texture descriptor (e.g. energy, homogeneity).
/// GetGaborResponse(frequency, orientation): returns the mean Gabor filter response magnitude.
/// GetGLCMContrast(): returns the GLCM contrast measure for adjacent pixel pairs.
/// Covers: GetTextureFeature no-throw; GetTextureFeature non-negative; GetTextureFeature consistent;
/// GetTextureFeature energy in [0,1] for uniform image;
/// GetGaborResponse no-throw; GetGaborResponse non-negative; GetGaborResponse consistent;
/// GetGaborResponse higher for periodic than uniform;
/// GetGLCMContrast no-throw; GetGLCMContrast non-negative; GetGLCMContrast consistent;
/// GetGLCMContrast zero for constant image; GetGLCMContrast save-load;
/// dogfood CreateImage→GetTextureFeature→GetGaborResponse→GetGLCMContrast pipeline.
/// </summary>
public class NetpbmR331GetTextureFeatureAndGaborResponseDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR331GetTextureFeatureAndGaborResponseDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR331_" + Guid.NewGuid().ToString("N"));
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
        // 12x12 PGM with horizontal gradient
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append((c * 21).ToString() + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append("128 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreatePeriodicPgm()
    {
        // Alternating stripes — periodic texture
        var path = TempFile("periodic.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append((c % 2 == 0 ? 0 : 255).ToString() + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantPgm()
    {
        var path = TempFile("constant.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append("200 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTextureFeature
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextureFeature_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetTextureFeature("energy"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextureFeature_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetTextureFeature("energy") >= 0);
    }

    [Fact]
    public void GetTextureFeature_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetTextureFeature("homogeneity"), img.GetTextureFeature("homogeneity"));
    }

    [Fact]
    public void GetTextureFeature_Energy_Uniform_In_Range()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        var energy = img.GetTextureFeature("energy");
        Assert.True(energy >= 0 && energy <= 1.0);
    }

    // -------------------------------------------------------------------------
    // GetGaborResponse
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGaborResponse_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetGaborResponse(0.1, 0.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGaborResponse_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetGaborResponse(0.1, 0.0) >= 0);
    }

    [Fact]
    public void GetGaborResponse_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetGaborResponse(0.2, Math.PI / 4), img.GetGaborResponse(0.2, Math.PI / 4));
    }

    [Fact]
    public void GetGaborResponse_Higher_For_Periodic_Than_Uniform()
    {
        var periodic = NetpbmImage.LoadFile(CreatePeriodicPgm());
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        // Periodic image should produce >= Gabor response than uniform
        var respPeriodic = periodic.GetGaborResponse(0.5, 0.0);
        var respUniform = uniform.GetGaborResponse(0.5, 0.0);
        Assert.True(respPeriodic >= respUniform);
    }

    // -------------------------------------------------------------------------
    // GetGLCMContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGLCMContrast_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetGLCMContrast());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGLCMContrast_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetGLCMContrast() >= 0);
    }

    [Fact]
    public void GetGLCMContrast_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetGLCMContrast(), img.GetGLCMContrast());
    }

    [Fact]
    public void GetGLCMContrast_Zero_For_Constant_Image()
    {
        var img = NetpbmImage.LoadFile(CreateConstantPgm());
        Assert.Equal(0.0, img.GetGLCMContrast(), precision: 6);
    }

    [Fact]
    public void GetGLCMContrast_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetGLCMContrast();
        var path = TempFile("glcm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGLCMContrast(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTextureFeature_GetGaborResponse_GetGLCMContrast_Pipeline()
    {
        // Remote sensing — synthetic aperture radar (SAR) texture analysis for land-use classification
        // Different texture regions: smooth water, rough forest, urban, agricultural
        var path = TempFile("sar_texture.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        var rng = new Random(20240201);
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                int val;
                if (r < 4 && c < 4)
                    // Water region — low backscatter, smooth
                    val = 20 + rng.Next(0, 10);
                else if (r < 4 && c >= 8)
                    // Forest — high backscatter, rough texture
                    val = 150 + rng.Next(-30, 50);
                else if (r >= 8 && c < 4)
                    // Urban — very high backscatter, geometric patterns
                    val = rng.Next(0, 2) == 0 ? 240 : 10;
                else
                    // Agricultural — medium, periodic rows
                    val = 80 + (c % 3 == 0 ? 50 : 0) + rng.Next(-10, 20);
                sb.Append(Math.Clamp(val, 0, 255).ToString() + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);

        // GetTextureFeature — energy
        var energy = img.GetTextureFeature("energy");
        Assert.True(energy >= 0);
        Assert.Equal(energy, img.GetTextureFeature("energy")); // consistent

        // GetTextureFeature — homogeneity
        var homog = img.GetTextureFeature("homogeneity");
        Assert.True(homog >= 0);

        // GetGaborResponse — horizontal frequency
        var gaborH = img.GetGaborResponse(0.2, 0.0);
        Assert.True(gaborH >= 0);
        Assert.Equal(gaborH, img.GetGaborResponse(0.2, 0.0)); // consistent

        // GetGaborResponse — diagonal frequency
        var gaborD = img.GetGaborResponse(0.2, Math.PI / 4);
        Assert.True(gaborD >= 0);

        // GetGLCMContrast
        var contrast = img.GetGLCMContrast();
        Assert.True(contrast >= 0);
        Assert.Equal(contrast, img.GetGLCMContrast()); // consistent

        // Uniform (water-like) reference
        var waterPath = TempFile("water.pgm");
        var wSb = new System.Text.StringBuilder();
        wSb.AppendLine("P2"); wSb.AppendLine("12 12"); wSb.AppendLine("255");
        for (int r = 0; r < 12; r++) { for (int c = 0; c < 12; c++) wSb.Append("25 "); wSb.AppendLine(); }
        File.WriteAllText(waterPath, wSb.ToString());
        var water = NetpbmImage.LoadFile(waterPath);
        Assert.Equal(0.0, water.GetGLCMContrast(), precision: 6);

        // SaveToFile
        var outPath = TempFile("sar_texture_out.pgm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(energy, loaded.GetTextureFeature("energy"));
        Assert.Equal(contrast, loaded.GetGLCMContrast(), precision: 6);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // Additional metrics
        var mean = img.GetMean();
        Assert.True(mean > 0);
        var stddev = img.GetStdDev();
        Assert.True(stddev >= 0);
    }
}
