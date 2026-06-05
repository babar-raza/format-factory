// R105 Wave 4: Netpbm .NET dogfood — MergeVertical + AdjustContrast pipeline
// Ledger: R105-DOGFOOD-NETPBM-MERGE-PIPELINE-001

using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR105DogfoodMergePipelineTests
{
    private static NetpbmImage MakeGray(int w, int h, byte val)
    {
        var pixels = new byte[w * h];
        for (int i = 0; i < pixels.Length; i++) pixels[i] = val;
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = pixels };
    }

    private static NetpbmImage MakeRgb(int w, int h, byte r, byte g, byte b)
    {
        var size = w * h;
        var red = new byte[size];
        var green = new byte[size];
        var blue = new byte[size];
        for (int i = 0; i < size; i++) { red[i] = r; green[i] = g; blue[i] = b; }
        return new NetpbmImage { Format = NetpbmFormat.PPM_P3, Width = w, Height = h, MaxValue = 255, RedChannel = red, GreenChannel = green, BlueChannel = blue };
    }

    [Fact]
    public void Dogfood_MergeTwoGrays_ThenAdjustContrast()
    {
        var top = MakeGray(4, 2, 100);
        var bot = MakeGray(4, 2, 200);
        var merged = top.MergeVertical(bot);
        Assert.Equal(4, merged.Height);
        var adjusted = merged.AdjustContrast(1.5);
        Assert.Equal(4, adjusted.Width);
        Assert.Equal(4, adjusted.Height);
    }

    [Fact]
    public void Dogfood_MergeTwoRgb_ThenAdjustContrast()
    {
        var top = MakeRgb(3, 2, 255, 0, 0);
        var bot = MakeRgb(3, 2, 0, 0, 255);
        var merged = top.MergeVertical(bot);
        Assert.Equal(4, merged.Height);
        Assert.Equal(3, merged.Width);
        var adj = merged.AdjustContrast(0.5);
        Assert.Equal(4, adj.Height);
    }

    [Fact]
    public void Dogfood_MergeChain_ThreeImages()
    {
        var a = MakeGray(2, 1, 50);
        var b = MakeGray(2, 1, 100);
        var c = MakeGray(2, 1, 150);
        var merged = a.MergeVertical(b).MergeVertical(c);
        Assert.Equal(3, merged.Height);
        Assert.Equal(2, merged.Width);
    }

    [Fact]
    public void Dogfood_AdjustContrast_IdentityFactor()
    {
        var img = MakeGray(4, 4, 128);
        var adj = img.AdjustContrast(1.0);
        for (int i = 0; i < adj.Pixels.Length; i++)
            Assert.Equal(128, adj.Pixels[i]);
    }

    [Fact]
    public void Dogfood_MergeVertical_PixelPreservation()
    {
        var top = MakeGray(2, 2, 10);
        var bot = MakeGray(2, 2, 250);
        var merged = top.MergeVertical(bot);
        Assert.Equal(10, merged.Pixels[0]);
        Assert.Equal(250, merged.Pixels[merged.Pixels.Length - 1]);
    }

    [Fact]
    public void Dogfood_FullPipeline_CreateMergeContrastVerify()
    {
        var dark = MakeRgb(2, 2, 30, 30, 30);
        var bright = MakeRgb(2, 2, 220, 220, 220);
        var merged = dark.MergeVertical(bright);
        var boosted = merged.AdjustContrast(2.0);
        Assert.Equal(4, boosted.Height);
        // Dark pixels should get darker, bright should get brighter (clamped)
        Assert.True(boosted.RedChannel![0] < 30);
        Assert.True(boosted.RedChannel[boosted.RedChannel.Length - 1] >= 220);
    }
}
