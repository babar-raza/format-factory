// Tests for FodtDocument.GetRevisionCount, GetChangeCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R406

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R406: Tests for FodtDocument.GetRevisionCount, GetChangeCount deeper.
/// GetRevisionCount(): returns the number of tracked revisions in the document.
/// GetChangeCount(): returns the number of tracked changes (insertions/deletions) in the document.
/// Covers: GetRevisionCount no-throw; GetRevisionCount non-negative; GetRevisionCount zero for new doc;
/// GetRevisionCount consistent; GetRevisionCount save-load;
/// GetChangeCount no-throw; GetChangeCount non-negative; GetChangeCount zero for new doc;
/// GetChangeCount consistent; GetChangeCount save-load; dogfood pipeline.
/// </summary>
public class FodtR406GetRevisionCountAndChangeCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR406GetRevisionCountAndChangeCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR406_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateFreshDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Fresh Document", 1);
        doc.AppendParagraph("This is a new document without any tracked changes or revisions.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRevisionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRevisionCount_NoThrow()
    {
        var doc = CreateFreshDoc();
        var ex = Record.Exception(() => doc.GetRevisionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRevisionCount_NonNegative()
    {
        var doc = CreateFreshDoc();
        Assert.True(doc.GetRevisionCount() >= 0);
    }

    [Fact]
    public void GetRevisionCount_Zero_ForNewDoc()
    {
        var doc = CreateFreshDoc();
        Assert.Equal(0, doc.GetRevisionCount());
    }

    [Fact]
    public void GetRevisionCount_Consistent()
    {
        var doc = CreateFreshDoc();
        Assert.Equal(doc.GetRevisionCount(), doc.GetRevisionCount());
    }

    [Fact]
    public void GetRevisionCount_SaveLoad_Consistent()
    {
        var doc = CreateFreshDoc();
        var before = doc.GetRevisionCount();
        var path = TempFile("rc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRevisionCount());
    }

    // -------------------------------------------------------------------------
    // GetChangeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChangeCount_NoThrow()
    {
        var doc = CreateFreshDoc();
        var ex = Record.Exception(() => doc.GetChangeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChangeCount_NonNegative()
    {
        var doc = CreateFreshDoc();
        Assert.True(doc.GetChangeCount() >= 0);
    }

    [Fact]
    public void GetChangeCount_Zero_ForNewDoc()
    {
        var doc = CreateFreshDoc();
        Assert.Equal(0, doc.GetChangeCount());
    }

    [Fact]
    public void GetChangeCount_Consistent()
    {
        var doc = CreateFreshDoc();
        Assert.Equal(doc.GetChangeCount(), doc.GetChangeCount());
    }

    [Fact]
    public void GetChangeCount_SaveLoad_Consistent()
    {
        var doc = CreateFreshDoc();
        var before = doc.GetChangeCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChangeCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRevisionCount_GetChangeCount_Pipeline()
    {
        // Legal — Law Commission / MoJ: Sentencing Guidelines Consultation Document
        // Multi-author legal consultation document tracked through formal review pipeline
        // Revision and change counts are mandatory audit fields under LCCP publication standards

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Sentencing Council: Draft Guidelines — Fraud, Bribery and Money Laundering", 1);
        doc.AppendParagraph("Consultation Reference: SG-CON-2024-007 | Issue Date: September 2024 | Closing Date: 15 December 2024");
        doc.AppendParagraph("This consultation sets out proposed guideline amendments for sentencing in cases of fraud, bribery, money laundering and related financial crimes. Respondents are invited to provide views on the proposed culpability factors, harm assessment bands, and starting points.");

        // Verify fresh document has no revisions
        var rev0 = doc.GetRevisionCount();
        var chg0 = doc.GetChangeCount();
        Assert.Equal(0, rev0);
        Assert.Equal(0, chg0);

        // Section 1: Fraud guidelines
        doc.InsertSection("Part A: Fraud Sentencing Guidelines");
        doc.InsertHeading(1, "A.1 Culpability Factors", 2);
        doc.AppendParagraph("The following culpability factors are proposed for incorporation into the revised fraud guidelines, replacing the existing 2014 guidelines as amended:");
        doc.AppendParagraph("Category A (High Culpability): sophisticated fraud involving multiple victims; abuse of position of trust; significant planning over sustained period; targeting of vulnerable victims; leadership role in organised crime group operating across jurisdictions; fraud using false identity or counterfeit documentation with systemic concealment mechanisms.");
        doc.AppendParagraph("Category B (Medium Culpability): some planning; limited number of victims; operational role within larger fraud operation; not targeted specifically at vulnerable individuals; use of established but not complex deceptive scheme.");
        doc.AppendParagraph("Category C (Lower Culpability): offender significantly influenced by others; opportunistic deception; limited harm to any individual victim; fraud committed in response to financial pressure without prior planning.");

        doc.InsertTable(1, new[] { "Culpability", "Starting Point (Band 1: £5k–£20k)", "Starting Point (Band 2: £20k–£100k)", "Starting Point (Band 3: £100k–£500k)" },
            new[] {
                new[] { "Category A (High)", "18 months custody", "3 years custody", "6 years custody" },
                new[] { "Category B (Medium)", "1 year custody", "2 years custody", "4 years custody" },
                new[] { "Category C (Lower)", "Community order", "18 months custody", "3 years custody" }
            });
        doc.InsertBookmark(1, "fraud_starting_points_table");

        // Verify still no revisions (revisions come from track-changes workflow, not content addition)
        var rev1 = doc.GetRevisionCount();
        var chg1 = doc.GetChangeCount();
        Assert.True(rev1 >= rev0);
        Assert.True(chg1 >= chg0);
        Assert.Equal(rev1, doc.GetRevisionCount()); // consistent
        Assert.Equal(chg1, doc.GetChangeCount()); // consistent

        // Section 2: Money laundering guidelines
        doc.InsertSection("Part B: Money Laundering");
        doc.InsertHeading(2, "B.1 Harm Assessment", 2);
        doc.AppendParagraph("The harm assessment for money laundering offences uses the value of funds laundered as the primary harm indicator, with reference to the Proceeds of Crime Act 2002. The following bandings apply:");
        doc.InsertTable(2, new[] { "Harm Band", "Value Laundered", "Aggravating Factor", "Starting Point Range" },
            new[] {
                new[] { "Band 1", "Up to £50,000", "Low level facilitation", "Community order to 12 months" },
                new[] { "Band 2", "£50,000–£500,000", "Moderate facilitation", "18 months to 4 years" },
                new[] { "Band 3", "£500,000–£2m", "Significant involvement", "3 years to 7 years" },
                new[] { "Band 4", "Over £2m", "Professional laundering", "6 years to 14 years" }
            });

        // Section 3: Bribery
        doc.InsertSection("Part C: Bribery and Corruption");
        doc.InsertHeading(3, "C.1 Public Sector Bribery", 2);
        doc.AppendParagraph("Bribery of public officials (section 2 Bribery Act 2010) is treated with particular seriousness where the corrupt payment undermines public confidence in institutions or where systemic corruption is established. The proposed starting points for Band 1 (£5k–£20k) are: Category A: 3 years custody; Category B: 2 years custody; Category C: 18 months custody.");
        doc.InsertBookmark(3, "bribery_starting_points");

        var rev2 = doc.GetRevisionCount();
        var chg2 = doc.GetChangeCount();
        Assert.True(rev2 >= rev1);
        Assert.True(chg2 >= chg1);
        Assert.True(doc.GetRevisionCount() == rev2); // consistent
        Assert.True(doc.GetChangeCount() == chg2);   // consistent

        // Document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetTableCount() >= 2);

        // SaveToFile
        var path1 = TempFile("sentencing_council_fraud_guidelines.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(rev2, loaded.GetRevisionCount());
        Assert.Equal(chg2, loaded.GetChangeCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetTableCount(), loaded.GetTableCount());

        // Further save
        var path2 = TempFile("sentencing_council_fraud_v2.fodt");
        loaded.SaveToFile(path2);
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(rev2, final.GetRevisionCount());
        Assert.Equal(chg2, final.GetChangeCount());

        var ex1 = Record.Exception(() => final.GetRevisionCount());
        var ex2 = Record.Exception(() => final.GetChangeCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
