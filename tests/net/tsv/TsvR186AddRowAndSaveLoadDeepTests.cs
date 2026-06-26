// Tests for TsvDocument.AddRow, RemoveRow, SaveToFile/LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R186

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R186: Tests for TsvDocument.AddRow, RemoveRow, SaveToFile/LoadFile deeper coverage.
/// AddRow(values): appends a new row with given values.
/// RemoveRow(rowIndex): removes the row at the given 0-based index.
/// SaveToFile(path): saves the document as a TSV file.
/// LoadFile(path): loads a TsvDocument from a TSV file.
/// Covers: AddRow increases RowCount; AddRow values in GetRow; AddRow multiple count correct;
/// AddRow then GetColumnValues includes new; RemoveRow decreases RowCount;
/// RemoveRow correct row removed; RemoveRow leaves others; RemoveRow last row;
/// SaveToFile creates file; SaveToFile non-empty; SaveToFile headers in file;
/// LoadFile non-null; LoadFile RowCount preserved; LoadFile headers preserved;
/// LoadFile data via GetCell; LoadFile then AddRow and save again;
/// dogfood LoadContent→AddRow×2→RemoveRow→SaveToFile→LoadFile→GetColumnValues pipeline.
/// </summary>
public class TsvR186AddRowAndSaveLoadDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR186AddRowAndSaveLoadDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR186_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tScore\tDept\n" +
        "Alice\t92\tEngineering\n" +
        "Bob\t78\tFinance\n" +
        "Carol\t85\tEngineering\n" +
        "Dave\t71\tHR\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
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
    public void AddRow_ValuesInGetRow()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Eve", row);
        Assert.Contains("90", row);
    }

    [Fact]
    public void AddRow_Multiple_CountCorrect()
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
        doc.RemoveRow(0); // Alice
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void RemoveRow_LeavesOthers()
    {
        var doc = LoadSample();
        doc.RemoveRow(1); // Bob
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    [Fact]
    public void RemoveRow_LastRow_Works()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.RemoveRow(before - 1);
        Assert.Equal(before - 1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = LoadSample();
        var path = TempFile("saved.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmpty()
    {
        var doc = LoadSample();
        var path = TempFile("nonempty.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_HasHeaders()
    {
        var doc = LoadSample();
        var path = TempFile("headers.tsv");
        TsvWriter.WriteToFile(doc, path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Name") || content.Contains("Score"));
    }

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = LoadSample();
        var path = TempFile("load.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.NotNull(TsvDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_RowCountPreserved()
    {
        var doc = LoadSample();
        var path = TempFile("rowcount.tsv");
        TsvWriter.WriteToFile(doc, path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_HeadersPreserved()
    {
        var doc = LoadSample();
        var path = TempFile("hdrpreserve.tsv");
        TsvWriter.WriteToFile(doc, path);
        var loaded = TsvDocument.LoadFile(path);
        var headers = loaded.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void LoadFile_DataViaGetCell()
    {
        var doc = LoadSample();
        var path = TempFile("getcell.tsv");
        TsvWriter.WriteToFile(doc, path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCell(0, "Name"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_AddRow_RemoveRow_SaveToFile_LoadFile_GetColumnValues_Pipeline()
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

        // RemoveRow — remove Bob (index 1)
        doc.RemoveRow(1);
        Assert.Equal(5, doc.RowCount);

        // GetColumnValues — Bob removed
        var updatedNames = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Bob", updatedNames);
        Assert.Contains("Alice", updatedNames);
        Assert.Contains("Frank", updatedNames);

        // SaveToFile
        var path = TempFile("dogfood.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);

        // GetColumnValues on loaded
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Equal(5, loadedNames.Count);
        Assert.Contains("Alice", loadedNames);
        Assert.Contains("Frank", loadedNames);
        Assert.DoesNotContain("Bob", loadedNames);

        // GetCell on loaded
        Assert.Equal("Alice", loaded.GetCell(0, "Name"));
        Assert.Equal("Engineering", loaded.GetCell(0, "Dept"));

        // AddRow to loaded and save again
        loaded.AddRow(new[] { "Zara", "99", "Research" });
        Assert.Equal(6, loaded.RowCount);
        var path2 = TempFile("dogfood2.tsv");
        TsvWriter.WriteToFile(loaded, path2);
        var final = TsvDocument.LoadFile(path2);
        Assert.Equal(6, final.RowCount);
        Assert.Contains("Zara", final.GetColumnValues("Name"));
    }
}
