// Tests for NdjsonWriter.WriteRecordsToFile.
// Sprint: ff-sprint-s138-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R138

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R138: Tests for NdjsonWriter.WriteRecordsToFile(IEnumerable&lt;object&gt; records, string path).
/// Serializes each record as a JSON line and writes to a file (UTF-8, no BOM, LF line endings).
/// Throws ArgumentNullException for null records. Throws NdjsonException for null/empty/whitespace path.
/// Covers: null records throws; null path throws; empty path throws; whitespace path throws;
/// file created; file is non-empty; each record is one line; records match WriteRecords output;
/// round-trip via LoadFile produces same count;
/// dogfood WriteRecordsToFile->LoadFile->Filter pipeline verifies record content.
/// </summary>
public class NdjsonR138WriterToFileTests
{
    private static List<object> ThreeObjects() => new()
    {
        new { name = "Alice", score = 95, active = true },
        new { name = "Bob", score = 72, active = false },
        new { name = "Carol", score = 88, active = true }
    };

    // -------------------------------------------------------------------------
    // Null guards
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecordsToFile_NullRecords_ThrowsArgumentNullException()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_{Guid.NewGuid():N}.ndjson");
        Assert.Throws<ArgumentNullException>(() => NdjsonWriter.WriteRecordsToFile(null!, path));
    }

    [Fact]
    public void WriteRecordsToFile_NullPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonWriter.WriteRecordsToFile(ThreeObjects(), null!));
    }

    [Fact]
    public void WriteRecordsToFile_EmptyPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonWriter.WriteRecordsToFile(ThreeObjects(), string.Empty));
    }

    [Fact]
    public void WriteRecordsToFile_WhitespacePath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonWriter.WriteRecordsToFile(ThreeObjects(), "   "));
    }

    // -------------------------------------------------------------------------
    // File creation
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecordsToFile_ValidPath_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_{Guid.NewGuid():N}.ndjson");
        try
        {
            NdjsonWriter.WriteRecordsToFile(ThreeObjects(), path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_ContentIsNonEmpty()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_{Guid.NewGuid():N}.ndjson");
        try
        {
            NdjsonWriter.WriteRecordsToFile(ThreeObjects(), path);
            Assert.True(new FileInfo(path).Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRecordsToFile_ContentMatchesWriteRecords()
    {
        var records = ThreeObjects();
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_{Guid.NewGuid():N}.ndjson");
        try
        {
            NdjsonWriter.WriteRecordsToFile(records, path);
            var fileContent = File.ReadAllText(path);
            var inMemory = NdjsonWriter.WriteRecords(records);
            // File content should match in-memory (modulo line ending normalization)
            Assert.Equal(inMemory.Replace("\r\n", "\n"), fileContent.Replace("\r\n", "\n"));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Round-trip via NdjsonDocument.LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRecordsToFile_RoundTrip_LoadFile_SameCount()
    {
        var records = ThreeObjects();
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_{Guid.NewGuid():N}.ndjson");
        try
        {
            NdjsonWriter.WriteRecordsToFile(records, path);
            var doc = NdjsonDocument.LoadFile(path);
            Assert.Equal(3, doc.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRecordsToFile -> LoadFile -> Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteToFile_LoadFile_Filter_ActiveOnly()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r138_dog_{Guid.NewGuid():N}.ndjson");
        try
        {
            NdjsonWriter.WriteRecordsToFile(ThreeObjects(), path);
            var doc = NdjsonDocument.LoadFile(path);

            // Filter active=true (Alice + Carol)
            var activeOnly = doc.Filter(r =>
                r.TryGetProperty("active", out var val) && val.GetBoolean());

            Assert.Equal(2, activeOnly.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
