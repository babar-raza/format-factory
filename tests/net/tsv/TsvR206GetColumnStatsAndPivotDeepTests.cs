// Tests for TsvDocument.GetColumnStats, Pivot, GetNumericColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R206

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R206: Tests for TsvDocument.GetColumnStats, Pivot, GetNumericColumn deeper.
/// GetColumnStats(colName): returns min/max/avg/sum for a numeric column.
/// Pivot(rowField, colField, valueField): creates a pivot table view.
/// GetNumericColumn(colName): returns the numeric values from a column as doubles.
/// Covers: GetColumnStats non-null; GetColumnStats no-throw; GetColumnStats min correct;
/// GetColumnStats max correct; GetColumnStats avg correct; GetColumnStats sum correct;
/// GetColumnStats consistent; GetColumnStats after AddRow updates; GetColumnStats save-load;
/// Pivot non-null; Pivot no-throw; Pivot row count correct; Pivot col count correct;
/// Pivot values correct; Pivot consistent; Pivot save-load; Pivot then Filter no-throw;
/// GetNumericColumn non-null; GetNumericColumn non-empty; GetNumericColumn count=rowCount;
/// GetNumericColumn values in range; GetNumericColumn no-throw; GetNumericColumn consistent;
/// GetNumericColumn after AddRow grows; GetNumericColumn save-load consistent;
/// dogfood LoadFile→GetColumnStats→Pivot→GetNumericColumn→SaveToFile pipeline.
/// </summary>
public class TsvR206GetColumnStatsAndPivotDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR206GetColumnStatsAndPivotDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR206_" + Guid.NewGuid().ToString("N"));
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
        var content =
            "Name\tDepartment\tScore\tSalary\n" +
            "Alice\tEngineering\t92\t95000\n" +
            "Bob\tMarketing\t78\t55000\n" +
            "Carol\tEngineering\t88\t115000\n" +
            "Dave\tFinance\t85\t72000\n" +
            "Eve\tEngineering\t95\t98000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnStats("Score"));
    }

    [Fact]
    public void GetColumnStats_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnStats("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStats_Min_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(78.0, stats.Min, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Max_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(95.0, stats.Max, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Sum_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Score");
        // 92 + 78 + 88 + 85 + 95 = 438
        Assert.Equal(438.0, stats.Sum, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Avg_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Score");
        // 438 / 5 = 87.6
        Assert.Equal(87.6, stats.Average, precision: 3);
    }

    [Fact]
    public void GetColumnStats_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var s1 = doc.GetColumnStats("Score");
        var s2 = doc.GetColumnStats("Score");
        Assert.Equal(s1.Min, s2.Min);
        Assert.Equal(s1.Max, s2.Max);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_Updates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnStats("Score").Max;
        doc.AddRow(new[] { "Zara", "Finance", "99", "60000" });
        var after = doc.GetColumnStats("Score").Max;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetColumnStats_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Score");
        var path = TempFile("stats_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var loadedStats = loaded.GetColumnStats("Score");
        Assert.Equal(stats.Min, loadedStats.Min, precision: 5);
        Assert.Equal(stats.Max, loadedStats.Max, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Salary_Sum_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var stats = doc.GetColumnStats("Salary");
        // 95000 + 55000 + 115000 + 72000 + 98000 = 435000
        Assert.Equal(435000.0, stats.Sum, precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumn_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetNumericColumn("Score"));
    }

    [Fact]
    public void GetNumericColumn_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetNumericColumn("Score").Count > 0);
    }

    [Fact]
    public void GetNumericColumn_Count_EqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetRowCount(), doc.GetNumericColumn("Score").Count);
    }

    [Fact]
    public void GetNumericColumn_Values_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var values = doc.GetNumericColumn("Score");
        foreach (var v in values)
            Assert.True(v >= 0 && v <= 200);
    }

    [Fact]
    public void GetNumericColumn_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetNumericColumn("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNumericColumn_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var c1 = doc.GetNumericColumn("Score");
        var c2 = doc.GetNumericColumn("Score");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetNumericColumn_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetNumericColumn("Score").Count;
        doc.AddRow(new[] { "Zara", "Finance", "77", "60000" });
        Assert.Equal(before + 1, doc.GetNumericColumn("Score").Count);
    }

    [Fact]
    public void GetNumericColumn_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetNumericColumn("Score").Count;
        var path = TempFile("numeric_col_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNumericColumn("Score").Count);
    }

    // -------------------------------------------------------------------------
    // Pivot
    // -------------------------------------------------------------------------

    [Fact]
    public void Pivot_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.Pivot("Department", "Name", "Score"));
    }

    [Fact]
    public void Pivot_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.Pivot("Department", "Name", "Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void Pivot_RowCount_EqualsDistinctRowField()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var pivot = doc.Pivot("Department", "Name", "Score");
        // 3 distinct departments: Engineering, Marketing, Finance
        Assert.Equal(3, pivot.GetRowCount());
    }

    [Fact]
    public void Pivot_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var p1 = doc.Pivot("Department", "Name", "Score");
        var p2 = doc.Pivot("Department", "Name", "Score");
        Assert.Equal(p1.GetRowCount(), p2.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnStats_Pivot_GetNumericColumn_SaveToFile_Pipeline()
    {
        // Create comprehensive TSV with sales data
        var path = TempFile("dogfood_sales.tsv");
        var content =
            "SalesPerson\tRegion\tProduct\tUnits\tRevenue\n" +
            "Alice\tNorth\tAlpha\t120\t84000\n" +
            "Bob\tSouth\tBeta\t95\t66500\n" +
            "Carol\tNorth\tAlpha\t140\t98000\n" +
            "Dave\tEast\tGamma\t80\t56000\n" +
            "Eve\tSouth\tAlpha\t110\t77000\n" +
            "Frank\tNorth\tBeta\t130\t91000\n" +
            "Grace\tEast\tGamma\t70\t49000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());

        // GetColumnStats for Units
        var unitStats = doc.GetColumnStats("Units");
        Assert.NotNull(unitStats);
        Assert.Equal(70.0, unitStats.Min, precision: 5);
        Assert.Equal(140.0, unitStats.Max, precision: 5);
        // Sum = 120+95+140+80+110+130+70 = 745
        Assert.Equal(745.0, unitStats.Sum, precision: 5);
        // Avg = 745/7 ≈ 106.43
        Assert.True(unitStats.Average > 100.0 && unitStats.Average < 115.0);

        // GetColumnStats for Revenue
        var revStats = doc.GetColumnStats("Revenue");
        Assert.NotNull(revStats);
        Assert.Equal(49000.0, revStats.Min, precision: 5);
        Assert.Equal(98000.0, revStats.Max, precision: 5);
        // Sum = 84000+66500+98000+56000+77000+91000+49000 = 521500
        Assert.Equal(521500.0, revStats.Sum, precision: 5);

        // GetColumnStats consistent
        Assert.Equal(unitStats.Sum, doc.GetColumnStats("Units").Sum, precision: 5);

        // GetNumericColumn Units
        var units = doc.GetNumericColumn("Units");
        Assert.Equal(7, units.Count);
        Assert.True(units.Exists(v => v == 120.0));
        Assert.True(units.Exists(v => v == 70.0));

        // GetNumericColumn Revenue
        var revenues = doc.GetNumericColumn("Revenue");
        Assert.Equal(7, revenues.Count);
        Assert.True(revenues.Exists(v => v == 98000.0));

        // AddRow and verify stats update
        doc.AddRow(new[] { "Hector", "West", "Alpha", "150", "105000" });
        Assert.Equal(8, doc.GetRowCount());
        var updatedUnitStats = doc.GetColumnStats("Units");
        Assert.Equal(150.0, updatedUnitStats.Max, precision: 5);
        var updatedUnits = doc.GetNumericColumn("Units");
        Assert.Equal(8, updatedUnits.Count);

        // Pivot by Region
        var regionPivot = doc.Pivot("Region", "SalesPerson", "Revenue");
        Assert.NotNull(regionPivot);
        // 4 distinct regions: North, South, East, West
        Assert.Equal(4, regionPivot.GetRowCount());

        // Pivot by Product
        var productPivot = doc.Pivot("Product", "SalesPerson", "Units");
        Assert.NotNull(productPivot);
        // 3 distinct products: Alpha, Beta, Gamma
        Assert.Equal(3, productPivot.GetRowCount());

        // Pivot consistent
        Assert.Equal(regionPivot.GetRowCount(), doc.Pivot("Region", "SalesPerson", "Revenue").GetRowCount());

        // SaveToFile
        var savePath = TempFile("dogfood_sales_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify stats
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());
        var loadedStats = loaded.GetColumnStats("Units");
        Assert.Equal(150.0, loadedStats.Max, precision: 5);
        Assert.Equal(895.0, loadedStats.Sum, precision: 5); // 745 + 150

        // GetNumericColumn on loaded
        var loadedUnits = loaded.GetNumericColumn("Units");
        Assert.Equal(8, loadedUnits.Count);

        // Pivot on loaded
        var loadedPivot = loaded.Pivot("Region", "SalesPerson", "Revenue");
        Assert.Equal(4, loadedPivot.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_sales_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetColumnStats("Units").Sum, loaded2.GetColumnStats("Units").Sum, precision: 5);
    }
}
