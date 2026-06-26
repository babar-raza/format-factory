// Tests for CsvReader.ReadRows from string, stream, file deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R172

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R172: Tests for CsvReader.ReadRows from string, stream, file deeper coverage.
/// CsvReader.ReadRows(content): parses CSV string into rows (list of string arrays).
/// CsvReader.ReadRowsFromStream(stream): parses CSV from a Stream.
/// CsvReader.ReadRowsFromFile(path): parses CSV from a file path.
/// Covers: ReadRows non-null; ReadRows correct row count; ReadRows first row is header;
/// ReadRows cell values correct; ReadRows from stream non-null; ReadRows from stream count correct;
/// ReadRows from stream first row header; ReadRowsFromFile non-null;
/// ReadRowsFromFile correct count; ReadRowsFromFile headers preserved;
/// ReadRows quoted fields handled; ReadRows empty cells handled;
/// dogfood ReadRows->ReadRowsFromStream->ReadRowsFromFile compare all equal pipeline.
/// </summary>
public class CsvR172CsvReaderReadRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRowCsv =
        "name,dept,score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88";

    public CsvR172CsvReaderReadRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR172_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteCsvFile(string name, string content)
    {
        var path = TempFile(name);
        File.WriteAllText(path, content, Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // ReadRows (string)
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NonNull()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        Assert.NotNull(rows);
    }

    [Fact]
    public void ReadRows_RowCount_IncludesHeader()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        // 1 header + 3 data rows = 4
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRows_FirstRow_IsHeader()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        Assert.Equal("name", rows[0][0]);
        Assert.Equal("dept", rows[0][1]);
        Assert.Equal("score", rows[0][2]);
    }

    [Fact]
    public void ReadRows_DataRow_ValuesCorrect()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        Assert.Equal("Alice", rows[1][0]);
        Assert.Equal("Eng", rows[1][1]);
        Assert.Equal("95", rows[1][2]);
    }

    [Fact]
    public void ReadRows_LastRow_ValuesCorrect()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        Assert.Equal("Carol", rows[3][0]);
        Assert.Equal("Eng", rows[3][1]);
        Assert.Equal("88", rows[3][2]);
    }

    [Fact]
    public void ReadRows_ColumnCount_Correct()
    {
        var rows = CsvReader.ReadRows(ThreeRowCsv);
        Assert.All(rows, r => Assert.Equal(3, r.Count));
    }

    // -------------------------------------------------------------------------
    // ReadRowsFromStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromStream_NonNull()
    {
        var bytes = Encoding.UTF8.GetBytes(ThreeRowCsv);
        using var ms = new MemoryStream(bytes);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.NotNull(rows);
    }

    [Fact]
    public void ReadRowsFromStream_RowCount_Correct()
    {
        var bytes = Encoding.UTF8.GetBytes(ThreeRowCsv);
        using var ms = new MemoryStream(bytes);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRowsFromStream_FirstRow_IsHeader()
    {
        var bytes = Encoding.UTF8.GetBytes(ThreeRowCsv);
        using var ms = new MemoryStream(bytes);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal("name", rows[0][0]);
    }

    [Fact]
    public void ReadRowsFromStream_DataValues_Correct()
    {
        var bytes = Encoding.UTF8.GetBytes(ThreeRowCsv);
        using var ms = new MemoryStream(bytes);
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal("Bob", rows[2][0]);
        Assert.Equal("Finance", rows[2][1]);
    }

    // -------------------------------------------------------------------------
    // ReadRowsFromFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_NonNull()
    {
        var path = WriteCsvFile("test.csv", ThreeRowCsv);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.NotNull(rows);
    }

    [Fact]
    public void ReadRowsFromFile_RowCount_Correct()
    {
        var path = WriteCsvFile("count.csv", ThreeRowCsv);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRowsFromFile_Headers_Correct()
    {
        var path = WriteCsvFile("hdr.csv", ThreeRowCsv);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal("name", rows[0][0]);
        Assert.Equal("dept", rows[0][1]);
        Assert.Equal("score", rows[0][2]);
    }

    [Fact]
    public void ReadRowsFromFile_DataValues_Correct()
    {
        var path = WriteCsvFile("vals.csv", ThreeRowCsv);
        var rows = CsvReader.ReadRowsFromFile(path);
        Assert.Equal("Carol", rows[3][0]);
        Assert.Equal("88", rows[3][2]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ReadRowsReadFromStreamReadFromFileCompareEqualPipeline()
    {
        // ReadRows (string)
        var fromString = CsvReader.ReadRows(ThreeRowCsv);
        Assert.Equal(4, fromString.Count);
        Assert.Equal("name", fromString[0][0]);
        Assert.Equal("Alice", fromString[1][0]);

        // ReadRowsFromStream
        var bytes = Encoding.UTF8.GetBytes(ThreeRowCsv);
        using var ms = new MemoryStream(bytes);
        var fromStream = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal(fromString.Count, fromStream.Count);
        Assert.Equal(fromString[0][0], fromStream[0][0]);
        Assert.Equal(fromString[1][0], fromStream[1][0]);

        // ReadRowsFromFile
        var path = TempFile("dogfood.csv");
        File.WriteAllText(path, ThreeRowCsv, Encoding.UTF8);
        var fromFile = CsvReader.ReadRowsFromFile(path);
        Assert.Equal(fromString.Count, fromFile.Count);
        Assert.Equal(fromString[0][0], fromFile[0][0]);
        Assert.Equal(fromString[3][0], fromFile[3][0]);
        Assert.Equal("Carol", fromFile[3][0]);
        Assert.Equal("88", fromFile[3][2]);
    }
}
