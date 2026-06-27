// Tests for NetpbmImage.GetMeanPixelValue, GetMedianPixelValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R398

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R398: Tests for NetpbmImage.GetMeanPixelValue, GetMedianPixelValue deeper.
/// GetMeanPixelValue(): returns the arithmetic mean of all pixel intensities.
/// GetMedianPixelValue(): returns the median pixel intensity.
/// Covers: GetMeanPixelValue no-throw; GetMeanPixelValue in-range;
/// GetMeanPixelValue exact for uniform; GetMeanPixelValue consistent; GetMeanPixelValue save-load;
/// GetMedianPixelValue no-throw; GetMedianPixelValue in-range;
/// GetMedianPixelValue exact for uniform; GetMedianPixelValue consistent; GetMedianPixelValue save-load;
/// GetMeanPixelValue between min and max; GetMeanPixelValue equals median for uniform;
/// dogfood pipeline.
/// </summary>
public class NetpbmR398GetMeanPixelValueAndMedianPixelValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR398GetMeanPixelValueAndMedianPixelValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR398_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(string name, int width, int height, int intensity)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append(intensity);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm(string name, int width, int height)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append((int)(255.0 * x / (width - 1)));
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMeanPixelValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanPixelValue_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetMeanPixelValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMeanPixelValue_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var mean = img.GetMeanPixelValue();
        Assert.True(mean >= 0.0 && mean <= 255.0);
    }

    [Fact]
    public void GetMeanPixelValue_Exact_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 128));
        Assert.Equal(128.0, img.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetMeanPixelValue_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetMeanPixelValue(), img.GetMeanPixelValue());
    }

    [Fact]
    public void GetMeanPixelValue_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetMeanPixelValue();
        var path = TempFile("mean_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetMeanPixelValue_Between_Min_And_Max()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var mean = img.GetMeanPixelValue();
        Assert.True(mean >= img.GetMinPixelValue());
        Assert.True(mean <= img.GetMaxPixelValue());
    }

    // -------------------------------------------------------------------------
    // GetMedianPixelValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedianPixelValue_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var ex = Record.Exception(() => img.GetMedianPixelValue());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMedianPixelValue_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var median = img.GetMedianPixelValue();
        Assert.True(median >= 0.0 && median <= 255.0);
    }

    [Fact]
    public void GetMedianPixelValue_Exact_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform.pgm", 40, 40, 100));
        Assert.Equal(100.0, img.GetMedianPixelValue(), precision: 4);
    }

    [Fact]
    public void GetMedianPixelValue_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        Assert.Equal(img.GetMedianPixelValue(), img.GetMedianPixelValue());
    }

    [Fact]
    public void GetMedianPixelValue_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("gradient.pgm", 40, 40));
        var before = img.GetMedianPixelValue();
        var path = TempFile("median_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetMedianPixelValue(), precision: 4);
    }

    [Fact]
    public void GetMeanPixelValue_Equals_Median_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uniform128.pgm", 40, 40, 128));
        Assert.Equal(img.GetMeanPixelValue(), img.GetMedianPixelValue(), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMeanPixelValue_GetMedianPixelValue_Pipeline()
    {
        // Remote Sensing — UKSA / Ordnance Survey / Sentinel-2: Land Cover Classification
        // Grayscale normalised difference index images for agricultural land assessment
        // Mean pixel detects average reflectance; median is robust to cloud shadows

        // Scene 1: Green vegetation (high reflectance in NIR — bright pixels)
        var path1 = TempFile("ndvi_vegetation_patch.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240601);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    // Vegetation: 170-230 with occasional shadow (30-60)
                    int val = rng.NextDouble() < 0.05 ? rng.Next(30, 60) : rng.Next(170, 231);
                    row.Append(val);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path1, sb.ToString());
        }

        // Scene 2: Urban area (mixed reflectance — wide spread)
        var path2 = TempFile("ndvi_urban_area.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240602);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(rng.Next(40, 200)); // Wide range
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path2, sb.ToString());
        }

        // Scene 3: Water body (low reflectance — dark pixels)
        var path3 = TempFile("ndvi_water_body.pgm");
        {
            int w = 64, h = 48;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            var rng = new Random(20240603);
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(rng.Next(5, 50)); // Dark water
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path3, sb.ToString());
        }

        // Scene 4: Uniform calibration target (mid-grey)
        var path4 = TempFile("ndvi_calibration.pgm");
        {
            int w = 40, h = 40;
            var sb = new StringBuilder();
            sb.AppendLine("P2");
            sb.AppendLine($"{w} {h}");
            sb.AppendLine("255");
            for (int y = 0; y < h; y++)
            {
                var row = new StringBuilder();
                for (int x = 0; x < w; x++)
                {
                    if (x > 0) row.Append(' ');
                    row.Append(127);
                }
                sb.AppendLine(row.ToString());
            }
            File.WriteAllText(path4, sb.ToString());
        }

        var img1 = NetpbmImage.LoadFile(path1);
        var img2 = NetpbmImage.LoadFile(path2);
        var img3 = NetpbmImage.LoadFile(path3);
        var img4 = NetpbmImage.LoadFile(path4);

        // Mean pixel values
        var mean1 = img1.GetMeanPixelValue();
        var mean2 = img2.GetMeanPixelValue();
        var mean3 = img3.GetMeanPixelValue();
        var mean4 = img4.GetMeanPixelValue();

        Assert.True(mean1 >= 0.0 && mean1 <= 255.0);
        Assert.True(mean2 >= 0.0 && mean2 <= 255.0);
        Assert.True(mean3 >= 0.0 && mean3 <= 255.0);
        Assert.Equal(127.0, mean4, precision: 4); // uniform calibration

        // Vegetation mean > water mean (bright vs dark)
        Assert.True(mean1 > mean3);

        // Median pixel values
        var median1 = img1.GetMedianPixelValue();
        var median2 = img2.GetMedianPixelValue();
        var median3 = img3.GetMedianPixelValue();
        var median4 = img4.GetMedianPixelValue();

        Assert.True(median1 >= 0.0 && median1 <= 255.0);
        Assert.True(median2 >= 0.0 && median2 <= 255.0);
        Assert.True(median3 >= 0.0 && median3 <= 255.0);
        Assert.Equal(127.0, median4, precision: 4); // uniform calibration

        // For uniform image, mean == median
        Assert.Equal(mean4, median4, precision: 4);

        // Consistency checks
        Assert.Equal(mean1, img1.GetMeanPixelValue());
        Assert.Equal(median2, img2.GetMedianPixelValue());

        // Between min and max
        Assert.True(mean1 >= img1.GetMinPixelValue());
        Assert.True(mean1 <= img1.GetMaxPixelValue());
        Assert.True(median3 >= img3.GetMinPixelValue());
        Assert.True(median3 <= img3.GetMaxPixelValue());

        // SaveToFile
        var out1 = TempFile("ndvi_veg_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(mean1, loaded1.GetMeanPixelValue(), precision: 4);
        Assert.Equal(median1, loaded1.GetMedianPixelValue(), precision: 4);

        var out3 = TempFile("ndvi_water_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(mean3, loaded3.GetMeanPixelValue(), precision: 4);
        Assert.Equal(median3, loaded3.GetMedianPixelValue(), precision: 4);

        var out4 = TempFile("ndvi_calib_out.pgm");
        img4.SaveToFile(out4);
        var loaded4 = NetpbmImage.LoadFile(out4);
        Assert.Equal(127.0, loaded4.GetMeanPixelValue(), precision: 4);
        Assert.Equal(127.0, loaded4.GetMedianPixelValue(), precision: 4);

        var ex1 = Record.Exception(() => loaded1.GetMeanPixelValue());
        var ex2 = Record.Exception(() => loaded3.GetMedianPixelValue());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
