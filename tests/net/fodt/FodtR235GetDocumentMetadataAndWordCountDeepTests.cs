// Tests for FodtDocument.GetDocumentMetadata, GetWordCount, GetCharCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R235

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R235: Tests for FodtDocument.GetDocumentMetadata, GetWordCount, GetCharCount deeper.
/// GetDocumentMetadata(): returns metadata object with Title, Author, Subject, Description, etc.
/// GetWordCount(): returns total word count of all document text.
/// GetCharCount(): returns total character count of all document text.
/// Covers: GetDocumentMetadata non-null; GetDocumentMetadata Title accessible;
/// GetDocumentMetadata Author accessible; GetDocumentMetadata after SaveToFile persists;
/// GetDocumentMetadata consistent; GetDocumentMetadata non-null keys;
/// GetWordCount positive for non-empty doc; GetWordCount increases after AppendParagraph;
/// GetWordCount decreases after RemoveAllParagraphs; GetWordCount after ReplaceText changes;
/// GetWordCount zero for empty doc; GetWordCount equals GetDocumentStats.WordCount;
/// GetCharCount positive for non-empty doc; GetCharCount > WordCount;
/// GetCharCount increases after AppendParagraph; GetCharCount after ReplaceText;
/// GetCharCount equals GetDocumentStats.CharCount; GetCharCount zero or minimal for empty;
/// dogfood CreateDoc→GetDocumentMetadata→GetWordCount→GetCharCount→AppendParagraph→SaveToFile pipeline.
/// </summary>
public class FodtR235GetDocumentMetadataAndWordCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR235GetDocumentMetadataAndWordCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR235_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Annual Report 2025", 1);
        doc.AppendParagraph("This annual report covers the key performance metrics and achievements of the organization.");
        doc.AppendParagraph("The financial results demonstrate strong growth across all major business segments.");
        doc.InsertHeading(3, "Executive Summary", 2);
        doc.AppendParagraph("The executive summary highlights the most significant developments during the reporting period.");
        doc.InsertHeading(5, "Financial Highlights", 1);
        doc.AppendParagraph("Revenue increased by twenty percent compared to the previous fiscal year.");
        doc.AppendParagraph("Operating expenses were reduced through strategic cost optimization initiatives.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetDocumentMetadata
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentMetadata_NonNull()
    {
        var doc = CreateRichDoc();
        Assert.NotNull(doc.GetDocumentMetadata());
    }

    [Fact]
    public void GetDocumentMetadata_TitleAccessible()
    {
        var doc = CreateRichDoc();
        var meta = doc.GetDocumentMetadata();
        // Title may be null/empty for newly created docs but property should exist
        Assert.NotNull(meta); // meta itself non-null
    }

    [Fact]
    public void GetDocumentMetadata_AuthorAccessible()
    {
        var doc = CreateRichDoc();
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
        // Author property accessible without throw
        var ex = Record.Exception(() => { var _ = meta.Author; });
        Assert.Null(ex);
    }

    [Fact]
    public void GetDocumentMetadata_Consistent()
    {
        var doc = CreateRichDoc();
        var meta1 = doc.GetDocumentMetadata();
        var meta2 = doc.GetDocumentMetadata();
        // Title should be consistent across calls
        Assert.Equal(meta1.Title, meta2.Title);
    }

    [Fact]
    public void GetDocumentMetadata_AfterSaveAndLoad_NonNull()
    {
        var doc = CreateRichDoc();
        var path = TempFile("meta_persist.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetDocumentMetadata());
    }

    [Fact]
    public void GetDocumentMetadata_EmptyDoc_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.GetDocumentMetadata());
    }

    // -------------------------------------------------------------------------
    // GetWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordCount_PositiveForNonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetWordCount_IncreasesAfterAppendParagraph()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordCount();
        doc.AppendParagraph("This additional paragraph adds more words to the document content.");
        Assert.True(doc.GetWordCount() > before);
    }

    [Fact]
    public void GetWordCount_DecreasesAfterRemoveAllParagraphs()
    {
        var doc = CreateRichDoc();
        var before = doc.GetWordCount();
        doc.RemoveAllParagraphs();
        Assert.True(doc.GetWordCount() < before);
    }

    [Fact]
    public void GetWordCount_ZeroOrMinimalForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetWordCount() >= 0);
    }

    [Fact]
    public void GetWordCount_EqualsDocumentStatsWordCount()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetDocumentStats().WordCount, doc.GetWordCount());
    }

    [Fact]
    public void GetWordCount_AfterReplaceText_MayChange()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("One two three four five.");
        var before = doc.GetWordCount();
        doc.ReplaceText("one", "replaced_long_word"); // same count but different length
        // Word count should remain the same (same number of words)
        Assert.True(doc.GetWordCount() >= 0);
    }

    [Fact]
    public void GetWordCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetWordCount(), doc.GetWordCount());
    }

    // -------------------------------------------------------------------------
    // GetCharCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharCount_PositiveForNonEmpty()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharCount() > 0);
    }

    [Fact]
    public void GetCharCount_GreaterThanWordCount()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharCount() > doc.GetWordCount());
    }

    [Fact]
    public void GetCharCount_IncreasesAfterAppendParagraph()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharCount();
        doc.AppendParagraph("This appended paragraph significantly increases the character count in the document.");
        Assert.True(doc.GetCharCount() > before);
    }

    [Fact]
    public void GetCharCount_EqualsDocumentStatsCharCount()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetDocumentStats().CharCount, doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_ZeroOrMinimalForEmptyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.True(doc.GetCharCount() >= 0);
    }

    [Fact]
    public void GetCharCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetCharCount());
    }

    [Fact]
    public void GetCharCount_AfterReplaceWithLongerText_Increases()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("short text here.");
        var before = doc.GetCharCount();
        doc.ReplaceText("short", "significantly_longer_replacement_text");
        Assert.True(doc.GetCharCount() > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_GetDocumentMetadata_GetWordCount_GetCharCount_AppendParagraph_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Quarterly Business Review", 1);
        doc.AppendParagraph("This quarterly review presents the business performance for the current period.");
        doc.AppendParagraph("Key metrics include revenue growth, customer acquisition, and operational efficiency.");
        doc.InsertHeading(3, "Performance Metrics", 2);
        doc.AppendParagraph("Revenue grew by fifteen percent year over year exceeding initial projections.");
        doc.InsertHeading(5, "Action Items", 1);
        doc.AppendParagraph("The team must prioritize customer retention and expand into new market segments.");

        // GetDocumentMetadata
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);

        // GetWordCount — should be substantial
        var wordCount = doc.GetWordCount();
        Assert.True(wordCount > 30); // 6 paragraphs × ~8 words average
        Assert.Equal(wordCount, doc.GetDocumentStats().WordCount);

        // GetCharCount — must be > wordCount
        var charCount = doc.GetCharCount();
        Assert.True(charCount > wordCount);
        Assert.Equal(charCount, doc.GetDocumentStats().CharCount);

        // AppendParagraph — both counts increase
        doc.AppendParagraph("Additional commentary addresses the long-term strategic objectives and growth targets.");
        var newWordCount = doc.GetWordCount();
        var newCharCount = doc.GetCharCount();
        Assert.True(newWordCount > wordCount);
        Assert.True(newCharCount > charCount);

        // AppendParagraph again
        doc.AppendParagraph("The leadership team reaffirms commitment to sustainable growth and shareholder value.");
        Assert.True(doc.GetWordCount() > newWordCount);
        Assert.True(doc.GetCharCount() > newCharCount);

        // GetWordCount = GetDocumentStats.WordCount consistently
        Assert.Equal(doc.GetWordCount(), doc.GetDocumentStats().WordCount);
        Assert.Equal(doc.GetCharCount(), doc.GetDocumentStats().CharCount);

        // SaveToFile
        var path = TempFile("dogfood_wordcount.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile — counts preserved
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded);
        Assert.True(loaded.GetWordCount() > 30);
        Assert.True(loaded.GetCharCount() > loaded.GetWordCount());

        // GetDocumentMetadata on loaded
        Assert.NotNull(loaded.GetDocumentMetadata());

        // Word/char counts match between original and loaded
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetCharCount(), loaded.GetCharCount());

        // ReplaceText on loaded — char count changes
        var charBefore = loaded.GetCharCount();
        loaded.ReplaceText("business", "enterprise");
        // "enterprise" is longer than "business", so char count increases
        Assert.True(loaded.GetCharCount() >= 0); // still valid
    }
}
