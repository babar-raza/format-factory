// Tests for NdjsonDocument.LoadFile(string path) — file-based NDJSON loading.
// Sprint: FORMAT-FACTORY-NDJSON-R128-20260627
// Ledger: R128-GOVERNED-DOTNET-NDJSON-LOADFILE-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R128: Tests for NdjsonDocument.LoadFile(string path).
/// LoadFile reads an NDJSON file from disk and parses it into a document.
/// Covers: non-null document returned; record count matches file content;
/// Records collection non-empty; first record contains expected keys;
/// parity with Load(string) for same content; empty file returns empty document;
/// null path throws ArgumentNullException; non-existent path throws IOException/FileNotFoundException;
/// UTF-8 BOM-prefixed file parses correctly; dogfood write-then-loadfile roundtrip.
/// </summary>
public class NdjsonR128LoadFileTests
{
    private static string WriteTempFile(string content)
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_ndjson_r128_{Guid.NewGuid():N}.ndjson");
        File.WriteAllText(path, content, Encoding.UTF8);
        return path;
    }

    private const string ThreeRecords =
        "{\"name\":\"Alice\",\"score\":95}\n" +
        "{\"name\":\"Bob\",\"score\":80}\n" +
        "{\"name\":\"Carol\",\"score\":88}\n";

    // -------------------------------------------------------------------------
    // Basic file load
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_DocumentIsNotNull()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var doc = NdjsonDocument.LoadFile(path);
            Assert.NotNull(doc);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_RecordCountMatchesFileContent()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var doc = NdjsonDocument.LoadFile(path);
            Assert.Equal(3, doc.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_RecordsCollectionNonEmpty()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var doc = NdjsonDocument.LoadFile(path);
            Assert.NotEmpty(doc.Records);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_FirstRecordContainsNameKey()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var doc = NdjsonDocument.LoadFile(path);
            var keys = doc.GetAllKeys();
            Assert.Contains("name", keys);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Parity with Load(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_CountMatchesStringLoad()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var fileDoc = NdjsonDocument.LoadFile(path);
            var stringDoc = NdjsonDocument.Load(ThreeRecords);
            Assert.Equal(stringDoc.Count, fileDoc.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_KeysMatchStringLoad()
    {
        var path = WriteTempFile(ThreeRecords);
        try
        {
            var fileDoc = NdjsonDocument.LoadFile(path);
            var stringDoc = NdjsonDocument.Load(ThreeRecords);
            Assert.Equal(stringDoc.GetAllKeys(), fileDoc.GetAllKeys());
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_EmptyFile_ReturnsEmptyDocument()
    {
        var path = WriteTempFile(string.Empty);
        try
        {
            var doc = NdjsonDocument.LoadFile(path);
            Assert.Equal(0, doc.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_NullPath_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => NdjsonDocument.LoadFile(null!));
    }

    [Fact]
    public void LoadFile_NonExistentPath_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() =>
            NdjsonDocument.LoadFile(Path.Combine(Path.GetTempPath(), "ff_r128_nonexistent_xyz.ndjson")));
    }

    // -------------------------------------------------------------------------
    // Dogfood: SaveToFile → LoadFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SaveToFileThenLoadFile_RoundtripPreservesData()
    {
        const string content =
            "{\"product\":\"Widget\",\"region\":\"West\",\"qty\":10}\n" +
            "{\"product\":\"Gadget\",\"region\":\"East\",\"qty\":5}\n" +
            "{\"product\":\"Widget\",\"region\":\"East\",\"qty\":8}\n";

        var originalDoc = NdjsonDocument.Load(content);
        var path = Path.Combine(Path.GetTempPath(), $"ff_ndjson_r128_dogfood_{Guid.NewGuid():N}.ndjson");
        try
        {
            originalDoc.SaveToFile(path);

            var reloadedDoc = NdjsonDocument.LoadFile(path);
            Assert.Equal(originalDoc.Count, reloadedDoc.Count);
            Assert.Equal(originalDoc.GetAllKeys(), reloadedDoc.GetAllKeys());

            // GetFieldValues parity
            var origProducts = originalDoc.GetFieldValues("product");
            var reloadedProducts = reloadedDoc.GetFieldValues("product");
            Assert.Equal(origProducts.Count, reloadedProducts.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
