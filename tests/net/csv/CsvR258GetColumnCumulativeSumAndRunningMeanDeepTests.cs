// Tests for CsvDocument.GetColumnCumulativeSum, GetColumnRunningMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R258

using System;
using System.IO;
using System.Text;
using System.Linq;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R258: Tests for CsvDocument.GetColumnCumulativeSum, GetColumnRunningMean deeper.
/// GetColumnCumulativeSum(colName): returns an array of running totals for a numeric column.
/// GetColumnRunningMean(colName): returns an array of running means for a numeric column.
/// Covers: GetColumnCumulativeSum no-throw; GetColumnCumulativeSum non-null;
/// GetColumnCumulativeSum length equals RowCount; GetColumnCumulativeSum last equals column sum;
/// GetColumnCumulativeSum monotone for non-negative; GetColumnCumulativeSum consistent;
/// GetColumnCumulativeSum save-load;
/// GetColumnRunningMean no-throw; GetColumnRunningMean non-null;
/// GetColumnRunningMean length equals RowCount; GetColumnRunningMean last equals column mean;
/// GetColumnRunningMean consistent; GetColumnRunningMean save-load;
/// dogfood CreateDoc→GetColumnCumulativeSum→GetColumnRunningMean pipeline.
/// </summary>
public class CsvR258GetColumnCumulativeSumAndRunningMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR258GetColumnCumulativeSumAndRunningMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR258_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("week,sales_units,revenue_gbp,returns,net_revenue");
        var rng = new Random(20240901);
        for (int i = 0; i < 52; i++)
        {
            int units = 500 + rng.Next(800);
            double rev = units * (18 + rng.NextDouble() * 12);
            int returns = (int)(units * 0.02);
            double netRev = rev * (1 - 0.02);
            sb.AppendLine($"W{i + 1:D2},{units},{rev:F2},{returns},{netRev:F2}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCumulativeSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCumulativeSum_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCumulativeSum("revenue_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCumulativeSum_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnCumulativeSum("revenue_gbp"));
    }

    [Fact]
    public void GetColumnCumulativeSum_LengthEqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnCumulativeSum("revenue_gbp").Length);
    }

    [Fact]
    public void GetColumnCumulativeSum_LastEqualsColumnSum()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var cs = doc.GetColumnCumulativeSum("revenue_gbp");
        Assert.Equal(doc.GetColumnSum("revenue_gbp"), cs[cs.Length - 1], precision: 4);
    }

    [Fact]
    public void GetColumnCumulativeSum_MonotoneForNonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var cs = doc.GetColumnCumulativeSum("sales_units");
        for (int i = 1; i < cs.Length; i++)
            Assert.True(cs[i] >= cs[i - 1]);
    }

    [Fact]
    public void GetColumnCumulativeSum_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var cs1 = doc.GetColumnCumulativeSum("net_revenue");
        var cs2 = doc.GetColumnCumulativeSum("net_revenue");
        Assert.Equal(cs1.Length, cs2.Length);
        for (int i = 0; i < cs1.Length; i++)
            Assert.Equal(cs1[i], cs2[i]);
    }

    [Fact]
    public void GetColumnCumulativeSum_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCumulativeSum("revenue_gbp");
        var path = TempFile("cs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnCumulativeSum("revenue_gbp");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRunningMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRunningMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRunningMean("revenue_gbp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRunningMean_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnRunningMean("revenue_gbp"));
    }

    [Fact]
    public void GetColumnRunningMean_LengthEqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRunningMean("revenue_gbp").Length);
    }

    [Fact]
    public void GetColumnRunningMean_LastEqualsColumnMean()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var rm = doc.GetColumnRunningMean("revenue_gbp");
        Assert.Equal(doc.GetColumnMean("revenue_gbp"), rm[rm.Length - 1], precision: 4);
    }

    [Fact]
    public void GetColumnRunningMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var rm1 = doc.GetColumnRunningMean("sales_units");
        var rm2 = doc.GetColumnRunningMean("sales_units");
        Assert.Equal(rm1.Length, rm2.Length);
        for (int i = 0; i < rm1.Length; i++)
            Assert.Equal(rm1[i], rm2[i]);
    }

    [Fact]
    public void GetColumnRunningMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRunningMean("net_revenue");
        var path = TempFile("rm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnRunningMean("net_revenue");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCumulativeSum_GetColumnRunningMean_Pipeline()
    {
        // Supply chain — ONS UK Supply Chain Resilience Monitor
        // Weekly critical goods throughput at UK ports: cumulative volume and rolling average
        var path = TempFile("ons_supply_chain.csv");
        var sb = new StringBuilder();
        sb.AppendLine("week_ending,pharmaceutical_tonnes,semiconductor_units,food_grade_containers,energy_LNG_TJ,vehicle_parts_pallets,total_trade_value_gbm");
        var rng = new Random(20241001);

        double[] pharmaBase = { 8400, 8200, 7900, 8600, 8800, 9100, 8750, 8900, 9200, 8600, 9400, 9800 };
        double[] semiBase = { 125000, 118000, 122000, 130000, 128000, 135000, 129000, 131000, 138000, 133000, 140000, 145000 };

        for (int i = 0; i < 52; i++)
        {
            // Seasonal patterns
            double seasonal = 1 + 0.08 * Math.Sin(2 * Math.PI * i / 52.0);
            double pharma = pharmaBase[i % 12] * seasonal * (0.95 + rng.NextDouble() * 0.1);
            double semi = semiBase[i % 12] * seasonal * (0.92 + rng.NextDouble() * 0.16);
            // Q4 disruption (weeks 40-52)
            if (i >= 40) { pharma *= 1.12; semi *= 0.88; }
            int food = 4800 + rng.Next(1200);
            double lng = 28 + rng.NextDouble() * 18;
            int vehicles = 12000 + rng.Next(5000);
            double tradeValue = (pharma * 0.85 + semi * 0.002 + food * 12000 + lng * 450000 + vehicles * 850) / 1e6;
            string weekEnd = $"2024-{(i / 4 + 1):D2}-{(i % 4 * 7 + 7):D2}";
            sb.AppendLine($"{weekEnd},{pharma:F0},{semi:F0},{food},{lng:F1},{vehicles},{tradeValue:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(52, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnCumulativeSum — annual throughput build-up
        var csPharma = doc.GetColumnCumulativeSum("pharmaceutical_tonnes");
        Assert.NotNull(csPharma);
        Assert.Equal(52, csPharma.Length);
        Assert.Equal(doc.GetColumnSum("pharmaceutical_tonnes"), csPharma[51], precision: 4);

        // Non-decreasing (all positive)
        for (int i = 1; i < csPharma.Length; i++)
            Assert.True(csPharma[i] >= csPharma[i - 1]);

        var csTrade = doc.GetColumnCumulativeSum("total_trade_value_gbm");
        Assert.Equal(52, csTrade.Length);
        Assert.Equal(doc.GetColumnSum("total_trade_value_gbm"), csTrade[51], precision: 4);

        // Consistent
        var csPharma2 = doc.GetColumnCumulativeSum("pharmaceutical_tonnes");
        for (int i = 0; i < csPharma.Length; i++)
            Assert.Equal(csPharma[i], csPharma2[i]);

        // GetColumnRunningMean — rolling averages
        var rmSemi = doc.GetColumnRunningMean("semiconductor_units");
        Assert.NotNull(rmSemi);
        Assert.Equal(52, rmSemi.Length);
        Assert.Equal(doc.GetColumnMean("semiconductor_units"), rmSemi[51], precision: 4);

        // Running mean with more data should be positive
        Assert.True(rmSemi[0] > 0);
        Assert.True(rmSemi[51] > 0);

        var rmPharma = doc.GetColumnRunningMean("pharmaceutical_tonnes");
        Assert.Equal(52, rmPharma.Length);
        Assert.Equal(doc.GetColumnMean("pharmaceutical_tonnes"), rmPharma[51], precision: 4);

        // Consistent
        var rmSemi2 = doc.GetColumnRunningMean("semiconductor_units");
        for (int i = 0; i < rmSemi.Length; i++)
            Assert.Equal(rmSemi[i], rmSemi2[i]);

        // Basic stats
        Assert.True(doc.GetColumnSum("pharmaceutical_tonnes") > 0);
        Assert.True(doc.GetColumnMean("semiconductor_units") > 0);
        Assert.True(doc.GetColumnMin("food_grade_containers") <= doc.GetColumnMax("food_grade_containers"));

        // SaveToFile
        var outPath = TempFile("ons_supply_chain_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(52, loaded.RowCount);
        var loadedCs = loaded.GetColumnCumulativeSum("pharmaceutical_tonnes");
        Assert.Equal(csPharma.Length, loadedCs.Length);
        for (int i = 0; i < csPharma.Length; i++)
            Assert.Equal(csPharma[i], loadedCs[i], precision: 4);
        var loadedRm = loaded.GetColumnRunningMean("semiconductor_units");
        Assert.Equal(rmSemi.Length, loadedRm.Length);
        Assert.Equal(rmSemi[51], loadedRm[51], precision: 4);
    }
}
