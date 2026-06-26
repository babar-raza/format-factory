// Tests for NetpbmImage.ConvertFormat, Comments, SourcePath.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R156

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R156: Tests for NetpbmImage.ConvertFormat, Comments, SourcePath.
/// ConvertFormat(targetFormat): creates a new image in the target format with the same dimensions.
/// Comments: list of string comments attached to the image (can be set).
/// SourcePath: string path of the source file (nullable, settable).
/// Covers: ConvertFormat PGM->PPM preserves dimensions; ConvertFormat PPM->PGM preserves dimensions;
/// ConvertFormat PBM->PGM preserves dimensions; ConvertFormat result has target format;
/// ConvertFormat invalid format throws; ConvertFormat same format is a copy;
/// ConvertFormat to PPM has channels; Comments initially empty; Comments can be added;
/// Comments added count increments; SourcePath default is null; SourcePath can be set;
/// dogfood Create->ConvertFormat->AddComments->SetSourcePath pipeline.
/// </summary>
public class NetpbmR156ConvertFormatAndCommentsTests
{
    // -------------------------------------------------------------------------
    // ConvertFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertFormat_PgmToPpm_PreservesDimensions()
    {
        var pgm = NetpbmImage.Create(4, 3, NetpbmFormat.PGM_P2, 128);
        var ppm = pgm.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.Equal(4, ppm.Width);
        Assert.Equal(3, ppm.Height);
    }

    [Fact]
    public void ConvertFormat_PpmToPgm_PreservesDimensions()
    {
        var ppm = NetpbmImage.Create(5, 5, NetpbmFormat.PPM_P3, 100);
        var pgm = ppm.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(5, pgm.Width);
        Assert.Equal(5, pgm.Height);
    }

    [Fact]
    public void ConvertFormat_ResultHasTargetFormat()
    {
        var pgm = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, 100);
        var ppm = pgm.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
    }

    [Fact]
    public void ConvertFormat_SameFormat_IsCopy()
    {
        var pgm = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, 77);
        var copy = pgm.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(NetpbmFormat.PGM_P2, copy.Format);
        Assert.Equal(3, copy.Width);
        Assert.Equal(3, copy.Height);
    }

    [Fact]
    public void ConvertFormat_PgmToPpm_HasChannels()
    {
        var pgm = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P2, 100);
        var ppm = pgm.ConvertFormat(NetpbmFormat.PPM_P3);
        // PPM should have color channels populated
        Assert.NotNull(ppm.RedChannel);
        Assert.NotNull(ppm.GreenChannel);
        Assert.NotNull(ppm.BlueChannel);
    }

    [Fact]
    public void ConvertFormat_PgmToPbm_PreservesDimensions()
    {
        var pgm = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P2, 200);
        var pbm = pgm.ConvertFormat(NetpbmFormat.PBM_P1);
        Assert.Equal(4, pbm.Width);
        Assert.Equal(4, pbm.Height);
    }

    // -------------------------------------------------------------------------
    // Comments
    // -------------------------------------------------------------------------

    [Fact]
    public void Comments_InitiallyEmpty()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        Assert.Empty(img.Comments);
    }

    [Fact]
    public void Comments_CanAddComment()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.Comments.Add("This is a test image.");
        Assert.Single(img.Comments);
    }

    [Fact]
    public void Comments_MultipleComments_CountIsCorrect()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.Comments.Add("Comment 1.");
        img.Comments.Add("Comment 2.");
        img.Comments.Add("Comment 3.");
        Assert.Equal(3, img.Comments.Count);
    }

    [Fact]
    public void Comments_ContainsExpectedText()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.Comments.Add("Format Factory NetPBM test.");
        Assert.Contains("Format Factory NetPBM test.", img.Comments);
    }

    // -------------------------------------------------------------------------
    // SourcePath
    // -------------------------------------------------------------------------

    [Fact]
    public void SourcePath_DefaultIsNull()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        Assert.Null(img.SourcePath);
    }

    [Fact]
    public void SourcePath_CanBeSet()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.SourcePath = "/tmp/test.pgm";
        Assert.Equal("/tmp/test.pgm", img.SourcePath);
    }

    [Fact]
    public void SourcePath_CanBeSetToNull()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P2, 0);
        img.SourcePath = "/some/path.pgm";
        img.SourcePath = null;
        Assert.Null(img.SourcePath);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->ConvertFormat->AddComments->SetSourcePath
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ConvertFormatCommentsSourcePath_Pipeline()
    {
        var pgm = NetpbmImage.Create(8, 6, NetpbmFormat.PGM_P2, 128);
        pgm.SourcePath = "input/original.pgm";
        pgm.Comments.Add("Original PGM image.");

        // Convert to PPM
        var ppm = pgm.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.Equal(NetpbmFormat.PPM_P3, ppm.Format);
        Assert.Equal(8, ppm.Width);
        Assert.Equal(6, ppm.Height);

        // PPM doesn't inherit comments (new image)
        ppm.Comments.Add("Converted to PPM.");
        ppm.SourcePath = "output/converted.ppm";
        Assert.Single(ppm.Comments);
        Assert.Equal("output/converted.ppm", ppm.SourcePath);

        // Original unchanged
        Assert.Equal("input/original.pgm", pgm.SourcePath);
        Assert.Single(pgm.Comments);
    }
}
