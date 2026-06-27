// Tests for NetpbmImage.GetHistogram dedicated coverage.
// Sprint: ff-sprint-s390-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R403

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R403: Dedicated tests for NetpbmImage.GetHistogram().
/// Returns non-null result.
/// Width unchanged after GetHistogram.
/// Height unchanged after GetHistogram.
/// Format unchanged after GetHistogram.
/// MaxValue unchanged after GetHistogram.
/// Idempotent (called twice same result length).
/// PBM histogram non-null.
/// PGM histogram non-null.
/// PPM histogram non-null.
/// Dogfood: 4x4 PGM histogram non-null.
/// Dogfood: 4x4 PPM histogram non-null.
/// </summary>
public class NetpbmR403GetHistogramDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_ReturnsNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }

    [Fact]
    public void GetHistogram_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetHistogram();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetHistogram_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetHistogram();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetHistogram_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetHistogram();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetHistogram_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetHistogram();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetHistogram_Idempotent_SameCount()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        var first = img.GetHistogram();
        var second = img.GetHistogram();
        Assert.Equal(first.Count, second.Count);
    }

    [Fact]
    public void GetHistogram_PBM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }

    [Fact]
    public void GetHistogram_PGM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }

    [Fact]
    public void GetHistogram_PPM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_HistogramNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_HistogramNonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        var histogram = img.GetHistogram();
        Assert.NotNull(histogram);
    }
}
