// R104 Wave 1: Netpbm .NET MergeHorizontal tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R104-GOVERNED-DOTNET-NETPBM-MERGEHORIZONTAL-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR104MergeHorizontalTests
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
    public void MergeHorizontal_PGM_CorrectDimensions()
    {
        var a = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var b = MakePgm(3, 2, new byte[] { 5, 6, 7, 8, 9, 10 });
        var result = a.MergeHorizontal(b);
        Assert.Equal(5, result.Width);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void MergeHorizontal_PGM_PixelLayout()
    {
        // a: 2x2 [[1,2],[3,4]]  b: 1x2 [[5],[6]]
        var a = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var b = MakePgm(1, 2, new byte[] { 5, 6 });
        var result = a.MergeHorizontal(b);
        // row0: 1,2,5  row1: 3,4,6
        Assert.Equal(new byte[] { 1, 2, 5, 3, 4, 6 }, result.Pixels);
    }

    [Fact]
    public void MergeHorizontal_PPM_CorrectDimensions()
    {
        var a = MakePpm(1, 2, new byte[] { 1, 2 }, new byte[] { 3, 4 }, new byte[] { 5, 6 });
        var b = MakePpm(1, 2, new byte[] { 7, 8 }, new byte[] { 9, 10 }, new byte[] { 11, 12 });
        var result = a.MergeHorizontal(b);
        Assert.Equal(2, result.Width);
        Assert.Equal(2, result.Height);
    }

    [Fact]
    public void MergeHorizontal_PPM_ChannelLayout()
    {
        var a = MakePpm(1, 1, new byte[] { 10 }, new byte[] { 20 }, new byte[] { 30 });
        var b = MakePpm(1, 1, new byte[] { 40 }, new byte[] { 50 }, new byte[] { 60 });
        var result = a.MergeHorizontal(b);
        Assert.Equal(new byte[] { 10, 40 }, result.RedChannel);
        Assert.Equal(new byte[] { 20, 50 }, result.GreenChannel);
        Assert.Equal(new byte[] { 30, 60 }, result.BlueChannel);
    }

    [Fact]
    public void MergeHorizontal_HeightMismatch_Throws()
    {
        var a = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var b = MakePgm(2, 3, new byte[] { 5, 6, 7, 8, 9, 10 });
        Assert.Throws<ArgumentException>(() => a.MergeHorizontal(b));
    }

    [Fact]
    public void MergeHorizontal_FormatMismatch_Throws()
    {
        var pgm = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        var ppm = MakePpm(2, 2, new byte[] { 1, 2, 3, 4 }, new byte[] { 1, 2, 3, 4 }, new byte[] { 1, 2, 3, 4 });
        Assert.Throws<ArgumentException>(() => pgm.MergeHorizontal(ppm));
    }

    [Fact]
    public void MergeHorizontal_NullOther_Throws()
    {
        var img = MakePgm(2, 2, new byte[] { 1, 2, 3, 4 });
        Assert.Throws<ArgumentNullException>(() => img.MergeHorizontal(null!));
    }

    [Fact]
    public void MergeHorizontal_PreservesFormat()
    {
        var a = MakePgm(1, 1, new byte[] { 10 });
        var b = MakePgm(1, 1, new byte[] { 20 });
        var result = a.MergeHorizontal(b);
        Assert.Equal(NetpbmFormat.PGM_P5, result.Format);
    }

    [Fact]
    public void MergeHorizontal_DoesNotMutateOriginals()
    {
        var a = MakePgm(2, 1, new byte[] { 1, 2 });
        var b = MakePgm(1, 1, new byte[] { 3 });
        a.MergeHorizontal(b);
        Assert.Equal(2, a.Width);
        Assert.Equal(1, b.Width);
    }

    [Fact]
    public void MergeHorizontal_SaveToFile()
    {
        var a = MakePgm(2, 2, new byte[] { 10, 20, 30, 40 });
        var b = MakePgm(2, 2, new byte[] { 50, 60, 70, 80 });
        var result = a.MergeHorizontal(b);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            result.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
