// Tests for NetpbmImage.GetThumbnailSize dedicated coverage.
// Sprint: ff-sprint-s448-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R466

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R466: Dedicated tests for NetpbmImage.GetThumbnailSize().
/// Returns positive int for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM thumbnail size positive.
/// </summary>
public class NetpbmR466GetThumbnailSizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetThumbnailSize_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetThumbnailSize_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetThumbnailSize();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetThumbnailSize_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetThumbnailSize();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetThumbnailSize_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetThumbnailSize();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetThumbnailSize_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetThumbnailSize();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetThumbnailSize_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int first = img.GetThumbnailSize();
        int second = img.GetThumbnailSize();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetThumbnailSize_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetThumbnailSize_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }

    [Fact]
    public void GetThumbnailSize_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ThumbnailSizePositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ThumbnailSizePositive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        int val = img.GetThumbnailSize();
        Assert.True(val > 0);
    }
}
