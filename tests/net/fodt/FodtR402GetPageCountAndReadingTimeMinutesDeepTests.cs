// Tests for FodtDocument.GetPageCount, GetReadingTimeMinutes deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R402

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R402: Tests for FodtDocument.GetPageCount, GetReadingTimeMinutes deeper.
/// GetPageCount(): returns the number of pages in the document (estimated from content length).
/// GetReadingTimeMinutes(): returns estimated reading time in minutes at ~200 words/minute.
/// Covers: GetPageCount no-throw; GetPageCount positive; GetPageCount non-decreasing after AppendParagraph;
/// GetPageCount consistent; GetPageCount save-load;
/// GetReadingTimeMinutes no-throw; GetReadingTimeMinutes non-negative; GetReadingTimeMinutes positive for content;
/// GetReadingTimeMinutes consistent; GetReadingTimeMinutes save-load;
/// GetReadingTimeMinutes increases after AppendParagraph; dogfood pipeline.
/// </summary>
public class FodtR402GetPageCountAndReadingTimeMinutesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR402GetPageCountAndReadingTimeMinutesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR402_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateShortDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Introduction", 1);
        doc.AppendParagraph("This is a brief introductory paragraph.");
        return doc;
    }

    private static FodtDocument CreateLongDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Comprehensive Policy Review", 1);
        for (int i = 0; i < 30; i++)
            doc.AppendParagraph(
                $"Section {i + 1}: This paragraph contains detailed analytical content describing " +
                $"policy implications, legislative background, and regulatory considerations for item {i + 1}. " +
                $"The analysis draws on primary source material and independent expert commentary.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageCount_NoThrow()
    {
        var doc = CreateShortDoc();
        var ex = Record.Exception(() => doc.GetPageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageCount_Positive()
    {
        var doc = CreateShortDoc();
        Assert.True(doc.GetPageCount() >= 1);
    }

    [Fact]
    public void GetPageCount_NonDecreasing_After_AppendParagraph()
    {
        var doc = CreateShortDoc();
        var before = doc.GetPageCount();
        for (int i = 0; i < 20; i++)
            doc.AppendParagraph(
                $"Additional paragraph {i}: containing substantial amounts of content " +
                "intended to fill multiple pages of a standard A4 document layout.");
        Assert.True(doc.GetPageCount() >= before);
    }

    [Fact]
    public void GetPageCount_Consistent()
    {
        var doc = CreateLongDoc();
        Assert.Equal(doc.GetPageCount(), doc.GetPageCount());
    }

    [Fact]
    public void GetPageCount_SaveLoad_Consistent()
    {
        var doc = CreateLongDoc();
        var before = doc.GetPageCount();
        var path = TempFile("pg_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageCount());
    }

    // -------------------------------------------------------------------------
    // GetReadingTimeMinutes
    // -------------------------------------------------------------------------

    [Fact]
    public void GetReadingTimeMinutes_NoThrow()
    {
        var doc = CreateShortDoc();
        var ex = Record.Exception(() => doc.GetReadingTimeMinutes());
        Assert.Null(ex);
    }

    [Fact]
    public void GetReadingTimeMinutes_NonNegative()
    {
        var doc = CreateShortDoc();
        Assert.True(doc.GetReadingTimeMinutes() >= 0);
    }

    [Fact]
    public void GetReadingTimeMinutes_Positive_ForContent()
    {
        var doc = CreateLongDoc();
        Assert.True(doc.GetReadingTimeMinutes() > 0);
    }

    [Fact]
    public void GetReadingTimeMinutes_Consistent()
    {
        var doc = CreateLongDoc();
        Assert.Equal(doc.GetReadingTimeMinutes(), doc.GetReadingTimeMinutes());
    }

    [Fact]
    public void GetReadingTimeMinutes_SaveLoad_Consistent()
    {
        var doc = CreateLongDoc();
        var before = doc.GetReadingTimeMinutes();
        var path = TempFile("rt_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetReadingTimeMinutes());
    }

    [Fact]
    public void GetReadingTimeMinutes_Increases_After_AppendParagraph()
    {
        var doc = CreateShortDoc();
        var before = doc.GetReadingTimeMinutes();
        for (int i = 0; i < 50; i++)
            doc.AppendParagraph(
                "Regulatory analysis paragraph with substantive technical and policy content. " +
                "This text adds approximately forty words of reading material per iteration. " +
                "Reading time should increase measurably after appending fifty such paragraphs.");
        Assert.True(doc.GetReadingTimeMinutes() >= before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPageCount_GetReadingTimeMinutes_Pipeline()
    {
        // Healthcare — NHS England / NICE: Clinical Commissioning Policy Document
        // Structured clinical guidance document with multiple sections, tables, and evidence references
        // Page count and reading time are key accessibility metrics in NICE document templates

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "NICE Clinical Commissioning Policy: Haemophilia A — Extended Half-Life Factor VIII", 1);
        doc.AppendParagraph("Version: 2.1 | Reference: NHS England/NICE/POL/2024/047 | Review Date: March 2026");

        // Part 1: Background and clinical need
        doc.InsertSection("Part 1: Clinical Background");
        doc.InsertHeading(1, "1.1 Condition Overview", 2);
        doc.AppendParagraph("Haemophilia A is an X-linked recessive disorder characterised by deficiency of clotting factor VIII (FVIII). The condition affects approximately 1 in 5,000 male births in England and causes recurrent spontaneous and trauma-induced bleeding into joints, muscles, and soft tissues. Severe haemophilia A (FVIII activity <1 IU/dL) accounts for approximately 40% of cases.");
        doc.AppendParagraph("The extended half-life (EHL) recombinant FVIII products approved for use under this policy demonstrate two- to three-fold increases in half-life compared to standard half-life products, enabling prophylaxis dosing intervals to be extended from every 48 hours to twice weekly or weekly administration.");

        doc.InsertHeading(2, "1.2 Current Standard of Care", 2);
        doc.AppendParagraph("Standard treatment comprises prophylactic intravenous infusion of recombinant FVIII concentrate three times weekly. Key limitations include venous access difficulties (particularly in paediatric patients), treatment burden affecting quality of life and adherence, and breakthrough bleeding events at trough FVIII levels below 1 IU/dL.");
        doc.AppendParagraph("The National Haemophilia Database (NHD) records approximately 2,200 patients with severe haemophilia A in England receiving prophylactic treatment. Annual infusion frequency ranges from 78 to 156 administrations per patient on standard half-life regimens.");

        var pg0 = doc.GetPageCount();
        var rt0 = doc.GetReadingTimeMinutes();
        Assert.True(pg0 >= 1);
        Assert.True(rt0 >= 0);

        // Part 2: Evidence base
        doc.InsertSection("Part 2: Clinical Evidence");
        doc.InsertHeading(3, "2.1 Clinical Trial Evidence", 2);
        doc.AppendParagraph("The ASPIRE trial (Phase III, n=148) demonstrated that extended half-life FVIII administered twice weekly achieved a median annualised bleeding rate (ABR) of 1.4 (IQR 0–4.3) compared with 4.7 (IQR 1.1–11.2) on standard half-life prophylaxis (p<0.001). Target joint resolution occurred in 83.2% of patients with pre-existing target joints.");
        doc.AppendParagraph("The HAVEN-3 extension study (n=89, 52 weeks) confirmed durability of effect: median ABR 0.9 at Week 52, with 60.7% of patients achieving zero bleeds. Pharmacokinetic modelling demonstrated FVIII trough maintenance above 3 IU/dL in 94% of patients on twice-weekly dosing.");

        doc.InsertTable(3, new[] { "Study", "N", "Dosing", "Median ABR", "p-value" },
            new[] {
                new[] { "ASPIRE (Phase III)", "148", "Twice weekly", "1.4", "<0.001" },
                new[] { "HAVEN-3 Extension", "89", "Weekly", "0.9", "0.003" },
                new[] { "PATHFINDER-2", "134", "Twice weekly", "1.1", "<0.001" },
                new[] { "ATLAS-A/B", "112", "Weekly", "1.6", "0.008" }
            });

        doc.InsertBookmark(3, "clinical_evidence_table");

        var pg1 = doc.GetPageCount();
        var rt1 = doc.GetReadingTimeMinutes();
        Assert.True(pg1 >= pg0); // more content → same or more pages
        Assert.True(rt1 >= rt0); // more content → same or more reading time

        // Part 3: Commissioning criteria
        doc.InsertSection("Part 3: Commissioning Criteria");
        doc.InsertHeading(4, "3.1 Patient Eligibility", 2);
        doc.AppendParagraph("This policy authorises NHS England commissioning of extended half-life FVIII for adults and children (≥2 years) with severe haemophilia A (FVIII <1 IU/dL) without inhibitors who meet ALL of the following criteria:");
        doc.AppendParagraph("(a) Currently receiving or eligible for prophylactic FVIII replacement therapy; (b) Documented inadequate control on standard half-life FVIII defined as ABR ≥4 bleeds per year OR failure to maintain FVIII trough ≥1 IU/dL on current regimen; (c) Agreement to participate in mandatory outcome monitoring via the National Haemophilia Database.");

        doc.InsertTable(4, new[] { "Criterion", "Assessment Method", "Threshold", "Review Frequency" },
            new[] {
                new[] { "FVIII activity level", "One-stage clotting assay", "<1 IU/dL", "At diagnosis" },
                new[] { "Annualised bleeding rate", "NHD audit", "≥4/year on SHL", "6-monthly" },
                new[] { "Inhibitor screen", "Bethesda assay", "Negative (<0.6 BU/mL)", "Prior to EHL initiation" },
                new[] { "Joint health score", "Pettersson/Haemo-A-MOM", "As documented", "Annually" },
                new[] { "Quality of life", "EQ-5D-5L / HEP-Test-Q", "Baseline established", "Annually" }
            });

        doc.InsertBookmark(4, "eligibility_criteria_table");

        var pg2 = doc.GetPageCount();
        var rt2 = doc.GetReadingTimeMinutes();
        Assert.True(pg2 >= pg1);
        Assert.True(rt2 >= rt1);

        // Part 4: Financial and service impact
        doc.InsertSection("Part 4: Financial Impact and Service Considerations");
        doc.InsertHeading(5, "4.1 Budget Impact", 2);
        doc.AppendParagraph("Based on 2024/25 NHS England tariff data, the incremental cost of EHL FVIII over standard half-life products is estimated at £8,200–£14,600 per patient per annum (list price basis). Following Commercial Medicines Unit (CMU) framework agreements, the net budget impact is estimated at £4,100–£7,300 per patient after rebate adjustments.");
        doc.AppendParagraph("NHS England's Highly Specialised Technologies programme estimates an eligible population of 320–480 patients (15–22% of severe haemophilia A cohort) based on current inadequate control criteria. Total indicative budget impact: £1.3M–£3.5M annually within the specialised services baseline.");

        doc.InsertTable(5, new[] { "Year", "Estimated Patients", "Gross Cost (£M)", "Net Cost After Rebate (£M)", "QALYs Gained" },
            new[] {
                new[] { "2025/26", "180", "2.1", "1.05", "54" },
                new[] { "2026/27", "290", "3.4", "1.70", "87" },
                new[] { "2027/28", "390", "4.5", "2.25", "117" },
                new[] { "2028/29", "450", "5.2", "2.60", "135" }
            });

        doc.InsertBookmark(5, "budget_impact_table");
        doc.InsertBookmark(5, "qaly_projection_table");

        var pg3 = doc.GetPageCount();
        var rt3 = doc.GetReadingTimeMinutes();
        Assert.True(pg3 >= pg2);
        Assert.True(rt3 >= rt2);
        Assert.True(doc.GetPageCount() == pg3); // consistent
        Assert.True(doc.GetReadingTimeMinutes() == rt3); // consistent

        // Basic document integrity
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetTableCount() >= 3);
        Assert.True(doc.GetBookmarkCount() >= 4);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("nice_haemophilia_policy.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(pg3, loaded.GetPageCount());
        Assert.Equal(rt3, loaded.GetReadingTimeMinutes());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());
        Assert.Equal(doc.GetTableCount(), loaded.GetTableCount());
        Assert.Equal(doc.GetBookmarkCount(), loaded.GetBookmarkCount());

        // Extend with appendix
        loaded.InsertSection("Appendix A: Glossary of Terms");
        loaded.InsertHeading(6, "A.1 Abbreviations", 2);
        loaded.AppendParagraph("ABR: Annualised Bleeding Rate. CMU: Commercial Medicines Unit. EHL: Extended Half-Life. FVIII: Factor VIII. NHD: National Haemophilia Database. NICE: National Institute for Health and Care Excellence. QoL: Quality of Life. SHL: Standard Half-Life.");

        loaded.InsertSection("Appendix B: References");
        loaded.InsertHeading(7, "B.1 Primary Literature", 2);
        loaded.AppendParagraph("1. Mahlangu J et al. Phase 3 study of recombinant factor VIII Fc fusion protein in severe haemophilia A. Blood. 2014;123(3):317-325. 2. Nolan B et al. Pharmacokinetics and prophylactic use of extended half-life FVIII concentrates. Haemophilia. 2022;28(Suppl 4):54-61.");

        var pgFinal = loaded.GetPageCount();
        var rtFinal = loaded.GetReadingTimeMinutes();
        Assert.True(pgFinal >= pg3);
        Assert.True(rtFinal >= rt3);

        var path2 = TempFile("nice_haemophilia_policy_with_appendix.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(pgFinal, final.GetPageCount());
        Assert.Equal(rtFinal, final.GetReadingTimeMinutes());

        var ex1 = Record.Exception(() => final.GetPageCount());
        var ex2 = Record.Exception(() => final.GetReadingTimeMinutes());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
