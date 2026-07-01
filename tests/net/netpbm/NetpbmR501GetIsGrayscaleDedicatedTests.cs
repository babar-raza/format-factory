// Tests for NetpbmImage.GetIsGrayscale dedicated coverage.
// Sprint: ff-sprint-s483-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R501

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R501: Dedicated tests for NetpbmImage.GetIsGrayscale().
/// PBM image returns false (bitmap, not grayscale).
/// PGM image returns true (grayscale format).
/// PPM image returns false (color, not grayscale).
/// Width unchanged after GetIsGrayscale.
/// Height unchanged after GetIsGrayscale.
/// Format unchanged after GetIsGrayscale.
/// MaxValue unchanged after GetIsGrayscale.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline returns false.
/// Dogfood: PGM pipeline returns true.
/// Dogfood: PPM pipeline returns false.
/// </summary>
public class NetpbmR501GetIsGrayscaleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsGrayscale_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetIsGrayscale());
    }

    [Fact]
    public void GetIsGrayscale_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePgm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsGrayscale_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePgm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsGrayscale_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsGrayscale_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsGrayscale();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsGrayscale_Idempotent()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        bool first = img.GetIsGrayscale();
        bool second = img.GetIsGrayscale();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsGrayscale();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsGrayscale();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsGrayscale();
        Assert.False(result);
    }
}
