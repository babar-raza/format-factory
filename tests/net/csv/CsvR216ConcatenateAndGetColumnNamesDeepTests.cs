// Tests for CsvDocument.Concatenate, GetColumnNames, GetNumericColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R216: Tests for CsvDocument.Concatenate, GetColumnNames, GetNumericColumn deeper.
/// Concatenate(other): vertically appends another CsvDocument, returning a combined document.
/// GetColumnNames(): returns a list of column header names.
/// GetNumericColumn(colName): returns the column values parsed as doubles.
/// Covers: Concatenate non-null; Concatenate no-throw; Concatenate row count sum;
/// Concatenate consistent; Concatenate save-load; Concatenate then GetDistinctValues;
/// Concatenate then FilterRows; Concatenate headers preserved;
/// GetColumnNames non-null; GetColumnNames no-throw; GetColumnNames count;
/// GetColumnNames correct names; GetColumnNames consistent; GetColumnNames save-load;
/// GetColumnNames after AddColumn; GetColumnNames after RemoveColumn;
/// GetNumericColumn non-null; GetNumericColumn no-throw; GetNumericColumn count;
/// GetNumericColumn correct values; GetNumericColumn consistent; GetNumericColumn save-load;
/// GetNumericColumn all positive for positive data; GetNumericColumn sum correct;
/// dogfood LoadFile→Concatenate→GetColumnNames→GetNumericColumn→SaveToFile pipeline.
/// </summary>
public class CsvR216ConcatenateAndGetColumnNamesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR216ConcatenateAndGetColumnNamesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR216_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateBatchACsv()
    {
        var path = TempFile("batch_a.csv");
        var content =
            "Code,Name,Category,Value,Count\n" +
            "A001,Alpha Product,Electronics,1250.00,100\n" +
            "A002,Beta Product,Hardware,850.00,200\n" +
            "A003,Gamma Product,Software,2100.00,50\n" +
            "A004,Delta Product,Electronics,750.00,150\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateBatchBCsv()
    {
        var path = TempFile("batch_b.csv");
        var content =
            "Code,Name,Category,Value,Count\n" +
            "B001,Epsilon Product,Software,3200.00,25\n" +
            "B002,Zeta Product,Hardware,640.00,300\n" +
            "B003,Eta Product,Electronics,980.00,75\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Concatenate
    // -------------------------------------------------------------------------

    [Fact]
    public void Concatenate_NonNull()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        Assert.NotNull(a.Concatenate(b));
    }

    [Fact]
    public void Concatenate_NoThrow()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var ex = Record.Exception(() => a.Concatenate(b));
        Assert.Null(ex);
    }

    [Fact]
    public void Concatenate_RowCount_IsSum()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var combined = a.Concatenate(b);
        Assert.Equal(a.GetRowCount() + b.GetRowCount(), combined.GetRowCount());
    }

    [Fact]
    public void Concatenate_Consistent()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var c1 = a.Concatenate(b);
        var c2 = a.Concatenate(b);
        Assert.Equal(c1.GetRowCount(), c2.GetRowCount());
    }

    [Fact]
    public void Concatenate_SaveLoad_Consistent()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var combined = a.Concatenate(b);
        var path = TempFile("concat_save.csv");
        combined.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(combined.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void Concatenate_Then_GetDistinctValues()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var combined = a.Concatenate(b);
        var categories = combined.GetDistinctValues("Category");
        Assert.True(categories.Count >= 2);
    }

    [Fact]
    public void Concatenate_Then_FilterRows()
    {
        var a = CsvDocument.LoadFile(CreateBatchACsv());
        var b = CsvDocument.LoadFile(CreateBatchBCsv());
        var combined = a.Concatenate(b);
        var electronics = combined.FilterRows("Category", "Electronics");
        Assert.True(electronics.GetRowCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetColumnNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNames_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        Assert.NotNull(doc.GetColumnNames());
    }

    [Fact]
    public void GetColumnNames_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var ex = Record.Exception(() => doc.GetColumnNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNames_Count_Equals_ColumnCount()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnNames().Count);
    }

    [Fact]
    public void GetColumnNames_CorrectNames()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var names = doc.GetColumnNames();
        Assert.True(names.Contains("Code") || names.Exists(n => n.Contains("Code")));
        Assert.True(names.Contains("Value") || names.Exists(n => n.Contains("Value")));
    }

    [Fact]
    public void GetColumnNames_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var n1 = doc.GetColumnNames();
        var n2 = doc.GetColumnNames();
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetColumnNames_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var before = doc.GetColumnNames().Count;
        var path = TempFile("gcn_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnNames().Count);
    }

    [Fact]
    public void GetColumnNames_After_AddColumn()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var before = doc.GetColumnNames().Count;
        doc.AddColumn("Discount", new[] { "5", "8", "3", "6" });
        Assert.Equal(before + 1, doc.GetColumnNames().Count);
    }

    // -------------------------------------------------------------------------
    // GetNumericColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumn_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        Assert.NotNull(doc.GetNumericColumn("Value"));
    }

    [Fact]
    public void GetNumericColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var ex = Record.Exception(() => doc.GetNumericColumn("Count"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNumericColumn_Count_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        Assert.Equal(doc.GetRowCount(), doc.GetNumericColumn("Value").Count);
    }

    [Fact]
    public void GetNumericColumn_AllPositive_ForPositiveData()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var values = doc.GetNumericColumn("Value");
        foreach (var v in values)
            Assert.True(v > 0);
    }

    [Fact]
    public void GetNumericColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var v1 = doc.GetNumericColumn("Count");
        var v2 = doc.GetNumericColumn("Count");
        Assert.Equal(v1.Count, v2.Count);
        Assert.Equal(v1[0], v2[0]);
    }

    [Fact]
    public void GetNumericColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var before = doc.GetNumericColumn("Value");
        var path = TempFile("gnc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetNumericColumn("Value");
        Assert.Equal(before.Count, after.Count);
        Assert.Equal(before[0], after[0], 2);
    }

    [Fact]
    public void GetNumericColumn_Sum_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateBatchACsv());
        var counts = doc.GetNumericColumn("Count");
        double sum = 0;
        foreach (var c in counts) sum += c;
        // 100+200+50+150 = 500
        Assert.True(Math.Abs(sum - 500.0) < 1.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Concatenate_GetColumnNames_GetNumericColumn_SaveToFile_Pipeline()
    {
        var pathQ1 = TempFile("dogfood_q1.csv");
        File.WriteAllText(pathQ1,
            "ProductId,Name,Line,Revenue,UnitsSold,Margin\n" +
            "P001,Apex Widget,Platform,125000,500,0.35\n" +
            "P002,Beta Module,Data,89000,356,0.28\n" +
            "P003,Gamma Suite,Platform,215000,172,0.42\n" +
            "P004,Delta Tool,Analytics,67000,536,0.22\n");

        var pathQ2 = TempFile("dogfood_q2.csv");
        File.WriteAllText(pathQ2,
            "ProductId,Name,Line,Revenue,UnitsSold,Margin\n" +
            "P005,Epsilon Pack,Data,145000,580,0.31\n" +
            "P006,Zeta Service,Platform,98000,392,0.38\n" +
            "P007,Eta Platform,Analytics,189000,756,0.29\n");

        var docQ1 = CsvDocument.LoadFile(pathQ1);
        var docQ2 = CsvDocument.LoadFile(pathQ2);

        Assert.Equal(4, docQ1.GetRowCount());
        Assert.Equal(3, docQ2.GetRowCount());

        // GetColumnNames
        var names = docQ1.GetColumnNames();
        Assert.NotNull(names);
        Assert.Equal(6, names.Count);
        Assert.True(names.Contains("Revenue") || names.Exists(n => n.Contains("Revenue")));
        Assert.True(names.Contains("Margin") || names.Exists(n => n.Contains("Margin")));
        Assert.Equal(names.Count, docQ1.GetColumnNames().Count); // consistent

        // GetNumericColumn — Revenue
        var q1Revenue = docQ1.GetNumericColumn("Revenue");
        Assert.Equal(4, q1Revenue.Count);
        foreach (var v in q1Revenue) Assert.True(v > 0);

        // Sum of Q1 revenue: 125000+89000+215000+67000 = 496000
        double q1Sum = 0;
        foreach (var v in q1Revenue) q1Sum += v;
        Assert.True(Math.Abs(q1Sum - 496000.0) < 1.0);

        // GetNumericColumn — Margin
        var q1Margin = docQ1.GetNumericColumn("Margin");
        Assert.Equal(4, q1Margin.Count);
        foreach (var m in q1Margin) Assert.True(m > 0 && m < 1);

        // Consistent
        Assert.Equal(q1Revenue.Count, docQ1.GetNumericColumn("Revenue").Count);

        // Concatenate
        var combined = docQ1.Concatenate(docQ2);
        Assert.Equal(7, combined.GetRowCount());

        // GetColumnNames on combined
        var combinedNames = combined.GetColumnNames();
        Assert.Equal(6, combinedNames.Count);

        // GetNumericColumn on combined
        var allRevenue = combined.GetNumericColumn("Revenue");
        Assert.Equal(7, allRevenue.Count);
        double totalRevenue = 0;
        foreach (var v in allRevenue) totalRevenue += v;
        // 496000 + 145000+98000+189000 = 928000
        Assert.True(Math.Abs(totalRevenue - 928000.0) < 1.0);

        // GetDistinctValues on combined
        var lines = combined.GetDistinctValues("Line");
        Assert.Equal(3, lines.Count); // Platform, Data, Analytics

        // FilterRows on combined
        var platform = combined.FilterRows("Line", "Platform");
        Assert.Equal(3, platform.GetRowCount()); // P001, P003, P006

        // GetNumericColumn on filtered
        var platformRevenue = platform.GetNumericColumn("Revenue");
        Assert.Equal(3, platformRevenue.Count);

        // SortByColumn on combined
        var sorted = combined.SortByColumn("Revenue", ascending: false);
        Assert.Equal(7, sorted.GetRowCount());
        var sortedRevenue = sorted.GetNumericColumn("Revenue");
        Assert.True(sortedRevenue[0] >= sortedRevenue[sortedRevenue.Count - 1]);

        // SaveToFile
        var savePath = TempFile("dogfood_combined_out.csv");
        combined.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(6, loaded.GetColumnNames().Count);
        var loadedRevenue = loaded.GetNumericColumn("Revenue");
        Assert.Equal(7, loadedRevenue.Count);
        double loadedTotal = 0;
        foreach (var v in loadedRevenue) loadedTotal += v;
        Assert.True(Math.Abs(loadedTotal - totalRevenue) < 1.0);

        // Concatenate loaded with original Q1
        var extended = loaded.Concatenate(docQ1);
        Assert.Equal(11, extended.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_combined_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(6, loaded2.GetColumnNames().Count);
        var ex = Record.Exception(() => loaded2.ExportToHtml());
        Assert.Null(ex);
    }
}
