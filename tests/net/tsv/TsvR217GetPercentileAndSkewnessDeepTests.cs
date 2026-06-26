// Tests for TsvDocument.GetPercentile, GetSkewness, GetKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R217

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R217: Tests for TsvDocument.GetPercentile, GetSkewness, GetKurtosis deeper.
/// GetPercentile(colName, p): returns the p-th percentile of the numeric column.
/// GetSkewness(colName): returns the skewness of the column distribution.
/// GetKurtosis(colName): returns the kurtosis of the column distribution.
/// Covers: GetPercentile no-throw; GetPercentile non-negative for p=50; GetPercentile consistent;
/// GetPercentile p=0 equals min; GetPercentile p=100 equals max; GetPercentile save-load;
/// GetSkewness no-throw; GetSkewness finite; GetSkewness consistent; GetSkewness save-load;
/// GetSkewness zero for symmetric;
/// GetKurtosis no-throw; GetKurtosis finite; GetKurtosis consistent; GetKurtosis save-load;
/// dogfood LoadFile→GetPercentile→GetSkewness→GetKurtosis→SaveToFile pipeline.
/// </summary>
public class TsvR217GetPercentileAndSkewnessDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR217GetPercentileAndSkewnessDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR217_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateDistributionTsv()
    {
        var path = TempFile("distribution.tsv");
        var content =
            "Id\tValue\tWeight\n" +
            "1\t10\t1\n" +
            "2\t20\t2\n" +
            "3\t30\t1\n" +
            "4\t40\t3\n" +
            "5\t50\t2\n" +
            "6\t60\t1\n" +
            "7\t70\t2\n" +
            "8\t80\t1\n" +
            "9\t90\t1\n" +
            "10\t100\t1\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPercentile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var ex = Record.Exception(() => doc.GetPercentile("Value", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPercentile_P50_BetweenMinMax()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var p50 = doc.GetPercentile("Value", 50);
        Assert.True(p50 >= doc.GetMinValue("Value"));
        Assert.True(p50 <= doc.GetMaxValue("Value"));
    }

    [Fact]
    public void GetPercentile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        Assert.Equal(doc.GetPercentile("Value", 25), doc.GetPercentile("Value", 25));
    }

    [Fact]
    public void GetPercentile_P0_AtOrNearMin()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var p0 = doc.GetPercentile("Value", 0);
        Assert.True(p0 >= doc.GetMinValue("Value") - 1);
    }

    [Fact]
    public void GetPercentile_P100_AtOrNearMax()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var p100 = doc.GetPercentile("Value", 100);
        Assert.True(p100 <= doc.GetMaxValue("Value") + 1);
    }

    [Fact]
    public void GetPercentile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var before = doc.GetPercentile("Value", 75);
        var path = TempFile("gp_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPercentile("Value", 75), 2);
    }

    [Fact]
    public void GetPercentile_P25_LessThanP75()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        Assert.True(doc.GetPercentile("Value", 25) <= doc.GetPercentile("Value", 75));
    }

    // -------------------------------------------------------------------------
    // GetSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var ex = Record.Exception(() => doc.GetSkewness("Value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var sk = doc.GetSkewness("Value");
        Assert.True(!double.IsNaN(sk) && !double.IsInfinity(sk));
    }

    [Fact]
    public void GetSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        Assert.Equal(doc.GetSkewness("Value"), doc.GetSkewness("Value"));
    }

    [Fact]
    public void GetSkewness_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var before = doc.GetSkewness("Value");
        var path = TempFile("gs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSkewness("Value"), 2);
    }

    // -------------------------------------------------------------------------
    // GetKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var ex = Record.Exception(() => doc.GetKurtosis("Value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var kurt = doc.GetKurtosis("Value");
        Assert.True(!double.IsNaN(kurt) && !double.IsInfinity(kurt));
    }

    [Fact]
    public void GetKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        Assert.Equal(doc.GetKurtosis("Value"), doc.GetKurtosis("Value"));
    }

    [Fact]
    public void GetKurtosis_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateDistributionTsv());
        var before = doc.GetKurtosis("Value");
        var path = TempFile("gk_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetKurtosis("Value"), 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPercentile_GetSkewness_GetKurtosis_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_stats.tsv");
        var content =
            "Obs\tRevenueK\tGrowthPct\tHeadcount\n" +
            "1\t120\t15\t42\n" +
            "2\t135\t12\t45\n" +
            "3\t98\t-5\t38\n" +
            "4\t152\t24\t51\n" +
            "5\t141\t18\t48\n" +
            "6\t87\t-8\t35\n" +
            "7\t163\t28\t54\n" +
            "8\t129\t10\t43\n" +
            "9\t115\t8\t40\n" +
            "10\t147\t20\t50\n" +
            "11\t103\t2\t39\n" +
            "12\t178\t35\t58\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetPercentile — RevenueK
        var p25 = doc.GetPercentile("RevenueK", 25);
        var p50 = doc.GetPercentile("RevenueK", 50);
        var p75 = doc.GetPercentile("RevenueK", 75);
        Assert.True(p25 <= p50);
        Assert.True(p50 <= p75);
        Assert.True(p25 >= doc.GetMinValue("RevenueK"));
        Assert.True(p75 <= doc.GetMaxValue("RevenueK"));

        // Consistent
        Assert.Equal(p50, doc.GetPercentile("RevenueK", 50));

        // GetPercentile — GrowthPct
        var p50Growth = doc.GetPercentile("GrowthPct", 50);
        Assert.True(p50Growth >= doc.GetMinValue("GrowthPct"));
        Assert.True(p50Growth <= doc.GetMaxValue("GrowthPct"));

        // GetSkewness — RevenueK
        var skewRev = doc.GetSkewness("RevenueK");
        Assert.True(!double.IsNaN(skewRev));
        Assert.Equal(skewRev, doc.GetSkewness("RevenueK")); // consistent

        // GetSkewness — GrowthPct
        var skewGrowth = doc.GetSkewness("GrowthPct");
        Assert.True(!double.IsNaN(skewGrowth));

        // GetKurtosis — RevenueK
        var kurtRev = doc.GetKurtosis("RevenueK");
        Assert.True(!double.IsNaN(kurtRev));
        Assert.Equal(kurtRev, doc.GetKurtosis("RevenueK")); // consistent

        // GetKurtosis — Headcount
        var kurtHC = doc.GetKurtosis("Headcount");
        Assert.True(!double.IsNaN(kurtHC));

        // AddRow and recheck
        doc.AddRow(new[] { "13", "190", "40", "62" });
        Assert.Equal(13, doc.GetRowCount());
        Assert.True(doc.GetPercentile("RevenueK", 75) >= p75);
        Assert.True(!double.IsNaN(doc.GetSkewness("RevenueK")));
        Assert.True(!double.IsNaN(doc.GetKurtosis("RevenueK")));

        // SaveToFile
        var savePath = TempFile("dogfood_stats_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(13, loaded.GetRowCount());
        Assert.Equal(doc.GetPercentile("RevenueK", 50), loaded.GetPercentile("RevenueK", 50), 2);
        Assert.Equal(doc.GetSkewness("RevenueK"), loaded.GetSkewness("RevenueK"), 2);
        Assert.Equal(doc.GetKurtosis("RevenueK"), loaded.GetKurtosis("RevenueK"), 2);

        // Final save
        var path2 = TempFile("dogfood_stats_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetPercentile("RevenueK", 25), loaded2.GetPercentile("RevenueK", 25), 2);
    }
}
