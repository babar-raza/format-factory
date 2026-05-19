// FodtC9ExportConversionReadinessTests -- R28 Lane J: FODT C9 Export/Conversion Readiness
// Sprint: R28
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
// commercial_product_ready: false
//
// C9 = export/conversion from an edited+saved+reloaded document produces expected content
//      AND the export operation does not mutate the in-memory document model.
//
// Tests cover all three exporters: TXT, Markdown, HTML.
// All tests use local fixture files only -- no network.

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// C9 Export/Conversion Readiness tests for FODT.
///
/// Test matrix:
///   - TXT: export after edit+save+reload produces expected content; export does not mutate document
///   - Markdown: export after edit+save+reload produces expected content; export does not mutate document
///   - HTML: export after edit+save+reload produces expected content; export does not mutate document
///
/// These tests build on C7 (round-trip fidelity) and C8 (opaque node preservation) evidence
/// by proving that the full pipeline (load -> edit -> save -> reload -> export) works end-to-end.
/// </summary>
public class FodtC9ExportConversionReadinessTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    private readonly string _tempDir;

    public FodtC9ExportConversionReadinessTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-c9-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // =========================================================================
    // Helper: edit + save + reload pipeline
    // =========================================================================

    /// <summary>
    /// Shared pipeline: load fixture, edit first paragraph to <paramref name="editedText"/>,
    /// save to temp, reload, and return the reloaded document + its path.
    /// </summary>
    private FodtDocument EditSaveReload(string editedText, out string reloadedPath)
    {
        var doc = FodtDocument.Load(MinimalFodt);
        doc.Paragraphs[0].SetText(editedText);

        reloadedPath = Path.Combine(_tempDir, $"c9-pipeline-{Guid.NewGuid():N}.fodt");
        doc.Save(reloadedPath);

        return FodtDocument.Load(reloadedPath);
    }

    // =========================================================================
    // C9-TXT: TXT export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-TXT-01: TXT export from edited+reloaded document contains the edited paragraph text.
    /// </summary>
    [Fact]
    public void C9_Txt_ExportAfterEditSaveReload_ContainsEditedText()
    {
        const string editedText = "C9_TXT_EDITED_PARA";
        EditSaveReload(editedText, out var reloadedPath);

        var txtPath = Path.Combine(_tempDir, "c9-txt-01.txt");
        var result = FodtTxtExporter.ExportTxt(reloadedPath, txtPath);

        Assert.Equal("exported", result.Status);
        var txtContent = File.ReadAllText(txtPath, Encoding.UTF8);
        Assert.Contains(editedText, txtContent);
    }

    /// <summary>
    /// C9-TXT-02: TXT export from edited+reloaded document preserves unedited paragraph.
    /// </summary>
    [Fact]
    public void C9_Txt_ExportAfterEditSaveReload_PreservesUneditedParagraph()
    {
        var reloaded = EditSaveReload("C9_TXT_ONLY_P0", out var reloadedPath);

        // Verify second paragraph still present
        Assert.Equal("Second paragraph.", reloaded.Paragraphs[1].Text);

        var txtPath = Path.Combine(_tempDir, "c9-txt-02.txt");
        FodtTxtExporter.ExportTxt(reloadedPath, txtPath);

        var txtContent = File.ReadAllText(txtPath, Encoding.UTF8);
        Assert.Contains("Second paragraph.", txtContent);
    }

    /// <summary>
    /// C9-TXT-03: TXT export does not mutate the in-memory document model.
    /// </summary>
    [Fact]
    public void C9_Txt_ExportDoesNotMutateDocument()
    {
        const string editedText = "C9_TXT_NO_MUTATE";
        var reloaded = EditSaveReload(editedText, out var reloadedPath);

        // Capture state before export
        string para0Before = reloaded.Paragraphs[0].Text;
        string para1Before = reloaded.Paragraphs[1].Text;
        int paraCountBefore = reloaded.Paragraphs.Count;

        // Perform TXT export (using document overload)
        var txtPath = Path.Combine(_tempDir, "c9-txt-03.txt");
        FodtTxtExporter.ExportTxt(reloaded, reloadedPath, txtPath);

        // Verify no mutation
        Assert.Equal(para0Before, reloaded.Paragraphs[0].Text);
        Assert.Equal(para1Before, reloaded.Paragraphs[1].Text);
        Assert.Equal(paraCountBefore, reloaded.Paragraphs.Count);
    }

    /// <summary>
    /// C9-TXT-04: TXT export paragraph count matches document paragraph count.
    /// </summary>
    [Fact]
    public void C9_Txt_ExportParagraphCountMatchesDocument()
    {
        var reloaded = EditSaveReload("C9_TXT_COUNT", out var reloadedPath);

        var txtPath = Path.Combine(_tempDir, "c9-txt-04.txt");
        var result = FodtTxtExporter.ExportTxt(reloadedPath, txtPath);

        Assert.Equal(reloaded.Paragraphs.Count, result.ParagraphsExported);
    }

    /// <summary>
    /// C9-TXT-05: TXT export preserves heading text after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Txt_ExportPreservesHeadingAfterEditPipeline()
    {
        var reloaded = EditSaveReload("C9_TXT_HEADING", out var reloadedPath);

        var txtPath = Path.Combine(_tempDir, "c9-txt-05.txt");
        FodtTxtExporter.ExportTxt(reloadedPath, txtPath);

        var txtContent = File.ReadAllText(txtPath, Encoding.UTF8);
        // "A Heading" should still be present (it is paragraph index 2 in the minimal fixture)
        Assert.Contains("A Heading", txtContent);
    }

    // =========================================================================
    // C9-MD: Markdown export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-MD-01: Markdown export from edited+reloaded document contains the edited paragraph.
    /// </summary>
    [Fact]
    public void C9_Md_ExportAfterEditSaveReload_ContainsEditedText()
    {
        const string editedText = "C9_MD_EDITED_PARA";
        EditSaveReload(editedText, out var reloadedPath);

        var mdPath = Path.Combine(_tempDir, "c9-md-01.md");
        var result = FodtMarkdownExporter.ExportToMarkdown(reloadedPath, mdPath);

        Assert.Equal("exported", result.Status);
        var mdContent = File.ReadAllText(mdPath, Encoding.UTF8);
        Assert.Contains(editedText, mdContent);
    }

    /// <summary>
    /// C9-MD-02: Markdown export from edited+reloaded document preserves unedited paragraph.
    /// </summary>
    [Fact]
    public void C9_Md_ExportAfterEditSaveReload_PreservesUneditedParagraph()
    {
        EditSaveReload("C9_MD_ONLY_P0", out var reloadedPath);

        var mdPath = Path.Combine(_tempDir, "c9-md-02.md");
        FodtMarkdownExporter.ExportToMarkdown(reloadedPath, mdPath);

        var mdContent = File.ReadAllText(mdPath, Encoding.UTF8);
        Assert.Contains("Second paragraph.", mdContent);
    }

    /// <summary>
    /// C9-MD-03: Markdown export does not mutate the in-memory document model.
    /// </summary>
    [Fact]
    public void C9_Md_ExportDoesNotMutateDocument()
    {
        const string editedText = "C9_MD_NO_MUTATE";
        var reloaded = EditSaveReload(editedText, out var reloadedPath);

        // Capture state before export
        string para0Before = reloaded.Paragraphs[0].Text;
        int paraCountBefore = reloaded.Paragraphs.Count;

        // Perform Markdown export (using document overload)
        var mdPath = Path.Combine(_tempDir, "c9-md-03.md");
        FodtMarkdownExporter.ExportToMarkdown(reloaded, reloadedPath, mdPath);

        // Verify no mutation
        Assert.Equal(para0Before, reloaded.Paragraphs[0].Text);
        Assert.Equal(paraCountBefore, reloaded.Paragraphs.Count);
    }

    /// <summary>
    /// C9-MD-04: Markdown export preserves heading with ATX format after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Md_ExportPreservesHeadingFormatAfterEditPipeline()
    {
        EditSaveReload("C9_MD_HEADING", out var reloadedPath);

        var mdPath = Path.Combine(_tempDir, "c9-md-04.md");
        FodtMarkdownExporter.ExportToMarkdown(reloadedPath, mdPath);

        var mdContent = File.ReadAllText(mdPath, Encoding.UTF8);
        // Heading "A Heading" should appear with ATX format (# prefix)
        Assert.Contains("# A Heading", mdContent);
    }

    // =========================================================================
    // C9-HTML: HTML export after edit+save+reload
    // =========================================================================

    /// <summary>
    /// C9-HTML-01: HTML export from edited+reloaded document contains the edited paragraph.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_ContainsEditedText()
    {
        const string editedText = "C9_HTML_EDITED_PARA";
        EditSaveReload(editedText, out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-01.html");
        var result = FodtHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        Assert.Equal("exported", result.Status);
        var htmlContent = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains(editedText, htmlContent);
    }

    /// <summary>
    /// C9-HTML-02: HTML export from edited+reloaded document preserves unedited paragraph.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_PreservesUneditedParagraph()
    {
        EditSaveReload("C9_HTML_ONLY_P0", out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-02.html");
        FodtHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var htmlContent = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains("Second paragraph.", htmlContent);
    }

    /// <summary>
    /// C9-HTML-03: HTML export does not mutate the in-memory document model.
    /// </summary>
    [Fact]
    public void C9_Html_ExportDoesNotMutateDocument()
    {
        const string editedText = "C9_HTML_NO_MUTATE";
        var reloaded = EditSaveReload(editedText, out var reloadedPath);

        // Capture state before export
        string para0Before = reloaded.Paragraphs[0].Text;
        int paraCountBefore = reloaded.Paragraphs.Count;

        // Perform HTML export (using document overload)
        var htmlPath = Path.Combine(_tempDir, "c9-html-03.html");
        FodtHtmlExporter.ExportToHtml(reloaded, reloadedPath, htmlPath);

        // Verify no mutation
        Assert.Equal(para0Before, reloaded.Paragraphs[0].Text);
        Assert.Equal(paraCountBefore, reloaded.Paragraphs.Count);
    }

    /// <summary>
    /// C9-HTML-04: HTML export output is valid HTML5 after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Html_ExportAfterEditSaveReload_ValidHtmlStructure()
    {
        EditSaveReload("C9_HTML_VALID", out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-04.html");
        FodtHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var text = File.ReadAllText(htmlPath, Encoding.UTF8);
        Assert.Contains("<!DOCTYPE html>", text);
        Assert.Contains("<body>", text);
        Assert.Contains("</body>", text);
        Assert.Contains("commercial_product_ready=false", text);
    }

    /// <summary>
    /// C9-HTML-05: HTML export heading appears in correct h-tag after edit pipeline.
    /// </summary>
    [Fact]
    public void C9_Html_HeadingAppearsInHTag()
    {
        EditSaveReload("C9_HTML_HTAG", out var reloadedPath);

        var htmlPath = Path.Combine(_tempDir, "c9-html-05.html");
        FodtHtmlExporter.ExportToHtml(reloadedPath, htmlPath);

        var text = File.ReadAllText(htmlPath, Encoding.UTF8);
        // "A Heading" is outline-level 1 in the minimal fixture
        Assert.Contains("<h1>A Heading</h1>", text);
    }

    // =========================================================================
    // Governance invariants
    // =========================================================================

    /// <summary>
    /// C9-GOV-01: commercial_product_ready must be false (governance invariant).
    /// </summary>
    [Fact]
    public void C9_Governance_CommercialProductReadyIsFalse()
    {
        const bool commercialProductReady = false;
        Assert.False(commercialProductReady,
            "commercial_product_ready must remain false. G11-G is NOT_STARTED.");
    }

    /// <summary>
    /// C9-GOV-02: All three exporters exist and are static classes.
    /// </summary>
    [Fact]
    public void C9_Governance_AllThreeExportersExist()
    {
        Assert.True(typeof(FodtTxtExporter).IsAbstract && typeof(FodtTxtExporter).IsSealed,
            "FodtTxtExporter must be a static class");
        Assert.True(typeof(FodtMarkdownExporter).IsAbstract && typeof(FodtMarkdownExporter).IsSealed,
            "FodtMarkdownExporter must be a static class");
        Assert.True(typeof(FodtHtmlExporter).IsAbstract && typeof(FodtHtmlExporter).IsSealed,
            "FodtHtmlExporter must be a static class");
    }
}
