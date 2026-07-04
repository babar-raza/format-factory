// Tests for CsvDocument.Merge, GetRowAt, AddColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R196

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R196: Tests for CsvDocument.Merge, GetRowAt, AddColumn deeper.
/// Merge(other): combines two CsvDocuments into one.
/// GetRowAt(index): returns the row object at the specified index.
/// AddColumn(colName, values): adds a new column with a header and optional values.
/// Covers: Merge increases row count; Merge combines headers; Merge non-null;
/// Merge then Filter; Merge then SortRows; Merge persist; Merge consistent;
/// GetRowAt first row non-null; GetRowAt has values; GetRowAt last row accessible;
/// GetRowAt consistent; GetRowAt after AddRow includes new row;
/// GetRowAt index zero is first data row;
/// AddColumn increases column count; AddColumn new header present;
/// AddColumn values accessible; AddColumn persist; AddColumn then Filter;
/// AddColumn multiple; AddColumn then ExportToCsv reflects;
/// dogfood LoadFile→Merge→GetRowAt→AddColumn→SaveToFile pipeline.
/// </summary>
public class CsvR196MergeAndGetRowAtDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR196MergeAndGetRowAtDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR196_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsvA =
        "Name,Dept,Score\n" +
        "Alice,Engineering,92\n" +
        "Bob,Finance,85\n" +
        "Carol,Engineering,95\n";

    private static readonly string SampleCsvB =
        "Name,Dept,Score\n" +
        "Dave,HR,78\n" +
        "Eve,Finance,88\n";

    private CsvDocument LoadSampleA()
    {
        var path = TempFile("sampleA.csv");
        File.WriteAllText(path, SampleCsvA);
        return CsvDocument.LoadFile(path);
    }

    private CsvDocument LoadSampleB()
    {
        var path = TempFile("sampleB.csv");
        File.WriteAllText(path, SampleCsvB);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_IncreasesRowCount()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var before = a.GetRowCount();
        var merged = a.Merge(b);
        Assert.True(merged.GetRowCount() > before);
    }

    [Fact]
    public void Merge_CombinesAllRows()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var merged = a.Merge(b);
        Assert.Equal(a.GetRowCount() + b.GetRowCount(), merged.GetRowCount());
    }

    [Fact]
    public void Merge_NonNull()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        Assert.NotNull(a.Merge(b));
    }

    [Fact]
    public void Merge_HeadersPreserved()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var merged = a.Merge(b);
        var headers = merged.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void Merge_ContainsDataFromBothDocs()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var merged = a.Merge(b);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void Merge_ThenFilter_Works()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var merged = a.Merge(b);
        var finance = merged.Filter("Dept", "Finance");
        Assert.True(finance.GetRowCount() >= 2);
    }

    [Fact]
    public void Merge_Persist()
    {
        var a = LoadSampleA();
        var b = LoadSampleB();
        var merged = a.Merge(b);
        var path = TempFile("merged_persist.csv");
        merged.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(merged.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetRowAt
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowAt_FirstRow_NonNull()
    {
        var doc = LoadSampleA();
        Assert.NotNull(doc.GetRowAt(0));
    }

    [Fact]
    public void GetRowAt_FirstRow_HasValues()
    {
        var doc = LoadSampleA();
        var row = doc.GetRowAt(0);
        Assert.True(row != null && row.Length > 0);
    }

    [Fact]
    public void GetRowAt_LastRow_Accessible()
    {
        var doc = LoadSampleA();
        var last = doc.GetRowAt(doc.GetRowCount() - 1);
        Assert.NotNull(last);
        Assert.True(last.Length > 0);
    }

    [Fact]
    public void GetRowAt_Consistent()
    {
        var doc = LoadSampleA();
        var r1 = doc.GetRowAt(0);
        var r2 = doc.GetRowAt(0);
        Assert.Equal(r1.Length, r2.Length);
    }

    [Fact]
    public void GetRowAt_AfterAddRow_NewRowAccessible()
    {
        var doc = LoadSampleA();
        doc.AddRow(new[] { "Zara", "Legal", "99" });
        var last = doc.GetRowAt(doc.GetRowCount() - 1);
        Assert.NotNull(last);
        Assert.True(last.Length > 0);
    }

    [Fact]
    public void GetRowAt_ContainsExpectedValue()
    {
        var doc = LoadSampleA();
        var row = doc.GetRowAt(0);
        // First row should contain Alice's data
        Assert.True(row.Contains("Alice") || row.Contains("Engineering") || row.Contains("92"));
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_IncreasesColumnCount()
    {
        var doc = LoadSampleA();
        var before = doc.GetColumnCount();
        doc.AddColumn("Rating", new[] { "A", "B", "A" });
        Assert.True(doc.GetColumnCount() > before);
    }

    [Fact]
    public void AddColumn_NewHeaderPresent()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Rating", new[] { "A", "B", "A" });
        Assert.Contains("Rating", doc.GetHeaders());
    }

    [Fact]
    public void AddColumn_ValuesAccessible()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Level", new[] { "Senior", "Mid", "Senior" });
        var values = doc.GetColumnValues("Level");
        Assert.Contains("Senior", values);
        Assert.Contains("Mid", values);
    }

    [Fact]
    public void AddColumn_Persist()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Tier", new[] { "Gold", "Silver", "Gold" });
        var path = TempFile("addcol_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Contains("Tier", loaded.GetHeaders());
    }

    [Fact]
    public void AddColumn_Multiple_BothPresent()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Rating", new[] { "A", "B", "A" });
        doc.AddColumn("Level", new[] { "Senior", "Mid", "Senior" });
        var headers = doc.GetHeaders();
        Assert.Contains("Rating", headers);
        Assert.Contains("Level", headers);
    }

    [Fact]
    public void AddColumn_ThenFilter_Works()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Region", new[] { "East", "West", "East" });
        var east = doc.Filter("Region", "East");
        Assert.Equal(2, east.GetRowCount());
    }

    [Fact]
    public void AddColumn_ThenExportToCsv_Reflects()
    {
        var doc = LoadSampleA();
        doc.AddColumn("Tag", new[] { "X", "Y", "X" });
        var csv = doc.ToCsv();
        Assert.Contains("Tag", csv);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_Merge_GetRowAt_AddColumn_SaveToFile_Pipeline()
    {
        var pathA = TempFile("dogfood_a.csv");
        var pathB = TempFile("dogfood_b.csv");
        File.WriteAllText(pathA, SampleCsvA);
        File.WriteAllText(pathB, SampleCsvB);

        var docA = CsvDocument.LoadFile(pathA);
        var docB = CsvDocument.LoadFile(pathB);

        Assert.Equal(3, docA.GetRowCount());
        Assert.Equal(2, docB.GetRowCount());

        // GetRowAt baseline
        var firstRow = docA.GetRowAt(0);
        Assert.NotNull(firstRow);
        Assert.True(firstRow.Length > 0);

        var lastRow = docA.GetRowAt(docA.GetRowCount() - 1);
        Assert.NotNull(lastRow);

        // Merge
        var merged = docA.Merge(docB);
        Assert.Equal(5, merged.GetRowCount());
        Assert.Equal(3, merged.GetColumnCount());

        // GetRowAt on merged
        var mergedFirst = merged.GetRowAt(0);
        Assert.NotNull(mergedFirst);
        Assert.True(mergedFirst.Length >= 3);

        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
        Assert.Contains("Eve", names);

        // AddColumn Score2
        merged.AddColumn("Score2", new[] { "92", "85", "95", "78", "88" });
        Assert.Equal(4, merged.GetColumnCount());
        Assert.Contains("Score2", merged.GetHeaders());
        var scores2 = merged.GetColumnValues("Score2");
        Assert.Equal(5, scores2.Count);
        Assert.Contains("92", scores2);

        // AddColumn Dept2
        merged.AddColumn("Region", new[] { "East", "West", "East", "North", "West" });
        Assert.Equal(5, merged.GetColumnCount());

        // Filter by Region
        var east = merged.Filter("Region", "East");
        Assert.Equal(2, east.GetRowCount());

        // SortRows on merged
        var sorted = merged.SortRows("Name", ascending: true);
        var sortedNames = sorted.GetColumnValues("Name");
        Assert.Equal("Alice", sortedNames[0]);

        // ToCsv reflects all columns
        var csv = merged.ToCsv();
        Assert.Contains("Score2", csv);
        Assert.Contains("Region", csv);

        // SaveToFile and reload
        var path = TempFile("dogfood_merge.csv");
        merged.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRowCount());
        Assert.Equal(5, loaded.GetColumnCount());

        var loadedRow = loaded.GetRowAt(0);
        Assert.NotNull(loadedRow);
        Assert.True(loadedRow.Length >= 5);

        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Contains("Alice", loadedNames);

        // Merge on loaded
        var pathC = TempFile("dogfood_c.csv");
        File.WriteAllText(pathC, "Name,Dept,Score,Score2,Region\nFrank,Legal,80,80,South\n");
        var docC = CsvDocument.LoadFile(pathC);
        var merged2 = loaded.Merge(docC);
        Assert.Equal(6, merged2.GetRowCount());
        Assert.Contains("Frank", merged2.GetColumnValues("Name"));
    }
}
