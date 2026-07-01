// Tests for NetpbmImage.GetPerceptualHash dedicated coverage.
// Sprint: ff-sprint-s447-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R465

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R465: Dedicated tests for NetpbmImage.GetPerceptualHash().
/// Returns non-null string for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Same image returns same hash.
/// Dogfood: 4x4 PGM and PPM hash not null.
/// </summary>
public class NetpbmR465GetPerceptualHashDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPerceptualHash_ReturnsNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetPerceptualHash_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetPerceptualHash();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetPerceptualHash_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetPerceptualHash();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetPerceptualHash_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetPerceptualHash();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetPerceptualHash_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetPerceptualHash();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetPerceptualHash_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetPerceptualHash();
        string second = img.GetPerceptualHash();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetPerceptualHash_PBM_NotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetPerceptualHash_PGM_NotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }

    [Fact]
    public void GetPerceptualHash_PPM_NotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_HashNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_HashNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string val = img.GetPerceptualHash();
        Assert.NotNull(val);
    }
}
