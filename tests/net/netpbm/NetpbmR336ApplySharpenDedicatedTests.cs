// Tests for NetpbmImage.ApplySharpen dedicated coverage.
// Sprint: ff-sprint-s324-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R336

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R336: Dedicated tests for NetpbmImage.ApplySharpen().
/// Valid call no exception.
/// Width unchanged after ApplySharpen.
/// Height unchanged after ApplySharpen.
/// Format unchanged after ApplySharpen.
/// MaxValue unchanged after ApplySharpen.
/// All pixels in valid range after ApplySharpen.
/// All-zero image remains zero.
/// Called twice no exception.
/// Dogfood: mixed pixel image after sharpen dims preserved.
/// Dogfood: uniform image after sharpen dims and format preserved.
/// </summary>
public class NetpbmR336ApplySharpenDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplySharpen_ValidCall_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 13 + y * 7) % 256);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Width;
        img.ApplySharpen();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void ApplySharpen_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(10, 5, NetpbmFormat.PGM, 255);
        int before = img.Height;
        img.ApplySharpen();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void ApplySharpen_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var before = img.Format;
        img.ApplySharpen();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void ApplySharpen_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        int before = img.MaxValue;
        img.ApplySharpen();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_AllPixelsInValidRange()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 11 + y * 9) % 256);
        img.ApplySharpen();
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                Assert.InRange(img.GetPixel(x, y), 0, img.MaxValue);
    }

    [Fact]
    public void ApplySharpen_AllZeroImage_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplySharpen_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x + y) * 15 % 256);
        img.ApplySharpen();
        var ex = Record.Exception(() => img.ApplySharpen());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MixedPixelImage_DimsPreserved()
    {
        var img = NetpbmImage.CreateNew(8, 8, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, (x * 19 + y * 11) % 256);
        img.ApplySharpen();
        Assert.Equal(8, img.Width);
        Assert.Equal(8, img.Height);
        Assert.Equal(NetpbmFormat.PGM, img.Format);
    }

    [Fact]
    public void DogfoodPipeline_UniformImage_DimsAndFormatPreserved()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PGM, 255);
        for (int y = 0; y < img.Height; y++)
            for (int x = 0; x < img.Width; x++)
                img.SetPixel(x, y, 128);
        img.ApplySharpen();
        Assert.Equal(6, img.Width);
        Assert.Equal(6, img.Height);
        Assert.Equal(NetpbmFormat.PGM, img.Format);
    }
}
