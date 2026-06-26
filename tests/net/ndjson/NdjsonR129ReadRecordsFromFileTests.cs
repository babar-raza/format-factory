// Tests for NdjsonReader.ReadRecordsFromFile(string path) — dedicated path-based read API.
// Sprint: FORMAT-FACTORY-NDJSON-R129-20260627
// Ledger: R129-GOVERNED-DOTNET-NDJSON-READ-RECORDS-FROM-FILE-001

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R129: Dedicated tests for NdjsonReader.ReadRecordsFromFile(string path).
/// ReadRecordsFromFile reads each non-blank line of the given file as a JSON value.
/// Throws NdjsonException for: null/empty path, non-existent file, invalid JSON lines.
/// Returns empty list for empty files. Skips blank lines between records.
/// Covers: non-null result; record count correct; element types; blank-line skipping;
/// empty file returns empty; null path throws; whitespace path throws;
/// non-existent file throws NdjsonException; invalid JSON throws NdjsonException;
/// dogfood parity with ReadRecords(string).
/// </summary>
public class NdjsonR129ReadRecordsFromFileTests
{
    private static string WriteFile(string content)
    {
        var path = Path.GetTempFileName();
        File.WriteAllText(path, content);
        return path;
    }

    private static readonly string SampleContent =
        "{\"name\":\"Alice\",\"score\":95}\n{\"name\":\"Bob\",\"score\":80}\n{\"name\":\"Carol\",\"score\":88}";

    // -------------------------------------------------------------------------
    // Basic loading
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecordsFromFile_ValidFile_ReturnsNonNullList()
    {
        var path = WriteFile(SampleContent);
        try
        {
            var records = NdjsonReader.ReadRecordsFromFile(path);
            Assert.NotNull(records);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRecordsFromFile_ValidFile_RecordCountMatches()
    {
        var path = WriteFile(SampleContent);
        try
        {
            var records = NdjsonReader.ReadRecordsFromFile(path);
            Assert.Equal(3, records.Count);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRecordsFromFile_ValidFile_RecordsAreObjects()
    {
        var path = WriteFile(SampleContent);
        try
        {
            var records = NdjsonReader.ReadRecordsFromFile(path);
            foreach (var r in records)
                Assert.Equal(JsonValueKind.Object, r.ValueKind);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRecordsFromFile_FileWithBlankLines_BlankLinesSkipped()
    {
        var path = WriteFile("{\"a\":1}\n\n{\"b\":2}\n\n{\"c\":3}");
        try
        {
            var records = NdjsonReader.ReadRecordsFromFile(path);
            Assert.Equal(3, records.Count);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRecordsFromFile_EmptyFile_ReturnsEmptyList()
    {
        var path = WriteFile(string.Empty);
        try
        {
            var records = NdjsonReader.ReadRecordsFromFile(path);
            Assert.Empty(records);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Error handling
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRecordsFromFile_NullPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecordsFromFile(null!));
    }

    [Fact]
    public void ReadRecordsFromFile_EmptyPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecordsFromFile(string.Empty));
    }

    [Fact]
    public void ReadRecordsFromFile_NonExistentPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() =>
            NdjsonReader.ReadRecordsFromFile("/nonexistent/r129-test-file.ndjson"));
    }

    [Fact]
    public void ReadRecordsFromFile_InvalidJsonLine_ThrowsNdjsonException()
    {
        var path = WriteFile("{\"valid\":1}\nNOT_VALID_JSON\n{\"ok\":2}");
        try
        {
            Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecordsFromFile(path));
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: parity with ReadRecords(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ParityWithReadRecordsString()
    {
        var path = WriteFile(SampleContent);
        try
        {
            var fromFile   = NdjsonReader.ReadRecordsFromFile(path);
            var fromString = NdjsonReader.ReadRecords(SampleContent);

            Assert.Equal(fromString.Count, fromFile.Count);
            for (int i = 0; i < fromString.Count; i++)
            {
                Assert.Equal(fromString[i].GetProperty("name").GetString(),
                             fromFile[i].GetProperty("name").GetString());
            }
        }
        finally { File.Delete(path); }
    }
}
