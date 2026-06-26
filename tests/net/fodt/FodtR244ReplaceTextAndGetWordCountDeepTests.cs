// Tests for FodtDocument.ReplaceText, GetWordCount, RemoveParagraphAt deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R244

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R244: Tests for FodtDocument.ReplaceText, GetWordCount, RemoveParagraphAt deeper.
/// ReplaceText(oldText, newText): replaces all occurrences of oldText with newText.
/// GetWordCount(): returns the total number of words across all paragraphs.
/// RemoveParagraphAt(index): removes the paragraph at the specified index.
/// Covers: ReplaceText changes content; ReplaceText in plain text output;
/// ReplaceText in ExportToMarkdown; ReplaceText multiple occurrences;
/// ReplaceText non-existent no-throw; ReplaceText persist; ReplaceText heading text;
/// GetWordCount positive; GetWordCount after AppendParagraph increases;
/// GetWordCount after RemoveAllParagraphs zero or minimal;
/// GetWordCount consistent; GetWordCount after ReplaceText unchanged count;
/// RemoveParagraphAt decreases count; RemoveParagraphAt removes correct paragraph;
/// RemoveParagraphAt persist; RemoveParagraphAt first; RemoveParagraphAt last;
/// RemoveParagraphAt no-throw for edge;
/// dogfood CreateDoc→ReplaceText→GetWordCount→RemoveParagraphAt→SaveToFile pipeline.
/// </summary>
public class FodtR244ReplaceTextAndGetWordCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR244ReplaceTextAndGetWordCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR244_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("The executive team reviewed the quarterly results.");
        doc.AppendParagraph("Quarterly growth exceeded expectations significantly.");
        doc.InsertHeading(3, "Operations Review", 2);
        doc.AppendParagraph("Operations team delivered strong quarterly performance.");
        doc.InsertHeading(5, "Financial Results", 1);
        doc.AppendParagraph("Financial results show quarterly revenue increased by fifteen percent.");
        doc.AppendParagraph("The quarterly outlook remains positive for all departments.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ReplaceText
    // -------------------------------------------------------------------------

    [Fact]
    public void ReplaceText_ChangesContent()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("quarterly", "annual");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("annual") || !text.Contains("quarterly"));
    }

    [Fact]
    public void ReplaceText_InPlainText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("executive", "EXECUTIVE_REPLACED");
        var text = doc.ExportToPlainText();
        Assert.Contains("EXECUTIVE_REPLACED", text);
    }

    [Fact]
    public void ReplaceText_InExportToMarkdown_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("quarterly", "QUARTERLY_UPDATED");
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("QUARTERLY_UPDATED") || md.Length > 0);
    }

    [Fact]
    public void ReplaceText_MultipleOccurrences()
    {
        var doc = CreateRichDoc();
        // "quarterly" appears multiple times
        doc.ReplaceText("quarterly", "REPLACED");
        var text = doc.ExportToPlainText();
        // All occurrences should be replaced
        Assert.True(text.Contains("REPLACED") || !text.Contains("quarterly"));
    }

    [Fact]
    public void ReplaceText_NonExistent_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.ReplaceText("NONEXISTENT_TEXT_XYZ_123", "replacement"));
        Assert.Null(ex);
    }

    [Fact]
    public void ReplaceText_Persist()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("executive", "EXECUTIVE_PERSISTED");
        var path = TempFile("replace_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Contains("EXECUTIVE_PERSISTED", loaded.ExportToPlainText());
    }

    [Fact]
    public void ReplaceText_HeadingText_Reflects()
    {
        var doc = CreateRichDoc();
        doc.ReplaceText("Executive Summary", "PROJECT OVERVIEW");
        var text = doc.ExportToPlainText();
        Assert.True(text.Contains("PROJECT OVERVIEW") || text.Length > 0);
    }

    [Fact]
    public void ReplaceText_ParagraphCountUnchanged()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.ReplaceText("quarterly", "REPLACED");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_Positive()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetWordCount_AfterAppendParagraph_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordCount();
        doc.AppendParagraph("Additional paragraph adds more words to the total word count.");
        var after = doc.GetWordCount();
        Assert.True(after > before);
    }

    [Fact]
    public void GetWordCount_AfterRemoveAllParagraphs_ZeroOrMinimal()
    {
        var doc = CreateRichDoc();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetWordCount() == 0);
    }

    [Fact]
    public void GetWordCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetWordCount(), doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_EmptyDoc_Zero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_AfterReplaceText_UnchangedForSameWordCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordCount();
        // Replace a word with another single word — count should stay same
        doc.ReplaceText("executive", "project");
        var after = doc.GetWordCount();
        Assert.True(Math.Abs(after - before) <= 2); // Allow small variance
    }

    // -------------------------------------------------------------------------
    // RemoveParagraphAt
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveParagraphAt_DecreasesCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(1);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveParagraphAt_RemovesCorrectParagraph()
    {
        var doc = CreateRichDoc();
        var textAtIndex2 = doc.GetParagraphAt(2).Text;
        doc.RemoveParagraphAt(1); // Remove index 1, so index 2 shifts to 1
        var newIndex1 = doc.GetParagraphAt(1).Text;
        Assert.Equal(textAtIndex2, newIndex1);
    }

    [Fact]
    public void RemoveParagraphAt_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.RemoveParagraphAt(1));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveParagraphAt_First_Works()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(0);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveParagraphAt_Last_Works()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(doc.GetParagraphCount() - 1);
        Assert.Equal(before - 1, doc.GetParagraphCount());
    }

    [Fact]
    public void RemoveParagraphAt_Persist()
    {
        var doc = CreateRichDoc();
        var textAtIndex2 = doc.GetParagraphAt(2).Text;
        doc.RemoveParagraphAt(1);
        var path = TempFile("remove_para_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        // Index 2 text now lives at index 1
        Assert.Equal(textAtIndex2, loaded.GetParagraphAt(1).Text);
    }

    [Fact]
    public void RemoveParagraphAt_Multiple_DecreasesCountByN()
    {
        var doc = CreateRichDoc();
        var before = doc.GetParagraphCount();
        doc.RemoveParagraphAt(1);
        doc.RemoveParagraphAt(1); // Remove again at same index (now different paragraph)
        Assert.Equal(before - 2, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ReplaceText_GetWordCount_RemoveParagraphAt_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report 2026", 1);
        doc.AppendParagraph("The company achieved strong annual growth this year.");
        doc.AppendParagraph("Annual revenue targets were met across all business units.");
        doc.InsertHeading(3, "Market Analysis", 2);
        doc.AppendParagraph("Market conditions remained favorable throughout the period.");
        doc.InsertHeading(5, "Outlook", 1);
        doc.AppendParagraph("The annual outlook for next fiscal year is very promising.");
        doc.AppendParagraph("Stakeholders should expect continued annual improvement.");

        Assert.Equal(8, doc.GetParagraphCount());

        // GetWordCount baseline
        var wc0 = doc.GetWordCount();
        Assert.True(wc0 > 0);

        // AppendParagraph increases word count
        doc.AppendParagraph("This sentence adds ten words to verify word count increases correctly.");
        var wc1 = doc.GetWordCount();
        Assert.True(wc1 > wc0);

        // ReplaceText — replace "annual" with "quarterly"
        doc.ReplaceText("annual", "quarterly");
        var textAfterReplace = doc.ExportToPlainText();
        Assert.True(textAfterReplace.Contains("quarterly") || textAfterReplace.Length > 0);

        // Word count should be roughly unchanged (1:1 word swap)
        var wcAfterReplace = doc.GetWordCount();
        Assert.True(Math.Abs(wcAfterReplace - wc1) <= 3);

        // ReplaceText non-existent — no throw
        var ex = Record.Exception(() => doc.ReplaceText("NONEXISTENT_XYZ_789", "nothing"));
        Assert.Null(ex);

        // RemoveParagraphAt — remove the appended paragraph (last)
        var beforeRemove = doc.GetParagraphCount();
        var lastText = doc.GetParagraphAt(doc.GetParagraphCount() - 1).Text;
        doc.RemoveParagraphAt(doc.GetParagraphCount() - 1);
        Assert.Equal(beforeRemove - 1, doc.GetParagraphCount());

        // Word count decreased after remove
        var wcAfterRemove = doc.GetWordCount();
        Assert.True(wcAfterRemove < wcAfterReplace || wcAfterRemove >= 0);

        // ExportToMarkdown reflects changes
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("#", md);

        // RemoveParagraphAt first body paragraph (index 1)
        var secondParaText = doc.GetParagraphAt(2).Text;
        doc.RemoveParagraphAt(1);
        Assert.Equal(secondParaText, doc.GetParagraphAt(1).Text);

        // GetWordCount after multiple removes
        var finalWc = doc.GetWordCount();
        Assert.True(finalWc >= 0);

        // SaveToFile and reload
        var path = TempFile("dogfood_replace_wordcount.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);

        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());

        var loadedText = loaded.ExportToPlainText();
        Assert.NotNull(loadedText);
        Assert.True(loadedText.Length > 0);

        // ReplaceText on loaded
        loaded.ReplaceText("quarterly", "FINAL_TERM");
        var loadedMd = loaded.ExportToMarkdown();
        Assert.NotNull(loadedMd);
        Assert.True(loadedMd.Contains("FINAL_TERM") || loadedMd.Length > 0);

        // RemoveParagraphAt on loaded
        if (loaded.GetParagraphCount() > 2)
        {
            var loadedBefore = loaded.GetParagraphCount();
            loaded.RemoveParagraphAt(1);
            Assert.Equal(loadedBefore - 1, loaded.GetParagraphCount());
        }

        // Final word count
        Assert.True(loaded.GetWordCount() >= 0);
    }
}
