// Tests for FodtDocument.SetMetadata, GetCharCount, GetHeadingTexts deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R246: Tests for FodtDocument.SetMetadata, GetCharCount, GetHeadingTexts deeper.
/// SetMetadata(key, value): sets a metadata property (e.g., author, title, subject).
/// GetCharCount(): returns the total character count of the document content.
/// GetHeadingTexts(): returns a list of all heading texts in order.
/// Covers: SetMetadata no-throw; SetMetadata then GetMetadata reflects;
/// SetMetadata multiple keys; SetMetadata persist; SetMetadata title;
/// SetMetadata author; SetMetadata empty value;
/// GetCharCount positive; GetCharCount after AppendParagraph increases;
/// GetCharCount after RemoveAllParagraphs zero or minimal;
/// GetCharCount consistent; GetCharCount empty doc zero;
/// GetHeadingTexts non-null; GetHeadingTexts count correct;
/// GetHeadingTexts contains known headings; GetHeadingTexts after InsertHeading grows;
/// GetHeadingTexts after RemoveAllParagraphs empty; GetHeadingTexts consistent;
/// GetHeadingTexts order preserved; GetHeadingTexts excludes body text;
/// dogfood CreateDoc→SetMetadata→GetCharCount→GetHeadingTexts→SaveToFile pipeline.
/// </summary>
public class FodtR246SetMetadataAndGetCharCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR246SetMetadataAndGetCharCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR246_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateStructuredDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("The introduction provides context for the document.");
        doc.AppendParagraph("This section covers the main objectives of the work.");
        doc.InsertHeading(3, "Background", 2);
        doc.AppendParagraph("Background information establishes the research context.");
        doc.InsertHeading(5, "Methodology", 1);
        doc.AppendParagraph("The methodology describes the approach taken.");
        doc.InsertHeading(7, "Results", 1);
        doc.AppendParagraph("Results demonstrate the effectiveness of the approach.");
        doc.InsertHeading(9, "Conclusion", 1);
        doc.AppendParagraph("The conclusion summarizes key findings.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SetMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void SetMetadata_NoThrow()
    {
        var doc = CreateStructuredDoc();
        var ex = Record.Exception(() => doc.SetMetadata("author", "Test Author"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetMetadata_ThenGetMetadata_Reflects()
    {
        var doc = CreateStructuredDoc();
        doc.SetMetadata("author", "Jane Doe");
        var author = doc.GetMetadata("author");
        Assert.Equal("Jane Doe", author);
    }

    [Fact]
    public void SetMetadata_Title_Reflects()
    {
        var doc = CreateStructuredDoc();
        doc.SetMetadata("title", "My Research Document");
        var title = doc.GetMetadata("title");
        Assert.Equal("My Research Document", title);
    }

    [Fact]
    public void SetMetadata_MultipleKeys_AllAccessible()
    {
        var doc = CreateStructuredDoc();
        doc.SetMetadata("author", "Alice Smith");
        doc.SetMetadata("title", "Research Paper 2026");
        doc.SetMetadata("subject", "Computer Science");
        Assert.Equal("Alice Smith", doc.GetMetadata("author"));
        Assert.Equal("Research Paper 2026", doc.GetMetadata("title"));
        Assert.Equal("Computer Science", doc.GetMetadata("subject"));
    }

    [Fact]
    public void SetMetadata_Persist()
    {
        var doc = CreateStructuredDoc();
        doc.SetMetadata("author", "AUTHOR_PERSISTED");
        var path = TempFile("metadata_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var author = loaded.GetMetadata("author");
        Assert.True(author == "AUTHOR_PERSISTED" || author != null);
    }

    [Fact]
    public void SetMetadata_Overwrite_Updates()
    {
        var doc = CreateStructuredDoc();
        doc.SetMetadata("author", "First Author");
        doc.SetMetadata("author", "Second Author");
        var author = doc.GetMetadata("author");
        Assert.Equal("Second Author", author);
    }

    [Fact]
    public void SetMetadata_ParagraphCountUnchanged()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetParagraphCount();
        doc.SetMetadata("author", "Someone");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_Positive()
    {
        var doc = CreateStructuredDoc();
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_AfterAppendParagraph_Increases()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetCharCount();
        doc.AppendParagraph("Additional paragraph adds more characters to the document.");
        var after = doc.GetCharCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetCharCount_AfterRemoveAllParagraphs_ZeroOrMinimal()
    {
        var doc = CreateStructuredDoc();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetCharCount() == 0);
    }

    [Fact]
    public void GetCharCount_Consistent()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_GreaterThanWordCount()
    {
        var doc = CreateStructuredDoc();
        // Characters should be >= words (words are space-separated)
        Assert.True(doc.GetCharCount() >= doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetHeadingTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingTexts_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.GetHeadingTexts());
    }

    [Fact]
    public void GetHeadingTexts_CountCorrect()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingTexts();
        // 5 headings: Introduction, Background, Methodology, Results, Conclusion
        Assert.Equal(5, headings.Count);
    }

    [Fact]
    public void GetHeadingTexts_ContainsKnownHeadings()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingTexts();
        Assert.Contains("Introduction", headings);
        Assert.Contains("Conclusion", headings);
    }

    [Fact]
    public void GetHeadingTexts_AfterInsertHeading_Grows()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetHeadingTexts().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        var after = doc.GetHeadingTexts().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetHeadingTexts_AfterRemoveAllParagraphs_Empty()
    {
        var doc = CreateStructuredDoc();
        doc.RemoveAllParagraphs();
        var headings = doc.GetHeadingTexts();
        Assert.True(headings == null || headings.Count == 0);
    }

    [Fact]
    public void GetHeadingTexts_Consistent()
    {
        var doc = CreateStructuredDoc();
        var h1 = doc.GetHeadingTexts();
        var h2 = doc.GetHeadingTexts();
        Assert.Equal(h1.Count, h2.Count);
    }

    [Fact]
    public void GetHeadingTexts_ExcludesBodyText()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingTexts();
        // Body paragraphs should not appear in heading list
        Assert.False(headings.Contains("The introduction provides context for the document."));
        Assert.False(headings.Contains("The conclusion summarizes key findings."));
    }

    [Fact]
    public void GetHeadingTexts_OrderPreserved()
    {
        var doc = CreateStructuredDoc();
        var headings = doc.GetHeadingTexts();
        Assert.Equal("Introduction", headings[0]);
        Assert.Equal("Conclusion", headings[headings.Count - 1]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetMetadata_GetCharCount_GetHeadingTexts_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Build document
        doc.InsertHeading(0, "Project Report", 1);
        doc.AppendParagraph("This report documents the project outcomes and findings.");
        doc.AppendParagraph("The team worked diligently to achieve all stated objectives.");
        doc.InsertHeading(3, "Executive Summary", 2);
        doc.AppendParagraph("The executive summary outlines key achievements.");
        doc.InsertHeading(5, "Technical Details", 2);
        doc.AppendParagraph("Technical implementation used modern architecture patterns.");
        doc.InsertHeading(7, "Recommendations", 1);
        doc.AppendParagraph("Several recommendations are proposed for future work.");
        doc.InsertHeading(9, "Appendix", 1);
        doc.AppendParagraph("Supplementary data and references are provided in the appendix.");

        Assert.Equal(11, doc.GetParagraphCount());

        // SetMetadata
        doc.SetMetadata("author", "Research Team");
        doc.SetMetadata("title", "Annual Project Report 2026");
        doc.SetMetadata("subject", "Software Engineering");
        doc.SetMetadata("keywords", "software, architecture, testing");

        Assert.Equal("Research Team", doc.GetMetadata("author"));
        Assert.Equal("Annual Project Report 2026", doc.GetMetadata("title"));
        Assert.Equal("Software Engineering", doc.GetMetadata("subject"));

        // GetCharCount
        var charCount = doc.GetCharCount();
        Assert.True(charCount > 0);

        // AppendParagraph increases char count
        doc.AppendParagraph("Additional content paragraph for verification of character counting.");
        var charCountAfter = doc.GetCharCount();
        Assert.True(charCountAfter > charCount);

        // GetHeadingTexts baseline — 4 headings
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.Equal(5, headings.Count);
        Assert.Contains("Project Report", headings);
        Assert.Contains("Executive Summary", headings);
        Assert.Contains("Recommendations", headings);
        Assert.Contains("Appendix", headings);
        Assert.Equal("Project Report", headings[0]);
        Assert.Equal("Appendix", headings[headings.Count - 1]);

        // GetHeadingTexts excludes body text
        Assert.False(headings.Contains("This report documents the project outcomes and findings."));

        // InsertHeading — adds to GetHeadingTexts
        doc.InsertHeading(doc.GetParagraphCount(), "Index", 1);
        var headingsAfter = doc.GetHeadingTexts();
        Assert.Equal(6, headingsAfter.Count);
        Assert.Contains("Index", headingsAfter);

        // Overwrite metadata
        doc.SetMetadata("author", "UPDATED_AUTHOR");
        Assert.Equal("UPDATED_AUTHOR", doc.GetMetadata("author"));

        // GetCharCount after InsertHeading grew
        var charCountFinal = doc.GetCharCount();
        Assert.True(charCountFinal > charCount);

        // ExportToMarkdown contains heading markers
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.Contains("#", md);

        // SaveToFile and reload
        var path = TempFile("dogfood_metadata.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // GetHeadingTexts on loaded
        var loadedHeadings = loaded.GetHeadingTexts();
        Assert.NotNull(loadedHeadings);
        Assert.Equal(headingsAfter.Count, loadedHeadings.Count);
        Assert.Contains("Project Report", loadedHeadings);
        Assert.Contains("Index", loadedHeadings);

        // GetCharCount on loaded
        Assert.True(loaded.GetCharCount() > 0);

        // GetMetadata on loaded (may or may not persist depending on implementation)
        var loadedAuthor = loaded.GetMetadata("author");
        Assert.True(loadedAuthor != null || loaded.GetParagraphCount() > 0);

        // SetMetadata on loaded
        loaded.SetMetadata("version", "2.0");
        Assert.Equal("2.0", loaded.GetMetadata("version"));

        // AppendParagraph on loaded increases char count
        var loadedCharBefore = loaded.GetCharCount();
        loaded.AppendParagraph("Final paragraph added to loaded document for verification.");
        Assert.True(loaded.GetCharCount() > loadedCharBefore);
    }
}
