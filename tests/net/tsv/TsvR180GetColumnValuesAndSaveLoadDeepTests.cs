// Tests for TsvDocument.GetColumnValues, SaveToFile, LoadFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R180

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R180: Tests for TsvDocument.GetColumnValues, SaveToFile, LoadFile deeper coverage.
/// GetColumnValues(colName): returns all values in the named column.
/// SaveToFile(path): saves the document as a TSV file.
/// LoadFile(path): loads a TsvDocument from a file.
/// Covers: GetColumnValues non-null; GetColumnValues count equals RowCount;
/// GetColumnValues all present; GetColumnValues after SetCellValue reflects change;
/// GetColumnValues after AddRow includes new value; GetColumnValues after Filter reduces;
/// SaveToFile creates file; SaveToFile file is non-empty;
/// LoadFile non-null; LoadFile RowCount matches; LoadFile ColumnCount matches;
/// LoadFile headers preserved; LoadFile data accessible via GetCell;
/// dogfood LoadContent->GetColumnValues->SaveToFile->LoadFile->Verify pipeline.
/// </summary>
public class TsvR180GetColumnValuesAndSaveLoadDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string Doc1Content = "Name\tDept\tScore\nAlice\tEng\t92\nBob\tFinance\t85\nCarol\tEng\t78\nDave\tHR\t91";

    public TsvR180GetColumnValuesAndSaveLoadDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR180_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal(doc.RowCount, doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_AllPresent()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnValues_DeptColumn()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var depts = doc.GetColumnValues("Dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);
    }

    [Fact]
    public void GetColumnValues_ScoreColumn_ContainsExpected()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var scores = doc.GetColumnValues("Score");
        Assert.Contains("92", scores);
        Assert.Contains("85", scores);
        Assert.Equal(4, scores.Count);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_ReflectsChange()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        doc.SetCellValue(0, "Score", "100");
        var scores = doc.GetColumnValues("Score");
        Assert.Contains("100", scores);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_IncludesNewValue()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        doc.AddRow(new[] { "Eve", "Legal", "95" });
        var names = doc.GetColumnValues("Name");
        Assert.Equal(5, names.Count);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_ReducesCount()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var names = engOnly.GetColumnValues("Name");
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("output.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("load.tsv");
        doc.SaveToFile(path);
        Assert.NotNull(TsvDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_RowCountMatches()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("rowcount.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_ColumnCountMatches()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("colcount.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.ColumnCount, loaded.ColumnCount);
    }

    [Fact]
    public void LoadFile_HeadersPreserved()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("headers.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("Name", loaded.Headers);
        Assert.Contains("Dept", loaded.Headers);
        Assert.Contains("Score", loaded.Headers);
    }

    [Fact]
    public void LoadFile_DataAccessibleViaGetCell()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        var path = TempFile("data.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCell(0, "Name"));
        Assert.Equal("Eng", loaded.GetCell(0, "Dept"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetColumnValues_SaveToFile_LoadFile_Verify_Pipeline()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal(4, doc.RowCount);

        // GetColumnValues for all columns
        var names = doc.GetColumnValues("Name");
        Assert.Equal(4, names.Count);
        Assert.Contains("Dave", names);

        var depts = doc.GetColumnValues("Dept");
        Assert.Equal(4, depts.Count);
        Assert.Contains("Finance", depts);

        // Mutation
        doc.AddRow(new[] { "Zara", "Legal", "99" });
        var namesAfter = doc.GetColumnValues("Name");
        Assert.Equal(5, namesAfter.Count);
        Assert.Contains("Zara", namesAfter);

        // SaveToFile
        var path = TempFile("dogfood.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);
        Assert.Equal(3, loaded.ColumnCount);
        Assert.Contains("Name", loaded.Headers);

        // GetColumnValues on loaded
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Equal(5, loadedNames.Count);
        Assert.Contains("Zara", loadedNames);
        Assert.Contains("Alice", loadedNames);

        // Filter on loaded
        var engOnly = loaded.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(2, engOnly.RowCount);
        var engNames = engOnly.GetColumnValues("Name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
    }
}
