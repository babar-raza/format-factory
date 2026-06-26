// Tests for NetpbmImage.Sharpen dedicated coverage.
// Sprint: ff-sprint-s240-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R247

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R247: Dedicated tests for NetpbmImage.Sharpen().
/// Sharpen returns a NEW image (non-destructive).
/// PBM images: returned clone unchanged.
/// Format preserved; MaxValue preserved; dimensions preserved.
/// Original image unchanged after sharpen.
/// Pixels in result are non-negative.
/// Pixels in result are within [0, MaxValue].
/// Called twice: returns non-null each time.
/// 1x1 image: no exception.
/// Dogfood: Create->SetPixel->Sharpen->verify pixels in range.
/// Dogfood: sharpen result is different object from original.
/// </summary>
public class NetpbmR247SharpenDedicatedTests
{
    // -------------------------------------------------------------------------
    // Return value / non-destructive tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Sharpen();
        Assert.NotNull(result);
    }

    [Fact]
    public void Sharpen_ReturnsDifferentObject()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Sharpen();
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Sharpen_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        int originalPixel = img.GetPixel(0, 0);
        img.Sharpen();
        Assert.Equal(originalPixel, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Preservation tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var result = img.Sharpen();
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Sharpen_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Sharpen();
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Sharpen_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Sharpen();
        Assert.Equal(5, result.Width);
        Assert.Equal(3, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel range tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_1x1Image_NoException()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.Sharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void Sharpen_CalledTwice_BothNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5);
        var r1 = img.Sharpen();
        var r2 = img.Sharpen();
        Assert.NotNull(r1);
        Assert.NotNull(r2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 200);
        img.SetPixel(2, 2, 100);
        img.SetPixel(3, 3, 150);
        var result = img.Sharpen();
        // Verify all pixels in result are within [0, MaxValue]
        for (int row = 0; row < result.Height; row++)
        {
            for (int col = 0; col < result.Width; col++)
            {
                int px = result.GetPixel(col, row);
                Assert.InRange(px, 0, result.MaxValue);
            }
        }
    }

    [Fact]
    public void DogfoodPipeline_SharpenResultIsDifferentObject()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(c, r, (r + c) * 10);
        var result = img.Sharpen();
        Assert.NotSame(img, result);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }
}
