// Tests for NetpbmImage.Clone dedicated coverage.
// Sprint: ff-sprint-s257-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R264

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R264: Dedicated tests for NetpbmImage.Clone().
/// Clone returns a new independent image.
/// Width of clone equals original width.
/// Height of clone equals original height.
/// Format of clone equals original format.
/// MaxValue of clone equals original MaxValue.
/// Pixel values are copied to the clone.
/// Modifying clone does not affect original.
/// Modifying original does not affect clone.
/// Clone of a clone is valid.
/// Dogfood: set pixels, clone, verify pixels match.
/// Dogfood: mutate clone, original pixels unchanged.
/// </summary>
public class NetpbmR264CloneDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic behavioral tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.NotNull(clone);
    }

    [Fact]
    public void Clone_WidthMatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.Equal(img.Width, clone.Width);
    }

    [Fact]
    public void Clone_HeightMatchesOriginal()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        var clone = img.Clone();
        Assert.Equal(img.Height, clone.Height);
    }

    [Fact]
    public void Clone_FormatMatchesOriginal()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        var clone = img.Clone();
        Assert.Equal(img.Format, clone.Format);
    }

    [Fact]
    public void Clone_MaxValueMatchesOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 200);
        var clone = img.Clone();
        Assert.Equal(img.MaxValue, clone.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Independence tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_ModifyingCloneDoesNotAffectOriginal()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(1, 1, 100);
        var clone = img.Clone();
        clone.SetPixel(1, 1, 200);
        // Original pixel at (1,1) should still be 100
        Assert.Equal(100, img.GetPixel(1, 1));
    }

    [Fact]
    public void Clone_ModifyingOriginalDoesNotAffectClone()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 50);
        var clone = img.Clone();
        img.SetPixel(0, 0, 150);
        // Clone pixel at (0,0) should still be 50
        Assert.Equal(50, clone.GetPixel(0, 0));
    }

    [Fact]
    public void Clone_OfClone_IsValid()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 77);
        var clone1 = img.Clone();
        var clone2 = clone1.Clone();
        Assert.Equal(77, clone2.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetPixelsThenClone_PixelsMatch()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 10);
        img.SetPixel(1, 1, 128);
        img.SetPixel(2, 2, 245);
        var clone = img.Clone();
        Assert.Equal(10, clone.GetPixel(0, 0));
        Assert.Equal(128, clone.GetPixel(1, 1));
        Assert.Equal(245, clone.GetPixel(2, 2));
    }

    [Fact]
    public void DogfoodPipeline_MutateClone_OriginalUnchanged()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 99);
        var clone = img.Clone();
        clone.InvertColors();
        // Original should not be inverted
        Assert.Equal(99, img.GetPixel(2, 2));
    }
}
