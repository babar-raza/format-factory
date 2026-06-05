// R107 Wave 4: Netpbm Equalize + Overlay + ConvertFormat dogfood pipeline
// Ledger: R107-DOGFOOD-NETPBM-EQUALIZE-OVERLAY

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR107DogfoodEqualizeOverlayTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    [Fact]
    public void Dogfood_OverlayThenEqualize()
    {
        var bg = MakeGray(8, 8, 30);
        var patch = MakeGray(3, 3, 200);
        var overlaid = bg.Overlay(patch, 2, 2);
        var equalized = overlaid.Equalize();
        Assert.Equal(8, equalized.Width);
        Assert.Equal(8, equalized.Height);
    }

    [Fact]
    public void Dogfood_EqualizeThenConvert()
    {
        var img = MakeGray(4, 4, 128);
        var eq = img.Equalize();
        var converted = eq.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(NetpbmFormat.PGM_P5, converted.Format);
    }

    [Fact]
    public void Dogfood_CropOverlayEqualizeConvert()
    {
        var bg = MakeGray(10, 10, 50);
        var fg = MakeGray(4, 4, 220);
        var cropped = bg.Crop(0, 0, 6, 6);
        var overlaid = cropped.Overlay(fg, 1, 1);
        var eq = overlaid.Equalize();
        var conv = eq.ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(6, conv.Width);
        Assert.Equal(6, conv.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, conv.Format);
    }

    [Fact]
    public void Dogfood_FlipDiagonalThenEqualize()
    {
        var img = MakeGray(6, 4, 100);
        var flipped = img.FlipDiagonal();
        var eq = flipped.Equalize();
        Assert.Equal(4, eq.Width);
        Assert.Equal(6, eq.Height);
    }

    [Fact]
    public void Dogfood_HistogramAfterEqualize()
    {
        // Gradient image — equalization should spread values
        var px = new byte[64];
        for (int i = 0; i < 64; i++) px[i] = (byte)(i * 4);
        var img = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = 8, Height = 8, MaxValue = 255, Pixels = px };
        var eq = img.Equalize();
        var hist = eq.GetHistogram();
        Assert.Equal(256, hist.Length);
    }

    [Fact]
    public void Dogfood_FullPipeline_CreateOverlayEqualizeConvertSave()
    {
        var bg = MakeGray(8, 8, 0);
        var fg = MakeGray(4, 4, 200);
        var result = bg.Overlay(fg, 2, 2).Equalize().ConvertFormat(NetpbmFormat.PGM_P5);
        Assert.Equal(8, result.Width);
        Assert.Equal(8, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }
}
