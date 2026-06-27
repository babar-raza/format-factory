// Tests for CsvDocument.GetCumulativeSum, GetMovingAverage, GetPercentileRank deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R233

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R233: Tests for CsvDocument.GetCumulativeSum, GetMovingAverage, GetPercentileRank deeper.
/// GetCumulativeSum(columnName): returns an array of cumulative sums for the column.
/// GetMovingAverage(columnName, windowSize): returns moving averages with the given window.
/// GetPercentileRank(columnName, value): returns the percentile rank (0-100) of the given value.
/// Covers: GetCumulativeSum no-throw; GetCumulativeSum count equals row count; GetCumulativeSum consistent;
/// GetCumulativeSum last equals column sum; GetCumulativeSum save-load;
/// GetMovingAverage no-throw; GetMovingAverage count leq row count; GetMovingAverage consistent;
/// GetMovingAverage save-load;
/// GetPercentileRank no-throw; GetPercentileRank in range; GetPercentileRank consistent;
/// GetPercentileRank 100 for max; GetPercentileRank save-load;
/// dogfood CreateDoc→GetCumulativeSum→GetMovingAverage→GetPercentileRank→SaveToFile pipeline.
/// </summary>
public class CsvR233GetCumulativeSumAndMovingAverageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR233GetCumulativeSumAndMovingAverageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR233_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStockCsv()
    {
        var path = TempFile("stock.csv");
        File.WriteAllText(path,
            "date,open,high,low,close,volume\n" +
            "2026-01-02,185.20,188.50,184.80,187.30,42800000\n" +
            "2026-01-05,187.30,190.20,186.80,189.50,38500000\n" +
            "2026-01-06,189.50,191.80,188.20,190.80,41200000\n" +
            "2026-01-07,190.80,193.50,190.10,192.40,39800000\n" +
            "2026-01-08,192.40,194.20,191.20,193.60,36200000\n" +
            "2026-01-09,193.60,195.80,192.80,195.10,44500000\n" +
            "2026-01-12,195.10,197.50,194.20,196.80,48200000\n" +
            "2026-01-13,196.80,198.20,195.50,197.50,35800000\n" +
            "2026-01-14,197.50,200.10,196.80,199.20,52400000\n" +
            "2026-01-15,199.20,201.50,198.40,200.80,46800000\n" +
            "2026-01-16,200.80,202.80,199.50,202.10,40200000\n" +
            "2026-01-19,202.10,204.50,201.20,203.80,38500000\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCumulativeSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCumulativeSum_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetCumulativeSum("volume"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCumulativeSum_Count_EqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(doc.GetRowCount(), doc.GetCumulativeSum("volume").Length);
    }

    [Fact]
    public void GetCumulativeSum_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var c1 = doc.GetCumulativeSum("close");
        var c2 = doc.GetCumulativeSum("close");
        Assert.Equal(c1.Length, c2.Length);
        for (int i = 0; i < c1.Length; i++)
            Assert.Equal(c1[i], c2[i]);
    }

    [Fact]
    public void GetCumulativeSum_LastEqualsColumnSum()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var cumSum = doc.GetCumulativeSum("volume");
        var colSum = doc.GetColumnSum("volume");
        Assert.Equal(colSum, cumSum[cumSum.Length - 1], precision: 6);
    }

    [Fact]
    public void GetCumulativeSum_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetCumulativeSum("close");
        var path = TempFile("cs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetCumulativeSum("close");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMovingAverage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMovingAverage_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetMovingAverage("close", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMovingAverage_Count_LeqRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.True(doc.GetMovingAverage("close", 5).Length <= doc.GetRowCount());
    }

    [Fact]
    public void GetMovingAverage_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var m1 = doc.GetMovingAverage("volume", 3);
        var m2 = doc.GetMovingAverage("volume", 3);
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void GetMovingAverage_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetMovingAverage("close", 5);
        var path = TempFile("ma_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetMovingAverage("close", 5);
        Assert.Equal(before.Length, after.Length);
    }

    // -------------------------------------------------------------------------
    // GetPercentileRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPercentileRank_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetPercentileRank("close", 195.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPercentileRank_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var rank = doc.GetPercentileRank("close", 195.0);
        Assert.True(rank >= 0.0);
        Assert.True(rank <= 100.0);
    }

    [Fact]
    public void GetPercentileRank_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(doc.GetPercentileRank("volume", 40000000), doc.GetPercentileRank("volume", 40000000));
    }

    [Fact]
    public void GetPercentileRank_100_ForMax()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var maxVal = doc.GetColumnMax("close");
        var rank = doc.GetPercentileRank("close", maxVal);
        Assert.True(rank >= 99.0);
    }

    [Fact]
    public void GetPercentileRank_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetPercentileRank("close", 192.0);
        var path = TempFile("pr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPercentileRank("close", 192.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCumulativeSum_GetMovingAverage_GetPercentileRank_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_sovereign_debt.csv");
        File.WriteAllText(path,
            "year,country_a_debt_gdp,country_b_debt_gdp,country_c_debt_gdp,avg_yield,primary_balance,issuance_bn\n" +
            "2015,84.2,48.5,122.8,2.85,0.5,285.4\n" +
            "2016,86.5,50.2,125.1,2.42,0.2,310.8\n" +
            "2017,88.1,51.8,124.5,2.28,0.8,298.2\n" +
            "2018,89.4,52.5,123.8,2.95,1.2,285.6\n" +
            "2019,90.8,53.2,125.2,2.08,0.9,302.4\n" +
            "2020,105.2,68.5,138.4,1.12,-8.5,485.2\n" +
            "2021,102.8,65.2,134.8,1.45,-4.8,425.8\n" +
            "2022,98.5,60.8,130.2,3.58,-1.2,368.4\n" +
            "2023,95.2,57.4,127.8,4.12,0.8,342.5\n" +
            "2024,93.4,55.8,126.5,4.48,1.2,320.2\n" +
            "2025,91.8,54.2,125.2,4.25,1.5,308.8\n" +
            "2026,90.2,52.8,124.8,4.02,1.8,295.4\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetCumulativeSum — issuance_bn
        var cumIssuance = doc.GetCumulativeSum("issuance_bn");
        Assert.Equal(12, cumIssuance.Length);
        for (int i = 1; i < cumIssuance.Length; i++)
            Assert.True(cumIssuance[i] >= cumIssuance[i - 1]); // monotone
        Assert.Equal(doc.GetColumnSum("issuance_bn"), cumIssuance[11], precision: 6);

        // GetCumulativeSum — avg_yield
        var cumYield = doc.GetCumulativeSum("avg_yield");
        Assert.Equal(12, cumYield.Length);

        // Consistent
        var cumIssuance2 = doc.GetCumulativeSum("issuance_bn");
        for (int i = 0; i < cumIssuance.Length; i++)
            Assert.Equal(cumIssuance[i], cumIssuance2[i], precision: 6);

        // GetMovingAverage — 3-year moving average of debt/GDP
        var ma3A = doc.GetMovingAverage("country_a_debt_gdp", 3);
        Assert.True(ma3A.Length <= 12);
        Assert.True(ma3A.Length > 0);

        var ma3B = doc.GetMovingAverage("country_b_debt_gdp", 3);
        Assert.True(ma3B.Length <= 12);

        // 5-year MA of issuance
        var ma5Issue = doc.GetMovingAverage("issuance_bn", 5);
        Assert.True(ma5Issue.Length <= 12);

        // GetPercentileRank — rank of 2020 crisis year issuance
        var rank2020 = doc.GetPercentileRank("issuance_bn", 485.2);
        Assert.True(rank2020 >= 0.0);
        Assert.True(rank2020 <= 100.0);
        Assert.True(rank2020 >= 99.0); // highest value

        // Rank of minimum issuance
        var minIssue = doc.GetColumnMin("issuance_bn");
        var rankMin = doc.GetPercentileRank("issuance_bn", minIssue);
        Assert.True(rankMin >= 0.0);

        // SaveToFile
        var out1 = TempFile("dogfood_debt_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        var loadedCum = loaded.GetCumulativeSum("issuance_bn");
        Assert.Equal(cumIssuance.Length, loadedCum.Length);
        for (int i = 0; i < cumIssuance.Length; i++)
            Assert.Equal(cumIssuance[i], loadedCum[i], precision: 6);

        // AddRow on loaded
        loaded.AddRow(new[] { "2027", "88.8", "51.5", "124.2", "3.85", "2.1", "285.0" });
        Assert.Equal(13, loaded.GetRowCount());
        var updatedCum = loaded.GetCumulativeSum("issuance_bn");
        Assert.Equal(13, updatedCum.Length);
        Assert.True(updatedCum[12] > cumIssuance[11]); // larger total after adding row

        // Final save
        var out2 = TempFile("dogfood_debt_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.Equal(13, loaded2.GetCumulativeSum("issuance_bn").Length);
        Assert.True(loaded2.GetMovingAverage("avg_yield", 3).Length <= 13);
        Assert.True(loaded2.GetPercentileRank("issuance_bn", 300.0) >= 0.0);
    }
}
