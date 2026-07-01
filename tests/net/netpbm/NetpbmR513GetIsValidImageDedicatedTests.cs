// Tests for NetpbmImage.GetIsValidImage dedicated coverage.
// Sprint: ff-sprint-s495-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R513

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R513: Dedicated tests for NetpbmImage.GetIsValidImage().
/// PBM image returns true (valid image).
/// PGM image returns true (valid image).
/// PPM image returns true (valid image).
/// Width unchanged after GetIsValidImage.
/// Height unchanged after GetIsValidImage.
/// Format unchanged after GetIsValidImage.
/// MaxValue unchanged after GetIsValidImage.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline is valid image.
/// Dogfood: PGM pipeline is valid image.
/// Dogfood: PPM pipeline is valid image.
/// </summary>
public class NetpbmR513GetIsValidImageDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsValidImage_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsValidImage());
    }

    [Fact]
    public void GetIsValidImage_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsValidImage());
    }

    [Fact]
    public void GetIsValidImage_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsValidImage());
    }

    [Fact]
    public void GetIsValidImage_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsValidImage();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsValidImage_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsValidImage();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsValidImage_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsValidImage();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsValidImage_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsValidImage();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsValidImage_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsValidImage();
        bool second = img.GetIsValidImage();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_IsValidImage()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsValidImage();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_IsValidImage()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsValidImage();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_IsValidImage()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsValidImage();
        Assert.True(result);
    }
}
