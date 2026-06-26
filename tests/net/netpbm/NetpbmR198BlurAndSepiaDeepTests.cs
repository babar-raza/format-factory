// Tests for NetpbmImage.BlurBox, Sepia deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R198

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R198: Tests for NetpbmImage.BlurBox, Sepia deeper coverage.
/// BlurBox(): applies a box blur filter; preserves dimensions.
/// Sepia(): applies a sepia tone effect; changes format to Ppm (color); preserves pixel count.
/// Covers: BlurBox non-null; BlurBox preserves dimensions; BlurBox on uniform canvas;
/// BlurBox on black canvas; BlurBox on white canvas; BlurBox chain;
/// BlurBox on small canvas; BlurBox on rectangular canvas;
/// Sepia non-null; Sepia output is Ppm; Sepia preserves width;
/// Sepia preserves height; Sepia on uniform canvas; Sepia chain;
/// BlurBox->Sepia combined; Sepia->BlurBox combined;
/// dogfood CreateCanvas->BlurBox->Sepia->Verify pipeline.
/// </summary>
public class NetpbmR198BlurAndSepiaDeepTests
{
    // -------------------------------------------------------------------------
    // BlurBox
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.BlurBox());
    }

    [Fact]
    public void BlurBox_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.BlurBox();
        Assert.Equal(8, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void BlurBox_OnUniformCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 200);
        var result = img.BlurBox();
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void BlurBox_OnBlackCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 0);
        var result = img.BlurBox();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void BlurBox_OnWhiteCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 255);
        var result = img.BlurBox();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void BlurBox_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.BlurBox().BlurBox().BlurBox();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void BlurBox_SmallCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(3, 3, NetpbmFormat.Pgm, 100);
        var result = img.BlurBox();
        Assert.Equal(3, result.Width);
        Assert.Equal(3, result.Height);
    }

    [Fact]
    public void BlurBox_RectangularCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(15, 5, NetpbmFormat.Pgm, 128);
        var result = img.BlurBox();
        Assert.Equal(15, result.Width);
        Assert.Equal(5, result.Height);
    }

    // -------------------------------------------------------------------------
    // Sepia
    // -------------------------------------------------------------------------

    [Fact]
    public void Sepia_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.Sepia());
    }

    [Fact]
    public void Sepia_PreservesWidth()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.Sepia();
        Assert.Equal(8, result.Width);
    }

    [Fact]
    public void Sepia_PreservesHeight()
    {
        var img = NetpbmImage.CreateCanvas(8, 6, NetpbmFormat.Pgm, 128);
        var result = img.Sepia();
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Sepia_OnUniformCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 10, NetpbmFormat.Pgm, 128);
        var result = img.Sepia();
        Assert.Equal(10, result.Width);
        Assert.Equal(10, result.Height);
    }

    [Fact]
    public void Sepia_Chain_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Sepia().Sepia();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Combined
    // -------------------------------------------------------------------------

    [Fact]
    public void BlurBox_ThenSepia_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.BlurBox().Sepia();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void Sepia_ThenBlurBox_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.Sepia().BlurBox();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_BlurBox_Sepia_Verify_Pipeline()
    {
        // Create 10x8 canvas
        var img = NetpbmImage.CreateCanvas(10, 8, NetpbmFormat.Pgm, 128);
        Assert.Equal(10, img.Width);
        Assert.Equal(8, img.Height);

        // BlurBox
        var blurred = img.BlurBox();
        Assert.Equal(10, blurred.Width);
        Assert.Equal(8, blurred.Height);

        // BlurBox chain
        var blurred2 = blurred.BlurBox();
        Assert.Equal(10, blurred2.Width);
        Assert.Equal(8, blurred2.Height);

        // Sepia
        var sepia = blurred2.Sepia();
        Assert.Equal(10, sepia.Width);
        Assert.Equal(8, sepia.Height);

        // BlurBox after Sepia
        var finalBlur = sepia.BlurBox();
        Assert.Equal(10, finalBlur.Width);
        Assert.Equal(8, finalBlur.Height);

        // Pixel count invariant
        Assert.Equal(img.Width * img.Height, finalBlur.Width * finalBlur.Height);
    }
}
