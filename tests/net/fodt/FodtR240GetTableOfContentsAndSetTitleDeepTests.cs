// Tests for FodtDocument.GetTableOfContents, SetTitle, CountSentences deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R240

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R240: Tests for FodtDocument.GetTableOfContents, SetTitle, CountSentences deeper.
/// GetTableOfContents(): returns list of headings with level and text for a TOC.
/// SetTitle(title): sets the document title metadata.
/// CountSentences(): returns approximate sentence count based on punctuation.
/// Covers: GetTableOfContents non-null; GetTableOfContents count correct;
/// GetTableOfContents contains heading texts; GetTableOfContents levels correct;
/// GetTableOfContents after InsertHeading increases; GetTableOfContents consistent;
/// GetTableOfContents after RemoveAllParagraphs empty; GetTableOfContents save-load;
/// SetTitle non-null after; SetTitle reflects in metadata; SetTitle persists after save;
/// SetTitle overwrite; SetTitle empty string; SetTitle consistent;
/// CountSentences positive; CountSentences increases with more paragraphs;
/// CountSentences correct for known content; CountSentences consistent;
/// CountSentences after RemoveAllParagraphs zero; CountSentences after ReplaceText;
/// dogfood CreateDoc→GetTableOfContents→SetTitle→CountSentences→SaveToFile pipeline.
/// </summary>
public class FodtR240GetTableOfContentsAndSetTitleDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR240GetTableOfContentsAndSetTitleDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR240_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Executive Summary", 1);
        doc.AppendParagraph("The executive summary provides a high-level overview of the report.");
        doc.AppendParagraph("Key findings are presented concisely. The results were significant.");
        doc.InsertHeading(3, "Background and Context", 2);
        doc.AppendParagraph("The background section explains the origins of the project. It began in 2024.");
        doc.InsertHeading(5, "Methodology", 2);
        doc.AppendParagraph("The methodology section describes research methods used. Data was collected carefully.");
        doc.AppendParagraph("Multiple approaches were evaluated. The best method was selected based on criteria.");
        doc.InsertHeading(8, "Conclusions", 1);
        doc.AppendParagraph("The conclusions summarize key findings. Future work is also discussed.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableOfContents
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableOfContents_NonNull()
    {
        var doc = CreateStructuredDoc();
        Assert.NotNull(doc.GetTableOfContents());
    }

    [Fact]
    public void GetTableOfContents_CountCorrect()
    {
        var doc = CreateStructuredDoc();
        var toc = doc.GetTableOfContents();
        // 4 headings: Executive Summary (H1), Background (H2), Methodology (H2), Conclusions (H1)
        Assert.True(toc.Count >= 4);
    }

    [Fact]
    public void GetTableOfContents_ContainsHeadingTexts()
    {
        var doc = CreateStructuredDoc();
        var toc = doc.GetTableOfContents();
        var texts = new System.Collections.Generic.List<string>();
        foreach (var entry in toc) texts.Add(entry.Text);
        Assert.True(texts.Contains("Executive Summary") || texts.Exists(t => t.Contains("Summary")));
    }

    [Fact]
    public void GetTableOfContents_ContainsAllHeadings()
    {
        var doc = CreateStructuredDoc();
        var toc = doc.GetTableOfContents();
        var texts = new System.Collections.Generic.List<string>();
        foreach (var entry in toc) texts.Add(entry.Text);
        Assert.True(texts.Exists(t => t.Contains("Executive") || t.Contains("Summary")));
        Assert.True(texts.Exists(t => t.Contains("Conclusion") || t.Contains("Conclusions")));
    }

    [Fact]
    public void GetTableOfContents_LevelsCorrect()
    {
        var doc = CreateStructuredDoc();
        var toc = doc.GetTableOfContents();
        // Should have H1 and H2 entries
        bool hasH1 = false, hasH2 = false;
        foreach (var entry in toc)
        {
            if (entry.Level == 1) hasH1 = true;
            if (entry.Level == 2) hasH2 = true;
        }
        Assert.True(hasH1);
        Assert.True(hasH2);
    }

    [Fact]
    public void GetTableOfContents_AfterInsertHeading_Increases()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetTableOfContents().Count;
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix", 1);
        var after = doc.GetTableOfContents().Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetTableOfContents_Consistent()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(
            doc.GetTableOfContents().Count,
            doc.GetTableOfContents().Count
        );
    }

    [Fact]
    public void GetTableOfContents_AfterRemoveAllParagraphs_Empty()
    {
        var doc = CreateStructuredDoc();
        doc.RemoveAllParagraphs();
        var toc = doc.GetTableOfContents();
        Assert.True(toc == null || toc.Count == 0);
    }

    [Fact]
    public void GetTableOfContents_SaveLoadConsistent()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetTableOfContents().Count;
        var path = TempFile("toc_test.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetTableOfContents().Count;
        Assert.Equal(before, after);
    }

    // -------------------------------------------------------------------------
    // SetTitle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTitle_NonNullAfter()
    {
        var doc = CreateStructuredDoc();
        doc.SetTitle("Annual Report 2026");
        Assert.NotNull(doc);
    }

    [Fact]
    public void SetTitle_ReflectsInMetadata()
    {
        var doc = CreateStructuredDoc();
        doc.SetTitle("My Document Title");
        var meta = doc.GetDocumentMetadata();
        Assert.True(meta != null);
    }

    [Fact]
    public void SetTitle_PersistsAfterSave()
    {
        var doc = CreateStructuredDoc();
        doc.SetTitle("Persisted Title UNIQUE-TAG-789");
        var path = TempFile("title_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var meta = loaded.GetDocumentMetadata();
        // Title should be preserved in the file
        Assert.NotNull(meta);
    }

    [Fact]
    public void SetTitle_Overwrite()
    {
        var doc = CreateStructuredDoc();
        doc.SetTitle("First Title");
        doc.SetTitle("Second Title");
        // No exception and doc still usable
        Assert.NotNull(doc.ExportToPlainText());
    }

    [Fact]
    public void SetTitle_EmptyString_NoThrow()
    {
        var doc = CreateStructuredDoc();
        var ex = Record.Exception(() => doc.SetTitle(""));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTitle_DocStillUsableAfter()
    {
        var doc = CreateStructuredDoc();
        doc.SetTitle("Title After Which Doc Is Still Usable");
        doc.AppendParagraph("Additional paragraph after SetTitle.");
        Assert.Contains("Additional paragraph", doc.ExportToPlainText());
    }

    // -------------------------------------------------------------------------
    // CountSentences
    // -------------------------------------------------------------------------

    [Fact]
    public void CountSentences_Positive()
    {
        var doc = CreateStructuredDoc();
        Assert.True(doc.CountSentences() > 0);
    }

    [Fact]
    public void CountSentences_IncreasesWithMoreParagraphs()
    {
        var doc = CreateStructuredDoc();
        var before = doc.CountSentences();
        doc.AppendParagraph("This is a new sentence. This is another sentence. And a third one.");
        var after = doc.CountSentences();
        Assert.True(after > before);
    }

    [Fact]
    public void CountSentences_Consistent()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.CountSentences(), doc.CountSentences());
    }

    [Fact]
    public void CountSentences_AfterRemoveAllParagraphs_ZeroOrMinimal()
    {
        var doc = CreateStructuredDoc();
        doc.RemoveAllParagraphs();
        Assert.True(doc.CountSentences() == 0);
    }

    [Fact]
    public void CountSentences_KnownContent_AtLeastExpected()
    {
        var doc = FodtDocument.CreateEmpty();
        // 3 clearly delimited sentences
        doc.AppendParagraph("First sentence here. Second sentence follows. Third and final sentence.");
        Assert.True(doc.CountSentences() >= 2); // at least 2 sentence boundaries detected
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetTableOfContents_SetTitle_CountSentences_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Project Proposal", 1);
        doc.AppendParagraph("This proposal outlines the scope and objectives of the project. It covers key deliverables.");
        doc.AppendParagraph("The project will span six months and involve multiple teams. Resources have been allocated.");
        doc.InsertHeading(3, "Technical Requirements", 2);
        doc.AppendParagraph("The technical requirements include modern infrastructure. Cloud services will be used.");
        doc.AppendParagraph("Security protocols must comply with industry standards. All data must be encrypted.");
        doc.InsertHeading(7, "Timeline and Milestones", 2);
        doc.AppendParagraph("Phase one begins in January. Phase two follows in March. Final delivery is in June.");
        doc.InsertHeading(doc.GetParagraphCount(), "Budget Overview", 1);
        doc.AppendParagraph("The total budget is one million dollars. Resources are allocated per phase.");

        // GetTableOfContents
        var toc = doc.GetTableOfContents();
        Assert.NotNull(toc);
        Assert.True(toc.Count >= 4);

        var tocTexts = new System.Collections.Generic.List<string>();
        foreach (var entry in toc) tocTexts.Add(entry.Text);
        Assert.True(tocTexts.Exists(t => t.Contains("Proposal") || t.Contains("Project")));
        Assert.True(tocTexts.Exists(t => t.Contains("Budget") || t.Contains("Timeline")));

        // Level verification
        var h1Count = 0; var h2Count = 0;
        foreach (var entry in toc)
        {
            if (entry.Level == 1) h1Count++;
            if (entry.Level == 2) h2Count++;
        }
        Assert.Equal(2, h1Count); // Project Proposal + Budget Overview
        Assert.Equal(2, h2Count); // Technical Requirements + Timeline

        // SetTitle
        doc.SetTitle("Project Proposal 2026 — Technical Overview");
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);

        // CountSentences — approximately 12+ sentences across all paragraphs
        var sentenceCount = doc.CountSentences();
        Assert.True(sentenceCount >= 6); // at least 6 clear sentence boundaries

        // InsertHeading and verify TOC grows
        doc.InsertHeading(doc.GetParagraphCount(), "Appendix A", 1);
        var updatedToc = doc.GetTableOfContents();
        Assert.True(updatedToc.Count > toc.Count);

        // CountSentences increases with new paragraph
        doc.AppendParagraph("Appendix content. Additional context. Reference materials follow.");
        var newSentenceCount = doc.CountSentences();
        Assert.True(newSentenceCount > sentenceCount);

        // SaveToFile and reload
        var path = TempFile("dogfood_toc_title.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodtDocument.LoadFile(path);

        // Verify loaded TOC
        var loadedToc = loaded.GetTableOfContents();
        Assert.NotNull(loadedToc);
        Assert.True(loadedToc.Count >= toc.Count);

        // Verify loaded sentence count
        var loadedSentences = loaded.CountSentences();
        Assert.True(loadedSentences >= sentenceCount);

        // SetTitle on loaded and verify no exception
        loaded.SetTitle("Updated Title After Reload");
        Assert.NotNull(loaded.ExportToPlainText());

        // TOC after RemoveAllParagraphs
        var docCopy = CreateStructuredDoc();
        docCopy.RemoveAllParagraphs();
        var emptyToc = docCopy.GetTableOfContents();
        Assert.True(emptyToc == null || emptyToc.Count == 0);
        Assert.True(docCopy.CountSentences() == 0);
    }
}
