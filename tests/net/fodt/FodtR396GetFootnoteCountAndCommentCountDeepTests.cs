// Tests for FodtDocument.GetFootnoteCount, GetCommentCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R396

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R396: Tests for FodtDocument.GetFootnoteCount, GetCommentCount deeper.
/// GetFootnoteCount(): returns the total number of footnotes in the document.
/// GetCommentCount(): returns the total number of comments/annotations in the document.
/// Covers: GetFootnoteCount no-throw; GetFootnoteCount non-negative; GetFootnoteCount zero for plain doc;
/// GetFootnoteCount consistent; GetFootnoteCount increases after AddFootnote;
/// GetFootnoteCount save-load; GetCommentCount no-throw; GetCommentCount non-negative;
/// GetCommentCount zero for plain doc; GetCommentCount consistent;
/// GetCommentCount increases after AddComment; GetCommentCount save-load; dogfood pipeline.
/// </summary>
public class FodtR396GetFootnoteCountAndCommentCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR396GetFootnoteCountAndCommentCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR396_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePlainDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Plain Document", 1);
        doc.AppendParagraph("This document contains only plain paragraphs without footnotes or comments.");
        doc.AppendParagraph("A second paragraph with more content to ensure the document is non-trivial.");
        return doc;
    }

    private static FodtDocument CreateFootnoteDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Document with Footnotes", 1);
        doc.AppendParagraph("The Economic Policy Institute defines poverty thresholds annually.");
        doc.AddFootnote(0, "EPI Poverty Threshold Report, 2024 edition, Table 3.");
        doc.AppendParagraph("GDP per capita is measured in constant 2015 US dollars.");
        doc.AddFootnote(1, "World Bank, World Development Indicators, accessed Q3 2024.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetFootnoteCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFootnoteCount_NoThrow()
    {
        var doc = CreateFootnoteDoc();
        var ex = Record.Exception(() => doc.GetFootnoteCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFootnoteCount_NonNegative()
    {
        var doc = CreateFootnoteDoc();
        Assert.True(doc.GetFootnoteCount() >= 0);
    }

    [Fact]
    public void GetFootnoteCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Consistent()
    {
        var doc = CreateFootnoteDoc();
        Assert.Equal(doc.GetFootnoteCount(), doc.GetFootnoteCount());
    }

    [Fact]
    public void GetFootnoteCount_Increases_After_AddFootnote()
    {
        var doc = CreateFootnoteDoc();
        var before = doc.GetFootnoteCount();
        doc.AddFootnote(2, "Additional source: ONS Statistical Bulletin, September 2024.");
        Assert.True(doc.GetFootnoteCount() > before);
    }

    [Fact]
    public void GetFootnoteCount_SaveLoad_Consistent()
    {
        var doc = CreateFootnoteDoc();
        var before = doc.GetFootnoteCount();
        var path = TempFile("fn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFootnoteCount());
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreatePlainDoc();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreatePlainDoc();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void GetCommentCount_Zero_ForPlainDoc()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(0, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreatePlainDoc();
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Increases_After_AddComment()
    {
        var doc = CreatePlainDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(0, "ReviewerA", "Please verify the GDP figures against ONS source.");
        Assert.True(doc.GetCommentCount() > before);
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreatePlainDoc();
        doc.AddComment(0, "Editor", "Check for consistency with prior year figures.");
        var before = doc.GetCommentCount();
        var path = TempFile("cm_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFootnoteCount_GetCommentCount_Pipeline()
    {
        // Academic — ESRC / UK Research and Innovation: Social Science Research Methodology Review
        // Annotated methodology chapter with peer review comments and citation footnotes
        // Footnote count tracks source density; comment count tracks review iteration depth

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Methodology Review — Cross-Sectional Survey Design in Social Science Research", 1);

        // Section 1: Study design overview (no footnotes yet)
        doc.InsertSection("Section 1: Study Design");
        doc.InsertHeading(1, "1.1 Population and Sampling Frame", 2);
        doc.AppendParagraph("The sampling frame for this study was drawn from the Office for National Statistics Integrated Household Survey, which covers approximately 340,000 adults annually across Great Britain.");
        doc.AppendParagraph("Stratified random sampling was employed to ensure adequate representation across income quintiles, geographic regions, and age cohorts.");

        var fn0 = doc.GetFootnoteCount();
        var cm0 = doc.GetCommentCount();
        Assert.Equal(0, fn0);
        Assert.Equal(0, cm0);

        // Section 2: Statistical methodology with footnotes
        doc.InsertSection("Section 2: Statistical Methodology");
        doc.InsertHeading(2, "2.1 Regression Specification", 2);
        doc.AppendParagraph("The primary analytical model employed a two-stage least squares regression to instrument for endogenous variables, following the approach of Heckman and Vytlacil.");
        doc.AddFootnote(1, "Heckman, J. and Vytlacil, E. (2007) 'Econometric Evaluation of Social Programs'. Handbook of Econometrics, Volume 6B, pp. 4779-4874.");
        doc.AddComment(1, "Peer_Reviewer_1", "Clarify why IV approach preferred over GMM — cite Angrist and Pischke.");
        doc.AppendParagraph("Standard errors were clustered at the local authority district level to account for spatial autocorrelation in survey responses, as recommended by Cameron and Miller.");
        doc.AddFootnote(2, "Cameron, A.C. and Miller, D.L. (2015) 'A Practitioner's Guide to Cluster-Robust Inference'. Journal of Human Resources, 50(2), pp. 317-372.");

        var fn1 = doc.GetFootnoteCount();
        var cm1 = doc.GetCommentCount();
        Assert.True(fn1 > fn0); // footnotes added
        Assert.True(cm1 > cm0); // comment added
        Assert.Equal(2, fn1);
        Assert.Equal(fn1, doc.GetFootnoteCount()); // consistent
        Assert.Equal(cm1, doc.GetCommentCount()); // consistent

        // Section 3: Data quality and limitations
        doc.InsertSection("Section 3: Data Quality");
        doc.InsertHeading(3, "3.1 Non-Response Bias Assessment", 2);
        doc.AppendParagraph("Response rates for the 2022 survey wave reached 68%, compared with a pre-pandemic baseline of 74%. Non-response weights were calibrated using the Annual Population Survey as auxiliary data.");
        doc.AddFootnote(3, "ONS (2023) Integrated Household Survey 2022: User Guide, Section 4.2 Weighting Methodology.");
        doc.AddComment(2, "Peer_Reviewer_2", "The 6pp drop in response rate requires sensitivity analysis — please add Appendix B.");
        doc.AddFootnote(4, "Lynn, P. (2009) 'Methods for Longitudinal Surveys' in Methodology of Longitudinal Surveys. Wiley.");
        doc.AddComment(3, "Lead_Author", "Appendix B drafted — sensitivity tables available on request.");

        doc.InsertHeading(4, "3.2 Measurement Error", 2);
        doc.AppendParagraph("Self-reported income data are subject to social desirability bias. Validation against HMRC administrative records confirmed a correlation of r = 0.83 for respondents providing valid consent.");
        doc.AddFootnote(5, "HMRC (2024) Research and Statistics: Personal Incomes Statistics 2021-22.");

        var fn2 = doc.GetFootnoteCount();
        var cm2 = doc.GetCommentCount();
        Assert.True(fn2 > fn1); // three more footnotes
        Assert.True(cm2 > cm1); // two more comments
        Assert.Equal(5, fn2);
        Assert.Equal(3, cm2);
        Assert.Equal(fn2, doc.GetFootnoteCount()); // consistent
        Assert.Equal(cm2, doc.GetCommentCount()); // consistent

        // Basic document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // SaveToFile
        var path1 = TempFile("esrc_methodology_review.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(fn2, loaded.GetFootnoteCount());
        Assert.Equal(cm2, loaded.GetCommentCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());

        // Extend with acknowledgements footnotes
        loaded.InsertSection("Section 4: Acknowledgements");
        loaded.AppendParagraph("This research was funded by the Economic and Social Research Council under Grant ES/R012345/1.");
        loaded.AddFootnote(6, "ESRC Grant ES/R012345/1: 'Social Mobility and Educational Attainment in Post-Brexit Britain', 2021-2024.");
        loaded.AddComment(4, "Copy_Editor", "Confirm grant reference number with UKRI portal.");

        var fnFinal = loaded.GetFootnoteCount();
        var cmFinal = loaded.GetCommentCount();
        Assert.True(fnFinal > fn2);
        Assert.True(cmFinal > cm2);

        var path2 = TempFile("esrc_methodology_review_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(fnFinal, final.GetFootnoteCount());
        Assert.Equal(cmFinal, final.GetCommentCount());

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetFootnoteCount());
        var ex2 = Record.Exception(() => final.GetCommentCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
