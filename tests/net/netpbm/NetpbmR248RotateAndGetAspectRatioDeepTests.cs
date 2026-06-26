// Tests for NetpbmImage.Rotate, GetAspectRatio, GetPixelValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R248

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R248: Tests for NetpbmImage.Rotate, GetAspectRatio, GetPixelValue deeper.
/// Rotate(degrees): rotates the image by the specified angle (90, 180, 270).
/// GetAspectRatio(): returns the width-to-height ratio of the image.
/// GetPixelValue(x, y): returns the pixel intensity at the given coordinates.
/// Covers: Rotate90 swaps dims; Rotate180 preserves dims; Rotate270 swaps dims;
/// Rotate90 no-throw; Rotate180 no-throw; Rotate270 no-throw;
/// Rotate90 persist; Rotate180 then Rotate180 same dims; Rotate then Crop no-throw;
/// Rotate then Invert no-throw; Rotate then ConvertToRgb no-throw;
/// GetAspectRatio positive; GetAspectRatio consistent; GetAspectRatio no-throw;
/// GetAspectRatio for square =1; GetAspectRatio wide >1; GetAspectRatio tall <1;
/// GetAspectRatio after Rotate90 changes; GetAspectRatio after Resize changes;
/// GetPixelValue non-negative; GetPixelValue in-range; GetPixelValue no-throw;
/// GetPixelValue consistent; GetPixelValue for white=max; GetPixelValue for black=0;
/// GetPixelValue after Invert changes; GetPixelValue after SetPixel reflects;
/// dogfood CreatePgm→Rotate→GetAspectRatio→GetPixelValue→SaveToFile pipeline.
/// </summary>
public class NetpbmR248RotateAndGetAspectRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR248RotateAndGetAspectRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR248_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGrayGradient(int width, int height)
    {
        var img = NetpbmImage.CreatePgm(width, height, 255);
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                img.SetPixel(x, y, (byte)((x + y) % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // Rotate
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate90_SwapsDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(90);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(12, rotated.Height);
    }

    [Fact]
    public void Rotate180_PreservesDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(180);
        Assert.Equal(12, rotated.Width);
        Assert.Equal(8, rotated.Height);
    }

    [Fact]
    public void Rotate270_SwapsDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(270);
        Assert.Equal(8, rotated.Width);
        Assert.Equal(12, rotated.Height);
    }

    [Fact]
    public void Rotate90_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var ex = Record.Exception(() => img.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate180_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var ex = Record.Exception(() => img.Rotate(180));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate270_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var ex = Record.Exception(() => img.Rotate(270));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_Persist()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(90);
        var path = TempFile("rotate90.pgm");
        rotated.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(12, loaded.Height);
    }

    [Fact]
    public void Rotate180_Twice_SameDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var rot1 = img.Rotate(180);
        var rot2 = rot1.Rotate(180);
        Assert.Equal(img.Width, rot2.Width);
        Assert.Equal(img.Height, rot2.Height);
    }

    [Fact]
    public void Rotate90_ThenCrop_NoThrow()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(90);
        var ex = Record.Exception(() => rotated.Crop(0, 0, 4, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_ThenInvert_NoThrow()
    {
        var img = CreateGrayGradient(12, 8);
        var rotated = img.Rotate(90);
        var ex = Record.Exception(() => rotated.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate90_ThenConvertToRgb_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var rotated = img.Rotate(90);
        var ex = Record.Exception(() => rotated.ConvertToRgb());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetAspectRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_Positive()
    {
        var img = CreateGrayGradient(12, 8);
        Assert.True(img.GetAspectRatio() > 0.0);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = CreateGrayGradient(12, 8);
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio());
    }

    [Fact]
    public void GetAspectRatio_NoThrow()
    {
        var img = CreateGrayGradient(12, 8);
        var ex = Record.Exception(() => img.GetAspectRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAspectRatio_ForSquare_IsOne()
    {
        var img = CreateGrayGradient(8, 8);
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 5);
    }

    [Fact]
    public void GetAspectRatio_Wide_GreaterThanOne()
    {
        var img = CreateGrayGradient(16, 8);
        Assert.True(img.GetAspectRatio() > 1.0);
    }

    [Fact]
    public void GetAspectRatio_Tall_LessThanOne()
    {
        var img = CreateGrayGradient(8, 16);
        Assert.True(img.GetAspectRatio() < 1.0);
    }

    [Fact]
    public void GetAspectRatio_AfterRotate90_Changes()
    {
        var img = CreateGrayGradient(16, 8);
        var original = img.GetAspectRatio();
        var rotated = img.Rotate(90);
        var rotatedRatio = rotated.GetAspectRatio();
        // Wide becomes tall: ratio should be < 1
        Assert.True(rotatedRatio < original);
    }

    [Fact]
    public void GetAspectRatio_AfterResize_Reflects()
    {
        var img = CreateGrayGradient(8, 8);
        var resized = img.Resize(16, 8);
        Assert.True(resized.GetAspectRatio() > 1.0);
    }

    // -------------------------------------------------------------------------
    // GetPixelValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelValue_NonNegative()
    {
        var img = CreateGrayGradient(10, 8);
        Assert.True(img.GetPixelValue(0, 0) >= 0);
    }

    [Fact]
    public void GetPixelValue_InRange()
    {
        var img = CreateGrayGradient(10, 8);
        var val = img.GetPixelValue(5, 4);
        Assert.True(val >= 0 && val <= 255);
    }

    [Fact]
    public void GetPixelValue_NoThrow()
    {
        var img = CreateGrayGradient(10, 8);
        var ex = Record.Exception(() => img.GetPixelValue(3, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelValue_Consistent()
    {
        var img = CreateGrayGradient(10, 8);
        Assert.Equal(img.GetPixelValue(2, 2), img.GetPixelValue(2, 2));
    }

    [Fact]
    public void GetPixelValue_ForWhite_IsMax()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(1, 1, 255);
        Assert.Equal(255, img.GetPixelValue(1, 1));
    }

    [Fact]
    public void GetPixelValue_ForBlack_IsZero()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(2, 2, 0);
        Assert.Equal(0, img.GetPixelValue(2, 2));
    }

    [Fact]
    public void GetPixelValue_AfterInvert_Changes()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        img.SetPixel(0, 0, 100);
        var original = img.GetPixelValue(0, 0);
        var inverted = img.Invert();
        var invertedVal = inverted.GetPixelValue(0, 0);
        Assert.NotEqual(original, invertedVal);
    }

    [Fact]
    public void GetPixelValue_AfterSetPixel_Reflects()
    {
        var img = NetpbmImage.CreatePgm(6, 6, 255);
        img.SetPixel(3, 3, 128);
        Assert.Equal(128, img.GetPixelValue(3, 3));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_Rotate_GetAspectRatio_GetPixelValue_SaveToFile_Pipeline()
    {
        // Create 16×8 gradient (wide landscape)
        var img = NetpbmImage.CreatePgm(16, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 16; x++)
                img.SetPixel(x, y, (byte)((x * 8 + y * 16) % 256));

        Assert.Equal(16, img.Width);
        Assert.Equal(8, img.Height);

        // GetAspectRatio baseline — should be 2.0 (wide)
        var ar = img.GetAspectRatio();
        Assert.True(ar > 1.0);

        // GetPixelValue baseline
        var pv00 = img.GetPixelValue(0, 0);
        Assert.True(pv00 >= 0 && pv00 <= 255);

        // Rotate 90
        var rot90 = img.Rotate(90);
        Assert.Equal(8, rot90.Width);
        Assert.Equal(16, rot90.Height);

        // GetAspectRatio after Rotate90 — should be < 1.0 (tall)
        var arRot90 = rot90.GetAspectRatio();
        Assert.True(arRot90 < 1.0);

        // Rotate 180
        var rot180 = img.Rotate(180);
        Assert.Equal(16, rot180.Width);
        Assert.Equal(8, rot180.Height);
        Assert.Equal(ar, rot180.GetAspectRatio(), precision: 5);

        // Rotate 270
        var rot270 = img.Rotate(270);
        Assert.Equal(8, rot270.Width);
        Assert.Equal(16, rot270.Height);
        Assert.True(rot270.GetAspectRatio() < 1.0);

        // Double rotate 180 — should match original dims
        var rot360 = rot180.Rotate(180);
        Assert.Equal(16, rot360.Width);
        Assert.Equal(8, rot360.Height);

        // GetPixelValue on rotated
        var pvRot = rot90.GetPixelValue(0, 0);
        Assert.True(pvRot >= 0 && pvRot <= 255);

        // GetPixelValue after SetPixel
        img.SetPixel(5, 3, 200);
        Assert.Equal(200, img.GetPixelValue(5, 3));

        // Invert and check GetPixelValue changes
        var inverted = img.Invert();
        var origPv = img.GetPixelValue(5, 3);
        var invPv = inverted.GetPixelValue(5, 3);
        Assert.NotEqual(origPv, invPv);

        // GetAspectRatio consistent
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio());

        // Crop rotated image
        var cropped = rot90.Crop(0, 0, 4, 8);
        Assert.Equal(4, cropped.Width);
        Assert.Equal(8, cropped.Height);

        // GetAspectRatio on cropped — square-ish
        var arCropped = cropped.GetAspectRatio();
        Assert.True(arCropped > 0.0);

        // Scale and verify GetAspectRatio
        var scaled = img.Scale(2.0);
        Assert.True(scaled.GetAspectRatio() > 0.0);
        Assert.Equal(img.GetAspectRatio(), scaled.GetAspectRatio(), precision: 5);

        // GetPixelValue for all corners
        var corners = new[]
        {
            img.GetPixelValue(0, 0),
            img.GetPixelValue(15, 0),
            img.GetPixelValue(0, 7),
            img.GetPixelValue(15, 7)
        };
        foreach (var c in corners)
            Assert.True(c >= 0 && c <= 255);

        // ConvertToRgb preserves GetAspectRatio
        var rgb = img.ConvertToRgb();
        Assert.Equal(img.GetAspectRatio(), rgb.GetAspectRatio(), precision: 5);

        // SaveToFile original
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        // SaveToFile rot90
        var pathRot90 = TempFile("dogfood_rot90.pgm");
        rot90.SaveToFile(pathRot90);
        Assert.True(File.Exists(pathRot90));

        // LoadFile rot90 and verify
        var loadedRot90 = NetpbmImage.LoadFile(pathRot90);
        Assert.Equal(8, loadedRot90.Width);
        Assert.Equal(16, loadedRot90.Height);
        Assert.True(loadedRot90.GetAspectRatio() < 1.0);

        // GetPixelValue on loaded
        var loadedPv = loadedRot90.GetPixelValue(0, 0);
        Assert.True(loadedPv >= 0 && loadedPv <= 255);

        // Rotate loaded back
        var loadedRot90Rotated = loadedRot90.Rotate(270);
        Assert.Equal(16, loadedRot90Rotated.Width);
        Assert.Equal(8, loadedRot90Rotated.Height);

        // SaveToFile final
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedRot90Rotated.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
    }
}
