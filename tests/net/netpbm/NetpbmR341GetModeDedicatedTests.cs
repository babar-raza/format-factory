// Tests for NetpbmImage.GetMode dedicated coverage.
// Sprint: ff-sprint-s329-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R341

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R341: Dedicated tests for NetpbmImage.GetMode().
/// Valid call no exception.
/// Width unchanged after GetMode.
/// Height unchanged after GetMode.
/// Format unchanged after GetMode.
/// MaxValue unchanged after GetMode.
/// Returns value in [0, MaxValue].
/// All-zero image mode is zero.
/// Idempotent (called twice same result).
/// Uniform image mode equals pixel value.
/// Dogfood: bimodal image mode is non-negative.
/// </summary>
public class NetpbmR341GetModeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMode_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 7 + y * 11) % 256);
        var ex = Record.Exception(() => img.GetMode());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMode_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        _ = img.GetMode();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMode_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        _ = img.GetMode();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMode_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        _ = img.GetMode();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMode_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        _ = img.GetMode();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMode_ReturnsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 3 + y * 9) % 256);
        int mode = img.GetMode();
        Assert.InRange(mode, 0, img.MaxValue);
    }

    [Fact]
    public void GetMode_AllZeroImage_ModeIsZero()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int mode = img.GetMode();
        Assert.Equal(0, mode);
    }

    [Fact]
    public void GetMode_CalledTwice_SameResult()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 5 + y * 7) % 256);
        int first = img.GetMode();
        int second = img.GetMode();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetMode_UniformImage_ModeEqualsPixelValue()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 90);
        int mode = img.GetMode();
        Assert.Equal(90, mode);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_BimodalImage_ModeNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) % 2 == 0 ? 80 : 180);
        int mode = img.GetMode();
        Assert.True(mode >= 0);
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
    }
}
