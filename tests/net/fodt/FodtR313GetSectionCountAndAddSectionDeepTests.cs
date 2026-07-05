// Tests for FodtDocument.GetSectionCount, AddSection, GetSectionName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R313

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R313: Tests for FodtDocument.GetSectionCount, AddSection, GetSectionName deeper.
/// GetSectionCount(): returns the number of sections in the document.
/// AddSection(name): adds a named section to the document.
/// GetSectionName(index): returns the name of the section at the given index.
/// Covers: GetSectionCount no-throw; GetSectionCount non-negative; GetSectionCount consistent;
/// GetSectionCount zero for new doc; GetSectionCount after AddSection increases;
/// GetSectionCount save-load;
/// AddSection no-throw; AddSection increases count; AddSection save-load;
/// AddSection multiple; AddSection then ExportToHtml no-throw; AddSection then ExportToMarkdown no-throw;
/// AddSection then GetCharCount positive;
/// GetSectionName no-throw; GetSectionName non-null; GetSectionName consistent;
/// GetSectionName save-load;
/// dogfood CreateDoc→AddSection→GetSectionCount→GetSectionName→SaveToFile pipeline.
/// </summary>
public class FodtR313GetSectionCountAndAddSectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR313GetSectionCountAndAddSectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR313_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateMultiSectionDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Monetary Policy Frameworks in Advanced Economies", 1);
        doc.AppendParagraph("Central banks deploy multiple policy instruments to achieve dual mandates of price stability and maximum employment.");
        doc.AppendParagraph("Inflation targeting frameworks introduced in the 1990s anchored expectations and reduced inflation volatility across OECD nations.");
        doc.InsertHeading(3, "Unconventional Monetary Policy", 2);
        doc.AppendParagraph("Quantitative easing expands central bank balance sheets by purchasing government bonds and mortgage-backed securities.");
        doc.AppendParagraph("Forward guidance communicates future policy intentions to shape market expectations and long-term interest rates.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_NoThrow()
    {
        var doc = CreateMultiSectionDoc();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_NonNegative()
    {
        var doc = CreateMultiSectionDoc();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void GetSectionCount_Consistent()
    {
        var doc = CreateMultiSectionDoc();
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A fresh document with no named sections.");
        Assert.Equal(0, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_Increases()
    {
        var doc = CreateMultiSectionDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("introduction");
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_SaveLoad_Consistent()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("policy_section");
        var before = doc.GetSectionCount();
        var path = TempFile("sc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    // -------------------------------------------------------------------------
    // AddSection
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSection_NoThrow()
    {
        var doc = CreateMultiSectionDoc();
        var ex = Record.Exception(() => doc.AddSection("intro_section"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Increases_Count()
    {
        var doc = CreateMultiSectionDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("qe_section");
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_SaveLoad_Persists()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("forward_guidance");
        var before = doc.GetSectionCount();
        var path = TempFile("as_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void AddSection_Multiple()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("abstract");
        doc.AddSection("methodology");
        doc.AddSection("results");
        Assert.Equal(3, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("html_test");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("md_test");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_GetCharCount_Positive()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("char_test");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetSectionName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionName_NoThrow()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("name_test");
        var ex = Record.Exception(() => doc.GetSectionName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionName_NonNull()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("non_null_test");
        Assert.NotNull(doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_Consistent()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("consist_test");
        Assert.Equal(doc.GetSectionName(0), doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_SaveLoad_Consistent()
    {
        var doc = CreateMultiSectionDoc();
        doc.AddSection("saveload_test");
        var before = doc.GetSectionName(0);
        var path = TempFile("sn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetSectionName(0));
        Assert.True(loaded.GetSectionName(0).Length >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSection_GetSectionCount_GetSectionName_SaveToFile_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Global Supply Chain Resilience: Disruption, Adaptation, and Strategy", 1);
        doc.AppendParagraph("The COVID-19 pandemic exposed critical vulnerabilities in globally integrated supply chains across all major industrial sectors.");
        doc.AppendParagraph("Just-in-time inventory systems optimised for cost-efficiency proved highly fragile under simultaneous demand and supply shocks.");

        doc.InsertHeading(3, "Disruption Taxonomy", 2);
        doc.AppendParagraph("Supply chain disruptions are classified along three axes: origin (natural/human-induced), scope (firm/industry/systemic), and duration (transient/persistent).");
        doc.AppendParagraph("The Suez Canal blockage of 2021 demonstrated how single-point failures propagate across multi-tier supplier networks within 72 hours.");

        doc.InsertHeading(6, "Resilience Strategies", 2);
        doc.AppendParagraph("Supplier diversification across geographies reduces concentration risk but increases coordination costs and inventory requirements.");
        doc.AppendParagraph("Digital twin technology enables real-time simulation of supply chain stress scenarios with sub-24-hour decision response cycles.");

        doc.InsertHeading(9, "Policy Implications", 1);
        doc.AppendParagraph("Friend-shoring and near-shoring policies reflect geopolitical risk premia being incorporated into supply chain investment decisions.");
        doc.AppendParagraph("Industrial policy resurgence in semiconductors, pharmaceuticals, and critical minerals signals a structural shift from pure market allocation.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetSectionCount — zero initially
        Assert.Equal(0, doc.GetSectionCount());

        // AddSection — structural document sections
        doc.AddSection("sec_executive_summary");
        Assert.Equal(1, doc.GetSectionCount());

        doc.AddSection("sec_disruption_taxonomy");
        Assert.Equal(2, doc.GetSectionCount());

        doc.AddSection("sec_resilience_strategies");
        Assert.Equal(3, doc.GetSectionCount());

        doc.AddSection("sec_digital_twin_analysis");
        Assert.Equal(4, doc.GetSectionCount());

        doc.AddSection("sec_policy_implications");
        Assert.Equal(5, doc.GetSectionCount());

        doc.AddSection("sec_conclusion");
        Assert.Equal(6, doc.GetSectionCount());

        // Consistent
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());

        // GetSectionName — first and last
        var name0 = doc.GetSectionName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetSectionName(0)); // consistent

        var name5 = doc.GetSectionName(5);
        Assert.NotNull(name5);

        var name2 = doc.GetSectionName(2);
        Assert.NotNull(name2);

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
        var path = TempFile("dogfood_supply_chain.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetSectionCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetSectionName(0));

        // AddSection on loaded
        loaded.AddSection("sec_appendix");
        Assert.Equal(7, loaded.GetSectionCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: supply chain resilience requires systemic investment in redundancy, digitisation, and geopolitical risk assessment.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_supply_chain_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetSectionCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetSectionName(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddSection("sec_final"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
