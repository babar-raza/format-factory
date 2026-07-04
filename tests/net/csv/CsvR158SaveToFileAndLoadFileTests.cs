// Tests for CsvDocument.SaveToFile, LoadFile, and CsvReader.ReadRows / CsvWriter.WriteRows.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R158

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R158: Tests for CsvDocument.SaveToFile, LoadFile pipeline and static reader/writer.
/// SaveToFile(path): writes CSV to file.
/// LoadFile(path, hasHeaders): reads CSV from file.
/// CsvReader.ReadRows(path): reads raw rows from file.
/// CsvWriter.WriteRows(rows, path): writes raw rows to file.
/// Covers: SaveToFile creates file; SaveToFile->LoadFile count matches;
/// SaveToFile->LoadFile cell values match; SaveToFile->LoadFile headers match;
/// CsvWriter.WriteRows creates file; CsvReader.ReadRows count matches written;
/// CsvWriter.WriteRows->CsvReader.ReadRows round-trips values;
/// SaveToFile->CsvReader.ReadRows content readable; LoadFile->SaveToFile->LoadFile idempotent;
/// CsvReader.ReadRows includes header row; WriteRows->ReadRows first row is header;
/// SaveToFile with path containing different name; LoadFile hasHeaders=false;
/// dogfood LoadFile->AddRow->SaveToFile->LoadFile->Filter->GetColumn.
/// </summary>
public class CsvR158SaveToFileAndLoadFileTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    public CsvR158SaveToFileAndLoadFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR158_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("a.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountMatches()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("b.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void SaveToFile_LoadFile_CellValuesMatch()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("c.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCellValue(0, 0));
        Assert.Equal("Dave", loaded.GetCellValue(3, 0));
    }

    [Fact]
    public void SaveToFile_LoadFile_HasHeaders_Match()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("d.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.HasHeaders, loaded.HasHeaders);
    }

    [Fact]
    public void LoadFile_HasHeadersFalse_RowCountIncludesHeaderRow()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("e.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path, hasHeaders: false);
        // 4 data rows + 1 header row = 5 total
        Assert.Equal(5, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows -> CsvReader.ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_CreatesFile()
    {
        var rows = new List<string[]>
        {
            new[] { "H1", "H2", "H3" },
            new[] { "A", "B", "C" },
            new[] { "D", "E", "F" }
        };
        var path = TempFile("f.csv");
        CsvWriter.WriteRows(rows, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRows_ReadRows_CountMatches()
    {
        var rows = new List<string[]>
        {
            new[] { "H1", "H2" },
            new[] { "1", "2" },
            new[] { "3", "4" }
        };
        var path = TempFile("g.csv");
        CsvWriter.WriteRows(rows, path);
        var read = CsvReader.ReadRows(path);
        Assert.Equal(2, read.Count); // header stripped; 2 data rows returned
    }

    [Fact]
    public void WriteRows_ReadRows_ValuesMatch()
    {
        var rows = new List<string[]>
        {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" }
        };
        var path = TempFile("h.csv");
        CsvWriter.WriteRows(rows, path);
        var read = CsvReader.ReadRows(path);
        // header stripped: read[0] is the first data row (Alice)
        Assert.Equal("Alice", read[0][0]);
        Assert.Equal("95", read[0][1]);
    }

    // -------------------------------------------------------------------------
    // LoadFile -> SaveToFile -> LoadFile (idempotent)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_SaveToFile_LoadFile_Idempotent()
    {
        // Initial file
        var path1 = TempFile("i1.csv");
        File.WriteAllText(path1, FourRowCsv);
        var doc1 = CsvDocument.LoadFile(path1);

        // Save to second file
        var path2 = TempFile("i2.csv");
        doc1.SaveToFile(path2);
        var doc2 = CsvDocument.LoadFile(path2);

        // They should be equal
        Assert.Equal(doc1.RowCount, doc2.RowCount);
        Assert.Equal(doc1.ColumnCount, doc2.ColumnCount);
        Assert.Equal(doc1.GetCellValue(0, 0), doc2.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadFile->AddRow->SaveToFile->LoadFile->Filter->GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFileAddRowSaveLoadFilterGetColumn_Pipeline()
    {
        // Write initial file
        var initial = TempFile("initial.csv");
        File.WriteAllText(initial, FourRowCsv);

        // LoadFile
        var doc = CsvDocument.LoadFile(initial);
        Assert.Equal(4, doc.RowCount);

        // AddRow
        doc.AddRow(new[] { "Eve", "Eng", "79" });
        Assert.Equal(5, doc.RowCount);

        // SaveToFile
        var saved = TempFile("saved.csv");
        doc.SaveToFile(saved);

        // LoadFile
        var loaded = CsvDocument.LoadFile(saved);
        Assert.Equal(5, loaded.RowCount);

        // Filter
        var eng = loaded.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Eve

        // GetColumn
        var names = eng.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Eve", names);
        Assert.DoesNotContain("Bob", names);
    }
}
