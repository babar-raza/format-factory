// Tests for NetpbmImage.AdjustContrast, ApplySepia, EqualizeHistogram deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R209

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R209: Tests for NetpbmImage.AdjustContrast, ApplySepia, EqualizeHistogram deeper coverage.
/// AdjustContrast(factor): returns image with contrast scaled by factor.
/// ApplySepia(): returns image with sepia tone effect.
/// EqualizeHistogram(): returns image with equalized histogram.
/// Covers: AdjustContrast non-null; AdjustContrast preserves dimensions;
/// AdjustContrast factor 1.0 preserves dimensions; AdjustContrast factor 2.0 non-null;
/// AdjustContrast factor 0.5 non-null;
/// ApplySepia non-null; ApplySepia preserves dimensions; ApplySepia pixel count preserved;
/// ApplySepia on black canvas non-null;
/// EqualizeHistogram non-null; EqualizeHistogram preserves dimensions;
/// EqualizeHistogram pixel count preserved; EqualizeHistogram on uniform canvas non-null;
/// dogfood CreateCanvas->AdjustContrast->ApplySepia->EqualizeHistogram->SaveToFile->Verify pipeline.
/// </summary>
public class NetpbmR209AdjustContrastAndSepiaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR209AdjustContrastAndSepiaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR209_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.AdjustContrast(1.5));
    }

    [Fact]
    public void AdjustContrast_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.AdjustContrast(1.5);
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void AdjustContrast_FactorOne_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var result = img.AdjustContrast(1.0);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void AdjustContrast_FactorTwo_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 64);
        Assert.NotNull(img.AdjustContrast(2.0));
    }

    [Fact]
    public void AdjustContrast_FactorHalf_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        Assert.NotNull(img.AdjustContrast(0.5));
    }

    [Fact]
    public void AdjustContrast_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(4, 6, 100);
        var result = img.AdjustContrast(1.2);
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void AdjustContrast_ChainedCalls_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        var result = img.AdjustContrast(1.5).AdjustContrast(0.8);
        Assert.NotNull(result);
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    // -------------------------------------------------------------------------
    // ApplySepia
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySepia_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        Assert.NotNull(img.ApplySepia());
    }

    [Fact]
    public void ApplySepia_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 100);
        var result = img.ApplySepia();
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ApplySepia_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 128);
        var result = img.ApplySepia();
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void ApplySepia_OnBlackCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 0);
        Assert.NotNull(img.ApplySepia());
    }

    [Fact]
    public void ApplySepia_OnWhiteCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 255);
        Assert.NotNull(img.ApplySepia());
    }

    [Fact]
    public void ApplySepia_ThenAdjustContrast_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 128);
        var result = img.ApplySepia().AdjustContrast(1.2);
        Assert.NotNull(result);
    }

    // -------------------------------------------------------------------------
    // EqualizeHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void EqualizeHistogram_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 100);
        Assert.NotNull(img.EqualizeHistogram());
    }

    [Fact]
    public void EqualizeHistogram_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 8, 128);
        var result = img.EqualizeHistogram();
        Assert.Equal(6, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void EqualizeHistogram_PixelCount_Preserved()
    {
        var img = NetpbmImage.CreateCanvas(5, 5, 100);
        var result = img.EqualizeHistogram();
        Assert.Equal(img.Width * img.Height, result.Width * result.Height);
    }

    [Fact]
    public void EqualizeHistogram_OnUniformCanvas_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        Assert.NotNull(img.EqualizeHistogram());
    }

    [Fact]
    public void EqualizeHistogram_AfterDrawLine_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 50);
        var withLine = img.DrawLine(0, 4, 7, 4, 200);
        var equalized = withLine.EqualizeHistogram();
        Assert.NotNull(equalized);
        Assert.Equal(8, equalized.Width);
        Assert.Equal(8, equalized.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_AdjustContrast_ApplySepia_EqualizeHistogram_SaveToFile_Verify_Pipeline()
    {
        // Create canvas
        var canvas = NetpbmImage.CreateCanvas(8, 8, 128);
        Assert.Equal(8, canvas.Width);

        // Draw some variation
        var withLine = canvas.DrawLine(0, 0, 7, 7, 64);
        Assert.NotNull(withLine);

        // AdjustContrast
        var contrasted = withLine.AdjustContrast(1.5);
        Assert.NotNull(contrasted);
        Assert.Equal(8, contrasted.Width);
        Assert.Equal(8, contrasted.Height);

        // ApplySepia
        var sepia = contrasted.ApplySepia();
        Assert.NotNull(sepia);
        Assert.Equal(8, sepia.Width);
        Assert.Equal(8, sepia.Height);

        // EqualizeHistogram
        var equalized = sepia.EqualizeHistogram();
        Assert.NotNull(equalized);
        Assert.Equal(8, equalized.Width);
        Assert.Equal(8, equalized.Height);

        // Save and reload
        var path = TempFile("dogfood_contrast_sepia.pgm");
        equalized.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(reloaded);
        Assert.Equal(8, reloaded.Width);
        Assert.Equal(8, reloaded.Height);

        // Histogram after reload
        var hist = reloaded.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count > 0);
    }
}
