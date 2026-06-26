// Tests for NetpbmImage.DrawRectangle and DrawLine operations.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R173

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R173: Tests for NetpbmImage.DrawRectangle and DrawLine operations.
/// DrawRectangle(top, left, height, width, fill, filled): draws a rectangle.
/// DrawLine(x0, y0, x1, y1, fill): draws a line using Bresenham algorithm.
/// Covers: DrawRectangle filled leaves fill pixels; DrawRectangle does not change dimensions;
/// DrawRectangle single cell fills one pixel; DrawRectangle corner pixel;
/// DrawRectangle unfilled leaves interior unchanged; DrawRectangle full image;
/// DrawLine from (0,0) to (0,n) horizontal; DrawLine from (0,0) to (n,0) vertical;
/// DrawLine does not change dimensions; DrawLine single pixel;
/// DrawLine then DrawRectangle pipeline; DrawRectangle then Clone;
/// dogfood Create->DrawRectangle->DrawLine->SaveToFile->reload check.
/// </summary>
public class NetpbmR173DrawRectangleAndLineTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR173DrawRectangleAndLineTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "NetpbmR173_" + System.Guid.NewGuid().ToString("N"));
        System.IO.Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (System.IO.Directory.Exists(_tempDir))
            System.IO.Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) =>
        System.IO.Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM, fill);

    // -------------------------------------------------------------------------
    // DrawRectangle (filled)
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawRectangle_Filled_PixelsInsideHaveFillValue()
    {
        var img = CreateGray(10, 10, 0);
        img.DrawRectangle(2, 2, 4, 4, 200, filled: true);
        Assert.Equal(200, img.GetPixel(3, 3)); // inside region
    }

    [Fact]
    public void DrawRectangle_Filled_DoesNotChangeDimensions()
    {
        var img = CreateGray(8, 8, 0);
        img.DrawRectangle(1, 1, 4, 4, 255, filled: true);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void DrawRectangle_Filled_SingleCell_FillsOnePixel()
    {
        var img = CreateGray(5, 5, 0);
        img.DrawRectangle(2, 3, 1, 1, 150, filled: true);
        Assert.Equal(150, img.GetPixel(2, 3));
    }

    [Fact]
    public void DrawRectangle_Filled_CornerPixel()
    {
        var img = CreateGray(6, 6, 0);
        img.DrawRectangle(0, 0, 6, 6, 111, filled: true);
        Assert.Equal(111, img.GetPixel(0, 0));
        Assert.Equal(111, img.GetPixel(5, 5));
    }

    [Fact]
    public void DrawRectangle_Unfilled_InteriorUnchanged()
    {
        var img = CreateGray(8, 8, 50);
        img.DrawRectangle(1, 1, 4, 4, 200, filled: false);
        // Interior should still be 50 (unfilled = only border)
        Assert.Equal(50, img.GetPixel(3, 3)); // interior
    }

    [Fact]
    public void DrawRectangle_Unfilled_BorderHasFillValue()
    {
        var img = CreateGray(8, 8, 0);
        img.DrawRectangle(1, 1, 5, 5, 200, filled: false);
        // Top-left corner of rectangle at (1,1)
        Assert.Equal(200, img.GetPixel(1, 1));
    }

    // -------------------------------------------------------------------------
    // DrawLine
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_Horizontal_StartPixelHasFillValue()
    {
        var img = CreateGray(8, 8, 0);
        img.DrawLine(0, 0, 0, 5, 255); // row 0, col 0 to col 5
        Assert.Equal(255, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_Vertical_StartPixelHasFillValue()
    {
        var img = CreateGray(8, 8, 0);
        img.DrawLine(0, 0, 5, 0, 255); // row 0 to row 5, col 0
        Assert.Equal(255, img.GetPixel(0, 0));
    }

    [Fact]
    public void DrawLine_DoesNotChangeDimensions()
    {
        var img = CreateGray(6, 6, 0);
        img.DrawLine(0, 0, 5, 5, 128);
        Assert.Equal(6, img.Width);
        Assert.Equal(6, img.Height);
    }

    [Fact]
    public void DrawLine_SinglePoint_FillsOnePixel()
    {
        var img = CreateGray(5, 5, 0);
        img.DrawLine(2, 2, 2, 2, 99); // start == end = single point
        Assert.Equal(99, img.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Combined operations
    // -------------------------------------------------------------------------

    [Fact]
    public void DrawLine_ThenDrawRectangle_BothAffectPixels()
    {
        var img = CreateGray(10, 10, 0);
        img.DrawLine(0, 0, 9, 9, 100);
        img.DrawRectangle(3, 3, 3, 3, 200, filled: true);
        // Line pixel at (0,0)
        Assert.Equal(100, img.GetPixel(0, 0));
        // Rect pixel at (4,4) (center of rect)
        Assert.Equal(200, img.GetPixel(4, 4));
    }

    [Fact]
    public void DrawRectangle_ThenClone_IndependentCopy()
    {
        var img = CreateGray(6, 6, 0);
        img.DrawRectangle(1, 1, 3, 3, 180, filled: true);
        var clone = img.Clone();
        clone.SetPixel(2, 2, 0);
        Assert.Equal(180, img.GetPixel(2, 2)); // original unaffected
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->DrawRectangle->DrawLine->SaveToFile->reload
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDrawRectangleDrawLineSaveReload_Pipeline()
    {
        // Create a 10x10 image
        var img = CreateGray(10, 10, 0);

        // Draw a filled 4x4 rectangle
        img.DrawRectangle(2, 2, 4, 4, 150, filled: true);
        Assert.Equal(150, img.GetPixel(3, 3));

        // Draw a diagonal line
        img.DrawLine(0, 0, 9, 9, 255);
        Assert.Equal(255, img.GetPixel(0, 0));

        // Save to file
        var path = TempFile("pipeline.pgm");
        img.SaveToFile(path);
        Assert.True(System.IO.File.Exists(path));

        // Reload and verify dimensions
        var parser = new NetpbmParser();
        var reloaded = parser.Parse(path);
        Assert.Equal(10, reloaded.Width);
        Assert.Equal(10, reloaded.Height);
    }
}
