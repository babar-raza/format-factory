// Tests for NetpbmImage.Threshold.
// Sprint: ff-sprint-s149-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R145

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R145: Tests for NetpbmImage.Threshold(int threshold).
/// Threshold converts a PGM or PPM image to a 1-bit PBM image.
/// PBM input throws InvalidOperationException. Threshold out of range throws ArgumentOutOfRangeException.
/// Output format is PBM_P1. Output MaxValue=1. Pixels >= threshold = 1, below = 0.
/// Covers: PBM_P1 input throws InvalidOperationException; PBM_P4 input throws;
/// negative threshold throws ArgumentOutOfRangeException; threshold > MaxValue throws;
/// output format is PBM_P1; output MaxValue is 1; output dimensions match input;
/// pixel above threshold = 1; pixel below threshold = 0; original unchanged;
/// dogfood Create->SetPixel->Threshold->GetPixel pipeline.
/// </summary>
public class NetpbmR145ThresholdTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PbmP1Input_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P1);
        Assert.Throws<InvalidOperationException>(() => img.Threshold(128));
    }

    [Fact]
    public void Threshold_PbmP4Input_ThrowsInvalidOperationException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PBM_P4);
        Assert.Throws<InvalidOperationException>(() => img.Threshold(128));
    }

    [Fact]
    public void Threshold_NegativeThreshold_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(-1));
    }

    [Fact]
    public void Threshold_ThresholdAboveMaxValue_ThrowsArgumentOutOfRangeException()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5); // MaxValue=255 by default
        Assert.Throws<ArgumentOutOfRangeException>(() => img.Threshold(256));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Threshold_PgmInput_OutputFormatIsPbmP1()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.Equal(NetpbmFormat.PBM_P1, result.Format);
    }

    [Fact]
    public void Threshold_Output_MaxValueIsOne()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = img.Threshold(128);
        Assert.Equal(1, result.MaxValue);
    }

    [Fact]
    public void Threshold_OutputDimensionsMatchInput()
    {
        var img = NetpbmImage.Create(4, 6, NetpbmFormat.PGM_P5);
        var result = img.Threshold(100);
        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
    }

    [Fact]
    public void Threshold_PixelAboveThreshold_IsOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);
        var result = img.Threshold(100);
        Assert.Equal(1, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_PixelBelowThreshold_IsZero()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        var result = img.Threshold(100);
        Assert.Equal(0, result.GetPixel(0, 0));
    }

    [Fact]
    public void Threshold_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 150);
        _ = img.Threshold(100);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format); // original format unchanged
        Assert.Equal(150, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Create_SetPixel_Threshold_GetPixel()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200); // above threshold
        img.SetPixel(1, 1, 50);  // below threshold
        img.SetPixel(2, 2, 128); // at threshold

        var result = img.Threshold(128);
        Assert.Equal(1, result.GetPixel(0, 0)); // 200 >= 128
        Assert.Equal(0, result.GetPixel(1, 1)); // 50 < 128
        Assert.Equal(1, result.GetPixel(2, 2)); // 128 >= 128
    }
}
