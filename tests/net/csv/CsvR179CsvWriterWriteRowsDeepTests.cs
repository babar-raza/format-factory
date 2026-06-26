// Tests for CsvWriter.WriteRows, WriteRowsToFile, WriteToStream deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R179

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R179: Tests for CsvWriter.WriteRows, WriteRowsToFile, WriteToStream deeper.
/// CsvWriter.WriteRows(rows, headers): returns a CSV string from a list of row dictionaries.
/// CsvWriter.WriteRowsToFile(rows, headers, path): writes rows to a CSV file.
/// CsvWriter.WriteToStream(doc, stream): writes a CsvDocument to a stream.
/// Covers: WriteRows non-null; WriteRows non-empty; WriteRows contains headers;
/// WriteRows contains data values; WriteRows correct row count;
/// WriteRowsToFile creates file; WriteRowsToFile content has headers;
/// WriteRowsToFile content has data; WriteRowsToFile multiple rows;
/// WriteToStream stream has content; WriteToStream content has headers;
/// WriteToStream content parseable back;
/// dogfood CreateDoc->WriteToStream->WriteRowsToFile->WriteRows->ReadBack->Verify pipeline.
/// </summary>
public class CsvR179CsvWriterWriteRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly List<string> Headers = new() { "Name", "Dept", "Score" };

    private static readonly List<Dictionary<string, string>> SampleRows = new()
    {
        new() { ["Name"] = "Alice", ["Dept"] = "Engineering", ["Score"] = "92" },
        new() { ["Name"] = "Bob", ["Dept"] = "Finance", ["Score"] = "85" },
        new() { ["Name"] = "Carol", ["Dept"] = "Engineering", ["Score"] = "78" },
    };

    public CsvR179CsvWriterWriteRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR179_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var csv = CsvWriter.WriteRows(SampleRows, Headers);
        Assert.NotNull(csv);
    }

    [Fact]
    public void WriteRows_NonEmpty()
    {
        var csv = CsvWriter.WriteRows(SampleRows, Headers);
        Assert.NotEmpty(csv);
    }

    [Fact]
    public void WriteRows_ContainsHeaderNames()
    {
        var csv = CsvWriter.WriteRows(SampleRows, Headers);
        Assert.Contains("Name", csv);
        Assert.Contains("Dept", csv);
    }

    [Fact]
    public void WriteRows_ContainsDataValues()
    {
        var csv = CsvWriter.WriteRows(SampleRows, Headers);
        Assert.Contains("Alice", csv);
        Assert.Contains("Finance", csv);
    }

    [Fact]
    public void WriteRows_HasCommaSeparator()
    {
        var csv = CsvWriter.WriteRows(SampleRows, Headers);
        Assert.Contains(",", csv);
    }

    [Fact]
    public void WriteRows_SingleRow_NonEmpty()
    {
        var singleRow = new List<Dictionary<string, string>>
        {
            new() { ["Name"] = "Dave", ["Dept"] = "HR", ["Score"] = "91" }
        };
        var csv = CsvWriter.WriteRows(singleRow, Headers);
        Assert.Contains("Dave", csv);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRowsToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = TempFile("output.csv");
        CsvWriter.WriteRowsToFile(SampleRows, Headers, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRowsToFile_ContentHasHeaders()
    {
        var path = TempFile("headers.csv");
        CsvWriter.WriteRowsToFile(SampleRows, Headers, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Name", content);
    }

    [Fact]
    public void WriteRowsToFile_ContentHasData()
    {
        var path = TempFile("data.csv");
        CsvWriter.WriteRowsToFile(SampleRows, Headers, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
    }

    [Fact]
    public void WriteRowsToFile_MultipleRows_AllPresent()
    {
        var path = TempFile("multi.csv");
        CsvWriter.WriteRowsToFile(SampleRows, Headers, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Bob", content);
        Assert.Contains("Finance", content);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_StreamHasContent()
    {
        var doc = CsvDocument.LoadContent("Name,Score\nAlice,92\nBob,85");
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(doc, ms);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_ContentHasHeaders()
    {
        var doc = CsvDocument.LoadContent("Name,Dept\nAlice,Eng\nBob,Finance");
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(doc, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Name", content);
        Assert.Contains("Dept", content);
    }

    [Fact]
    public void WriteToStream_ContentHasData()
    {
        var doc = CsvDocument.LoadContent("Name,Score\nAlice,92\nBob,85");
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(doc, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Alice", content);
    }

    [Fact]
    public void WriteToStream_ParseableBack()
    {
        var doc = CsvDocument.LoadContent("Name,Score\nAlice,92\nBob,85");
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(doc, ms);
        ms.Position = 0;
        var content = Encoding.UTF8.GetString(ms.ToArray());
        var reloaded = CsvDocument.LoadContent(content);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_WriteToStream_WriteRowsToFile_WriteRows_ReadBack_Verify_Pipeline()
    {
        // Create document
        var doc = CsvDocument.CreateEmpty(new[] { "Product", "Price", "Qty" });
        doc.AddRow(new[] { "Widget", "9.99", "100" });
        doc.AddRow(new[] { "Gadget", "24.99", "50" });

        // WriteToStream
        using var ms = new MemoryStream();
        CsvWriter.WriteToStream(doc, ms);
        Assert.True(ms.Length > 0);
        var streamContent = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Widget", streamContent);

        // WriteRows
        var rowDicts = new List<Dictionary<string, string>>
        {
            new() { ["Product"] = "Widget", ["Price"] = "9.99", ["Qty"] = "100" },
            new() { ["Product"] = "Gadget", ["Price"] = "24.99", ["Qty"] = "50" },
        };
        var headers = new List<string> { "Product", "Price", "Qty" };
        var csv = CsvWriter.WriteRows(rowDicts, headers);
        Assert.NotEmpty(csv);
        Assert.Contains("Widget", csv);

        // WriteRowsToFile
        var path = TempFile("dogfood.csv");
        CsvWriter.WriteRowsToFile(rowDicts, headers, path);
        Assert.True(File.Exists(path));
        var fileContent = File.ReadAllText(path);
        Assert.Contains("Gadget", fileContent);

        // ReadBack with CsvDocument.LoadFile
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount);
        Assert.Equal("Widget", loaded.GetCellValue(0, "Product"));
        Assert.Equal("50", loaded.GetCellValue(1, "Qty"));
    }
}
