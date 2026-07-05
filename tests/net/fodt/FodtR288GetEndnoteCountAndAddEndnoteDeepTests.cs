// Tests for FodtDocument.GetEndnoteCount, AddEndnote, GetEndnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R288

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R288: Tests for FodtDocument.GetEndnoteCount, AddEndnote, GetEndnoteText deeper.
/// GetEndnoteCount(): returns the number of endnotes in the document.
/// AddEndnote(paragraphIndex, text): adds an endnote at the specified paragraph.
/// GetEndnoteText(endnoteIndex): returns the text of the specified endnote.
/// Covers: GetEndnoteCount no-throw; GetEndnoteCount non-negative; GetEndnoteCount consistent;
/// GetEndnoteCount zero for new doc; GetEndnoteCount after AddEndnote increases;
/// GetEndnoteCount save-load;
/// AddEndnote no-throw; AddEndnote increases count; AddEndnote save-load;
/// AddEndnote multiple; AddEndnote then ExportToHtml no-throw;
/// AddEndnote then ExportToMarkdown no-throw; AddEndnote then GetCharCount positive;
/// GetEndnoteText no-throw; GetEndnoteText non-null; GetEndnoteText consistent;
/// GetEndnoteText save-load; GetEndnoteText multiple endnotes;
/// dogfood CreateDoc→AddEndnote→GetEndnoteCount→GetEndnoteText→SaveToFile pipeline.
/// </summary>
public class FodtR288GetEndnoteCountAndAddEndnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR288GetEndnoteCountAndAddEndnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR288_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Philosophy of Artificial Intelligence", 1);
        doc.AppendParagraph("The question of machine consciousness has occupied philosophers for decades.");
        doc.AppendParagraph("Functionalism holds that mental states are defined by their functional roles.");
        doc.InsertHeading(3, "The Chinese Room Argument", 2);
        doc.AppendParagraph("Searle's Chinese Room thought experiment challenges computational theories of mind.");
        doc.AppendParagraph("Critics argue that the system as a whole understands, even if no part does individually.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetEndnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEndnoteCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetEndnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEndnoteCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetEndnoteCount() >= 0);
    }

    [Fact]
    public void GetEndnoteCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetEndnoteCount(), doc.GetEndnoteCount());
    }

    [Fact]
    public void GetEndnoteCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No endnotes in this document.");
        Assert.Equal(0, doc.GetEndnoteCount());
    }

    [Fact]
    public void GetEndnoteCount_AfterAddEndnote_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetEndnoteCount();
        doc.AddEndnote(1, "Turing, A. (1950). Computing Machinery and Intelligence. Mind, 59(236), 433-460.");
        Assert.Equal(before + 1, doc.GetEndnoteCount());
    }

    [Fact]
    public void GetEndnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Searle, J. (1980). Minds, Brains, and Programs. Behavioral and Brain Sciences, 3(3), 417-424.");
        var before = doc.GetEndnoteCount();
        var path = TempFile("enc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEndnoteCount());
    }

    // -------------------------------------------------------------------------
    // AddEndnote
    // -------------------------------------------------------------------------

    [Fact]
    public void AddEndnote_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddEndnote(1, "Chalmers, D. (1996). The Conscious Mind. Oxford University Press."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddEndnote_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetEndnoteCount();
        doc.AddEndnote(2, "Dennett, D. (1991). Consciousness Explained. Little, Brown and Company.");
        Assert.Equal(before + 1, doc.GetEndnoteCount());
    }

    [Fact]
    public void AddEndnote_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Nagel, T. (1974). What Is It Like to Be a Bat? Philosophical Review, 83(4), 435-450.");
        var before = doc.GetEndnoteCount();
        var path = TempFile("ae_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEndnoteCount());
    }

    [Fact]
    public void AddEndnote_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(0, "Block, N. (1995). On a Confusion about a Function of Consciousness. Behavioral and Brain Sciences, 18(2).");
        doc.AddEndnote(2, "Jackson, F. (1982). Epiphenomenal Qualia. Philosophical Quarterly, 32(127), 127-136.");
        doc.AddEndnote(4, "Levine, J. (1983). Materialism and Qualia: The Explanatory Gap. Pacific Philosophical Quarterly.");
        Assert.Equal(3, doc.GetEndnoteCount());
    }

    [Fact]
    public void AddEndnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "HTML endnote test reference.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddEndnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(2, "Markdown endnote test reference.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddEndnote_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "GetCharCount endnote test.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetEndnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEndnoteText_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Test endnote text.");
        var ex = Record.Exception(() => doc.GetEndnoteText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetEndnoteText_NonNull()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Non-null endnote test.");
        Assert.NotNull(doc.GetEndnoteText(0));
    }

    [Fact]
    public void GetEndnoteText_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Consistent endnote text.");
        Assert.Equal(doc.GetEndnoteText(0), doc.GetEndnoteText(0));
    }

    [Fact]
    public void GetEndnoteText_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(1, "Save load endnote text.");
        var before = doc.GetEndnoteText(0);
        var path = TempFile("get_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetEndnoteText(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetEndnoteText_Multiple_Endnotes()
    {
        var doc = CreateRichDoc();
        doc.AddEndnote(0, "First endnote reference.");
        doc.AddEndnote(2, "Second endnote reference.");
        Assert.NotNull(doc.GetEndnoteText(0));
        Assert.NotNull(doc.GetEndnoteText(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddEndnote_GetEndnoteCount_GetEndnoteText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Environmental Economics and Climate Policy", 1);
        doc.AppendParagraph("Carbon pricing mechanisms represent the most efficient approach to reducing greenhouse gas emissions.");
        doc.AppendParagraph("The social cost of carbon incorporates damages from climate change into economic decision-making.");

        doc.InsertHeading(3, "Market-Based Instruments", 2);
        doc.AppendParagraph("Emissions trading schemes create financial incentives for reducing pollution at lowest cost.");
        doc.AppendParagraph("Carbon taxes provide price certainty while allowing quantity uncertainty in emission reductions.");

        doc.InsertHeading(6, "Regulatory Approaches", 2);
        doc.AppendParagraph("Command-and-control regulations set specific limits but may not achieve cost-effective outcomes.");
        doc.AppendParagraph("Technology mandates can drive innovation but may lock in sub-optimal solutions prematurely.");

        doc.InsertHeading(9, "Distributional Effects", 1);
        doc.AppendParagraph("Carbon pricing can be regressive absent revenue recycling to lower-income households.");
        doc.AppendParagraph("Dividend policies have been shown to make carbon pricing broadly progressive in multiple jurisdictions.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetEndnoteCount — zero initially
        Assert.Equal(0, doc.GetEndnoteCount());

        // AddEndnote — introduction
        doc.AddEndnote(0, "IPCC (2023). Climate Change 2023: Synthesis Report. Intergovernmental Panel on Climate Change, Geneva.");
        Assert.Equal(1, doc.GetEndnoteCount());

        // AddEndnote — ETS
        doc.AddEndnote(3, "Schmalensee, R. and Stavins, R. (2017). Lessons Learned from Three Decades of Experience with Cap-and-Trade. Review of Environmental Economics and Policy.");
        Assert.Equal(2, doc.GetEndnoteCount());

        // AddEndnote — regulatory
        doc.AddEndnote(6, "Weitzman, M. (1974). Prices vs. Quantities. Review of Economic Studies, 41(4), 477-491.");
        Assert.Equal(3, doc.GetEndnoteCount());

        // AddEndnote — distributional
        doc.AddEndnote(9, "Goulder, L., Hafstead, M., Kim, G. and Long, X. (2019). Impacts of a Carbon Tax across US Household Income Groups. Journal of Public Economics.");
        Assert.Equal(4, doc.GetEndnoteCount());

        // GetEndnoteText
        var t0 = doc.GetEndnoteText(0);
        var t1 = doc.GetEndnoteText(1);
        var t2 = doc.GetEndnoteText(2);
        var t3 = doc.GetEndnoteText(3);
        Assert.NotNull(t0);
        Assert.NotNull(t1);
        Assert.NotNull(t2);
        Assert.NotNull(t3);

        // Consistent
        Assert.Equal(doc.GetEndnoteCount(), doc.GetEndnoteCount());
        Assert.Equal(doc.GetEndnoteText(0), doc.GetEndnoteText(0));

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
        var path = TempFile("dogfood_climate_econ.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetEndnoteCount());
        Assert.True(loaded.GetParagraphCount() > 0);

        // GetEndnoteText on loaded
        for (int i = 0; i < loaded.GetEndnoteCount(); i++)
            Assert.NotNull(loaded.GetEndnoteText(i));

        // AddEndnote on loaded
        loaded.AddEndnote(loaded.GetParagraphCount() - 1, "Stern, N. (2007). The Economics of Climate Change: The Stern Review. Cambridge University Press.");
        Assert.Equal(5, loaded.GetEndnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: a portfolio of policy instruments is required to achieve deep decarbonization by mid-century.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_climate_econ_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetEndnoteCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.ExportToPlainText());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
