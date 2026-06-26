// Tests for NetpbmImage canvas creation and DrawPixel/DrawLine deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R221

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R221: Tests for NetpbmImage canvas creation and DrawPixel/DrawLine deeper coverage.
/// CreateCanvas(w, h, value): creates a blank image with uniform pixel value.
/// DrawPixel(x, y, value): sets a single pixel at (x,y) to value.
/// DrawLine(x1, y1, x2, y2, value): draws a line between two points.
/// Covers: CreateCanvas positive dims; CreateCanvas correct pixel count; CreateCanvas uniform value;
/// CreateCanvas different sizes; DrawPixel no throw; DrawPixel GetPixel reflects;
/// DrawPixel multiple different locations; DrawPixel at corners;
/// DrawLine no throw; DrawLine changes histogram; DrawLine horizontal;
/// DrawLine vertical; DrawLine chained twice; DrawLine then SaveToFile;
/// DrawLine GetPixel at start point; PixelCount = Width * Height;
/// dogfood CreateCanvas→DrawPixel×4→DrawLine×2→GetHistogram→SaveToFile→LoadFile pipeline.
/// </summary>
public class NetpbmR221CanvasAndDrawPixelDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR221CanvasAndDrawPixelDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR221_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CreateCanvas
    // -------------------------------------------------------------------------

    [Fact]
    public void CreateCanvas_PositiveDims()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        Assert.True(img.Width > 0);
        Assert.True(img.Height > 0);
    }

    [Fact]
    public void CreateCanvas_CorrectPixelCount()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, 200);
        Assert.Equal(60, img.PixelCount);
    }

    [Fact]
    public void CreateCanvas_UniformValue()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 150);
        Assert.Equal(150, img.GetPixel(0, 0));
        Assert.Equal(150, img.GetPixel(4, 4));
        Assert.Equal(150, img.GetPixel(7, 7));
    }

    [Fact]
    public void CreateCanvas_DifferentSizes()
    {
        var img1 = NetpbmImage.CreateCanvas(4, 4, 100);
        var img2 = NetpbmImage.CreateCanvas(16, 8, 200);
        Assert.Equal(16, img1.PixelCount);
        Assert.Equal(128, img2.PixelCount);
    }

    [Fact]
    public void CreateCanvas_PixelCountEqualsWidthTimesHeight()
    {
        var img = NetpbmImage.CreateCanvas(12, 7, 100);
        Assert.Equal(12 * 7, img.PixelCount);
    }

    // -------------------------------------------------------------------------
    // DrawPixel
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawPixel_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.DrawPixel(4, 4, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawPixel_GetPixel_Reflects()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawPixel(4, 4, 50);
        Assert.Equal(50, img.GetPixel(4, 4));
    }

    [Fact]
    public void DrawPixel_MultipleLocations()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawPixel(0, 0, 10);
        img.DrawPixel(4, 4, 20);
        img.DrawPixel(7, 7, 30);
        Assert.Equal(10, img.GetPixel(0, 0));
        Assert.Equal(20, img.GetPixel(4, 4));
        Assert.Equal(30, img.GetPixel(7, 7));
    }

    [Fact]
    public void DrawPixel_AtCorners()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawPixel(0, 0, 10);
        img.DrawPixel(7, 0, 20);
        img.DrawPixel(0, 7, 30);
        img.DrawPixel(7, 7, 40);
        Assert.Equal(10, img.GetPixel(0, 0));
        Assert.Equal(40, img.GetPixel(7, 7));
    }

    [Fact]
    public void DrawPixel_Overwrite_LastValueWins()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawPixel(3, 3, 50);
        img.DrawPixel(3, 3, 100);
        Assert.Equal(100, img.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.DrawLine(0, 0, 7, 7, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_ChangesHistogram()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 7, 7, 50);
        var hist = img.GetHistogram();
        Assert.True(hist.Count >= 2);
    }

    [Fact]
    public void DrawLine_Horizontal_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.DrawLine(0, 4, 7, 4, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_Vertical_NoThrow()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        var ex = Record.Exception(() => img.DrawLine(4, 0, 4, 7, 50));
        Assert.Null(ex);
    }

    [Fact]
    public void DrawLine_ChainedTwice_MoreHistogramValues()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 7, 7, 50);
        img.DrawLine(0, 7, 7, 0, 100);
        var hist = img.GetHistogram();
        Assert.True(hist.Count >= 2);
    }

    [Fact]
    public void DrawLine_ThenSaveToFile_CreatesFile()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 7, 7, 50);
        var path = TempFile("drawline.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DrawLine_GetPixelAtStartPoint()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, 200);
        img.DrawLine(0, 0, 0, 0, 75); // Single point line at origin
        Assert.Equal(75, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_DrawPixel_DrawLine_GetHistogram_SaveToFile_LoadFile_Pipeline()
    {
        var img = NetpbmImage.CreateCanvas(16, 16, 200);
        Assert.Equal(256, img.PixelCount);
        Assert.Equal(200, img.GetPixel(0, 0));

        // DrawPixel at 4 corners
        img.DrawPixel(0, 0, 10);
        img.DrawPixel(15, 0, 20);
        img.DrawPixel(0, 15, 30);
        img.DrawPixel(15, 15, 40);
        Assert.Equal(10, img.GetPixel(0, 0));
        Assert.Equal(40, img.GetPixel(15, 15));

        // DrawLine × 2
        img.DrawLine(0, 8, 15, 8, 100); // Horizontal midline
        img.DrawLine(8, 0, 8, 15, 150); // Vertical midline

        // GetHistogram — multiple values
        var hist = img.GetHistogram();
        Assert.True(hist.Count >= 3); // 200 bg + 100 hline + 150 vline

        // Sum check
        var sum = 0;
        foreach (var kv in hist)
            sum += kv.Value;
        Assert.Equal(256, sum);

        // SaveToFile
        var path = TempFile("canvas_draw.pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = NetpbmImage.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.Equal(16, loaded.Width);
        Assert.Equal(16, loaded.Height);
        Assert.Equal(256, loaded.PixelCount);

        // GetPixel on loaded — drawn pixels preserved
        Assert.Equal(10, loaded.GetPixel(0, 0));
        Assert.Equal(40, loaded.GetPixel(15, 15));

        // GetHistogram on loaded preserved
        var loadedHist = loaded.GetHistogram();
        Assert.True(loadedHist.Count >= 2);

        // Draw more on loaded
        loaded.DrawPixel(8, 8, 255);
        Assert.Equal(255, loaded.GetPixel(8, 8));
    }
}
