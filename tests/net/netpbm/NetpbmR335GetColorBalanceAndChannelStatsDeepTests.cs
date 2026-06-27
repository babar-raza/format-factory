// Tests for NetpbmImage.GetChannelMean, GetChannelStdDev, GetColorBalance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R335

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R335: Tests for NetpbmImage.GetChannelMean, GetChannelStdDev, GetColorBalance deeper.
/// GetChannelMean(channel): returns the mean pixel value for the specified channel (R/G/B for PPM, 0 for PGM).
/// GetChannelStdDev(channel): returns the standard deviation for the specified channel.
/// GetColorBalance(): returns the ratio of channel means as (R/G, B/G) tuple or scalar imbalance.
/// Covers: GetChannelMean no-throw; GetChannelMean in [0, MaxVal]; GetChannelMean consistent;
/// GetChannelMean uniform image equals pixel value;
/// GetChannelStdDev no-throw; GetChannelStdDev non-negative; GetChannelStdDev consistent;
/// GetChannelStdDev zero for uniform image;
/// GetColorBalance no-throw; GetColorBalance non-negative; GetColorBalance consistent;
/// GetColorBalance zero for grey image; GetColorBalance save-load;
/// dogfood CreateImage→GetChannelMean→GetChannelStdDev→GetColorBalance pipeline.
/// </summary>
public class NetpbmR335GetColorBalanceAndChannelStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR335GetColorBalanceAndChannelStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR335_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateColorPpm()
    {
        // 12×12 PPM with red-dominant quadrant, green-dominant quadrant, etc.
        var path = TempFile("color.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                if (r < 6 && c < 6)
                    sb.Append("200 50 50 "); // red dominant
                else if (r < 6 && c >= 6)
                    sb.Append("50 200 50 "); // green dominant
                else if (r >= 6 && c < 6)
                    sb.Append("50 50 200 "); // blue dominant
                else
                    sb.Append("150 150 150 "); // grey
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPpm()
    {
        var path = TempFile("uniform.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++) sb.Append("128 128 128 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGreyPpm()
    {
        var path = TempFile("grey.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++) sb.Append("100 100 100 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetChannelMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelMean_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        var ex = Record.Exception(() => img.GetChannelMean(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelMean_In_Valid_Range()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        var mean = img.GetChannelMean(0);
        Assert.True(mean >= 0 && mean <= 255);
    }

    [Fact]
    public void GetChannelMean_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        Assert.Equal(img.GetChannelMean(0), img.GetChannelMean(0));
    }

    [Fact]
    public void GetChannelMean_Uniform_Equals_Pixel_Value()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPpm());
        Assert.Equal(128.0, img.GetChannelMean(0), precision: 6); // red channel
        Assert.Equal(128.0, img.GetChannelMean(1), precision: 6); // green channel
        Assert.Equal(128.0, img.GetChannelMean(2), precision: 6); // blue channel
    }

    // -------------------------------------------------------------------------
    // GetChannelStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelStdDev_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        var ex = Record.Exception(() => img.GetChannelStdDev(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelStdDev_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        Assert.True(img.GetChannelStdDev(0) >= 0);
    }

    [Fact]
    public void GetChannelStdDev_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        Assert.Equal(img.GetChannelStdDev(1), img.GetChannelStdDev(1));
    }

    [Fact]
    public void GetChannelStdDev_Zero_For_Uniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPpm());
        Assert.Equal(0.0, img.GetChannelStdDev(0), precision: 6);
        Assert.Equal(0.0, img.GetChannelStdDev(1), precision: 6);
        Assert.Equal(0.0, img.GetChannelStdDev(2), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColorBalance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorBalance_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        var ex = Record.Exception(() => img.GetColorBalance());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorBalance_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        Assert.True(img.GetColorBalance() >= 0);
    }

    [Fact]
    public void GetColorBalance_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        Assert.Equal(img.GetColorBalance(), img.GetColorBalance());
    }

    [Fact]
    public void GetColorBalance_Zero_For_Grey()
    {
        var img = NetpbmImage.LoadFile(CreateGreyPpm());
        // Perfect grey has zero color imbalance
        Assert.Equal(0.0, img.GetColorBalance(), precision: 6);
    }

    [Fact]
    public void GetColorBalance_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateColorPpm());
        var before = img.GetColorBalance();
        var path = TempFile("cb_save.ppm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorBalance(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChannelMean_GetChannelStdDev_GetColorBalance_Pipeline()
    {
        // Satellite remote sensing — multispectral image for vegetation index analysis
        // Channels: R (red), G (green), B (blue) — simulate high NIR vegetation areas
        var path = TempFile("multispectral.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        var rng = new Random(20250701);
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                int red, green, blue;
                if (r < 5)
                {
                    // Vegetation: high green, low red
                    red = 50 + rng.Next(40);
                    green = 150 + rng.Next(60);
                    blue = 60 + rng.Next(40);
                }
                else if (r >= 5 && r < 9)
                {
                    // Urban: roughly balanced, slightly bluish
                    red = 100 + rng.Next(60);
                    green = 100 + rng.Next(60);
                    blue = 130 + rng.Next(60);
                }
                else
                {
                    // Water: low reflectance overall
                    red = 20 + rng.Next(30);
                    green = 40 + rng.Next(30);
                    blue = 80 + rng.Next(40);
                }
                sb.Append($"{Math.Clamp(red, 0, 255)} {Math.Clamp(green, 0, 255)} {Math.Clamp(blue, 0, 255)} ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);

        // GetChannelMean — all 3 channels
        var rMean = img.GetChannelMean(0);
        var gMean = img.GetChannelMean(1);
        var bMean = img.GetChannelMean(2);
        Assert.True(rMean >= 0 && rMean <= 255);
        Assert.True(gMean >= 0 && gMean <= 255);
        Assert.True(bMean >= 0 && bMean <= 255);
        Assert.Equal(rMean, img.GetChannelMean(0)); // consistent

        // Vegetation dominates → green > red for this image
        Assert.True(gMean > rMean);

        // GetChannelStdDev
        var rStd = img.GetChannelStdDev(0);
        var gStd = img.GetChannelStdDev(1);
        var bStd = img.GetChannelStdDev(2);
        Assert.True(rStd >= 0);
        Assert.True(gStd >= 0);
        Assert.True(bStd >= 0);
        Assert.Equal(rStd, img.GetChannelStdDev(0)); // consistent

        // GetColorBalance — non-zero since we have color variation
        var balance = img.GetColorBalance();
        Assert.True(balance >= 0);
        Assert.Equal(balance, img.GetColorBalance()); // consistent

        // Uniform grey reference
        var greyPath = TempFile("grey_ref.ppm");
        var gSb = new System.Text.StringBuilder();
        gSb.AppendLine("P3"); gSb.AppendLine("12 12"); gSb.AppendLine("255");
        for (int r = 0; r < 12; r++) { for (int c = 0; c < 12; c++) gSb.Append("100 100 100 "); gSb.AppendLine(); }
        File.WriteAllText(greyPath, gSb.ToString());
        var grey = NetpbmImage.LoadFile(greyPath);
        Assert.Equal(0.0, grey.GetColorBalance(), precision: 6);
        Assert.Equal(0.0, grey.GetChannelStdDev(0), precision: 6);

        // SaveToFile
        var outPath = TempFile("multispectral_out.ppm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(rMean, loaded.GetChannelMean(0), precision: 6);
        Assert.Equal(gMean, loaded.GetChannelMean(1), precision: 6);
        Assert.Equal(rStd, loaded.GetChannelStdDev(0), precision: 6);
        Assert.Equal(balance, loaded.GetColorBalance(), precision: 6);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // Additional metrics
        var mean = img.GetMean();
        Assert.True(mean > 0);
    }
}
