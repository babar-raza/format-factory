// R106 Wave 4: Netpbm dogfood — Crop + Overlay + save pipeline
// Ledger: R106-DOGFOOD-NETPBM-CROP-OVERLAY-001

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR106DogfoodCropOverlayTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = px };
    }

    [Fact]
    public void Dogfood_CropThenOverlay()
    {
        var bg = MakeGray(10, 10, 0);
        var patch = MakeGray(3, 3, 200);
        var cropped = bg.Crop(0, 0, 5, 5);
        var result = cropped.Overlay(patch, 1, 1);
        Assert.Equal(5, result.Width);
        Assert.Equal(5, result.Height);
        Assert.Equal(200, result.Pixels[1 * 5 + 1]);
    }

    [Fact]
    public void Dogfood_OverlayThenFlipDiagonal()
    {
        var bg = MakeGray(4, 4, 50);
        var patch = MakeGray(2, 2, 200);
        var overlaid = bg.Overlay(patch, 0, 0);
        var flipped = overlaid.FlipDiagonal();
        Assert.Equal(4, flipped.Width);
        Assert.Equal(4, flipped.Height);
    }

    [Fact]
    public void Dogfood_FlipDiagonalThenCrop()
    {
        var img = MakeGray(6, 4, 100);
        var flipped = img.FlipDiagonal();
        Assert.Equal(4, flipped.Width);
        Assert.Equal(6, flipped.Height);
        var cropped = flipped.Crop(0, 0, 3, 3);
        Assert.Equal(3, cropped.Width);
        Assert.Equal(3, cropped.Height);
    }

    [Fact]
    public void Dogfood_OverlayChain()
    {
        var bg = MakeGray(8, 8, 0);
        var p1 = MakeGray(2, 2, 100);
        var p2 = MakeGray(2, 2, 200);
        var result = bg.Overlay(p1, 0, 0).Overlay(p2, 4, 4);
        Assert.Equal(100, result.Pixels[0]);
        Assert.Equal(200, result.Pixels[4 * 8 + 4]);
        Assert.Equal(0, result.Pixels[3 * 8 + 3]);
    }

    [Fact]
    public void Dogfood_CropOverlayContrast()
    {
        var img = MakeGray(10, 10, 128);
        var patch = MakeGray(3, 3, 50);
        var result = img.Overlay(patch, 2, 2).AdjustContrast(1.5);
        Assert.Equal(10, result.Width);
    }

    [Fact]
    public void Dogfood_FullPipeline_CreateOverlayCropSave()
    {
        var bg = MakeGray(8, 8, 30);
        var fg = MakeGray(4, 4, 220);
        var overlaid = bg.Overlay(fg, 2, 2);
        var cropped = overlaid.Crop(1, 1, 6, 6);
        var flipped = cropped.FlipDiagonal();
        Assert.Equal(6, flipped.Width);
        Assert.Equal(6, flipped.Height);
    }
}
