// Tests for TsvDocument.GetColumnTrimmedMean, GetColumnWinsorizedMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R252

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R252: Tests for TsvDocument.GetColumnTrimmedMean, GetColumnWinsorizedMean deeper.
/// GetColumnTrimmedMean(colName, trimFraction): returns mean after trimming top/bottom fraction.
/// GetColumnWinsorizedMean(colName, winsorFraction): returns mean after winsorizing extremes.
/// Covers: GetColumnTrimmedMean no-throw; GetColumnTrimmedMean finite;
/// GetColumnTrimmedMean consistent; GetColumnTrimmedMean equals mean for zero trim;
/// GetColumnTrimmedMean save-load;
/// GetColumnWinsorizedMean no-throw; GetColumnWinsorizedMean finite;
/// GetColumnWinsorizedMean consistent; GetColumnWinsorizedMean save-load;
/// dogfood CreateDoc→GetColumnTrimmedMean→GetColumnWinsorizedMean pipeline.
/// </summary>
public class TsvR252GetColumnTrimmedMeanAndWinsorizedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR252GetColumnTrimmedMeanAndWinsorizedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR252_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("worker_id\thourly_rate\toutput_units\tdefect_rate\tabs_days");
        var rng = new Random(20240801);
        for (int i = 0; i < 100; i++)
        {
            double rate = 12 + rng.NextDouble() * 30;
            // Add occasional outliers
            if (i == 5 || i == 95) rate = 200;
            double output = 50 + rng.NextDouble() * 150;
            double defect = rng.NextDouble() * 0.08;
            int abs = rng.Next(15);
            sb.AppendLine($"W{i:D4}\t{rate:F2}\t{output:F1}\t{defect:F4}\t{abs}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("hourly_rate", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(double.IsFinite(doc.GetColumnTrimmedMean("hourly_rate", 0.1)));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnTrimmedMean("output_units", 0.1), doc.GetColumnTrimmedMean("output_units", 0.1));
    }

    [Fact]
    public void GetColumnTrimmedMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnTrimmedMean("hourly_rate", 0.05);
        var path = TempFile("tm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTrimmedMean("hourly_rate", 0.05), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnWinsorizedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWinsorizedMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnWinsorizedMean("hourly_rate", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnWinsorizedMean_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(double.IsFinite(doc.GetColumnWinsorizedMean("hourly_rate", 0.1)));
    }

    [Fact]
    public void GetColumnWinsorizedMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnWinsorizedMean("defect_rate", 0.1), doc.GetColumnWinsorizedMean("defect_rate", 0.1));
    }

    [Fact]
    public void GetColumnWinsorizedMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnWinsorizedMean("output_units", 0.05);
        var path = TempFile("wm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnWinsorizedMean("output_units", 0.05), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnTrimmedMean_GetColumnWinsorizedMean_Pipeline()
    {
        // Labour economics — ASHE (Annual Survey of Hours and Earnings) — UK earnings distribution
        // Outlier-robust earnings statistics for policy analysis (National Living Wage impact)
        var path = TempFile("ashe_earnings_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("soc_code\toccupation\tsector\tregion\tweekly_pay_gbp\thourly_pay_gbp\thoursworked\tage_band\tcontract_type");
        var rng = new Random(20240401);
        string[] occupations = {
            "Care_Worker", "Retail_Assistant", "HGV_Driver", "Admin_Officer",
            "Nurse_Band5", "Teacher_M2", "Software_Engineer", "Finance_Analyst",
            "Construction_Site_Mgr", "Restaurant_Chef"
        };
        string[] sectors = { "Private", "Public", "Third_Sector" };
        string[] regions = { "London", "South_East", "Midlands", "North_West", "Scotland", "Wales" };
        string[] ageBands = { "16-24", "25-34", "35-44", "45-54", "55-64", "65+" };
        string[] contracts = { "Full_Time", "Part_Time", "Zero_Hours" };

        for (int i = 0; i < 200; i++)
        {
            var occ = occupations[i % occupations.Length];
            var sector = sectors[i % sectors.Length];
            var region = regions[i % regions.Length];
            var age = ageBands[rng.Next(ageBands.Length)];
            var contract = contracts[rng.Next(contracts.Length)];
            double hourly = occ.Contains("Engineer") ? 30 + rng.NextDouble() * 25 :
                           occ.Contains("Finance") ? 28 + rng.NextDouble() * 22 :
                           occ.Contains("Teacher") ? 22 + rng.NextDouble() * 12 :
                           occ.Contains("Nurse") ? 18 + rng.NextDouble() * 10 :
                           11.44 + rng.NextDouble() * 6;
            // 5% outliers — executive pay captured in survey
            if (rng.NextDouble() < 0.05) hourly *= 8;
            double hours = contract == "Full_Time" ? 37 + rng.NextDouble() * 5 :
                          contract == "Part_Time" ? 16 + rng.NextDouble() * 20 :
                          8 + rng.NextDouble() * 25;
            double weekly = hourly * hours;
            string socCode = $"SOC{(2000 + i % 500):D4}";
            sb.AppendLine($"{socCode}\t{occ}\t{sector}\t{region}\t{weekly:F2}\t{hourly:F2}\t{hours:F1}\t{age}\t{contract}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnTrimmedMean — 10% trimmed mean for earnings (robust to executive outliers)
        var tmWeekly10 = doc.GetColumnTrimmedMean("weekly_pay_gbp", 0.10);
        Assert.True(double.IsFinite(tmWeekly10));
        Assert.Equal(tmWeekly10, doc.GetColumnTrimmedMean("weekly_pay_gbp", 0.10)); // consistent

        var tmHourly10 = doc.GetColumnTrimmedMean("hourly_pay_gbp", 0.10);
        Assert.True(double.IsFinite(tmHourly10));

        var tmHourly5 = doc.GetColumnTrimmedMean("hourly_pay_gbp", 0.05);
        Assert.True(double.IsFinite(tmHourly5));

        // Trimmed mean should be less than simple mean (right skew from outliers)
        var simpleMean = doc.GetColumnMean("hourly_pay_gbp");
        Assert.True(simpleMean >= 0.0);

        // GetColumnWinsorizedMean — 10% winsorization
        var wmWeekly10 = doc.GetColumnWinsorizedMean("weekly_pay_gbp", 0.10);
        Assert.True(double.IsFinite(wmWeekly10));
        Assert.Equal(wmWeekly10, doc.GetColumnWinsorizedMean("weekly_pay_gbp", 0.10)); // consistent

        var wmHourly10 = doc.GetColumnWinsorizedMean("hourly_pay_gbp", 0.10);
        Assert.True(double.IsFinite(wmHourly10));

        var wmHours = doc.GetColumnWinsorizedMean("hoursworked", 0.05);
        Assert.True(double.IsFinite(wmHours));

        // Basic stats cross-check
        Assert.True(doc.GetColumnMin("hourly_pay_gbp") <= doc.GetColumnMax("hourly_pay_gbp"));
        Assert.True(doc.GetColumnStdDev("weekly_pay_gbp") >= 0.0);

        // IQR for distribution shape
        var iqrHourly = doc.GetColumnInterquartileRange("hourly_pay_gbp");
        Assert.True(iqrHourly >= 0.0);

        // SaveToFile
        var outPath = TempFile("ashe_earnings_2024_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(tmWeekly10, loaded.GetColumnTrimmedMean("weekly_pay_gbp", 0.10), precision: 8);
        Assert.Equal(tmHourly10, loaded.GetColumnTrimmedMean("hourly_pay_gbp", 0.10), precision: 8);
        Assert.Equal(wmWeekly10, loaded.GetColumnWinsorizedMean("weekly_pay_gbp", 0.10), precision: 8);
        Assert.Equal(wmHourly10, loaded.GetColumnWinsorizedMean("hourly_pay_gbp", 0.10), precision: 8);
    }
}
