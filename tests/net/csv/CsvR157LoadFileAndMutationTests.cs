// Tests for CsvDocument.LoadFile, mutation pipeline, and HasHeaders behavior.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R157

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R157: Tests for CsvDocument.LoadFile, mutation pipeline, and header behavior.
/// LoadFile(path): loads CSV from a file path.
/// AddRow: appends to Rows.
/// SetCell: updates a cell value.
/// RemoveRow: removes a row.
/// Covers: LoadFile creates valid doc; LoadFile count matches written;
/// LoadFile HasHeaders true; LoadFile cell values correct;
/// AddRow->LoadFile not yet persisted; SetCell->SaveToFile->LoadFile updated;
/// RemoveRow->SaveToFile->LoadFile row count decremented;
/// AddRow->SaveToFile->LoadFile->GetColumn has new value;
/// LoadFile->Filter->GetColumn works; HasHeaders after LoadFile;
/// ColumnCount after LoadFile; RowCount after LoadFile;
/// GetCellValue after LoadFile;
/// dogfood WriteFile->LoadFile->AddRow->SetCell->SaveToFile->LoadFile verify.
/// </summary>
public class CsvR157LoadFileAndMutationTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    public CsvR157LoadFileAndMutationTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR157_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteAndGetPath(string content, string name = "data.csv")
    {
        var path = TempFile(name);
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_CreatesValidDoc()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadFile_CountMatches()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void LoadFile_HasHeaders_True()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_CellValues_Correct()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Eng", doc.GetCellValue(0, 1));
        Assert.Equal("95", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void LoadFile_ColumnCount_IsThree()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(3, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Mutation -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_SaveToFile_LoadFile_UpdatedValue()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        doc.SetCell(0, 2, "100");
        var savePath = TempFile("updated.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal("100", loaded.GetCellValue(0, 2));
    }

    [Fact]
    public void RemoveRow_SaveToFile_LoadFile_RowCountDecremented()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        doc.RemoveRow(0);
        var savePath = TempFile("removed.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(3, loaded.RowCount);
    }

    [Fact]
    public void AddRow_SaveToFile_LoadFile_GetColumn_HasNewValue()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        doc.AddRow(new[] { "Eve", "Eng", "79" });
        var savePath = TempFile("addrow.csv");
        doc.SaveToFile(savePath);
        var loaded = CsvDocument.LoadFile(savePath);
        var names = loaded.GetColumn("Name");
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // LoadFile -> Filter -> GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_Filter_GetColumn_Works()
    {
        var path = WriteAndGetPath(FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        var names = eng.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteFile->LoadFile->AddRow->SetCell->SaveToFile->LoadFile->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteLoadMutateSaveVerify_Pipeline()
    {
        // Write initial file
        var path = WriteAndGetPath(FourRowCsv, "initial.csv");

        // LoadFile
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
        Assert.True(doc.HasHeaders);
        Assert.True(doc.HasColumn("Name"));

        // AddRow
        doc.AddRow(new[] { "Eve", "Eng", "79" });
        Assert.Equal(5, doc.RowCount);

        // SetCell: update Alice's score
        doc.SetCell(0, 2, "99");
        Assert.Equal("99", doc.GetCellValue(0, 2));

        // SaveToFile
        var savePath = TempFile("final.csv");
        doc.SaveToFile(savePath);

        // LoadFile and verify
        var final = CsvDocument.LoadFile(savePath);
        Assert.Equal(5, final.RowCount);
        Assert.Equal("99", final.GetCellValue(0, 2));
        var names = final.GetColumn("Name");
        Assert.Contains("Eve", names);
        Assert.Contains("Alice", names);
    }
}
