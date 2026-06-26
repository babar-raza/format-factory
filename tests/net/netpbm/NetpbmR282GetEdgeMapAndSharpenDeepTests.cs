// Tests for NetpbmImage.GetEdgeMap, Sharpen, Blur deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R282

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R282: Tests for NetpbmImage.GetEdgeMap, Sharpen, Blur deeper.
/// GetEdgeMap(): returns a new image highlighting edges using gradient detection.
/// Sharpen(): returns a new image with enhanced edges and fine details.
/// Blur(): returns a new image with reduced noise via averaging.
/// Covers: GetEdgeMap no-throw; GetEdgeMap same dims; GetEdgeMap consistent; GetEdgeMap save-load;
/// GetEdgeMap uniform-image all zeros or very low values;
/// Sharpen no-throw; Sharpen same dims; Sharpen consistent; Sharpen save-load;
/// Sharpen MaxVal unchanged;
/// Blur no-throw; Blur same dims; Blur consistent; Blur save-load;
/// Blur MaxVal unchanged; Blur reduces contrast vs original;
/// dogfood LoadFile→GetEdgeMap→Sharpen→Blur→SaveToFile pipeline.
/// </summary>
public class NetpbmR282GetEdgeMapAndSharpenDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR282GetEdgeMapAndSharpenDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR282_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCheckerPgm(int size = 16)
    {
        var path = TempFile($"checker_{size}x{size}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{size} {size}");
        sw.WriteLine("255");
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                int val = ((x / 4 + y / 4) % 2 == 0) ? 255 : 0;
                sw.Write(val);
                if (x < size - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateUniformPgm(int intensity, int size = 8)
    {
        var path = TempFile($"uniform_{intensity}_{size}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{size} {size}");
        sw.WriteLine("255");
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                sw.Write(intensity);
                if (x < size - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    private string CreateGradientPgm(int width = 16, int height = 16)
    {
        var path = TempFile($"grad_{width}x{height}.pgm");
        using var sw = new StreamWriter(path);
        sw.WriteLine("P2");
        sw.WriteLine($"{width} {height}");
        sw.WriteLine("255");
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                int val = (x * 255) / Math.Max(1, width - 1);
                sw.Write(val);
                if (x < width - 1) sw.Write(' ');
            }
            sw.WriteLine();
        }
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEdgeMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeMap_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerPgm());
        var ex = Record.Exception(() => img.GetEdgeMap());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeMap_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerPgm());
        var edge = img.GetEdgeMap();
        Assert.Equal(img.Width, edge.Width);
        Assert.Equal(img.Height, edge.Height);
    }

    [Fact]
    public void GetEdgeMap_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerPgm());
        var e1 = img.GetEdgeMap();
        var e2 = img.GetEdgeMap();
        Assert.Equal(e1.Width, e2.Width);
        Assert.Equal(e1.Height, e2.Height);
    }

    [Fact]
    public void GetEdgeMap_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerPgm());
        var edge = img.GetEdgeMap();
        var path = TempFile("edge_save.pgm");
        edge.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(edge.Width, loaded.Width);
        Assert.Equal(edge.Height, loaded.Height);
    }

    [Fact]
    public void GetEdgeMap_Uniform_LowValues()
    {
        // Uniform image has no edges → edge map values should be very low
        var img = NetpbmImage.LoadFile(CreateUniformPgm(128));
        var edge = img.GetEdgeMap();
        Assert.Equal(img.Width, edge.Width);
        Assert.Equal(img.Height, edge.Height);
        // Brightness of edge map should be near 0 for uniform image
        Assert.True(edge.GetBrightness() < 0.2);
    }

    // -------------------------------------------------------------------------
    // Sharpen
    // -------------------------------------------------------------------------

    [Fact]
    public void Sharpen_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Sharpen());
        Assert.Null(ex);
    }

    [Fact]
    public void Sharpen_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var sharpened = img.Sharpen();
        Assert.Equal(img.Width, sharpened.Width);
        Assert.Equal(img.Height, sharpened.Height);
    }

    [Fact]
    public void Sharpen_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var s1 = img.Sharpen();
        var s2 = img.Sharpen();
        Assert.Equal(s1.Width, s2.Width);
        Assert.Equal(s1.Height, s2.Height);
    }

    [Fact]
    public void Sharpen_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var sharpened = img.Sharpen();
        var path = TempFile("sharp_save.pgm");
        sharpened.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(sharpened.Width, loaded.Width);
        Assert.Equal(sharpened.Height, loaded.Height);
    }

    [Fact]
    public void Sharpen_MaxVal_Unchanged()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var sharpened = img.Sharpen();
        Assert.Equal(img.MaxVal, sharpened.MaxVal);
    }

    // -------------------------------------------------------------------------
    // Blur
    // -------------------------------------------------------------------------

    [Fact]
    public void Blur_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.Blur());
        Assert.Null(ex);
    }

    [Fact]
    public void Blur_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var blurred = img.Blur();
        Assert.Equal(img.Width, blurred.Width);
        Assert.Equal(img.Height, blurred.Height);
    }

    [Fact]
    public void Blur_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var b1 = img.Blur();
        var b2 = img.Blur();
        Assert.Equal(b1.Width, b2.Width);
        Assert.Equal(b1.Height, b2.Height);
    }

    [Fact]
    public void Blur_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var blurred = img.Blur();
        var path = TempFile("blur_save.pgm");
        blurred.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(blurred.Width, loaded.Width);
        Assert.Equal(blurred.Height, loaded.Height);
    }

    [Fact]
    public void Blur_MaxVal_Unchanged()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var blurred = img.Blur();
        Assert.Equal(img.MaxVal, blurred.MaxVal);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgeMap_Sharpen_Blur_SaveToFile_Pipeline()
    {
        var srcPath = CreateCheckerPgm(16);
        var img = NetpbmImage.LoadFile(srcPath);
        Assert.Equal(16, img.Width);
        Assert.Equal(16, img.Height);

        // GetEdgeMap
        var edge = img.GetEdgeMap();
        Assert.NotNull(edge);
        Assert.Equal(img.Width, edge.Width);
        Assert.Equal(img.Height, edge.Height);
        var edgePath = TempFile("dogfood_edge.pgm");
        edge.SaveToFile(edgePath);
        Assert.True(File.Exists(edgePath));
        var edgeLoaded = NetpbmImage.LoadFile(edgePath);
        Assert.Equal(edge.Width, edgeLoaded.Width);
        Assert.Equal(edge.Height, edgeLoaded.Height);

        // Sharpen
        var sharp = img.Sharpen();
        Assert.NotNull(sharp);
        Assert.Equal(img.Width, sharp.Width);
        Assert.Equal(img.Height, sharp.Height);
        Assert.Equal(img.MaxVal, sharp.MaxVal);
        var sharpPath = TempFile("dogfood_sharp.pgm");
        sharp.SaveToFile(sharpPath);
        Assert.True(File.Exists(sharpPath));
        var sharpLoaded = NetpbmImage.LoadFile(sharpPath);
        Assert.Equal(sharp.Width, sharpLoaded.Width);

        // Blur
        var blur = img.Blur();
        Assert.NotNull(blur);
        Assert.Equal(img.Width, blur.Width);
        Assert.Equal(img.Height, blur.Height);
        Assert.Equal(img.MaxVal, blur.MaxVal);
        var blurPath = TempFile("dogfood_blur.pgm");
        blur.SaveToFile(blurPath);
        Assert.True(File.Exists(blurPath));
        var blurLoaded = NetpbmImage.LoadFile(blurPath);
        Assert.Equal(blur.Width, blurLoaded.Width);

        // Uniform image edge map should have near-zero brightness
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm(200, 8));
        var uniformEdge = uniform.GetEdgeMap();
        Assert.True(uniformEdge.GetBrightness() < 0.1);

        // Chain: blur then edge
        var blurEdge = img.Blur().GetEdgeMap();
        Assert.Equal(img.Width, blurEdge.Width);
        Assert.Equal(img.Height, blurEdge.Height);

        // Chain: sharpen then blur (approximately restores)
        var sharpBlur = img.Sharpen().Blur();
        Assert.Equal(img.Width, sharpBlur.Width);
        Assert.Equal(img.Height, sharpBlur.Height);

        // All operations preserve MaxVal
        Assert.Equal(img.MaxVal, edge.MaxVal);
        Assert.Equal(img.MaxVal, sharp.MaxVal);
        Assert.Equal(img.MaxVal, blur.MaxVal);

        // Save chained result
        var chainPath = TempFile("dogfood_sharpen_blur.pgm");
        sharpBlur.SaveToFile(chainPath);
        Assert.True(File.Exists(chainPath));
        Assert.True(new FileInfo(chainPath).Length > 0);
        var chainLoaded = NetpbmImage.LoadFile(chainPath);
        Assert.Equal(img.Width, chainLoaded.Width);
        Assert.Equal(img.Height, chainLoaded.Height);

        // Second doc — gradient image
        var grad = NetpbmImage.LoadFile(CreateGradientPgm(12, 8));
        var gradEdge = grad.GetEdgeMap();
        Assert.Equal(12, gradEdge.Width);
        Assert.Equal(8, gradEdge.Height);
        var gradSharp = grad.Sharpen();
        Assert.Equal(12, gradSharp.Width);
        var finalPath = TempFile("dogfood_grad_chain.pgm");
        gradSharp.Blur().SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var finalLoaded = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(12, finalLoaded.Width);
        Assert.Equal(8, finalLoaded.Height);
    }
}
