// Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R320

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R320: Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// AddFootnote(paragraphIndex, text): adds a footnote referencing the specified paragraph.
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
public class FodtR320GetFootnoteCountAndAddFootnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR320GetFootnoteCountAndAddFootnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR320_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Machine Learning in Drug Discovery: Algorithms, Applications, and Limitations", 1);
        doc.AppendParagraph("Deep learning models have demonstrated state-of-the-art performance on molecular property prediction benchmarks including BBBP, Tox21, and MUV datasets.");
        doc.AppendParagraph("Graph neural networks represent molecular structures as attributed graphs, enabling permutation-invariant feature learning for QSAR modelling.");
        doc.InsertHeading(3, "Generative Models", 2);
        doc.AppendParagraph("Variational autoencoders and generative adversarial networks have been applied to de novo molecular design with drug-like property constraints.");
        doc.AppendParagraph("Reinforcement learning with molecular generation enables goal-directed optimisation of synthetic accessibility and binding affinity simultaneously.");
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
        doc.AppendParagraph("A document without any footnotes.");
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = CreateAcademicDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "Refer to Gilmer et al. (2017) for the original MPNN formulation.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(2, "Yang et al. (2019) ChemProp paper benchmark results.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("fnc_save.fodt");
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
        var ex = Record.Exception(() => doc.AddFootnote(0, "See Appendix A for supplementary data."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Increases_Count()
    {
        var doc = CreateAcademicDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(3, "Gomez-Bombarelli et al. (2018) Chemical VAE paper.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_SaveLoad_Persists()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(4, "Olivecrona et al. (2017) REINVENT drug generation framework.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("afn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Multiple()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(0, "Introduction reference.");
        doc.AddFootnote(1, "Data availability statement.");
        doc.AddFootnote(3, "Competing interests declaration.");
        Assert.Equal(3, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(2, "HTML export footnote test.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(1, "Markdown export footnote test.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_GetCharCount_Positive()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(0, "Character count test footnote.");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFootnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteText_NoThrow()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(1, "Footnote text retrieval test.");
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
        doc.AddFootnote(0, "Consistency test footnote.");
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_SaveLoad_Consistent()
    {
        var doc = CreateAcademicDoc();
        doc.AddFootnote(3, "Save-load footnote text persistence.");
        var path = TempFile("fnt_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetFootnoteText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddFootnote_GetFootnoteCount_GetFootnoteText_SaveToFile_Pipeline()
    {
        // Systematic review — evidence synthesis in health technology assessment
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Systematic Review of mRNA Vaccine Efficacy: COVID-19 and Influenza Platforms", 1);
        doc.AppendParagraph("mRNA vaccine platforms enable rapid antigen design and manufacturing scale-up, reducing development timelines from years to months compared to conventional approaches.");
        doc.AppendParagraph("Phase III trials of BNT162b2 and mRNA-1273 demonstrated 94-95% efficacy against symptomatic COVID-19 disease in the 30-day post-vaccination period.");

        doc.InsertHeading(3, "Immunogenicity Mechanisms", 2);
        doc.AppendParagraph("Lipid nanoparticle encapsulation protects mRNA from ribonuclease degradation and facilitates endosomal escape for cytoplasmic translation.");
        doc.AppendParagraph("Spike protein antigen presentation triggers both humoral (neutralising antibody) and cellular (CD4+/CD8+ T-cell) immune responses.");

        doc.InsertHeading(6, "Waning Immunity and Booster Dosing", 2);
        doc.AppendParagraph("Vaccine effectiveness against Omicron subvariants declined to 30-40% for infection prevention but maintained 70-85% protection against hospitalisation.");
        doc.AppendParagraph("Bivalent boosters targeting ancestral and BA.4/5 spike sequences demonstrated improved cross-reactive neutralising titres in immunogenicity sub-studies.");

        doc.InsertHeading(9, "Safety Profile", 1);
        doc.AppendParagraph("Myocarditis incidence post-mRNA vaccination estimated at 1-4.8 per 100,000 doses, predominantly in adolescent males following the second dose.");
        doc.AppendParagraph("VAERS and Yellow Card surveillance systems identified reactogenicity as the most common adverse event class, consistent with robust immune activation.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetFootnoteCount — zero initially
        Assert.Equal(0, doc.GetFootnoteCount());

        // AddFootnote — academic citations
        doc.AddFootnote(1, "Polack FP et al. (2020). Safety and Efficacy of the BNT162b2 mRNA Covid-19 Vaccine. N Engl J Med. 383:2603-2615.");
        Assert.Equal(1, doc.GetFootnoteCount());

        doc.AddFootnote(2, "Baden LR et al. (2021). Efficacy and Safety of the mRNA-1273 SARS-CoV-2 Vaccine. N Engl J Med. 384:403-416.");
        Assert.Equal(2, doc.GetFootnoteCount());

        doc.AddFootnote(3, "Pardi N et al. (2018). mRNA vaccines — a new era in vaccinology. Nat Rev Drug Discov. 17:261-279.");
        Assert.Equal(3, doc.GetFootnoteCount());

        doc.AddFootnote(5, "Andrews N et al. (2022). Effectiveness of COVID-19 vaccines against the Omicron variant. N Engl J Med. 386:1532-1546.");
        Assert.Equal(4, doc.GetFootnoteCount());

        doc.AddFootnote(6, "Bivalent Booster Immunobridging Study — EMA Assessment Report, October 2022.");
        Assert.Equal(5, doc.GetFootnoteCount());

        doc.AddFootnote(8, "Oster ME et al. (2022). Myocarditis Cases Reported After mRNA-Based COVID-19 Vaccination. JAMA. 327(4):331-340.");
        Assert.Equal(6, doc.GetFootnoteCount());

        // Consistent
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());

        // GetFootnoteText
        var text0 = doc.GetFootnoteText(0);
        Assert.NotNull(text0);
        Assert.Equal(text0, doc.GetFootnoteText(0)); // consistent

        var text3 = doc.GetFootnoteText(3);
        Assert.NotNull(text3);

        var text5 = doc.GetFootnoteText(5);
        Assert.NotNull(text5);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_mrna_review.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetFootnoteCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetFootnoteText(0));
        Assert.NotNull(loaded.GetFootnoteText(5));

        // AddFootnote on loaded
        loaded.AddFootnote(9, "VAERS Data — Vaccine Adverse Event Reporting System, CDC/FDA Joint Reporting Database (2021-2023).");
        Assert.Equal(7, loaded.GetFootnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: mRNA vaccines represent a paradigm shift in vaccinology with favourable benefit-risk profiles supporting broad population deployment.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_mrna_review_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetFootnoteCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetFootnoteText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddFootnote(0, "Final footnote."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
