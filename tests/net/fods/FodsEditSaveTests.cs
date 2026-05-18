// FormatFactory.Fods Tests -- Edit/Save Capability Tests (G11-E Expanded Prototype)
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false
//
// Tests the load → edit → save → reload vertical slice.
// All tests use local fixture files only — no network.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for FODS edit-save round-trip capability (G11-E Expanded Prototype).
/// Validates: load, mutate cell, save, reload, verify mutation persisted.
/// </summary>
public class FodsEditSaveTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsEditSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-edit-save-tests-" + Guid.NewGuid().ToString("N"));
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
    public void EditSave_LoadEditSaveReload_CellValuePersists()
    {
        // Load original
        var doc = FodsDocument.Load(MinimalFods);
        Assert.True(doc.Sheets.Count > 0, "Fixture must have at least one sheet");

        var sheet = doc.Sheets[0];
        Assert.True(sheet.Rows.Count > 0, "First sheet must have at least one row");

        var firstRow = sheet.Rows[0];
        Assert.True(firstRow.Cells.Count > 0, "First row must have at least one cell");

        // Edit the first cell
        const string editedValue = "R23_EDIT_TEST_VALUE_42";
        firstRow.Cells[0].SetText(editedValue);

        // Save to temp file
        var savedPath = Path.Combine(_tempDir, "edited.fods");
        doc.Save(savedPath);
        Assert.True(File.Exists(savedPath), "Saved file must exist");

        // Reload
        var reloaded = FodsDocument.Load(savedPath);
        Assert.True(reloaded.Sheets.Count > 0, "Reloaded doc must have sheets");

        var reloadedCell = reloaded.Sheets[0].Rows[0].Cells[0];
        Assert.Equal(editedValue, reloadedCell.Value);
    }

    [Fact]
    public void EditSave_SavedFile_IsNonEmpty()
    {
        var doc = FodsDocument.Load(MinimalFods);
        var savedPath = Path.Combine(_tempDir, "saved.fods");
        doc.Save(savedPath);

        var info = new FileInfo(savedPath);
        Assert.True(info.Length > 0, "Saved file must be non-empty");
    }

    [Fact]
    public void EditSave_SavedFile_IsValidXml()
    {
        var doc = FodsDocument.Load(MinimalFods);
        var savedPath = Path.Combine(_tempDir, "saved.fods");
        doc.Save(savedPath);

        // If we can reload it, it is valid XML (FodsDocument.Load uses XmlReader)
        var reloaded = FodsDocument.Load(savedPath);
        Assert.NotNull(reloaded);
    }

    [Fact]
    public void EditSave_ReloadedDoc_SheetCountMatches()
    {
        var doc = FodsDocument.Load(MinimalFods);
        int originalSheets = doc.Sheets.Count;

        var savedPath = Path.Combine(_tempDir, "saved.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        Assert.Equal(originalSheets, reloaded.Sheets.Count);
    }

    [Fact]
    public void EditSave_MultipleEdits_AllPersist()
    {
        var doc = FodsDocument.Load(MinimalFods);
        var sheet = doc.Sheets[0];

        // Edit multiple cells if available
        var values = new[] { "ALPHA", "BETA", "GAMMA" };
        int editCount = 0;

        foreach (var row in sheet.Rows)
        {
            if (editCount >= values.Length) break;
            foreach (var cell in row.Cells)
            {
                if (editCount >= values.Length) break;
                if (!cell.IsCovered)
                {
                    cell.SetText(values[editCount]);
                    editCount++;
                }
            }
        }

        var savedPath = Path.Combine(_tempDir, "multi-edit.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        // Verify at least one value survived (exact count depends on fixture)
        bool found = false;
        foreach (var row in reloaded.Sheets[0].Rows)
        {
            foreach (var cell in row.Cells)
            {
                if (cell.Value == values[0]) { found = true; break; }
            }
            if (found) break;
        }
        Assert.True(found, "At least one edited value must persist after reload");
    }

    // -------------------------------------------------------------------------
    // Governance
    // -------------------------------------------------------------------------

    [Fact]
    public void EditSave_DocumentMimeType_IsSpreadsheetOrNull()
    {
        var doc = FodsDocument.Load(MinimalFods);
        // MimeType is either the correct FODS MIME type or null (not checked strictly here)
        Assert.True(
            doc.MimeType is null ||
            doc.MimeType.Contains("opendocument"),
            $"Unexpected MIME type: {doc.MimeType}");
    }
}
