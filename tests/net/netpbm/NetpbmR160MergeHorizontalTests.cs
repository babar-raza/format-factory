// Tests for NetpbmImage.MergeHorizontal dedicated coverage.
// Sprint: ff-sprint-s164-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R160

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R160: Dedicated tests for NetpbmImage.MergeHorizontal(NetpbmImage other).
/// MergeHorizontal places 'other' to the right of this image. Returns a NEW image.
/// Both images must have the same Height and Format.
/// Throws ArgumentNullException if other is null.
/// Throws ArgumentException if heights differ or formats differ.
/// Covers: null other throws ArgumentNullException; height mismatch throws ArgumentException;
/// format mismatch throws ArgumentException; output Width = Width+other.Width;
/// output Height equals source Height; format preserved; originals unchanged;
/// left-side pixels preserved at their positions; dogfood Create->SetPixel->MergeHorizontal->GetPixel;
/// dogfood right-side pixels accessible at Width offset.
/// </summary>
public class NetpbmR160MergeHorizontalTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_NullOther_ThrowsArgumentNullException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentNullException>(() => img.MergeHorizontal(null!));
    }

    [Fact]
    public void MergeHorizontal_HeightMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(2, 3, NetpbmFormat.PGM_P5); // 2w 3h
        var other = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5); // 2w 4h — different height
        Assert.Throws<ArgumentException>(() => img.MergeHorizontal(other));
    }

    [Fact]
    public void MergeHorizontal_FormatMismatch_ThrowsArgumentException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var other = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P4);
        Assert.Throws<ArgumentException>(() => img.MergeHorizontal(other));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeHorizontal_OutputWidth_IsSumOfWidths()
    {
        var left = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(5, 2, NetpbmFormat.PGM_P5);
        var result = left.MergeHorizontal(right);
        Assert.Equal(8, result.Width); // 3 + 5
    }

    [Fact]
    public void MergeHorizontal_OutputHeight_EqualsSourceHeight()
    {
        var left = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(2, 4, NetpbmFormat.PGM_P5);
        var result = left.MergeHorizontal(right);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void MergeHorizontal_FormatPreserved()
    {
        var left = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = left.MergeHorizontal(right);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeHorizontal_OriginalDimsUnchanged()
    {
        var left = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        _ = left.MergeHorizontal(right);
        Assert.Equal(3, left.Width);
        Assert.Equal(4, right.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LeftPixelPreserved()
    {
        var left = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        left.SetPixel(1, 2, 77); // row=1, col=2 in left
        var right = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = left.MergeHorizontal(right);
        Assert.Equal(77, result.GetPixel(1, 2)); // same position in merged
    }

    [Fact]
    public void DogfoodPipeline_RightPixelAtWidthOffset()
    {
        var left = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        right.SetPixel(0, 1, 99); // row=0, col=1 in right
        var result = left.MergeHorizontal(right);
        // In merged: row=0, col=left.Width+1=3+1=4
        Assert.Equal(99, result.GetPixel(0, 4));
    }

    [Fact]
    public void DogfoodPipeline_BothSidesPixelCheck()
    {
        var left = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var right = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        left.SetPixel(0, 0, 11);
        right.SetPixel(0, 0, 22);
        var result = left.MergeHorizontal(right);
        Assert.Equal(11, result.GetPixel(0, 0));
        Assert.Equal(22, result.GetPixel(0, 2)); // right starts at col=left.Width=2
    }
}
