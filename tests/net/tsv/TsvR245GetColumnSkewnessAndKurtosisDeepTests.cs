// Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnMoment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R245: Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnMoment deeper.
/// GetColumnSkewness(columnName): returns the sample skewness of numeric values in the column.
/// GetColumnKurtosis(columnName): returns the sample excess kurtosis (Kurt − 3) of numeric values.
/// GetColumnMoment(columnName, order): returns the sample central moment of the given order.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness consistent;
/// GetColumnSkewness zero for symmetric data;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnKurtosis negative for uniform distribution;
/// GetColumnMoment no-throw; GetColumnMoment zero for first moment; GetColumnMoment consistent;
/// GetColumnMoment save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetColumnMoment pipeline.
/// </summary>
public class TsvR245GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR245GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR245_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateReturnsTsv()
    {
        var path = TempFile("returns.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "fund_id\tmonth\treturn_pct\tbenchmark_pct\talpha",
            "F001\t2024-01\t2.1\t1.8\t0.3",
            "F001\t2024-02\t-1.5\t-0.9\t-0.6",
            "F001\t2024-03\t3.2\t2.8\t0.4",
            "F001\t2024-04\t0.8\t1.1\t-0.3",
            "F001\t2024-05\t1.9\t1.6\t0.3",
            "F001\t2024-06\t-0.7\t0.2\t-0.9",
            "F001\t2024-07\t4.5\t3.2\t1.3",
            "F001\t2024-08\t-2.1\t-1.4\t-0.7",
            "F001\t2024-09\t1.1\t0.9\t0.2",
            "F001\t2024-10\t0.5\t0.7\t-0.2",
            "F001\t2024-11\t2.8\t2.1\t0.7",
            "F001\t2024-12\t-0.4\t0.1\t-0.5",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateSymmetricTsv()
    {
        // Perfectly symmetric data around mean
        var path = TempFile("symmetric.tsv");
        var lines = new string[]
        {
            "id\tvalue",
            "1\t-3",
            "2\t-2",
            "3\t-1",
            "4\t0",
            "5\t1",
            "6\t2",
            "7\t3",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.True(double.IsFinite(doc.GetColumnSkewness("return_pct")));
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.Equal(doc.GetColumnSkewness("return_pct"), doc.GetColumnSkewness("return_pct"));
    }

    [Fact]
    public void GetColumnSkewness_Zero_For_Symmetric()
    {
        var doc = TsvDocument.LoadFile(CreateSymmetricTsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("return_pct")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.Equal(doc.GetColumnKurtosis("alpha"), doc.GetColumnKurtosis("alpha"));
    }

    [Fact]
    public void GetColumnKurtosis_Negative_For_Uniform_Like()
    {
        // Symmetric uniform-like distribution has negative excess kurtosis
        var doc = TsvDocument.LoadFile(CreateSymmetricTsv());
        var kurt = doc.GetColumnKurtosis("value");
        Assert.True(double.IsFinite(kurt));
        Assert.True(kurt < 0); // excess kurtosis < 0 for uniform
    }

    // -------------------------------------------------------------------------
    // GetColumnMoment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMoment_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        var ex = Record.Exception(() => doc.GetColumnMoment("return_pct", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMoment_First_Moment_Zero()
    {
        // First central moment = 0 by definition
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.Equal(0.0, doc.GetColumnMoment("return_pct", 1), precision: 6);
    }

    [Fact]
    public void GetColumnMoment_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        Assert.Equal(doc.GetColumnMoment("return_pct", 2), doc.GetColumnMoment("return_pct", 2));
    }

    [Fact]
    public void GetColumnMoment_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateReturnsTsv());
        var before = doc.GetColumnMoment("return_pct", 2);
        var path = TempFile("moment_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMoment("return_pct", 2), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetColumnMoment_Pipeline()
    {
        // Environmental monitoring — daily PM2.5 air quality measurements across UK monitoring stations
        var path = TempFile("air_quality.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("station_id\tsite_name\tdate\tpm25_ug_m3\tpm10_ug_m3\tno2_ug_m3\to3_ug_m3");
        var rng = new Random(20240601);
        string[] sites = { "London_Marylebone", "Birmingham_Centre", "Manchester_Piccadilly",
                           "Leeds_Centre", "Bristol_St_Pauls", "Edinburgh_St_Leonard" };
        for (int i = 0; i < 150; i++)
        {
            var site = sites[i % 6];
            // PM2.5: log-normal, right-skewed (pollution spikes)
            double pm25 = Math.Exp(2.5 + rng.NextDouble() * 1.5);
            // PM10: similar but higher
            double pm10 = pm25 * (1.2 + rng.NextDouble() * 0.8);
            // NO2: moderate right skew
            double no2 = 15 + Math.Exp(rng.NextDouble() * 2.5);
            // O3: roughly symmetric, seasonal
            double o3 = 30 + (rng.NextDouble() - 0.5) * 40;
            lines.Add($"ST{(i % 6 + 1):D2}\t{site}\t2024-{(i % 12 + 1):D2}-{(i % 28 + 1):D2}\t{pm25:F1}\t{pm10:F1}\t{no2:F1}\t{o3:F1}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnSkewness — PM2.5 (expect positive, right-skewed)
        var pm25Skew = doc.GetColumnSkewness("pm25_ug_m3");
        Assert.True(double.IsFinite(pm25Skew));
        Assert.Equal(pm25Skew, doc.GetColumnSkewness("pm25_ug_m3")); // consistent

        // GetColumnSkewness — O3 (roughly symmetric, small skewness)
        var o3Skew = doc.GetColumnSkewness("o3_ug_m3");
        Assert.True(double.IsFinite(o3Skew));

        // GetColumnKurtosis — PM2.5 (heavy right tail, high kurtosis)
        var pm25Kurt = doc.GetColumnKurtosis("pm25_ug_m3");
        Assert.True(double.IsFinite(pm25Kurt));
        Assert.Equal(pm25Kurt, doc.GetColumnKurtosis("pm25_ug_m3")); // consistent

        // GetColumnKurtosis — NO2
        var no2Kurt = doc.GetColumnKurtosis("no2_ug_m3");
        Assert.True(double.IsFinite(no2Kurt));

        // GetColumnMoment — 2nd central moment = variance
        var pm25Var = doc.GetColumnMoment("pm25_ug_m3", 2);
        Assert.True(pm25Var > 0);
        Assert.Equal(pm25Var, doc.GetColumnMoment("pm25_ug_m3", 2)); // consistent

        // GetColumnMoment — 1st central moment = 0
        Assert.Equal(0.0, doc.GetColumnMoment("pm25_ug_m3", 1), precision: 6);

        // GetColumnMoment — 3rd central moment (related to skewness)
        var pm25M3 = doc.GetColumnMoment("pm25_ug_m3", 3);
        Assert.True(double.IsFinite(pm25M3));

        // All columns
        foreach (var col in new[] { "pm25_ug_m3", "pm10_ug_m3", "no2_ug_m3", "o3_ug_m3" })
        {
            Assert.True(double.IsFinite(doc.GetColumnSkewness(col)));
            Assert.True(double.IsFinite(doc.GetColumnKurtosis(col)));
            Assert.Equal(0.0, doc.GetColumnMoment(col, 1), precision: 6);
        }

        // SaveToFile
        var outPath = TempFile("air_quality_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(pm25Skew, loaded.GetColumnSkewness("pm25_ug_m3"), precision: 6);
        Assert.Equal(pm25Kurt, loaded.GetColumnKurtosis("pm25_ug_m3"), precision: 6);
        Assert.Equal(pm25Var, loaded.GetColumnMoment("pm25_ug_m3", 2), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean and StdDev consistency
        var mean = doc.GetColumnMean("pm25_ug_m3");
        var std = doc.GetColumnStdDev("pm25_ug_m3");
        Assert.True(mean > 0);
        Assert.True(std >= 0);
    }
}
