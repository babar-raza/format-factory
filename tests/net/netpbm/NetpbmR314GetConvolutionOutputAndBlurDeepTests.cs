// Tests for NetpbmImage.GetConvolutionOutput, GetBlurredImage, GetSharpenedImage deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R314

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R314: Tests for NetpbmImage.GetConvolutionOutput, GetBlurredImage, GetSharpenedImage deeper.
/// GetConvolutionOutput(kernel): applies the given convolution kernel and returns a new image.
/// GetBlurredImage(radius): returns a new image blurred with a Gaussian kernel of given radius.
/// GetSharpenedImage(strength): returns a new image with unsharp masking applied.
/// Covers: GetConvolutionOutput no-throw; GetConvolutionOutput same dims; GetConvolutionOutput consistent;
/// GetConvolutionOutput identity kernel preserves mean; GetConvolutionOutput save-load;
/// GetBlurredImage no-throw; GetBlurredImage same dims; GetBlurredImage consistent;
/// GetBlurredImage reduces edge strength vs original; GetBlurredImage save-load;
/// GetSharpenedImage no-throw; GetSharpenedImage same dims; GetSharpenedImage consistent;
/// GetSharpenedImage save-load;
/// dogfood CreateImage→GetConvolutionOutput→GetBlurredImage→GetSharpenedImage→SaveToFile pipeline.
/// </summary>
public class NetpbmR314GetConvolutionOutputAndBlurDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR314GetConvolutionOutputAndBlurDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR314_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateSharpEdgePgm()
    {
        var path = TempFile("sharp_edge.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = c < 6 ? (byte)20 : (byte)230;
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    // Identity kernel: [[0,0,0],[0,1,0],[0,0,0]]
    private static double[][] IdentityKernel => new[]
    {
        new double[] { 0, 0, 0 },
        new double[] { 0, 1, 0 },
        new double[] { 0, 0, 0 }
    };

    // -------------------------------------------------------------------------
    // GetConvolutionOutput
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConvolutionOutput_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetConvolutionOutput(IdentityKernel));
        Assert.Null(ex);
    }

    [Fact]
    public void GetConvolutionOutput_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var conv = img.GetConvolutionOutput(IdentityKernel);
        Assert.Equal(img.Width, conv.Width);
        Assert.Equal(img.Height, conv.Height);
    }

    [Fact]
    public void GetConvolutionOutput_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var c1 = img.GetConvolutionOutput(IdentityKernel);
        var c2 = img.GetConvolutionOutput(IdentityKernel);
        Assert.Equal(c1.GetMeanPixelValue(), c2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetConvolutionOutput_Identity_PreservesMean()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var conv = img.GetConvolutionOutput(IdentityKernel);
        // Identity kernel should preserve mean pixel value
        Assert.Equal(img.GetMeanPixelValue(), conv.GetMeanPixelValue(), precision: 1);
    }

    [Fact]
    public void GetConvolutionOutput_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var conv = img.GetConvolutionOutput(IdentityKernel);
        var path = TempFile("conv_save.pgm");
        conv.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(conv.Width, loaded.Width);
        Assert.Equal(conv.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetBlurredImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlurredImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetBlurredImage(1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlurredImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var blurred = img.GetBlurredImage(1);
        Assert.Equal(img.Width, blurred.Width);
        Assert.Equal(img.Height, blurred.Height);
    }

    [Fact]
    public void GetBlurredImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var b1 = img.GetBlurredImage(1);
        var b2 = img.GetBlurredImage(1);
        Assert.Equal(b1.GetMeanPixelValue(), b2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetBlurredImage_ReducesEdgeStrength()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var blurred = img.GetBlurredImage(2);
        // Blurring reduces gradient magnitude (edge strength)
        Assert.True(blurred.GetEdgeStrength() <= img.GetEdgeStrength() + 1.0);
    }

    [Fact]
    public void GetBlurredImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var blurred = img.GetBlurredImage(1);
        var path = TempFile("blur_save.pgm");
        blurred.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(blurred.Width, loaded.Width);
        Assert.Equal(blurred.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetSharpenedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpenedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetSharpenedImage(1.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSharpenedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var sharpened = img.GetSharpenedImage(1.0);
        Assert.Equal(img.Width, sharpened.Width);
        Assert.Equal(img.Height, sharpened.Height);
    }

    [Fact]
    public void GetSharpenedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var s1 = img.GetSharpenedImage(1.0);
        var s2 = img.GetSharpenedImage(1.0);
        Assert.Equal(s1.GetMeanPixelValue(), s2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetSharpenedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var sharpened = img.GetSharpenedImage(0.5);
        var path = TempFile("sharp_save.pgm");
        sharpened.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(sharpened.Width, loaded.Width);
        Assert.Equal(sharpened.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetConvolutionOutput_GetBlurredImage_GetSharpenedImage_SaveToFile_Pipeline()
    {
        // Satellite image enhancement — multispectral land use classification pre-processing
        var path = TempFile("dogfood_satellite.pgm");
        var pixels = new byte[12 * 10];
        // Simulate land use zones: urban (high), vegetation (medium), water (low), clouds (very high)
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
            {
                bool isUrban = r < 3 && c < 5;
                bool isVegetation = r >= 3 && r < 7 && c >= 2 && c < 9;
                bool isWater = r >= 7 && c < 4;
                bool isCloud = r < 2 && c >= 9;
                pixels[r * 12 + c] = isCloud ? (byte)250
                    : isUrban ? (byte)(150 + c * 8)
                    : isVegetation ? (byte)(80 + r * 5 + c * 3)
                    : isWater ? (byte)(30 + c * 5)
                    : (byte)(100 + r * 4 + c * 2);
            }
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(255, img.MaxVal);

        var origMean = img.GetMeanPixelValue();
        Assert.True(origMean > 0.0);

        // GetConvolutionOutput with identity kernel
        var conv = img.GetConvolutionOutput(IdentityKernel);
        Assert.Equal(12, conv.Width);
        Assert.Equal(10, conv.Height);
        Assert.Equal(conv.GetMeanPixelValue(), img.GetConvolutionOutput(IdentityKernel).GetMeanPixelValue(), precision: 4); // consistent
        // Identity preserves mean approximately
        Assert.True(Math.Abs(conv.GetMeanPixelValue() - origMean) < 5.0);

        // GetConvolutionOutput save/load
        var convPath = TempFile("dogfood_satellite_conv.pgm");
        conv.SaveToFile(convPath);
        Assert.True(File.Exists(convPath));
        var loadedConv = NetpbmImage.LoadFile(convPath);
        Assert.Equal(12, loadedConv.Width);

        // GetBlurredImage — atmospheric haze simulation
        var blurred = img.GetBlurredImage(1);
        Assert.Equal(12, blurred.Width);
        Assert.Equal(10, blurred.Height);
        Assert.Equal(blurred.GetMeanPixelValue(), img.GetBlurredImage(1).GetMeanPixelValue(), precision: 4); // consistent
        // Blur reduces edge sharpness
        Assert.True(blurred.GetEdgeStrength() <= img.GetEdgeStrength() + 5.0);

        // Stronger blur
        var blurred2 = img.GetBlurredImage(2);
        Assert.Equal(12, blurred2.Width);
        Assert.True(blurred2.GetMeanPixelValue() > 0.0);

        // GetSharpenedImage — detail enhancement for classification
        var sharpened = img.GetSharpenedImage(0.8);
        Assert.Equal(12, sharpened.Width);
        Assert.Equal(10, sharpened.Height);
        Assert.Equal(sharpened.GetMeanPixelValue(), img.GetSharpenedImage(0.8).GetMeanPixelValue(), precision: 4); // consistent

        // Higher strength sharpening
        var superSharp = img.GetSharpenedImage(2.0);
        Assert.Equal(12, superSharp.Width);

        // Chain: blur → sharpen → save
        var enhanced = img.GetBlurredImage(1).GetSharpenedImage(1.5);
        Assert.Equal(12, enhanced.Width);
        Assert.Equal(10, enhanced.Height);

        // SaveToFile — blurred
        var out1 = TempFile("dogfood_satellite_blur.pgm");
        blurred.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loadedBlur = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loadedBlur.Width);
        Assert.Equal(blurred.GetMeanPixelValue(), loadedBlur.GetMeanPixelValue(), precision: 2);

        // SaveToFile — sharpened
        var out2 = TempFile("dogfood_satellite_sharp.pgm");
        sharpened.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loadedSharp = NetpbmImage.LoadFile(out2);
        Assert.Equal(12, loadedSharp.Width);
        Assert.Equal(sharpened.GetMeanPixelValue(), loadedSharp.GetMeanPixelValue(), precision: 2);

        // SaveToFile — enhanced chain
        var out3 = TempFile("dogfood_satellite_enhanced.pgm");
        enhanced.SaveToFile(out3);
        Assert.True(File.Exists(out3));
        var loadedEnhanced = NetpbmImage.LoadFile(out3);
        Assert.Equal(enhanced.Width, loadedEnhanced.Width);

        // Final chained pipeline: conv → blur → sharpen
        var pipeline = img.GetConvolutionOutput(IdentityKernel).GetBlurredImage(1).GetSharpenedImage(1.0);
        Assert.Equal(12, pipeline.Width);
        Assert.Equal(10, pipeline.Height);
        var ex1 = Record.Exception(() => pipeline.SaveToFile(TempFile("dogfood_pipeline.pgm")));
        Assert.Null(ex1);
    }
}
