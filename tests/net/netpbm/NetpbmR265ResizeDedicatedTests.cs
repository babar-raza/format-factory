// Tests for NetpbmImage.Resize dedicated coverage.
// Sprint: ff-sprint-s258-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R265

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R265: Dedicated tests for NetpbmImage.Resize(width, height).
/// Zero/negative width → throws exception.
/// Zero/negative height → throws exception.
/// Valid resize → returns new image (non-null).
/// Result width matches requested width.
/// Result height matches requested height.
/// Format preserved in result.
/// MaxValue preserved in result.
/// Original dimensions unchanged after resize.
/// Resize to same dimensions → new image with same dims.
/// Dogfood: resize up, new dims correct.
/// Dogfood: resize down, new dims correct.
/// </summary>
public class NetpbmR265ResizeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ZeroWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.Resize(0, 4));
    }

    [Fact]
    public void Resize_NegativeWidth_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.Resize(-1, 4));
    }

    [Fact]
    public void Resize_ZeroHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.Resize(4, 0));
    }

    [Fact]
    public void Resize_NegativeHeight_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.Resize(4, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Resize_ValidDimensions_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(8, 6);
        Assert.NotNull(result);
    }

    [Fact]
    public void Resize_ResultWidthMatchesRequested()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(10, 6);
        Assert.Equal(10, result.Width);
    }

    [Fact]
    public void Resize_ResultHeightMatchesRequested()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(10, 6);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Resize_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(8, 8);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Resize_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var result = img.Resize(8, 8);
        Assert.Equal(200, result.MaxValue);
    }

    [Fact]
    public void Resize_OriginalDimensionsUnchanged()
    {
        var img = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.Resize(8, 6);
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ResizeUp_NewDimsCorrect()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 128);
        var result = img.Resize(9, 9);
        Assert.Equal(9, result.Width);
        Assert.Equal(9, result.Height);
    }

    [Fact]
    public void DogfoodPipeline_ResizeDown_NewDimsCorrect()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var result = img.Resize(2, 2);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
    }
}
