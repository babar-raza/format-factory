// Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkNames deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R277

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R277: Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkNames deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(paragraphIndex, name): inserts a named bookmark at the given paragraph.
/// GetBookmarkNames(): returns a list of all bookmark names in the document.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load; AddBookmark no-throw; AddBookmark increases GetBookmarkCount;
/// AddBookmark save-load; AddBookmark multiple bookmarks; AddBookmark then ExportToHtml no-throw;
/// AddBookmark then ExportToMarkdown no-throw; AddBookmark then GetCharCount positive;
/// GetBookmarkNames no-throw; GetBookmarkNames non-null; GetBookmarkNames count matches;
/// GetBookmarkNames consistent; GetBookmarkNames save-load; GetBookmarkNames no-duplicates;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→GetBookmarkNames→SaveToFile pipeline.
/// </summary>
public class FodtR277GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR277GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR277_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Technical Architecture Overview", 1);
        doc.AppendParagraph("This document describes the core technical architecture of the platform.");
        doc.AppendParagraph("All sections have been reviewed and approved by the architecture review board.");
        doc.InsertHeading(3, "System Components", 2);
        doc.AppendParagraph("The system is divided into six distinct architectural layers.");
        doc.AppendParagraph("Each layer has a well-defined interface and single responsibility.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Fresh document without any bookmarks.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(1, "intro-section");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "arch-overview");
        var before = doc.GetBookmarkCount();
        var path = TempFile("bc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    // -------------------------------------------------------------------------
    // AddBookmark
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBookmark_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddBookmark(1, "test-bookmark-alpha"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_GetBookmarkCount()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(2, "section-components");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "persisted-bookmark");
        var before = doc.GetBookmarkCount();
        var path = TempFile("ab_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple_Bookmarks()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(0, "bookmark-heading");
        doc.AddBookmark(1, "bookmark-intro");
        doc.AddBookmark(3, "bookmark-components");
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "html-anchor");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "markdown-anchor");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "char-count-test");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBookmarkNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkNames_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "name-test");
        var ex = Record.Exception(() => doc.GetBookmarkNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkNames_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "non-null-test");
        Assert.NotNull(doc.GetBookmarkNames());
    }

    [Fact]
    public void GetBookmarkNames_Count_Matches_GetBookmarkCount()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(0, "name-match-1");
        doc.AddBookmark(2, "name-match-2");
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkNames().Count);
    }

    [Fact]
    public void GetBookmarkNames_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "consistent-bm");
        var n1 = doc.GetBookmarkNames();
        var n2 = doc.GetBookmarkNames();
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetBookmarkNames_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(1, "sl-bookmark-a");
        doc.AddBookmark(3, "sl-bookmark-b");
        var before = doc.GetBookmarkNames().Count;
        var path = TempFile("bn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkNames().Count);
    }

    [Fact]
    public void GetBookmarkNames_NoDuplicates()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark(0, "unique-bm-1");
        doc.AddBookmark(1, "unique-bm-2");
        doc.AddBookmark(2, "unique-bm-3");
        var names = doc.GetBookmarkNames();
        var set = new System.Collections.Generic.HashSet<string>(names);
        Assert.Equal(names.Count, set.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_GetBookmarkNames_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Enterprise System Architecture 2026", 1);
        doc.AppendParagraph("This document defines the enterprise system architecture for the coming fiscal year.");
        doc.AppendParagraph("All architectural decisions have been validated against the approved technology radar.");

        doc.InsertHeading(3, "Data Layer", 2);
        doc.AppendParagraph("The data layer comprises the primary persistence and caching infrastructure.");
        doc.AppendParagraph("PostgreSQL with streaming replication serves as the primary data store.");

        doc.InsertHeading(6, "Service Layer", 2);
        doc.AppendParagraph("The service layer exposes all business logic through REST and gRPC endpoints.");
        doc.AppendParagraph("Rate limiting and circuit breakers are enforced at the API gateway level.");

        doc.InsertHeading(9, "Presentation Layer", 1);
        doc.AppendParagraph("The presentation layer uses server-side rendering for initial page loads.");
        doc.AppendParagraph("Client-side hydration enables rich interactivity after the initial render.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetBookmarkCount — zero initially
        Assert.Equal(0, doc.GetBookmarkCount());

        // GetBookmarkNames — empty initially
        var initialNames = doc.GetBookmarkNames();
        Assert.NotNull(initialNames);
        Assert.Equal(0, initialNames.Count);

        // AddBookmark — executive summary anchor
        doc.AddBookmark(0, "exec-summary");
        Assert.Equal(1, doc.GetBookmarkCount());

        // AddBookmark — data layer anchor
        doc.AddBookmark(3, "data-layer");
        Assert.Equal(2, doc.GetBookmarkCount());

        // AddBookmark — service layer anchor
        doc.AddBookmark(6, "service-layer");
        Assert.Equal(3, doc.GetBookmarkCount());

        // AddBookmark — presentation layer anchor
        doc.AddBookmark(9, "presentation-layer");
        Assert.Equal(4, doc.GetBookmarkCount());

        // GetBookmarkNames
        var names = doc.GetBookmarkNames();
        Assert.NotNull(names);
        Assert.Equal(4, names.Count);
        foreach (var name in names)
            Assert.NotNull(name);

        // No duplicates
        var nameSet = new System.Collections.Generic.HashSet<string>(names);
        Assert.Equal(names.Count, nameSet.Count);

        // Count matches names count
        Assert.Equal(doc.GetBookmarkCount(), names.Count);

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
        Assert.Equal(names.Count, doc.GetBookmarkNames().Count);

        // ExportToHtml works after bookmarks
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_arch.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetBookmarkCount());
        Assert.Equal(4, loaded.GetBookmarkNames().Count);
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetBookmarkNames on loaded
        var loadedNames = loaded.GetBookmarkNames();
        Assert.NotNull(loadedNames);
        Assert.Equal(4, loadedNames.Count);
        var loadedSet = new System.Collections.Generic.HashSet<string>(loadedNames);
        Assert.Equal(loadedNames.Count, loadedSet.Count);

        // AddBookmark on loaded
        loaded.AddBookmark(loaded.GetParagraphCount() - 1, "appendix");
        Assert.Equal(5, loaded.GetBookmarkCount());
        Assert.Equal(5, loaded.GetBookmarkNames().Count);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Appendix: all architecture decisions are recorded in the ADR register.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_arch_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetBookmarkCount());
        Assert.Equal(5, loaded2.GetBookmarkNames().Count);
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
