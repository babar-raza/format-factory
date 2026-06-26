// Tests for NetpbmImage.Normalize dedicated coverage.
// Sprint: ff-sprint-s282-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R290

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R290: Dedicated tests for NetpbmImage.Normalize().
/// Valid call no exception.
/// All pixels in [0, MaxValue] after Normalize.
/// Width unchanged after Normalize.
/// Height unchanged after Normalize.
/// Format unchanged after Normalize.
/// MaxValue unchanged after Normalize.
/// Called twice no exception.
/// All-zero image Normalize no exception.
/// Dogfood: mixed image normalized pixels in range.
/// Dogfood: normalize then get pixel no exception.
/// </summary>
public class NetpbmR290NormalizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Normalize_ValidCall_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_AllPixelsInRange()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 50);
        img.SetPixel(1, 1, 200);
        img.Normalize();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void Normalize_WidthUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.Normalize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void Normalize_HeightUnchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.Normalize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void Normalize_FormatUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.Normalize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void Normalize_MaxValueUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.Normalize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void Normalize_CalledTwice_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 128);
        img.Normalize();
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    [Fact]
    public void Normalize_AllZero_NoException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.Normalize());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedImage_NormalizedPixelsInRange()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM, 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 0, 100);
        img.SetPixel(2, 0, 200);
        img.SetPixel(3, 0, 240);
        img.Normalize();
        for (int x = 0; x < 4; x++)
            Assert.InRange(img.GetPixel(x, 0), 0, img.MaxValue);
    }

    [Fact]
    public void DogfoodPipeline_NormalizeThenGetPixel_NoException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM, 255);
        img.SetPixel(1, 1, 128);
        img.Normalize();
        var ex = Record.Exception(() => img.GetPixel(1, 1));
        Assert.Null(ex);
    }
}
