// Tests for TsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R177

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R177: Tests for TsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper.
/// TsvReader.ReadRows(path): reads all rows from a TSV file.
/// TsvReader.ReadRowsFromStream(stream): reads all rows from a stream.
/// TsvReader.GetHeaders(path): returns the header row from a TSV file.
/// Covers: ReadRows non-null; ReadRows count matches file rows; ReadRows first row correct;
/// ReadRows all rows accessible; ReadRowsFromStream non-null;
/// ReadRowsFromStream count matches; ReadRowsFromStream data accessible;
/// ReadRowsFromStream from MemoryStream with tab-separated data;
/// GetHeaders non-null; GetHeaders count correct; GetHeaders contains expected values;
/// GetHeaders order preserved;
/// dogfood WriteTsv->ReadRows->ReadRowsFromStream->GetHeaders->Verify pipeline.
/// </summary>
public class TsvR177TsvReaderReadRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string SampleTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEngineering\t92\n" +
        "Bob\tFinance\t85\n" +
        "Carol\tEngineering\t78\n" +
        "Dave\tHR\t91";

    public TsvR177TsvReaderReadRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR177_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string WriteSampleFile(string name)
    {
        var path = TempFile(name);
        File.WriteAllText(path, SampleTsv);
        return path;
    }

    // -------------------------------------------------------------------------
    // TsvReader.ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NonNull()
    {
        var path = WriteSampleFile("sample.tsv");
        Assert.NotNull(TsvReader.ReadRows(path));
    }

    [Fact]
    public void ReadRows_CountMatchesDataRows()
    {
        var path = WriteSampleFile("count.tsv");
        var rows = TsvReader.ReadRows(path);
        // 4 data rows (excluding header)
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRows_FirstRow_ContainsExpectedValues()
    {
        var path = WriteSampleFile("first.tsv");
        var rows = TsvReader.ReadRows(path);
        var first = rows[0];
        Assert.Contains("Alice", first);
    }

    [Fact]
    public void ReadRows_AllRowsNonNull()
    {
        var path = WriteSampleFile("allrows.tsv");
        var rows = TsvReader.ReadRows(path);
        foreach (var row in rows)
            Assert.NotNull(row);
    }

    [Fact]
    public void ReadRows_LastRow_ContainsExpectedValue()
    {
        var path = WriteSampleFile("last.tsv");
        var rows = TsvReader.ReadRows(path);
        var last = rows[rows.Count - 1];
        Assert.Contains("Dave", last);
    }

    [Fact]
    public void ReadRows_EachRow_HasColumnCount()
    {
        var path = WriteSampleFile("cols.tsv");
        var rows = TsvReader.ReadRows(path);
        foreach (var row in rows)
            Assert.Equal(3, row.Count);
    }

    // -------------------------------------------------------------------------
    // TsvReader.ReadRowsFromStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromStream_NonNull()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        Assert.NotNull(TsvReader.ReadRowsFromStream(ms));
    }

    [Fact]
    public void ReadRowsFromStream_CountMatchesDataRows()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var rows = TsvReader.ReadRowsFromStream(ms);
        Assert.Equal(4, rows.Count);
    }

    [Fact]
    public void ReadRowsFromStream_DataAccessible()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var rows = TsvReader.ReadRowsFromStream(ms);
        Assert.Contains("Alice", rows[0]);
    }

    [Fact]
    public void ReadRowsFromStream_FromFileStream_MatchesReadRows()
    {
        var path = WriteSampleFile("filestream.tsv");
        var fromFile = TsvReader.ReadRows(path);
        using var fs = File.OpenRead(path);
        var fromStream = TsvReader.ReadRowsFromStream(fs);
        Assert.Equal(fromFile.Count, fromStream.Count);
    }

    [Fact]
    public void ReadRowsFromStream_SimpleTabData_CorrectValues()
    {
        var data = "A\tB\tC\n1\t2\t3\n4\t5\t6";
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(data));
        var rows = TsvReader.ReadRowsFromStream(ms);
        Assert.Equal(2, rows.Count);
        Assert.Contains("1", rows[0]);
        Assert.Contains("6", rows[1]);
    }

    // -------------------------------------------------------------------------
    // TsvReader.GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var path = WriteSampleFile("headers.tsv");
        Assert.NotNull(TsvReader.GetHeaders(path));
    }

    [Fact]
    public void GetHeaders_CountCorrect()
    {
        var path = WriteSampleFile("headcount.tsv");
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal(3, headers.Count);
    }

    [Fact]
    public void GetHeaders_ContainsExpectedValues()
    {
        var path = WriteSampleFile("headvals.tsv");
        var headers = TsvReader.GetHeaders(path);
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void GetHeaders_OrderPreserved()
    {
        var path = WriteSampleFile("headorder.tsv");
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal("Name", headers[0]);
        Assert.Equal("Dept", headers[1]);
        Assert.Equal("Score", headers[2]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteTsv_ReadRows_ReadRowsFromStream_GetHeaders_Verify_Pipeline()
    {
        // Build and save a TsvDocument
        var doc = TsvDocument.CreateEmpty(new List<string> { "Product", "Price", "Stock" });
        doc.AddRow(new List<string> { "Widget", "9.99", "100" });
        doc.AddRow(new List<string> { "Gadget", "24.99", "50" });
        doc.AddRow(new List<string> { "Gizmo", "14.99", "75" });
        var path = TempFile("dogfood.tsv");
        doc.SaveToFile(path);

        // ReadRows
        var rows = TsvReader.ReadRows(path);
        Assert.NotNull(rows);
        Assert.Equal(3, rows.Count);
        Assert.Contains("Widget", rows[0]);
        Assert.Contains("Gizmo", rows[2]);

        // GetHeaders
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal(3, headers.Count);
        Assert.Equal("Product", headers[0]);
        Assert.Equal("Price", headers[1]);

        // ReadRowsFromStream
        using var fs = File.OpenRead(path);
        var streamRows = TsvReader.ReadRowsFromStream(fs);
        Assert.Equal(3, streamRows.Count);
        Assert.Contains("Gadget", streamRows[1]);

        // Verify row data consistency
        Assert.Equal(rows.Count, streamRows.Count);
        for (var i = 0; i < rows.Count; i++)
            Assert.Equal(rows[i].Count, streamRows[i].Count);
    }
}
