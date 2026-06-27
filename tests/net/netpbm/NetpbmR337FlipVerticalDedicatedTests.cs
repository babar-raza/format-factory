// Tests for NetpbmImage.FlipVertical dedicated coverage.
// Sprint: ff-sprint-s325-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R337

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R337: Dedicated tests for NetpbmImage.FlipVertical().
/// Valid call no exception.
/// Width unchanged after FlipVertical.
/// Height unchanged after FlipVertical.
/// Format unchanged after FlipVertical.
/// MaxValue unchanged after FlipVertical.
/// All pixels in valid range after FlipVertical.
/// Flip twice restores original pixel.
/// All-zero image remains zero after flip.
/// Dogfood: gradient image dims preserved after flip.
/// Dogfood: single row image flip ok.
/// </summary>
public class NetpbmR337FlipVerticalDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FlipVertical_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 13) % 256);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
    }

    [Fact]
    public void FlipVertical_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.FlipVertical();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void FlipVertical_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.FlipVertical();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void FlipVertical_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.FlipVertical();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void FlipVertical_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.FlipVertical();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void FlipVertical_AllPixelsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 19) % 256);
        img.FlipVertical();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void FlipVertical_TwiceRestoresOriginalPixel()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 7) % 256);
        int original = img.GetPixel(3, 3);
        img.FlipVertical();
        img.FlipVertical();
        Assert.Equal(original, img.GetPixel(3, 3));
    }

    [Fact]
    public void FlipVertical_AllZeroImage_RemainsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        img.FlipVertical();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.Equal(0, img.GetPixel(x, y));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GradientImage_DimsPreserved()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, y * 32);
        img.FlipVertical();
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
        Assert.Equal(NetpbmFormat.PGM, img.Format);
    }

    [Fact]
    public void DogfoodPipeline_SingleRowImage_FlipOk()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM, 255);
        for (int x = 0; x < img.Width; x++)
            img.SetPixel(x, 0, x * 30);
        var ex = Record.Exception(() => img.FlipVertical());
        Assert.Null(ex);
        Assert.Equal(8, img.Width);
        Assert.Equal(1, img.Height);
    }
}
