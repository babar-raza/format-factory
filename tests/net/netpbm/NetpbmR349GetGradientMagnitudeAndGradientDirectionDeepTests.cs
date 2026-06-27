// Tests for NetpbmImage.GetGradientMagnitude, GetGradientDirection deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R349

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R349: Tests for NetpbmImage.GetGradientMagnitude, GetGradientDirection deeper.
/// GetGradientMagnitude(): returns mean gradient magnitude across the image (Sobel/Prewitt).
/// GetGradientDirection(): returns mean gradient direction in radians across the image.
/// Covers: GetGradientMagnitude no-throw; GetGradientMagnitude non-negative;
/// GetGradientMagnitude consistent; GetGradientMagnitude zero for uniform;
/// GetGradientMagnitude save-load;
/// GetGradientDirection no-throw; GetGradientDirection finite; GetGradientDirection consistent;
/// GetGradientDirection save-load;
/// dogfood CreateImage→GetGradientMagnitude→GetGradientDirection pipeline.
/// </summary>
public class NetpbmR349GetGradientMagnitudeAndGradientDirectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR349GetGradientMagnitudeAndGradientDirectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR349_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateEdgeImage()
    {
        // PGM 80x80 — strong vertical edge in the middle
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                pixels[y * w + x] = x < w / 2 ? (byte)30 : (byte)220;
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateUniformImage()
    {
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        Array.Fill(pixels, (byte)128);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    private static NetpbmImage CreateTextureImage()
    {
        // PGM 80x80 — noise texture with many edges
        int w = 80, h = 80;
        var pixels = new byte[h * w];
        var rng = new Random(20241201);
        for (int i = 0; i < pixels.Length; i++)
            pixels[i] = (byte)rng.Next(256);
        return NetpbmImage.FromGrayscalePixels(pixels, w, h, 255);
    }

    // -------------------------------------------------------------------------
    // GetGradientMagnitude
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGradientMagnitude_NoThrow()
    {
        var img = CreateEdgeImage();
        var ex = Record.Exception(() => img.GetGradientMagnitude());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGradientMagnitude_NonNegative()
    {
        var img = CreateEdgeImage();
        Assert.True(img.GetGradientMagnitude() >= 0.0);
    }

    [Fact]
    public void GetGradientMagnitude_Consistent()
    {
        var img = CreateEdgeImage();
        Assert.Equal(img.GetGradientMagnitude(), img.GetGradientMagnitude());
    }

    [Fact]
    public void GetGradientMagnitude_Zero_ForUniform()
    {
        var img = CreateUniformImage();
        Assert.Equal(0.0, img.GetGradientMagnitude(), precision: 4);
    }

    [Fact]
    public void GetGradientMagnitude_SaveLoad_Consistent()
    {
        var img = CreateEdgeImage();
        var before = img.GetGradientMagnitude();
        var path = TempFile("gm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGradientMagnitude(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetGradientDirection
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGradientDirection_NoThrow()
    {
        var img = CreateEdgeImage();
        var ex = Record.Exception(() => img.GetGradientDirection());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGradientDirection_Finite()
    {
        var img = CreateEdgeImage();
        Assert.True(double.IsFinite(img.GetGradientDirection()));
    }

    [Fact]
    public void GetGradientDirection_Consistent()
    {
        var img = CreateEdgeImage();
        Assert.Equal(img.GetGradientDirection(), img.GetGradientDirection());
    }

    [Fact]
    public void GetGradientDirection_SaveLoad_Consistent()
    {
        var img = CreateEdgeImage();
        var before = img.GetGradientDirection();
        var path = TempFile("gd_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetGradientDirection(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetGradientMagnitude_GetGradientDirection_Pipeline()
    {
        // Medical imaging — chest X-ray quality control: gradient-based sharpness and orientation analysis
        // Used in DICOM ingestion pipeline for automatic quality flag before radiologist reading
        var rng = new Random(20241210);

        // Sharp chest X-ray simulation — high gradient at lung/soft tissue boundaries
        int w = 120, h = 120;
        var sharpPixels = new byte[h * w];
        Array.Fill(sharpPixels, (byte)80); // background air
        // Lung fields (left and right)
        for (int y = 20; y < 100; y++)
            for (int x = 10; x < 55; x++) // left lung
                sharpPixels[y * w + x] = (byte)(30 + rng.Next(15)); // dark lung
        for (int y = 20; y < 100; y++)
            for (int x = 65; x < 110; x++) // right lung
                sharpPixels[y * w + x] = (byte)(30 + rng.Next(15));
        // Mediastinum (bright)
        for (int y = 15; y < 105; y++)
            for (int x = 55; x < 65; x++)
                sharpPixels[y * w + x] = (byte)(180 + rng.Next(40));
        // Diaphragm line (horizontal edge)
        for (int x = 10; x < 110; x++)
        {
            sharpPixels[100 * w + x] = (byte)(200 + rng.Next(30));
            sharpPixels[99 * w + x] = (byte)(160 + rng.Next(20));
        }
        var sharpImg = NetpbmImage.FromGrayscalePixels(sharpPixels, w, h, 255);

        // Blurred chest X-ray simulation — reduced gradient (motion artefact)
        var blurredPixels = new byte[h * w];
        Array.Copy(sharpPixels, blurredPixels, sharpPixels.Length);
        // Simple box blur
        var tempPixels = new byte[h * w];
        for (int y = 1; y < h - 1; y++)
            for (int x = 1; x < w - 1; x++)
            {
                int sum = 0;
                for (int dy = -2; dy <= 2; dy++)
                    for (int dx = -2; dx <= 2; dx++)
                    {
                        int ny = Math.Clamp(y + dy, 0, h - 1);
                        int nx = Math.Clamp(x + dx, 0, w - 1);
                        sum += blurredPixels[ny * w + nx];
                    }
                tempPixels[y * w + x] = (byte)(sum / 25);
            }
        var blurredImg = NetpbmImage.FromGrayscalePixels(tempPixels, w, h, 255);

        // Uniform image (failed acquisition)
        var uniformPixels = new byte[h * w];
        Array.Fill(uniformPixels, (byte)90);
        var uniformImg = NetpbmImage.FromGrayscalePixels(uniformPixels, w, h, 255);

        // GetGradientMagnitude
        var gmSharp = sharpImg.GetGradientMagnitude();
        Assert.True(gmSharp >= 0.0);
        Assert.Equal(gmSharp, sharpImg.GetGradientMagnitude()); // consistent

        var gmBlurred = blurredImg.GetGradientMagnitude();
        Assert.True(gmBlurred >= 0.0);
        Assert.Equal(gmBlurred, blurredImg.GetGradientMagnitude()); // consistent

        var gmUniform = uniformImg.GetGradientMagnitude();
        Assert.Equal(0.0, gmUniform, precision: 4);

        // Sharp image should have higher gradient than blurred
        Assert.True(gmSharp >= gmBlurred);

        // GetGradientDirection
        var gdSharp = sharpImg.GetGradientDirection();
        Assert.True(double.IsFinite(gdSharp));
        Assert.Equal(gdSharp, sharpImg.GetGradientDirection()); // consistent

        var gdBlurred = blurredImg.GetGradientDirection();
        Assert.True(double.IsFinite(gdBlurred));

        // Basic image properties
        Assert.Equal(w, sharpImg.Width);
        Assert.Equal(h, sharpImg.Height);
        Assert.True(sharpImg.GetMeanIntensity() >= 0.0);
        Assert.True(sharpImg.GetMeanIntensity() <= 255.0);

        // SaveToFile
        var pathSharp = TempFile("cxr_sharp.pgm");
        sharpImg.SaveToFile(pathSharp);
        Assert.True(File.Exists(pathSharp));
        Assert.True(new FileInfo(pathSharp).Length > 0);

        var pathBlurred = TempFile("cxr_blurred.pgm");
        blurredImg.SaveToFile(pathBlurred);
        Assert.True(File.Exists(pathBlurred));

        // LoadFile and verify
        var loadedSharp = NetpbmImage.LoadFile(pathSharp);
        Assert.Equal(w, loadedSharp.Width);
        Assert.Equal(h, loadedSharp.Height);
        Assert.Equal(gmSharp, loadedSharp.GetGradientMagnitude(), precision: 4);
        Assert.Equal(gdSharp, loadedSharp.GetGradientDirection(), precision: 4);

        var loadedBlurred = NetpbmImage.LoadFile(pathBlurred);
        Assert.Equal(gmBlurred, loadedBlurred.GetGradientMagnitude(), precision: 4);

        // Additional operations
        var ex1 = Record.Exception(() => sharpImg.GetStandardDeviation());
        var ex2 = Record.Exception(() => blurredImg.GetEntropy());
        var ex3 = Record.Exception(() => uniformImg.GetHistogram());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
