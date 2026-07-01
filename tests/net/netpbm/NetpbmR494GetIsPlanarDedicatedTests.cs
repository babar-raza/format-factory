// Tests for NetpbmImage.GetIsPlanar dedicated coverage.
// Sprint: ff-sprint-s476-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R494

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R494: Dedicated tests for NetpbmImage.GetIsPlanar().
/// PBM returns false (not planar).
/// PGM returns false (not planar).
/// PPM returns false (not planar — interleaved RGB).
/// Width unchanged after GetIsPlanar.
/// Height unchanged after GetIsPlanar.
/// Format unchanged after GetIsPlanar.
/// MaxValue unchanged after GetIsPlanar.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not planar.
/// Dogfood: 4x4 PGM not planar.
/// Dogfood: 4x4 PPM not planar.
/// </summary>
public class NetpbmR494GetIsPlanarDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsPlanar_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsPlanar());
    }

    [Fact]
    public void GetIsPlanar_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsPlanar());
    }

    [Fact]
    public void GetIsPlanar_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsPlanar());
    }

    [Fact]
    public void GetIsPlanar_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsPlanar();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsPlanar_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsPlanar();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsPlanar_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsPlanar();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsPlanar_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsPlanar();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsPlanar_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsPlanar();
        bool second = img.GetIsPlanar();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotPlanar()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsPlanar());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotPlanar()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsPlanar());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotPlanar()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsPlanar());
    }
}
