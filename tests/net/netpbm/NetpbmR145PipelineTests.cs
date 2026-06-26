// Tests for NetpbmImage.Pipeline and NetpbmImage.Create.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R145

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R145: Tests for NetpbmImage.Pipeline and NetpbmImage.Create.
/// Pipeline(steps) applies a sequence of image transforms, each step receiving the
/// previous step's output. Throws ArgumentNullException if steps or any step is null.
/// Create(width, height, format, fill) creates a blank canvas filled with the given byte value;
/// PPM channels are also filled; invalid dimensions throw.
/// Covers: Pipeline empty steps returns same image; Pipeline single step applies it;
/// Pipeline multiple steps applied in order; Pipeline null steps throws;
/// Pipeline null step in sequence throws; Pipeline result is independent of source;
/// Create PGM fills pixels; Create PPM fills all channels;
/// Create width zero throws; Create height zero throws;
/// dogfood Create->Pipeline composition.
/// </summary>
public class NetpbmR145PipelineTests
{
    private static NetpbmImage MakeGray(int w, int h, byte fill)
    {
        var px = new byte[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = fill;
        return new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = w, Height = h, MaxValue = 255, Pixels = px,
        };
    }

    // -------------------------------------------------------------------------
    // Pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Pipeline_EmptySteps_ReturnsSameContent()
    {
        var img = MakeGray(2, 2, 100);
        var result = img.Pipeline(Array.Empty<Func<NetpbmImage, NetpbmImage>>());
        Assert.Equal(img.Pixels, result.Pixels);
    }

    [Fact]
    public void Pipeline_SingleStep_AppliesTransform()
    {
        var img = MakeGray(2, 2, 50);
        // Single step: convert to binary (P2 format)
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.ConvertFormat(NetpbmFormat.PGM_P2)
        });
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
    }

    [Fact]
    public void Pipeline_MultipleSteps_AppliedInOrder()
    {
        var img = MakeGray(2, 2, 128);
        var log = new List<int>();

        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => { log.Add(1); return i.Clone(); },
            i => { log.Add(2); return i.Clone(); },
            i => { log.Add(3); return i.Clone(); },
        });

        Assert.Equal(new[] { 1, 2, 3 }, log);
        Assert.Equal(128, result.Pixels[0]);
    }

    [Fact]
    public void Pipeline_NullSteps_Throws()
    {
        var img = MakeGray(2, 2, 10);
        Assert.Throws<ArgumentNullException>(() =>
            img.Pipeline(null!));
    }

    [Fact]
    public void Pipeline_NullStepInSequence_Throws()
    {
        var img = MakeGray(2, 2, 10);
        Assert.ThrowsAny<ArgumentNullException>(() =>
            img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
            {
                i => i.Clone(),
                null!,
                i => i.Clone(),
            }));
    }

    [Fact]
    public void Pipeline_ResultIsIndependentFromSource()
    {
        var img = MakeGray(2, 2, 77);
        var result = img.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            i => i.Clone()
        });
        result.Pixels[0] = 0;
        Assert.NotEqual(0, img.Pixels[0]);
    }

    // -------------------------------------------------------------------------
    // Create
    // -------------------------------------------------------------------------

    [Fact]
    public void Create_PgmFill_AllPixelsHaveCorrectValue()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5, fill: 200);
        Assert.All(img.Pixels, p => Assert.Equal(200, p));
    }

    [Fact]
    public void Create_PgmFill_DimensionsCorrect()
    {
        var img = NetpbmImage.Create(4, 2, NetpbmFormat.PGM_P5);
        Assert.Equal(4, img.Width);
        Assert.Equal(2, img.Height);
        Assert.Equal(8, img.Pixels.Length);
    }

    [Fact]
    public void Create_PpmFill_AllChannelsFilled()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P3, fill: 128);
        Assert.All(img.RedChannel!, p => Assert.Equal(128, p));
        Assert.All(img.GreenChannel!, p => Assert.Equal(128, p));
        Assert.All(img.BlueChannel!, p => Assert.Equal(128, p));
    }

    [Fact]
    public void Create_WidthZero_Throws()
    {
        Assert.ThrowsAny<Exception>(() =>
            NetpbmImage.Create(0, 4, NetpbmFormat.PGM_P5));
    }

    [Fact]
    public void Create_HeightZero_Throws()
    {
        Assert.ThrowsAny<Exception>(() =>
            NetpbmImage.Create(4, 0, NetpbmFormat.PGM_P5));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create then Pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateThenPipeline_Composition()
    {
        // Create blank 4x4 PGM, then apply Clone + ConvertFormat via Pipeline
        var canvas = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, fill: 0);

        var result = canvas.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => img.ConvertFormat(NetpbmFormat.PGM_P2),
            img => img.Clone(),
        });

        Assert.Equal(4, result.Width);
        Assert.Equal(4, result.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, result.Format);
        Assert.All(result.Pixels, p => Assert.Equal(0, p));
    }
}
