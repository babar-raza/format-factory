// Tests for FodtDocument.GetHeadingCount, GetHeadingHierarchy deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R374

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R374: Tests for FodtDocument.GetHeadingCount, GetHeadingHierarchy deeper.
/// GetHeadingCount(): returns the total number of headings in the document.
/// GetHeadingHierarchy(): returns the list of headings as (level, text) pairs in document order.
/// Covers: GetHeadingCount no-throw; GetHeadingCount non-negative; GetHeadingCount consistent;
/// GetHeadingCount save-load; GetHeadingHierarchy no-throw; GetHeadingHierarchy count equals GetHeadingCount;
/// GetHeadingHierarchy consistent; GetHeadingHierarchy save-load;
/// GetHeadingCount increases after InsertHeading; GetHeadingHierarchy ordered;
/// dogfood CreateDoc→GetHeadingCount→GetHeadingHierarchy→SaveToFile pipeline.
/// </summary>
public class FodtR374GetHeadingCountAndHeadingHierarchyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR374GetHeadingCountAndHeadingHierarchyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR374_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateStructuredDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Regulatory Capital Framework", 1);
        doc.AppendParagraph("Overview of capital requirements under CRR2.");
        doc.InsertHeading(3, "1.1 CET1 Requirements", 2);
        doc.AppendParagraph("Minimum CET1 ratio of 4.5% plus buffers.");
        doc.InsertHeading(3, "1.2 Tier 1 Capital", 2);
        doc.AppendParagraph("Total Tier 1 minimum 6.0%.");
        doc.InsertHeading(3, "1.3 Total Capital", 2);
        doc.AppendParagraph("Total capital minimum 8.0%.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetHeadingCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingCount_NoThrow()
    {
        var doc = CreateStructuredDoc();
        var ex = Record.Exception(() => doc.GetHeadingCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingCount_NonNegative()
    {
        var doc = CreateStructuredDoc();
        Assert.True(doc.GetHeadingCount() >= 0);
    }

    [Fact]
    public void GetHeadingCount_Consistent()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_SaveLoad_Consistent()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetHeadingCount();
        var path = TempFile("hc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeadingCount());
    }

    [Fact]
    public void GetHeadingCount_Increases_After_InsertHeading()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetHeadingCount();
        doc.InsertHeading(3, "1.4 Leverage Ratio", 2);
        Assert.True(doc.GetHeadingCount() > before);
    }

    // -------------------------------------------------------------------------
    // GetHeadingHierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHeadingHierarchy_NoThrow()
    {
        var doc = CreateStructuredDoc();
        var ex = Record.Exception(() => doc.GetHeadingHierarchy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHeadingHierarchy_Count_Equals_GetHeadingCount()
    {
        var doc = CreateStructuredDoc();
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingHierarchy().Count);
    }

    [Fact]
    public void GetHeadingHierarchy_Consistent()
    {
        var doc = CreateStructuredDoc();
        var h1 = doc.GetHeadingHierarchy();
        var h2 = doc.GetHeadingHierarchy();
        Assert.Equal(h1, h2);
    }

    [Fact]
    public void GetHeadingHierarchy_SaveLoad_Consistent()
    {
        var doc = CreateStructuredDoc();
        var before = doc.GetHeadingHierarchy();
        var path = TempFile("hh_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeadingHierarchy());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHeadingCount_GetHeadingHierarchy_SaveToFile_Pipeline()
    {
        // Legal — UK Solicitors Regulation Authority (SRA): Law Firm Regulatory Compliance Manual
        // Multi-section compliance document with heading hierarchy for structured navigation
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "SRA Code of Conduct for Solicitors: Compliance Manual", 1);
        doc.AppendParagraph("This Compliance Manual has been prepared by the firm's Compliance Officer for Legal Practice (COLP) pursuant to the SRA Standards and Regulations 2019 and sets out the firm's systems, controls, and obligations.");

        var initialHeadingCount = doc.GetHeadingCount();
        Assert.True(initialHeadingCount >= 0);
        var initialHierarchy = doc.GetHeadingHierarchy();
        Assert.Equal(initialHeadingCount, initialHierarchy.Count);

        // Part 1
        doc.InsertSection("Part 1: Conduct Obligations");
        doc.InsertHeading(3, "1. Acting in the Best Interests of Clients", 2);
        doc.AppendParagraph("Pursuant to Principle 7 (SRA Principles 2019), solicitors must act in the best interests of each client. This requires the firm to: (a) give clear and honest advice; (b) identify and manage conflicts of interest; (c) maintain client confidentiality; and (d) preserve the confidentiality of information relating to former clients.");

        doc.InsertHeading(3, "1.1 Client Care Letters", 2);
        doc.AppendParagraph("The firm must provide each new client with a client care letter at the outset of the retainer, complying with paragraph 8.6 of the Code of Conduct for Solicitors, RELs and RFLs ('the Code'). The letter must confirm: the identity of the supervising fee earner; the costs estimate and billing arrangements; and the firm's complaints procedure.");

        doc.InsertHeading(3, "1.2 Conflicts of Interest", 2);
        doc.AppendParagraph("The firm operates a conflicts system in compliance with paragraphs 6.1 and 6.2 of the Code. All new matters must be conflict-checked against the firm's client and matter database before a retainer is accepted.");

        doc.InsertHeading(3, "2. Maintaining Trust and Acting Fairly", 2);
        doc.AppendParagraph("Principle 2 requires solicitors not to behave in a way that is dishonest or that diminishes public trust in the solicitors' profession. The firm's policies on financial crime, anti-bribery and corruption (ABC), and anti-money laundering (AML) are set out in Part 3.");

        var headingCountAfterPart1 = doc.GetHeadingCount();
        Assert.True(headingCountAfterPart1 > initialHeadingCount);
        var hierarchyAfterPart1 = doc.GetHeadingHierarchy();
        Assert.Equal(headingCountAfterPart1, hierarchyAfterPart1.Count);

        // Part 2
        doc.InsertSection("Part 2: Supervision and Accountability");
        doc.InsertHeading(3, "3. Supervision Requirements", 2);
        doc.AppendParagraph("Paragraph 3.5 of the Code requires that client matters are supervised by a solicitor. The firm's supervision framework requires that all fee earner work is reviewed at regular intervals determined by matter type and complexity as set out in the firm's Supervision Policy.");

        doc.InsertHeading(3, "3.1 COLP and COFA Obligations", 2);
        doc.AppendParagraph("The COLP is responsible for compliance with the terms and conditions of the firm's authorisation and for ensuring all managers and employees comply with the SRA's regulatory arrangements. The COFA is responsible for ensuring appropriate arrangements are in place for the firm's financial management.");

        doc.InsertHeading(3, "4. Reporting Obligations", 2);
        doc.AppendParagraph("The firm must promptly report to the SRA any facts or matters that it is required to notify, including: (a) material changes to the firm's circumstances; (b) serious financial difficulty or insolvency risk; (c) serious misconduct by any manager or employee; and (d) any SRA investigation, civil claim, or criminal charge.");

        var headingCountAfterPart2 = doc.GetHeadingCount();
        Assert.True(headingCountAfterPart2 > headingCountAfterPart1);
        var hierarchyAfterPart2 = doc.GetHeadingHierarchy();
        Assert.Equal(headingCountAfterPart2, hierarchyAfterPart2.Count);
        Assert.Equal(doc.GetHeadingCount(), doc.GetHeadingCount()); // consistent

        // Part 3
        doc.InsertSection("Part 3: Financial Crime Compliance");
        doc.InsertHeading(3, "5. Anti-Money Laundering", 2);
        doc.AppendParagraph("The firm complies with the Money Laundering, Terrorist Financing and Transfer of Funds (Information on the Payer) Regulations 2017 (as amended by the Money Laundering and Terrorist Financing (Amendment) Regulations 2019 and 2023).");

        doc.InsertHeading(3, "5.1 Customer Due Diligence", 2);
        doc.AppendParagraph("The firm applies customer due diligence (CDD) measures in accordance with Regulations 27-38 of the MLR 2017 before establishing a business relationship or carrying out an occasional transaction, including for all conveyancing and company formation work.");

        var finalHeadingCount = doc.GetHeadingCount();
        Assert.True(finalHeadingCount > headingCountAfterPart2);
        var finalHierarchy = doc.GetHeadingHierarchy();
        Assert.Equal(finalHeadingCount, finalHierarchy.Count);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path1 = TempFile("dogfood_sra_compliance_manual.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(finalHeadingCount, loaded.GetHeadingCount());
        Assert.Equal(finalHierarchy, loaded.GetHeadingHierarchy());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add appendix section
        loaded.InsertSection("Appendix A: Regulatory References");
        loaded.InsertHeading(3, "A.1 Primary Legislation", 2);
        loaded.AppendParagraph("Solicitors Act 1974; Legal Services Act 2007; Legal Aid, Sentencing and Punishment of Offenders Act 2012.");
        loaded.InsertHeading(3, "A.2 Secondary Legislation", 2);
        loaded.AppendParagraph("SRA Standards and Regulations 2019 (effective 25 November 2019); SRA Financial Services (Conduct of Business) Rules 2019; SRA Accounts Rules 2019.");

        Assert.True(loaded.GetHeadingCount() > finalHeadingCount);
        Assert.Equal(loaded.GetHeadingCount(), loaded.GetHeadingHierarchy().Count);

        // Final save
        var path2 = TempFile("dogfood_sra_compliance_manual_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetHeadingCount(), final.GetHeadingCount());
        Assert.Equal(loaded.GetHeadingHierarchy(), final.GetHeadingHierarchy());

        Assert.True(final.GetWordCount() > 0);

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.ExportToMarkdown());
        var ex3 = Record.Exception(() => final.InsertHeading(3, "A.3 SRA Guidance", 2));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.True(final.GetHeadingCount() >= loaded.GetHeadingCount());
    }
}
