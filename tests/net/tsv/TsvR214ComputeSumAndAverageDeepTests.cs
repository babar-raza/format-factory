// Tests for TsvDocument.ComputeSum, ComputeAverage, GetRowsWhere deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R214

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R214: Tests for TsvDocument.ComputeSum, ComputeAverage, GetRowsWhere deeper.
/// ComputeSum(colName): returns the sum of numeric values in a column.
/// ComputeAverage(colName): returns the arithmetic mean of numeric values in a column.
/// GetRowsWhere(colName, value): returns a new TsvDocument with rows matching the filter.
/// Covers: ComputeSum no-throw; ComputeSum positive for positive data; ComputeSum correct;
/// ComputeSum consistent; ComputeSum save-load; ComputeSum after AddRow increases;
/// ComputeAverage no-throw; ComputeAverage positive; ComputeAverage correct;
/// ComputeAverage in range [min, max]; ComputeAverage consistent; ComputeAverage save-load;
/// GetRowsWhere non-null; GetRowsWhere no-throw; GetRowsWhere correct count;
/// GetRowsWhere Engineering three rows; GetRowsWhere no-match empty;
/// GetRowsWhere consistent; GetRowsWhere save-load; GetRowsWhere total rows sum;
/// GetRowsWhere then ComputeSum; GetRowsWhere then ExportToHtml no-throw;
/// dogfood LoadFile→ComputeSum→ComputeAverage→GetRowsWhere→SaveToFile pipeline.
/// </summary>
public class TsvR214ComputeSumAndAverageDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR214ComputeSumAndAverageDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR214_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSalesTsv()
    {
        var path = TempFile("sales.tsv");
        var content =
            "Rep\tRegion\tQ1\tQ2\tQ3\tQ4\n" +
            "Alice\tNorth\t120000\t135000\t128000\t145000\n" +
            "Bob\tSouth\t95000\t102000\t98000\t110000\n" +
            "Carol\tNorth\t145000\t158000\t151000\t170000\n" +
            "Dave\tEast\t88000\t92000\t90000\t98000\n" +
            "Eve\tNorth\t132000\t140000\t136000\t155000\n" +
            "Frank\tSouth\t79000\t85000\t82000\t91000\n" +
            "Grace\tEast\t115000\t122000\t118000\t130000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ComputeSum
    // -------------------------------------------------------------------------

    [Fact]
    public void ComputeSum_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.ComputeSum("Q1"));
        Assert.Null(ex);
    }

    [Fact]
    public void ComputeSum_Positive_ForPositiveData()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.True(doc.ComputeSum("Q1") > 0);
    }

    [Fact]
    public void ComputeSum_Q1_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        // 120000+95000+145000+88000+132000+79000+115000 = 774000
        var sum = doc.ComputeSum("Q1");
        Assert.True(Math.Abs(sum - 774000.0) < 1.0);
    }

    [Fact]
    public void ComputeSum_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.Equal(doc.ComputeSum("Q2"), doc.ComputeSum("Q2"));
    }

    [Fact]
    public void ComputeSum_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.ComputeSum("Q3");
        var path = TempFile("cs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.ComputeSum("Q3"), 1);
    }

    [Fact]
    public void ComputeSum_AfterAddRow_Increases()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.ComputeSum("Q1");
        doc.AddRow(new[] { "Hector", "West", "100000", "108000", "104000", "115000" });
        Assert.True(doc.ComputeSum("Q1") > before);
    }

    // -------------------------------------------------------------------------
    // ComputeAverage
    // -------------------------------------------------------------------------

    [Fact]
    public void ComputeAverage_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.ComputeAverage("Q1"));
        Assert.Null(ex);
    }

    [Fact]
    public void ComputeAverage_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.True(doc.ComputeAverage("Q1") > 0);
    }

    [Fact]
    public void ComputeAverage_Q1_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        // 774000 / 7 = 110571.43
        var avg = doc.ComputeAverage("Q1");
        Assert.True(Math.Abs(avg - (774000.0 / 7)) < 1.0);
    }

    [Fact]
    public void ComputeAverage_InRange_Min_Max()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var avg = doc.ComputeAverage("Q1");
        var nums = doc.GetNumericColumn("Q1");
        double min = double.MaxValue, max = double.MinValue;
        foreach (var v in nums) { if (v < min) min = v; if (v > max) max = v; }
        Assert.True(avg >= min && avg <= max);
    }

    [Fact]
    public void ComputeAverage_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.Equal(doc.ComputeAverage("Q4"), doc.ComputeAverage("Q4"));
    }

    [Fact]
    public void ComputeAverage_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.ComputeAverage("Q2");
        var path = TempFile("ca_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.ComputeAverage("Q2"), 2);
    }

    // -------------------------------------------------------------------------
    // GetRowsWhere
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowsWhere_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        Assert.NotNull(doc.GetRowsWhere("Region", "North"));
    }

    [Fact]
    public void GetRowsWhere_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var ex = Record.Exception(() => doc.GetRowsWhere("Region", "South"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRowsWhere_North_ThreeRows()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var north = doc.GetRowsWhere("Region", "North");
        Assert.Equal(3, north.GetRowCount()); // Alice, Carol, Eve
    }

    [Fact]
    public void GetRowsWhere_South_TwoRows()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var south = doc.GetRowsWhere("Region", "South");
        Assert.Equal(2, south.GetRowCount()); // Bob, Frank
    }

    [Fact]
    public void GetRowsWhere_NoMatch_EmptyResult()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var none = doc.GetRowsWhere("Region", "West");
        Assert.Equal(0, none.GetRowCount());
    }

    [Fact]
    public void GetRowsWhere_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var e1 = doc.GetRowsWhere("Region", "East");
        var e2 = doc.GetRowsWhere("Region", "East");
        Assert.Equal(e1.GetRowCount(), e2.GetRowCount());
    }

    [Fact]
    public void GetRowsWhere_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var before = doc.GetRowsWhere("Region", "North").GetRowCount();
        var path = TempFile("grw_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRowsWhere("Region", "North").GetRowCount());
    }

    [Fact]
    public void GetRowsWhere_Then_ComputeSum()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var north = doc.GetRowsWhere("Region", "North");
        var sum = north.ComputeSum("Q1");
        // Alice(120)+Carol(145)+Eve(132) = 397000
        Assert.True(Math.Abs(sum - 397000.0) < 1.0);
    }

    [Fact]
    public void GetRowsWhere_Then_ExportToHtml_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalesTsv());
        var south = doc.GetRowsWhere("Region", "South");
        var ex = Record.Exception(() => south.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ComputeSum_ComputeAverage_GetRowsWhere_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_performance.tsv");
        var content =
            "Division\tBU\tRevenue\tCost\tHeadcount\tGrowthPct\n" +
            "EMEA\tPlatform\t8500000\t5200000\t85\t14.2\n" +
            "AMER\tPlatform\t12000000\t7800000\t120\t18.5\n" +
            "APAC\tData\t5800000\t3600000\t58\t22.1\n" +
            "EMEA\tData\t4200000\t2700000\t42\t9.8\n" +
            "AMER\tFinance\t3100000\t2100000\t31\t6.3\n" +
            "APAC\tPlatform\t6700000\t4100000\t67\t16.9\n" +
            "EMEA\tFinance\t2800000\t1900000\t28\t4.2\n" +
            "AMER\tData\t7400000\t4500000\t74\t19.7\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // ComputeSum — Revenue
        var totalRevenue = doc.ComputeSum("Revenue");
        // 8.5+12+5.8+4.2+3.1+6.7+2.8+7.4 = 50.5M
        Assert.True(totalRevenue > 0);
        Assert.True(Math.Abs(totalRevenue - 50500000.0) < 100.0);

        // ComputeSum — Cost
        var totalCost = doc.ComputeSum("Cost");
        Assert.True(totalCost > 0);
        Assert.True(totalCost < totalRevenue); // profitable

        // ComputeSum — Headcount
        var totalHeadcount = doc.ComputeSum("Headcount");
        // 85+120+58+42+31+67+28+74 = 505
        Assert.True(Math.Abs(totalHeadcount - 505.0) < 1.0);

        // Consistent
        Assert.Equal(totalRevenue, doc.ComputeSum("Revenue"));

        // ComputeAverage — GrowthPct
        var avgGrowth = doc.ComputeAverage("GrowthPct");
        // (14.2+18.5+22.1+9.8+6.3+16.9+4.2+19.7)/8 = 111.7/8 = 13.9625
        Assert.True(avgGrowth > 0 && avgGrowth < 30);

        // ComputeAverage — Revenue per division
        var avgRevenue = doc.ComputeAverage("Revenue");
        Assert.True(avgRevenue > 0);
        Assert.Equal(avgRevenue, doc.ComputeAverage("Revenue")); // consistent

        // GetRowsWhere — EMEA divisions
        var emea = doc.GetRowsWhere("Division", "EMEA");
        Assert.Equal(3, emea.GetRowCount()); // Platform, Data, Finance EMEA

        // ComputeSum on filtered
        var emeaRevenue = emea.ComputeSum("Revenue");
        // 8.5+4.2+2.8 = 15.5M
        Assert.True(Math.Abs(emeaRevenue - 15500000.0) < 100.0);

        // GetRowsWhere — Platform BU
        var platform = doc.GetRowsWhere("BU", "Platform");
        Assert.Equal(3, platform.GetRowCount()); // EMEA, AMER, APAC

        // ComputeAverage on filtered
        var platformAvgGrowth = platform.ComputeAverage("GrowthPct");
        Assert.True(platformAvgGrowth > 0);

        // GetRowsWhere — AMER
        var amer = doc.GetRowsWhere("Division", "AMER");
        Assert.Equal(3, amer.GetRowCount());

        // GetRowsWhere no match
        var west = doc.GetRowsWhere("Division", "WEST");
        Assert.Equal(0, west.GetRowCount());

        // Sum of all regional revenue equals total
        var emeaSum = doc.GetRowsWhere("Division", "EMEA").ComputeSum("Revenue");
        var amerSum = doc.GetRowsWhere("Division", "AMER").ComputeSum("Revenue");
        var apacSum = doc.GetRowsWhere("Division", "APAC").ComputeSum("Revenue");
        Assert.True(Math.Abs(emeaSum + amerSum + apacSum - totalRevenue) < 100.0);

        // AddRow and recompute
        doc.AddRow(new[] { "APAC", "Finance", "1800000", "1200000", "18", "3.5" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.ComputeSum("Revenue") > totalRevenue);

        // SaveToFile
        var savePath = TempFile("dogfood_performance_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.ComputeSum("Revenue"), loaded.ComputeSum("Revenue"), 1);
        Assert.Equal(doc.ComputeAverage("GrowthPct"), loaded.ComputeAverage("GrowthPct"), 2);
        Assert.Equal(4, loaded.GetRowsWhere("Division", "APAC").GetRowCount()); // 3 original + 1 added

        // Final save
        var path2 = TempFile("dogfood_performance_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.ComputeSum("Headcount"), loaded2.ComputeSum("Headcount"), 1);
    }
}
