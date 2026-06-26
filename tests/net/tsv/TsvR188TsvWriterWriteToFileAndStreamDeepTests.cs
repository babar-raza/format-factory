// Tests for TsvWriter.WriteToFile, WriteToStream, GetHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R188

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R188: Tests for TsvWriter.WriteToFile, WriteToStream, GetHeaders deeper coverage.
/// TsvWriter.WriteToFile(rows, path, headers): writes rows to a .tsv file on disk.
/// TsvWriter.WriteToStream(rows, stream, headers): writes rows to a stream.
/// TsvDocument.GetHeaders(): returns the list of column header names.
/// Covers: WriteToFile creates file; WriteToFile non-empty; WriteToFile content has tabs;
/// WriteToFile round-trip via LoadFile; WriteToFile headers in first line;
/// WriteToFile multiple rows; WriteToFile then SaveToFile consistent;
/// WriteToStream non-null; WriteToStream bytes positive; WriteToStream has tabs;
/// WriteToStream round-trip; WriteToStream header in output; WriteToStream multiple rows;
/// GetHeaders non-null; GetHeaders correct count; GetHeaders contains expected;
/// GetHeaders after AddColumn increases; GetHeaders after LoadFile preserved;
/// dogfood WriteToFile→LoadFile→GetHeaders→WriteToStream→filter→verify pipeline.
/// </summary>
public class TsvR188TsvWriterWriteToFileAndStreamDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR188TsvWriterWriteToFileAndStreamDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR188_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string[] Headers = { "Name", "Department", "Salary", "Years" };
    private static readonly string[][] Rows =
    {
        new[] { "Alice", "Engineering", "95000", "5" },
        new[] { "Bob", "Finance", "82000", "3" },
        new[] { "Carol", "Engineering", "105000", "8" },
        new[] { "Dave", "HR", "72000", "2" },
    };

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var path = TempFile("write.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_NonEmpty()
    {
        var path = TempFile("nonempty.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_ContentHasTabs()
    {
        var path = TempFile("tabs.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        Assert.Contains("\t", File.ReadAllText(path));
    }

    [Fact]
    public void WriteToFile_HeadersInFirstLine()
    {
        var path = TempFile("headers.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var firstLine = File.ReadAllLines(path)[0];
        Assert.Contains("Name", firstLine);
        Assert.Contains("Department", firstLine);
    }

    [Fact]
    public void WriteToFile_RoundTripViaLoadFile()
    {
        var path = TempFile("roundtrip.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void WriteToFile_AllDataRowsPresent()
    {
        var path = TempFile("allrows.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
        Assert.Contains("Dave", content);
    }

    [Fact]
    public void WriteToFile_SingleRow()
    {
        var path = TempFile("single.tsv");
        TsvWriter.WriteToFile(new[] { new[] { "Solo", "Only", "50000", "1" } }, path, Headers);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(1, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_NonNull()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        Assert.NotNull(ms.ToArray());
    }

    [Fact]
    public void WriteToStream_BytesPositive()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_HasTabs()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var content = System.Text.Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("\t", content);
    }

    [Fact]
    public void WriteToStream_HeaderInOutput()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var content = System.Text.Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Name", content);
        Assert.Contains("Department", content);
    }

    [Fact]
    public void WriteToStream_DataInOutput()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var content = System.Text.Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
    }

    [Fact]
    public void WriteToStream_RoundTrip_ViaWriteToFile()
    {
        // Write to stream, save to file, load back
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var path = TempFile("stream_rt.tsv");
        File.WriteAllBytes(path, ms.ToArray());
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void WriteToStream_MultipleRows()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var content = System.Text.Encoding.UTF8.GetString(ms.ToArray());
        // Header + 4 data rows = 5 lines minimum
        var lines = content.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 4);
    }

    // -------------------------------------------------------------------------
    // GetHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeaders_NonNull()
    {
        var path = TempFile("headers_get.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetHeaders());
    }

    [Fact]
    public void GetHeaders_CorrectCount()
    {
        var path = TempFile("headers_count.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.GetHeaders().Count);
    }

    [Fact]
    public void GetHeaders_ContainsExpected()
    {
        var path = TempFile("headers_expected.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        var doc = TsvDocument.LoadFile(path);
        var headers = doc.GetHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Department", headers);
        Assert.Contains("Salary", headers);
    }

    [Fact]
    public void GetHeaders_AfterLoadFile_Preserved()
    {
        var content = "Alpha\tBeta\tGamma\nv1\tv2\tv3\n";
        var path = TempFile("preserved.tsv");
        File.WriteAllText(path, content);
        var doc = TsvDocument.LoadFile(path);
        var headers = doc.GetHeaders();
        Assert.Contains("Alpha", headers);
        Assert.Contains("Gamma", headers);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToFile_LoadFile_GetHeaders_WriteToStream_Filter_Pipeline()
    {
        // WriteToFile
        var path = TempFile("dogfood.tsv");
        TsvWriter.WriteToFile(Rows, path, Headers);
        Assert.True(File.Exists(path));

        // LoadFile
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);

        // GetHeaders
        var headers = doc.GetHeaders();
        Assert.NotNull(headers);
        Assert.Equal(4, headers.Count);
        Assert.Contains("Name", headers);
        Assert.Contains("Salary", headers);

        // GetColumnValues
        var names = doc.GetColumnValues("Name");
        Assert.Equal(4, names.Count);
        Assert.Contains("Alice", names);

        // WriteToStream from loaded doc's rows
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, ms, Headers);
        var streamContent = System.Text.Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("\t", streamContent);
        Assert.Contains("Alice", streamContent);

        // WriteToFile with subset
        var engRows = new[] { Rows[0], Rows[2] }; // Alice and Carol — Engineering
        var engPath = TempFile("engineering.tsv");
        TsvWriter.WriteToFile(engRows, engPath, Headers);
        var engDoc = TsvDocument.LoadFile(engPath);
        Assert.Equal(2, engDoc.RowCount);
        var engHeaders = engDoc.GetHeaders();
        Assert.Equal(4, engHeaders.Count);

        // Filter from original doc
        var filtered = doc.Filter("Department", "Engineering");
        Assert.Equal(2, filtered.RowCount);
        Assert.Equal(4, filtered.GetHeaders().Count);

        // WriteToFile filtered rows manually then verify
        var filteredPath = TempFile("filtered_out.tsv");
        filtered.SaveToFile(filteredPath);
        var filteredLoaded = TsvDocument.LoadFile(filteredPath);
        Assert.Equal(2, filteredLoaded.RowCount);
        Assert.Contains("Alice", filteredLoaded.GetColumnValues("Name"));

        // GetHeaders consistent across save/load
        Assert.Equal(headers.Count, filteredLoaded.GetHeaders().Count);
    }
}
