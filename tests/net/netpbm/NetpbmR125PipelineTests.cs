// Tests for NetpbmImage.Pipeline(steps) — sequential image transformation API.
// Sprint: FORMAT-FACTORY-NETPBM-PIPELINE-20260626
// Ledger: R125-GOVERNED-DOTNET-NETPBM-PIPELINE-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R125: Pipeline(IEnumerable{Func{NetpbmImage, NetpbmImage}} steps) — applies
/// each step function to the image produced by the previous step. Returns the
/// final image. Null steps or null step functions throw ArgumentNullException.
/// Tests verify sequential application, dimension/format propagation, empty pipeline,
/// null guards, and multi-step dogfood pipelines.
/// </summary>
public class NetpbmR125PipelineTests
{
    private static NetpbmDocument LoadPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- Empty pipeline returns the original image ----

    [Fact]
    public void Pipeline_EmptySteps_ReturnsSameImage()
    {
        const string pgm = "P2\n3 3\n255\n10 20 30\n40 50 60\n70 80 90\n";
        var doc = LoadPgm(pgm);

        var result = doc.Image.Pipeline(Array.Empty<Func<NetpbmImage, NetpbmImage>>());
        var resultDoc = NetpbmDocument.FromImage(result);

        Assert.Equal(doc.Width, resultDoc.Width);
        Assert.Equal(doc.Height, resultDoc.Height);
    }

    // ---- Single-step pipeline applies the step ----

    [Fact]
    public void Pipeline_SingleStep_AppliesStep()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        // Single step: fill all pixels to 100 via Clone + FillRegion
        var result = doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => { var c = img.Clone(); c.FillRegion(0, 0, 2, 2, 100); return c; }
        });

        var resultDoc = NetpbmDocument.FromImage(result);
        Assert.Equal(100, resultDoc.GetPixel(0, 0));
        Assert.Equal(100, resultDoc.GetPixel(1, 1));
    }

    // ---- Multi-step pipeline: steps applied in order ----

    [Fact]
    public void Pipeline_MultiStep_StepsAppliedInOrder()
    {
        const string pgm = "P2\n4 4\n255\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";
        var doc = LoadPgm(pgm);

        // Step 1: fill to 50; Step 2: adjust brightness by +50 → expect ~100
        var result = doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => { var c = img.Clone(); c.FillRegion(0, 0, 4, 4, 50); return c; },
            img => img.AdjustBrightness(50)
        });

        var resultDoc = NetpbmDocument.FromImage(result);
        // All pixels should be approximately 100 (50 + 50)
        Assert.True(resultDoc.GetPixel(0, 0) >= 90, "Pixel should be near 100 after two steps");
    }

    // ---- Pipeline preserves final image dimensions ----

    [Fact]
    public void Pipeline_DimensionsPreservedByNonResizingSteps()
    {
        const string pgm = "P2\n5 3\n255\n100 100 100 100 100\n100 100 100 100 100\n100 100 100 100 100\n";
        var doc = LoadPgm(pgm);

        var result = doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => img.AdjustBrightness(-20),
            img => img.AdjustBrightness(10)
        });

        Assert.Equal(doc.Width, result.Width);
        Assert.Equal(doc.Height, result.Height);
    }

    // ---- Null steps collection throws ----

    [Fact]
    public void Pipeline_NullSteps_ThrowsArgumentNullException()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<ArgumentNullException>(() =>
            doc.Image.Pipeline(null!));
    }

    // ---- Null step function in collection throws ----

    [Fact]
    public void Pipeline_NullStepFunction_ThrowsArgumentNullException()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        Assert.Throws<ArgumentNullException>(() =>
            doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>?[]
            {
                img => img.Clone(),
                null!
            }));
    }

    // ---- Pipeline on PPM applies format-aware steps ----

    [Fact]
    public void Pipeline_PpmToGrayscaleStep_ResultIsGrayscale()
    {
        const string ppm = "P3\n2 2\n255\n100 150 200  100 150 200\n100 150 200  100 150 200\n";
        var doc = LoadPpm(ppm);

        var result = doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => img.ToGrayscale()
        });

        var resultDoc = NetpbmDocument.FromImage(result);
        Assert.True(resultDoc.IsGrayscale);
    }

    // ---- Dogfood: three-step pipeline with Clone + FillRegion + AdjustBrightness ----

    [Fact]
    public void DogfoodPipeline_ThreeSteps_PixelCountInvariant()
    {
        const string pgm = "P2\n4 4\n255\n50 50 50 50\n50 50 50 50\n50 50 50 50\n50 50 50 50\n";
        var doc = LoadPgm(pgm);

        var result = doc.Image.Pipeline(new Func<NetpbmImage, NetpbmImage>[]
        {
            img => img.Clone(),
            img => img.AdjustBrightness(30),
            img => img.AdjustBrightness(-10)
        });

        // Pixel count invariant
        Assert.Equal(doc.PixelCount, result.Width * result.Height);

        // Brightness net +20: 50 + 20 = 70
        var resultDoc = NetpbmDocument.FromImage(result);
        var pixel = resultDoc.GetPixel(0, 0);
        Assert.True(pixel >= 60 && pixel <= 80, $"Expected pixel ~70, got {pixel}");
    }
}
