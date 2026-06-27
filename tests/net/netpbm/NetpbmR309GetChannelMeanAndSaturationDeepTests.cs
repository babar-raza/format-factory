// Tests for NetpbmImage.GetChannelMean, GetSaturationScore, GetHueMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R309

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R309: Tests for NetpbmImage.GetChannelMean, GetSaturationScore, GetHueMean deeper.
/// GetChannelMean(channel): returns the mean value of the specified colour channel (0=R,1=G,2=B).
/// GetSaturationScore(): returns the mean HSV saturation [0,1] across all pixels.
/// GetHueMean(): returns the circular mean hue [0,360] of the image.
/// Covers: GetChannelMean no-throw; GetChannelMean in range; GetChannelMean consistent;
/// GetChannelMean red channel for red image; GetChannelMean save-load;
/// GetSaturationScore no-throw; GetSaturationScore in range; GetSaturationScore consistent;
/// GetSaturationScore zero for greyscale; GetSaturationScore save-load;
/// GetHueMean no-throw; GetHueMean in range; GetHueMean consistent; GetHueMean save-load;
/// dogfood CreateImage→GetChannelMean→GetSaturationScore→GetHueMean→SaveToFile pipeline.
/// </summary>
public class NetpbmR309GetChannelMeanAndSaturationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR309GetChannelMeanAndSaturationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR309_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePurePpmRed()
    {
        // 8×8 pure red PPM
        var path = TempFile("red.ppm");
        var pixels = new byte[8 * 8 * 3];
        for (int i = 0; i < 8 * 8; i++) { pixels[i * 3] = 255; pixels[i * 3 + 1] = 0; pixels[i * 3 + 2] = 0; }
        var header = System.Text.Encoding.ASCII.GetBytes("P6\n8 8\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreatePurePpmGreen()
    {
        var path = TempFile("green.ppm");
        var pixels = new byte[8 * 8 * 3];
        for (int i = 0; i < 8 * 8; i++) { pixels[i * 3] = 0; pixels[i * 3 + 1] = 255; pixels[i * 3 + 2] = 0; }
        var header = System.Text.Encoding.ASCII.GetBytes("P6\n8 8\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateGreyscalePpm()
    {
        // 8×8 grey PPM (R=G=B=128 → saturation=0)
        var path = TempFile("grey.ppm");
        var pixels = new byte[8 * 8 * 3];
        Array.Fill(pixels, (byte)128);
        var header = System.Text.Encoding.ASCII.GetBytes("P6\n8 8\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateColorfulPpm()
    {
        // 12×10 colorful image with varied hues
        var path = TempFile("colorful.ppm");
        var pixels = new byte[12 * 10 * 3];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
            {
                int idx = (r * 12 + c) * 3;
                pixels[idx]     = (byte)((c * 20 + r * 10) % 256);
                pixels[idx + 1] = (byte)((r * 25 + c * 8)  % 256);
                pixels[idx + 2] = (byte)((c * 15 + r * 18) % 256);
            }
        var header = System.Text.Encoding.ASCII.GetBytes("P6\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetChannelMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelMean_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var ex = Record.Exception(() => img.GetChannelMean(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelMean_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        for (int ch = 0; ch < 3; ch++)
        {
            var mean = img.GetChannelMean(ch);
            Assert.True(mean >= 0.0);
            Assert.True(mean <= img.MaxVal);
        }
    }

    [Fact]
    public void GetChannelMean_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        Assert.Equal(img.GetChannelMean(0), img.GetChannelMean(0));
        Assert.Equal(img.GetChannelMean(1), img.GetChannelMean(1));
        Assert.Equal(img.GetChannelMean(2), img.GetChannelMean(2));
    }

    [Fact]
    public void GetChannelMean_RedChannel_ForRedImage()
    {
        var img = NetpbmImage.LoadFile(CreatePurePpmRed());
        Assert.Equal(255.0, img.GetChannelMean(0), precision: 2); // R=255
        Assert.Equal(0.0,   img.GetChannelMean(1), precision: 2); // G=0
        Assert.Equal(0.0,   img.GetChannelMean(2), precision: 2); // B=0
    }

    [Fact]
    public void GetChannelMean_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var before0 = img.GetChannelMean(0);
        var path = TempFile("cm_save.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before0, loaded.GetChannelMean(0), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetSaturationScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSaturationScore_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var ex = Record.Exception(() => img.GetSaturationScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSaturationScore_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var sat = img.GetSaturationScore();
        Assert.True(sat >= 0.0);
        Assert.True(sat <= 1.0);
    }

    [Fact]
    public void GetSaturationScore_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        Assert.Equal(img.GetSaturationScore(), img.GetSaturationScore());
    }

    [Fact]
    public void GetSaturationScore_Zero_ForGreyscale()
    {
        var img = NetpbmImage.LoadFile(CreateGreyscalePpm());
        Assert.Equal(0.0, img.GetSaturationScore(), precision: 4);
    }

    [Fact]
    public void GetSaturationScore_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var before = img.GetSaturationScore();
        var path = TempFile("sat_save.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSaturationScore(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetHueMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHueMean_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var ex = Record.Exception(() => img.GetHueMean());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHueMean_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var hue = img.GetHueMean();
        Assert.True(hue >= 0.0);
        Assert.True(hue < 360.0);
    }

    [Fact]
    public void GetHueMean_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        Assert.Equal(img.GetHueMean(), img.GetHueMean());
    }

    [Fact]
    public void GetHueMean_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorfulPpm());
        var before = img.GetHueMean();
        var path = TempFile("hue_save.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetHueMean(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChannelMean_GetSaturationScore_GetHueMean_SaveToFile_Pipeline()
    {
        // Astronomical image quality — synthetic star field simulation
        var path = TempFile("dogfood_starfield.ppm");
        var pixels = new byte[12 * 10 * 3];
        // Background: deep blue (R=10, G=10, B=40)
        for (int i = 0; i < 12 * 10; i++)
        {
            pixels[i * 3]     = 10;  // R
            pixels[i * 3 + 1] = 10;  // G
            pixels[i * 3 + 2] = 40;  // B
        }
        // Bright white stars at specific positions
        int[] starPos = { 15, 28, 42, 67, 88, 102 };
        foreach (int pos in starPos)
        {
            if (pos < 12 * 10)
            {
                pixels[pos * 3]     = 240;
                pixels[pos * 3 + 1] = 240;
                pixels[pos * 3 + 2] = 255;
            }
        }
        // Red giant star
        pixels[5 * 3] = 220; pixels[5 * 3 + 1] = 80; pixels[5 * 3 + 2] = 60;
        // Blue supergiant
        pixels[95 * 3] = 80; pixels[95 * 3 + 1] = 120; pixels[95 * 3 + 2] = 255;

        var header = System.Text.Encoding.ASCII.GetBytes("P6\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);

        // GetChannelMean — blue-dominant background
        var rMean = img.GetChannelMean(0);
        var gMean = img.GetChannelMean(1);
        var bMean = img.GetChannelMean(2);
        Assert.True(rMean >= 0.0); Assert.True(rMean <= 255.0);
        Assert.True(gMean >= 0.0); Assert.True(gMean <= 255.0);
        Assert.True(bMean >= 0.0); Assert.True(bMean <= 255.0);
        Assert.Equal(rMean, img.GetChannelMean(0)); // consistent
        Assert.Equal(gMean, img.GetChannelMean(1)); // consistent
        Assert.Equal(bMean, img.GetChannelMean(2)); // consistent

        // Blue channel should be highest (background is blue-tinted)
        Assert.True(bMean >= rMean);

        // GetSaturationScore
        var saturation = img.GetSaturationScore();
        Assert.True(saturation >= 0.0);
        Assert.True(saturation <= 1.0);
        Assert.Equal(saturation, img.GetSaturationScore()); // consistent

        // GetHueMean
        var hueMean = img.GetHueMean();
        Assert.True(hueMean >= 0.0);
        Assert.True(hueMean < 360.0);
        Assert.Equal(hueMean, img.GetHueMean()); // consistent

        // Pure red image: R channel highest, saturation=1
        var redImg = NetpbmImage.LoadFile(CreatePurePpmRed());
        Assert.Equal(255.0, redImg.GetChannelMean(0), precision: 2);
        Assert.Equal(0.0,   redImg.GetChannelMean(1), precision: 2);
        Assert.Equal(1.0,   redImg.GetSaturationScore(), precision: 4);

        // Greyscale: saturation=0
        var greyImg = NetpbmImage.LoadFile(CreateGreyscalePpm());
        Assert.Equal(0.0, greyImg.GetSaturationScore(), precision: 4);
        Assert.Equal(greyImg.GetChannelMean(0), greyImg.GetChannelMean(1), precision: 2);
        Assert.Equal(greyImg.GetChannelMean(1), greyImg.GetChannelMean(2), precision: 2);

        // SaveToFile
        var out1 = TempFile("dogfood_starfield_out.ppm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loaded.Width);
        Assert.Equal(10, loaded.Height);
        Assert.Equal(rMean, loaded.GetChannelMean(0), precision: 2);
        Assert.Equal(gMean, loaded.GetChannelMean(1), precision: 2);
        Assert.Equal(bMean, loaded.GetChannelMean(2), precision: 2);
        Assert.Equal(saturation, loaded.GetSaturationScore(), precision: 4);
        Assert.Equal(hueMean, loaded.GetHueMean(), precision: 2);

        // Final save
        var out2 = TempFile("dogfood_starfield_v2.ppm");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        var ex1 = Record.Exception(() => loaded2.GetChannelMean(0));
        var ex2 = Record.Exception(() => loaded2.GetSaturationScore());
        var ex3 = Record.Exception(() => loaded2.GetHueMean());
        Assert.Null(ex1); Assert.Null(ex2); Assert.Null(ex3);
    }
}
