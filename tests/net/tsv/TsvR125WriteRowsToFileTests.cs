// Tests for TsvWriter.WriteRowsToFile(IEnumerable<IEnumerable<string?>>, string path).
// Sprint: FORMAT-FACTORY-TSV-R125-20260627
// Ledger: R125-GOVERNED-DOTNET-TSV-WRITE-ROWS-TO-FILE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R125: Dedicated tests for TsvWriter.WriteRowsToFile(rows, path).
/// WriteRowsToFile serializes rows to a TSV file, UTF-8 without BOM,
/// LF line endings. Creates parent directories as needed.
/// Throws TsvException for: null rows, null/empty path, tab/newline in fields.
/// Covers: output file created; file is non-empty; UTF-8 no-BOM; tab separators present;
/// multi-row output; null field treated as empty; null rows throws;
/// null path throws TsvException; empty path throws; tab-in-field throws;
/// dogfood WriteRowsToFile→ReadRowsFromFile roundtrip.
/// </summary>
public class TsvR125WriteRowsToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"tsv-r125-{Guid.NewGuid():N}.tsv");

    private static readonly string[][] SampleRows =
    [
        ["Name", "Score", "City"],
        ["Alice", "95", "NYC"],
        ["Bob", "80", "London"],
        ["Carol", "88", "Paris"],
    ];

    // -------------------------------------------------------------------------
    // Basic file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_ValidRows_FileIsCreated()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_ValidRows_FileIsNonEmpty()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_ValidRows_ContentContainsTabs()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            var content = File.ReadAllText(path);
            Assert.Contains("\t", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_ValidRows_MultipleRowsWritten()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            var content = File.ReadAllText(path);
            var lines = content.Split('\n', StringSplitOptions.RemoveEmptyEntries);
            Assert.Equal(4, lines.Length); // header + 3 data rows
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_NullField_TreatedAsEmpty()
    {
        var path = TempPath();
        string?[][] rowsWithNull = [["Alice", null, "NYC"]];
        try
        {
            TsvWriter.WriteRowsToFile(rowsWithNull, path);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice\t\tNYC", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_Utf8NoBom_FirstBytesNotBom()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            var bytes = File.ReadAllBytes(path);
            // UTF-8 BOM is 0xEF 0xBB 0xBF — should NOT be present
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Error handling
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_NullRows_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            TsvWriter.WriteRowsToFile(null!, TempPath()));
    }

    [Fact]
    public void WriteRowsToFile_NullPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvWriter.WriteRowsToFile(SampleRows, null!));
    }

    [Fact]
    public void WriteRowsToFile_EmptyPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvWriter.WriteRowsToFile(SampleRows, string.Empty));
    }

    [Fact]
    public void WriteRowsToFile_TabInField_ThrowsTsvException()
    {
        var path = TempPath();
        string?[][] badRows = [["Alice\tBob"]];
        try
        {
            Assert.Throws<TsvException>(() => TsvWriter.WriteRowsToFile(badRows, path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRowsToFile → ReadRowsFromFile roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRowsToFile_ThenReadRowsFromFile_RoundtripPreservesData()
    {
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(SampleRows, path);
            var read = TsvReader.ReadRowsFromFile(path);

            Assert.Equal(SampleRows.Length, read.Count);
            Assert.Equal("Name",  read[0][0]);
            Assert.Equal("Alice", read[1][0]);
            Assert.Equal("95",    read[1][1]);
            Assert.Equal("Paris", read[3][2]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
