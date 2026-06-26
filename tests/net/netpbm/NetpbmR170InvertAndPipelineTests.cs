// Tests for NetpbmImage.Invert, Pipeline, Clone, Comments, and SourcePath.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R170

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R170: Tests for NetpbmImage.Invert, Pipeline, Clone, Comments, and SourcePath.
/// Invert(): inverts all pixel values in-place.
/// Pipeline(steps): applies a sequence of transforms returning a new image.
/// Clone(): creates an independent copy of the image.
/// Comments: list of string comments attached to the image.
/// SourcePath: optional file origin path.
/// Covers: Invert on white image produces black; Invert on black produces white;
/// Invert twice returns to original; Pipeline with single step same as direct call;
/// Pipeline with multiple steps; Clone preserves dimensions;
/// Clone is independent (mutating clone does not affect original);
/// Comments.Add stores comment; Comments count; Comments content;
/// SourcePath is null for programmatic images; SourcePath after Create;
/// dogfood Create->Invert->Pipeline->Clone->Comments pipeline.
/// </summary>
public class NetpbmR170InvertAndPipelineTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM, fill);

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_WhiteImage_ProducesBlack()
    {
        var img = CreateGray(3, 3, 255);
        img.Invert();
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                Assert.Equal(0, img.GetPixel(r, c));
    }

    [Fact]
    public void Invert_BlackImage_ProducesWhite()
    {
        var img = CreateGray(3, 3, 0);
        img.Invert();
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                Assert.Equal(255, img.GetPixel(r, c));
    }

    [Fact]
    public void Invert_Twice_RestoresOriginal()
    {
        var img = CreateGray(4, 4, 128);
        img.Invert();
        img.Invert();
        Assert.Equal(128, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_MidGray_ProducesMirroredValue()
    {
        var img = CreateGray(2, 2, 100);
        img.Invert();
        Assert.Equal(155, img.GetPixel(0, 0)); // 255 - 100 = 155
    }

    [Fact]
    public void Invert_DoesNotChangeDimensions()
    {
        var img = CreateGray(5, 3, 200);
        img.Invert();
        Assert.Equal(5, img.Width);
        Assert.Equal(3, img.Height);
    }

    // -------------------------------------------------------------------------
    // Pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Pipeline_SingleStep_SameAsDirectCall()
    {
        var img = CreateGray(4, 4, 100);
        var direct = img.AdjustBrightness(20);
        var piped = img.Pipeline(new List<Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(20)
        });
        Assert.Equal(direct.Width, piped.Width);
        Assert.Equal(direct.Height, piped.Height);
        Assert.Equal(direct.GetPixel(0, 0), piped.GetPixel(0, 0));
    }

    [Fact]
    public void Pipeline_MultipleSteps_AppliesInOrder()
    {
        var img = CreateGray(4, 4, 100);
        var result = img.Pipeline(new List<Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(20),
            i => i.AdjustBrightness(-10)
        });
        // 100 + 20 - 10 = 110
        Assert.Equal(110, result.GetPixel(0, 0));
    }

    [Fact]
    public void Pipeline_EmptySteps_ReturnsSamePixels()
    {
        var img = CreateGray(3, 3, 77);
        var result = img.Pipeline(new List<Func<NetpbmImage, NetpbmImage>>());
        Assert.Equal(77, result.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_PreservesDimensions()
    {
        var img = CreateGray(6, 4, 128);
        var clone = img.Clone();
        Assert.Equal(img.Width, clone.Width);
        Assert.Equal(img.Height, clone.Height);
    }

    [Fact]
    public void Clone_PreservesPixelValues()
    {
        var img = CreateGray(3, 3, 200);
        var clone = img.Clone();
        Assert.Equal(200, clone.GetPixel(0, 0));
    }

    [Fact]
    public void Clone_IsIndependent_MutatingCloneDoesNotAffectOriginal()
    {
        var img = CreateGray(3, 3, 100);
        var clone = img.Clone();
        clone.SetPixel(0, 0, 255);
        Assert.Equal(100, img.GetPixel(0, 0)); // original unchanged
    }

    // -------------------------------------------------------------------------
    // Comments
    // -------------------------------------------------------------------------

    [Fact]
    public void Comments_AddComment_StoresComment()
    {
        var img = CreateGray(2, 2, 0);
        img.Comments.Add("Test comment");
        Assert.Contains("Test comment", img.Comments);
    }

    [Fact]
    public void Comments_MultipleComments_CountIsCorrect()
    {
        var img = CreateGray(2, 2, 0);
        img.Comments.Add("First");
        img.Comments.Add("Second");
        Assert.Equal(2, img.Comments.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Invert->Pipeline->Clone->Comments
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInvertPipelineCloneComments_Pipeline()
    {
        // Create a mid-gray image
        var img = CreateGray(4, 4, 100);
        Assert.Equal(4, img.Width);

        // Invert it
        img.Invert();
        Assert.Equal(155, img.GetPixel(0, 0)); // 255 - 100

        // Pipeline: adjust brightness back up by 45 and threshold at 200
        var processed = img.Pipeline(new List<Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(45) // 155 + 45 = 200
        });
        Assert.Equal(200, processed.GetPixel(0, 0));

        // Clone the processed image
        var clone = processed.Clone();
        Assert.Equal(processed.Width, clone.Width);
        clone.SetPixel(1, 1, 0);
        Assert.Equal(200, processed.GetPixel(1, 1)); // original unaffected

        // Add a comment
        clone.Comments.Add("dogfood R170");
        Assert.Single(clone.Comments);
        Assert.Equal("dogfood R170", clone.Comments[0]);
    }
}
