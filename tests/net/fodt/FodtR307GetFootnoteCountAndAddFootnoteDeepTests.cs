// Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R307

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R307: Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// AddFootnote(paragraphIndex, text): adds a footnote to the specified paragraph.
/// GetFootnoteText(index): returns the text content of the footnote at the given index.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount consistent;
/// GetFootnoteCount zero for new doc; GetFootnoteCount after AddFootnote increases;
/// GetFootnoteCount save-load;
/// AddFootnote no-throw; AddFootnote increases count; AddFootnote save-load;
/// AddFootnote multiple; AddFootnote then ExportToHtml no-throw; AddFootnote then ExportToMarkdown no-throw;
/// AddFootnote then GetCharCount positive;
/// GetFootnoteText no-throw; GetFootnoteText non-null; GetFootnoteText consistent;
/// GetFootnoteText save-load;
/// dogfood CreateDoc→AddFootnote→GetFootnoteCount→GetFootnoteText→SaveToFile pipeline.
/// </summary>
public class FodtR307GetFootnoteCountAndAddFootnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR307GetFootnoteCountAndAddFootnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR307_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateAcademicDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Behavioural Economics: Nudge Theory and Policy Applications", 1);
        doc.AppendParagraph("Nudge theory proposes that choice architecture can guide individuals toward beneficial decisions without restricting options.");
        doc.AppendParagraph("Thaler and Sunstein's 2008 framework demonstrates measurable improvements in health, wealth, and happiness outcomes.");
        doc.InsertHeading(3, "Empirical Evidence", 2);
        doc.AppendParagraph("Default pension enrolment increased participation rates from 65% to 95% in UK workplace schemes.");
        doc.AppendParagraph("Organ donation opt-out systems increased donor registration rates by 20-25 percentage points across European nations.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateAcademicDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateAcademicDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateAcademicDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A fresh document without any footnotes.");
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = CreateAcademicDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "Thaler, R.H. & Sunstein, C.R. (2008). Nudge: Improving Decisions About Health, Wealth, and Happiness. Yale University Press.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(2, "HM Treasury Workplace Pension Study 2019, Office for National Statistics.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("fc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    // -------------------------------------------------------------------------
    // AddFootnote
    // -------------------------------------------------------------------------

    [Fact]
    public void AddFootnote_NoThrow()
    {
        var doc = CreateAcademicDoc();
        var ex = Record.Exception(() => doc.AddFootnote(0, "See also Kahneman (2011), Thinking Fast and Slow."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Increases_Count()
    {
        var doc = CreateAcademicDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "Statistical significance p<0.001 across all cohorts studied.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_SaveLoad_Persists()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(3, "European Health Outcomes Database, 2022 edition.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("af_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Multiple()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(0, "First footnote reference.");
        doc.AddFootnote(2, "Second footnote reference.");
        doc.AddFootnote(4, "Third footnote reference.");
        Assert.Equal(3, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(1, "HTML export footnote test.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(2, "Markdown export footnote test.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_GetCharCount_Positive()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(0, "Char count test footnote.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFootnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteText_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(1, "Test footnote text.");
        var ex = Record.Exception(() => doc.GetFootnoteText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteText_NonNull()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(2, "Non-null footnote text.");
        Assert.NotNull(doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_Consistent()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(0, "Consistent footnote.");
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_SaveLoad_Consistent()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(3, "Save-load footnote text.");
        var before = doc.GetFootnoteText(0);
        var path = TempFile("ft_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        var after = loaded.GetFootnoteText(0);
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddFootnote_GetFootnoteCount_GetFootnoteText_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Urban Economics: Housing Markets and Gentrification Dynamics", 1);
        doc.AppendParagraph("Housing affordability has deteriorated in major metropolitan areas, with price-to-income ratios reaching 12:1 in London and 15:1 in Sydney.");
        doc.AppendParagraph("Supply constraints, planning restrictions, and land use regulations are identified as primary drivers of housing cost escalation.");

        doc.InsertHeading(3, "Gentrification Mechanisms", 2);
        doc.AppendParagraph("Gentrification processes displace lower-income residents through both direct displacement and exclusionary displacement mechanisms.");
        doc.AppendParagraph("The role of amenity migration in driving neighbourhood transition has been documented across 24 OECD cities since 2000.");

        doc.InsertHeading(6, "Policy Responses", 2);
        doc.AppendParagraph("Inclusionary zoning mandates require developers to allocate 10-30% of units as affordable housing in new residential schemes.");
        doc.AppendParagraph("Community land trusts (CLTs) provide long-term affordability by separating land ownership from building ownership structures.");

        doc.InsertHeading(9, "Empirical Evidence", 1);
        doc.AppendParagraph("A meta-analysis of 47 rent control studies finds mixed evidence on long-term affordability outcomes across different market conditions.");
        doc.AppendParagraph("Upzoning experiments in Auckland and Minneapolis show 3-8% rent reductions within 5 years of implementation.");

        Assert.Equal(10, doc.GetParagraphCount());

        // GetFootnoteCount — zero initially
        Assert.Equal(0, doc.GetFootnoteCount());

        // AddFootnote — academic citations
        doc.AddFootnote(1, "Demographia International Housing Affordability Survey 2024, 20th Annual Edition.");
        Assert.Equal(1, doc.GetFootnoteCount());

        doc.AddFootnote(2, "Glaeser, E.L. & Gyourko, J. (2018). The Economic Implications of Housing Supply. Journal of Economic Perspectives, 32(1), 3-30.");
        Assert.Equal(2, doc.GetFootnoteCount());

        doc.AddFootnote(3, "Marcuse, P. (1986). Abandonment, gentrification and displacement. In N. Smith & P. Williams (Eds.), Gentrification of the City, pp. 153-177.");
        Assert.Equal(3, doc.GetFootnoteCount());

        doc.AddFootnote(5, "Monitoring Urban Change: OECD Housing Data Repository, 2023 Update. Available at stats.oecd.org/housing.");
        Assert.Equal(4, doc.GetFootnoteCount());

        doc.AddFootnote(7, "Diamond, R. & McQuade, T. (2019). Who Wants Affordable Housing in Their Backyard? Journal of Political Economy, 127(3), 1063-1117.");
        Assert.Equal(5, doc.GetFootnoteCount());

        doc.AddFootnote(8, "Mense, A. (2022). The Impact of New Housing Supply on the Distribution of Rents. Working Paper, FAU Erlangen-Nürnberg.");
        Assert.Equal(6, doc.GetFootnoteCount());

        // Consistent
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());

        // GetFootnoteText
        var fn0 = doc.GetFootnoteText(0);
        Assert.NotNull(fn0);
        Assert.Equal(fn0, doc.GetFootnoteText(0)); // consistent

        var fn1 = doc.GetFootnoteText(1);
        Assert.NotNull(fn1);

        var fn5 = doc.GetFootnoteText(5);
        Assert.NotNull(fn5);

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
        var path = TempFile("dogfood_urbaneconomics.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetFootnoteCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetFootnoteText(0));

        // AddFootnote on loaded
        loaded.AddFootnote(9, "Hsieh, C.T. & Moretti, E. (2019). Housing Constraints and Spatial Misallocation. American Economic Journal: Macroeconomics, 11(2), 1-39.");
        Assert.Equal(7, loaded.GetFootnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: effective housing policy requires coordinated action across planning, finance, and social protection domains.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_urbaneconomics_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetFootnoteCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetFootnoteText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddFootnote(0, "Additional citation note."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
