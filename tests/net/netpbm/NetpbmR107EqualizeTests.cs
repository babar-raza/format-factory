// R107 Wave 2: Netpbm Equalize tests
// Ledger: R107-NETPBM-EQUALIZE

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR107EqualizeTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    [Fact]
    public void Equalize_UniformImage_ReturnsSameDimensions()
    {
        var img = MakeGray(4, 4, 128);
        var eq = img.Equalize();
        Assert.Equal(4, eq.Width);
        Assert.Equal(4, eq.Height);
        Assert.Equal(255, eq.MaxValue);
    }

    [Fact]
    public void Equalize_AllSameValue_MapsToMaxOrSingle()
    {
        var img = MakeGray(4, 4, 100);
        var eq = img.Equalize();
        // All pixels same → CDF is step function → all map to same value
        byte first = eq.Pixels[0];
        for (int i = 1; i < eq.Pixels.Length; i++)
            Assert.Equal(first, eq.Pixels[i]);
    }

    [Fact]
    public void Equalize_GradientImage_SpreadsDynamicRange()
    {
        var px = new byte[256];
        for (int i = 0; i < 256; i++) px[i] = (byte)i;
        var img = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = 256, Height = 1, MaxValue = 255, Pixels = px };
        var eq = img.Equalize();
        // Perfect gradient → equalization should keep values spread across full range
        Assert.Equal(0, eq.Pixels[0]);
        Assert.Equal(255, eq.Pixels[255]);
    }

    [Fact]
    public void Equalize_PBM_ReturnsClone()
    {
        var px = new byte[] { 0, 1, 0, 1 };
        var img = new NetpbmImage { Format = NetpbmFormat.PBM_P1, Width = 2, Height = 2, MaxValue = 1, Pixels = px };
        var eq = img.Equalize();
        Assert.Equal(NetpbmFormat.PBM_P1, eq.Format);
        Assert.Equal(px, eq.Pixels);
    }

    [Fact]
    public void Equalize_PPM_ConvertsToGrayscale()
    {
        int len = 4;
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[0],
            RedChannel = new byte[] { 100, 150, 200, 50 },
            GreenChannel = new byte[] { 100, 150, 200, 50 },
            BlueChannel = new byte[] { 100, 150, 200, 50 },
        };
        var eq = img.Equalize();
        // PPM equalization converts to PGM
        Assert.True(eq.Format == NetpbmFormat.PGM_P5);
    }

    [Fact]
    public void Equalize_1x1Image_ReturnsValue()
    {
        var img = MakeGray(1, 1, 42);
        var eq = img.Equalize();
        Assert.Equal(1, eq.Width);
        Assert.Equal(1, eq.Height);
    }

    [Fact]
    public void Equalize_DoesNotMutateOriginal()
    {
        var img = MakeGray(4, 4, 128);
        byte original = img.Pixels[0];
        var eq = img.Equalize();
        Assert.Equal(original, img.Pixels[0]);
    }

    [Fact]
    public void Equalize_LargeImage_Completes()
    {
        var px = new byte[100 * 100];
        for (int i = 0; i < px.Length; i++) px[i] = (byte)(i % 256);
        var img = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = 100, Height = 100, MaxValue = 255, Pixels = px };
        var eq = img.Equalize();
        Assert.Equal(100, eq.Width);
        Assert.Equal(100, eq.Height);
    }
}
