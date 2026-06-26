// Tests for NetpbmImage.Invert, Equalize deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R227

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R227: Tests for NetpbmImage.Invert, Equalize deeper coverage.
/// Invert(): inverts all pixel values (255 - value per channel).
/// Equalize(): applies histogram equalization to improve contrast.
/// Covers: Invert non-null; Invert same dimensions; Invert twice restores original pixel;
/// Invert white becomes black; Invert black becomes white; Invert mid-value;
/// Invert then SaveToFile/LoadFile preserved; Invert on grayscale;
/// Equalize non-null; Equalize same dimensions; Equalize on grayscale;
/// Equalize on color; Equalize then SaveToFile/LoadFile preserved; Equalize twice non-null;
/// Equalize + Invert pipeline; Equalize preserves dimension metadata;
/// dogfood CreateCanvas→SetPixel→Invert→verify pixels→Equalize→SaveLoad→GetChannelStats pipeline.
/// </summary>
public class NetpbmR227InvertAndEqualizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR227InvertAndEqualizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR227_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateColorCanvas(int w = 8, int h = 8)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PPM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, x * 32, y * 32, 128);
        return img;
    }

    private static NetpbmImage CreateGrayCanvas(int w = 8, int h = 8)
    {
        var img = NetpbmImage.CreateCanvas(w, h, NetpbmFormat.PGM);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, (x + y) * 16);
        return img;
    }

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.Invert());
    }

    [Fact]
    public void Invert_SameDimensions()
    {
        var img = CreateColorCanvas(8, 6);
        var inverted = img.Invert();
        Assert.Equal(8, inverted.Width);
        Assert.Equal(6, inverted.Height);
    }

    [Fact]
    public void Invert_TwiceRestoresOriginalPixel()
    {
        var img = CreateColorCanvas();
        img.SetPixel(0, 0, 100, 150, 200);
        var original = img.GetPixel(0, 0);
        var restored = img.Invert().Invert().GetPixel(0, 0);
        Assert.Equal(original.R, restored.R);
        Assert.Equal(original.G, restored.G);
        Assert.Equal(original.B, restored.B);
    }

    [Fact]
    public void Invert_WhiteBecomesBlack()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 255);
        var inverted = img.Invert();
        var pixel = inverted.GetPixel(0, 0);
        Assert.Equal(0, pixel.R);
    }

    [Fact]
    public void Invert_BlackBecomesWhite()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        var inverted = img.Invert();
        var pixel = inverted.GetPixel(0, 0);
        Assert.Equal(255, pixel.R);
    }

    [Fact]
    public void Invert_MidValue128Inverts()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 128);
        var inverted = img.Invert();
        var pixel = inverted.GetPixel(0, 0);
        Assert.Equal(127, pixel.R); // 255 - 128 = 127
    }

    [Fact]
    public void Invert_ThenSaveAndLoad_Preserved()
    {
        var img = CreateColorCanvas();
        var inverted = img.Invert();
        var path = TempFile("invert.ppm");
        inverted.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void Invert_OnGrayscale_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.Invert());
    }

    [Fact]
    public void Invert_OnGrayscale_SameDimensions()
    {
        var img = CreateGrayCanvas(8, 6);
        var inverted = img.Invert();
        Assert.Equal(8, inverted.Width);
        Assert.Equal(6, inverted.Height);
    }

    // -------------------------------------------------------------------------
    // Equalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Equalize_NonNull()
    {
        var img = CreateColorCanvas();
        Assert.NotNull(img.Equalize());
    }

    [Fact]
    public void Equalize_SameDimensions()
    {
        var img = CreateColorCanvas(8, 6);
        var eq = img.Equalize();
        Assert.Equal(8, eq.Width);
        Assert.Equal(6, eq.Height);
    }

    [Fact]
    public void Equalize_OnGrayscale_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.Equalize());
    }

    [Fact]
    public void Equalize_OnGrayscale_SameDimensions()
    {
        var img = CreateGrayCanvas(8, 6);
        var eq = img.Equalize();
        Assert.Equal(8, eq.Width);
        Assert.Equal(6, eq.Height);
    }

    [Fact]
    public void Equalize_ThenSaveAndLoad_Preserved()
    {
        var img = CreateColorCanvas();
        var eq = img.Equalize();
        var path = TempFile("equalize.ppm");
        eq.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void Equalize_Twice_NonNull()
    {
        var img = CreateGrayCanvas();
        Assert.NotNull(img.Equalize().Equalize());
    }

    [Fact]
    public void Equalize_PreservesDimensionMetadata()
    {
        var img = CreateColorCanvas(10, 6);
        var eq = img.Equalize();
        var meta = eq.GetMetadata();
        Assert.Equal(10, meta.Width);
        Assert.Equal(6, meta.Height);
    }

    [Fact]
    public void Equalize_ThenInvert_Pipeline()
    {
        var img = CreateGrayCanvas();
        var result = img.Equalize().Invert();
        Assert.NotNull(result);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_SetPixel_Invert_VerifyPixels_Equalize_SaveLoad_GetChannelStats_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.PPM);

        // SetPixel with known values
        img.SetPixel(0, 0, 255, 0, 0);   // red
        img.SetPixel(7, 0, 0, 255, 0);   // green
        img.SetPixel(0, 7, 0, 0, 255);   // blue
        img.SetPixel(7, 7, 128, 128, 128); // gray
        img.SetPixel(4, 4, 0, 0, 0);       // black

        // Invert
        var inverted = img.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(8, inverted.Width);
        Assert.Equal(8, inverted.Height);

        // Verify specific pixels inverted
        var topLeft = inverted.GetPixel(0, 0); // was 255,0,0 → 0,255,255
        Assert.Equal(0, topLeft.R);
        Assert.Equal(255, topLeft.G);

        var black = inverted.GetPixel(4, 4); // was 0,0,0 → 255,255,255
        Assert.Equal(255, black.R);
        Assert.Equal(255, black.G);
        Assert.Equal(255, black.B);

        // Invert twice = original at (0,0)
        var restored = inverted.Invert().GetPixel(0, 0);
        Assert.Equal(255, restored.R);
        Assert.Equal(0, restored.G);
        Assert.Equal(0, restored.B);

        // Save inverted
        var invertPath = TempFile("dogfood_invert.ppm");
        inverted.SaveToFile(invertPath);
        Assert.True(File.Exists(invertPath));

        // LoadFile inverted
        var invertLoaded = NetpbmImage.LoadFile(invertPath);
        Assert.Equal(8, invertLoaded.Width);

        // Equalize on loaded
        var equalized = invertLoaded.Equalize();
        Assert.NotNull(equalized);
        Assert.Equal(8, equalized.Width);
        Assert.Equal(8, equalized.Height);

        // Save equalized
        var eqPath = TempFile("dogfood_equalize.ppm");
        equalized.SaveToFile(eqPath);
        Assert.True(File.Exists(eqPath));

        // LoadFile equalized
        var eqLoaded = NetpbmImage.LoadFile(eqPath);
        Assert.Equal(8, eqLoaded.Width);

        // GetChannelStats on equalized
        var stats = eqLoaded.GetChannelStats();
        Assert.Equal(3, stats.Count);
        foreach (var s in stats)
        {
            Assert.True(s.Min >= 0);
            Assert.True(s.Max <= 255);
        }

        // Grayscale pipeline: CreateGrayCanvas → Invert → Equalize
        var gray = CreateGrayCanvas();
        var grayInverted = gray.Invert();
        var grayEqualized = grayInverted.Equalize();
        Assert.NotNull(grayEqualized);
        Assert.Equal(gray.Width, grayEqualized.Width);
        Assert.Equal(gray.Height, grayEqualized.Height);
        var grayStats = grayEqualized.GetChannelStats();
        Assert.Equal(1, grayStats.Count);
    }
}
