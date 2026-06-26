// Tests for NetpbmImage.ExtractChannel, ToColor, ToGrayscale deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R199

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R199: Tests for NetpbmImage.ExtractChannel, ToColor, ToGrayscale deeper coverage.
/// ExtractChannel(channel): extracts a single color channel (R, G, B) from a Ppm image as Pgm.
/// ToColor(): converts a Pgm grayscale image to Ppm color format.
/// ToGrayscale(): converts a Ppm color image to Pgm grayscale format.
/// Covers: ExtractChannel red non-null; ExtractChannel green non-null; ExtractChannel blue non-null;
/// ExtractChannel preserves dimensions; ExtractChannel output is Pgm;
/// ToColor non-null; ToColor preserves dimensions; ToColor from Pgm produces Ppm;
/// ToGrayscale non-null; ToGrayscale preserves dimensions; ToGrayscale from Ppm produces Pgm;
/// ToColor->ToGrayscale round-trip dimensions; ToGrayscale->ToColor round-trip dimensions;
/// ExtractChannel->ToColor dimensions; ExtractChannel from ToColor image;
/// dogfood CreateCanvas->ToColor->ExtractChannel->ToGrayscale->Verify pipeline.
/// </summary>
public class NetpbmR199ExtractChannelAndToColorDeepTests
{
    // -------------------------------------------------------------------------
    // ExtractChannel
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_Red_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        Assert.NotNull(img.ExtractChannel(NetpbmChannel.Red));
    }

    [Fact]
    public void ExtractChannel_Green_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        Assert.NotNull(img.ExtractChannel(NetpbmChannel.Green));
    }

    [Fact]
    public void ExtractChannel_Blue_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        Assert.NotNull(img.ExtractChannel(NetpbmChannel.Blue));
    }

    [Fact]
    public void ExtractChannel_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, NetpbmFormat.Ppm, 128);
        var extracted = img.ExtractChannel(NetpbmChannel.Red);
        Assert.Equal(10, extracted.Width);
        Assert.Equal(6, extracted.Height);
    }

    [Fact]
    public void ExtractChannel_OutputFormat_IsPgm()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 200);
        var extracted = img.ExtractChannel(NetpbmChannel.Green);
        Assert.Equal(NetpbmFormat.Pgm, extracted.Format);
    }

    [Fact]
    public void ExtractChannel_AllChannels_SameDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        var r = img.ExtractChannel(NetpbmChannel.Red);
        var g = img.ExtractChannel(NetpbmChannel.Green);
        var b = img.ExtractChannel(NetpbmChannel.Blue);
        Assert.Equal(r.Width, g.Width);
        Assert.Equal(g.Width, b.Width);
        Assert.Equal(r.Height, g.Height);
    }

    // -------------------------------------------------------------------------
    // ToColor
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        Assert.NotNull(img.ToColor());
    }

    [Fact]
    public void ToColor_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, NetpbmFormat.Pgm, 128);
        var result = img.ToColor();
        Assert.Equal(10, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void ToColor_FromPgm_OutputIsPpm()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.ToColor();
        Assert.Equal(NetpbmFormat.Ppm, result.Format);
    }

    [Fact]
    public void ToColor_OnPpCanvas_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        var result = img.ToColor();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // ToGrayscale
    // -------------------------------------------------------------------------

    [Fact]
    public void ToGrayscale_NonNull()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        Assert.NotNull(img.ToGrayscale());
    }

    [Fact]
    public void ToGrayscale_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(10, 6, NetpbmFormat.Ppm, 128);
        var result = img.ToGrayscale();
        Assert.Equal(10, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void ToGrayscale_FromPpm_OutputIsPgm()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        var result = img.ToGrayscale();
        Assert.Equal(NetpbmFormat.Pgm, result.Format);
    }

    // -------------------------------------------------------------------------
    // Combined
    // -------------------------------------------------------------------------

    [Fact]
    public void ToColor_ThenToGrayscale_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Pgm, 128);
        var result = img.ToColor().ToGrayscale();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    [Fact]
    public void ToGrayscale_ThenToColor_PreservesDimensions()
    {
        var img = NetpbmImage.CreateCanvas(8, 8, NetpbmFormat.Ppm, 128);
        var result = img.ToGrayscale().ToColor();
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateCanvas_ToColor_ExtractChannel_ToGrayscale_Verify_Pipeline()
    {
        // Create Pgm canvas
        var pgm = NetpbmImage.CreateCanvas(10, 8, NetpbmFormat.Pgm, 128);
        Assert.Equal(10, pgm.Width);
        Assert.Equal(8, pgm.Height);
        Assert.Equal(NetpbmFormat.Pgm, pgm.Format);

        // ToColor — becomes Ppm
        var ppm = pgm.ToColor();
        Assert.Equal(10, ppm.Width);
        Assert.Equal(8, ppm.Height);
        Assert.Equal(NetpbmFormat.Ppm, ppm.Format);

        // ExtractChannel — becomes Pgm
        var redChannel = ppm.ExtractChannel(NetpbmChannel.Red);
        Assert.Equal(10, redChannel.Width);
        Assert.Equal(8, redChannel.Height);
        Assert.Equal(NetpbmFormat.Pgm, redChannel.Format);

        // ToGrayscale from Ppm — becomes Pgm
        var gray = ppm.ToGrayscale();
        Assert.Equal(10, gray.Width);
        Assert.Equal(8, gray.Height);
        Assert.Equal(NetpbmFormat.Pgm, gray.Format);

        // Chain: ToColor->ExtractChannel->dimensions match
        var greenChannel = ppm.ExtractChannel(NetpbmChannel.Green);
        Assert.Equal(redChannel.Width, greenChannel.Width);
        Assert.Equal(redChannel.Height, greenChannel.Height);
    }
}
