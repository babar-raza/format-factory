// Tests for CsvDocument.AddRow, RemoveRow, GetColumnValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R186

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R186: Tests for CsvDocument.AddRow, RemoveRow, GetColumnValues deeper coverage.
/// AddRow(values): appends a new row with given values.
/// RemoveRow(rowIndex): removes the row at the given index.
/// GetColumnValues(colName): returns all values in a named column.
/// Covers: AddRow increases RowCount; AddRow values accessible via GetRow;
/// AddRow multiple rows increases count correctly; AddRow then GetColumnValues includes new;
/// RemoveRow decreases RowCount; RemoveRow correct row removed; RemoveRow last row works;
/// RemoveRow then RowCount correct; RemoveRow leaves others intact;
/// GetColumnValues non-null; GetColumnValues count=RowCount; GetColumnValues contains all names;
/// GetColumnValues after AddRow includes new; GetColumnValues after RemoveRow excludes removed;
/// GetColumnValues after SetCellValue reflects;
/// dogfood LoadContent→AddRow×2→GetColumnValues→RemoveRow→GetColumnValues→SaveToFile→LoadFile pipeline.
/// </summary>
public class CsvR186AddRowAndRemoveRowDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR186AddRowAndRemoveRowDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR186_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleCsv =
        "Name,Score,Dept\n" +
        "Alice,92,Engineering\n" +
        "Bob,78,Finance\n" +
        "Carol,85,Engineering\n" +
        "Dave,71,HR\n";

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncreasesRowCount()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_ValuesAccessibleViaGetRow()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Eve", row);
    }

    [Fact]
    public void AddRow_MultipleRows_CountCorrect()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        doc.AddRow(new[] { "Frank", "88", "Engineering" });
        doc.AddRow(new[] { "Grace", "76", "HR" });
        Assert.Equal(before + 3, doc.RowCount);
    }

    [Fact]
    public void AddRow_ThenGetColumnValues_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Zara", "99", "Research" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Zara", names);
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecreasesRowCount()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_CorrectRowRemoved()
    {
        var doc = LoadSample();
        doc.RemoveRow(0); // Remove Alice
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void RemoveRow_LastRow_Works()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(before - 1);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_LeavesOthersIntact()
    {
        var doc = LoadSample();
        doc.RemoveRow(1); // Remove Bob
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void RemoveRow_Multiple_CountCorrect()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(0);
        doc.RemoveRow(0);
        Assert.Equal(before - 2, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.RowCount, doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_ContainsAllNames()
    {
        var doc = LoadSample();
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_IncludesNew()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Eve", names);
        Assert.Equal(5, names.Count);
    }

    [Fact]
    public void GetColumnValues_AfterRemoveRow_ExcludesRemoved()
    {
        var doc = LoadSample();
        doc.RemoveRow(0); // Remove Alice
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Alice", names);
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "ALICE_NEW");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_NEW", names);
        Assert.DoesNotContain("Alice", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_AddRow_GetColumnValues_RemoveRow_SaveToFile_LoadFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.RowCount);

        // AddRow × 2
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        doc.AddRow(new[] { "Frank", "88", "Engineering" });
        Assert.Equal(6, doc.RowCount);

        // GetColumnValues — all 6 names
        var names = doc.GetColumnValues("Name");
        Assert.Equal(6, names.Count);
        Assert.Contains("Eve", names);
        Assert.Contains("Frank", names);
        Assert.Contains("Alice", names);

        // GetColumnValues for Dept
        var depts = doc.GetColumnValues("Dept");
        Assert.Equal(6, depts.Count);
        Assert.Contains("Engineering", depts);

        // RemoveRow — remove Dave (index 3)
        doc.RemoveRow(3); // Dave is 4th row (0-indexed)
        Assert.Equal(5, doc.RowCount);

        // GetColumnValues — Dave removed
        var updatedNames = doc.GetColumnValues("Name");
        Assert.Equal(5, updatedNames.Count);
        Assert.DoesNotContain("Dave", updatedNames);
        Assert.Contains("Alice", updatedNames);
        Assert.Contains("Frank", updatedNames);

        // SetCellValue and verify
        doc.SetCellValue(0, "Name", "ALICE_V2");
        var finalNames = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_V2", finalNames);

        // SaveToFile
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Contains("ALICE_V2", loadedNames);
        Assert.DoesNotContain("Dave", loadedNames);
        Assert.Contains("Frank", loadedNames);
    }
}
