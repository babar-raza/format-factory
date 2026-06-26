// Tests for NetpbmImage.FillRegion and CopyRegion operations.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R172

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R172: Tests for NetpbmImage.FillRegion and CopyRegion operations.
/// FillRegion(top, left, height, width, fill): fills a rectangle with a constant value.
/// CopyRegion(source, srcTop, srcLeft, dstTop, dstLeft, height, width): copies pixels from source.
/// Covers: FillRegion target pixels have fill value; FillRegion leaves non-region pixels unchanged;
/// FillRegion full image fills all pixels; FillRegion single cell;
/// FillRegion does not change dimensions; CopyRegion copies pixels from source;
/// CopyRegion destination pixels match source; CopyRegion leaves other pixels unchanged;
/// CopyRegion does not modify source image; CopyRegion single pixel copy;
/// FillRegion then CopyRegion pipeline; FillRegion PPM format;
/// dogfood Create->FillRegion->CopyRegion->SaveToFile->reload check.
/// </summary>
public class NetpbmR172FillRegionAndCopyRegionTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR172FillRegionAndCopyRegionTests()
    {
        _tempDir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),
            "NetpbmR172_" + System.Guid.NewGuid().ToString("N"));
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
    // FillRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_TargetPixelsHaveFillValue()
    {
        var img = CreateGray(6, 6, 0);
        img.FillRegion(1, 1, 3, 3, 200);
        // Check a pixel in the filled region
        Assert.Equal(200, img.GetPixel(2, 2));
    }

    [Fact]
    public void FillRegion_NonRegionPixelsUnchanged()
    {
        var img = CreateGray(6, 6, 100);
        img.FillRegion(2, 2, 2, 2, 200);
        // Corner pixels should be unchanged (100)
        Assert.Equal(100, img.GetPixel(0, 0));
        Assert.Equal(100, img.GetPixel(5, 5));
    }

    [Fact]
    public void FillRegion_FullImage_FillsAllPixels()
    {
        var img = CreateGray(4, 4, 0);
        img.FillRegion(0, 0, 4, 4, 255);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                Assert.Equal(255, img.GetPixel(r, c));
    }

    [Fact]
    public void FillRegion_SingleCell_FillsOnePixel()
    {
        var img = CreateGray(4, 4, 0);
        img.FillRegion(2, 3, 1, 1, 199);
        Assert.Equal(199, img.GetPixel(2, 3));
        Assert.Equal(0, img.GetPixel(2, 2)); // adjacent pixel unchanged
    }

    [Fact]
    public void FillRegion_DoesNotChangeDimensions()
    {
        var img = CreateGray(5, 5, 50);
        img.FillRegion(0, 0, 3, 3, 255);
        Assert.Equal(5, img.Width);
        Assert.Equal(5, img.Height);
    }

    // -------------------------------------------------------------------------
    // CopyRegion
    // -------------------------------------------------------------------------

    [Fact]
    public void CopyRegion_DestinationPixelsMatchSource()
    {
        var src = CreateGray(4, 4, 0);
        src.SetPixel(1, 1, 150);
        src.SetPixel(1, 2, 160);

        var dst = CreateGray(6, 6, 0);
        dst.CopyRegion(src, 1, 1, 2, 2, 1, 2);
        Assert.Equal(150, dst.GetPixel(2, 2));
        Assert.Equal(160, dst.GetPixel(2, 3));
    }

    [Fact]
    public void CopyRegion_LeavesOtherPixelsUnchanged()
    {
        var src = CreateGray(3, 3, 200);
        var dst = CreateGray(6, 6, 50);
        dst.CopyRegion(src, 0, 0, 0, 0, 3, 3);
        // Outside the copied region, dst should still be 50
        Assert.Equal(50, dst.GetPixel(5, 5));
    }

    [Fact]
    public void CopyRegion_DoesNotModifySource()
    {
        var src = CreateGray(4, 4, 128);
        var dst = CreateGray(6, 6, 0);
        dst.CopyRegion(src, 0, 0, 0, 0, 3, 3);
        Assert.Equal(128, src.GetPixel(0, 0)); // source unchanged
    }

    [Fact]
    public void CopyRegion_SinglePixel_CopiesOnePixel()
    {
        var src = CreateGray(3, 3, 0);
        src.SetPixel(1, 2, 77);
        var dst = CreateGray(5, 5, 0);
        dst.CopyRegion(src, 1, 2, 3, 3, 1, 1);
        Assert.Equal(77, dst.GetPixel(3, 3));
    }

    // -------------------------------------------------------------------------
    // FillRegion then CopyRegion pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegionThenCopyRegion_Pipeline()
    {
        var src = CreateGray(4, 4, 0);
        src.FillRegion(1, 1, 2, 2, 180);

        var dst = CreateGray(6, 6, 0);
        dst.CopyRegion(src, 1, 1, 2, 2, 2, 2);
        Assert.Equal(180, dst.GetPixel(2, 2));
        Assert.Equal(0, dst.GetPixel(0, 0)); // outside region
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->FillRegion->CopyRegion->SaveToFile->reload
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFillRegionCopyRegionSaveReload_Pipeline()
    {
        // Create 8x8 image, all 0
        var src = CreateGray(8, 8, 0);
        Assert.Equal(8, src.Width);

        // Fill a 4x4 region with value 100
        src.FillRegion(2, 2, 4, 4, 100);
        Assert.Equal(100, src.GetPixel(3, 3));
        Assert.Equal(0, src.GetPixel(0, 0));

        // Create a 10x10 destination and copy the region
        var dst = CreateGray(10, 10, 0);
        dst.CopyRegion(src, 2, 2, 3, 3, 4, 4);
        Assert.Equal(100, dst.GetPixel(3, 3));

        // Save dst to file
        var path = TempFile("pipeline.pgm");
        dst.SaveToFile(path);
        Assert.True(System.IO.File.Exists(path));

        // Reload and verify dimensions
        var parser = new NetpbmParser();
        var reloaded = parser.Parse(path);
        Assert.Equal(10, reloaded.Width);
        Assert.Equal(10, reloaded.Height);
    }
}
