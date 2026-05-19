// FodtC7C8RoundtripPreservationTests -- R27 Lane H: FODT C7/C8 Round-Trip Preservation
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

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// Tests for FODT C7 (round-trip fidelity) and C8 (opaque node preservation).
/// C7: load a FODT, edit paragraph text, save, reload, verify the changed text persists
///      AND unaffected paragraphs survive unchanged.
/// C8: unrecognized XML elements (custom namespaces, styles, metadata) survive round-trip.
///
/// The implementation uses XDocument (DOM-backed), which inherently preserves all nodes
/// that are not explicitly modified. C8 is therefore a natural consequence of the DOM
/// strategy and these tests verify that property.
/// </summary>
public class FodtC7C8RoundtripPreservationTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private static readonly string OpaqueNodesFodt =
        Path.Combine(FixturesDir, "fodt-opaque-nodes.fodt");

    private readonly string _tempDir;

    public FodtC7C8RoundtripPreservationTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-c7c8-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // =========================================================================
    // C7: Round-Trip Fidelity -- Edit + Verify Unchanged Paragraphs Survive
    // =========================================================================

    /// <summary>
    /// C7-01: Edit first paragraph, save, reload -- edited text persists.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_EditedTextPersists()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        const string newText = "R27_C7_FODT_EDITED";
        doc.Paragraphs[0].SetText(newText);

        var savedPath = Path.Combine(_tempDir, "c7-01.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(newText, reloaded.Paragraphs[0].Text);
    }

    /// <summary>
    /// C7-02: Edit first paragraph, save, reload -- unaffected paragraph 1 survives.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_Paragraph1Survives()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        doc.Paragraphs[0].SetText("CHANGED_P0");

        var savedPath = Path.Combine(_tempDir, "c7-02.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal("Second paragraph.", reloaded.Paragraphs[1].Text);
    }

    /// <summary>
    /// C7-03: Edit first paragraph, save, reload -- heading survives unchanged.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_HeadingSurvives()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        doc.Paragraphs[0].SetText("CHANGED_P0");

        var savedPath = Path.Combine(_tempDir, "c7-03.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal("A Heading", reloaded.Paragraphs[2].Text);
        Assert.True(reloaded.Paragraphs[2].IsHeading);
    }

    /// <summary>
    /// C7-04: Edit first paragraph, save, reload -- paragraph count preserved.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_ParagraphCountPreserved()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        int originalCount = doc.Paragraphs.Count;

        doc.Paragraphs[0].SetText("CHANGED_P0");

        var savedPath = Path.Combine(_tempDir, "c7-04.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(originalCount, reloaded.Paragraphs.Count);
    }

    /// <summary>
    /// C7-05: Edit first paragraph, save, reload -- MimeType preserved.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_MimeTypePreserved()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        string? originalMime = doc.MimeType;

        doc.Paragraphs[0].SetText("CHANGED_P0");

        var savedPath = Path.Combine(_tempDir, "c7-05.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(originalMime, reloaded.MimeType);
    }

    /// <summary>
    /// C7-06: Edit first paragraph, save, reload -- OdfVersion preserved.
    /// </summary>
    [Fact]
    public void C7_EditParagraph0_SaveReload_OdfVersionPreserved()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        string? originalVersion = doc.OdfVersion;

        doc.Paragraphs[0].SetText("CHANGED_P0");

        var savedPath = Path.Combine(_tempDir, "c7-06.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(originalVersion, reloaded.OdfVersion);
    }

    /// <summary>
    /// C7-07: Edit heading text, save, reload -- heading status and outline level preserved.
    /// </summary>
    [Fact]
    public void C7_EditHeading_SaveReload_HeadingStatusPreserved()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        // Paragraph[2] is the heading "A Heading"
        Assert.True(doc.Paragraphs[2].IsHeading);
        int originalLevel = doc.Paragraphs[2].OutlineLevel;

        doc.Paragraphs[2].SetText("Edited Heading");

        var savedPath = Path.Combine(_tempDir, "c7-07.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal("Edited Heading", reloaded.Paragraphs[2].Text);
        Assert.True(reloaded.Paragraphs[2].IsHeading);
        Assert.Equal(originalLevel, reloaded.Paragraphs[2].OutlineLevel);
    }

    /// <summary>
    /// C7-08: Double round-trip -- edit, save, reload, edit again, save, reload.
    /// </summary>
    [Fact]
    public void C7_DoubleRoundtrip_FidelityHolds()
    {
        // First round-trip
        var doc = FodtDocument.Load(MinimalFodt);
        doc.Paragraphs[0].SetText("PASS_1");

        var path1 = Path.Combine(_tempDir, "c7-08-pass1.fodt");
        doc.Save(path1);

        // Second round-trip
        var doc2 = FodtDocument.Load(path1);
        Assert.Equal("PASS_1", doc2.Paragraphs[0].Text);
        Assert.Equal("Second paragraph.", doc2.Paragraphs[1].Text);

        doc2.Paragraphs[1].SetText("PASS_2");

        var path2 = Path.Combine(_tempDir, "c7-08-pass2.fodt");
        doc2.Save(path2);

        var doc3 = FodtDocument.Load(path2);
        Assert.Equal("PASS_1", doc3.Paragraphs[0].Text);
        Assert.Equal("PASS_2", doc3.Paragraphs[1].Text);
        Assert.Equal("A Heading", doc3.Paragraphs[2].Text);
        Assert.Equal("Third paragraph after heading.", doc3.Paragraphs[3].Text);
    }

    /// <summary>
    /// C7-09: Edit last paragraph, save, reload -- first paragraph unchanged.
    /// </summary>
    [Fact]
    public void C7_EditLastParagraph_SaveReload_FirstParagraphSurvives()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        doc.Paragraphs[^1].SetText("LAST_EDITED");

        var savedPath = Path.Combine(_tempDir, "c7-09.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal("Hello, world.", reloaded.Paragraphs[0].Text);
        Assert.Equal("LAST_EDITED", reloaded.Paragraphs[^1].Text);
    }

    // =========================================================================
    // C8: Opaque Node Preservation -- Unknown XML Elements Survive Round-Trip
    // =========================================================================

    /// <summary>
    /// C8-01: Custom namespace element in office:meta survives no-edit round-trip.
    /// </summary>
    [Fact]
    public void C8_OpaqueMetaElement_SurvivesNoEditRoundtrip()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);

        var savedPath = Path.Combine(_tempDir, "c8-01.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("custom:vendor-metadata", content);
        Assert.Contains("Custom vendor text data", content);
        Assert.Contains("http://example.org/custom-extension/1.0", content);
    }

    /// <summary>
    /// C8-02: Custom namespace element survives edit round-trip.
    /// </summary>
    [Fact]
    public void C8_OpaqueMetaElement_SurvivesEditRoundtrip()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);

        // Edit a paragraph
        doc.Paragraphs[0].SetText("C8_FODT_EDITED");

        var savedPath = Path.Combine(_tempDir, "c8-02.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("C8_FODT_EDITED", content);
        Assert.Contains("custom:vendor-metadata", content);
        Assert.Contains("Custom vendor text data", content);
    }

    /// <summary>
    /// C8-03: office:automatic-styles section survives round-trip.
    /// </summary>
    [Fact]
    public void C8_AutomaticStyles_SurviveRoundtrip()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);
        doc.Paragraphs[0].SetText("STYLE_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-03.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("style:style", content);
        Assert.Contains("style:name=\"P1\"", content);
    }

    /// <summary>
    /// C8-04: dc:title metadata element survives edit round-trip.
    /// </summary>
    [Fact]
    public void C8_DcTitle_SurvivesEditRoundtrip()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);
        doc.Paragraphs[1].SetText("TITLE_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-04.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("Opaque Node Text Test", content);
    }

    /// <summary>
    /// C8-05: Custom attribute on opaque element survives round-trip.
    /// </summary>
    [Fact]
    public void C8_CustomAttribute_SurvivesRoundtrip()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);
        doc.Paragraphs[0].SetText("ATTR_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-05.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("99", content);
    }

    /// <summary>
    /// C8-06: Reloaded document after edit retains correct paragraph count (no node duplication).
    /// </summary>
    [Fact]
    public void C8_EditRoundtrip_NoDuplicateNodes()
    {
        var doc = FodtDocument.Load(OpaqueNodesFodt);
        int originalCount = doc.Paragraphs.Count;

        doc.Paragraphs[0].SetText("NO_DUP_CHECK");

        var savedPath = Path.Combine(_tempDir, "c8-06.fodt");
        doc.Save(savedPath);

        var reloaded = FodtDocument.Load(savedPath);
        Assert.Equal(originalCount, reloaded.Paragraphs.Count);
    }

    /// <summary>
    /// C8-07: office:automatic-styles from minimal fixture (style:) survives no-edit round-trip.
    /// Uses the minimal fixture which has an empty office:automatic-styles element.
    /// </summary>
    [Fact]
    public void C8_MinimalFixture_AutomaticStylesSurvive()
    {
        var doc = FodtDocument.Load(MinimalFodt);

        var savedPath = Path.Combine(_tempDir, "c8-07.fodt");
        doc.Save(savedPath);

        var content = File.ReadAllText(savedPath);
        Assert.Contains("automatic-styles", content);
    }
}
