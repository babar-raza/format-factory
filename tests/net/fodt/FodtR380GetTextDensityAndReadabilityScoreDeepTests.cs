// Tests for FodtDocument.GetTextDensity, GetReadabilityScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R380

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R380: Tests for FodtDocument.GetTextDensity, GetReadabilityScore deeper.
/// GetTextDensity(): returns average characters per paragraph (total chars / paragraph count).
/// GetReadabilityScore(): returns a readability metric (e.g. Flesch-Kincaid or similar); higher = more readable.
/// Covers: GetTextDensity no-throw; GetTextDensity non-negative; GetTextDensity consistent;
/// GetTextDensity save-load; GetTextDensity increases after AppendParagraph;
/// GetReadabilityScore no-throw; GetReadabilityScore non-negative; GetReadabilityScore consistent;
/// GetReadabilityScore save-load; GetReadabilityScore in reasonable range;
/// dogfood CreateDoc→GetTextDensity→GetReadabilityScore→SaveToFile pipeline.
/// </summary>
public class FodtR380GetTextDensityAndReadabilityScoreDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR380GetTextDensityAndReadabilityScoreDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR380_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateDenseDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Technical Specification", 1);
        doc.AppendParagraph("This specification sets out the detailed technical requirements for the implementation of a distributed ledger-based transaction processing system, incorporating cryptographic authentication protocols, asynchronous message queuing, and real-time audit trail generation for regulatory compliance purposes.");
        doc.AppendParagraph("The system architecture shall conform to the principles of defence-in-depth security, applying multiple independent layers of access control, input validation, anomaly detection, and cryptographic verification to ensure that no single point of failure can compromise the integrity of transaction records.");
        doc.AppendParagraph("Performance requirements mandate that the system shall sustain throughput of not less than ten thousand transactions per second at peak load, with end-to-end processing latency not exceeding fifty milliseconds at the ninety-ninth percentile under conditions representative of maximum anticipated operational demand.");
        return doc;
    }

    private static FodtDocument CreateSimpleDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Summary", 1);
        doc.AppendParagraph("The cat sat on the mat.");
        doc.AppendParagraph("The dog ran fast.");
        doc.AppendParagraph("She read the book.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTextDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextDensity_NoThrow()
    {
        var doc = CreateDenseDoc();
        var ex = Record.Exception(() => doc.GetTextDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextDensity_NonNegative()
    {
        var doc = CreateDenseDoc();
        Assert.True(doc.GetTextDensity() >= 0.0);
    }

    [Fact]
    public void GetTextDensity_Consistent()
    {
        var doc = CreateDenseDoc();
        Assert.Equal(doc.GetTextDensity(), doc.GetTextDensity());
    }

    [Fact]
    public void GetTextDensity_SaveLoad_Consistent()
    {
        var doc = CreateDenseDoc();
        var before = doc.GetTextDensity();
        var path = TempFile("td_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTextDensity(), precision: 6);
    }

    [Fact]
    public void GetTextDensity_Increases_After_AppendParagraph()
    {
        var doc = CreateSimpleDoc();
        var before = doc.GetTextDensity();
        // Append a much longer paragraph to push average up
        doc.AppendParagraph("This is a significantly longer paragraph containing many more words and characters than the previous short sentences, which will substantially increase the average character density per paragraph when recalculated.");
        var after = doc.GetTextDensity();
        Assert.True(after > before);
    }

    // -------------------------------------------------------------------------
    // GetReadabilityScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetReadabilityScore_NoThrow()
    {
        var doc = CreateSimpleDoc();
        var ex = Record.Exception(() => doc.GetReadabilityScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetReadabilityScore_NonNegative()
    {
        var doc = CreateSimpleDoc();
        Assert.True(doc.GetReadabilityScore() >= 0.0);
    }

    [Fact]
    public void GetReadabilityScore_Consistent()
    {
        var doc = CreateDenseDoc();
        Assert.Equal(doc.GetReadabilityScore(), doc.GetReadabilityScore());
    }

    [Fact]
    public void GetReadabilityScore_SaveLoad_Consistent()
    {
        var doc = CreateDenseDoc();
        var before = doc.GetReadabilityScore();
        var path = TempFile("rs_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetReadabilityScore(), precision: 6);
    }

    [Fact]
    public void GetReadabilityScore_InReasonableRange()
    {
        var doc = CreateSimpleDoc();
        var score = doc.GetReadabilityScore();
        // Flesch-Kincaid Reading Ease: 0–100 (higher = simpler). Allow [-10, 120] for edge cases.
        Assert.True(score >= -10.0 && score <= 120.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTextDensity_GetReadabilityScore_SaveToFile_Pipeline()
    {
        // Legal — UK Law Commission: Law Reform Report Draft
        // Commissioned report on Automated Legal Processes and Digital Identity
        // Text density and readability analysis for accessibility compliance (Plain English Campaign)

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Law Commission Report: Automated Legal Processes — Consultation Paper", 1);
        doc.AppendParagraph("This Consultation Paper is published by the Law Commission of England and Wales pursuant to its Thirteenth Programme of Law Reform. The Commission invites responses from interested parties by 30 September 2025.");

        var densityAfterIntro = doc.GetTextDensity();
        Assert.True(densityAfterIntro >= 0.0);
        var readabilityAfterIntro = doc.GetReadabilityScore();
        Assert.True(readabilityAfterIntro >= -10.0);

        // Part 1: Plain English summary (high readability, lower density)
        doc.InsertSection("Part 1: Executive Summary");
        doc.InsertHeading(3, "1. What is this about?", 2);
        doc.AppendParagraph("This paper asks whether the law should change to make it easier to use computers to do legal work.");
        doc.AppendParagraph("At the moment, many legal rules assume a human being is doing the work. We ask if this needs to change.");
        doc.AppendParagraph("We also look at digital identity — how people prove who they are online when signing contracts.");
        doc.AppendParagraph("We want to hear what you think. This is your chance to help shape the law.");

        var densityAfterSummary = doc.GetTextDensity();
        Assert.True(densityAfterSummary >= 0.0);
        var readabilityAfterSummary = doc.GetReadabilityScore();
        Assert.True(readabilityAfterSummary >= -10.0);
        Assert.Equal(doc.GetTextDensity(), doc.GetTextDensity()); // consistent

        // Part 2: Technical legal analysis (lower readability, higher density)
        doc.InsertSection("Part 2: The Legal Framework");
        doc.InsertHeading(3, "2. Current Statutory Provisions", 2);
        doc.AppendParagraph("The Electronic Communications Act 2000, as amended by the Electronic Identification and Trust Services for Electronic Transactions Regulations 2016 (SI 2016/696), provides the primary statutory framework governing electronic signatures and digital authentication mechanisms in commercial and legal transactions under English law.");
        doc.AppendParagraph("Section 7 of the Electronic Communications Act 2000 confers evidential weight on electronic signatures where: (a) the electronic signature is incorporated into or logically associated with the electronic communication; (b) the electronic signature is certified by an appropriate certificate; and (c) the certification service provider issuing that certificate meets such requirements as may be prescribed by the Secretary of State.");
        doc.AppendParagraph("The Law of Property (Miscellaneous Provisions) Act 1989, section 2, requires that contracts for the sale or other disposition of an interest in land must be made in writing, signed by or on behalf of each party, and must incorporate all the terms which the parties have expressly agreed. The courts have not yet definitively resolved whether a digital signature satisfies this requirement in all circumstances.");
        doc.AppendParagraph("Regulation (EU) 910/2014 (eIDAS Regulation) ceased to have direct effect in the United Kingdom upon the expiry of the transition period on 31 December 2020. The Electronic Identification and Trust Services for Electronic Transactions Regulations 2016 remain operative as retained EU law as modified by the Electronic Identification and Trust Services for Electronic Transactions (Amendment etc.) (EU Exit) Regulations 2019 (SI 2019/89).");

        var densityAfterLegal = doc.GetTextDensity();
        Assert.True(densityAfterLegal >= 0.0);
        var readabilityAfterLegal = doc.GetReadabilityScore();
        Assert.True(readabilityAfterLegal >= -10.0);

        // Part 3: Mixed — recommendations in plain English
        doc.InsertSection("Part 3: Provisional Proposals");
        doc.InsertHeading(3, "3. Proposal 1 — Recognise Automated Decision-Making", 2);
        doc.AppendParagraph("We propose that the law should clearly say that a contract can be formed by a computer program, without a human pressing a button at the moment of formation.");
        doc.AppendParagraph("This would mean businesses could use software to buy and sell goods automatically, and those contracts would be legally binding.");

        doc.InsertHeading(3, "4. Proposal 2 — Digital Identity Framework", 2);
        doc.AppendParagraph("We provisionally propose the enactment of primary legislation establishing a statutory framework for digital identity verification services, conferring on the Secretary of State powers to designate approved identity providers and prescribe minimum standards for identity verification, authentication, and fraud prevention consistent with international standards including ISO/IEC 29115:2013.");
        doc.AppendParagraph("The framework should impose proportionality requirements ensuring that the level of identity assurance demanded is commensurate with the transaction risk, and should provide a safe harbour for relying parties who act in good faith on a certified digital identity verification in specified categories of high-risk transaction.");

        var finalDensity = doc.GetTextDensity();
        Assert.True(finalDensity >= 0.0);
        var finalReadability = doc.GetReadabilityScore();
        Assert.True(finalReadability >= -10.0);
        Assert.Equal(finalDensity, doc.GetTextDensity()); // consistent
        Assert.Equal(finalReadability, doc.GetReadabilityScore()); // consistent

        // Basic content assertions
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetSectionCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile
        var path1 = TempFile("dogfood_law_commission_consultation.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify text metrics preserved
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(finalDensity, loaded.GetTextDensity(), precision: 6);
        Assert.Equal(finalReadability, loaded.GetReadabilityScore(), precision: 6);
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());

        // Extend with responses section
        loaded.InsertSection("Part 4: How to Respond");
        loaded.InsertHeading(3, "5. Responding to this Consultation", 2);
        loaded.AppendParagraph("Please send your response to lawcom@lawcommission.gov.uk by 30 September 2025.");
        loaded.AppendParagraph("You can also respond via our online portal at www.lawcom.gov.uk/automated-legal-processes.");
        loaded.AppendParagraph("If you want to discuss your response, please contact the project team.");

        var densityAfterExtension = loaded.GetTextDensity();
        Assert.True(densityAfterExtension >= 0.0);
        Assert.True(loaded.GetReadabilityScore() >= -10.0);
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_law_commission_consultation_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(densityAfterExtension, final.GetTextDensity(), precision: 6);
        Assert.Equal(loaded.GetReadabilityScore(), final.GetReadabilityScore(), precision: 6);

        Assert.True(final.GetWordCount() > doc.GetWordCount());
        Assert.True(final.GetSectionCount() >= doc.GetSectionCount());

        var ex1 = Record.Exception(() => final.GetTextDensity());
        var ex2 = Record.Exception(() => final.GetReadabilityScore());
        var ex3 = Record.Exception(() => final.ExportToHtml());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
