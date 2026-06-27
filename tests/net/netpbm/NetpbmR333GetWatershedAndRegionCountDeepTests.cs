// Tests for NetpbmImage.GetWatershedRegionCount, GetRegionMeanIntensity, GetRegionBoundaryPixels deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R333

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R333: Tests for NetpbmImage.GetWatershedRegionCount, GetRegionMeanIntensity, GetRegionBoundaryPixels deeper.
/// GetWatershedRegionCount(): returns the number of distinct regions after watershed segmentation.
/// GetRegionMeanIntensity(regionIndex): returns the mean pixel intensity of the specified region.
/// GetRegionBoundaryPixels(regionIndex): returns the count of boundary pixels for the specified region.
/// Covers: GetWatershedRegionCount no-throw; GetWatershedRegionCount positive;
/// GetWatershedRegionCount consistent; GetWatershedRegionCount one for uniform image;
/// GetRegionMeanIntensity no-throw; GetRegionMeanIntensity in [0, MaxVal]; GetRegionMeanIntensity consistent;
/// GetRegionBoundaryPixels no-throw; GetRegionBoundaryPixels non-negative;
/// GetRegionBoundaryPixels consistent; GetRegionBoundaryPixels save-load;
/// dogfood CreateImage→GetWatershedRegionCount→GetRegionMeanIntensity→GetRegionBoundaryPixels pipeline.
/// </summary>
public class NetpbmR333GetWatershedAndRegionCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR333GetWatershedAndRegionCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR333_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMultiRegionPgm()
    {
        // 12x12 with 4 distinct regions (quadrants at different intensities)
        var path = TempFile("regions.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                int val;
                if (r < 6 && c < 6) val = 50;       // top-left: dark
                else if (r < 6 && c >= 6) val = 150; // top-right: medium
                else if (r >= 6 && c < 6) val = 100; // bottom-left: medium-dark
                else val = 200;                        // bottom-right: bright
                sb.Append(val.ToString() + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++) sb.Append("128 ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
                sb.Append((c * 21).ToString() + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetWatershedRegionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWatershedRegionCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        var ex = Record.Exception(() => img.GetWatershedRegionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetWatershedRegionCount_Positive()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        Assert.True(img.GetWatershedRegionCount() > 0);
    }

    [Fact]
    public void GetWatershedRegionCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        Assert.Equal(img.GetWatershedRegionCount(), img.GetWatershedRegionCount());
    }

    [Fact]
    public void GetWatershedRegionCount_One_For_Uniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        // Uniform image has no gradients → 1 region
        Assert.Equal(1, img.GetWatershedRegionCount());
    }

    // -------------------------------------------------------------------------
    // GetRegionMeanIntensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRegionMeanIntensity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        var ex = Record.Exception(() => img.GetRegionMeanIntensity(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRegionMeanIntensity_In_Valid_Range()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        var mean = img.GetRegionMeanIntensity(0);
        Assert.True(mean >= 0 && mean <= img.MaxVal);
    }

    [Fact]
    public void GetRegionMeanIntensity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        Assert.Equal(img.GetRegionMeanIntensity(0), img.GetRegionMeanIntensity(0));
    }

    // -------------------------------------------------------------------------
    // GetRegionBoundaryPixels
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRegionBoundaryPixels_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        var ex = Record.Exception(() => img.GetRegionBoundaryPixels(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRegionBoundaryPixels_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        Assert.True(img.GetRegionBoundaryPixels(0) >= 0);
    }

    [Fact]
    public void GetRegionBoundaryPixels_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        Assert.Equal(img.GetRegionBoundaryPixels(0), img.GetRegionBoundaryPixels(0));
    }

    [Fact]
    public void GetRegionBoundaryPixels_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiRegionPgm());
        var before = img.GetRegionBoundaryPixels(0);
        var path = TempFile("reg_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetRegionBoundaryPixels(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWatershedRegionCount_GetRegionMeanIntensity_GetRegionBoundaryPixels_Pipeline()
    {
        // Medical imaging — MRI brain slice segmentation for white matter/grey matter/CSF classification
        var path = TempFile("mri_brain_slice.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        var rng = new Random(20240801);
        for (int r = 0; r < 12; r++)
        {
            for (int c = 0; c < 12; c++)
            {
                int val;
                double dist = Math.Sqrt(Math.Pow(r - 5.5, 2) + Math.Pow(c - 5.5, 2));
                if (dist < 2.0)
                    // CSF (bright): inner circle
                    val = 220 + rng.Next(-10, 20);
                else if (dist < 3.5)
                    // White matter: middle ring
                    val = 170 + rng.Next(-15, 25);
                else if (dist < 5.5)
                    // Grey matter: outer ring
                    val = 100 + rng.Next(-20, 30);
                else
                    // Background: dark
                    val = 20 + rng.Next(-10, 10);
                sb.Append(Math.Clamp(val, 0, 255).ToString() + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);

        // GetWatershedRegionCount — expect multiple regions (CSF/WM/GM/background)
        var regionCount = img.GetWatershedRegionCount();
        Assert.True(regionCount > 0);
        Assert.Equal(regionCount, img.GetWatershedRegionCount()); // consistent

        // GetRegionMeanIntensity — region 0
        var meanR0 = img.GetRegionMeanIntensity(0);
        Assert.True(meanR0 >= 0 && meanR0 <= 255);
        Assert.Equal(meanR0, img.GetRegionMeanIntensity(0)); // consistent

        // GetRegionBoundaryPixels — region 0
        var boundR0 = img.GetRegionBoundaryPixels(0);
        Assert.True(boundR0 >= 0);
        Assert.Equal(boundR0, img.GetRegionBoundaryPixels(0)); // consistent

        // If multiple regions exist, check region 1 too
        if (regionCount > 1)
        {
            var meanR1 = img.GetRegionMeanIntensity(1);
            Assert.True(meanR1 >= 0 && meanR1 <= 255);
            var boundR1 = img.GetRegionBoundaryPixels(1);
            Assert.True(boundR1 >= 0);
        }

        // Uniform reference
        var uniformPath = TempFile("uniform.pgm");
        var uSb = new System.Text.StringBuilder();
        uSb.AppendLine("P2"); uSb.AppendLine("12 12"); uSb.AppendLine("255");
        for (int r = 0; r < 12; r++) { for (int c = 0; c < 12; c++) uSb.Append("128 "); uSb.AppendLine(); }
        File.WriteAllText(uniformPath, uSb.ToString());
        var uImg = NetpbmImage.LoadFile(uniformPath);
        Assert.Equal(1, uImg.GetWatershedRegionCount());

        // SaveToFile
        var outPath = TempFile("mri_brain_slice_out.pgm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(regionCount, loaded.GetWatershedRegionCount());
        Assert.Equal(meanR0, loaded.GetRegionMeanIntensity(0));
        Assert.Equal(boundR0, loaded.GetRegionBoundaryPixels(0));
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // Additional metrics
        var mean = img.GetMean();
        Assert.True(mean > 0 && mean < 256);
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
    }
}
