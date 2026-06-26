// Tests for CsvDocument.LoadFile, CsvWriter, CsvReader deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R150

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R150: Tests for CsvDocument.LoadFile, CsvWriter, CsvReader deeper coverage.
/// LoadFile(path): loads CSV from file.
/// CsvWriter: writes CSV rows to file.
/// CsvReader: reads CSV rows from file.
/// Covers: LoadFile count matches; LoadFile cell values; LoadFile hasHeaders=true;
/// LoadFile hasHeaders=false RowCount; CsvWriter.WriteRows creates file;
/// CsvWriter output readable by LoadFile; CsvReader.ReadRows returns rows;
/// CsvReader first row matches expected; CsvReader hasHeaders=true;
/// LoadFile->Filter->SaveToFile->LoadFile chain; RowCount after Filter;
/// GetColumn after LoadFile; dogfood full file pipeline.
/// </summary>
public class CsvR150LoadFileAndWriterTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR150LoadFileAndWriterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR150_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    private string WriteThreeRowFile(string name)
    {
        var path = TempFile(name);
        File.WriteAllText(path, ThreeRowCsv);
        return path;
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_CountMatches()
    {
        var path = WriteThreeRowFile("count.csv");
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void LoadFile_CellValuesCorrect()
    {
        var path = WriteThreeRowFile("cells.csv");
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void LoadFile_WithHeaders_HasHeadersTrue()
    {
        var path = WriteThreeRowFile("wh.csv");
        var doc = CsvDocument.LoadFile(path, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_NoHeaders_RowCountIncludesHeaderRow()
    {
        var path = WriteThreeRowFile("nh.csv");
        var doc = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(4, doc.RowCount); // header row + 3 data rows
    }

    [Fact]
    public void LoadFile_GetColumnValues()
    {
        var path = WriteThreeRowFile("cols.csv");
        var doc = CsvDocument.LoadFile(path);
        var names = doc.GetColumn(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // CsvWriter
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvWriter_WriteRows_CreatesFile()
    {
        var path = TempFile("writer.csv");
        var writer = new CsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" }
        }, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void CsvWriter_WriteRows_OutputReadableByLoadFile()
    {
        var path = TempFile("readable.csv");
        var writer = new CsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" },
            new[] { "Bob", "82" }
        }, path);
        var doc = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, doc.RowCount);
        Assert.Equal("Alice", doc.GetCellValue(1, 0));
    }

    // -------------------------------------------------------------------------
    // CsvReader
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvReader_ReadRows_ReturnsRows()
    {
        var path = WriteThreeRowFile("reader.csv");
        var reader = new CsvReader();
        var rows = reader.ReadRows(path);
        Assert.NotEmpty(rows);
    }

    [Fact]
    public void CsvReader_ReadRows_FirstRowIsHeader()
    {
        var path = WriteThreeRowFile("firstrow.csv");
        var reader = new CsvReader();
        var rows = reader.ReadRows(path);
        Assert.Contains("Name", rows[0]);
    }

    [Fact]
    public void CsvReader_ReadRows_CountMatchesLines()
    {
        var path = WriteThreeRowFile("linecount.csv");
        var reader = new CsvReader();
        var rows = reader.ReadRows(path);
        Assert.Equal(4, rows.Count); // header + 3 data rows
    }

    // -------------------------------------------------------------------------
    // Chain: LoadFile->Filter->SaveToFile->LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_Filter_SaveToFile_LoadFile_Chain()
    {
        var path1 = WriteThreeRowFile("step1.csv");
        var doc = CsvDocument.LoadFile(path1);

        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        var path2 = TempFile("step2.csv");
        eng.SaveToFile(path2);

        var reloaded = CsvDocument.LoadFile(path2, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Contains("Alice", reloaded.GetColumn(0));
        Assert.Contains("Carol", reloaded.GetColumn(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Write->Read->Load->Filter->Save->Reload pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteReadLoadFilterSavePipeline()
    {
        // Write with CsvWriter
        var path1 = TempFile("dogfood.csv");
        var writer = new CsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Dept", "Score" },
            new[] { "Alice", "Eng", "95" },
            new[] { "Bob", "Finance", "82" },
            new[] { "Carol", "Eng", "88" },
            new[] { "Dave", "Finance", "91" }
        }, path1);

        // Read with CsvReader
        var reader = new CsvReader();
        var rows = reader.ReadRows(path1);
        Assert.Equal(5, rows.Count);

        // Load with CsvDocument
        var doc = CsvDocument.LoadFile(path1, hasHeaders: false);
        Assert.Equal(5, doc.RowCount);

        // Filter Finance
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, finance.RowCount);

        // Save and reload
        var path2 = TempFile("finance.csv");
        finance.SaveToFile(path2);
        var final = CsvDocument.LoadFile(path2, hasHeaders: false);
        Assert.Equal(2, final.RowCount);
        Assert.Contains("Bob", final.GetColumn(0));
        Assert.Contains("Dave", final.GetColumn(0));
    }
}
