// R105 Wave 2: Netpbm .NET MergeVertical tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R105-GOVERNED-DOTNET-NETPBM-MERGEVERTICAL-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR105MergeVerticalTests
{
    private static NetpbmImage MakePgm(int w, int h, byte[] pixels) => new()
    {
        Format = NetpbmFormat.PGM_P5,
        Width = w, Height = h, MaxValue = 255,
        Pixels = pixels,
    };

    private static NetpbmImage MakePpm(int w, int h, byte[] r, byte[] g, byte[] b) => new()
    {
        Format = NetpbmFormat.PPM_P6,
        Width = w, Height = h, MaxValue = 255,
        RedChannel = r, GreenChannel = g, BlueChannel = b,
        Pixels = Array.Empty<byte>(),
    };

    [Fact]
    public void MergeVertical_PGM_CorrectDimensions()
    {
        var top = MakePgm(3, 2, new byte[] { 1, 2, 3, 4, 5, 6 });
        var bot = MakePgm(3, 3, new byte[] { 7, 8, 9, 10, 11, 12, 13, 14, 15 });
        var result = top.MergeVertical(bot);
        Assert.Equal(3, result.Width);
        Assert.Equal(5, result.Height);
    }

    [Fact]
    public void MergeVertical_PGM_PixelLayout()
    {
        var top = MakePgm(2, 1, new byte[] { 1, 2 });
        var bot = MakePgm(2, 1, new byte[] { 3, 4 });
        var result = top.MergeVertical(bot);
        Assert.Equal(new byte[] { 1, 2, 3, 4 }, result.Pixels);
    }

    [Fact]
    public void MergeVertical_PPM_CorrectDimensions()
    {
        var top = MakePpm(2, 1, new byte[] { 1, 2 }, new byte[] { 3, 4 }, new byte[] { 5, 6 });
        var bot = MakePpm(2, 1, new byte[] { 7, 8 }, new byte[] { 9, 10 }, new byte[] { 11, 12 });
        var result = top.MergeVertical(bot);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void MergeVertical_PPM_ChannelLayout()
    {
        var top = MakePpm(1, 1, new byte[] { 10 }, new byte[] { 20 }, new byte[] { 30 });
        var bot = MakePpm(1, 1, new byte[] { 40 }, new byte[] { 50 }, new byte[] { 60 });
        var result = top.MergeVertical(bot);
        Assert.Equal(new byte[] { 10, 40 }, result.RedChannel);
        Assert.Equal(new byte[] { 20, 50 }, result.GreenChannel);
        Assert.Equal(new byte[] { 30, 60 }, result.BlueChannel);
    }

    [Fact]
    public void MergeVertical_WidthMismatch_Throws()
    {
        var a = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var b = MakePgm(3, 2, new byte[] { 5, 6, 7, 8, 9, 10 });
        Assert.Throws<ArgumentException>(() => a.MergeVertical(b));
    }

    [Fact]
    public void MergeVertical_FormatMismatch_Throws()
    {
        var pgm = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var ppm = MakePpm(2, 2, new byte[] { 1, 2, 3, 4 }, new byte[] { 1, 2, 3, 4 }, new byte[] { 1, 2, 3, 4 });
        Assert.Throws<ArgumentException>(() => pgm.MergeVertical(ppm));
    }

    [Fact]
    public void MergeVertical_NullOther_Throws()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        Assert.Throws<ArgumentNullException>(() => img.MergeVertical(null!));
    }

    [Fact]
    public void MergeVertical_PreservesFormat()
    {
        var a = MakePgm(1, 1, new byte[] { 10 });
        var b = MakePgm(1, 1, new byte[] { 20 });
        var result = a.MergeVertical(b);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeVertical_DoesNotMutateOriginals()
    {
        var a = MakePgm(2, 1, new byte[] { 1, 2 });
        var b = MakePgm(2, 1, new byte[] { 3, 4 });
        a.MergeVertical(b);
        Assert.Equal(1, a.Height);
        Assert.Equal(1, b.Height);
    }

    [Fact]
    public void MergeVertical_SaveToFile()
    {
        var top = MakePgm(2, 2, new byte[] { 10, 20, 30, 40 });
        var bot = MakePgm(2, 2, new byte[] { 50, 60, 70, 80 });
        var result = top.MergeVertical(bot);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            result.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
