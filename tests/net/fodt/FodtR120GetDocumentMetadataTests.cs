// Tests for FodtDocument.GetDocumentMetadata()
// Sprint: FORMAT-FACTORY-FODT-DOC-METADATA-20260626
// Ledger: R120-GOVERNED-DOTNET-FODT-DOC-METADATA-001

using System;
using System.IO;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R120: GetDocumentMetadata() — returns a read-only dictionary of metadata from
/// the office:meta element (title, creator, date, description, subject, language,
/// creation-date, editing-cycles, generator, initial-creator).
/// Missing fields are omitted; empty doc returns empty dict.
/// </summary>
public class FodtR120GetDocumentMetadataTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fodt"));

    // ---- Empty document ----

    [Fact]
    public void GetDocumentMetadata_EmptyDoc_ReturnsEmptyDict()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.Empty(meta);
    }

    // ---- CreateEmpty has no metadata ----

    [Fact]
    public void GetDocumentMetadata_CreateEmpty_HasNoTitle()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.False(meta.ContainsKey("title"));
    }

    // ---- Returns IReadOnlyDictionary ----

    [Fact]
    public void GetDocumentMetadata_ReturnsReadOnlyDictionary()
    {
        var doc = FodtDocument.CreateEmpty();
        var meta = doc.GetDocumentMetadata();
        Assert.IsAssignableFrom<IReadOnlyDictionary<string, string>>(meta);
    }

    // ---- Keys are lowercase strings ----

    [Fact]
    public void GetDocumentMetadata_AllKeysAreLowercase()
    {
        // Load a real fixture and check all keys are lowercase
        var path = Path.Combine(SamplesDir, "minimal-document.fodt");
        if (!File.Exists(path)) return; // skip if no fixture

        var doc = FodtDocument.Load(path);
        var meta = doc.GetDocumentMetadata();

        foreach (var key in meta.Keys)
        {
            Assert.Equal(key, key.ToLowerInvariant());
        }
    }

    // ---- Valid keys from known list ----

    [Fact]
    public void GetDocumentMetadata_AllKeysAreKnown()
    {
        var knownKeys = new System.Collections.Generic.HashSet<string>
        {
            "title", "creator", "date", "description", "subject", "language",
            "creation-date", "editing-cycles", "generator", "initial-creator"
        };

        var path = Path.Combine(SamplesDir, "minimal-document.fodt");
        if (!File.Exists(path)) return;

        var doc = FodtDocument.Load(path);
        var meta = doc.GetDocumentMetadata();

        foreach (var key in meta.Keys)
        {
            Assert.Contains(key, knownKeys);
        }
    }

    // ---- Not null for loaded fixture ----

    [Fact]
    public void GetDocumentMetadata_LoadedFixture_NotNull()
    {
        var path = Path.Combine(SamplesDir, "minimal-document.fodt");
        if (!File.Exists(path)) return;

        var doc = FodtDocument.Load(path);
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    // ---- Values are non-empty strings for present keys ----

    [Fact]
    public void GetDocumentMetadata_PresentKeys_HaveNonEmptyValues()
    {
        var path = Path.Combine(SamplesDir, "minimal-document.fodt");
        if (!File.Exists(path)) return;

        var doc = FodtDocument.Load(path);
        var meta = doc.GetDocumentMetadata();

        foreach (var kvp in meta)
        {
            Assert.False(string.IsNullOrEmpty(kvp.Value),
                $"Key '{kvp.Key}' should have non-empty value");
        }
    }

    // ---- Dogfood pipeline: load, inspect metadata, continue with content ----

    [Fact]
    public void DogfoodPipeline_LoadInspectMetadataThenReadContent()
    {
        var path = Path.Combine(SamplesDir, "minimal-document.fodt");
        if (!File.Exists(path)) return;

        var doc = FodtDocument.Load(path);

        // Metadata should not throw
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);

        // Content reading should still work after metadata inspection
        var wordCount = doc.GetWordCount();
        Assert.True(wordCount >= 0);

        var paraCount = doc.GetParagraphCount();
        Assert.True(paraCount >= 0);
    }

    // ---- CreateEmpty metadata does not exist: won't throw ----

    [Fact]
    public void GetDocumentMetadata_NeverThrows_ForAnyDocument()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Some content.");
        doc.InsertHeading(1, "A Heading", 1);

        // Must not throw even with no metadata element
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }
}
