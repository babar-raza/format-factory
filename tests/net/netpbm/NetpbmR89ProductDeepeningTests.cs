// R89 Train H: Netpbm .NET Product Deepening Tests
// New APIs: GetChannelStats, Rotate90Cw, Crop
// Sprint: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR89GetChannelStatsTests
{
    [Fact]
    public void GetChannelStats_ReturnsPerChannelStatistics()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 10, 20 },
            GreenChannel = new byte[] { 30, 40 },
            BlueChannel = new byte[] { 50, 60 }
        };

        var stats = img.GetChannelStats();

        Assert.Equal(15.0, stats.R.Mean);
        Assert.Equal(10, stats.R.Min);
        Assert.Equal(20, stats.R.Max);
        Assert.Equal(35.0, stats.G.Mean);
        Assert.Equal(55.0, stats.B.Mean);
    }

    [Fact]
    public void GetChannelStats_ThrowsOnPgm()
    {
        var img = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = 1, Height = 1, Pixels = new byte[] { 128 } };
        Assert.Throws<System.InvalidOperationException>(() => img.GetChannelStats());
    }

    [Fact]
    public void GetChannelStats_SinglePixelImage()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 100 },
            GreenChannel = new byte[] { 150 },
            BlueChannel = new byte[] { 200 }
        };

        var stats = img.GetChannelStats();
        Assert.Equal(100.0, stats.R.Mean);
        Assert.Equal(150.0, stats.G.Mean);
        Assert.Equal(200.0, stats.B.Mean);
    }
}

public class NetpbmR89Rotate90CwTests
{
    [Fact]
    public void Rotate90Cw_SwapsDimensions()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6 }
        };

        var rotated = img.Rotate90Cw();

        Assert.Equal(2, rotated.Width);  // old height
        Assert.Equal(3, rotated.Height); // old width
    }

    [Fact]
    public void Rotate90Cw_CorrectPixelMapping_PGM()
    {
        // Original 2x3:
        //  1 2 3
        //  4 5 6
        // After 90CW (3x2):
        //  4 1
        //  5 2
        //  6 3
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6 }
        };

        var rotated = img.Rotate90Cw();

        Assert.Equal(4, rotated.GetPixel(0, 0));
        Assert.Equal(1, rotated.GetPixel(0, 1));
        Assert.Equal(5, rotated.GetPixel(1, 0));
        Assert.Equal(2, rotated.GetPixel(1, 1));
        Assert.Equal(6, rotated.GetPixel(2, 0));
        Assert.Equal(3, rotated.GetPixel(2, 1));
    }

    [Fact]
    public void Rotate90Cw_FourTimesRestoresOriginal()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 3, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0, 1, 1 }
        };

        var result = img.Rotate90Cw().Rotate90Cw().Rotate90Cw().Rotate90Cw();

        Assert.Equal(img.Width, result.Width);
        Assert.Equal(img.Height, result.Height);
        Assert.Equal(img.Pixels, result.Pixels);
    }

    [Fact]
    public void Rotate90Cw_PPM_PreservesChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            RedChannel = new byte[] { 10, 20 },
            GreenChannel = new byte[] { 30, 40 },
            BlueChannel = new byte[] { 50, 60 }
        };

        var rotated = img.Rotate90Cw();

        Assert.Equal(1, rotated.Width);
        Assert.Equal(2, rotated.Height);
        // Top pixel should be bottom-left of original → (10, 30, 50)
        var (r0, g0, b0) = rotated.GetPixelColor(0, 0);
        Assert.Equal(10, r0);
        Assert.Equal(30, g0);
        Assert.Equal(50, b0);
    }

    [Fact]
    public void Rotate90Cw_PreservesComments()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 128 }
        };
        img.Comments.Add("test comment");

        var rotated = img.Rotate90Cw();
        Assert.Contains("test comment", rotated.Comments);
    }
}

public class NetpbmR89CropTests
{
    [Fact]
    public void Crop_ExtractsSubregion_PGM()
    {
        // 3x3 image:
        //  1  2  3
        //  4  5  6
        //  7  8  9
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 3, MaxValue = 255,
            Pixels = new byte[] { 1, 2, 3, 4, 5, 6, 7, 8, 9 }
        };

        // Crop 2x2 from (0,1)
        var cropped = img.Crop(0, 1, 2, 2);

        Assert.Equal(2, cropped.Width);
        Assert.Equal(2, cropped.Height);
        Assert.Equal(2, cropped.GetPixel(0, 0));
        Assert.Equal(3, cropped.GetPixel(0, 1));
        Assert.Equal(5, cropped.GetPixel(1, 0));
        Assert.Equal(6, cropped.GetPixel(1, 1));
    }

    [Fact]
    public void Crop_FullImage_ReturnsCopy()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 }
        };

        var cropped = img.Crop(0, 0, 2, 2);
        Assert.Equal(img.Pixels, cropped.Pixels);
        Assert.NotSame(img.Pixels, cropped.Pixels);
    }

    [Fact]
    public void Crop_PPM_PreservesChannels()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 2, MaxValue = 255,
            RedChannel = new byte[] { 10, 20, 30, 40 },
            GreenChannel = new byte[] { 50, 60, 70, 80 },
            BlueChannel = new byte[] { 90, 100, 110, 120 }
        };

        var cropped = img.Crop(1, 0, 1, 2);

        Assert.Equal(2, cropped.Width);
        Assert.Equal(1, cropped.Height);
        var (r, g, b) = cropped.GetPixelColor(0, 0);
        Assert.Equal(30, r);
        Assert.Equal(70, g);
        Assert.Equal(110, b);
    }

    [Fact]
    public void Crop_InvalidBounds_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 3, MaxValue = 255,
            Pixels = new byte[9]
        };

        Assert.Throws<System.ArgumentOutOfRangeException>(() => img.Crop(2, 2, 2, 2));
    }

    [Fact]
    public void Crop_ZeroDimension_Throws()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 3, MaxValue = 255,
            Pixels = new byte[9]
        };

        Assert.Throws<System.ArgumentOutOfRangeException>(() => img.Crop(0, 0, 0, 1));
    }
}
