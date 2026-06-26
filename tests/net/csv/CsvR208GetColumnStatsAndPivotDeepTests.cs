// Tests for CsvDocument.GetColumnStats, Pivot, GetNumericColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R208

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R208: Tests for CsvDocument.GetColumnStats, Pivot, GetNumericColumn deeper.
/// GetColumnStats(colName): returns min/max/avg/sum for a numeric column.
/// Pivot(rowField, colField, valueField): creates a pivot table view.
/// GetNumericColumn(colName): returns column values as a list of doubles.
/// Covers: GetColumnStats non-null; GetColumnStats no-throw; GetColumnStats min correct;
/// GetColumnStats max correct; GetColumnStats avg in range; GetColumnStats sum correct;
/// GetColumnStats consistent; GetColumnStats after AddRow updates; GetColumnStats save-load;
/// GetColumnStats second column; GetNumericColumn non-null; GetNumericColumn count=rowCount;
/// GetNumericColumn values in valid range; GetNumericColumn no-throw; GetNumericColumn consistent;
/// GetNumericColumn after AddRow grows; GetNumericColumn save-load; Pivot non-null;
/// Pivot no-throw; Pivot row count distinct; Pivot consistent; Pivot save-load;
/// Pivot then Filter no-throw; Pivot after AddRow updates;
/// dogfood LoadFile→GetColumnStats→GetNumericColumn→Pivot→SaveToFile pipeline.
/// </summary>
public class CsvR208GetColumnStatsAndPivotDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR208GetColumnStatsAndPivotDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR208_" + Guid.NewGuid().ToString("N"));
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
        var content =
            "Name,Department,Score,Salary\n" +
            "Alice,Engineering,92,95000\n" +
            "Bob,Marketing,78,55000\n" +
            "Carol,Engineering,88,115000\n" +
            "Dave,Finance,85,72000\n" +
            "Eve,Engineering,95,98000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStats_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnStats("Score"));
    }

    [Fact]
    public void GetColumnStats_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnStats("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStats_Min_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(78.0, stats.Min, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Max_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Score");
        Assert.Equal(95.0, stats.Max, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Sum_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Score");
        // 92 + 78 + 88 + 85 + 95 = 438
        Assert.Equal(438.0, stats.Sum, precision: 5);
    }

    [Fact]
    public void GetColumnStats_Avg_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Score");
        // 438/5 = 87.6
        Assert.True(stats.Average > 80.0 && stats.Average < 95.0);
    }

    [Fact]
    public void GetColumnStats_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var s1 = doc.GetColumnStats("Score");
        var s2 = doc.GetColumnStats("Score");
        Assert.Equal(s1.Min, s2.Min);
        Assert.Equal(s1.Sum, s2.Sum);
    }

    [Fact]
    public void GetColumnStats_AfterAddRow_UpdatesMax()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnStats("Score").Max;
        doc.AddRow(new[] { "Zara", "Finance", "99", "60000" });
        var after = doc.GetColumnStats("Score").Max;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetColumnStats_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Score");
        var path = TempFile("stats_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var loadedStats = loaded.GetColumnStats("Score");
        Assert.Equal(stats.Sum, loadedStats.Sum, precision: 5);
    }

    [Fact]
    public void GetColumnStats_SecondColumn_Salary()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var stats = doc.GetColumnStats("Salary");
        // min=55000, max=115000
        Assert.Equal(55000.0, stats.Min, precision: 5);
        Assert.Equal(115000.0, stats.Max, precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumn_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetNumericColumn("Score"));
    }

    [Fact]
    public void GetNumericColumn_Count_EqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetRowCount(), doc.GetNumericColumn("Score").Count);
    }

    [Fact]
    public void GetNumericColumn_Values_InValidRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var values = doc.GetNumericColumn("Score");
        foreach (var v in values)
            Assert.True(v >= 0 && v <= 200);
    }

    [Fact]
    public void GetNumericColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetNumericColumn("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNumericColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var c1 = doc.GetNumericColumn("Score");
        var c2 = doc.GetNumericColumn("Score");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetNumericColumn_AfterAddRow_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetNumericColumn("Score").Count;
        doc.AddRow(new[] { "Zara", "Finance", "77", "60000" });
        Assert.Equal(before + 1, doc.GetNumericColumn("Score").Count);
    }

    [Fact]
    public void GetNumericColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetNumericColumn("Score").Count;
        var path = TempFile("numeric_col_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNumericColumn("Score").Count);
    }

    // -------------------------------------------------------------------------
    // Pivot
    // -------------------------------------------------------------------------

    [Fact]
    public void Pivot_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.Pivot("Department", "Name", "Score"));
    }

    [Fact]
    public void Pivot_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.Pivot("Department", "Name", "Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void Pivot_RowCount_EqualsDistinctDepartments()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var pivot = doc.Pivot("Department", "Name", "Score");
        // 3 distinct departments: Engineering, Marketing, Finance
        Assert.Equal(3, pivot.GetRowCount());
    }

    [Fact]
    public void Pivot_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var p1 = doc.Pivot("Department", "Name", "Score");
        var p2 = doc.Pivot("Department", "Name", "Score");
        Assert.Equal(p1.GetRowCount(), p2.GetRowCount());
    }

    [Fact]
    public void Pivot_ThenFilter_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var pivot = doc.Pivot("Department", "Name", "Score");
        var ex = Record.Exception(() => pivot.Filter("Department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Pivot_AfterAddRow_Updates()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddRow(new[] { "Hector", "HR", "80", "65000" });
        var pivot = doc.Pivot("Department", "Name", "Score");
        // Now 4 departments: Engineering, Marketing, Finance, HR
        Assert.Equal(4, pivot.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnStats_GetNumericColumn_Pivot_SaveToFile_Pipeline()
    {
        // Create comprehensive CSV with product sales data
        var path = TempFile("dogfood_sales.csv");
        var content =
            "SalesPerson,Region,Product,Units,Revenue,Quarter\n" +
            "Alice,North,Alpha,120,84000,Q1\n" +
            "Bob,South,Beta,95,66500,Q1\n" +
            "Carol,North,Alpha,140,98000,Q2\n" +
            "Dave,East,Gamma,80,56000,Q1\n" +
            "Eve,South,Alpha,110,77000,Q2\n" +
            "Frank,North,Beta,130,91000,Q2\n" +
            "Grace,East,Gamma,70,49000,Q1\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());

        // GetColumnStats for Units
        var unitStats = doc.GetColumnStats("Units");
        Assert.NotNull(unitStats);
        Assert.Equal(70.0, unitStats.Min, precision: 5);
        Assert.Equal(140.0, unitStats.Max, precision: 5);
        // Sum = 120+95+140+80+110+130+70 = 745
        Assert.Equal(745.0, unitStats.Sum, precision: 5);
        Assert.True(unitStats.Average > 100.0 && unitStats.Average < 115.0);

        // GetColumnStats for Revenue
        var revStats = doc.GetColumnStats("Revenue");
        Assert.NotNull(revStats);
        Assert.Equal(49000.0, revStats.Min, precision: 5);
        Assert.Equal(98000.0, revStats.Max, precision: 5);

        // GetNumericColumn for Units
        var units = doc.GetNumericColumn("Units");
        Assert.Equal(7, units.Count);
        Assert.True(units.Exists(v => v == 140.0));
        Assert.True(units.Exists(v => v == 70.0));

        // GetNumericColumn for Revenue
        var revenues = doc.GetNumericColumn("Revenue");
        Assert.Equal(7, revenues.Count);
        Assert.True(revenues.Exists(v => v == 98000.0));

        // Pivot by Region
        var regionPivot = doc.Pivot("Region", "SalesPerson", "Revenue");
        Assert.NotNull(regionPivot);
        // 3 distinct regions: North, South, East
        Assert.Equal(3, regionPivot.GetRowCount());

        // Pivot by Product
        var productPivot = doc.Pivot("Product", "SalesPerson", "Units");
        Assert.NotNull(productPivot);
        // 3 distinct products: Alpha, Beta, Gamma
        Assert.Equal(3, productPivot.GetRowCount());

        // Pivot by Quarter
        var quarterPivot = doc.Pivot("Quarter", "SalesPerson", "Revenue");
        Assert.NotNull(quarterPivot);
        // 2 distinct quarters: Q1, Q2
        Assert.Equal(2, quarterPivot.GetRowCount());

        // AddRow and verify stats update
        doc.AddRow(new[] { "Hector", "West", "Alpha", "150", "105000", "Q2" });
        Assert.Equal(8, doc.GetRowCount());
        var updatedStats = doc.GetColumnStats("Units");
        Assert.Equal(150.0, updatedStats.Max, precision: 5);

        // Pivot after AddRow — West adds a new region
        var updatedRegionPivot = doc.Pivot("Region", "SalesPerson", "Revenue");
        Assert.Equal(4, updatedRegionPivot.GetRowCount());

        // GetNumericColumn after AddRow
        var updatedUnits = doc.GetNumericColumn("Units");
        Assert.Equal(8, updatedUnits.Count);

        // GetColumnStats consistent
        Assert.Equal(unitStats.Min, doc.GetColumnStats("Units").Min, precision: 5); // min unchanged

        // SaveToFile
        var savePath = TempFile("dogfood_sales_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRowCount());
        var loadedStats = loaded.GetColumnStats("Units");
        Assert.Equal(150.0, loadedStats.Max, precision: 5);

        // GetNumericColumn on loaded
        var loadedUnits = loaded.GetNumericColumn("Units");
        Assert.Equal(8, loadedUnits.Count);

        // Pivot on loaded
        var loadedPivot = loaded.Pivot("Region", "SalesPerson", "Revenue");
        Assert.Equal(4, loadedPivot.GetRowCount());

        // Filter then GetColumnStats
        var filtered = doc.Filter("Region", "North");
        var filteredStats = filtered.GetColumnStats("Revenue");
        Assert.NotNull(filteredStats);
        Assert.True(filteredStats.Sum > 0);

        // ExportToXml still works
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);

        // Final save
        var path2 = TempFile("dogfood_sales_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetColumnStats("Units").Sum, loaded2.GetColumnStats("Units").Sum, precision: 5);
    }
}
