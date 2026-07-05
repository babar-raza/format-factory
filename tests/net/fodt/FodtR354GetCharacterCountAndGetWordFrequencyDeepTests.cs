// Tests for FodtDocument.GetCharacterCount, GetWordFrequency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R354

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R354: Tests for FodtDocument.GetCharacterCount, GetWordFrequency deeper.
/// GetCharacterCount(): returns the total number of characters in the document.
/// GetWordFrequency(word): returns the frequency (count) of a specific word across the document.
/// Covers: GetCharacterCount no-throw; GetCharacterCount non-negative; GetCharacterCount consistent;
/// GetCharacterCount save-load; GetCharacterCount positive for doc with content;
/// GetCharacterCount equals GetCharCount;
/// GetWordFrequency no-throw; GetWordFrequency non-negative; GetWordFrequency consistent;
/// GetWordFrequency zero for absent word; GetWordFrequency save-load;
/// GetWordFrequency positive for known word; GetWordFrequency then GetParagraphCount unchanged;
/// dogfood CreateDoc→GetCharacterCount→GetWordFrequency→SaveToFile pipeline.
/// </summary>
public class FodtR354GetCharacterCountAndGetWordFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR354GetCharacterCountAndGetWordFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR354_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateResearchDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Systematic Review: Efficacy of Digital Cognitive Behavioural Therapy in Adolescent Depression", 1);
        doc.AppendParagraph("Background: adolescent depression represents a significant public health challenge, with prevalence estimated at 13-14% in UK secondary school populations. Digital interventions, including smartphone applications and web-based CBT programmes, offer scalable alternatives to face-to-face therapy.");
        doc.AppendParagraph("Methods: we conducted a systematic review and meta-analysis following PRISMA 2020 guidelines. Electronic databases searched: MEDLINE, PsycINFO, EMBASE, CENTRAL, and ClinicalTrials.gov. Search period: January 2015 to December 2024. Randomised controlled trials of digital CBT interventions in adolescents aged 12-18 years with clinically significant depressive symptoms were eligible.");
        doc.AppendParagraph("Results: seventeen trials (n=4,382 participants) met inclusion criteria. Digital CBT showed moderate effect on depressive symptoms versus control (SMD -0.42, 95% CI -0.56 to -0.28, p<0.001, I²=47%). Guided digital CBT outperformed unguided (SMD -0.51 vs -0.28). Completion rates ranged from 54% to 89% across included trials.");
        doc.AppendParagraph("Conclusions: digital CBT demonstrates clinically meaningful reductions in adolescent depression with moderate effect size. Heterogeneity related to guidance intensity and parental involvement. Future trials should standardise outcome measurement using validated adolescent-specific depression scales.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCharacterCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharacterCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetCharacterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharacterCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetCharacterCount() >= 0);
    }

    [Fact]
    public void GetCharacterCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetCharacterCount(), doc.GetCharacterCount());
    }

    [Fact]
    public void GetCharacterCount_Positive_ForDocWithContent()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetCharacterCount() > 0);
    }

    [Fact]
    public void GetCharacterCount_Equals_GetCharCount()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetCharCount(), doc.GetCharacterCount());
    }

    [Fact]
    public void GetCharacterCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetCharacterCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCharacterCount());
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetWordFrequency("depression"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordFrequency_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetWordFrequency("depression") >= 0);
    }

    [Fact]
    public void GetWordFrequency_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetWordFrequency("digital"), doc.GetWordFrequency("digital"));
    }

    [Fact]
    public void GetWordFrequency_Zero_ForAbsentWord()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(0, doc.GetWordFrequency("xyznonexistentword123"));
    }

    [Fact]
    public void GetWordFrequency_Positive_ForKnownWord()
    {
        var doc = CreateResearchDoc();
        // "CBT" appears multiple times in the document
        Assert.True(doc.GetWordFrequency("CBT") > 0);
    }

    [Fact]
    public void GetWordFrequency_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetWordFrequency("depression");
        var path = TempFile("wf_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWordFrequency("depression"));
    }

    [Fact]
    public void GetWordFrequency_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetParagraphCount();
        _ = doc.GetWordFrequency("adolescent");
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCharacterCount_GetWordFrequency_Pipeline()
    {
        // Policy — UK Government white paper: "The Future of Artificial Intelligence Regulation"
        // Character count and word frequency used for legislative drafting quality analysis
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "AI Regulation White Paper: A Pro-Innovation Approach to Artificial Intelligence", 1);
        doc.AppendParagraph("The United Kingdom Government is committed to a pro-innovation, risk-proportionate approach to artificial intelligence regulation. This white paper sets out the Government's framework for supporting safe, responsible deployment of AI across the UK economy, building on the strengths of existing regulatory bodies while avoiding unnecessary duplication or fragmentation.");
        doc.AppendParagraph("The framework is built on five cross-sectoral principles that regulators should consider applying to AI: safety, security and robustness; appropriate transparency and explainability; fairness; accountability and governance; contestability and redress. These principles are intended to guide regulators in applying existing laws and powers to AI, rather than creating new statutory requirements at this stage.");
        doc.AppendParagraph("International context: the Government recognises the global dimension of AI development and deployment. The United Kingdom will continue to engage with international partners through the OECD AI Policy Observatory, the Global Partnership on AI, and bilateral channels, and will seek mutual recognition arrangements for AI conformity assessments where appropriate to facilitate cross-border data flows and AI system deployment.");
        doc.AppendParagraph("Regulatory sandboxes and innovation hubs: the Government will support regulators in establishing innovation-friendly environments. Building on the success of the FCA's regulatory sandbox (which has supported over 500 firms since 2016), AI-specific sandboxes will enable developers to test systems in controlled environments with regulatory oversight, accelerating safe deployment while maintaining consumer and societal protections.");
        doc.AppendParagraph("Mandatory incident reporting: the Government will consult on requirements for providers of high-risk AI systems in critical national infrastructure to report significant AI incidents to the AI Safety Institute. This builds on the AI Safety Institute's foundation model evaluation programme, which has assessed systems from frontier AI developers including OpenAI, Anthropic, Google DeepMind, and Meta.");
        doc.AppendParagraph("Frontier AI governance: following the Bletchley Declaration signed by 28 countries at the AI Safety Summit in November 2023, the Government will work with international partners to develop shared evaluation methodologies for frontier AI systems, building on the work of the AI Safety Institute established under the Department for Science, Innovation and Technology.");
        doc.AppendParagraph("Implementation timeline: the central functions will be established by April 2025. Regulatory guidance will be published by sector regulators by September 2025. A statutory duty to consider AI principles will be evaluated at the 12-month review point, with the option to introduce legislation if voluntary approaches prove insufficient.");
        doc.AppendParagraph("Economic impact assessment: the Government's independent analysis, conducted by the Office for AI in collaboration with the Frontier AI Taskforce, estimates the framework will unlock £1.2 billion in additional AI investment over the 2025-2030 period by providing regulatory certainty for AI developers and deployers, compared to a counterfactual of fragmented sector-specific interventions.");

        Assert.Equal(9, doc.GetParagraphCount());

        // GetCharacterCount
        var charCount = doc.GetCharacterCount();
        Assert.True(charCount > 0);
        Assert.Equal(charCount, doc.GetCharacterCount()); // consistent
        Assert.Equal(doc.GetCharCount(), charCount);

        // GetWordFrequency — key policy terms should appear multiple times
        var freqAI = doc.GetWordFrequency("AI");
        Assert.True(freqAI > 0);
        Assert.Equal(freqAI, doc.GetWordFrequency("AI")); // consistent

        var freqRegulation = doc.GetWordFrequency("regulation");
        Assert.True(freqRegulation > 0);

        var freqGovernment = doc.GetWordFrequency("Government");
        Assert.True(freqGovernment > 0);

        var freqRegulators = doc.GetWordFrequency("regulators");
        Assert.True(freqRegulators >= 0);

        var freqSafety = doc.GetWordFrequency("safety");
        Assert.True(freqSafety >= 0);

        // Absent words
        Assert.Equal(0, doc.GetWordFrequency("xyzabsent99999"));
        Assert.Equal(0, doc.GetWordFrequency("randomnonexistentterm"));

        // Paragraph count unchanged after frequency queries
        Assert.Equal(9, doc.GetParagraphCount());

        // Word count positive
        Assert.True(doc.GetWordCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile
        var path = TempFile("dogfood_ai_white_paper.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(charCount, loaded.GetCharacterCount());
        Assert.Equal(freqAI, loaded.GetWordFrequency("AI"));
        Assert.Equal(freqGovernment, loaded.GetWordFrequency("Government"));
        Assert.Equal(9, loaded.GetParagraphCount());

        // AppendParagraph on loaded — increases char count
        loaded.AppendParagraph("Review and evaluation: the Secretary of State for Science, Innovation and Technology will commission a comprehensive review of the framework's effectiveness at the 18-month point, including an independent assessment of whether sector regulators have implemented the AI principles consistently and whether novel risks have emerged from frontier AI systems that require additional governance measures.");
        Assert.True(loaded.GetCharacterCount() > charCount);
        Assert.True(loaded.GetWordFrequency("AI") >= freqAI); // more AI mentions
        Assert.Equal(10, loaded.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_ai_white_paper_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.True(loaded2.GetCharacterCount() > charCount);
        Assert.True(loaded2.GetWordFrequency("AI") > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetWordFrequency("Secretary"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
