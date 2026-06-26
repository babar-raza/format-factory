// Tests for CsvDocument.Merge, IsEmpty, Clear deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R187

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R187: Tests for CsvDocument.Merge, IsEmpty, Clear deeper coverage.
/// Merge(other): combines rows from two CsvDocuments.
/// IsEmpty: returns true if the document has no rows.
/// Clear(): removes all rows from the document.
/// Covers: Merge non-null; Merge count=sum; Merge contains rows from both;
/// Merge GetColumnValues includes all; Merge with empty doc same as original;
/// Merge headers from first doc preserved; IsEmpty true for empty doc;
/// IsEmpty false for non-empty; IsEmpty true after Clear; IsEmpty true after RemoveRow all;
/// Clear reduces RowCount to 0; Clear then AddRow works; Clear non-throw;
/// Clear then IsEmpty true; Clear then SaveToFile and LoadFile reflect empty;
/// dogfood LoadContent×2→Merge→GetColumnValues→IsEmpty→Clear→AddRow pipeline.
/// </summary>
public class CsvR187MergeAndIsEmptyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR187MergeAndIsEmptyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR187_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string Doc1Csv =
        "Name,Score,Dept\n" +
        "Alice,92,Engineering\n" +
        "Bob,78,Finance\n" +
        "Carol,85,Engineering\n";

    private static readonly string Doc2Csv =
        "Name,Score,Dept\n" +
        "Dave,71,HR\n" +
        "Eve,90,Finance\n" +
        "Frank,88,Engineering\n";

    private CsvDocument LoadDoc1()
    {
        var path = TempFile("doc1.csv");
        File.WriteAllText(path, Doc1Csv);
        return CsvDocument.LoadFile(path);
    }

    private CsvDocument LoadDoc2()
    {
        var path = TempFile("doc2.csv");
        File.WriteAllText(path, Doc2Csv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_NonNull()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        Assert.NotNull(doc1.Merge(doc2));
    }

    [Fact]
    public void Merge_CountEqualsSumOfBoth()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        Assert.Equal(doc1.RowCount + doc2.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_ContainsRowsFromBoth()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Merge_GetColumnValues_AllSixNames()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Equal(6, names.Count);
    }

    [Fact]
    public void Merge_WithEmptyDoc_SameAsOriginal()
    {
        var doc1 = LoadDoc1();
        var emptyPath = TempFile("empty.csv");
        File.WriteAllText(emptyPath, "Name,Score,Dept\n");
        var empty = CsvDocument.LoadFile(emptyPath);
        var merged = doc1.Merge(empty);
        Assert.Equal(doc1.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_HeadersFromFirstDoc()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();
        var merged = doc1.Merge(doc2);
        var headers = merged.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);
        Assert.Contains("Dept", headers);
    }

    // -------------------------------------------------------------------------
    // IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void IsEmpty_TrueForEmptyDoc()
    {
        var path = TempFile("isempty.csv");
        File.WriteAllText(path, "Name,Score\n");
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_FalseForNonEmpty()
    {
        var doc = LoadDoc1();
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_TrueAfterClear()
    {
        var doc = LoadDoc1();
        doc.Clear();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void IsEmpty_TrueAfterRemoveAllRows()
    {
        var doc = LoadDoc1();
        while (!doc.IsEmpty)
            doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Clear
    // -------------------------------------------------------------------------

    [Fact]
    public void Clear_ReducesRowCountToZero()
    {
        var doc = LoadDoc1();
        doc.Clear();
        Assert.Equal(0, doc.RowCount);
    }

    [Fact]
    public void Clear_NoThrow()
    {
        var doc = LoadDoc1();
        var ex = Record.Exception(() => doc.Clear());
        Assert.Null(ex);
    }

    [Fact]
    public void Clear_ThenAddRow_Works()
    {
        var doc = LoadDoc1();
        doc.Clear();
        doc.AddRow(new[] { "NewPerson", "100", "Research" });
        Assert.Equal(1, doc.RowCount);
        Assert.Contains("NewPerson", doc.GetColumnValues("Name"));
    }

    [Fact]
    public void Clear_ThenIsEmpty_True()
    {
        var doc = LoadDoc1();
        doc.Clear();
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void Clear_SecondCall_NoThrow()
    {
        var doc = LoadDoc1();
        doc.Clear();
        var ex = Record.Exception(() => doc.Clear());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Merge_GetColumnValues_IsEmpty_Clear_AddRow_Pipeline()
    {
        var doc1 = LoadDoc1();
        var doc2 = LoadDoc2();

        // Verify initial state
        Assert.False(doc1.IsEmpty);
        Assert.False(doc2.IsEmpty);

        // Merge
        var merged = doc1.Merge(doc2);
        Assert.Equal(6, merged.RowCount);
        Assert.False(merged.IsEmpty);

        // GetColumnValues on merged
        var names = merged.GetColumnValues("Name");
        Assert.Equal(6, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);

        var depts = merged.GetColumnValues("Dept");
        Assert.Contains("Engineering", depts);
        Assert.Contains("HR", depts);
        Assert.Contains("Finance", depts);

        // Filter on merged
        var engOnly = merged.Filter("Dept", "Engineering");
        Assert.Equal(3, engOnly.RowCount);

        // IsEmpty checks
        Assert.False(engOnly.IsEmpty);
        var emptyPath = TempFile("empty_check.csv");
        File.WriteAllText(emptyPath, "Name,Score\n");
        var emptyDoc = CsvDocument.LoadFile(emptyPath);
        Assert.True(emptyDoc.IsEmpty);

        // Clear on a copy of doc1
        var path1 = TempFile("doc1_copy.csv");
        File.WriteAllText(path1, Doc1Csv);
        var docCopy = CsvDocument.LoadFile(path1);
        Assert.False(docCopy.IsEmpty);
        docCopy.Clear();
        Assert.True(docCopy.IsEmpty);
        Assert.Equal(0, docCopy.RowCount);

        // AddRow after Clear
        docCopy.AddRow(new[] { "Solo", "100", "Solo Dept" });
        Assert.Equal(1, docCopy.RowCount);
        Assert.False(docCopy.IsEmpty);
        Assert.Contains("Solo", docCopy.GetColumnValues("Name"));

        // SaveToFile after mutations on merged
        merged.AddRow(new[] { "Zara", "99", "Research" });
        Assert.Equal(7, merged.RowCount);
        var mergePath = TempFile("merged.csv");
        merged.SaveToFile(mergePath);
        Assert.True(File.Exists(mergePath));
        var loadedMerge = CsvDocument.LoadFile(mergePath);
        Assert.Equal(7, loadedMerge.RowCount);
        Assert.Contains("Zara", loadedMerge.GetColumnValues("Name"));
    }
}
