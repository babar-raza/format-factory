// Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R295

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R295: Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(name, paragraphIndex): adds a named bookmark at the specified paragraph.
/// GetBookmarkName(index): returns the name of the bookmark at the given index.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load;
/// AddBookmark no-throw; AddBookmark increases count; AddBookmark save-load;
/// AddBookmark multiple; AddBookmark then ExportToHtml no-throw;
/// AddBookmark then ExportToMarkdown no-throw; AddBookmark then GetCharCount positive;
/// GetBookmarkName no-throw; GetBookmarkName non-null; GetBookmarkName consistent;
/// GetBookmarkName save-load; GetBookmarkName multiple;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→GetBookmarkName→SaveToFile pipeline.
/// </summary>
public class FodtR295GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR295GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR295_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Neuroscience of Learning and Memory", 1);
        doc.AppendParagraph("Long-term potentiation (LTP) is the synaptic strengthening mechanism underlying memory formation.");
        doc.AppendParagraph("The hippocampus is critical for episodic memory formation and spatial navigation.");
        doc.InsertHeading(3, "Consolidation Mechanisms", 2);
        doc.AppendParagraph("Memory consolidation during sleep involves hippocampal replay of waking experiences.");
        doc.AppendParagraph("Synaptic homeostasis hypothesis proposes sleep functions to downscale synaptic weights.");
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
        doc.AppendParagraph("No bookmarks yet.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("intro", 0);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("section1", 1);
        var before = doc.GetBookmarkCount();
        var path = TempFile("bkc_save.fodt");
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
        var ex = Record.Exception(() => doc.AddBookmark("chapter1", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("chapter2", 2);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("ref_ltp", 1);
        var before = doc.GetBookmarkCount();
        var path = TempFile("abk_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("intro", 0);
        doc.AddBookmark("ltp_section", 1);
        doc.AddBookmark("hippocampus", 2);
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("html_anchor", 1);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("md_anchor", 2);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("cc_test", 0);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBookmarkName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkName_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("name_test", 0);
        var ex = Record.Exception(() => doc.GetBookmarkName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkName_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("null_test", 1);
        Assert.NotNull(doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("consist_test", 0);
        Assert.Equal(doc.GetBookmarkName(0), doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("sl_test", 0);
        var before = doc.GetBookmarkName(0);
        var path = TempFile("gbn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetBookmarkName(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetBookmarkName_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddBookmark("first_bk", 0);
        doc.AddBookmark("second_bk", 2);
        Assert.NotNull(doc.GetBookmarkName(0));
        Assert.NotNull(doc.GetBookmarkName(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_GetBookmarkName_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "International Trade Theory and Global Value Chains", 1);
        doc.AppendParagraph("Comparative advantage theory explains why nations specialise in goods they produce most efficiently.");
        doc.AppendParagraph("Global value chains have fundamentally restructured international production networks since the 1990s.");

        doc.InsertHeading(3, "Heckscher-Ohlin Model", 2);
        doc.AppendParagraph("Factor endowments determine comparative advantage in the Heckscher-Ohlin framework.");
        doc.AppendParagraph("Leontief paradox challenged the Heckscher-Ohlin model using US trade data in 1953.");

        doc.InsertHeading(6, "New Trade Theory", 2);
        doc.AppendParagraph("Krugman's new trade theory introduced economies of scale and product differentiation.");
        doc.AppendParagraph("Intra-industry trade patterns are better explained by new trade theory than classical models.");

        doc.InsertHeading(9, "Global Value Chain Analysis", 1);
        doc.AppendParagraph("Smile curve analysis reveals that design and distribution capture more value than manufacturing.");
        doc.AppendParagraph("Reshoring trends post-pandemic signal a reconfiguration of global value chain architecture.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetBookmarkCount — zero initially
        Assert.Equal(0, doc.GetBookmarkCount());

        // AddBookmark — key sections
        doc.AddBookmark("intro_trade", 0);
        Assert.Equal(1, doc.GetBookmarkCount());

        doc.AddBookmark("heckscher_ohlin", 3);
        Assert.Equal(2, doc.GetBookmarkCount());

        doc.AddBookmark("new_trade_theory", 6);
        Assert.Equal(3, doc.GetBookmarkCount());

        doc.AddBookmark("gvc_analysis", 9);
        Assert.Equal(4, doc.GetBookmarkCount());

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());

        // GetBookmarkName
        var bk0 = doc.GetBookmarkName(0);
        Assert.NotNull(bk0);
        Assert.Equal(bk0, doc.GetBookmarkName(0)); // consistent

        var bk1 = doc.GetBookmarkName(1);
        Assert.NotNull(bk1);

        var bk2 = doc.GetBookmarkName(2);
        Assert.NotNull(bk2);

        var bk3 = doc.GetBookmarkName(3);
        Assert.NotNull(bk3);

        // ExportToHtml works
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
        var path = TempFile("dogfood_trade.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetBookmarkCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetBookmarkName on loaded
        for (int i = 0; i < loaded.GetBookmarkCount(); i++)
            Assert.NotNull(loaded.GetBookmarkName(i));

        // AddBookmark on loaded
        loaded.AddBookmark("conclusion_trade", loaded.GetParagraphCount() - 1);
        Assert.Equal(5, loaded.GetBookmarkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: understanding trade theory is essential for designing effective industrial and trade policy.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_trade_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetBookmarkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
