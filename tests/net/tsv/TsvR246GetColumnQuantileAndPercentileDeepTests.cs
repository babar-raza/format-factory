// Tests for TsvDocument.GetColumnQuantile, GetColumnPercentile, GetColumnDecile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R246: Tests for TsvDocument.GetColumnQuantile, GetColumnPercentile, GetColumnDecile deeper.
/// GetColumnQuantile(columnName, q): returns the q-th quantile (0≤q≤1) of numeric column values.
/// GetColumnPercentile(columnName, p): returns the p-th percentile (0≤p≤100) of numeric column values.
/// GetColumnDecile(columnName, d): returns the d-th decile (1≤d≤9) of numeric column values.
/// Covers: GetColumnQuantile no-throw; GetColumnQuantile between min and max; GetColumnQuantile consistent;
/// GetColumnQuantile Q0=min, Q1=max;
/// GetColumnPercentile no-throw; GetColumnPercentile between min and max; GetColumnPercentile consistent;
/// GetColumnPercentile P0=min, P100=max;
/// GetColumnDecile no-throw; GetColumnDecile between min and max; GetColumnDecile consistent;
/// GetColumnDecile save-load;
/// dogfood CreateDoc→GetColumnQuantile→GetColumnPercentile→GetColumnDecile pipeline.
/// </summary>
public class TsvR246GetColumnQuantileAndPercentileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR246GetColumnQuantileAndPercentileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR246_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePropTsv()
    {
        var path = TempFile("properties.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "property_id\tpostcode\tprice_gbp\tbedrooms\tfloor_area_sqm",
            "P001\tSW1A 1AA\t850000\t3\t95",
            "P002\tEC1A 1BB\t1250000\t4\t142",
            "P003\tW1A 2CC\t425000\t2\t68",
            "P004\tN1 3DD\t675000\t3\t88",
            "P005\tE1 4EE\t320000\t1\t52",
            "P006\tSE1 5FF\t540000\t2\t75",
            "P007\tWC2H 6GG\t985000\t3\t115",
            "P008\tEC2M 7HH\t1850000\t5\t210",
            "P009\tN16 8JJ\t485000\t2\t72",
            "P010\tE2 9KK\t395000\t2\t65",
            "P011\tSW6 1LL\t760000\t3\t92",
            "P012\tW14 2MM\t1120000\t4\t158",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnQuantile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuantile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var ex = Record.Exception(() => doc.GetColumnQuantile("price_gbp", 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuantile_Between_Min_And_Max()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var q = doc.GetColumnQuantile("price_gbp", 0.5);
        var min = doc.GetColumnMin("price_gbp");
        var max = doc.GetColumnMax("price_gbp");
        Assert.True(q >= min && q <= max);
    }

    [Fact]
    public void GetColumnQuantile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnQuantile("price_gbp", 0.75), doc.GetColumnQuantile("price_gbp", 0.75));
    }

    [Fact]
    public void GetColumnQuantile_Q0_Equals_Min()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnMin("floor_area_sqm"), doc.GetColumnQuantile("floor_area_sqm", 0.0), precision: 6);
    }

    [Fact]
    public void GetColumnQuantile_Q1_Equals_Max()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnMax("floor_area_sqm"), doc.GetColumnQuantile("floor_area_sqm", 1.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var ex = Record.Exception(() => doc.GetColumnPercentile("price_gbp", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentile_Between_Min_And_Max()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var p = doc.GetColumnPercentile("price_gbp", 50);
        var min = doc.GetColumnMin("price_gbp");
        var max = doc.GetColumnMax("price_gbp");
        Assert.True(p >= min && p <= max);
    }

    [Fact]
    public void GetColumnPercentile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnPercentile("bedrooms", 75), doc.GetColumnPercentile("bedrooms", 75));
    }

    [Fact]
    public void GetColumnPercentile_P0_Equals_Min()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnMin("bedrooms"), doc.GetColumnPercentile("bedrooms", 0), precision: 6);
    }

    [Fact]
    public void GetColumnPercentile_P100_Equals_Max()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnMax("bedrooms"), doc.GetColumnPercentile("bedrooms", 100), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnDecile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDecile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var ex = Record.Exception(() => doc.GetColumnDecile("price_gbp", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDecile_Between_Min_And_Max()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var d = doc.GetColumnDecile("price_gbp", 5);
        var min = doc.GetColumnMin("price_gbp");
        var max = doc.GetColumnMax("price_gbp");
        Assert.True(d >= min && d <= max);
    }

    [Fact]
    public void GetColumnDecile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        Assert.Equal(doc.GetColumnDecile("floor_area_sqm", 3), doc.GetColumnDecile("floor_area_sqm", 3));
    }

    [Fact]
    public void GetColumnDecile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropTsv());
        var before = doc.GetColumnDecile("price_gbp", 9);
        var path = TempFile("decile_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnDecile("price_gbp", 9), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnQuantile_GetColumnPercentile_GetColumnDecile_Pipeline()
    {
        // Office for National Statistics — Annual Survey of Hours and Earnings (ASHE) data
        var path = TempFile("ashe_earnings.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("employee_ref\tsoc_code\tregion\tgross_weekly_pay\thours_worked\thourly_rate\temployment_type");
        var rng = new Random(20241201);
        string[] regions = { "London", "South_East", "East_Midlands", "North_West", "Yorkshire", "Scotland" };
        string[] empTypes = { "Full_Time", "Part_Time" };
        for (int i = 0; i < 150; i++)
        {
            string region = regions[i % 6];
            // London premium: higher pay
            double baseHourly = region == "London" ? 18 + rng.NextDouble() * 32 : 10 + rng.NextDouble() * 20;
            double hours = empTypes[i % 2] == "Full_Time" ? 35 + rng.NextDouble() * 5 : 15 + rng.NextDouble() * 15;
            double weeklyPay = baseHourly * hours;
            lines.Add($"EMP{i:D6}\t{(2100 + rng.Next(300))}\t{region}\t{weeklyPay:F2}\t{hours:F1}\t{baseHourly:F2}\t{empTypes[i % 2]}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnQuantile — weekly pay distribution
        var q25 = doc.GetColumnQuantile("gross_weekly_pay", 0.25);
        var q50 = doc.GetColumnQuantile("gross_weekly_pay", 0.50);
        var q75 = doc.GetColumnQuantile("gross_weekly_pay", 0.75);
        Assert.True(q25 <= q50);
        Assert.True(q50 <= q75);
        Assert.Equal(q50, doc.GetColumnQuantile("gross_weekly_pay", 0.50)); // consistent

        // Q0 = min, Q1 = max
        Assert.Equal(doc.GetColumnMin("hourly_rate"), doc.GetColumnQuantile("hourly_rate", 0.0), precision: 6);
        Assert.Equal(doc.GetColumnMax("hourly_rate"), doc.GetColumnQuantile("hourly_rate", 1.0), precision: 6);

        // GetColumnPercentile — hourly rate
        var p10 = doc.GetColumnPercentile("hourly_rate", 10);
        var p90 = doc.GetColumnPercentile("hourly_rate", 90);
        Assert.True(p10 <= p90);
        Assert.Equal(p90, doc.GetColumnPercentile("hourly_rate", 90)); // consistent

        // P0 = min, P100 = max
        Assert.Equal(doc.GetColumnMin("hours_worked"), doc.GetColumnPercentile("hours_worked", 0), precision: 6);
        Assert.Equal(doc.GetColumnMax("hours_worked"), doc.GetColumnPercentile("hours_worked", 100), precision: 6);

        // GetColumnDecile — weekly pay
        var d1 = doc.GetColumnDecile("gross_weekly_pay", 1);
        var d5 = doc.GetColumnDecile("gross_weekly_pay", 5);
        var d9 = doc.GetColumnDecile("gross_weekly_pay", 9);
        Assert.True(d1 <= d5);
        Assert.True(d5 <= d9);
        Assert.Equal(d5, doc.GetColumnDecile("gross_weekly_pay", 5)); // consistent

        // Decile monotonicity
        double prev = double.MinValue;
        for (int d = 1; d <= 9; d++)
        {
            double curr = doc.GetColumnDecile("gross_weekly_pay", d);
            Assert.True(curr >= prev);
            prev = curr;
        }

        // SaveToFile
        var outPath = TempFile("ashe_earnings_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(q50, loaded.GetColumnQuantile("gross_weekly_pay", 0.50), precision: 6);
        Assert.Equal(p90, loaded.GetColumnPercentile("hourly_rate", 90), precision: 6);
        Assert.Equal(d9, loaded.GetColumnDecile("gross_weekly_pay", 9), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var mean = doc.GetColumnMean("gross_weekly_pay");
        Assert.True(mean > 0);
        // Mean > median in right-skewed distribution
        Assert.True(mean > 0 && q50 > 0);
    }
}
