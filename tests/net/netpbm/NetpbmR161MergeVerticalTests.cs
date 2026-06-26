// Tests for NetpbmImage.MergeVertical dedicated coverage.
// Sprint: ff-sprint-s165-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R161

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R161: Dedicated tests for NetpbmImage.MergeVertical(NetpbmImage other).
/// MergeVertical places 'other' below this image. Returns a NEW image.
/// Both images must have the same Width and Format.
/// Throws ArgumentNullException if other is null.
/// Throws ArgumentException if widths differ or formats differ.
/// Covers: null other throws ArgumentNullException; width mismatch throws ArgumentException;
/// format mismatch throws ArgumentException; output Height = Height+other.Height;
/// output Width equals source Width; format preserved; originals unchanged;
/// top-half pixels preserved at their positions; bottom-half pixels at Height offset;
/// dogfood Create->SetPixel->MergeVertical->GetPixel; dogfood both halves pixel check.
/// </summary>
public class NetpbmR161MergeVerticalTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_NullOther_ThrowsArgumentNullException()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        Assert.Throws<ArgumentNullException>(() => img.MergeVertical(null!));
    }

    [Fact]
    public void MergeVertical_WidthMismatch_ThrowsArgumentException()
    {
        var top = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 3w 2h
        var bottom = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5); // 4w 2h — different width
        Assert.Throws<ArgumentException>(() => top.MergeVertical(bottom));
    }

    [Fact]
    public void MergeVertical_FormatMismatch_ThrowsArgumentException()
    {
        var top = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(2, 2, NetpbmFormat.PBM_P4);
        Assert.Throws<ArgumentException>(() => top.MergeVertical(bottom));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeVertical_OutputHeight_IsSumOfHeights()
    {
        var top = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        var result = top.MergeVertical(bottom);
        Assert.Equal(6, result.Height); // 2 + 4
    }

    [Fact]
    public void MergeVertical_OutputWidth_EqualsSourceWidth()
    {
        var top = NetpbmImage.Create(5, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(5, 3, NetpbmFormat.PGM_P5);
        var result = top.MergeVertical(bottom);
        Assert.Equal(5, result.Width);
    }

    [Fact]
    public void MergeVertical_FormatPreserved()
    {
        var top = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var result = top.MergeVertical(bottom);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeVertical_OriginalDimsUnchanged()
    {
        var top = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(3, 4, NetpbmFormat.PGM_P5);
        _ = top.MergeVertical(bottom);
        Assert.Equal(2, top.Height);
        Assert.Equal(4, bottom.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TopPixelPreserved()
    {
        var top = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        top.SetPixel(1, 2, 55); // row=1, col=2 in top image
        var bottom = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5);
        var result = top.MergeVertical(bottom);
        Assert.Equal(55, result.GetPixel(1, 2)); // same row/col in merged
    }

    [Fact]
    public void DogfoodPipeline_BottomPixelAtHeightOffset()
    {
        var top = NetpbmImage.Create(3, 2, NetpbmFormat.PGM_P5); // 2h
        var bottom = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        bottom.SetPixel(1, 0, 88); // row=1, col=0 in bottom
        var result = top.MergeVertical(bottom);
        // In merged: row=top.Height+1=3, col=0
        Assert.Equal(88, result.GetPixel(3, 0));
    }

    [Fact]
    public void DogfoodPipeline_BothHalvesPixelCheck()
    {
        var top = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        var bottom = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        top.SetPixel(0, 0, 11);
        bottom.SetPixel(0, 0, 22);
        var result = top.MergeVertical(bottom);
        Assert.Equal(11, result.GetPixel(0, 0));
        Assert.Equal(22, result.GetPixel(2, 0)); // bottom starts at row=top.Height=2
    }
}
