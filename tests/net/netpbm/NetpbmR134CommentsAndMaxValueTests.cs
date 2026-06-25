// Tests for NetpbmImage.Comments (parsed comment lines) and MaxValue with non-255 maxval.
// Sprint: FORMAT-FACTORY-NETPBM-COMMENTS-MAXVALUE-20260626
// Ledger: R134-GOVERNED-DOTNET-NETPBM-COMMENTS-MAXVALUE-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R134: NetpbmImage.Comments (List{string}) captures PGM/PPM comment lines (lines
/// starting with '#'). NetpbmDocument.MaxValue reflects the actual PNM maxval header
/// value — 100 for "P2 1 1 100", 255 for standard images. Pixel access respects MaxValue.
/// </summary>
public class NetpbmR134CommentsAndMaxValueTests
{
    private static NetpbmDocument LoadAscii(string pnmText)
    {
        var bytes = Encoding.ASCII.GetBytes(pnmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- Comments: no comments ----

    [Fact]
    public void Comments_NoCommentLines_IsEmptyList()
    {
        var doc = LoadAscii("P2\n2 2\n255\n10 20\n30 40\n");
        Assert.Empty(doc.Image.Comments);
    }

    // ---- Comments: single comment ----

    [Fact]
    public void Comments_SingleCommentLine_CountIsOne()
    {
        var doc = LoadAscii("P2\n# This is a comment\n2 1\n255\n128 200\n");
        Assert.Single(doc.Image.Comments);
    }

    [Fact]
    public void Comments_SingleCommentLine_ContentPreserved()
    {
        var doc = LoadAscii("P2\n# Test comment\n1 1\n255\n128\n");
        Assert.Contains(doc.Image.Comments, c => c.Contains("Test comment"));
    }

    // ---- Comments: multiple comments ----

    [Fact]
    public void Comments_MultipleCommentLines_CountMatches()
    {
        var doc = LoadAscii("P2\n# First comment\n# Second comment\n1 1\n255\n64\n");
        Assert.Equal(2, doc.Image.Comments.Count);
    }

    // ---- MaxValue: standard 255 ----

    [Fact]
    public void MaxValue_Standard255_Is255()
    {
        var doc = LoadAscii("P2\n1 1\n255\n128\n");
        Assert.Equal(255, doc.MaxValue);
    }

    // ---- MaxValue: non-standard values ----

    [Fact]
    public void MaxValue_Maxval100_Is100()
    {
        var doc = LoadAscii("P2\n1 1\n100\n50\n");
        Assert.Equal(100, doc.MaxValue);
    }

    [Fact]
    public void MaxValue_Maxval15_Is15()
    {
        // Small depth PGM, common for 4-bit images
        var doc = LoadAscii("P2\n1 1\n15\n7\n");
        Assert.Equal(15, doc.MaxValue);
    }

    // ---- MaxValue: pixel value bounded by MaxValue ----

    [Fact]
    public void MaxValue_PixelValueAtMax_IsMaxValue()
    {
        var doc = LoadAscii("P2\n1 1\n100\n100\n");
        Assert.Equal(100, (int)doc.GetPixel(0, 0));
    }

    [Fact]
    public void MaxValue_PixelValueMidRange_CorrectValue()
    {
        // maxval=100, pixel=50 → pixel is 50 (not 255/2)
        var doc = LoadAscii("P2\n1 1\n100\n50\n");
        Assert.Equal(50, (int)doc.GetPixel(0, 0));
    }

    // ---- Consistency: MaxValue doesn't affect image dimensions ----

    [Fact]
    public void MaxValue_DifferentFromDefault_DimensionsCorrect()
    {
        var doc = LoadAscii("P2\n3 2\n100\n10 20 30\n40 50 60\n");
        Assert.Equal(3, doc.Width);
        Assert.Equal(2, doc.Height);
        Assert.Equal(100, doc.MaxValue);
    }

    // ---- Dogfood: comment + maxval combined ----

    [Fact]
    public void DogfoodPipeline_CommentsAndMaxValue_AllPropertiesCorrect()
    {
        var pgm = "P2\n# Created by Format Factory\n# MaxVal=50\n3 1\n50\n0 25 50\n";
        var doc = LoadAscii(pgm);

        // Comments
        Assert.Equal(2, doc.Image.Comments.Count);
        Assert.Contains(doc.Image.Comments, c => c.Contains("Format Factory"));

        // MaxValue
        Assert.Equal(50, doc.MaxValue);

        // Pixel values
        Assert.Equal(0,  (int)doc.GetPixel(0, 0));
        Assert.Equal(25, (int)doc.GetPixel(0, 1));
        Assert.Equal(50, (int)doc.GetPixel(0, 2));

        // Format detection still works
        Assert.True(doc.IsGrayscale);
        Assert.Equal(3, doc.Width);
    }
}
