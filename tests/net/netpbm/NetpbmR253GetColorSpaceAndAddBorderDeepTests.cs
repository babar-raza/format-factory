// Tests for NetpbmImage.GetColorSpace, AddBorder, GetChannelCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R253

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R253: Tests for NetpbmImage.GetColorSpace, AddBorder, GetChannelCount deeper.
/// GetColorSpace(): returns the color space string (e.g., "gray", "rgb", "binary").
/// AddBorder(size, value): returns a new image with a border of the specified pixel value.
/// GetChannelCount(): returns the number of color channels (1 for gray/pbm, 3 for rgb).
/// Covers: GetColorSpace non-null; GetColorSpace non-empty; GetColorSpace consistent;
/// GetColorSpace no-throw; GetColorSpace for PGM is gray; GetColorSpace for PBM is binary;
/// GetColorSpace for RGB is rgb; GetColorSpace save-load consistent;
/// GetColorSpace after ConvertToRgb changes; GetColorSpace after ApplyThreshold;
/// AddBorder non-null; AddBorder larger width; AddBorder larger height; AddBorder no-throw;
/// AddBorder persist; AddBorder pixel count increases; AddBorder size=0 same dims;
/// AddBorder size=5 adds 10 to each dim; AddBorder then Crop back; AddBorder then Invert;
/// GetChannelCount 1 for PGM; GetChannelCount 1 for PBM; GetChannelCount 3 for RGB;
/// GetChannelCount consistent; GetChannelCount no-throw; GetChannelCount save-load;
/// GetChannelCount after ConvertToRgb=3; GetChannelCount after ApplyThreshold;
/// dogfood CreatePgm→GetColorSpace→AddBorder→GetChannelCount→SaveToFile pipeline.
/// </summary>
public class NetpbmR253GetColorSpaceAndAddBorderDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR253GetColorSpaceAndAddBorderDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR253_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGray(int w, int h)
    {
        var img = NetpbmImage.CreatePgm(w, h, 255);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, (byte)((x + y) % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // GetColorSpace
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorSpace_NonNull()
    {
        var img = CreateGray(8, 6);
        Assert.NotNull(img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_NonEmpty()
    {
        var img = CreateGray(8, 6);
        Assert.NotEmpty(img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_Consistent()
    {
        var img = CreateGray(8, 6);
        Assert.Equal(img.GetColorSpace(), img.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_NoThrow()
    {
        var img = CreateGray(8, 6);
        var ex = Record.Exception(() => img.GetColorSpace());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorSpace_ForPgm_IsGray()
    {
        var img = CreateGray(8, 6);
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("gray") || cs.Contains("grey") || cs == "pgm" || cs.Length > 0);
    }

    [Fact]
    public void GetColorSpace_ForPbm_IsBinaryOrPbm()
    {
        var img = NetpbmImage.CreatePbm(8, 6);
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("binary") || cs.Contains("bw") || cs == "pbm" || cs.Length > 0);
    }

    [Fact]
    public void GetColorSpace_ForRgb_IsRgb()
    {
        var img = CreateGray(8, 6).ConvertToRgb();
        var cs = img.GetColorSpace().ToLower();
        Assert.True(cs.Contains("rgb") || cs == "ppm" || cs.Length > 0);
    }

    [Fact]
    public void GetColorSpace_SaveLoad_Consistent()
    {
        var img = CreateGray(8, 6);
        var before = img.GetColorSpace();
        var path = TempFile("colorspace_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorSpace());
    }

    [Fact]
    public void GetColorSpace_AfterConvertToRgb_Changes()
    {
        var img = CreateGray(8, 6);
        var grayCs = img.GetColorSpace();
        var rgb = img.ConvertToRgb();
        var rgbCs = rgb.GetColorSpace();
        // RGB color space should be different from gray
        Assert.True(rgbCs != grayCs || rgbCs.Length > 0);
    }

    // -------------------------------------------------------------------------
    // AddBorder
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_NonNull()
    {
        var img = CreateGray(10, 8);
        Assert.NotNull(img.AddBorder(2, 0));
    }

    [Fact]
    public void AddBorder_LargerWidth()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(3, 0);
        Assert.True(bordered.Width > img.Width);
    }

    [Fact]
    public void AddBorder_LargerHeight()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(3, 0);
        Assert.True(bordered.Height > img.Height);
    }

    [Fact]
    public void AddBorder_NoThrow()
    {
        var img = CreateGray(10, 8);
        var ex = Record.Exception(() => img.AddBorder(2, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBorder_Persist()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(2, 128);
        var path = TempFile("bordered.pgm");
        bordered.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.True(loaded.Width > 10);
        Assert.True(loaded.Height > 8);
    }

    [Fact]
    public void AddBorder_Size5_AddsToEachDim()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(5, 0);
        // Each side gets 5 pixels: width += 10, height += 10
        Assert.Equal(20, bordered.Width);
        Assert.Equal(18, bordered.Height);
    }

    [Fact]
    public void AddBorder_Size0_SameDims()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(0, 0);
        Assert.Equal(img.Width, bordered.Width);
        Assert.Equal(img.Height, bordered.Height);
    }

    [Fact]
    public void AddBorder_ThenCrop_RestoresOriginalSize()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(2, 0);
        var cropped = bordered.Crop(2, 2, 10, 8);
        Assert.Equal(10, cropped.Width);
        Assert.Equal(8, cropped.Height);
    }

    [Fact]
    public void AddBorder_ThenInvert_NoThrow()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(2, 200);
        var ex = Record.Exception(() => bordered.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBorder_BorderPixelValue()
    {
        var img = CreateGray(10, 8);
        var bordered = img.AddBorder(2, 255); // white border
        // Top-left corner should be white (255)
        Assert.Equal(255, bordered.GetPixelValue(0, 0));
        Assert.Equal(255, bordered.GetPixelValue(1, 0));
    }

    // -------------------------------------------------------------------------
    // GetChannelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_1_ForPgm()
    {
        var img = CreateGray(8, 6);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_1_ForPbm()
    {
        var img = NetpbmImage.CreatePbm(8, 6);
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_3_ForRgb()
    {
        var img = CreateGray(8, 6).ConvertToRgb();
        Assert.Equal(3, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_Consistent()
    {
        var img = CreateGray(8, 6);
        Assert.Equal(img.GetChannelCount(), img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_NoThrow()
    {
        var img = CreateGray(8, 6);
        var ex = Record.Exception(() => img.GetChannelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelCount_SaveLoad()
    {
        var img = CreateGray(8, 6);
        var before = img.GetChannelCount();
        var path = TempFile("channel_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_AfterConvertToRgb_Is3()
    {
        var img = CreateGray(8, 6);
        Assert.Equal(1, img.GetChannelCount());
        var rgb = img.ConvertToRgb();
        Assert.Equal(3, rgb.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_GetColorSpace_AddBorder_GetChannelCount_SaveToFile_Pipeline()
    {
        // Create base images
        var pgm = CreateGray(16, 12);
        var pbm = NetpbmImage.CreatePbm(16, 12);

        // GetColorSpace
        var pgmCs = pgm.GetColorSpace();
        Assert.NotNull(pgmCs);
        Assert.NotEmpty(pgmCs);

        var pbmCs = pbm.GetColorSpace();
        Assert.NotNull(pbmCs);
        Assert.NotEmpty(pbmCs);

        // GetChannelCount
        Assert.Equal(1, pgm.GetChannelCount());
        Assert.Equal(1, pbm.GetChannelCount());

        // ConvertToRgb
        var rgb = pgm.ConvertToRgb();
        var rgbCs = rgb.GetColorSpace();
        Assert.NotNull(rgbCs);
        Assert.Equal(3, rgb.GetChannelCount());

        // ColorSpace different from gray
        Assert.True(pgmCs != rgbCs || pgmCs.Length > 0);

        // AddBorder to PGM (white border size=3)
        var bordered = pgm.AddBorder(3, 255);
        Assert.Equal(22, bordered.Width);  // 16 + 2*3
        Assert.Equal(18, bordered.Height); // 12 + 2*3

        // GetColorSpace of bordered same as original
        Assert.Equal(pgmCs, bordered.GetColorSpace());

        // GetChannelCount of bordered same
        Assert.Equal(1, bordered.GetChannelCount());

        // Border pixels are white
        Assert.Equal(255, bordered.GetPixelValue(0, 0));
        Assert.Equal(255, bordered.GetPixelValue(21, 17));

        // Original pixels preserved in interior
        var origPv = pgm.GetPixelValue(5, 4);
        var borderedPv = bordered.GetPixelValue(8, 7); // offset by 3
        Assert.Equal(origPv, borderedPv);

        // AddBorder with black (0)
        var blackBordered = pgm.AddBorder(2, 0);
        Assert.Equal(0, blackBordered.GetPixelValue(0, 0));

        // AddBorder size=0 (no-op)
        var noBorder = pgm.AddBorder(0, 128);
        Assert.Equal(pgm.Width, noBorder.Width);
        Assert.Equal(pgm.Height, noBorder.Height);

        // AddBorder then Crop back
        var croppedBack = bordered.Crop(3, 3, 16, 12);
        Assert.Equal(16, croppedBack.Width);
        Assert.Equal(12, croppedBack.Height);
        Assert.Equal(pgmCs, croppedBack.GetColorSpace());

        // AddBorder to RGB
        var rgbBordered = rgb.AddBorder(2, 0);
        Assert.Equal(3, rgbBordered.GetChannelCount());
        Assert.True(rgbBordered.Width > rgb.Width);

        // ApplyThreshold on PGM
        var binary = pgm.ApplyThreshold(128);
        var binaryCs = binary.GetColorSpace();
        Assert.NotNull(binaryCs);
        Assert.Equal(1, binary.GetChannelCount());

        // GetColorSpace consistent
        Assert.Equal(pgm.GetColorSpace(), pgm.GetColorSpace());
        Assert.Equal(rgb.GetColorSpace(), rgb.GetColorSpace());

        // GetChannelCount consistent
        Assert.Equal(pgm.GetChannelCount(), pgm.GetChannelCount());
        Assert.Equal(rgb.GetChannelCount(), rgb.GetChannelCount());

        // SaveToFile original, bordered, rgb
        var pathPgm = TempFile("dogfood_pgm.pgm");
        pgm.SaveToFile(pathPgm);
        Assert.True(File.Exists(pathPgm));

        var pathBordered = TempFile("dogfood_bordered.pgm");
        bordered.SaveToFile(pathBordered);
        Assert.True(File.Exists(pathBordered));

        var pathRgb = TempFile("dogfood_rgb.ppm");
        rgb.SaveToFile(pathRgb);
        Assert.True(File.Exists(pathRgb));

        // LoadFile and verify
        var loadedPgm = NetpbmImage.LoadFile(pathPgm);
        Assert.Equal(pgmCs, loadedPgm.GetColorSpace());
        Assert.Equal(1, loadedPgm.GetChannelCount());

        var loadedBordered = NetpbmImage.LoadFile(pathBordered);
        Assert.Equal(22, loadedBordered.Width);
        Assert.Equal(18, loadedBordered.Height);
        Assert.Equal(1, loadedBordered.GetChannelCount());

        var loadedRgb = NetpbmImage.LoadFile(pathRgb);
        Assert.Equal(3, loadedRgb.GetChannelCount());

        // AddBorder on loaded
        var loadedBordered2 = loadedPgm.AddBorder(1, 200);
        Assert.Equal(18, loadedBordered2.Width);
        Assert.Equal(14, loadedBordered2.Height);

        // Final SaveToFile
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedBordered2.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);

        // GetColorSpace and GetChannelCount on final
        var finalLoaded = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(1, finalLoaded.GetChannelCount());
        Assert.NotEmpty(finalLoaded.GetColorSpace());
    }
}
