// R114: NetpbmImage.Pipeline — sequential image transformation
// Governed /add-dotnet-api sprint: FORMAT-FACTORY-MAINSTREAM-R114-PRODUCT-EXECUTION-*

using Xunit;
using System;
using System.Collections.Generic;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR114FlipMergePipelineTests
{
    private static NetpbmImage MakePgm(int w, int h, byte fill = 100)
    {
        var pixels = new byte[w * h];
        Array.Fill(pixels, fill);
        return new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = w,
            Height = h,
            MaxValue = 255,
            Pixels = pixels,
        };
    }

    [Fact]
    public void Pipeline_EmptySteps_ReturnsSameImage()
    {
        var img = MakePgm(4, 4, 128);
        var result = img.Pipeline(Array.Empty<Func<NetpbmImage, NetpbmImage>>());
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
    }

    [Fact]
    public void Pipeline_SingleStep_AppliesTransform()
    {
        var img = MakePgm(4, 4, 50);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.AdjustBrightness(50)
        });
        Assert.Equal(4, result.Width);
        // Brightness 50 added — all pixels should be >= 50
        foreach (var px in result.Pixels)
            Assert.True(px >= 50);
    }

    [Fact]
    public void Pipeline_MultiStep_AppliesAllInOrder()
    {
        var img = MakePgm(4, 4, 50);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.AdjustBrightness(30),   // 50 -> 80
            i => i.AdjustBrightness(20),   // 80 -> 100
            i => i.AdjustBrightness(55),   // 100 -> 155
        });
        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
        // All pixels should be 155 after +30+20+55
        foreach (var px in result.Pixels)
            Assert.Equal(155, px);
    }

    [Fact]
    public void Pipeline_NullSteps_ThrowsArgumentNullException()
    {
        var img = MakePgm(2, 2);
        Assert.Throws<ArgumentNullException>(() =>
            img.Pipeline(null!));
    }

    [Fact]
    public void Pipeline_NullStepInSequence_ThrowsArgumentNullException()
    {
        var img = MakePgm(2, 2);
        var steps = new Func<NetpbmImage, NetpbmImage>[] { null! };
        Assert.Throws<ArgumentNullException>(() =>
            img.Pipeline(steps));
    }

    [Fact]
    public void Pipeline_PreservesFormat()
    {
        var img = MakePgm(4, 4, 80);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.AdjustBrightness(10),
            i => i.AdjustBrightness(10),
        });
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    [Fact]
    public void Pipeline_FlipThenBrightness_ProducesCorrectDimensions()
    {
        var img = MakePgm(6, 3, 100);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.FlipDiagonal(),       // 6x3 -> 3x6
            i => i.AdjustBrightness(20),
        });
        Assert.Equal(3, result.Width);
        Assert.Equal(6, result.Height);
    }

    [Fact]
    public void Pipeline_ListInput_WorksLikeArray()
    {
        var img = MakePgm(4, 4, 60);
        var steps = new List<Func<NetpbmImage, NetpbmImage>>
        {
            i => i.AdjustBrightness(40),
            i => i.AdjustBrightness(0),
        };
        var result = img.Pipeline(steps);
        Assert.Equal(4, result.Width);
        // 60 + 40 = 100
        foreach (var px in result.Pixels)
            Assert.Equal(100, px);
    }

    [Fact]
    public void Pipeline_MergeAfterBrightness_DimensionsDoubled()
    {
        var img = MakePgm(4, 2, 80);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.AdjustBrightness(20),
            i => i.MergeHorizontal(i),   // 4x2 + 4x2 = 8x2
        });
        Assert.Equal(8, result.Width);
        Assert.Equal(2, result.Height);
    }
}
