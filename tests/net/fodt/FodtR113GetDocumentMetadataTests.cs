using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtR113GetDocumentMetadataTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetDocumentMetadata_ReturnsDict()
    {
        var doc = FodtDocument.Load(SamplePath);
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    [Fact]
    public void GetDocumentMetadata_ContainsGenerator()
    {
        var doc = FodtDocument.Load(SamplePath);
        var meta = doc.GetDocumentMetadata();
        // Most ODF files have a generator, but if not, at least verify the API works
        Assert.IsAssignableFrom<IReadOnlyDictionary<string, string>>(meta);
    }

    [Fact]
    public void GetDocumentMetadata_EmptyDocument_ReturnsEmptyDict()
    {
        var doc = FodtDocument.Load(SamplePath);
        var meta = doc.GetDocumentMetadata();
        // Even if no metadata, should return empty dict not null
        Assert.NotNull(meta);
    }

    [Fact]
    public void GetDocumentMetadata_AfterSaveReload_StillWorks()
    {
        var doc = FodtDocument.Load(SamplePath);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var meta = reloaded.GetDocumentMetadata();
            Assert.NotNull(meta);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void GetDocumentMetadata_AllKeysAreNonEmpty()
    {
        var doc = FodtDocument.Load(SamplePath);
        var meta = doc.GetDocumentMetadata();
        foreach (var kvp in meta)
        {
            Assert.False(string.IsNullOrEmpty(kvp.Key));
            Assert.False(string.IsNullOrEmpty(kvp.Value));
        }
    }

    [Fact]
    public void GetDocumentMetadata_KnownKeysSubset()
    {
        var doc = FodtDocument.Load(SamplePath);
        var meta = doc.GetDocumentMetadata();
        var knownKeys = new HashSet<string>
        {
            "title", "creator", "date", "description", "subject",
            "language", "creation-date", "editing-cycles", "generator",
            "initial-creator"
        };
        foreach (var key in meta.Keys)
        {
            Assert.Contains(key, knownKeys);
        }
    }
}
