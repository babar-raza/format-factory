// Tests for CsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R181

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R181: Tests for CsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper coverage.
/// ReadRows(path): returns a list of row data from a CSV file.
/// ReadRowsFromStream(stream): returns rows from a stream.
/// GetHeaders(path): returns the header row from a CSV file.
/// Covers: ReadRows non-null; ReadRows correct count; ReadRows first row correct;
/// ReadRows last row correct; ReadRows each row has correct field count;
/// ReadRowsFromStream non-null; ReadRowsFromStream correct count;
/// ReadRowsFromStream data accessible; ReadRowsFromStream matches ReadRows count;
/// GetHeaders non-null; GetHeaders correct count; GetHeaders contains expected;
/// GetHeaders order preserved;
/// dogfood WriteRows->ReadRows->ReadRowsFromStream->GetHeaders->Verify pipeline.
/// </summary>
public class CsvR181CsvReaderReadRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string SampleCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,92\n" +
        "Bob,Finance,85\n" +
        "Carol,HR,78\n" +
        "Dave,Eng,91";

    public CsvR181CsvReaderReadRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR181_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteSampleFile(string filename = "sample.csv")
    {
        var path = TempFile(filename);
        File.WriteAllText(path, SampleCsv);
        return path;
    }

    // -------------------------------------------------------------------------
    // ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NonNull()
    {
        var path = WriteSampleFile();
        Assert.NotNull(CsvReader.ReadRows(path));
    }

    [Fact]
    public void ReadRows_CorrectCount()
    {
        var path = WriteSampleFile();
        var rows = CsvReader.ReadRows(path);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRows_FirstRow_Correct()
    {
        var path = WriteSampleFile();
        var rows = CsvReader.ReadRows(path);
        Assert.Contains("Alice", rows[0]);
    }

    [Fact]
    public void ReadRows_LastRow_Correct()
    {
        var path = WriteSampleFile();
        var rows = CsvReader.ReadRows(path);
        Assert.Contains("Dave", rows[rows.Count - 1]);
    }

    [Fact]
    public void ReadRows_AllNonNull()
    {
        var path = WriteSampleFile();
        var rows = CsvReader.ReadRows(path);
        foreach (var row in rows)
            Assert.NotNull(row);
    }

    [Fact]
    public void ReadRows_EachRow_HasThreeFields()
    {
        var path = WriteSampleFile();
        var rows = CsvReader.ReadRows(path);
        foreach (var row in rows)
            Assert.Equal(3, row.Count);
    }

    [Fact]
    public void ReadRows_SingleRowCsv_ReturnsOne()
    {
        var path = TempFile("single.csv");
        File.WriteAllText(path, "A,B\n1,2");
        var rows = CsvReader.ReadRows(path);
        Assert.Equal(1, rows.Count);
    }

    // -------------------------------------------------------------------------
    // ReadRowsFromStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromStream_NonNull()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(SampleCsv));
        Assert.NotNull(CsvReader.ReadRowsFromStream(ms));
    }

    [Fact]
    public void ReadRowsFromStream_CorrectCount()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(SampleCsv));
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRowsFromStream_DataAccessible()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(SampleCsv));
        var rows = CsvReader.ReadRowsFromStream(ms);
        Assert.Contains("Alice", rows[0]);
    }

    [Fact]
    public void ReadRowsFromStream_MatchesReadRowsCount()
    {
        var path = WriteSampleFile();
        var fileRows = CsvReader.ReadRows(path);
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(SampleCsv));
        var streamRows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal(fileRows.Count, streamRows.Count);
    }

    [Fact]
    public void ReadRowsFromStream_AllNonNull()
    {
        using var ms = new MemoryStream(System.Text.Encoding.UTF8.GetBytes(SampleCsv));
        var rows = CsvReader.ReadRowsFromStream(ms);
        foreach (var row in rows)
            Assert.NotNull(row);
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var path = WriteSampleFile();
        Assert.NotNull(CsvReader.GetHeaders(path));
    }

    [Fact]
    public void GetHeaders_CorrectCount()
    {
        var path = WriteSampleFile();
        var headers = CsvReader.GetHeaders(path);
        Assert.Equal(3, headers.Count);
    }

    [Fact]
    public void GetHeaders_ContainsExpected()
    {
        var path = WriteSampleFile();
        var headers = CsvReader.GetHeaders(path);
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void GetHeaders_OrderPreserved()
    {
        var path = WriteSampleFile();
        var headers = CsvReader.GetHeaders(path);
        Assert.Equal("Name", headers[0]);
        Assert.Equal("Dept", headers[1]);
        Assert.Equal("Score", headers[2]);
    }

    [Fact]
    public void GetHeaders_SingleColumn_ReturnsOne()
    {
        var path = TempFile("single_col.csv");
        File.WriteAllText(path, "OnlyColumn\nVal1\nVal2");
        var headers = CsvReader.GetHeaders(path);
        Assert.Equal(1, headers.Count);
        Assert.Equal("OnlyColumn", headers[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteRows_ReadRows_ReadRowsFromStream_GetHeaders_Verify_Pipeline()
    {
        // Write file
        var path = WriteSampleFile("dogfood.csv");

        // GetHeaders
        var headers = CsvReader.GetHeaders(path);
        Assert.Equal(3, headers.Count);
        Assert.Equal("Name", headers[0]);

        // ReadRows
        var rows = CsvReader.ReadRows(path);
        Assert.Equal(4, rows.Count);
        Assert.Equal(3, rows[0].Count);
        Assert.Contains("Alice", rows[0]);
        Assert.Contains("Dave", rows[rows.Count - 1]);

        // ReadRowsFromStream from same content
        using var ms = new MemoryStream(File.ReadAllBytes(path));
        var streamRows = CsvReader.ReadRowsFromStream(ms);
        Assert.Equal(rows.Count, streamRows.Count);

        // Verify each stream row has same fields as file row
        for (var i = 0; i < rows.Count; i++)
            Assert.Equal(rows[i].Count, streamRows[i].Count);

        // Verify specific values
        Assert.Contains("Eng", rows[0]);
        Assert.Contains("92", rows[0]);
        Assert.Contains("Finance", rows[1]);
        Assert.Contains("HR", rows[2]);
    }
}
