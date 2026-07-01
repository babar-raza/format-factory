// Tests for NetpbmImage.GetStructuralSimilarityIndex dedicated coverage.
// Sprint: ff-sprint-s443-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R461

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R461: Dedicated tests for NetpbmImage.GetStructuralSimilarityIndex().
/// Returns value in range [0, 1] for PBM/PGM/PPM.
/// Width/Height/Format/MaxValue unchanged after call.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM and PPM SSIM in [0, 1].
/// </summary>
public class NetpbmR461GetStructuralSimilarityIndexDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStructuralSimilarityIndex_InRange()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetStructuralSimilarityIndex();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetStructuralSimilarityIndex();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetStructuralSimilarityIndex();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetStructuralSimilarityIndex();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double first = img.GetStructuralSimilarityIndex();
        double second = img.GetStructuralSimilarityIndex();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_PBM_InRange()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_PGM_InRange()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }

    [Fact]
    public void GetStructuralSimilarityIndex_PPM_InRange()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_SSIMInRange()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_SSIMInRange()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        double val = img.GetStructuralSimilarityIndex();
        Assert.True(val >= 0.0 && val <= 1.0);
    }
}
