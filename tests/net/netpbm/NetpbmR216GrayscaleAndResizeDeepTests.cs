// Tests for NetpbmImage.ToGrayscale, Resize, GetHistogram deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R216: Tests for NetpbmImage.ToGrayscale, Resize, GetHistogram deeper coverage.
/// ToGrayscale(): converts image to grayscale (P2/P5 format).
/// Resize(width, height): resizes the image to the given dimensions.
/// GetHistogram(): returns pixel value frequency distribution.
/// Covers: ToGrayscale non-null; ToGrayscale preserves pixel count; ToGrayscale dims unchanged;
/// ToGrayscale result parseable; ToGrayscale on already-gray no-throw;
/// Resize non-null; Resize to smaller has new dims; Resize to larger has new dims;
/// Resize pixel count = new_w*new_h; Resize no-throw on same size;
/// Resize then SaveToFile; GetHistogram non-null; GetHistogram non-empty;
/// GetHistogram sum equals pixel count; GetHistogram uniform image has 1 key;
/// GetHistogram after DrawLine has more keys;
/// dogfood CreateCanvas→DrawLine→ToGrayscale→Resize→GetHistogram→SaveToFile→LoadFile pipeline.
/// </summary>
public class NetpbmR216GrayscaleAndResizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR216GrayscaleAndResizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR216_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotNull(img.ToGrayscale());
    }

    [Fact]
    public void ToGrayscale_PreservesPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var gray = img.ToGrayscale();
        Assert.Equal(img.PixelCount, gray.PixelCount);
    }

    [Fact]
    public void ToGrayscale_DimsUnchanged()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, 150);
        var gray = img.ToGrayscale();
        Assert.Equal(img.Width, gray.Width);
        Assert.Equal(img.Height, gray.Height);
    }

    [Fact]
    public void ToGrayscale_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 128);
        var ex = Record.Exception(() => img.ToGrayscale());
        Assert.Null(ex);
    }

    [Fact]
    public void ToGrayscale_AfterDrawLine_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 7, 7, 50);
        var ex = Record.Exception(() => img.ToGrayscale());
        Assert.Null(ex);
    }

    [Fact]
    public void ToGrayscale_ChainedTwice_ConsistentDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var gray1 = img.ToGrayscale();
        var gray2 = gray1.ToGrayscale();
        Assert.Equal(img.Width, gray2.Width);
        Assert.Equal(img.Height, gray2.Height);
    }

    // -------------------------------------------------------------------------
    // Resize
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotNull(img.Resize(4, 4));
    }

    [Fact]
    public void Resize_ToSmaller_HasNewDims()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
    }

    [Fact]
    public void Resize_ToLarger_HasNewDims()
    {
        var img = NetpbmImage.CreateCanvas(4, 4, 200);
        var resized = img.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
    }

    [Fact]
    public void Resize_PixelCountMatchesNewDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var resized = img.Resize(4, 6);
        Assert.Equal(4 * 6, resized.PixelCount);
    }

    [Fact]
    public void Resize_SameSize_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.Resize(8, 8));
        Assert.Null(ex);
    }

    [Fact]
    public void Resize_ThenSaveToFile_CreatesFile()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var resized = img.Resize(4, 4);
        var path = TempFile("resized.pgm");
        resized.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_NonEmpty()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotEmpty(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var hist = img.GetHistogram();
        var sum = 0;
        foreach (var kv in hist)
            sum += kv.Value;
        Assert.Equal(img.PixelCount, sum);
    }

    [Fact]
    public void GetHistogram_UniformImage_OneKey()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 128);
        var hist = img.GetHistogram();
        Assert.Equal(1, hist.Count);
    }

    [Fact]
    public void GetHistogram_AfterDrawLine_MoreKeys()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 7, 7, 50);
        var hist = img.GetHistogram();
        Assert.True(hist.Count >= 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawLine_ToGrayscale_Resize_GetHistogram_SaveToFile_LoadFile_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        Assert.Equal(256, img.PixelCount);

        // DrawLine
        img.DrawLine(0, 0, 15, 15, 50);
        img.DrawLine(0, 15, 15, 0, 100);

        // GetHistogram — multiple values
        var hist = img.GetHistogram();
        Assert.True(hist.Count >= 2);

        // ToGrayscale
        var gray = img.ToGrayscale();
        Assert.NotNull(gray);
        Assert.Equal(16, gray.Width);
        Assert.Equal(16, gray.Height);

        // Resize to 8x8
        var resized = gray.Resize(8, 8);
        Assert.Equal(8, resized.Width);
        Assert.Equal(8, resized.Height);
        Assert.Equal(64, resized.PixelCount);

        // GetHistogram on resized
        var resizedHist = resized.GetHistogram();
        Assert.NotNull(resizedHist);
        Assert.True(resizedHist.Count >= 1);

        // SaveToFile
        var path = TempFile("grayscale_resized.pgm");
        resized.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(8, loaded.Width);
        Assert.Equal(8, loaded.Height);
        Assert.Equal(64, loaded.PixelCount);

        // GetHistogram on loaded
        var loadedHist = loaded.GetHistogram();
        Assert.NotNull(loadedHist);
        var sum = 0;
        foreach (var kv in loadedHist)
            sum += kv.Value;
        Assert.Equal(64, sum);

        // Resize loaded to 4x4
        var small = loaded.Resize(4, 4);
        Assert.Equal(4, small.Width);
        Assert.Equal(4, small.Height);
        Assert.Equal(16, small.PixelCount);
    }
}
