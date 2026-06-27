// Tests for NetpbmImage.GetRipleyKFunction, GetSpatialClusteringIndex deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R342

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R342: Tests for NetpbmImage.GetRipleyKFunction, GetSpatialClusteringIndex deeper.
/// GetRipleyKFunction(radius): returns the Ripley K estimate for pixel intensity distribution at given radius.
/// GetSpatialClusteringIndex(): returns a scalar measure of how clustered bright pixels are vs. random.
/// Covers: GetRipleyKFunction no-throw; GetRipleyKFunction non-negative; GetRipleyKFunction consistent;
/// GetRipleyKFunction increases with radius (K function is monotone);
/// GetSpatialClusteringIndex no-throw; GetSpatialClusteringIndex non-negative; GetSpatialClusteringIndex consistent;
/// GetSpatialClusteringIndex uniform lower than clustered; GetSpatialClusteringIndex save-load;
/// dogfood CreateDoc→GetRipleyKFunction→GetSpatialClusteringIndex pipeline.
/// </summary>
public class NetpbmR342GetRipleyKFunctionAndSpatialClusteringDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR342GetRipleyKFunctionAndSpatialClusteringDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR342_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformPgm(int size = 50, int value = 128)
    {
        var path = TempFile($"uniform_{value}.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        for (int r = 0; r < size; r++)
        {
            for (int c = 0; c < size; c++) sb.Append(value + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateClusteredPgm(int size = 80)
    {
        // Several bright clusters on dark background
        var path = TempFile("clustered.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        int[][] clusterCentres = { new[]{15,15}, new[]{15,65}, new[]{40,40}, new[]{65,15}, new[]{65,65} };
        for (int r = 0; r < size; r++)
        {
            for (int c = 0; c < size; c++)
            {
                int val = 10; // dark background
                foreach (var cen in clusterCentres)
                {
                    double d = Math.Sqrt((r - cen[0]) * (r - cen[0]) + (c - cen[1]) * (c - cen[1]));
                    if (d <= 8) { val = 220; break; }
                }
                sb.Append(val + " ");
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRandomPgm(int size = 60)
    {
        var path = TempFile("random.pgm");
        var rng = new Random(88);
        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{size} {size}\n255");
        for (int r = 0; r < size; r++)
        {
            for (int c = 0; c < size; c++)
                sb.Append(rng.Next(256) + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRipleyKFunction
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRipleyKFunction_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        var ex = Record.Exception(() => img.GetRipleyKFunction(5.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRipleyKFunction_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        Assert.True(img.GetRipleyKFunction(5.0) >= 0.0);
    }

    [Fact]
    public void GetRipleyKFunction_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        Assert.Equal(img.GetRipleyKFunction(10.0), img.GetRipleyKFunction(10.0));
    }

    [Fact]
    public void GetRipleyKFunction_Increases_With_Radius()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        var k5 = img.GetRipleyKFunction(5.0);
        var k15 = img.GetRipleyKFunction(15.0);
        // K function is non-decreasing in radius
        Assert.True(k15 >= k5);
    }

    [Fact]
    public void GetRipleyKFunction_Larger_Radius_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        var ex = Record.Exception(() => img.GetRipleyKFunction(20.0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSpatialClusteringIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSpatialClusteringIndex_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        var ex = Record.Exception(() => img.GetSpatialClusteringIndex());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSpatialClusteringIndex_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        Assert.True(img.GetSpatialClusteringIndex() >= 0.0);
    }

    [Fact]
    public void GetSpatialClusteringIndex_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        Assert.Equal(img.GetSpatialClusteringIndex(), img.GetSpatialClusteringIndex());
    }

    [Fact]
    public void GetSpatialClusteringIndex_Clustered_Greater_Than_Uniform()
    {
        var clustered = NetpbmImage.LoadFile(CreateClusteredPgm());
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.True(clustered.GetSpatialClusteringIndex() >= uniform.GetSpatialClusteringIndex());
    }

    [Fact]
    public void GetSpatialClusteringIndex_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateClusteredPgm());
        var before = img.GetSpatialClusteringIndex();
        var path = TempFile("sci_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSpatialClusteringIndex());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRipleyKFunction_GetSpatialClusteringIndex_Pipeline()
    {
        // Astronomy — galaxy cluster member distribution analysis (simulated SDSS photometric survey data)
        var rng = new Random(20250701);
        int width = 200, height = 200;

        // Simulate galaxy cluster: Abell-type cluster with BCG at centre + satellite galaxies + field galaxies
        var path = TempFile("galaxy_cluster_sdss.pgm");
        var pixels = new int[height, width];

        // Background: faint field galaxies (noise level)
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
                pixels[r, c] = rng.Next(15); // dark sky background

        // Cluster core: bright central region (BCG = Brightest Cluster Galaxy)
        int bcgR = 100, bcgC = 100;
        for (int r = 0; r < height; r++)
            for (int c = 0; c < width; c++)
            {
                double d = Math.Sqrt((r - bcgR) * (r - bcgR) + (c - bcgC) * (c - bcgC));
                if (d < 5) pixels[r, c] = 230 + rng.Next(25);
                else if (d < 30) pixels[r, c] = Math.Min(255, pixels[r, c] + (int)(100 * Math.Exp(-d * d / (2 * 15 * 15))));
            }

        // Satellite cluster members (concentrated within 50 pixels of BCG)
        for (int i = 0; i < 60; i++)
        {
            double theta = rng.NextDouble() * 2 * Math.PI;
            double dist = rng.NextDouble() * 45;
            int gr = (int)(bcgR + dist * Math.Sin(theta));
            int gc = (int)(bcgC + dist * Math.Cos(theta));
            if (gr >= 0 && gr < height && gc >= 0 && gc < width)
                for (int dr = -2; dr <= 2; dr++)
                    for (int dc = -2; dc <= 2; dc++)
                    {
                        int rr = gr + dr, rc = gc + dc;
                        if (rr >= 0 && rr < height && rc >= 0 && rc < width)
                            pixels[rr, rc] = Math.Min(255, pixels[rr, rc] + 80 + rng.Next(60));
                    }
        }

        // Background field galaxies (uniformly distributed)
        for (int i = 0; i < 40; i++)
        {
            int fr = rng.Next(height), fc = rng.Next(width);
            if (Math.Sqrt((fr - bcgR) * (fr - bcgR) + (fc - bcgC) * (fc - bcgC)) > 60)
                for (int dr = -1; dr <= 1; dr++)
                    for (int dc = -1; dc <= 1; dc++)
                    {
                        int rr = fr + dr, rc = fc + dc;
                        if (rr >= 0 && rr < height && rc >= 0 && rc < width)
                            pixels[rr, rc] = Math.Min(255, pixels[rr, rc] + 50 + rng.Next(40));
                    }
        }

        var sb = new System.Text.StringBuilder();
        sb.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++)
                sb.Append(pixels[r, c] + " ");
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());

        // Uniform comparison
        var uniformPath = TempFile("uniform_sky.pgm");
        var sb2 = new System.Text.StringBuilder();
        sb2.AppendLine($"P2\n{width} {height}\n255");
        for (int r = 0; r < height; r++)
        {
            for (int c = 0; c < width; c++) sb2.Append((20 + rng.Next(10)) + " ");
            sb2.AppendLine();
        }
        File.WriteAllText(uniformPath, sb2.ToString());

        var cluster = NetpbmImage.LoadFile(path);
        var uniform = NetpbmImage.LoadFile(uniformPath);

        Assert.Equal(width, cluster.Width);
        Assert.Equal(height, cluster.Height);

        // GetRipleyKFunction
        var k5 = cluster.GetRipleyKFunction(5.0);
        Assert.True(k5 >= 0.0);
        Assert.Equal(k5, cluster.GetRipleyKFunction(5.0)); // consistent

        var k10 = cluster.GetRipleyKFunction(10.0);
        var k20 = cluster.GetRipleyKFunction(20.0);
        var k40 = cluster.GetRipleyKFunction(40.0);
        // K monotone non-decreasing
        Assert.True(k10 >= k5);
        Assert.True(k20 >= k10);
        Assert.True(k40 >= k20);

        // GetSpatialClusteringIndex
        var sciCluster = cluster.GetSpatialClusteringIndex();
        Assert.True(sciCluster >= 0.0);
        Assert.Equal(sciCluster, cluster.GetSpatialClusteringIndex()); // consistent

        var sciUniform = uniform.GetSpatialClusteringIndex();
        Assert.True(sciCluster >= sciUniform); // cluster more clustered than uniform sky

        // Image stats
        Assert.True(cluster.GetMeanIntensity() > uniform.GetMeanIntensity());
        Assert.True(cluster.GetStdDevIntensity() > 0.0);

        // SaveToFile
        var outPath = TempFile("galaxy_cluster_sdss_out.pgm");
        cluster.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(width, loaded.Width);
        Assert.Equal(height, loaded.Height);
        Assert.Equal(sciCluster, loaded.GetSpatialClusteringIndex());
        Assert.Equal(k10, loaded.GetRipleyKFunction(10.0));

        var ex1 = Record.Exception(() => loaded.GetRipleyKFunction(15.0));
        var ex2 = Record.Exception(() => loaded.GetSpatialClusteringIndex());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
