// FormatFactory.Fodt Tests -- Edit/Save Capability Tests (G11-E Expanded Prototype)
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false
//
// Tests the load → edit → save → reload vertical slice for FODT.
// All tests use local fixture files only — no network.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for FODT edit-save round-trip capability (G11-E Expanded Prototype).
/// Validates: load, mutate paragraph text, save, reload, verify mutation persisted.
/// </summary>
public class FodtEditSaveTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtEditSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-edit-save-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // Edit-save round trip
    // -------------------------------------------------------------------------

    [Fact]
    public void EditSave_LoadEditSaveReload_ParagraphTextPersists()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        Assert.True(doc.Paragraphs.Count > 0, "Fixture must have at least one paragraph");

        const string editedText = "R23_EDIT_TEST_FODT_VALUE_99";
        doc.Paragraphs[0].SetText(editedText);

        var savedPath = Path.Combine(_tempDir, "edited.fodt");
        doc.Save(savedPath);
        Assert.True(File.Exists(savedPath), "Saved FODT file must exist");

        var reloaded = FodtDocument.Load(savedPath);
        Assert.True(reloaded.Paragraphs.Count > 0, "Reloaded doc must have paragraphs");
        Assert.Equal(editedText, reloaded.Paragraphs[0].Text);
    }

    [Fact]
    public void EditSave_SavedFile_IsNonEmpty()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var savedPath = Path.Combine(_tempDir, "saved.fodt");
        doc.Save(savedPath);

        var info = new FileInfo(savedPath);
        Assert.True(info.Length > 0, "Saved file must be non-empty");
    }

    [Fact]
    public void EditSave_SavedFile_IsValidXml()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var savedPath = Path.Combine(_tempDir, "saved.fodt");
        doc.Save(savedPath);

        // If we can reload it, it is valid XML
        var reloaded = FodtDocument.Load(savedPath);
        Assert.NotNull(reloaded);
    }

    [Fact]
    public void EditSave_ReloadedDoc_ParagraphCountMatches()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        int originalCount = doc.Paragraphs.Count;

        var savedPath = Path.Combine(_tempDir, "saved.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(originalCount, reloaded.Paragraphs.Count);
    }

    [Fact]
    public void EditSave_AppendText_PersistsAfterReload()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        if (doc.Paragraphs.Count == 0)
        {
            // Skip if no paragraphs (edge case)
            return;
        }

        var lastPara = doc.Paragraphs[^1];
        var originalText = lastPara.Text;
        var appendedText = originalText + " [R23_APPENDED]";
        lastPara.SetText(appendedText);

        var savedPath = Path.Combine(_tempDir, "appended.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        var reloadedLastPara = reloaded.Paragraphs[^1];
        Assert.Equal(appendedText, reloadedLastPara.Text);
    }

    // -------------------------------------------------------------------------
    // Governance
    // -------------------------------------------------------------------------

    [Fact]
    public void EditSave_DocumentMimeType_IsTextOrNull()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        Assert.True(
            doc.MimeType is null ||
            doc.MimeType.Contains("opendocument"),
            $"Unexpected MIME type: {doc.MimeType}");
    }
}
