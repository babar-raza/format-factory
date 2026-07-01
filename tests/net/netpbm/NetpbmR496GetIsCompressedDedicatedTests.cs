// Tests for NetpbmImage.GetIsCompressed dedicated coverage.
// Sprint: ff-sprint-s478-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R496

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R496: Dedicated tests for NetpbmImage.GetIsCompressed().
/// PBM returns false (Netpbm raw format is uncompressed).
/// PGM returns false (Netpbm raw format is uncompressed).
/// PPM returns false (Netpbm raw format is uncompressed).
/// Width unchanged after GetIsCompressed.
/// Height unchanged after GetIsCompressed.
/// Format unchanged after GetIsCompressed.
/// MaxValue unchanged after GetIsCompressed.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not compressed.
/// Dogfood: 4x4 PGM not compressed.
/// Dogfood: 4x4 PPM not compressed.
/// </summary>
public class NetpbmR496GetIsCompressedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsCompressed_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsCompressed());
    }

    [Fact]
    public void GetIsCompressed_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsCompressed());
    }

    [Fact]
    public void GetIsCompressed_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsCompressed());
    }

    [Fact]
    public void GetIsCompressed_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsCompressed();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsCompressed_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsCompressed();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsCompressed_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsCompressed();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsCompressed_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsCompressed();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsCompressed_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsCompressed();
        bool second = img.GetIsCompressed();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotCompressed()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsCompressed());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotCompressed()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsCompressed());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotCompressed()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsCompressed());
    }
}
