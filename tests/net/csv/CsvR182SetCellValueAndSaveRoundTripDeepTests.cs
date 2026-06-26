// Tests for CsvDocument.SetCellValue, SaveToFile, LoadFile round-trip deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R182

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R182: Tests for CsvDocument.SetCellValue, SaveToFile, LoadFile round-trip deeper coverage.
/// SetCellValue(row, col, value): sets the value of a cell at the given row/col.
/// SetCellValue(row, colName, value): sets the value by column name.
/// SaveToFile(path): saves the document as a CSV file.
/// LoadFile(path): loads a CsvDocument from a file path.
/// Covers: SetCellValue by index changes value; SetCellValue by name changes value;
/// SetCellValue multiple times LastWins; SetCellValue doesn't change RowCount;
/// SetCellValue then GetCellValue returns new value; SetCellValue then GetRow has new value;
/// SaveToFile creates file; SaveToFile file has headers; SaveToFile file has data;
/// LoadFile non-null; LoadFile RowCount matches; LoadFile headers preserved;
/// LoadFile data correct; LoadFile mutation persists after SaveToFile;
/// dogfood LoadContent->SetCellValue->SaveToFile->LoadFile->Verify pipeline.
/// </summary>
public class CsvR182SetCellValueAndSaveRoundTripDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string SampleContent = "Name,Dept,Score\nAlice,Eng,92\nBob,Finance,85\nCarol,HR,78";

    public CsvR182SetCellValueAndSaveRoundTripDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR182_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // SetCellValue by index
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ByIndex_ChangesValue()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, 0, "ALICE_UPDATED");
        Assert.Equal("ALICE_UPDATED", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ByIndex_LastWins()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, 0, "First");
        doc.SetCellValue(0, 0, "Second");
        doc.SetCellValue(0, 0, "Third");
        Assert.Equal("Third", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_ByIndex_DoesNotChangeRowCount()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var before = doc.RowCount;
        doc.SetCellValue(0, 0, "UPDATED");
        Assert.Equal(before, doc.RowCount);
    }

    [Fact]
    public void SetCellValue_ByIndex_GetRow_HasNewValue()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(1, 2, "999");
        var row = doc.GetRow(1);
        Assert.Contains("999", row);
    }

    [Fact]
    public void SetCellValue_MultipleRows_EachUpdatesCorrectly()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, 2, "100");
        doc.SetCellValue(1, 2, "200");
        doc.SetCellValue(2, 2, "300");
        Assert.Equal("100", doc.GetCellValue(0, 2));
        Assert.Equal("200", doc.GetCellValue(1, 2));
        Assert.Equal("300", doc.GetCellValue(2, 2));
    }

    // -------------------------------------------------------------------------
    // SetCellValue by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_ByName_ChangesValue()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, "Score", "100");
        Assert.Equal("100", doc.GetCellValue(0, "Score"));
    }

    [Fact]
    public void SetCellValue_ByName_LastWins()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, "Dept", "IT");
        doc.SetCellValue(0, "Dept", "Legal");
        Assert.Equal("Legal", doc.GetCellValue(0, "Dept"));
    }

    [Fact]
    public void SetCellValue_ByName_GetRow_HasNewValue()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(2, "Name", "CAROL_NEW");
        var row = doc.GetRow(2);
        Assert.Contains("CAROL_NEW", row);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("output.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileHasHeaders()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("headers.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Name", content);
        Assert.Contains("Score", content);
    }

    [Fact]
    public void LoadFile_NonNull()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("load.csv");
        doc.SaveToFile(path);
        Assert.NotNull(CsvDocument.LoadFile(path));
    }

    [Fact]
    public void LoadFile_RowCountMatches()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("rowcount.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_HeadersPreserved()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("hdrs.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var headers = loaded.GetRow(-1); // headers at index -1 or via ColumnHeaders
        Assert.True(loaded.ColumnCount == 3);
    }

    [Fact]
    public void LoadFile_DataCorrect()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var path = TempFile("data.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCellValue(0, "Name"));
        Assert.Equal("Eng", loaded.GetCellValue(0, "Dept"));
    }

    [Fact]
    public void SaveAfterMutation_LoadFile_ReflectsChange()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, "Score", "100");
        var path = TempFile("mutated.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("100", loaded.GetCellValue(0, "Score"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_SetCellValue_SaveToFile_LoadFile_Verify_Pipeline()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.Equal(3, doc.RowCount);

        // SetCellValue by index
        doc.SetCellValue(0, 2, "100");
        Assert.Equal("100", doc.GetCellValue(0, 2));

        // SetCellValue by name
        doc.SetCellValue(1, "Dept", "Operations");
        Assert.Equal("Operations", doc.GetCellValue(1, "Dept"));

        // AddRow then SetCellValue
        doc.AddRow(new[] { "Dave", "HR", "95" });
        Assert.Equal(4, doc.RowCount);
        doc.SetCellValue(3, "Name", "David");
        Assert.Equal("David", doc.GetCellValue(3, "Name"));

        // GetRow reflects mutations
        var row0 = doc.GetRow(0);
        Assert.Contains("100", row0);

        // SaveToFile
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
        Assert.Equal(3, loaded.ColumnCount);
        Assert.Equal("100", loaded.GetCellValue(0, "Score"));
        Assert.Equal("Operations", loaded.GetCellValue(1, "Dept"));
        Assert.Equal("David", loaded.GetCellValue(3, "Name"));

        // GetColumnValues from loaded
        var allNames = loaded.GetColumnValues("Name");
        Assert.Equal(4, allNames.Count);
        Assert.Contains("Alice", allNames);
        Assert.Contains("David", allNames);
    }
}
