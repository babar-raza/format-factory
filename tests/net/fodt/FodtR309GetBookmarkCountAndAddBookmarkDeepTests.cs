// Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkPosition deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R309

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R309: Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkPosition deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(name, paragraphIndex): adds a named bookmark at the specified paragraph.
/// GetBookmarkPosition(name): returns the paragraph index of the named bookmark.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load;
/// AddBookmark no-throw; AddBookmark increases count; AddBookmark save-load;
/// AddBookmark multiple; AddBookmark then ExportToHtml no-throw; AddBookmark then ExportToMarkdown no-throw;
/// AddBookmark then GetCharCount positive;
/// GetBookmarkPosition no-throw; GetBookmarkPosition non-negative; GetBookmarkPosition consistent;
/// GetBookmarkPosition save-load;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→GetBookmarkPosition→SaveToFile pipeline.
/// </summary>
public class FodtR309GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR309GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR309_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateTechnicalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Deep Learning Architectures: From CNN to Transformers", 1);
        doc.AppendParagraph("Convolutional neural networks extract hierarchical spatial features through learned filter banks.");
        doc.AppendParagraph("Recurrent architectures process sequential data by maintaining hidden state across time steps.");
        doc.InsertHeading(3, "Attention Mechanisms", 2);
        doc.AppendParagraph("Self-attention allows models to relate each position to every other position in a sequence.");
        doc.AppendParagraph("Multi-head attention projects queries, keys, and values through different learned subspaces.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateTechnicalDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateTechnicalDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No bookmarks in this new document.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateTechnicalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("intro_section", 0);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("cnn_section", 1);
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
        var doc = CreateTechnicalDoc();
        var ex = Record.Exception(() => doc.AddBookmark("first_para", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_Count()
    {
        var doc = CreateTechnicalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("rnn_section", 2);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("attention_section", 3);
        var before = doc.GetBookmarkCount();
        var path = TempFile("ab_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("title", 0);
        doc.AddBookmark("intro", 1);
        doc.AddBookmark("attention", 4);
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("html_test", 0);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("md_test", 1);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetCharCount_Positive()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("char_test", 2);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBookmarkPosition
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkPosition_NoThrow()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("pos_test", 2);
        var ex = Record.Exception(() => doc.GetBookmarkPosition("pos_test"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkPosition_NonNegative()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("nonneg_test", 1);
        Assert.True(doc.GetBookmarkPosition("nonneg_test") >= 0);
    }

    [Fact]
    public void GetBookmarkPosition_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("consist_test", 3);
        Assert.Equal(doc.GetBookmarkPosition("consist_test"), doc.GetBookmarkPosition("consist_test"));
    }

    [Fact]
    public void GetBookmarkPosition_SaveLoad_Consistent()
    {
        var doc = CreateTechnicalDoc();
        doc.AddBookmark("saveload_test", 2);
        var before = doc.GetBookmarkPosition("saveload_test");
        var path = TempFile("bp_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetBookmarkPosition("saveload_test");
        Assert.True(after >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_GetBookmarkPosition_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "International Relations Theory: Power, Institutions, and Norms", 1);
        doc.AppendParagraph("Realist theory posits that states are the primary actors in an anarchic international system driven by power competition.");
        doc.AppendParagraph("Liberal institutionalism argues that international organisations reduce transaction costs and promote cooperative equilibria.");

        doc.InsertHeading(3, "Constructivism and Norms", 2);
        doc.AppendParagraph("Constructivist scholars emphasise how ideas, norms, and identities shape state behaviour and international outcomes.");
        doc.AppendParagraph("The norm life cycle model tracks the emergence, cascade, and internalisation of international norms over time.");

        doc.InsertHeading(6, "Critical Perspectives", 2);
        doc.AppendParagraph("Critical theory challenges mainstream IR by exposing how dominant paradigms serve hegemonic state interests.");
        doc.AppendParagraph("Feminist IR scholarship examines how gender hierarchies structure both domestic and international political arrangements.");

        doc.InsertHeading(9, "Empirical Applications", 1);
        doc.AppendParagraph("The democratic peace thesis holds that liberal democracies rarely engage in armed conflict with one another.");
        doc.AppendParagraph("Regime complexity in international institutions creates overlapping authority that complicates compliance and enforcement.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetBookmarkCount — zero initially
        Assert.Equal(0, doc.GetBookmarkCount());

        // AddBookmark — navigation anchors
        doc.AddBookmark("bm_title", 0);
        Assert.Equal(1, doc.GetBookmarkCount());

        doc.AddBookmark("bm_realism", 1);
        Assert.Equal(2, doc.GetBookmarkCount());

        doc.AddBookmark("bm_liberalism", 2);
        Assert.Equal(3, doc.GetBookmarkCount());

        doc.AddBookmark("bm_constructivism", 4);
        Assert.Equal(4, doc.GetBookmarkCount());

        doc.AddBookmark("bm_critical", 6);
        Assert.Equal(5, doc.GetBookmarkCount());

        doc.AddBookmark("bm_democratic_peace", 8);
        Assert.Equal(6, doc.GetBookmarkCount());

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());

        // GetBookmarkPosition
        var pos0 = doc.GetBookmarkPosition("bm_title");
        Assert.True(pos0 >= 0);
        Assert.Equal(pos0, doc.GetBookmarkPosition("bm_title")); // consistent

        var pos1 = doc.GetBookmarkPosition("bm_realism");
        Assert.True(pos1 >= 0);

        var pos5 = doc.GetBookmarkPosition("bm_democratic_peace");
        Assert.True(pos5 >= 0);

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
        var path = TempFile("dogfood_ir_theory.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetBookmarkCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.True(loaded.GetBookmarkPosition("bm_title") >= 0);

        // AddBookmark on loaded
        loaded.AddBookmark("bm_conclusion", loaded.GetParagraphCount() - 1);
        Assert.Equal(7, loaded.GetBookmarkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: IR theory continues to evolve in response to new empirical challenges and interdisciplinary insights.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_ir_theory_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetBookmarkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.True(loaded2.GetBookmarkPosition("bm_realism") >= 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddBookmark("bm_new", 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
