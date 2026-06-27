// Tests for NetpbmImage.GetInvertedImage, GetNormalizedImage, GetGammaCorrectedImage deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R312

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R312: Tests for NetpbmImage.GetInvertedImage, GetNormalizedImage, GetGammaCorrectedImage deeper.
/// GetInvertedImage(): returns a new image with each pixel value replaced by MaxVal - value.
/// GetNormalizedImage(): returns a new image with pixels scaled to fill the full [0,MaxVal] range.
/// GetGammaCorrectedImage(gamma): returns a new image with gamma correction applied.
/// Covers: GetInvertedImage no-throw; GetInvertedImage same dims; GetInvertedImage consistent;
/// GetInvertedImage inverts pixel values; GetInvertedImage double-invert roundtrip; GetInvertedImage save-load;
/// GetNormalizedImage no-throw; GetNormalizedImage same dims; GetNormalizedImage consistent;
/// GetNormalizedImage max equals MaxVal; GetNormalizedImage save-load;
/// GetGammaCorrectedImage no-throw; GetGammaCorrectedImage same dims; GetGammaCorrectedImage consistent;
/// GetGammaCorrectedImage save-load;
/// dogfood CreateImage→GetInvertedImage→GetNormalizedImage→GetGammaCorrectedImage→SaveToFile pipeline.
/// </summary>
public class NetpbmR312GetInvertedAndNormalizedImageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR312GetInvertedAndNormalizedImageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR312_" + Guid.NewGuid().ToString("N"));
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
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateDarkPgm()
    {
        // Dark image: pixels mostly in 10-50 range
        var path = TempFile("dark.pgm");
        var pixels = new byte[8 * 8];
        for (int i = 0; i < 64; i++) pixels[i] = (byte)(10 + i % 40);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n8 8\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetInvertedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetInvertedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetInvertedImage());
        Assert.Null(ex);
    }

    [Fact]
    public void GetInvertedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.GetInvertedImage();
        Assert.Equal(img.Width, inv.Width);
        Assert.Equal(img.Height, inv.Height);
    }

    [Fact]
    public void GetInvertedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var i1 = img.GetInvertedImage();
        var i2 = img.GetInvertedImage();
        Assert.Equal(i1.GetMeanPixelValue(), i2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetInvertedImage_InvertsMean()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.GetInvertedImage();
        // Mean of original + mean of inverted ≈ MaxVal
        var sum = img.GetMeanPixelValue() + inv.GetMeanPixelValue();
        Assert.True(Math.Abs(sum - img.MaxVal) < 1.0);
    }

    [Fact]
    public void GetInvertedImage_DoubleInvert_Roundtrip()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var dbl = img.GetInvertedImage().GetInvertedImage();
        Assert.Equal(img.GetMeanPixelValue(), dbl.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetInvertedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var inv = img.GetInvertedImage();
        var path = TempFile("inv_save.pgm");
        inv.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(inv.Width, loaded.Width);
        Assert.Equal(inv.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetNormalizedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNormalizedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateDarkPgm());
        var ex = Record.Exception(() => img.GetNormalizedImage());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNormalizedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateDarkPgm());
        var norm = img.GetNormalizedImage();
        Assert.Equal(img.Width, norm.Width);
        Assert.Equal(img.Height, norm.Height);
    }

    [Fact]
    public void GetNormalizedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateDarkPgm());
        var n1 = img.GetNormalizedImage();
        var n2 = img.GetNormalizedImage();
        Assert.Equal(n1.GetMeanPixelValue(), n2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetNormalizedImage_MaxEqualsMaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateDarkPgm());
        var norm = img.GetNormalizedImage();
        Assert.Equal(norm.MaxVal, norm.GetMaxPixel());
    }

    [Fact]
    public void GetNormalizedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateDarkPgm());
        var norm = img.GetNormalizedImage();
        var path = TempFile("norm_save.pgm");
        norm.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(norm.Width, loaded.Width);
        Assert.Equal(norm.GetMaxPixel(), loaded.GetMaxPixel());
    }

    // -------------------------------------------------------------------------
    // GetGammaCorrectedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGammaCorrectedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetGammaCorrectedImage(2.2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGammaCorrectedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var gc = img.GetGammaCorrectedImage(1.8);
        Assert.Equal(img.Width, gc.Width);
        Assert.Equal(img.Height, gc.Height);
    }

    [Fact]
    public void GetGammaCorrectedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var g1 = img.GetGammaCorrectedImage(2.2);
        var g2 = img.GetGammaCorrectedImage(2.2);
        Assert.Equal(g1.GetMeanPixelValue(), g2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetGammaCorrectedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var gc = img.GetGammaCorrectedImage(2.2);
        var path = TempFile("gc_save.pgm");
        gc.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(gc.Width, loaded.Width);
        Assert.Equal(gc.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetInvertedImage_GetNormalizedImage_GetGammaCorrectedImage_SaveToFile_Pipeline()
    {
        // Forensic image enhancement — crime scene photograph simulation
        var path = TempFile("dogfood_forensic.pgm");
        var pixels = new byte[12 * 10];
        // Simulate dark scene with some bright evidence (fingerprint ridges)
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
            {
                bool isEvidence = (r >= 3 && r <= 6) && (c >= 2 && c <= 9) && ((r + c) % 3 == 0);
                pixels[r * 12 + c] = isEvidence ? (byte)200 : (byte)(15 + r * 4 + c * 2);
            }
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(255, img.MaxVal);

        var origMean = img.GetMeanPixelValue();
        Assert.True(origMean > 0.0);

        // GetInvertedImage — negative to reveal latent evidence
        var inv = img.GetInvertedImage();
        Assert.Equal(12, inv.Width);
        Assert.Equal(10, inv.Height);
        Assert.True(Math.Abs(origMean + inv.GetMeanPixelValue() - 255) < 1.0);
        Assert.Equal(inv.GetMeanPixelValue(), img.GetInvertedImage().GetMeanPixelValue(), precision: 4); // consistent

        // Double-invert roundtrip
        var dbl = inv.GetInvertedImage();
        Assert.Equal(origMean, dbl.GetMeanPixelValue(), precision: 4);

        // GetNormalizedImage — enhance contrast
        var norm = img.GetNormalizedImage();
        Assert.Equal(12, norm.Width);
        Assert.Equal(10, norm.Height);
        Assert.Equal(255, norm.GetMaxPixel()); // max always hits MaxVal after normalisation
        Assert.Equal(0, norm.GetMinPixel());   // min always hits 0 after normalisation
        Assert.Equal(norm.GetMeanPixelValue(), img.GetNormalizedImage().GetMeanPixelValue(), precision: 4); // consistent

        // GetGammaCorrectedImage — various gamma values
        var gcDark = img.GetGammaCorrectedImage(2.2);
        Assert.Equal(12, gcDark.Width);
        Assert.Equal(10, gcDark.Height);
        Assert.Equal(gcDark.GetMeanPixelValue(), img.GetGammaCorrectedImage(2.2).GetMeanPixelValue(), precision: 4); // consistent

        var gcLight = img.GetGammaCorrectedImage(0.5);
        Assert.Equal(12, gcLight.Width);
        // Gamma < 1 lightens; gamma > 1 darkens
        Assert.True(gcLight.GetMeanPixelValue() > gcDark.GetMeanPixelValue());

        // SaveToFile — inverted
        var out1 = TempFile("dogfood_forensic_inv.pgm");
        inv.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loadedInv = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loadedInv.Width);
        Assert.Equal(inv.GetMeanPixelValue(), loadedInv.GetMeanPixelValue(), precision: 4);

        // SaveToFile — normalized
        var out2 = TempFile("dogfood_forensic_norm.pgm");
        norm.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loadedNorm = NetpbmImage.LoadFile(out2);
        Assert.Equal(255, loadedNorm.GetMaxPixel());

        // SaveToFile — gamma corrected
        var out3 = TempFile("dogfood_forensic_gc.pgm");
        gcDark.SaveToFile(out3);
        Assert.True(File.Exists(out3));
        var loadedGc = NetpbmImage.LoadFile(out3);
        Assert.Equal(gcDark.GetMeanPixelValue(), loadedGc.GetMeanPixelValue(), precision: 2);

        // Chain: normalize → invert → gamma
        var chain = img.GetNormalizedImage().GetInvertedImage().GetGammaCorrectedImage(1.5);
        Assert.Equal(12, chain.Width);
        Assert.Equal(10, chain.Height);
        var ex1 = Record.Exception(() => chain.SaveToFile(TempFile("dogfood_chain.pgm")));
        Assert.Null(ex1);
    }
}
