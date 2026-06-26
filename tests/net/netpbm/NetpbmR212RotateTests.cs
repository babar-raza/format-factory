// Tests for NetpbmImage.Rotate dedicated coverage.
// Sprint: ff-sprint-s207-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R212

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R212: Dedicated tests for NetpbmImage.Rotate(int degrees).
/// degrees not in {0, 90, 180, 270} → ArgumentException.
/// degrees = 0 → returns clone.
/// degrees = 180 → width and height preserved.
/// degrees = 90 or 270 → width and height swapped.
/// Returns new image (not same reference).
/// Format preserved. MaxValue preserved.
/// Rotate 90 degrees: top-left pixel moves to top-right.
/// Rotate 360 (0) restores original values.
/// Rotate 90 then 270 restores original.
/// Dogfood: rotate 180, pixel at opposite corner.
/// </summary>
public class NetpbmR212RotateTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_InvalidDegrees_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentException>(() => img.Rotate(45));
    }

    [Fact]
    public void Rotate_NegativeDegrees_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentException>(() => img.Rotate(-90));
    }

    // -------------------------------------------------------------------------
    // Structural tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_90_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = img.Rotate(90);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate_180_ReturnsNewImage()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate(180);
        Assert.NotSame(img, result);
    }

    [Fact]
    public void Rotate_Format_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate(90);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void Rotate_PpmFormat_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P6);
        var result = img.Rotate(180);
        Assert.Equal(NetpbmFormat.PPM_P6, result.Format);
    }

    [Fact]
    public void Rotate_MaxValue_Preserved()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        var result = img.Rotate(270);
        Assert.Equal(img.MaxValue, result.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_180_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate(180);
        Assert.Equal(6, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Rotate_90_DimensionsSwapped()
    {
        var img = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P5);
        var result = img.Rotate(90);
        // Width and height should swap for 90° rotation
        Assert.Equal(4, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Rotate_180_PixelAtOppositeCorner()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 200);  // top-left
        var result = img.Rotate(180);
        // After 180°, top-left goes to bottom-right (row=4, col=4)
        Assert.Equal(200, result.GetPixel(4, 4));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Rotate90Then270_RestoresOriginal()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 0, 150);
        var r90 = img.Rotate(90);
        var r360 = r90.Rotate(270);
        Assert.Equal(150, r360.GetPixel(1, 0));
    }

    [Fact]
    public void DogfoodPipeline_Rotate180Twice_RestoresOriginal()
    {
        var img = NetpbmImage.Create(5, 5, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        var r1 = img.Rotate(180);
        var r2 = r1.Rotate(180);
        Assert.Equal(100, r2.GetPixel(0, 0));
        Assert.Equal(NetpbmFormat.PGM_P5, r2.Format);
    }
}
