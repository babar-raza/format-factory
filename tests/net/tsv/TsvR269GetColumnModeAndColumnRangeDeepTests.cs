// Tests for TsvDocument.GetColumnMode, GetColumnRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R269

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R269: Tests for TsvDocument.GetColumnMode, GetColumnRange deeper.
/// GetColumnMode(colName): returns the most frequently occurring numeric value in the column (mode).
/// GetColumnRange(colName): returns the range (max - min) of numeric values in the column; ≥ 0.
/// Covers: GetColumnMode no-throw; GetColumnMode consistent; GetColumnMode save-load;
/// GetColumnRange no-throw; GetColumnRange non-negative; GetColumnRange zero for uniform;
/// GetColumnRange consistent; GetColumnRange save-load;
/// GetColumnRange equals GetColumnMax minus GetColumnMin;
/// dogfood OFGEM smart meter energy consumption data pipeline.
/// </summary>
public class TsvR269GetColumnModeAndColumnRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR269GetColumnModeAndColumnRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR269_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tvalue\tcategory_code");
        // value: 10 appears 5x, 20 appears 3x, 30 appears 2x
        for (int i = 0; i < 5; i++) sb.AppendLine($"R{i:D2}\t10\t1");
        for (int i = 5; i < 8; i++) sb.AppendLine($"R{i:D2}\t20\t2");
        for (int i = 8; i < 10; i++) sb.AppendLine($"R{i:D2}\t30\t3");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tmeasure");
        for (int i = 0; i < 30; i++) sb.AppendLine($"R{i:D2}\t50");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMode("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMode("value"), doc.GetColumnMode("value"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMode("value");
        var path = TempFile("mode_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMode_Uniform_EqualsSingleValue()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(50.0, doc.GetColumnMode("measure"), precision: 3);
    }

    // -------------------------------------------------------------------------
    // GetColumnRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRange_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnRange("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRange_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnRange("value") >= 0.0);
    }

    [Fact]
    public void GetColumnRange_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnRange("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnRange_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnRange("value"), doc.GetColumnRange("value"));
    }

    [Fact]
    public void GetColumnRange_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnRange("value");
        var path = TempFile("range_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRange("value"), precision: 6);
    }

    [Fact]
    public void GetColumnRange_EqualsMaxMinusMin()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var range = doc.GetColumnRange("value");
        var max = doc.GetColumnMax("value");
        var min = doc.GetColumnMin("value");
        Assert.Equal(max - min, range, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnRange_Pipeline()
    {
        // Energy — Ofgem/BEIS: Smart Meter Energy Consumption Dataset 2024
        // Half-hourly electricity consumption data from smart meter rollout
        // Mode identifies the most common consumption band; range detects high-variation households

        var path = TempFile("ofgem_smart_meter_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("meter_id\tsettlement_date\thalf_hour_period\tkwh_consumed\tprofile_class\ttariff_type\tregion_code");

        var rng = new Random(20241001);
        string[] profileClasses = { "PC1", "PC2", "PC1", "PC1", "PC2", "PC3", "PC4" };
        string[] tariffTypes = { "Standard", "Standard", "Standard", "Economy7", "Smart_Variable", "Fixed_Rate" };
        string[] regions = { "South_East", "London", "Midlands", "North_West", "Yorkshire",
                              "Eastern", "Southern", "South_West", "North_East" };
        // Common consumption bands: 0.1 kWh appears frequently (base load)
        double[] commonBands = { 0.1, 0.1, 0.1, 0.2, 0.2, 0.3, 0.5, 0.8, 1.2, 2.5 };

        for (int i = 0; i < 350; i++)
        {
            string meter = $"MPR{1100000000 + i}";
            string date = $"2024-{(rng.Next(1, 12) + 1):D2}-{(rng.Next(1, 28) + 1):D2}";
            int period = rng.Next(1, 49);
            double kwh = i < 300 ? commonBands[rng.Next(commonBands.Length)] : rng.NextDouble() * 5.0; // 300 normal, 50 variable
            string pc = profileClasses[rng.Next(profileClasses.Length)];
            string tariff = tariffTypes[rng.Next(tariffTypes.Length)];
            string region = regions[rng.Next(regions.Length)];
            sb.AppendLine($"{meter}\t{date}\t{period}\t{kwh:F2}\t{pc}\t{tariff}\t{region}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(350, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnMode for kwh_consumed — 0.1 should dominate
        var mode = doc.GetColumnMode("kwh_consumed");
        Assert.Equal(mode, doc.GetColumnMode("kwh_consumed")); // consistent

        // GetColumnRange for kwh_consumed
        var range = doc.GetColumnRange("kwh_consumed");
        Assert.True(range >= 0.0);
        Assert.True(range > 0.0); // we have variable consumption
        Assert.Equal(range, doc.GetColumnRange("kwh_consumed")); // consistent

        // Range equals max minus min
        var maxKwh = doc.GetColumnMax("kwh_consumed");
        var minKwh = doc.GetColumnMin("kwh_consumed");
        Assert.Equal(maxKwh - minKwh, range, precision: 6);
        Assert.True(maxKwh > minKwh);

        // GetColumnRange for half_hour_period (1-48)
        var periodRange = doc.GetColumnRange("half_hour_period");
        Assert.True(periodRange >= 0.0);
        Assert.Equal(periodRange, doc.GetColumnRange("half_hour_period")); // consistent

        // Mode for half_hour_period
        var periodMode = doc.GetColumnMode("half_hour_period");
        Assert.Equal(periodMode, doc.GetColumnMode("half_hour_period")); // consistent

        // SaveToFile
        var outPath = TempFile("ofgem_sm_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(mode, loaded.GetColumnMode("kwh_consumed"), precision: 6);
        Assert.Equal(range, loaded.GetColumnRange("kwh_consumed"), precision: 6);
        Assert.Equal(periodRange, loaded.GetColumnRange("half_hour_period"), precision: 6);
    }
}
