// Tests for NdjsonWriter.WriteRecordsToFile(records, path) — dedicated path-based write API.
// Sprint: FORMAT-FACTORY-NDJSON-R130-20260627
// Ledger: R130-GOVERNED-DOTNET-NDJSON-WRITE-RECORDS-TO-FILE-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R130: Dedicated tests for NdjsonWriter.WriteRecordsToFile(IEnumerable records, string path).
/// WriteRecordsToFile serializes each record as a JSON line and writes to a UTF-8 no-BOM file.
/// Throws ArgumentNullException for null records; NdjsonException for null/empty path.
/// Covers: file created; non-empty; line count matches record count; UTF-8 no-BOM;
/// each line is valid JSON; null records throws; null path throws;
/// empty path throws; roundtrip with ReadRecordsFromFile;
/// dogfood WriteRecordsToFile→ReadRecordsFromFile pipeline.
/// </summary>
public class NdjsonR130WriteRecordsToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ndjson-r130-{Guid.NewGuid():N}.ndjson");

    private static readonly object[] SampleRecords =
    [
        new { name = "Alice", score = 95 },
        new { name = "Bob",   score = 80 },
        new { name = "Carol", score = 88 },
    ];

    // -------------------------------------------------------------------------
    // Basic file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecordsToFile_ValidRecords_FileIsCreated()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_ValidRecords_FileIsNonEmpty()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_ValidRecords_LineCountMatchesRecordCount()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
            var lines = File.ReadAllLines(path);
            // Non-blank lines should equal SampleRecords.Length
            var nonBlank = System.Linq.Enumerable.Where(lines, l => !string.IsNullOrWhiteSpace(l));
            Assert.Equal(SampleRecords.Length, System.Linq.Enumerable.Count(nonBlank));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_ValidRecords_EachLineIsValidJson()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
            var content = File.ReadAllText(path);
            foreach (var line in content.Split('\n'))
            {
                if (string.IsNullOrWhiteSpace(line)) continue;
                // Should parse without throwing
                using var doc = JsonDocument.Parse(line);
                Assert.Equal(JsonValueKind.Object, doc.RootElement.ValueKind);
            }
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_Utf8NoBom_FirstBytesNotBom()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
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
    public void WriteRecordsToFile_NullRecords_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            NdjsonWriter.WriteRecordsToFile(null!, TempPath()));
    }

    [Fact]
    public void WriteRecordsToFile_NullPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() =>
            NdjsonWriter.WriteRecordsToFile(SampleRecords, null!));
    }

    [Fact]
    public void WriteRecordsToFile_EmptyPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() =>
            NdjsonWriter.WriteRecordsToFile(SampleRecords, string.Empty));
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRecordsToFile → ReadRecordsFromFile roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRecordsToFile_ThenReadRecordsFromFile_Roundtrip()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(SampleRecords, path);
            var read = NdjsonReader.ReadRecordsFromFile(path);

            Assert.Equal(SampleRecords.Length, read.Count);
            Assert.Equal(JsonValueKind.Object, read[0].ValueKind);
            Assert.Equal("Alice", read[0].GetProperty("name").GetString());
            Assert.Equal(88,      read[2].GetProperty("score").GetInt32());
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_EmptyList_CreatesEmptyFile()
    {
        var path = TempPath();
        try
        {
            NdjsonWriter.WriteRecordsToFile(new List<object>(), path);
            // File may be empty or whitespace only
            var content = File.ReadAllText(path);
            Assert.True(string.IsNullOrWhiteSpace(content));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
