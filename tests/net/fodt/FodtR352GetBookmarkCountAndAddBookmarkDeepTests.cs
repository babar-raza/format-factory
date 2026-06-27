// Tests for FodtDocument.GetBookmarkCount, AddBookmark deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R352

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R352: Tests for FodtDocument.GetBookmarkCount, AddBookmark deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(name, paragraphIndex): inserts a named bookmark at the given paragraph index.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load; AddBookmark no-throw; AddBookmark increases count;
/// AddBookmark multiple; AddBookmark save-load; AddBookmark then ExportToHtml no-throw;
/// AddBookmark then ExportToMarkdown no-throw; AddBookmark then GetWordCount positive;
/// AddBookmark then GetParagraphCount unchanged;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→SaveToFile pipeline.
/// </summary>
public class FodtR352GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR352GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR352_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateLongformDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Report and Accounts 2024: Sustainable Infrastructure Holdings PLC", 1);
        doc.AppendParagraph("Sustainable Infrastructure Holdings PLC is a UK-listed infrastructure investment company (FTSE 250) managing a diversified portfolio of renewable energy assets, transport infrastructure, and social infrastructure across the United Kingdom and Northern Europe.");
        doc.AppendParagraph("The Group's portfolio comprises 47 assets with a combined GAV of £3.2 billion, generating stable, long-duration cash flows underpinned by government-backed contracts and regulatory frameworks.");
        doc.InsertHeading(3, "Strategic Report", 2);
        doc.AppendParagraph("Portfolio performance in FY2024 exceeded expectations, with aggregate EBITDA of £287.4 million representing a 12.3% increase year-on-year, driven by operational improvements across the offshore wind portfolio and strong performance from the regulated water assets.");
        doc.AppendParagraph("The Board approved a final dividend of 6.8p per share for H2 2024, bringing the full-year dividend to 13.2p per share, in line with the progressive dividend policy targeting 3-5% annual growth.");
        doc.InsertHeading(6, "Governance Report", 2);
        doc.AppendParagraph("The Board comprises nine directors — four executive directors and five independent non-executive directors — providing robust governance oversight in compliance with the 2018 UK Corporate Governance Code (FRC).");
        doc.AppendParagraph("Board effectiveness review conducted by Lintstock Ltd (external facilitator) concluded the Board operates effectively with appropriate mix of skills, experience, and diversity.");
        doc.InsertHeading(9, "Financial Statements", 1);
        doc.AppendParagraph("The consolidated financial statements have been prepared in accordance with UK-adopted International Accounting Standards (UK-IAS) and applicable law. The financial year covers the 12 months to 31 December 2024.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateLongformDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateLongformDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateLongformDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A paragraph with no bookmarks.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateLongformDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("StrategicReport", 2);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("FinancialStatements", 5);
        var before = doc.GetBookmarkCount();
        var path = TempFile("gbc_save.fodt");
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
        var doc = CreateLongformDoc();
        var ex = Record.Exception(() => doc.AddBookmark("TestBookmark", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_Count()
    {
        var doc = CreateLongformDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark("NavBookmark", 1);
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("BM_Executive", 0);
        doc.AddBookmark("BM_Strategy", 2);
        doc.AddBookmark("BM_Governance", 4);
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("PersistedBM", 1);
        var before = doc.GetBookmarkCount();
        var path = TempFile("ab_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("HtmlBookmark", 0);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("MdBookmark", 2);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetWordCount_Positive()
    {
        var doc = CreateLongformDoc();
        doc.AddBookmark("WCBookmark", 0);
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void AddBookmark_Then_GetParagraphCount_Unchanged()
    {
        var doc = CreateLongformDoc();
        var before = doc.GetParagraphCount();
        doc.AddBookmark("ParaCountBM", 1);
        Assert.Equal(before, doc.GetParagraphCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_SaveToFile_Pipeline()
    {
        // Legal — Litigation bundle: High Court judicial review proceedings
        // Claimant: Environmental Defence Alliance / Defendant: Secretary of State for Energy Security
        // Case: Judicial review of development consent for new gas peaking plant (NSIP)
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Judicial Review Bundle: R (Environmental Defence Alliance) v Secretary of State for Energy Security and Net Zero [2024] EWHC 3847 (Admin)", 1);
        doc.AppendParagraph("This bundle is prepared in accordance with CPR Part 54 and the Practice Direction — Administrative Court (Judicial Review). Index compiled by Thornton Fairweather LLP, solicitors for the Claimant.");
        doc.AppendParagraph("Hearing dates: 15-18 October 2024 before Mr Justice Cavendish-Murray. Estimate: 4 days. Location: Royal Courts of Justice, Strand, London WC2A 2LL. Judge's reading time estimate: 3 hours.");

        doc.InsertHeading(3, "Section A — Legal Framework", 2);
        doc.AppendParagraph("The Planning Act 2008 (as amended by the Infrastructure Act 2015) provides the statutory framework for Nationally Significant Infrastructure Projects (NSIPs). The relevant National Policy Statement is EN-1 (Overarching Energy) and EN-4 (Gas Supply Infrastructure and Gas and Oil Pipelines), designated under s.5 of the Planning Act 2008.");
        doc.AppendParagraph("The decision-maker exercised discretion under s.104(7) of the Planning Act 2008 (overriding important and relevant matter contrary to development plan policy). Claimant contends: (1) error of law in interpretation of s.104(7); (2) failure to take into account relevant considerations (net zero carbon budget pathway per Climate Change Act 2008, s.1); (3) procedural unfairness in pre-examination process.");

        doc.InsertHeading(6, "Section B — Statement of Facts", 2);
        doc.AppendParagraph("The Interested Party, Apex Power Ltd, applied to the Planning Inspectorate for a Development Consent Order (DCO) on 14 February 2023 for a 299 MW Open Cycle Gas Turbine (OCGT) peaking plant at Carrington Industrial Estate, Greater Manchester (NGC reference: DCO/2023/0042).");
        doc.AppendParagraph("The Examining Authority conducted the examination from April to October 2023 (six months). Written representations received: 847. Hearings held: 12. The ExA recommendation to the Secretary of State was to GRANT the DCO, subject to 47 requirements (Planning Act 2008, s.120 requirements).");
        doc.AppendParagraph("The Secretary of State issued the decision letter dated 22 April 2024 granting the DCO. The Claimant filed Claim Form on 20 June 2024 (within the 6-week statutory time limit under s.118(1) of the Planning Act 2008). Permission granted by Sir Philip Ainsworth QC sitting as a Deputy High Court Judge on 12 July 2024.");

        doc.InsertHeading(9, "Section C — Expert Evidence", 2);
        doc.AppendParagraph("Climate expert report: Professor Helena Marchetti (Professor of Climate Policy, LSE Grantham Research Institute). Expert opinion: the OCGT will emit approximately 142,000 tCO2e per annum at 50% load factor, inconsistent with the Sixth Carbon Budget pathway (CCC, 2020) requiring decarbonisation of electricity grid by 2035.");
        doc.AppendParagraph("Planning expert report: Mr Alistair Thornton-Davies FRTPI. Opinion: the Secretary of State failed to give adequate reasons for departing from the ExA's assessment of the cumulative impact of the development on the Mersey Estuary SSSI (Wildlife and Countryside Act 1981, s.28).");

        doc.InsertHeading(12, "Section D — Respondent's Evidence", 2);
        doc.AppendParagraph("The Secretary of State's response, filed per s.118(3)(b) PA 2008, asserts: (1) the decision is lawful having regard to EN-1 para 4.1.2 (gas peaking as transition technology); (2) net zero considerations were material considerations properly weighed; (3) the procedure complied with reg 5 of the Infrastructure Planning (Environmental Impact Assessment) Regulations 2017.");

        doc.InsertHeading(15, "Section E — Skeleton Arguments", 1);
        doc.AppendParagraph("Claimant's skeleton argument, settled by Rupert Cavendish-Lee KC and Amanda Whitmore-Singh of Chambers, argues three grounds of review. Ground 1 (error of law): Secretary of State applied wrong legal test under s.104(7). Ground 2 (relevancy): net zero obligations under Climate Change Act 2008 are mandatory relevant considerations. Ground 3 (procedural unfairness): pre-application consultation failed to meet procedural legitimate expectations.");
        doc.AppendParagraph("Secretary of State's skeleton argument, settled by Timothy Wren-Ashford KC, resists all three grounds. Concedes Ground 3 is 'not without difficulty' but submits the procedural error, if any, was not material (R v North and East Devon Health Authority, ex p Coughlan [2001] QB 213 applied).");

        Assert.Equal(10, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetBookmarkCount());

        // AddBookmark — cross-reference navigation bookmarks for judicial bundle
        doc.AddBookmark("BM_LegalFramework", 1);
        Assert.Equal(1, doc.GetBookmarkCount());

        doc.AddBookmark("BM_StatementOfFacts", 3);
        Assert.Equal(2, doc.GetBookmarkCount());

        doc.AddBookmark("BM_ExpertEvidence", 6);
        Assert.Equal(3, doc.GetBookmarkCount());

        doc.AddBookmark("BM_RespondentEvidence", 8);
        Assert.Equal(4, doc.GetBookmarkCount());

        doc.AddBookmark("BM_SkeletonArguments", 9);
        Assert.Equal(5, doc.GetBookmarkCount());

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());

        // Paragraph count unchanged
        Assert.Equal(10, doc.GetParagraphCount());

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
        var path = TempFile("dogfood_jr_bundle.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetBookmarkCount());
        Assert.Equal(10, loaded.GetParagraphCount());
        Assert.True(loaded.GetWordCount() > 0);

        // AddBookmark on loaded
        loaded.AddBookmark("BM_InterlocutoryOrders", 0);
        Assert.Equal(6, loaded.GetBookmarkCount());
        Assert.Equal(10, loaded.GetParagraphCount()); // still unchanged

        // AppendParagraph on loaded
        loaded.AppendParagraph("Order for costs: if the Claimant succeeds on any ground, costs to follow the event. Parties directed to file written submissions on costs within 14 days of judgment. Court of Appeal permission to appeal: dealt with in judgment.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_jr_bundle_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetBookmarkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddBookmark("BM_Final", 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
