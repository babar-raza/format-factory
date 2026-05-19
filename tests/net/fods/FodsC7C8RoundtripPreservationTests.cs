// FodsC7C8RoundtripPreservationTests -- R27 Lane G: FODS C7/C8 Round-Trip Preservation
// Sprint: R27
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// commercial_product_ready: false
//
// C7 = same-format save with round-trip fidelity (load -> edit -> save -> reload -> verify)
// C8 = opaque node preservation (unrecognized XML elements survive round-trip)
//
// All tests use local fixture files only -- no network.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for FODS C7 (round-trip fidelity) and C8 (opaque node preservation).
/// C7: load a FODS, edit a cell value, save, reload, verify the changed value persists
///      AND unaffected cells survive unchanged.
/// C8: unrecognized XML elements (custom namespaces, styles, metadata) survive round-trip.
///
/// The implementation uses XDocument (DOM-backed), which inherently preserves all nodes
/// that are not explicitly modified. C8 is therefore a natural consequence of the DOM
/// strategy and these tests verify that property.
/// </summary>
public class FodsC7C8RoundtripPreservationTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private static readonly string OpaqueNodesFods =
        Path.Combine(FixturesDir, "fods-opaque-nodes.fods");

    private readonly string _tempDir;

    public FodsC7C8RoundtripPreservationTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-c7c8-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // =========================================================================
    // C7: Round-Trip Fidelity — Edit + Verify Unchanged Cells Survive
    // =========================================================================

    /// <summary>
    /// C7-01: Edit cell A1, save, reload — edited value persists.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_EditedValuePersists()
    {
        var doc = FodsDocument.Load(MinimalFods);
        var sheet = doc.Sheets[0];

        const string newValue = "R27_C7_EDITED";
        sheet.Rows[0].Cells[0].SetText(newValue);

        var savedPath = Path.Combine(_tempDir, "c7-01.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        Assert.Equal(newValue, reloaded.Sheets[0].Rows[0].Cells[0].Value);
    }

    /// <summary>
    /// C7-02: Edit cell A1, save, reload — unaffected cell B1 survives unchanged.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_UneditedCellB1Survives()
    {
        var doc = FodsDocument.Load(MinimalFods);
        var sheet = doc.Sheets[0];

        // Record original B1 value
        var originalB1 = sheet.Rows[0].Cells[1].Value;
        Assert.Equal("World", originalB1);

        // Edit only A1
        sheet.Rows[0].Cells[0].SetText("CHANGED_A1");

        var savedPath = Path.Combine(_tempDir, "c7-02.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        Assert.Equal("World", reloaded.Sheets[0].Rows[0].Cells[1].Value);
    }

    /// <summary>
    /// C7-03: Edit cell A1, save, reload — unaffected row 2 survives unchanged.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_Row2Survives()
    {
        var doc = FodsDocument.Load(MinimalFods);
        sheet_edit_and_save(doc, "c7-03.fods", out var reloaded);

        Assert.Equal("Row2Cell1", reloaded.Sheets[0].Rows[1].Cells[0].Value);
    }

    /// <summary>
    /// C7-04: Edit cell A1, save, reload — sheet count preserved.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_SheetCountPreserved()
    {
        var doc = FodsDocument.Load(MinimalFods);
        int originalCount = doc.Sheets.Count;

        sheet_edit_and_save(doc, "c7-04.fods", out var reloaded);

        Assert.Equal(originalCount, reloaded.Sheets.Count);
    }

    /// <summary>
    /// C7-05: Edit cell A1, save, reload — row count preserved.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_RowCountPreserved()
    {
        var doc = FodsDocument.Load(MinimalFods);
        int originalRows = doc.Sheets[0].Rows.Count;

        sheet_edit_and_save(doc, "c7-05.fods", out var reloaded);

        Assert.Equal(originalRows, reloaded.Sheets[0].Rows.Count);
    }

    /// <summary>
    /// C7-06: Edit cell A1, save, reload — sheet name preserved.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_SheetNamePreserved()
    {
        var doc = FodsDocument.Load(MinimalFods);
        string originalName = doc.Sheets[0].Name;

        sheet_edit_and_save(doc, "c7-06.fods", out var reloaded);

        Assert.Equal(originalName, reloaded.Sheets[0].Name);
    }

    /// <summary>
    /// C7-07: Edit cell A1, save, reload — MimeType preserved.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_MimeTypePreserved()
    {
        var doc = FodsDocument.Load(MinimalFods);
        string? originalMime = doc.MimeType;

        sheet_edit_and_save(doc, "c7-07.fods", out var reloaded);

        Assert.Equal(originalMime, reloaded.MimeType);
    }

    /// <summary>
    /// C7-08: Edit cell A1, save, reload — OdfVersion preserved.
    /// </summary>
    [Fact]
    public void C7_EditCellA1_SaveReload_OdfVersionPreserved()
    {
        var doc = FodsDocument.Load(MinimalFods);
        string? originalVersion = doc.OdfVersion;

        sheet_edit_and_save(doc, "c7-08.fods", out var reloaded);

        Assert.Equal(originalVersion, reloaded.OdfVersion);
    }

    /// <summary>
    /// C7-09: Double round-trip (edit, save, reload, edit again, save, reload) — fidelity holds.
    /// </summary>
    [Fact]
    public void C7_DoubleRoundtrip_FidelityHolds()
    {
        // First round-trip
        var doc = FodsDocument.Load(MinimalFods);
        doc.Sheets[0].Rows[0].Cells[0].SetText("PASS_1");

        var path1 = Path.Combine(_tempDir, "c7-09-pass1.fods");
        doc.Save(path1);

        // Second round-trip
        var doc2 = FodsDocument.Load(path1);
        Assert.Equal("PASS_1", doc2.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal("World", doc2.Sheets[0].Rows[0].Cells[1].Value);

        doc2.Sheets[0].Rows[0].Cells[1].SetText("PASS_2");

        var path2 = Path.Combine(_tempDir, "c7-09-pass2.fods");
        doc2.Save(path2);

        var doc3 = FodsDocument.Load(path2);
        Assert.Equal("PASS_1", doc3.Sheets[0].Rows[0].Cells[0].Value);
        Assert.Equal("PASS_2", doc3.Sheets[0].Rows[0].Cells[1].Value);
        Assert.Equal("Row2Cell1", doc3.Sheets[0].Rows[1].Cells[0].Value);
    }

    /// <summary>
    /// C7-10: Multi-sheet fixture — edit in sheet 1 does not corrupt sheet 2.
    /// Uses the multi-sheet fixture if available, otherwise uses inline XML.
    /// </summary>
    [Fact]
    public void C7_MultiSheet_EditSheet1_Sheet2Survives()
    {
        var multiSheetPath = Path.Combine(FixturesDir, "fods-multi-sheet.fods");
        if (!File.Exists(multiSheetPath))
        {
            // Use inline minimal multi-sheet FODS
            const string xml =
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
                "<office:document" +
                " xmlns:office=\"urn:oasis:names:tc:opendocument:xmlns:office:1.0\"" +
                " xmlns:table=\"urn:oasis:names:tc:opendocument:xmlns:table:1.0\"" +
                " xmlns:text=\"urn:oasis:names:tc:opendocument:xmlns:text:1.0\"" +
                " office:mimetype=\"application/vnd.oasis.opendocument.spreadsheet-flat-xml\"" +
                " office:version=\"1.3\">" +
                "<office:body><office:spreadsheet>" +
                "<table:table table:name=\"Sheet1\">" +
                "<table:table-row><table:table-cell office:value-type=\"string\"><text:p>S1R1</text:p></table:table-cell></table:table-row>" +
                "</table:table>" +
                "<table:table table:name=\"Sheet2\">" +
                "<table:table-row><table:table-cell office:value-type=\"string\"><text:p>S2R1</text:p></table:table-cell></table:table-row>" +
                "</table:table>" +
                "</office:spreadsheet></office:body></office:document>";

            multiSheetPath = Path.Combine(_tempDir, "multi-sheet-inline.fods");
            File.WriteAllText(multiSheetPath, xml);
        }

        var doc = FodsDocument.Load(multiSheetPath);
        Assert.True(doc.Sheets.Count >= 2, "Need at least 2 sheets for this test");

        string sheet2Name = doc.Sheets[1].Name;
        string? sheet2CellValue = doc.Sheets[1].Rows.Count > 0 && doc.Sheets[1].Rows[0].Cells.Count > 0
            ? doc.Sheets[1].Rows[0].Cells[0].Value
            : null;

        // Edit only sheet 1
        if (doc.Sheets[0].Rows.Count > 0 && doc.Sheets[0].Rows[0].Cells.Count > 0)
            doc.Sheets[0].Rows[0].Cells[0].SetText("SHEET1_EDITED");

        var savedPath = Path.Combine(_tempDir, "c7-10.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        Assert.Equal(sheet2Name, reloaded.Sheets[1].Name);
        if (sheet2CellValue != null)
        {
            Assert.Equal(sheet2CellValue, reloaded.Sheets[1].Rows[0].Cells[0].Value);
        }
    }

    // =========================================================================
    // C8: Opaque Node Preservation — Unknown XML Elements Survive Round-Trip
    // =========================================================================

    /// <summary>
    /// C8-01: Custom namespace element in office:meta survives no-edit round-trip.
    /// </summary>
    [Fact]
    public void C8_OpaqueMetaElement_SurvivesNoEditRoundtrip()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);

        var savedPath = Path.Combine(_tempDir, "c8-01.fods");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("custom:vendor-metadata", content);
        Assert.Contains("Custom vendor data", content);
        Assert.Contains("http://example.org/custom-extension/1.0", content);
    }

    /// <summary>
    /// C8-02: Custom namespace element survives edit round-trip (edit cell, save, verify opaque node).
    /// </summary>
    [Fact]
    public void C8_OpaqueMetaElement_SurvivesEditRoundtrip()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);

        // Edit a cell
        doc.Sheets[0].Rows[0].Cells[0].SetText("C8_EDITED");

        var savedPath = Path.Combine(_tempDir, "c8-02.fods");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        // Verify edit persisted
        Assert.Contains("C8_EDITED", content);
        // Verify opaque node survived
        Assert.Contains("custom:vendor-metadata", content);
        Assert.Contains("Custom vendor data", content);
    }

    /// <summary>
    /// C8-03: office:automatic-styles section survives round-trip (style elements are opaque to cell edits).
    /// </summary>
    [Fact]
    public void C8_AutomaticStyles_SurviveRoundtrip()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);
        doc.Sheets[0].Rows[0].Cells[0].SetText("STYLE_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-03.fods");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("style:style", content);
        Assert.Contains("style:name=\"co1\"", content);
    }

    /// <summary>
    /// C8-04: dc:title metadata element survives edit round-trip.
    /// </summary>
    [Fact]
    public void C8_DcTitle_SurvivesEditRoundtrip()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);
        doc.Sheets[0].Rows[1].Cells[0].SetText("TITLE_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-04.fods");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("Opaque Node Test", content);
    }

    /// <summary>
    /// C8-05: Custom attribute on opaque element survives round-trip.
    /// </summary>
    [Fact]
    public void C8_CustomAttribute_SurvivesRoundtrip()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);
        doc.Sheets[0].Rows[0].Cells[0].SetText("ATTR_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-05.fods");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        // The custom:version="42" attribute on the opaque element
        Assert.Contains("42", content);
    }

    /// <summary>
    /// C8-06: Reloaded document after edit retains correct cell count (no node duplication).
    /// </summary>
    [Fact]
    public void C8_EditRoundtrip_NoDuplicateNodes()
    {
        var doc = FodsDocument.Load(OpaqueNodesFods);
        int originalRowCount = doc.Sheets[0].Rows.Count;
        int originalCellCountR0 = doc.Sheets[0].Rows[0].Cells.Count;

        doc.Sheets[0].Rows[0].Cells[0].SetText("NO_DUP_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-06.fods");
        doc.Save(savedPath);

        var reloaded = FodsDocument.Load(savedPath);
        Assert.Equal(originalRowCount, reloaded.Sheets[0].Rows.Count);
        Assert.Equal(originalCellCountR0, reloaded.Sheets[0].Rows[0].Cells.Count);
    }

    // =========================================================================
    // Helpers
    // =========================================================================

    private void sheet_edit_and_save(FodsDocument doc, string filename, out FodsDocument reloaded)
    {
        doc.Sheets[0].Rows[0].Cells[0].SetText("R27_HELPER_EDIT");

        var savedPath = Path.Combine(_tempDir, filename);
        doc.Save(savedPath);

        reloaded = FodsDocument.Load(savedPath);
    }
}
