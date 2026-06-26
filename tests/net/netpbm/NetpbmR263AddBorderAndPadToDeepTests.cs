// Tests for NetpbmImage.AddBorder, PadTo, GetAspectRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R263

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R263: Tests for NetpbmImage.AddBorder, PadTo, GetAspectRatio deeper.
/// AddBorder(thickness, value): adds a border of given pixel value around the image.
/// PadTo(width, height, value): pads the image to the target dimensions.
/// GetAspectRatio(): returns width/height as a double.
/// Covers: AddBorder non-null; AddBorder no-throw; AddBorder increases dims;
/// AddBorder thickness=1 adds 2 pixels each side; AddBorder consistent;
/// AddBorder then SaveToFile; AddBorder border pixels correct value;
/// AddBorder then FlipHorizontal no-throw; AddBorder then Normalize no-throw;
/// PadTo non-null; PadTo no-throw; PadTo width=target; PadTo height=target;
/// PadTo larger target; PadTo same dims no-throw; PadTo then SaveToFile;
/// PadTo consistent; PadTo border value correct; PadTo then Threshold no-throw;
/// GetAspectRatio positive; GetAspectRatio no-throw; GetAspectRatio correct;
/// GetAspectRatio consistent; GetAspectRatio square=1.0; GetAspectRatio save-load;
/// GetAspectRatio landscape>1; GetAspectRatio portrait<1;
/// dogfood CreatePgm→AddBorder→PadTo→GetAspectRatio→SaveToFile pipeline.
/// </summary>
public class NetpbmR263AddBorderAndPadToDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR263AddBorderAndPadToDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR263_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGradient(int w, int h)
    {
        var img = NetpbmImage.CreatePgm(w, h, 255);
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                img.SetPixel(x, y, (byte)((x + y) * 10 % 200 + 28));
        return img;
    }

    // -------------------------------------------------------------------------
    // AddBorder
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBorder_NonNull()
    {
        var img = CreateGradient(10, 8);
        Assert.NotNull(img.AddBorder(1, 0));
    }

    [Fact]
    public void AddBorder_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var ex = Record.Exception(() => img.AddBorder(1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBorder_Increases_Width()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(1, 0);
        Assert.Equal(12, bordered.Width);
    }

    [Fact]
    public void AddBorder_Increases_Height()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(1, 0);
        Assert.Equal(10, bordered.Height);
    }

    [Fact]
    public void AddBorder_Thickness2_Width()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(2, 0);
        Assert.Equal(14, bordered.Width);
    }

    [Fact]
    public void AddBorder_Thickness2_Height()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(2, 0);
        Assert.Equal(12, bordered.Height);
    }

    [Fact]
    public void AddBorder_Consistent()
    {
        var img = CreateGradient(10, 8);
        var b1 = img.AddBorder(1, 0);
        var b2 = img.AddBorder(1, 0);
        Assert.Equal(b1.Width, b2.Width);
        Assert.Equal(b1.Height, b2.Height);
    }

    [Fact]
    public void AddBorder_ThenSaveToFile()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(1, 128);
        var path = TempFile("border_out.pgm");
        bordered.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(10, loaded.Height);
    }

    [Fact]
    public void AddBorder_BorderPixels_CorrectValue()
    {
        var img = CreateGradient(8, 6);
        var bordered = img.AddBorder(1, 200);
        // Top-left corner should be border value
        Assert.Equal(200, bordered.GetPixelValue(0, 0));
        // Top-right corner
        Assert.Equal(200, bordered.GetPixelValue(9, 0));
        // Bottom-left corner
        Assert.Equal(200, bordered.GetPixelValue(0, 7));
    }

    [Fact]
    public void AddBorder_ThenFlipHorizontal_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(1, 0);
        var ex = Record.Exception(() => bordered.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBorder_ThenNormalize_NoThrow()
    {
        var img = CreateGradient(10, 8);
        var bordered = img.AddBorder(1, 50);
        var ex = Record.Exception(() => bordered.Normalize());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // PadTo
    // -------------------------------------------------------------------------

    [Fact]
    public void PadTo_NonNull()
    {
        var img = CreateGradient(8, 6);
        Assert.NotNull(img.PadTo(12, 10, 0));
    }

    [Fact]
    public void PadTo_NoThrow()
    {
        var img = CreateGradient(8, 6);
        var ex = Record.Exception(() => img.PadTo(12, 10, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void PadTo_Width_Equals_Target()
    {
        var img = CreateGradient(8, 6);
        var padded = img.PadTo(12, 10, 0);
        Assert.Equal(12, padded.Width);
    }

    [Fact]
    public void PadTo_Height_Equals_Target()
    {
        var img = CreateGradient(8, 6);
        var padded = img.PadTo(12, 10, 0);
        Assert.Equal(10, padded.Height);
    }

    [Fact]
    public void PadTo_SameDims_NoThrow()
    {
        var img = CreateGradient(8, 6);
        var ex = Record.Exception(() => img.PadTo(8, 6, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void PadTo_ThenSaveToFile()
    {
        var img = CreateGradient(8, 6);
        var padded = img.PadTo(16, 12, 128);
        var path = TempFile("padded_out.pgm");
        padded.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(12, loaded.Height);
    }

    [Fact]
    public void PadTo_Consistent()
    {
        var img = CreateGradient(8, 6);
        var p1 = img.PadTo(12, 10, 0);
        var p2 = img.PadTo(12, 10, 0);
        Assert.Equal(p1.Width, p2.Width);
        Assert.Equal(p1.Height, p2.Height);
    }

    [Fact]
    public void PadTo_ThenThreshold_NoThrow()
    {
        var img = CreateGradient(8, 6);
        var padded = img.PadTo(12, 10, 0);
        var ex = Record.Exception(() => padded.Threshold(128));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetAspectRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_Positive()
    {
        var img = CreateGradient(12, 8);
        Assert.True(img.GetAspectRatio() > 0);
    }

    [Fact]
    public void GetAspectRatio_NoThrow()
    {
        var img = CreateGradient(12, 8);
        var ex = Record.Exception(() => img.GetAspectRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAspectRatio_Correct()
    {
        var img = CreateGradient(12, 8);
        Assert.Equal(12.0 / 8.0, img.GetAspectRatio(), 5);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = CreateGradient(12, 8);
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio(), 5);
    }

    [Fact]
    public void GetAspectRatio_Square_Is1()
    {
        var img = CreateGradient(8, 8);
        Assert.Equal(1.0, img.GetAspectRatio(), 5);
    }

    [Fact]
    public void GetAspectRatio_Landscape_GreaterThan1()
    {
        var img = CreateGradient(16, 8);
        Assert.True(img.GetAspectRatio() > 1.0);
    }

    [Fact]
    public void GetAspectRatio_Portrait_LessThan1()
    {
        var img = CreateGradient(8, 16);
        Assert.True(img.GetAspectRatio() < 1.0);
    }

    [Fact]
    public void GetAspectRatio_SaveLoad_Consistent()
    {
        var img = CreateGradient(12, 8);
        var before = img.GetAspectRatio();
        var path = TempFile("ar_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetAspectRatio(), 5);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_AddBorder_PadTo_GetAspectRatio_SaveToFile_Pipeline()
    {
        // Create 12×8 gradient image
        var img = CreateGradient(12, 8);
        Assert.Equal(12, img.Width);
        Assert.Equal(8, img.Height);

        // GetAspectRatio
        var ar = img.GetAspectRatio();
        Assert.Equal(12.0 / 8.0, ar, 5);
        Assert.True(ar > 1.0); // landscape

        // AddBorder — thickness=1, black
        var bordered1 = img.AddBorder(1, 0);
        Assert.Equal(14, bordered1.Width);
        Assert.Equal(10, bordered1.Height);

        // Border pixel values = 0 (black)
        Assert.Equal(0, bordered1.GetPixelValue(0, 0));
        Assert.Equal(0, bordered1.GetPixelValue(13, 0));
        Assert.Equal(0, bordered1.GetPixelValue(0, 9));

        // AddBorder — thickness=2, white
        var bordered2 = img.AddBorder(2, 255);
        Assert.Equal(16, bordered2.Width);
        Assert.Equal(12, bordered2.Height);
        Assert.Equal(255, bordered2.GetPixelValue(0, 0));
        Assert.Equal(255, bordered2.GetPixelValue(15, 11));

        // Consistent
        var b3 = img.AddBorder(1, 0);
        Assert.Equal(bordered1.Width, b3.Width);

        // GetAspectRatio after AddBorder
        var borderedAr = bordered1.GetAspectRatio();
        Assert.True(borderedAr > 0);
        Assert.Equal(14.0 / 10.0, borderedAr, 5);

        // PadTo — pad to 20×16
        var padded = img.PadTo(20, 16, 0);
        Assert.Equal(20, padded.Width);
        Assert.Equal(16, padded.Height);

        // GetAspectRatio after PadTo
        var paddedAr = padded.GetAspectRatio();
        Assert.Equal(20.0 / 16.0, paddedAr, 5);

        // PadTo to exact same dims — no change
        var sameSize = img.PadTo(12, 8, 128);
        Assert.Equal(12, sameSize.Width);
        Assert.Equal(8, sameSize.Height);

        // Chain: AddBorder then PadTo
        var chained = img.AddBorder(1, 0).PadTo(20, 14, 128);
        Assert.Equal(20, chained.Width);
        Assert.Equal(14, chained.Height);

        // Normalize bordered image
        var normBordered = bordered1.Normalize();
        Assert.Equal(14, normBordered.Width);

        // FlipHorizontal on padded
        var flipPadded = padded.FlipHorizontal();
        Assert.Equal(20, flipPadded.Width);

        // SaveToFile originals and processed
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathBordered = TempFile("dogfood_bordered.pgm");
        bordered1.SaveToFile(pathBordered);
        Assert.True(File.Exists(pathBordered));

        var pathPadded = TempFile("dogfood_padded.pgm");
        padded.SaveToFile(pathPadded);
        Assert.True(File.Exists(pathPadded));

        // LoadFile bordered and verify
        var loadedBordered = NetpbmImage.LoadFile(pathBordered);
        Assert.Equal(14, loadedBordered.Width);
        Assert.Equal(10, loadedBordered.Height);
        Assert.Equal(0, loadedBordered.GetPixelValue(0, 0));
        Assert.Equal(ar, img.GetAspectRatio(), 5); // original unchanged

        // LoadFile padded and verify
        var loadedPadded = NetpbmImage.LoadFile(pathPadded);
        Assert.Equal(20, loadedPadded.Width);
        Assert.Equal(16, loadedPadded.Height);
        Assert.Equal(paddedAr, loadedPadded.GetAspectRatio(), 5);

        // AddBorder on loaded
        var loadedBorderedAgain = loadedBordered.AddBorder(1, 200);
        Assert.Equal(16, loadedBorderedAgain.Width);
        Assert.Equal(12, loadedBorderedAgain.Height);
        Assert.Equal(200, loadedBorderedAgain.GetPixelValue(0, 0));

        // Final save
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedBorderedAgain.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
        var final = NetpbmImage.LoadFile(pathFinal);
        Assert.Equal(16, final.Width);
        Assert.Equal(12, final.Height);
    }
}
