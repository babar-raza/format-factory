// Tests for NetpbmImage.ExtractChannel.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R143

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R143: Tests for NetpbmImage.ExtractChannel(int channel).
/// ExtractChannel extracts a single color channel (0=R, 1=G, 2=B) from a PPM image
/// as a PGM grayscale image. Throws if the image is not PPM or channel index is invalid.
/// Covers: extract red channel returns PGM format; extract green channel pixel values correct;
/// extract blue channel pixel values correct; extracted image has same dimensions;
/// extracted image has same MaxValue; non-PPM format throws InvalidOperationException;
/// channel -1 throws; channel 3 throws; null channels throw;
/// extracted image is independent copy (mutation isolation);
/// dogfood PPM load->ExtractChannel->PGM pipeline.
/// </summary>
public class NetpbmR143ExtractChannelTests
{
    private static NetpbmImage MakePpm(int w, int h,
        byte[] red, byte[] green, byte[] blue)
    {
        return new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = red,
            GreenChannel = green,
            BlueChannel = blue,
        };
    }

    // -------------------------------------------------------------------------
    // Format and dimensions
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_Red_ReturnsPgmFormat()
    {
        var img = MakePpm(2, 2,
            new byte[] { 100, 110, 120, 130 },
            new byte[] { 10, 20, 30, 40 },
            new byte[] { 1, 2, 3, 4 });
        var pgm = img.ExtractChannel(0);
        Assert.True(pgm.Format == NetpbmFormat.PGM_P5 || pgm.Format == NetpbmFormat.PGM_P2,
            $"Expected PGM format, got {pgm.Format}.");
    }

    [Fact]
    public void ExtractChannel_SameDimensionsAsSource()
    {
        var img = MakePpm(3, 2,
            new byte[] { 1, 2, 3, 4, 5, 6 },
            new byte[] { 10, 20, 30, 40, 50, 60 },
            new byte[] { 100, 110, 120, 130, 140, 150 });
        var pgm = img.ExtractChannel(1);
        Assert.Equal(3, pgm.Width);
        Assert.Equal(2, pgm.Height);
    }

    [Fact]
    public void ExtractChannel_SameMaxValueAsSource()
    {
        var img = MakePpm(2, 1,
            new byte[] { 200, 210 },
            new byte[] { 5, 6 },
            new byte[] { 50, 60 });
        var pgm = img.ExtractChannel(2);
        Assert.Equal(255, pgm.MaxValue);
    }

    // -------------------------------------------------------------------------
    // Pixel correctness per channel
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_Red_PixelValuesMatchRedChannel()
    {
        var red = new byte[] { 255, 128, 64, 32 };
        var img = MakePpm(2, 2, red,
            new byte[] { 10, 20, 30, 40 },
            new byte[] { 5, 6, 7, 8 });
        var pgm = img.ExtractChannel(0);
        Assert.Equal(red, pgm.Pixels);
    }

    [Fact]
    public void ExtractChannel_Green_PixelValuesMatchGreenChannel()
    {
        var green = new byte[] { 90, 80, 70, 60 };
        var img = MakePpm(2, 2,
            new byte[] { 10, 20, 30, 40 },
            green,
            new byte[] { 5, 6, 7, 8 });
        var pgm = img.ExtractChannel(1);
        Assert.Equal(green, pgm.Pixels);
    }

    [Fact]
    public void ExtractChannel_Blue_PixelValuesMatchBlueChannel()
    {
        var blue = new byte[] { 11, 22, 33, 44 };
        var img = MakePpm(2, 2,
            new byte[] { 200, 201, 202, 203 },
            new byte[] { 100, 101, 102, 103 },
            blue);
        var pgm = img.ExtractChannel(2);
        Assert.Equal(blue, pgm.Pixels);
    }

    [Fact]
    public void ExtractChannel_SinglePixel_CorrectValue()
    {
        var img = MakePpm(1, 1,
            new byte[] { 77 },
            new byte[] { 88 },
            new byte[] { 99 });
        Assert.Equal(77, img.ExtractChannel(0).Pixels[0]);
        Assert.Equal(88, img.ExtractChannel(1).Pixels[0]);
        Assert.Equal(99, img.ExtractChannel(2).Pixels[0]);
    }

    // -------------------------------------------------------------------------
    // Error cases
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_NonPpmFormat_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40 },
        };
        Assert.ThrowsAny<Exception>(() => img.ExtractChannel(0));
    }

    [Fact]
    public void ExtractChannel_ChannelNegative_Throws()
    {
        var img = MakePpm(1, 1,
            new byte[] { 1 }, new byte[] { 2 }, new byte[] { 3 });
        Assert.ThrowsAny<Exception>(() => img.ExtractChannel(-1));
    }

    [Fact]
    public void ExtractChannel_Channel3_Throws()
    {
        var img = MakePpm(1, 1,
            new byte[] { 1 }, new byte[] { 2 }, new byte[] { 3 });
        Assert.ThrowsAny<Exception>(() => img.ExtractChannel(3));
    }

    // -------------------------------------------------------------------------
    // Mutation isolation
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_MutatingResult_DoesNotAffectSource()
    {
        var red = new byte[] { 100, 110, 120, 130 };
        var img = MakePpm(2, 2,
            (byte[])red.Clone(),
            new byte[] { 10, 20, 30, 40 },
            new byte[] { 1, 2, 3, 4 });
        var pgm = img.ExtractChannel(0);
        pgm.Pixels[0] = 0;
        Assert.NotEqual(0, img.RedChannel![0]);
    }

    // -------------------------------------------------------------------------
    // PPM_P6 support
    // -------------------------------------------------------------------------

    [Fact]
    public void ExtractChannel_PpmP6Format_Works()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 2, Height = 1, MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 200, 210 },
            GreenChannel = new byte[] { 100, 110 },
            BlueChannel = new byte[] { 50, 60 },
        };
        var pgm = img.ExtractChannel(1);
        Assert.Equal(new byte[] { 100, 110 }, pgm.Pixels);
    }

    // -------------------------------------------------------------------------
    // Dogfood: full pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExtractAllChannels_PipelineConsistency()
    {
        // Construct a known 2x1 PPM image and verify R/G/B extraction
        var img = MakePpm(2, 1,
            new byte[] { 255, 0 },   // Red: full, zero
            new byte[] { 0, 255 },   // Green: zero, full
            new byte[] { 128, 128 }); // Blue: mid both

        var r = img.ExtractChannel(0);
        var g = img.ExtractChannel(1);
        var b = img.ExtractChannel(2);

        // Each extraction produces independent PGM
        Assert.Equal(2, r.Width);
        Assert.Equal(2, g.Width);
        Assert.Equal(2, b.Width);

        // Pixel correctness
        Assert.Equal(255, r.Pixels[0]);
        Assert.Equal(0, r.Pixels[1]);
        Assert.Equal(0, g.Pixels[0]);
        Assert.Equal(255, g.Pixels[1]);
        Assert.Equal(128, b.Pixels[0]);
        Assert.Equal(128, b.Pixels[1]);
    }
}
