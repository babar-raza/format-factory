// Tests for TsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R184

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R184: Tests for TsvReader.ReadRows, ReadRowsFromStream, GetHeaders deeper coverage.
/// TsvReader.ReadRows(path): reads all data rows from a TSV file.
/// TsvReader.ReadRowsFromStream(stream): reads rows from a stream.
/// TsvReader.GetHeaders(path): returns header row values.
/// Covers: ReadRows non-null; ReadRows count equals RowCount; ReadRows first row correct;
/// ReadRows last row correct; ReadRows each has fields; ReadRows single row;
/// ReadRowsFromStream non-null; ReadRowsFromStream count matches ReadRows;
/// ReadRowsFromStream first row correct; ReadRowsFromStream data accessible;
/// GetHeaders non-null; GetHeaders count correct; GetHeaders contains expected names;
/// GetHeaders order preserved; GetHeaders single column; GetHeaders after WriteToFile;
/// dogfood WriteSampleFile→GetHeaders→ReadRows→ReadRowsFromStream→row-level verify pipeline.
/// </summary>
public class TsvR184TsvReaderReadRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR184TsvReaderReadRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR184_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tDept\tSalary\n" +
        "Alice\tEngineering\t95000\n" +
        "Bob\tFinance\t82000\n" +
        "Carol\tEngineering\t91000\n" +
        "Dave\tHR\t75000\n";

    private string WriteSampleFile()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return path;
    }

    // -------------------------------------------------------------------------
    // ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NonNull()
    {
        var path = WriteSampleFile();
        Assert.NotNull(TsvReader.ReadRows(path));
    }

    [Fact]
    public void ReadRows_FourRows()
    {
        var path = WriteSampleFile();
        Assert.Equal(4, TsvReader.ReadRows(path).Count);
    }

    [Fact]
    public void ReadRows_FirstRowCorrect()
    {
        var path = WriteSampleFile();
        var rows = TsvReader.ReadRows(path);
        Assert.Contains("Alice", rows[0]);
    }

    [Fact]
    public void ReadRows_LastRowCorrect()
    {
        var path = WriteSampleFile();
        var rows = TsvReader.ReadRows(path);
        Assert.Contains("Dave", rows[rows.Count - 1]);
    }

    [Fact]
    public void ReadRows_AllRowsNonNull()
    {
        var path = WriteSampleFile();
        foreach (var row in TsvReader.ReadRows(path))
            Assert.NotNull(row);
    }

    [Fact]
    public void ReadRows_EachRowHasThreeFields()
    {
        var path = WriteSampleFile();
        foreach (var row in TsvReader.ReadRows(path))
            Assert.True(row.Count >= 3);
    }

    [Fact]
    public void ReadRows_SingleDataRow()
    {
        var path = TempFile("single.tsv");
        File.WriteAllText(path, "Name\tScore\nAlice\t92\n");
        var rows = TsvReader.ReadRows(path);
        Assert.Equal(1, rows.Count);
        Assert.Contains("Alice", rows[0]);
    }

    // -------------------------------------------------------------------------
    // ReadRowsFromStream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromStream_NonNull()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        Assert.NotNull(TsvReader.ReadRowsFromStream(ms));
    }

    [Fact]
    public void ReadRowsFromStream_CountMatchesFile()
    {
        var path = WriteSampleFile();
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        Assert.Equal(TsvReader.ReadRows(path).Count, TsvReader.ReadRowsFromStream(ms).Count);
    }

    [Fact]
    public void ReadRowsFromStream_FirstRowCorrect()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var rows = TsvReader.ReadRowsFromStream(ms);
        Assert.Contains("Alice", rows[0]);
    }

    [Fact]
    public void ReadRowsFromStream_DataAccessible()
    {
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(SampleTsv));
        var rows = TsvReader.ReadRowsFromStream(ms);
        var found = false;
        foreach (var row in rows)
            if (row.Contains("Carol"))
                found = true;
        Assert.True(found);
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var path = WriteSampleFile();
        Assert.NotNull(TsvReader.GetHeaders(path));
    }

    [Fact]
    public void GetHeaders_ThreeColumns()
    {
        var path = WriteSampleFile();
        Assert.Equal(3, TsvReader.GetHeaders(path).Count);
    }

    [Fact]
    public void GetHeaders_ContainsExpectedNames()
    {
        var path = WriteSampleFile();
        var headers = TsvReader.GetHeaders(path);
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Salary", headers);
    }

    [Fact]
    public void GetHeaders_OrderPreserved()
    {
        var path = WriteSampleFile();
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal("Name", headers[0]);
        Assert.Equal("Dept", headers[1]);
        Assert.Equal("Salary", headers[2]);
    }

    [Fact]
    public void GetHeaders_SingleColumn()
    {
        var path = TempFile("single_col.tsv");
        File.WriteAllText(path, "Value\n100\n200\n");
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal(1, headers.Count);
        Assert.Equal("Value", headers[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteSampleFile_GetHeaders_ReadRows_ReadRowsFromStream_Verify_Pipeline()
    {
        // Write sample file via TsvDocument + TsvWriter
        var doc = TsvDocument.CreateEmpty(new[] { "Employee", "Team", "Level", "YearsExp" });
        doc.AddRow(new[] { "Alice", "Backend", "Senior", "7" });
        doc.AddRow(new[] { "Bob", "Frontend", "Junior", "2" });
        doc.AddRow(new[] { "Carol", "Backend", "Lead", "10" });
        doc.AddRow(new[] { "Dave", "DevOps", "Senior", "5" });
        doc.AddRow(new[] { "Eve", "Backend", "Mid", "4" });
        var path = TempFile("employees.tsv");
        TsvWriter.WriteToFile(doc, path);
        Assert.True(File.Exists(path));

        // GetHeaders
        var headers = TsvReader.GetHeaders(path);
        Assert.Equal(4, headers.Count);
        Assert.Equal("Employee", headers[0]);
        Assert.Equal("Team", headers[1]);

        // ReadRows
        var rows = TsvReader.ReadRows(path);
        Assert.Equal(5, rows.Count);
        Assert.Contains("Alice", rows[0]);
        Assert.Contains("Eve", rows[4]);

        // Each row has 4 fields
        foreach (var row in rows)
            Assert.True(row.Count >= 4);

        // ReadRowsFromStream from file content
        var content = File.ReadAllText(path);
        using var ms = new MemoryStream(Encoding.UTF8.GetBytes(content));
        var streamRows = TsvReader.ReadRowsFromStream(ms);
        Assert.Equal(rows.Count, streamRows.Count);
        Assert.Contains("Alice", streamRows[0]);

        // Verify Carol in rows
        var carolFound = false;
        foreach (var row in rows)
            if (row.Contains("Carol"))
                carolFound = true;
        Assert.True(carolFound);

        // Single-column edge case
        var singlePath = TempFile("single_employee.tsv");
        File.WriteAllText(singlePath, "Name\nSolo\n");
        var singleHeaders = TsvReader.GetHeaders(singlePath);
        Assert.Equal(1, singleHeaders.Count);
        var singleRows = TsvReader.ReadRows(singlePath);
        Assert.Equal(1, singleRows.Count);
    }
}
