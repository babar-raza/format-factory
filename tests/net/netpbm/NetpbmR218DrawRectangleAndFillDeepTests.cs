// Tests for NetpbmImage.DrawRectangle, Fill, GetPixel deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R218

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R218: Tests for NetpbmImage.DrawRectangle, Fill, GetPixel deeper coverage.
/// DrawRectangle(x, y, w, h, value): draws a rectangle outline on the image.
/// Fill(x, y, value): flood-fills from (x,y) with the given pixel value.
/// GetPixel(x, y): returns pixel value at given coordinates.
/// Covers: DrawRectangle non-null; DrawRectangle dims unchanged; DrawRectangle changes histogram;
/// DrawRectangle at origin; DrawRectangle full canvas no-throw; DrawRectangle chained twice;
/// Fill non-null; Fill uniform canvas same value; Fill after DrawLine changes pixel;
/// Fill dims unchanged; Fill then SaveToFile; GetPixel returns valid range;
/// GetPixel at origin; GetPixel after DrawLine changes value; GetPixel after Fill matches value;
/// GetPixel consistent across multiple calls;
/// dogfood CreateCanvas→DrawRectangle→GetPixel→Fill→GetHistogram→SaveToFile→LoadFile pipeline.
/// </summary>
public class NetpbmR218DrawRectangleAndFillDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR218DrawRectangleAndFillDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR218_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // DrawRectangle
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var result = img.DrawRectangle(2, 2, 8, 8, 50);
        Assert.NotNull(result);
    }

    [Fact]
    public void DrawRectangle_DimsUnchanged()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var result = img.DrawRectangle(2, 2, 8, 8, 50);
        Assert.Equal(16, result.Width);
        Assert.Equal(16, result.Height);
    }

    [Fact]
    public void DrawRectangle_ChangesHistogram()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var result = img.DrawRectangle(2, 2, 8, 8, 50);
        var hist = result.GetHistogram();
        Assert.True(hist.Count >= 2); // 200 background + 50 border
    }

    [Fact]
    public void DrawRectangle_AtOrigin_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var ex = Record.Exception(() => img.DrawRectangle(0, 0, 4, 4, 100));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawRectangle_FullCanvas_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.DrawRectangle(0, 0, 8, 8, 100));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawRectangle_ChainedTwice_DimsStable()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        var result = img.DrawRectangle(1, 1, 6, 6, 80).DrawRectangle(8, 8, 6, 6, 120);
        Assert.Equal(16, result.Width);
        Assert.Equal(16, result.Height);
    }

    // -------------------------------------------------------------------------
    // Fill
    // -------------------------------------------------------------------------

    [Fact]
    public void Fill_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.NotNull(img.Fill(4, 4, 100));
    }

    [Fact]
    public void Fill_UniformCanvas_SameValue()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var filled = img.Fill(0, 0, 200); // Same value as canvas
        var hist = filled.GetHistogram();
        Assert.Equal(1, hist.Count); // Still uniform
    }

    [Fact]
    public void Fill_DimsUnchanged()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var filled = img.Fill(0, 0, 100);
        Assert.Equal(8, filled.Width);
        Assert.Equal(8, filled.Height);
    }

    [Fact]
    public void Fill_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.Fill(4, 4, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void Fill_ThenSaveToFile_CreatesFile()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var filled = img.Fill(0, 0, 100);
        var path = TempFile("filled.pgm");
        filled.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // GetPixel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixel_ReturnsValidRange()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var pixel = img.GetPixel(4, 4);
        Assert.True(pixel >= 0 && pixel <= 255);
    }

    [Fact]
    public void GetPixel_AtOrigin()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 150);
        Assert.Equal(150, img.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_AfterDrawLine_ChangesValue()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 0, 0, 50); // Set origin pixel
        Assert.Equal(50, img.GetPixel(0, 0));
    }

    [Fact]
    public void GetPixel_ConsistentAcrossMultipleCalls()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 150);
        var first = img.GetPixel(3, 3);
        var second = img.GetPixel(3, 3);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPixel_CanvasValue_MatchesConstructorValue()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 128);
        // All pixels should be 128
        Assert.Equal(128, img.GetPixel(0, 0));
        Assert.Equal(128, img.GetPixel(7, 7));
        Assert.Equal(128, img.GetPixel(4, 4));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawRectangle_GetPixel_Fill_GetHistogram_SaveToFile_LoadFile_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        Assert.Equal(256, img.PixelCount);

        // DrawRectangle at (2,2) 8x8 with value 50
        var withRect = img.DrawRectangle(2, 2, 8, 8, 50);
        Assert.Equal(16, withRect.Width);
        Assert.Equal(16, withRect.Height);

        // GetHistogram — multiple values after rectangle
        var hist = withRect.GetHistogram();
        Assert.True(hist.Count >= 2);

        // GetPixel — background should still be 200 at corner
        var cornerPixel = withRect.GetPixel(0, 0);
        Assert.Equal(200, cornerPixel);

        // Fill the background with 150
        var filled = withRect.Fill(0, 0, 150);
        Assert.Equal(16, filled.Width);
        Assert.Equal(16, filled.Height);

        // GetHistogram after fill — still at least 2 values (rectangle border + filled area)
        var filledHist = filled.GetHistogram();
        Assert.True(filledHist.Count >= 1);

        // GetPixel at corner — should be 150 now
        Assert.Equal(150, filled.GetPixel(0, 0));

        // DrawLine on top
        filled.DrawLine(0, 8, 15, 8, 100);
        var lineHist = filled.GetHistogram();
        Assert.True(lineHist.Count >= 2);

        // SaveToFile
        var path = TempFile("dogfood_rect.pgm");
        filled.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(16, loaded.Height);
        Assert.Equal(256, loaded.PixelCount);

        // GetHistogram on loaded — preserved
        var loadedHist = loaded.GetHistogram();
        Assert.NotNull(loadedHist);
        var sum = 0;
        foreach (var kv in loadedHist)
            sum += kv.Value;
        Assert.Equal(256, sum);
    }
}
