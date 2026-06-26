// Tests for NetpbmImage.ConvertToGrayscale, GetChannelCount, GetColorSpace deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R258

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R258: Tests for NetpbmImage.ConvertToGrayscale, GetChannelCount, GetColorSpace deeper.
/// ConvertToGrayscale(): converts an RGB image to grayscale (PGM).
/// GetChannelCount(): returns the number of color channels (1 for PGM/PBM, 3 for PPM/RGB).
/// GetColorSpace(): returns the color space of the image as a string.
/// Covers: ConvertToGrayscale non-null; ConvertToGrayscale no-throw;
/// ConvertToGrayscale same dims; ConvertToGrayscale result is PGM;
/// ConvertToGrayscale channel count=1; ConvertToGrayscale from PGM same;
/// ConvertToGrayscale then SaveToFile; ConvertToGrayscale then Invert;
/// ConvertToGrayscale consistent;
/// GetChannelCount=1 for PGM; GetChannelCount=1 for PBM; GetChannelCount=3 for RGB;
/// GetChannelCount no-throw; GetChannelCount consistent; GetChannelCount save-load;
/// GetChannelCount after ConvertToRgb=3; GetChannelCount after ConvertToGrayscale=1;
/// GetColorSpace for PGM=gray; GetColorSpace for PBM=binary; GetColorSpace for RGB=rgb;
/// GetColorSpace no-throw; GetColorSpace consistent; GetColorSpace save-load;
/// GetColorSpace non-null; GetColorSpace non-empty;
/// dogfood CreateRgb→ConvertToGrayscale→GetChannelCount→GetColorSpace→SaveToFile pipeline.
/// </summary>
public class NetpbmR258ConvertToGrayscaleAndGetChannelCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR258ConvertToGrayscaleAndGetChannelCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR258_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateRgbImage(int width, int height)
    {
        var img = NetpbmImage.CreateRgb(width, height, 255);
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                img.SetPixelRgb(x, y, (byte)(x * 20 % 256), (byte)(y * 20 % 256), (byte)((x + y) * 10 % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // ConvertToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertToGrayscale_NonNull()
    {
        var img = CreateRgbImage(8, 6);
        Assert.NotNull(img.ConvertToGrayscale());
    }

    [Fact]
    public void ConvertToGrayscale_NoThrow()
    {
        var img = CreateRgbImage(8, 6);
        var ex = Record.Exception(() => img.ConvertToGrayscale());
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertToGrayscale_SameDimensions()
    {
        var img = CreateRgbImage(10, 8);
        var gray = img.ConvertToGrayscale();
        Assert.Equal(10, gray.Width);
        Assert.Equal(8, gray.Height);
    }

    [Fact]
    public void ConvertToGrayscale_ChannelCount_IsOne()
    {
        var img = CreateRgbImage(8, 6);
        var gray = img.ConvertToGrayscale();
        Assert.Equal(1, gray.GetChannelCount());
    }

    [Fact]
    public void ConvertToGrayscale_ColorSpace_IsGray()
    {
        var img = CreateRgbImage(8, 6);
        var gray = img.ConvertToGrayscale();
        var cs = gray.GetColorSpace().ToLower();
        Assert.True(cs.Contains("gray") || cs.Contains("grey") || cs.Contains("pgm"));
    }

    [Fact]
    public void ConvertToGrayscale_FromPgm_SameChannelCount()
    {
        var pgm = NetpbmImage.CreatePgm(8, 6, 255);
        var gray = pgm.ConvertToGrayscale();
        Assert.Equal(1, gray.GetChannelCount());
    }

    [Fact]
    public void ConvertToGrayscale_ThenSaveToFile()
    {
        var img = CreateRgbImage(8, 6);
        var gray = img.ConvertToGrayscale();
        var path = TempFile("grayscale.pgm");
        gray.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(1, loaded.GetChannelCount());
    }

    [Fact]
    public void ConvertToGrayscale_ThenInvert_NoThrow()
    {
        var img = CreateRgbImage(8, 6);
        var gray = img.ConvertToGrayscale();
        var ex = Record.Exception(() => gray.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void ConvertToGrayscale_Consistent()
    {
        var img = CreateRgbImage(8, 6);
        var g1 = img.ConvertToGrayscale();
        var g2 = img.ConvertToGrayscale();
        Assert.Equal(g1.Width, g2.Width);
        Assert.Equal(g1.GetChannelCount(), g2.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // GetChannelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_ForPgm_IsOne()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_ForPbm_IsOne()
    {
        var img = NetpbmImage.CreatePbm(8, 6);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_ForRgb_IsThree()
    {
        var img = CreateRgbImage(8, 6);
        Assert.Equal(3, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_NoThrow()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        var ex = Record.Exception(() => img.GetChannelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelCount_Consistent()
    {
        var img = CreateRgbImage(8, 6);
        Assert.Equal(img.GetChannelCount(), img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_SaveLoad_Consistent()
    {
        var img = CreateRgbImage(8, 6);
        var path = TempFile("channel_save.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(img.GetChannelCount(), loaded.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_AfterConvertToRgb_IsThree()
    {
        var pgm = NetpbmImage.CreatePgm(8, 6, 255);
        var rgb = pgm.ConvertToRgb();
        Assert.Equal(3, rgb.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_AfterConvertToGrayscale_IsOne()
    {
        var rgb = CreateRgbImage(8, 6);
        var gray = rgb.ConvertToGrayscale();
        Assert.Equal(1, gray.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // GetColorSpace
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_ForPgm_ContainsGray()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("gray") || cs.Contains("grey") || cs.Contains("pgm"));
    }

    [Fact]
    public void GetColorSpace_ForPbm_ContainsBinary()
    {
        var img = NetpbmImage.CreatePbm(8, 6);
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("binary") || cs.Contains("bit") || cs.Contains("pbm") || cs.Contains("black"));
    }

    [Fact]
    public void GetColorSpace_ForRgb_ContainsRgb()
    {
        var img = CreateRgbImage(8, 6);
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("rgb") || cs.Contains("color") || cs.Contains("ppm"));
    }

    [Fact]
    public void GetColorSpace_NoThrow()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        var ex = Record.Exception(() => img.GetColorSpace());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorSpace_Consistent()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        Assert.Equal(img.GetColorSpace(), img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_SaveLoad_Consistent()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        var before = img.GetColorSpace();
        var path = TempFile("colorspace_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_NonNull()
    {
        var img = CreateRgbImage(8, 6);
        Assert.NotNull(img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_NonEmpty()
    {
        var img = CreateRgbImage(8, 6);
        Assert.NotEmpty(img.GetColorSpace());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateRgb_ConvertToGrayscale_GetChannelCount_GetColorSpace_SaveToFile_Pipeline()
    {
        // Create RGB image 12×8
        var rgb = NetpbmImage.CreateRgb(12, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 12; x++)
                rgb.SetPixelRgb(x, y,
                    (byte)(x * 20 % 256),
                    (byte)(y * 30 % 256),
                    (byte)((x + y) * 15 % 256));

        Assert.Equal(12, rgb.Width);
        Assert.Equal(8, rgb.Height);
        Assert.Equal(3, rgb.GetChannelCount());
        var rgbCs = rgb.GetColorSpace().ToLower();
        Assert.True(rgbCs.Contains("rgb") || rgbCs.Contains("color") || rgbCs.Contains("ppm"));

        // Create PGM image 12×8
        var pgm = NetpbmImage.CreatePgm(12, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 12; x++)
                pgm.SetPixel(x, y, (byte)((x + y) * 15 % 256));

        Assert.Equal(1, pgm.GetChannelCount());
        var pgmCs = pgm.GetColorSpace().ToLower();
        Assert.True(pgmCs.Contains("gray") || pgmCs.Contains("grey") || pgmCs.Contains("pgm"));

        // ConvertToGrayscale from RGB
        var rgbToGray = rgb.ConvertToGrayscale();
        Assert.Equal(12, rgbToGray.Width);
        Assert.Equal(8, rgbToGray.Height);
        Assert.Equal(1, rgbToGray.GetChannelCount());
        var rgbToGrayCs = rgbToGray.GetColorSpace().ToLower();
        Assert.True(rgbToGrayCs.Contains("gray") || rgbToGrayCs.Contains("grey") || rgbToGrayCs.Contains("pgm"));

        // ConvertToGrayscale from PGM (already gray)
        var pgmToGray = pgm.ConvertToGrayscale();
        Assert.Equal(1, pgmToGray.GetChannelCount());

        // ConvertToRgb from PGM
        var pgmToRgb = pgm.ConvertToRgb();
        Assert.Equal(3, pgmToRgb.GetChannelCount());
        var pgmToRgbCs = pgmToRgb.GetColorSpace().ToLower();
        Assert.True(pgmToRgbCs.Contains("rgb") || pgmToRgbCs.Contains("ppm"));

        // RGB → Gray → RGB — channel count chain
        var doubleConvert = rgb.ConvertToGrayscale().ConvertToRgb();
        Assert.Equal(3, doubleConvert.GetChannelCount());

        // GetChannelCount consistent
        Assert.Equal(rgb.GetChannelCount(), rgb.GetChannelCount());
        Assert.Equal(pgm.GetChannelCount(), pgm.GetChannelCount());
        Assert.Equal(rgbToGray.GetChannelCount(), rgbToGray.GetChannelCount());

        // GetColorSpace consistent
        Assert.Equal(rgb.GetColorSpace(), rgb.GetColorSpace());
        Assert.Equal(pgm.GetColorSpace(), pgm.GetColorSpace());

        // PBM channel count
        var pbm = NetpbmImage.CreatePbm(8, 6);
        Assert.Equal(1, pbm.GetChannelCount());
        Assert.NotEmpty(pbm.GetColorSpace());

        // SaveToFile for all
        var pathRgb = TempFile("dogfood_rgb.ppm");
        rgb.SaveToFile(pathRgb);
        Assert.True(File.Exists(pathRgb));

        var pathGray = TempFile("dogfood_gray.pgm");
        rgbToGray.SaveToFile(pathGray);
        Assert.True(File.Exists(pathGray));

        var pathRgb2 = TempFile("dogfood_rgb_from_pgm.ppm");
        pgmToRgb.SaveToFile(pathRgb2);
        Assert.True(File.Exists(pathRgb2));

        // LoadFile and verify channel counts
        var loadedRgb = NetpbmImage.LoadFile(pathRgb);
        Assert.Equal(3, loadedRgb.GetChannelCount());
        Assert.Equal(rgb.GetColorSpace(), loadedRgb.GetColorSpace());

        var loadedGray = NetpbmImage.LoadFile(pathGray);
        Assert.Equal(1, loadedGray.GetChannelCount());
        Assert.Equal(pgm.GetColorSpace(), loadedGray.GetColorSpace());

        // ConvertToGrayscale on loaded RGB
        var loadedRgbToGray = loadedRgb.ConvertToGrayscale();
        Assert.Equal(1, loadedRgbToGray.GetChannelCount());
        Assert.Equal(12, loadedRgbToGray.Width);
        Assert.Equal(8, loadedRgbToGray.Height);

        // Final SaveToFile
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedRgbToGray.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
        var finalLoaded = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(1, finalLoaded.GetChannelCount());
        Assert.Equal(12, finalLoaded.Width);
        Assert.Equal(8, finalLoaded.Height);
    }
}
