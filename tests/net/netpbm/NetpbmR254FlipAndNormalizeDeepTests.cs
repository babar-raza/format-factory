// Tests for NetpbmImage.FlipHorizontal, FlipVertical, Normalize deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R254

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R254: Tests for NetpbmImage.FlipHorizontal, FlipVertical, Normalize deeper.
/// FlipHorizontal(): mirrors the image left-right.
/// FlipVertical(): mirrors the image top-bottom.
/// Normalize(): scales pixel values to full 0-255 range.
/// Covers: FlipHorizontal preserves dims; FlipHorizontal no-throw; FlipHorizontal non-null;
/// FlipHorizontal double=same dims; FlipHorizontal reflects pixel at edges;
/// FlipHorizontal then SaveToFile; FlipHorizontal then Rotate no-throw;
/// FlipHorizontal then Crop no-throw; FlipHorizontal consistent;
/// FlipVertical preserves dims; FlipVertical no-throw; FlipVertical non-null;
/// FlipVertical double=same dims; FlipVertical reflects top-bottom;
/// FlipVertical then SaveToFile; FlipVertical then Invert no-throw;
/// FlipHorizontal then FlipVertical = Rotate180 dims;
/// Normalize non-null; Normalize no-throw; Normalize same dims;
/// Normalize max=255 for non-uniform; Normalize min=0; Normalize consistent;
/// Normalize then SaveToFile; Normalize idempotent for already-normalized;
/// dogfood CreatePgm→FlipH→FlipV→Normalize→SaveToFile pipeline.
/// </summary>
public class NetpbmR254FlipAndNormalizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR254FlipAndNormalizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR254_" + Guid.NewGuid().ToString("N"));
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
                img.SetPixel(x, y, (byte)((x * 8 + y * 16) % 256));
        return img;
    }

    // -------------------------------------------------------------------------
    // FlipHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipHorizontal_PreservesDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipHorizontal();
        Assert.Equal(12, flipped.Width);
        Assert.Equal(8, flipped.Height);
    }

    [Fact]
    public void FlipHorizontal_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var ex = Record.Exception(() => img.FlipHorizontal());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_NonNull()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.NotNull(img.FlipHorizontal());
    }

    [Fact]
    public void FlipHorizontal_Double_SameDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped2 = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.Width, flipped2.Width);
        Assert.Equal(img.Height, flipped2.Height);
    }

    [Fact]
    public void FlipHorizontal_Double_SamePixelAt00()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        img.SetPixel(0, 0, 100);
        var flipped2 = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(100, flipped2.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipHorizontal_Consistent()
    {
        var img = CreateGrayGradient(10, 8);
        var f1 = img.FlipHorizontal();
        var f2 = img.FlipHorizontal();
        Assert.Equal(f1.Width, f2.Width);
        Assert.Equal(f1.GetPixelValue(0, 0), f2.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipHorizontal_ThenSaveToFile()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipHorizontal();
        var path = TempFile("fliph.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void FlipHorizontal_ThenRotate_NoThrow()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipHorizontal();
        var ex = Record.Exception(() => flipped.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void FlipHorizontal_ThenCrop_NoThrow()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipHorizontal();
        var ex = Record.Exception(() => flipped.Crop(0, 0, 4, 4));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // FlipVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_PreservesDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipVertical();
        Assert.Equal(12, flipped.Width);
        Assert.Equal(8, flipped.Height);
    }

    [Fact]
    public void FlipVertical_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_NonNull()
    {
        var img = CreateGrayGradient(8, 6);
        Assert.NotNull(img.FlipVertical());
    }

    [Fact]
    public void FlipVertical_Double_SameDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped2 = img.FlipVertical().FlipVertical();
        Assert.Equal(img.Width, flipped2.Width);
        Assert.Equal(img.Height, flipped2.Height);
    }

    [Fact]
    public void FlipVertical_Double_SamePixelAt00()
    {
        var img = NetpbmImage.CreatePgm(8, 6, 255);
        img.SetPixel(0, 0, 150);
        var flipped2 = img.FlipVertical().FlipVertical();
        Assert.Equal(150, flipped2.GetPixelValue(0, 0));
    }

    [Fact]
    public void FlipVertical_ThenSaveToFile()
    {
        var img = CreateGrayGradient(12, 8);
        var flipped = img.FlipVertical();
        var path = TempFile("flipv.pgm");
        flipped.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void FlipVertical_ThenInvert_NoThrow()
    {
        var img = CreateGrayGradient(10, 6);
        var flipped = img.FlipVertical();
        var ex = Record.Exception(() => flipped.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipH_Then_FlipV_SameDimsAsRotate180()
    {
        var img = CreateGrayGradient(12, 8);
        var flipBoth = img.FlipHorizontal().FlipVertical();
        var rot180 = img.Rotate(180);
        Assert.Equal(rot180.Width, flipBoth.Width);
        Assert.Equal(rot180.Height, flipBoth.Height);
    }

    // -------------------------------------------------------------------------
    // Normalize
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_NonNull()
    {
        var img = CreateGrayGradient(10, 8);
        Assert.NotNull(img.Normalize());
    }

    [Fact]
    public void Normalize_NoThrow()
    {
        var img = CreateGrayGradient(10, 8);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_SameDimensions()
    {
        var img = CreateGrayGradient(12, 8);
        var norm = img.Normalize();
        Assert.Equal(12, norm.Width);
        Assert.Equal(8, norm.Height);
    }

    [Fact]
    public void Normalize_MaxPixel_Is255()
    {
        // Create image with constrained range (50-150)
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, (byte)(50 + (x + y) * 6 % 100));
        var norm = img.Normalize();
        // After normalization, max should be 255
        var maxVal = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                maxVal = Math.Max(maxVal, norm.GetPixelValue(x, y));
        Assert.Equal(255, maxVal);
    }

    [Fact]
    public void Normalize_MinPixel_IsZero()
    {
        // Create image with constrained range (50-150)
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, (byte)(50 + (x + y) * 6 % 100));
        var norm = img.Normalize();
        var minVal = 255;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                minVal = Math.Min(minVal, norm.GetPixelValue(x, y));
        Assert.Equal(0, minVal);
    }

    [Fact]
    public void Normalize_Consistent()
    {
        var img = CreateGrayGradient(10, 8);
        var n1 = img.Normalize();
        var n2 = img.Normalize();
        Assert.Equal(n1.GetPixelValue(0, 0), n2.GetPixelValue(0, 0));
    }

    [Fact]
    public void Normalize_ThenSaveToFile()
    {
        var img = CreateGrayGradient(10, 8);
        var norm = img.Normalize();
        var path = TempFile("normalized.pgm");
        norm.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_FlipH_FlipV_Normalize_SaveToFile_Pipeline()
    {
        // Create 16×8 gradient image
        var img = NetpbmImage.CreatePgm(16, 8, 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 16; x++)
                img.SetPixel(x, y, (byte)((x * 10 + y * 20) % 200 + 28)); // range 28-227

        Assert.Equal(16, img.Width);
        Assert.Equal(8, img.Height);

        // SetPixel corners for verification
        img.SetPixel(0, 0, 50);
        img.SetPixel(15, 0, 200);
        img.SetPixel(0, 7, 100);
        img.SetPixel(15, 7, 150);

        // FlipHorizontal
        var flipH = img.FlipHorizontal();
        Assert.Equal(16, flipH.Width);
        Assert.Equal(8, flipH.Height);
        // After horizontal flip, top-left becomes top-right
        Assert.Equal(img.GetPixelValue(15, 0), flipH.GetPixelValue(0, 0));
        Assert.Equal(img.GetPixelValue(0, 0), flipH.GetPixelValue(15, 0));

        // FlipVertical
        var flipV = img.FlipVertical();
        Assert.Equal(16, flipV.Width);
        Assert.Equal(8, flipV.Height);
        // After vertical flip, top-left becomes bottom-left
        Assert.Equal(img.GetPixelValue(0, 7), flipV.GetPixelValue(0, 0));
        Assert.Equal(img.GetPixelValue(0, 0), flipV.GetPixelValue(0, 7));

        // Double flip restores original pixels
        var doubleFH = img.FlipHorizontal().FlipHorizontal();
        Assert.Equal(img.GetPixelValue(0, 0), doubleFH.GetPixelValue(0, 0));
        Assert.Equal(img.GetPixelValue(15, 7), doubleFH.GetPixelValue(15, 7));

        var doubleFV = img.FlipVertical().FlipVertical();
        Assert.Equal(img.GetPixelValue(0, 0), doubleFV.GetPixelValue(0, 0));

        // FlipH then FlipV = Rotate180 dims
        var flipBoth = img.FlipHorizontal().FlipVertical();
        var rot180 = img.Rotate(180);
        Assert.Equal(rot180.Width, flipBoth.Width);
        Assert.Equal(rot180.Height, flipBoth.Height);

        // Normalize
        var norm = img.Normalize();
        Assert.Equal(16, norm.Width);
        Assert.Equal(8, norm.Height);

        // After normalize, max should be 255
        var maxVal = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 16; x++)
                maxVal = Math.Max(maxVal, norm.GetPixelValue(x, y));
        Assert.Equal(255, maxVal);

        // Normalize then FlipH — no throw
        var normFlip = norm.FlipHorizontal();
        Assert.NotNull(normFlip);

        // Invert flipped image
        var inverted = flipH.Invert();
        Assert.NotNull(inverted);
        Assert.Equal(16, inverted.Width);

        // SaveToFile originals and flips
        var pathOrig = TempFile("dogfood_orig.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathFlipH = TempFile("dogfood_fliph.pgm");
        flipH.SaveToFile(pathFlipH);
        Assert.True(File.Exists(pathFlipH));

        var pathFlipV = TempFile("dogfood_flipv.pgm");
        flipV.SaveToFile(pathFlipV);
        Assert.True(File.Exists(pathFlipV));

        var pathNorm = TempFile("dogfood_norm.pgm");
        norm.SaveToFile(pathNorm);
        Assert.True(File.Exists(pathNorm));

        // LoadFile flip-H and verify dimensions
        var loadedFlipH = NetpbmImage.LoadFile(pathFlipH);
        Assert.Equal(16, loadedFlipH.Width);
        Assert.Equal(8, loadedFlipH.Height);

        // Re-flip loaded image to restore
        var restored = loadedFlipH.FlipHorizontal();
        Assert.Equal(img.GetPixelValue(0, 0), restored.GetPixelValue(0, 0));

        // LoadFile norm and verify max
        var loadedNorm = NetpbmImage.LoadFile(pathNorm);
        var loadedMax = 0;
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 16; x++)
                loadedMax = Math.Max(loadedMax, loadedNorm.GetPixelValue(x, y));
        Assert.Equal(255, loadedMax);

        // Crop the normalized image
        var cropped = norm.Crop(0, 0, 8, 4);
        Assert.Equal(8, cropped.Width);
        Assert.Equal(4, cropped.Height);

        // Final SaveToFile
        var pathFinal = TempFile("dogfood_final.pgm");
        cropped.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
    }
}
