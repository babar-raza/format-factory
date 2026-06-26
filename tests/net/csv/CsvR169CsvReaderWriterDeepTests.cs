// Tests for CsvReader.ReadRows, CsvWriter.WriteRows deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R169

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R169: Tests for CsvReader.ReadRows, CsvWriter.WriteRows deeper.
/// CsvReader.ReadRows(content): parses CSV string to list of row lists.
/// CsvReader.ReadRowsFromFile(path): reads from file.
/// CsvWriter.WriteRows(rows): serializes to CSV string.
/// CsvWriter.WriteRowsToFile(rows, path): writes to file.
/// Covers: ReadRows non-null; ReadRows count correct; ReadRows first row is header;
/// ReadRows all values accessible; ReadRows column order preserved;
/// ReadRowsFromFile count correct; ReadRowsFromFile values correct;
/// WriteRows non-null; WriteRows non-empty; WriteRows contains all values;
/// WriteRows->ReadRows round-trip count matches; WriteRowsToFile creates file;
/// WriteRowsToFile->ReadRowsFromFile count matches; WriteRows comma-separated;
/// ReadRows->CsvDocument.Load->Filter->WriteRows chain;
/// dogfood WriteRows->WriteRowsToFile->ReadRowsFromFile->CsvDocument.Load->Filter->Verify.
/// </summary>
public class CsvR169CsvReaderWriterDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly List<List<string>> SampleRows = new()
    {
        new() { "name", "dept", "salary" },
        new() { "Alice", "Eng", "95000" },
        new() { "Bob", "Finance", "82000" },
        new() { "Carol", "Eng", "88000" }
    };

    public CsvR169CsvReaderWriterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR169_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CsvReader.ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NonNull()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        Assert.NotNull(rows);
    }

    [Fact]
    public void ReadRows_CountCorrect()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        // 4 total lines (header + 3 data)
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRows_FirstRow_IsHeader()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        Assert.Contains("name", rows[0]);
        Assert.Contains("dept", rows[0]);
    }

    [Fact]
    public void ReadRows_AllValues_Accessible()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        var all = string.Join(" ", rows.SelectMany(r => r));
        Assert.Contains("Alice", all);
        Assert.Contains("Carol", all);
    }

    [Fact]
    public void ReadRows_ColumnOrder_Preserved()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        // Find Alice's row
        List<string>? aliceRow = null;
        foreach (var row in rows)
            if (row.Contains("Alice")) { aliceRow = row; break; }
        Assert.NotNull(aliceRow);
        Assert.Equal("Alice", aliceRow[0]);
        Assert.Equal("Eng", aliceRow[1]);
        Assert.Equal("95000", aliceRow[2]);
    }

    // -------------------------------------------------------------------------
    // CsvReader.ReadRowsFromFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_CountCorrect()
    {
        var path = TempFile("read.csv");
        CsvWriter.WriteRowsToFile(SampleRows, path);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRowsFromFile_ValuesCorrect()
    {
        var path = TempFile("vals.csv");
        CsvWriter.WriteRowsToFile(SampleRows, path);
        var rows = CsvReader.ReadRowsFromFile(path);
        var all = string.Join(" ", rows.SelectMany(r => r));
        Assert.Contains("Bob", all);
        Assert.Contains("82000", all);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        Assert.NotNull(csv);
    }

    [Fact]
    public void WriteRows_NonEmpty()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        Assert.False(string.IsNullOrWhiteSpace(csv));
    }

    [Fact]
    public void WriteRows_ContainsAllValues()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains("95000", csv);
    }

    [Fact]
    public void WriteRows_CommaSeparated()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void WriteRows_ReadRows_RoundTrip_CountMatches()
    {
        var csv = CsvWriter.WriteRows(SampleRows);
        var rows = CsvReader.ReadRows(csv);
        Assert.Equal(SampleRows.Count, rows.Count);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRowsToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = TempFile("out.csv");
        CsvWriter.WriteRowsToFile(SampleRows, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRowsToFile_ReadRowsFromFile_CountMatches()
    {
        var path = TempFile("rtf.csv");
        CsvWriter.WriteRowsToFile(SampleRows, path);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal(4, rows.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteRowsWriteToFileReadRowsFromFileCsvDocLoadFilterVerify_Pipeline()
    {
        // WriteRows
        var csv = CsvWriter.WriteRows(SampleRows);
        Assert.Contains("Alice", csv);

        // WriteRowsToFile
        var path = TempFile("dogfood.csv");
        CsvWriter.WriteRowsToFile(SampleRows, path);
        Assert.True(File.Exists(path));

        // ReadRowsFromFile
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal(4, rows.Count);

        // CsvDocument.Load
        var doc = CsvDocument.Load(csv);
        Assert.Equal(3, doc.RowCount);
        Assert.True(doc.HasHeaders);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Verify
        var names = eng.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);

        // WriteRows from filtered doc
        var filteredCsv = eng.ToCsv();
        Assert.Contains("Alice", filteredCsv);
        Assert.DoesNotContain("Bob", filteredCsv);
    }
}
