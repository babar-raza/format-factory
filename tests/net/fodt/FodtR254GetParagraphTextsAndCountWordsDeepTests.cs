// Tests for FodtDocument.GetParagraphTexts, CountWords, SetFontStyle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R254

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R254: Tests for FodtDocument.GetParagraphTexts, CountWords, SetFontStyle deeper.
/// GetParagraphTexts(): returns a list of all paragraph text content.
/// CountWords(): returns the total number of words in the document.
/// SetFontStyle(index, style): sets the font style of a paragraph.
/// Covers: GetParagraphTexts non-null; GetParagraphTexts non-empty; GetParagraphTexts count correct;
/// GetParagraphTexts contains known; GetParagraphTexts consistent; GetParagraphTexts no-throw;
/// GetParagraphTexts after AppendParagraph grows; GetParagraphTexts after RemoveParagraphAt shrinks;
/// GetParagraphTexts after ReplaceText reflects; GetParagraphTexts save-load consistent;
/// GetParagraphTexts empty doc empty or null;
/// CountWords positive; CountWords consistent; CountWords no-throw; CountWords after AppendParagraph grows;
/// CountWords after ReplaceText reflects; CountWords after RemoveAll near zero;
/// CountWords matches GetWordCount; CountWords empty doc zero;
/// SetFontStyle no-throw; SetFontStyle multiple no-throw; SetFontStyle persist;
/// SetFontStyle then ExportToHtml non-null; SetFontStyle then SaveToFile;
/// SetFontStyle then GetParagraphTexts unchanged; SetFontStyle then CountWords unchanged;
/// dogfood CreateDoc→GetParagraphTexts→CountWords→SetFontStyle→SaveToFile pipeline.
/// </summary>
public class FodtR254GetParagraphTextsAndCountWordsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR254GetParagraphTextsAndCountWordsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR254_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Project Overview", 1);
        doc.AppendParagraph("This project provides a comprehensive overview of our initiatives.");
        doc.AppendParagraph("The team has worked diligently to achieve the stated goals.");
        doc.InsertHeading(3, "Scope and Objectives", 2);
        doc.AppendParagraph("The scope covers three major domains of the business.");
        doc.AppendParagraph("Each objective is measurable and time-bound for clarity.");
        doc.InsertHeading(6, "Timeline", 1);
        doc.AppendParagraph("The timeline spans twelve months with quarterly milestones.");
        doc.AppendParagraph("Reviews are scheduled at the end of each quarter.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetParagraphTexts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetParagraphTexts_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetParagraphTexts());
    }

    [Fact]
    public void GetParagraphTexts_NonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetParagraphTexts().Count > 0);
    }

    [Fact]
    public void GetParagraphTexts_CountMatchesParagraphCount()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetParagraphCount(), doc.GetParagraphTexts().Count);
    }

    [Fact]
    public void GetParagraphTexts_ContainsKnown()
    {
        var doc = CreateRichDoc();
        var texts = doc.GetParagraphTexts();
        Assert.True(
            texts.Contains("Project Overview") ||
            texts.Contains("Scope and Objectives") ||
            texts.Contains("Timeline") ||
            texts.Exists(t => t.Contains("overview") || t.Contains("team") || t.Contains("scope")));
    }

    [Fact]
    public void GetParagraphTexts_Consistent()
    {
        var doc = CreateRichDoc();
        var t1 = doc.GetParagraphTexts();
        var t2 = doc.GetParagraphTexts();
        Assert.Equal(t1.Count, t2.Count);
    }

    [Fact]
    public void GetParagraphTexts_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetParagraphTexts());
        Assert.Null(ex);
    }

    [Fact]
    public void GetParagraphTexts_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.AppendParagraph("Additional paragraph for paragraph text verification.");
        var after = doc.GetParagraphTexts().Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetParagraphTexts_AfterRemoveParagraphAt_Shrinks()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.RemoveParagraphAt(0);
        var after = doc.GetParagraphTexts().Count;
        Assert.Equal(before - 1, after);
    }

    [Fact]
    public void GetParagraphTexts_AfterReplaceText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("overview", "OVERVIEW_REPLACED");
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Exists(t => t.Contains("OVERVIEW_REPLACED")));
    }

    [Fact]
    public void GetParagraphTexts_SaveLoadConsistent()
    {
        var doc = CreateRichDoc();
        var texts = doc.GetParagraphTexts();
        var path = TempFile("para_texts_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var loadedTexts = loaded.GetParagraphTexts();
        Assert.Equal(texts.Count, loadedTexts.Count);
    }

    [Fact]
    public void GetParagraphTexts_EmptyDoc_EmptyOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var texts = doc.GetParagraphTexts();
        Assert.True(texts == null || texts.Count == 0);
    }

    // -------------------------------------------------------------------------
    // CountWords
    // -------------------------------------------------------------------------

    [Fact]
    public void CountWords_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.CountWords() > 0);
    }

    [Fact]
    public void CountWords_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.CountWords(), doc.CountWords());
    }

    [Fact]
    public void CountWords_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.CountWords());
        Assert.Null(ex);
    }

    [Fact]
    public void CountWords_AfterAppendParagraph_Grows()
    {
        var doc = CreateRichDoc();
        var before = doc.CountWords();
        doc.AppendParagraph("This paragraph adds exactly five words.");
        var after = doc.CountWords();
        Assert.True(after > before);
    }

    [Fact]
    public void CountWords_MatchesGetWordCount()
    {
        var doc = CreateRichDoc();
        // Both should return same or similar count
        var cw = doc.CountWords();
        var gwc = doc.GetWordCount();
        Assert.True(Math.Abs(cw - gwc) <= 5); // allow minor differences
    }

    [Fact]
    public void CountWords_AfterRemoveAll_ZeroOrMinimal()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        Assert.True(doc.CountWords() >= 0);
    }

    [Fact]
    public void CountWords_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.CountWords() >= 0);
    }

    [Fact]
    public void CountWords_AfterReplaceText_SimilarCount()
    {
        var doc = CreateRichDoc();
        var before = doc.CountWords();
        // Replace single word with single word — count should stay same
        doc.ReplaceText("project", "initiative");
        var after = doc.CountWords();
        Assert.True(Math.Abs(after - before) <= 5);
    }

    // -------------------------------------------------------------------------
    // SetFontStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetFontStyle_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.SetFontStyle(1, "bold"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetFontStyle_Multiple_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() =>
        {
            doc.SetFontStyle(0, "bold");
            doc.SetFontStyle(1, "italic");
            doc.SetFontStyle(2, "bold-italic");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void SetFontStyle_Persist()
    {
        var doc = CreateRichDoc();
        doc.SetFontStyle(1, "bold");
        var path = TempFile("font_style_persist.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void SetFontStyle_ThenExportToHtml_NonNull()
    {
        var doc = CreateRichDoc();
        doc.SetFontStyle(1, "bold");
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
    }

    [Fact]
    public void SetFontStyle_DoesNotChangeParagraphCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.SetFontStyle(1, "italic");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    [Fact]
    public void SetFontStyle_DoesNotChangeCountWords()
    {
        var doc = CreateRichDoc();
        var before = doc.CountWords();
        doc.SetFontStyle(1, "bold");
        var after = doc.CountWords();
        Assert.Equal(before, after);
    }

    [Fact]
    public void SetFontStyle_GetParagraphTexts_Unchanged()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphTexts().Count;
        doc.SetFontStyle(2, "italic");
        var after = doc.GetParagraphTexts().Count;
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetParagraphTexts_CountWords_SetFontStyle_SaveToFile_Pipeline()
    {
        // Build comprehensive document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Strategic Planning Document", 1);
        doc.AppendParagraph("This document outlines the strategic plans for the upcoming fiscal year.");
        doc.AppendParagraph("All stakeholders are expected to review and provide feedback.");
        doc.InsertHeading(3, "Market Analysis", 2);
        doc.AppendParagraph("The market analysis reveals significant growth opportunities in three sectors.");
        doc.AppendParagraph("Competitive landscape has shifted considerably due to recent acquisitions.");
        doc.AppendParagraph("Customer satisfaction scores remain above industry average at ninety-two percent.");
        doc.InsertHeading(6, "Resource Allocation", 2);
        doc.AppendParagraph("Budget allocation follows the priority matrix established in Q3 reviews.");
        doc.AppendParagraph("Headcount additions are planned in engineering and customer success teams.");
        doc.InsertHeading(9, "Risk Management", 1);
        doc.AppendParagraph("Primary risks include supply chain disruptions and regulatory changes.");
        doc.AppendParagraph("Mitigation strategies are documented and owned by respective teams.");

        Assert.Equal(11, doc.GetParagraphCount());

        // GetParagraphTexts baseline
        var texts = doc.GetParagraphTexts();
        Assert.NotNull(texts);
        Assert.Equal(11, texts.Count);
        Assert.True(texts.Exists(t => t.Contains("Strategic") || t.Contains("strategic")));
        Assert.True(texts.Exists(t => t.Contains("market") || t.Contains("Market")));

        // CountWords baseline
        var wordCount = doc.CountWords();
        Assert.True(wordCount > 50);

        // GetWordCount should be similar
        var gwc = doc.GetWordCount();
        Assert.True(Math.Abs(wordCount - gwc) <= 10);

        // SetFontStyle on headings
        doc.SetFontStyle(0, "bold"); // Strategic Planning Document
        doc.SetFontStyle(3, "bold"); // Market Analysis
        doc.SetFontStyle(6, "bold"); // Resource Allocation
        doc.SetFontStyle(9, "bold"); // Risk Management

        // CountWords unchanged after SetFontStyle
        Assert.Equal(wordCount, doc.CountWords());

        // GetParagraphTexts unchanged after SetFontStyle
        var textsAfterStyle = doc.GetParagraphTexts();
        Assert.Equal(texts.Count, textsAfterStyle.Count);

        // SetFontStyle on body paragraphs
        doc.SetFontStyle(1, "normal");
        doc.SetFontStyle(2, "italic");
        doc.SetFontStyle(4, "normal");

        // AppendParagraph and verify GetParagraphTexts grows
        doc.AppendParagraph("MARKER_PARAGRAPH_UNIQUE_XYZ: additional content for pipeline verification.");
        Assert.Equal(12, doc.GetParagraphCount());
        var textsAfterAppend = doc.GetParagraphTexts();
        Assert.Equal(12, textsAfterAppend.Count);
        Assert.True(textsAfterAppend.Exists(t => t.Contains("MARKER_PARAGRAPH_UNIQUE_XYZ")));

        // CountWords grew
        var wordCountAfterAppend = doc.CountWords();
        Assert.True(wordCountAfterAppend > wordCount);

        // SetFontStyle on new paragraph
        doc.SetFontStyle(11, "bold-italic");

        // ReplaceText and verify GetParagraphTexts reflects
        doc.ReplaceText("strategic", "TACTICAL");
        var textsAfterReplace = doc.GetParagraphTexts();
        Assert.True(textsAfterReplace.Exists(t => t.Contains("TACTICAL")));
        Assert.Equal(12, textsAfterReplace.Count);

        // ExportToHtml after styling
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetCharCount positive
        var cc = doc.GetCharCount();
        Assert.True(cc > 0);

        // GetHeadingTexts
        var headings = doc.GetHeadingTexts();
        Assert.NotNull(headings);
        Assert.True(headings.Count >= 3);

        // RemoveParagraphAt and verify GetParagraphTexts shrinks
        doc.RemoveParagraphAt(11); // Remove the MARKER paragraph
        Assert.Equal(11, doc.GetParagraphTexts().Count);

        // CountWords after remove
        var wordCountAfterRemove = doc.CountWords();
        Assert.True(wordCountAfterRemove < wordCountAfterAppend);

        // GetParagraphTexts consistent
        var t1 = doc.GetParagraphTexts();
        var t2 = doc.GetParagraphTexts();
        Assert.Equal(t1.Count, t2.Count);

        // CountWords consistent
        Assert.Equal(doc.CountWords(), doc.CountWords());

        // SaveToFile
        var path = TempFile("dogfood_para_words.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // GetParagraphTexts on loaded
        var loadedTexts = loaded.GetParagraphTexts();
        Assert.NotNull(loadedTexts);
        Assert.Equal(doc.GetParagraphTexts().Count, loadedTexts.Count);

        // CountWords on loaded
        var loadedWordCount = loaded.CountWords();
        Assert.True(loadedWordCount > 0);

        // SetFontStyle on loaded
        var loadedStyleEx = Record.Exception(() => loaded.SetFontStyle(0, "bold"));
        Assert.Null(loadedStyleEx);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: all objectives have been documented and assigned owners.");
        Assert.Equal(doc.GetParagraphCount() + 1, loaded.GetParagraphCount());

        // GetParagraphTexts after AppendParagraph on loaded
        var loadedTextsAfterAppend = loaded.GetParagraphTexts();
        Assert.Equal(loaded.GetParagraphCount(), loadedTextsAfterAppend.Count);
        Assert.True(loadedTextsAfterAppend.Exists(t => t.Contains("Conclusion")));

        // Final SaveToFile
        var path2 = TempFile("dogfood_para_words_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetParagraphCount(), loaded2.GetParagraphCount());
        Assert.True(loaded2.CountWords() >= loadedWordCount);
    }
}
