// Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R348

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R348: Tests for FodtDocument.GetFootnoteCount, AddFootnote, GetFootnoteText deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// AddFootnote(paragraphIndex, text): inserts a footnote anchor at the given paragraph.
/// GetFootnoteText(index): returns the text of the footnote at the given index.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount consistent;
/// GetFootnoteCount zero for new doc; GetFootnoteCount after AddFootnote increases;
/// GetFootnoteCount save-load;
/// AddFootnote no-throw; AddFootnote increases count; AddFootnote save-load;
/// AddFootnote multiple; AddFootnote then ExportToHtml no-throw;
/// AddFootnote then ExportToMarkdown no-throw; AddFootnote then GetWordCount positive;
/// GetFootnoteText no-throw; GetFootnoteText non-null; GetFootnoteText consistent;
/// GetFootnoteText save-load;
/// dogfood CreateDoc→AddFootnote→GetFootnoteCount→GetFootnoteText→SaveToFile pipeline.
/// </summary>
public class FodtR348GetFootnoteCountAndAddFootnoteDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR348GetFootnoteCountAndAddFootnoteDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR348_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Monetary Policy Transmission in Open Economies: Exchange Rate Channels and Spillover Effects in Emerging Market Economies", 1);
        doc.AppendParagraph("This paper examines the transmission of monetary policy shocks in emerging market economies (EMEs) with particular attention to the exchange rate channel and cross-border spillover effects from advanced economy central banks, using a panel vector autoregression (PVAR) framework estimated on quarterly data for 28 EMEs over 2000-2023.");
        doc.AppendParagraph("The identification strategy follows Cholesky decomposition of the structural VAR, with ordering informed by the recursive identification scheme of Christiano, Eichenbaum and Evans (1999), adapted for the open economy setting proposed by Kim and Roubini (2000).");
        doc.InsertHeading(3, "Data and Methodology", 2);
        doc.AppendParagraph("The dataset comprises quarterly observations for real GDP growth, CPI inflation, short-term nominal interest rates, nominal effective exchange rates (NEER), current account balances, and foreign exchange reserves for 28 EMEs from the IMF International Financial Statistics and World Bank World Development Indicators databases.");
        doc.AppendParagraph("The PVAR specification includes four lags selected by the Akaike Information Criterion, and country-fixed effects are removed using the Helmert procedure (forward mean differencing) to avoid Nickell bias in dynamic panel estimation.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no footnotes.");
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_AfterAddFootnote_Increases()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(1, "Christiano, L., Eichenbaum, M. and Evans, C. (1999). Monetary policy shocks: What have we learned and to what end? Handbook of Macroeconomics, 1A, pp.65-148.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(2, "Kim, S. and Roubini, N. (2000). Exchange rate anomalies in the industrial countries: A solution with a structural VAR approach. Journal of Monetary Economics, 45(3), pp.561-586.");
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
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.AddFootnote(0, "Data sourced from IMF IFS (accessed January 2024)."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Increases_Count()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(3, "Helmert procedure: see Arellano and Bover (1995). Another look at the instrumental variable estimation of error-components models. Journal of Econometrics, 68(1), pp.29-51.");
        Assert.Equal(before + 1, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_SaveLoad_Persists()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(4, "AIC lag selection: four-quarter lag length consistent with monetary policy transmission literature.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("afn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Multiple()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(0, "Footnote 1.");
        doc.AddFootnote(1, "Footnote 2.");
        doc.AddFootnote(3, "Footnote 3.");
        Assert.Equal(3, doc.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(2, "HTML footnote — see supplementary material.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(1, "Markdown footnote — data available on request.");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddFootnote_Then_GetWordCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(0, "Word count footnote — includes all sections.");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetFootnoteText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteText_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(1, "Text retrieval footnote.");
        var ex = Record.Exception(() => doc.GetFootnoteText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteText_NonNull()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(2, "Non-null footnote.");
        Assert.NotNull(doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(0, "Consistent footnote text.");
        Assert.Equal(doc.GetFootnoteText(0), doc.GetFootnoteText(0));
    }

    [Fact]
    public void GetFootnoteText_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddFootnote(3, "Save-load footnote.");
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
        // Legal academic — law review article on the EU AI Act regulatory framework
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Regulatory Architecture of the EU Artificial Intelligence Act: Conformity Assessment, Fundamental Rights Impact Assessment, and Enforcement Mechanisms under Regulation (EU) 2024/1689", 1);
        doc.AppendParagraph("The Artificial Intelligence Act (AIA), formally published as Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024, establishes a comprehensive risk-based regulatory framework for artificial intelligence systems placed on the EU market or put into service within the Union, constituting the world's first legally binding general-purpose regulation of AI systems.");
        doc.AppendParagraph("The Act creates a tripartite classification of AI systems: prohibited systems under Article 5 (e.g., social scoring by public authorities, subliminal manipulation), high-risk systems enumerated in Annexes II and III (e.g., biometric identification, critical infrastructure management, employment decision-making), and general-purpose AI models as defined in Article 3(63).");

        doc.InsertHeading(3, "Conformity Assessment Obligations", 2);
        doc.AppendParagraph("High-risk AI systems listed in Annex II (systems covered by existing product safety legislation) must follow the conformity assessment procedures specified in that legislation, as modified by Article 43(1). Systems listed in Annex III must undergo conformity assessment under Article 43(2), either by internal control (Annex VI) or third-party assessment by a notified body (Annex VII).");
        doc.AppendParagraph("Article 9 imposes a risk management system obligation on providers of high-risk AI systems, requiring continuous iterative risk identification, analysis, and mitigation throughout the system lifecycle. The risk management system must be documented and updated, and must address risks to health, safety, and fundamental rights identified by the provider and by users.");

        doc.InsertHeading(6, "Fundamental Rights Impact Assessment", 2);
        doc.AppendParagraph("Article 27 requires public bodies and private entities providing public services to conduct a Fundamental Rights Impact Assessment (FRIA) before deploying a high-risk AI system listed in Annex III. The FRIA must assess the system's potential impact on fundamental rights as guaranteed by the EU Charter, including non-discrimination, data protection, freedom of expression, and the right to an effective remedy.");
        doc.AppendParagraph("The FRIA obligation does not apply to AI systems used exclusively for military, national security, or scientific research purposes under Article 2(3) and (6). The Commission has published a template FRIA under Article 27(5), though this template remains non-binding guidance rather than a mandatory format.");

        doc.InsertHeading(9, "Enforcement and Penalties", 1);
        doc.AppendParagraph("Article 99 establishes administrative penalties of up to €35 million or 7% of global annual turnover for violations of the prohibited practices under Article 5, and up to €15 million or 3% of global annual turnover for violations of other AIA obligations. The competent authorities responsible for enforcement are designated by Member States under Article 70.");
        doc.AppendParagraph("The European AI Office, established within the Commission under Decision C(2024) 1831, exercises supervisory authority over general-purpose AI model providers, with the power to conduct evaluations, request information, impose remedial actions, and refer cases to national authorities for penalties under Article 101.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetFootnoteCount());

        // AddFootnote — legal citations and cross-references
        doc.AddFootnote(1, "Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence [2024] OJ L 2024/1689. The Act entered into force on 2 August 2024 and applies from 2 August 2026 (with some exceptions applying earlier under Article 113).");
        Assert.Equal(1, doc.GetFootnoteCount());

        doc.AddFootnote(2, "The concept of 'general-purpose AI model' under Article 3(63) captures foundation models trained on large datasets capable of performing a wide range of tasks. The specific obligations for GPAI model providers with 'systemic risk' are set out in Articles 51-55.");
        Assert.Equal(2, doc.GetFootnoteCount());

        doc.AddFootnote(3, "Annex II lists product safety legislation whose conformity assessment procedures are modified by Article 43(1), including the Machinery Regulation (EU) 2023/1230, the Medical Devices Regulation (EU) 2017/745, and the Artificial Intelligence Act itself for embedded systems.");
        Assert.Equal(3, doc.GetFootnoteCount());

        doc.AddFootnote(5, "The risk management system under Article 9 must specifically address reasonably foreseeable misuse of the AI system, as well as risks arising from interactions between the system and the environment in which it is used. See Recital 61 for the Commission's guidance on iterative risk assessment.");
        Assert.Equal(4, doc.GetFootnoteCount());

        doc.AddFootnote(7, "The FRIA under Article 27 is procedurally distinct from the Data Protection Impact Assessment (DPIA) required under Article 35 GDPR. Where both are required, Article 27(4) AIA allows for a combined assessment provided all requirements of both instruments are met. See European Data Protection Board, Guidelines 05/2022.");
        Assert.Equal(5, doc.GetFootnoteCount());

        doc.AddFootnote(9, "The administrative penalties in Article 99 must be read alongside Article 101 (penalties for providers of general-purpose AI models), Article 100 (penalties for Member States for incorrect designation of notified bodies), and Article 102 (penalties for individuals and third-country entities). For SME provisions, see Article 99(9).");
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

        // GetWordCount positive
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_eu_ai_act_law_review.fodt");
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
        loaded.AddFootnote(8, "The European AI Office (EAIO), established by Commission Decision C(2024) 1831 of 21 February 2024, is headed by the AI Office Director. As of June 2024, the EAIO had initiated its first model evaluation programme targeting frontier GPAI models under Article 55.");
        Assert.Equal(7, loaded.GetFootnoteCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the EU AI Act introduces a comprehensive risk-based regulatory regime for artificial intelligence that imposes significant compliance obligations on providers and deployers of high-risk AI systems. The conformity assessment, FRIA, and risk management system requirements collectively constitute a novel form of pre-market AI governance with no clear precedent in European product regulation.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_eu_ai_act_law_review_v2.fodt");
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
