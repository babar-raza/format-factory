using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R114 Train C: MedianFilter — noise-reduction median filter for image processing pipelines.
/// </summary>
public class NetpbmR114MedianFilterTests
{
    private static NetpbmImage MakeGrayscale(int w, int h, byte fill = 128)
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = new byte[w * h]
        };
        for (int i = 0; i < img.Pixels.Length; i++)
            img.Pixels[i] = fill;
        return img;
    }

    [Fact]
    public void MedianFilter_RadiusZero_ReturnsSamePixels()
    {
        var img = MakeGrayscale(4, 4, 100);
        var filtered = img.MedianFilter(0);
        Assert.Equal(img.Pixels, filtered.Pixels);
    }

    [Fact]
    public void MedianFilter_UniformImage_PreservesValues()
    {
        var img = MakeGrayscale(5, 5, 200);
        var filtered = img.MedianFilter(1);
        Assert.All(filtered.Pixels, p => Assert.Equal(200, p));
    }

    [Fact]
    public void MedianFilter_NegativeRadius_Throws()
    {
        var img = MakeGrayscale(4, 4);
        Assert.Throws<ArgumentOutOfRangeException>(() => img.MedianFilter(-1));
    }

    [Fact]
    public void MedianFilter_SameFormat()
    {
        var img = MakeGrayscale(4, 4);
        var filtered = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PGM_P2, filtered.Format);
    }

    [Fact]
    public void MedianFilter_SameDimensions()
    {
        var img = MakeGrayscale(6, 4);
        var filtered = img.MedianFilter(1);
        Assert.Equal(6, filtered.Width);
        Assert.Equal(4, filtered.Height);
    }

    [Fact]
    public void MedianFilter_SaltAndPepper_SmoothsNoise()
    {
        var img = MakeGrayscale(5, 5, 128);
        // Inject salt-and-pepper noise at center
        img.SetPixel(2, 2, 255);
        var filtered = img.MedianFilter(1);
        // After median filter, center should be close to 128
        Assert.True(filtered.GetPixel(2, 2) <= 200);
    }

    [Fact]
    public void MedianFilter_ColorImage_AllThreeChannelsFiltered()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P3, 150);
        var filtered = img.MedianFilter(1);
        Assert.Equal(NetpbmFormat.PPM_P3, filtered.Format);
        Assert.NotNull(filtered.RedChannel);
        Assert.NotNull(filtered.GreenChannel);
        Assert.NotNull(filtered.BlueChannel);
    }

    [Fact]
    public void MedianFilter_Radius2_LargerKernel()
    {
        var img = MakeGrayscale(8, 8, 64);
        var filtered = img.MedianFilter(2);
        Assert.Equal(8, filtered.Width);
        Assert.Equal(8, filtered.Height);
        Assert.All(filtered.Pixels, p => Assert.Equal(64, p));
    }
}
