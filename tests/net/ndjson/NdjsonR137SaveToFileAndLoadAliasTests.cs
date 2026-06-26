// Tests for NdjsonDocument.SaveToFile and LoadFromContent/LoadContent aliases.
// Sprint: ff-sprint-s136-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R137

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R137: Tests for NdjsonDocument.SaveToFile and the LoadFromContent/LoadContent named aliases.
/// SaveToFile writes the serialized NDJSON to disk (UTF-8 no BOM, LF-separated).
/// Throws NdjsonException for null/empty/whitespace path.
/// LoadFromContent and LoadContent are named aliases for Load(string) — prefer them for clarity.
/// Covers: SaveToFile null path throws NdjsonException; empty path throws; whitespace throws;
/// file created; content non-empty; round-trip via LoadFile same count;
/// LoadFromContent same result as Load; LoadContent same result as Load;
/// dogfood Filter->SaveToFile->LoadFile verifies filtered records.
/// </summary>
public class NdjsonR137SaveToFileAndLoadAliasTests
{
    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95,\"active\":true}\n" +
        "{\"name\":\"Bob\",\"score\":72,\"active\":false}\n" +
        "{\"name\":\"Carol\",\"score\":88,\"active\":true}";

    // -------------------------------------------------------------------------
    // SaveToFile null/empty guards
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_NullPath_ThrowsNdjsonException()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Throws<NdjsonException>(() => doc.SaveToFile(null!));
    }

    [Fact]
    public void SaveToFile_EmptyPath_ThrowsNdjsonException()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Throws<NdjsonException>(() => doc.SaveToFile(string.Empty));
    }

    [Fact]
    public void SaveToFile_WhitespacePath_ThrowsNdjsonException()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        Assert.Throws<NdjsonException>(() => doc.SaveToFile("   "));
    }

    // -------------------------------------------------------------------------
    // SaveToFile file creation
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ValidPath_CreatesFile()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r137_{Guid.NewGuid():N}.ndjson");
        try
        {
            doc.SaveToFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_ContentIsNonEmpty()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r137_{Guid.NewGuid():N}.ndjson");
        try
        {
            doc.SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.True(content.Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_RoundTripViaLoadFile_SameRecordCount()
    {
        var original = NdjsonDocument.Load(ThreeRecords);
        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r137_{Guid.NewGuid():N}.ndjson");
        try
        {
            original.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);
            Assert.Equal(original.Count, reloaded.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // LoadFromContent alias
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFromContent_ProducesDocumentWithSameCountAsLoad()
    {
        var via_load = NdjsonDocument.Load(ThreeRecords);
        var via_alias = NdjsonDocument.LoadFromContent(ThreeRecords);
        Assert.Equal(via_load.Count, via_alias.Count);
    }

    // -------------------------------------------------------------------------
    // LoadContent alias
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadContent_ProducesDocumentWithSameCountAsLoad()
    {
        var via_load = NdjsonDocument.Load(ThreeRecords);
        var via_alias = NdjsonDocument.LoadContent(ThreeRecords);
        Assert.Equal(via_load.Count, via_alias.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Filter -> SaveToFile -> LoadFile -> verify
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Filter_SaveToFile_LoadFile_ContainsOnlyActiveRecords()
    {
        var doc = NdjsonDocument.Load(ThreeRecords);
        var activeOnly = doc.Filter(r =>
            r.TryGetProperty("active", out var val) && val.GetBoolean());

        var path = Path.Combine(Path.GetTempPath(), $"ndjson_r137_dog_{Guid.NewGuid():N}.ndjson");
        try
        {
            activeOnly.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);

            // Alice (95, active) and Carol (88, active) — 2 records
            Assert.Equal(2, reloaded.Count);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice", content);
            Assert.Contains("Carol", content);
            Assert.DoesNotContain("Bob", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
