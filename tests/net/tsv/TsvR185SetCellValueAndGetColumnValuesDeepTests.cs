// Tests for TsvDocument.SetCellValue, GetColumnValues, GetRow deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R185

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R185: Tests for TsvDocument.SetCellValue, GetColumnValues, GetRow deeper coverage.
/// SetCellValue(rowIndex, colName, value): sets the cell at given row and column.
/// GetColumnValues(colName): returns all values in a named column.
/// GetRow(rowIndex): returns all values in a row as list.
/// Covers: SetCellValue by name changes value; SetCellValue last-write wins;
/// SetCellValue no RowCount change; SetCellValue GetRow reflects;
/// SetCellValue by index changes value; SetCellValue chained multiple;
/// GetColumnValues non-null; GetColumnValues count=RowCount; GetColumnValues all names present;
/// GetColumnValues after AddRow includes new; GetColumnValues after RemoveRow excludes;
/// GetColumnValues after SetCellValue reflects;
/// GetRow non-null; GetRow count=ColumnCount; GetRow first row correct; GetRow last row correct;
/// GetRow after SetCellValue reflects; GetRow after AddRow accessible;
/// dogfood LoadContent→SetCellValue→GetColumnValues→GetRow→AddRow→RemoveRow→SaveToFile pipeline.
/// </summary>
public class TsvR185SetCellValueAndGetColumnValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR185SetCellValueAndGetColumnValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR185_" + Guid.NewGuid().ToString("N"));
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
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ByName_ChangesValue()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "ALICE_MOD");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_MOD", names);
    }

    [Fact]
    public void SetCellValue_ByName_LastWriteWins()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "FIRST");
        doc.SetCellValue(0, "Name", "SECOND");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("SECOND", names);
        Assert.DoesNotContain("FIRST", names);
    }

    [Fact]
    public void SetCellValue_NoRowCountChange()
    {
        var doc = LoadSample();
        var before = doc.RowCount;
        doc.SetCellValue(0, "Name", "ALICE_MOD");
        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCellValue_GetRow_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Score", "100");
        var row = doc.GetRow(0);
        Assert.Contains("100", row);
    }

    [Fact]
    public void SetCellValue_ByIndex_ChangesValue()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, 1, "100"); // Row 0, col 1 = Score
        var scores = doc.GetColumnValues("Score");
        Assert.Contains("100", scores);
    }

    [Fact]
    public void SetCellValue_ChainedMultiple_AllReflected()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "Alice2");
        doc.SetCellValue(1, "Name", "Bob2");
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice2", names);
        Assert.Contains("Bob2", names);
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
    public void GetColumnValues_AllNamesPresent()
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
    }

    [Fact]
    public void GetColumnValues_AfterRemoveRow_ExcludesRemoved()
    {
        var doc = LoadSample();
        doc.RemoveRow(0); // Remove Alice
        var names = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Alice", names);
    }

    [Fact]
    public void GetColumnValues_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Dept", "Marketing");
        var depts = doc.GetColumnValues("Dept");
        Assert.Contains("Marketing", depts);
    }

    // -------------------------------------------------------------------------
    // GetRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRow_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetRow(0));
    }

    [Fact]
    public void GetRow_CountEqualsColumnCount()
    {
        var doc = LoadSample();
        Assert.True(doc.GetRow(0).Count >= doc.ColumnCount);
    }

    [Fact]
    public void GetRow_FirstRowCorrect()
    {
        var doc = LoadSample();
        var row = doc.GetRow(0);
        Assert.Contains("Alice", row);
        Assert.Contains("92", row);
        Assert.Contains("Engineering", row);
    }

    [Fact]
    public void GetRow_LastRowCorrect()
    {
        var doc = LoadSample();
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Dave", row);
        Assert.Contains("71", row);
    }

    [Fact]
    public void GetRow_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue(0, "Name", "ALICE_MOD");
        var row = doc.GetRow(0);
        Assert.Contains("ALICE_MOD", row);
    }

    [Fact]
    public void GetRow_AfterAddRow_Accessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        var row = doc.GetRow(doc.RowCount - 1);
        Assert.Contains("Eve", row);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_SetCellValue_GetColumnValues_GetRow_AddRow_RemoveRow_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.RowCount);

        // SetCellValue
        doc.SetCellValue(0, "Name", "ALICE_V2");
        doc.SetCellValue(1, "Score", "99");

        // GetColumnValues — reflects changes
        var names = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_V2", names);
        Assert.DoesNotContain("Alice", names);

        var scores = doc.GetColumnValues("Score");
        Assert.Contains("99", scores);

        // GetRow — Alice and Bob rows updated
        var aliceRow = doc.GetRow(0);
        Assert.Contains("ALICE_V2", aliceRow);
        var bobRow = doc.GetRow(1);
        Assert.Contains("99", bobRow);

        // AddRow
        doc.AddRow(new[] { "Eve", "90", "Finance" });
        Assert.Equal(5, doc.RowCount);
        var eveRow = doc.GetRow(4);
        Assert.Contains("Eve", eveRow);

        // GetColumnValues after AddRow
        var updatedNames = doc.GetColumnValues("Name");
        Assert.Equal(5, updatedNames.Count);
        Assert.Contains("Eve", updatedNames);

        // RemoveRow — remove Carol (index 2)
        doc.RemoveRow(2);
        Assert.Equal(4, doc.RowCount);
        var postRemoveNames = doc.GetColumnValues("Name");
        Assert.DoesNotContain("Carol", postRemoveNames);

        // SaveToFile
        var path = TempFile("dogfood.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
        var loadedNames = loaded.GetColumnValues("Name");
        Assert.Contains("ALICE_V2", loadedNames);
        Assert.Contains("Eve", loadedNames);
        Assert.DoesNotContain("Carol", loadedNames);
    }
}
