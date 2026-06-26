// Tests for NetpbmImage.Crop, MergeVertical, MergeHorizontal deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R204

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R204: Tests for NetpbmImage.Crop, MergeVertical, MergeHorizontal deeper coverage.
/// Crop(x, y, width, height): returns a cropped sub-image of the given dimensions.
/// MergeVertical(other): stacks another image below this one.
/// MergeHorizontal(other): places another image to the right of this one.
/// Covers: Crop non-null; Crop correct dimensions; Crop top-left corner; Crop bottom-right region;
/// Crop full image preserves dimensions; MergeVertical non-null; MergeVertical doubles height;
/// MergeVertical preserves width; MergeVertical different heights sums;
/// MergeHorizontal non-null; MergeHorizontal doubles width; MergeHorizontal preserves height;
/// MergeVertical then MergeHorizontal dimensions correct;
/// dogfood CreateCanvas->Crop->MergeVertical->MergeHorizontal->Verify pipeline.
/// </summary>
public class NetpbmR204CropAndMergeVerticalDeepTests
{
    // -------------------------------------------------------------------------
    // Crop
    // -------------------------------------------------------------------------

    [Fact]
    public void Crop_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        Assert.NotNull(img.Crop(0, 0, 4, 3));
    }

    [Fact]
    public void Crop_CorrectWidth()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        var cropped = img.Crop(0, 0, 4, 3);
        Assert.Equal(4, cropped.Width);
    }

    [Fact]
    public void Crop_CorrectHeight()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 200);
        var cropped = img.Crop(0, 0, 4, 3);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_TopLeftCorner_CorrectDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 8, NetpbmFormat.Pgm, 128);
        var cropped = img.Crop(0, 0, 3, 3);
        Assert.Equal(3, cropped.Width);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Crop_BottomRightRegion_CorrectDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 8, NetpbmFormat.Pgm, 128);
        var cropped = img.Crop(5, 4, 5, 4);
        Assert.Equal(5, cropped.Width);
        Assert.Equal(4, cropped.Height);
    }

    [Fact]
    public void Crop_FullImage_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var cropped = img.Crop(0, 0, img.Width, img.Height);
        Assert.Equal(img.Width, cropped.Width);
        Assert.Equal(img.Height, cropped.Height);
    }

    [Fact]
    public void Crop_Single_Pixel_OneByOne()
    {
        var img = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var cropped = img.Crop(2, 2, 1, 1);
        Assert.Equal(1, cropped.Width);
        Assert.Equal(1, cropped.Height);
    }

    // -------------------------------------------------------------------------
    // MergeVertical
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_NonNull()
    {
        var img1 = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 100);
        Assert.NotNull(img1.MergeVertical(img2));
    }

    [Fact]
    public void MergeVertical_SameSize_DoublesHeight()
    {
        var img1 = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeVertical(img2);
        Assert.Equal(8, merged.Height);
    }

    [Fact]
    public void MergeVertical_PreservesWidth()
    {
        var img1 = NetpbmImage.CreateCanvas(6, 4, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(6, 3, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeVertical(img2);
        Assert.Equal(6, merged.Width);
    }

    [Fact]
    public void MergeVertical_SumsHeights()
    {
        var img1 = NetpbmImage.CreateCanvas(5, 3, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(5, 5, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeVertical(img2);
        Assert.Equal(8, merged.Height);
    }

    // -------------------------------------------------------------------------
    // MergeHorizontal
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_NonNull()
    {
        var img1 = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 100);
        Assert.NotNull(img1.MergeHorizontal(img2));
    }

    [Fact]
    public void MergeHorizontal_SameSize_DoublesWidth()
    {
        var img1 = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeHorizontal(img2);
        Assert.Equal(8, merged.Width);
    }

    [Fact]
    public void MergeHorizontal_PreservesHeight()
    {
        var img1 = NetpbmImage.CreateCanvas(4, 6, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(3, 6, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeHorizontal(img2);
        Assert.Equal(6, merged.Height);
    }

    [Fact]
    public void MergeHorizontal_SumsWidths()
    {
        var img1 = NetpbmImage.CreateCanvas(3, 5, NetpbmFormat.Pgm, 200);
        var img2 = NetpbmImage.CreateCanvas(5, 5, NetpbmFormat.Pgm, 100);
        var merged = img1.MergeHorizontal(img2);
        Assert.Equal(8, merged.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_Crop_MergeVertical_MergeHorizontal_Verify_Pipeline()
    {
        // CreateCanvas 12x8
        var img = NetpbmImage.CreateCanvas(12, 8, NetpbmFormat.Pgm, 200);
        Assert.Equal(12, img.Width);
        Assert.Equal(8, img.Height);

        // Crop top-left 6x4
        var topLeft = img.Crop(0, 0, 6, 4);
        Assert.Equal(6, topLeft.Width);
        Assert.Equal(4, topLeft.Height);

        // Crop bottom-right 6x4
        var bottomRight = img.Crop(6, 4, 6, 4);
        Assert.Equal(6, bottomRight.Width);
        Assert.Equal(4, bottomRight.Height);

        // MergeVertical top-left and bottom-right → 6x8
        var vertical = topLeft.MergeVertical(bottomRight);
        Assert.Equal(6, vertical.Width);
        Assert.Equal(8, vertical.Height);

        // Crop two halves from original for horizontal merge
        var leftHalf = img.Crop(0, 0, 6, 8);
        var rightHalf = img.Crop(6, 0, 6, 8);

        // MergeHorizontal → 12x8
        var horizontal = leftHalf.MergeHorizontal(rightHalf);
        Assert.Equal(12, horizontal.Width);
        Assert.Equal(8, horizontal.Height);

        // Chain: crop small and then merge vertical twice
        var small = NetpbmImage.CreateCanvas(4, 3, NetpbmFormat.Pgm, 100);
        var triple = small.MergeVertical(small).MergeVertical(small);
        Assert.Equal(4, triple.Width);
        Assert.Equal(9, triple.Height);
    }
}
