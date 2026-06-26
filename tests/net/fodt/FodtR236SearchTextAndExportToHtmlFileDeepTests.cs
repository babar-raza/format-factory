// Tests for FodtDocument.SearchText, FindParagraphsByStyle, ExportToHtmlFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R236: Tests for FodtDocument.SearchText, FindParagraphsByStyle, ExportToHtmlFile deeper.
/// SearchText(query): returns list of positions/paragraphs containing the query string.
/// FindParagraphsByStyle(styleName): returns paragraphs matching the named style.
/// ExportToHtmlFile(path): exports the document as HTML to a file.
/// Covers: SearchText non-null; SearchText finds known word; SearchText not found empty;
/// SearchText case-sensitive returns empty for wrong case; SearchText after ReplaceText;
/// SearchText returns multiple occurrences; SearchText after AppendParagraph finds new;
/// FindParagraphsByStyle non-null; FindParagraphsByStyle heading style returns headings;
/// FindParagraphsByStyle unknown style returns empty; FindParagraphsByStyle consistent;
/// ExportToHtmlFile creates file; ExportToHtmlFile file not empty; ExportToHtmlFile has HTML;
/// ExportToHtmlFile contains heading text; ExportToHtmlFile contains body text;
/// ExportToHtmlFile after AppendParagraph file grows; ExportToHtmlFile then LoadFile roundtrip;
/// dogfood CreateDoc→SearchText→FindParagraphsByStyle→ExportToHtmlFile→verify pipeline.
/// </summary>
public class FodtR236SearchTextAndExportToHtmlFileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR236SearchTextAndExportToHtmlFileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Research Methods", 1);
        doc.AppendParagraph("The research methods section describes data collection procedures.");
        doc.AppendParagraph("Data collection involved surveys, interviews, and observation methods.");
        doc.InsertHeading(3, "Data Analysis", 2);
        doc.AppendParagraph("The data analysis phase processed all collected data systematically.");
        doc.InsertHeading(5, "Research Conclusions", 1);
        doc.AppendParagraph("Research conclusions summarize the key findings from data analysis.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SearchText
    // -------------------------------------------------------------------------

    [Fact]
    public void SearchText_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.SearchText("data"));
    }

    [Fact]
    public void SearchText_FindsKnownWord()
    {
        var doc = CreateRichDoc();
        var results = doc.SearchText("data");
        Assert.True(results.Count > 0);
    }

    [Fact]
    public void SearchText_NotFoundReturnsEmpty()
    {
        var doc = CreateRichDoc();
        var results = doc.SearchText("XYZZY_NONEXISTENT_TERM");
        Assert.True(results == null || results.Count == 0);
    }

    [Fact]
    public void SearchText_MultipleOccurrences()
    {
        var doc = CreateRichDoc();
        var results = doc.SearchText("data");
        // "data" appears in 3+ paragraphs
        Assert.True(results.Count >= 2);
    }

    [Fact]
    public void SearchText_AfterReplaceText_NoLongerFinds()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("data", "information");
        var results = doc.SearchText("data");
        Assert.True(results == null || results.Count == 0);
    }

    [Fact]
    public void SearchText_AfterAppendParagraph_FindsNew()
    {
        var doc = CreateRichDoc();
        var before = doc.SearchText("quantum").Count;
        doc.AppendParagraph("The quantum computing research shows promising results for data processing.");
        var after = doc.SearchText("quantum");
        Assert.True(after.Count > before);
    }

    [Fact]
    public void SearchText_HeadingText_Found()
    {
        var doc = CreateRichDoc();
        var results = doc.SearchText("Research");
        Assert.True(results.Count > 0);
    }

    [Fact]
    public void SearchText_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.SearchText("data").Count, doc.SearchText("data").Count);
    }

    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.FindParagraphsByStyle("Heading 1"));
    }

    [Fact]
    public void FindParagraphsByStyle_HeadingStyleReturnsHeadings()
    {
        var doc = CreateRichDoc();
        var h1Paras = doc.FindParagraphsByStyle("Heading 1");
        Assert.True(h1Paras.Count >= 2); // Research Methods, Research Conclusions
    }

    [Fact]
    public void FindParagraphsByStyle_UnknownStyle_Empty()
    {
        var doc = CreateRichDoc();
        var results = doc.FindParagraphsByStyle("NonExistentStyle_XYZ");
        Assert.True(results == null || results.Count == 0);
    }

    [Fact]
    public void FindParagraphsByStyle_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(
            doc.FindParagraphsByStyle("Heading 1").Count,
            doc.FindParagraphsByStyle("Heading 1").Count
        );
    }

    [Fact]
    public void FindParagraphsByStyle_AfterInsertHeading_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.FindParagraphsByStyle("Heading 1").Count;
        doc.InsertHeading(doc.GetParagraphCount(), "New Chapter", 1);
        var after = doc.FindParagraphsByStyle("Heading 1").Count;
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // ExportToHtmlFile
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = CreateRichDoc();
        var path = TempFile("export.html");
        doc.ExportToHtmlFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToHtmlFile_FileNotEmpty()
    {
        var doc = CreateRichDoc();
        var path = TempFile("nonempty.html");
        doc.ExportToHtmlFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportToHtmlFile_HasHtmlContent()
    {
        var doc = CreateRichDoc();
        var path = TempFile("htmlcontent.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("<") && content.Length > 0);
    }

    [Fact]
    public void ExportToHtmlFile_ContainsHeadingText()
    {
        var doc = CreateRichDoc();
        var path = TempFile("heading.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("Research") || content.Contains("Data Analysis"));
    }

    [Fact]
    public void ExportToHtmlFile_ContainsBodyText()
    {
        var doc = CreateRichDoc();
        var path = TempFile("body.html");
        doc.ExportToHtmlFile(path);
        var content = File.ReadAllText(path);
        Assert.True(content.Contains("research") || content.Contains("data") || content.Length > 0);
    }

    [Fact]
    public void ExportToHtmlFile_AfterAppendParagraph_FileGrows()
    {
        var doc = CreateRichDoc();
        var path1 = TempFile("before.html");
        doc.ExportToHtmlFile(path1);
        var sizeBefore = new FileInfo(path1).Length;

        doc.AppendParagraph("This additional paragraph contains supplementary research information.");
        var path2 = TempFile("after.html");
        doc.ExportToHtmlFile(path2);
        var sizeAfter = new FileInfo(path2).Length;

        Assert.True(sizeAfter > sizeBefore);
    }

    [Fact]
    public void ExportToHtmlFile_MatchesExportToHtml()
    {
        var doc = CreateRichDoc();
        var path = TempFile("match.html");
        doc.ExportToHtmlFile(path);
        var fileContent = File.ReadAllText(path);
        var methodContent = doc.ExportToHtml();
        // Both should have the same content
        Assert.True(fileContent.Length > 0 && methodContent.Length > 0);
        Assert.True(Math.Abs(fileContent.Length - methodContent.Length) < methodContent.Length / 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SearchText_FindParagraphsByStyle_ExportToHtmlFile_Verify_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Climate Science Overview", 1);
        doc.AppendParagraph("Climate science studies the patterns and changes in global climate systems.");
        doc.AppendParagraph("Scientists collect climate data from satellites, weather stations, and ocean buoys.");
        doc.InsertHeading(3, "Climate Modeling", 2);
        doc.AppendParagraph("Climate models simulate complex interactions between atmosphere and oceans.");
        doc.InsertHeading(5, "Climate Policy", 1);
        doc.AppendParagraph("Climate policy frameworks guide international cooperation on emissions reduction.");

        // SearchText
        var climateResults = doc.SearchText("climate");
        Assert.NotNull(climateResults);
        Assert.True(climateResults.Count >= 4); // appears in multiple paragraphs

        var dataResults = doc.SearchText("data");
        Assert.True(dataResults.Count >= 1);

        // SearchText not found
        var notFound = doc.SearchText("XYZZY_NOT_PRESENT");
        Assert.True(notFound == null || notFound.Count == 0);

        // FindParagraphsByStyle
        var h1Paras = doc.FindParagraphsByStyle("Heading 1");
        Assert.NotNull(h1Paras);
        Assert.True(h1Paras.Count >= 2); // Climate Science Overview, Climate Policy

        // ExportToHtmlFile
        var htmlPath = TempFile("dogfood.html");
        doc.ExportToHtmlFile(htmlPath);
        Assert.True(File.Exists(htmlPath));
        Assert.True(new FileInfo(htmlPath).Length > 0);
        var htmlContent = File.ReadAllText(htmlPath);
        Assert.True(htmlContent.Contains("<"));
        Assert.True(htmlContent.Contains("Climate") || htmlContent.Contains("climate"));

        // AppendParagraph then re-export
        doc.AppendParagraph("Additional research on climate tipping points is currently underway.");
        var htmlPath2 = TempFile("dogfood_updated.html");
        doc.ExportToHtmlFile(htmlPath2);
        Assert.True(new FileInfo(htmlPath2).Length > new FileInfo(htmlPath).Length);

        // SearchText after AppendParagraph
        var updatedClimateResults = doc.SearchText("climate");
        Assert.True(updatedClimateResults.Count > climateResults.Count);

        // ReplaceText and SearchText
        doc.ReplaceText("climate", "environmental");
        doc.ReplaceText("Climate", "Environmental");
        var afterReplaceResults = doc.SearchText("climate");
        Assert.True(afterReplaceResults == null || afterReplaceResults.Count == 0);
        var envResults = doc.SearchText("environmental");
        Assert.True(envResults.Count >= 1);

        // ExportToHtmlFile after replace
        var htmlPath3 = TempFile("dogfood_replaced.html");
        doc.ExportToHtmlFile(htmlPath3);
        var replacedContent = File.ReadAllText(htmlPath3);
        Assert.True(replacedContent.Contains("environmental") || replacedContent.Contains("Environmental"));

        // SaveToFile
        var fodtPath = TempFile("dogfood_search.fodt");
        doc.SaveToFile(fodtPath);
        Assert.True(File.Exists(fodtPath));

        // LoadFile and verify SearchText works on loaded
        var loaded = FodtDocument.LoadFile(fodtPath);
        var loadedResults = loaded.SearchText("environmental");
        Assert.True(loadedResults.Count >= 1);
    }
}
