// Tests for NetpbmImage.Threshold dedicated coverage.
// Sprint: ff-sprint-s175-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R171

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R171: Dedicated tests for NetpbmImage.Threshold(int threshold).
/// Converts a grayscale/color image to PBM by binarization.
/// PBM input throws InvalidOperationException (already binary).
/// threshold outside 0..MaxValue throws ArgumentOutOfRangeException.
/// Result format is always PBM_P1, MaxValue=1.
/// Pixel >= threshold → 1; pixel &lt; threshold → 0.
/// Covers: PBM throws; negative throws; over-max throws;
/// result format=PBM_P1; width/height unchanged; MaxValue=1;
/// pixel-at-threshold=1; pixel-below-threshold=0; all-black result; dogfood PGM pipeline.
/// </summary>
public class NetpbmR171ThresholdTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_OnPbmImage_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P1);
        Assert.Throws<InvalidOperationException>(() => img.Threshold(1));
    }

    [Fact]
    public void Threshold_NegativeThreshold_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(-1));
    }

    [Fact]
    public void Threshold_OverMaxValue_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(img.MaxValue + 1));
    }

    // -------------------------------------------------------------------------
    // Result structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_ResultFormat_IsPbmP1()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void Threshold_ResultMaxValue_IsOne()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.Equal(1, result.MaxValue);
    }

    [Fact]
    public void Threshold_ResultDimensions_MatchOriginal()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P2);
        var result = img.Threshold(100);
        Assert.Equal(4, result.Width);
        Assert.Equal(6, result.Height);
    }

    // -------------------------------------------------------------------------
    // Pixel semantics tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PixelAtThreshold_BecomesOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        var result = img.Threshold(128);
        Assert.Equal(1, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_PixelBelowThreshold_BecomesZero()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        var result = img.Threshold(128);
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_AllZeroImage_AllResultsAreZero()
    {
        // threshold=1 → all zeros below threshold → all 0
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        // all pixels default to 0
        var result = img.Threshold(1);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.Equal(0, result.GetPixel(r, c));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmSetPixelsThenThreshold_CorrectBinaryMap()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200); // above 128 → 1
        img.SetPixel(0, 1, 50);  // below 128 → 0
        img.SetPixel(1, 0, 128); // at 128 → 1
        img.SetPixel(1, 1, 127); // below 128 → 0
        var result = img.Threshold(128);
        Assert.Equal(1, result.GetPixel(0, 0));
        Assert.Equal(0, result.GetPixel(0, 1));
        Assert.Equal(1, result.GetPixel(1, 0));
        Assert.Equal(0, result.GetPixel(1, 1));
    }
}
