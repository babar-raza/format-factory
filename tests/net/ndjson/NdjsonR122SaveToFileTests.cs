// Tests for NdjsonDocument.SaveToFile() — file persistence and round-trip via LoadFile.
// Sprint: FORMAT-FACTORY-NDJSON-SAVETOFILE-R122-20260626
// Ledger: R122-GOVERNED-DOTNET-NDJSON-SAVETOFILE-001

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R122: NdjsonDocument.SaveToFile(path) writes the document to disk as NDJSON.
/// LoadFile(path) after SaveToFile produces a document with the same record count,
/// same keys, and same field values. File encoding is UTF-8 without BOM.
/// </summary>
public class NdjsonR122SaveToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_ndjson_r122_{Guid.NewGuid():N}.ndjson");

    private static NdjsonDocument BuildDoc() =>
        NdjsonDocument.Load(
            "{\"name\":\"Alice\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"score\":87}\n" +
            "{\"name\":\"Carol\",\"score\":72}\n");

    // ---- File creation ----

    [Fact]
    public void SaveToFile_ValidPath_CreatesFile()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsJsonContent()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("{", content);
            Assert.Contains("}", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsFieldNames()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("name", content);
            Assert.Contains("score", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsFieldValues()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice", content);
            Assert.Contains("Bob",   content);
            Assert.Contains("Carol", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Round-trip: SaveToFile → LoadFile ----

    [Fact]
    public void RoundTrip_SaveAndLoad_CountPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);
            Assert.Equal(original.Count, reloaded.Count);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void RoundTrip_SaveAndLoad_KeysPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);
            var origKeys    = original.GetAllKeys();
            var reloadedKeys = reloaded.GetAllKeys();
            Assert.Equal(origKeys, reloadedKeys);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void RoundTrip_SaveAndLoad_FieldValuesPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);

            var origNames    = original.GetFieldValues("name");
            var reloadedNames = reloaded.GetFieldValues("name");
            Assert.Equal(origNames, reloadedNames);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Encoding ----

    [Fact]
    public void SaveToFile_Encoding_NoUtf8Bom()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var bytes = File.ReadAllBytes(path);
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "NDJSON file must not start with UTF-8 BOM");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Dogfood: product catalog round-trip ----

    [Fact]
    public void DogfoodPipeline_ProductCatalog_FullRoundTrip()
    {
        var path = TempPath();
        try
        {
            var original = NdjsonDocument.Load(
                "{\"sku\":\"P001\",\"name\":\"Widget Pro\",\"price\":29.99,\"inStock\":true}\n" +
                "{\"sku\":\"P002\",\"name\":\"Gadget Mini\",\"price\":9.99,\"inStock\":false}\n" +
                "{\"sku\":\"P003\",\"name\":\"Super Cable\",\"price\":4.99,\"inStock\":true}\n");

            original.SaveToFile(path);
            var reloaded = NdjsonDocument.LoadFile(path);

            // Count
            Assert.Equal(3, reloaded.Count);

            // Keys
            Assert.Contains("sku",     reloaded.GetAllKeys());
            Assert.Contains("name",    reloaded.GetAllKeys());
            Assert.Contains("price",   reloaded.GetAllKeys());
            Assert.Contains("inStock", reloaded.GetAllKeys());

            // Values
            var names = reloaded.GetFieldValues("name");
            Assert.Contains("Widget Pro",  names);
            Assert.Contains("Gadget Mini", names);
            Assert.Contains("Super Cable", names);

            var skus = reloaded.GetFieldValues("sku");
            Assert.Contains("P001", skus);
            Assert.Contains("P003", skus);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
