// Tests for FodtDocument.GetFootnoteCount, GetEndnoteCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R376

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R376: Tests for FodtDocument.GetFootnoteCount, GetEndnoteCount deeper.
/// GetFootnoteCount(): returns the number of footnotes in the document.
/// GetEndnoteCount(): returns the number of endnotes in the document.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount consistent;
/// GetFootnoteCount save-load; GetEndnoteCount no-throw; GetEndnoteCount non-negative;
/// GetEndnoteCount consistent; GetEndnoteCount save-load;
/// AddFootnote then GetFootnoteCount increases; AddEndnote then GetEndnoteCount increases;
/// dogfood CreateDoc→AddFootnote→GetFootnoteCount→GetEndnoteCount→SaveToFile pipeline.
/// </summary>
public class FodtR376GetFootnoteCountAndEndnoteCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR376GetFootnoteCountAndEndnoteCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR376_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateLegalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Takeover Code: Practice Statement No. 31", 1);
        doc.AppendParagraph("This Practice Statement sets out the Panel Executive's approach to the application of Rule 2.7(c) of the City Code on Takeovers and Mergers (the 'Code') in circumstances where an offeror announces that it is considering making an offer.");
        doc.AppendParagraph("The Code is published and administered by the Panel on Takeovers and Mergers (the 'Panel'). The Panel is an independent body, established in 1968, whose main functions are to issue and administer the Code and to supervise and regulate takeovers and other matters to which the Code applies.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateLegalDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddFootnote("See Panel Statement 2023/3 for guidance on this point.");
        var before = doc.GetFootnoteCount();
        var path = TempFile("fc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    [Fact]
    public void AddFootnote_Then_GetFootnoteCount_Increases()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote("See Rule 2.6 of the Code for the definition of 'possible offer period'.");
        Assert.True(doc.GetFootnoteCount() > before);
    }

    // -------------------------------------------------------------------------
    // GetEndnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEndnoteCount_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetEndnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEndnoteCount_NonNegative()
    {
        var doc = CreateLegalDoc();
        Assert.True(doc.GetEndnoteCount() >= 0);
    }

    [Fact]
    public void GetEndnoteCount_Consistent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(doc.GetEndnoteCount(), doc.GetEndnoteCount());
    }

    [Fact]
    public void GetEndnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddEndnote("References: City Code on Takeovers and Mergers, 13th Edition (2022).");
        var before = doc.GetEndnoteCount();
        var path = TempFile("ec_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetEndnoteCount());
    }

    [Fact]
    public void AddEndnote_Then_GetEndnoteCount_Increases()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetEndnoteCount();
        doc.AddEndnote("See also the Panel's Statement 2021/1: 'Impact of COVID-19 on Offer Timetables'.");
        Assert.True(doc.GetEndnoteCount() > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFootnoteCount_GetEndnoteCount_SaveToFile_Pipeline()
    {
        // Legal — Slaughter and May: Competition Law Advisory Opinion
        // Multi-section advice with footnoted statutory references and endnoted case law
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Competition Act 1998: Chapter II Prohibition — Dominance Analysis", 1);
        doc.AppendParagraph("This opinion has been prepared by Slaughter and May on behalf of Nexus Digital Infrastructure Limited ('Nexus') in connection with its proposed acquisition of behavioural analytics from DataStream Analytics plc ('DataStream').");
        doc.AppendParagraph("The purpose of this opinion is to assess whether Nexus holds a dominant position within the meaning of the Competition Act 1998 ('the Act') and, if so, whether the proposed data acquisition would constitute an abuse of that dominant position.");

        var initialFn = doc.GetFootnoteCount();
        var initialEn = doc.GetEndnoteCount();
        Assert.True(initialFn >= 0);
        Assert.True(initialEn >= 0);

        doc.InsertSection("1. Legal Framework");
        doc.InsertHeading(3, "1.1 The Chapter II Prohibition", 2);
        doc.AppendParagraph("Section 18(1) of the Act prohibits any conduct on the part of one or more undertakings which amounts to the abuse of a dominant position in a market if it may affect trade within the United Kingdom.");
        doc.AddFootnote("Section 18 CA 1998, as amended by the Enterprise Act 2002 and the Digital Markets, Competition and Consumers Act 2024.");
        doc.AddFootnote("For the purposes of s.18, 'dominant position' has the same meaning as in Article 102 TFEU: Case 27/76 United Brands v Commission [1978] ECR 207, para 65.");

        var fnAfter1 = doc.GetFootnoteCount();
        Assert.True(fnAfter1 > initialFn);
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount()); // consistent

        doc.InsertHeading(3, "1.2 Market Definition", 2);
        doc.AppendParagraph("The relevant market for dominance assessment comprises both a relevant product market and a relevant geographic market. The Commission's Notice on Market Definition (OJ C 372, 9.12.1997, p. 5) provides guidance on the methodology.");
        doc.AddFootnote("Commission Notice on the definition of the relevant market, OJ C 372, 9.12.1997. See also CMA's Guidance on Market Definition (CMA56, 2017).");

        doc.InsertSection("2. Dominance Assessment");
        doc.InsertHeading(3, "2.1 Market Shares", 2);
        doc.AppendParagraph("On the basis of the data provided, Nexus holds a market share of approximately 42% in the supply of broadband infrastructure services to enterprise customers in the United Kingdom. Market shares above 40% are generally regarded as prima facie evidence of dominance.");
        doc.AddFootnote("AKZO Nobel Chemicals v Commission, Case C-62/86 [1991] ECR I-3359: market share of 50%+ = dominant as a rule; 40-50% = rebuttable presumption.");

        doc.InsertHeading(3, "2.2 Barriers to Entry and Expansion", 2);
        doc.AppendParagraph("The CMA has consistently held that high sunk costs, network effects, and switching costs constitute significant barriers to entry in digital infrastructure markets. These factors, combined with Nexus's established customer relationships and proprietary network assets, reinforce the dominance finding.");

        var fnAfter2 = doc.GetFootnoteCount();
        Assert.True(fnAfter2 > fnAfter1);

        doc.InsertSection("3. Abuse Analysis");
        doc.InsertHeading(3, "3.1 Data Accumulation as Potential Abuse", 2);
        doc.AppendParagraph("The proposed acquisition of DataStream's behavioural analytics dataset may constitute an abuse of dominance under s.18(2)(a) (imposing unfair trading conditions) or s.18(2)(c) (limiting technical development to the prejudice of consumers), where the data would foreclose rivals' access to inputs necessary for effective competition.");

        // Endnotes for case law bibliography
        doc.AddEndnote("Google Shopping (Case AT.39740) Commission Decision C(2017) 4444 final; on appeal: Google LLC v European Commission, Case T-612/17 [2021] ECR.");
        doc.AddEndnote("Meta Platforms (Case AT.40684) Commission Decision C(2019) 1316; concerning data accumulation and self-preferencing in social networking.");
        doc.AddEndnote("CMA Decision (Case 50885), Experian Limited (2020): abuse of dominance in consumer credit reporting markets.");

        var enAfter1 = doc.GetEndnoteCount();
        Assert.True(enAfter1 > initialEn);
        Assert.Equal(doc.GetEndnoteCount(), doc.GetEndnoteCount()); // consistent

        // Content checks
        Assert.True(doc.GetWordCount() > 0);
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
        var path1 = TempFile("dogfood_competition_opinion.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(fnAfter2, loaded.GetFootnoteCount());
        Assert.Equal(enAfter1, loaded.GetEndnoteCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add more footnotes and endnotes
        loaded.InsertSection("4. Conclusion");
        loaded.InsertHeading(3, "4.1 Summary", 2);
        loaded.AppendParagraph("For the reasons set out in this opinion, we conclude that Nexus holds a dominant position in the relevant market and that the proposed data acquisition presents a material risk of constituting an abuse of that dominant position.");
        loaded.AddFootnote("This opinion is based on information provided as at the date of instruction and may require updating if material facts change.");
        loaded.AddEndnote("Bibliography: Competition Act 1998; Digital Markets, Competition and Consumers Act 2024; CMA Guidance: Abuse of a Dominant Position (OFT402, 2004).");

        Assert.True(loaded.GetFootnoteCount() > fnAfter2);
        Assert.True(loaded.GetEndnoteCount() > enAfter1);

        // Final save
        var path2 = TempFile("dogfood_competition_opinion_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetFootnoteCount(), final.GetFootnoteCount());
        Assert.Equal(loaded.GetEndnoteCount(), final.GetEndnoteCount());

        Assert.True(final.GetWordCount() > 0);

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.ExportToMarkdown());
        var ex3 = Record.Exception(() => final.AddFootnote("Additional authority: Generali v Commission, Case T-534/18."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.True(final.GetFootnoteCount() >= loaded.GetFootnoteCount());
    }
}
