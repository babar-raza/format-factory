// Tests for FodtDocument.GetSectionName, RenameSection deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R351

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R351: Tests for FodtDocument.GetSectionName, RenameSection deeper.
/// GetSectionName(sectionIndex): returns the name of the section at the given index.
/// RenameSection(sectionIndex, newName): renames the section at the given index.
/// Covers: GetSectionName no-throw; GetSectionName non-null; GetSectionName consistent;
/// GetSectionName save-load; RenameSection no-throw; RenameSection then GetSectionName updated;
/// RenameSection then GetSectionCount unchanged; RenameSection then ExportToHtml no-throw;
/// RenameSection then ExportToMarkdown no-throw; RenameSection save-load;
/// RenameSection multiple sections; RenameSection then GetWordCount positive;
/// dogfood CreateDoc→AddSection→GetSectionName→RenameSection→SaveToFile pipeline.
/// </summary>
public class FodtR351GetSectionNameAndRenameSectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR351GetSectionNameAndRenameSectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR351_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateSectionDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Technical Architecture Review: Cloud-Native Platform Migration", 1);
        doc.AppendParagraph("This document presents the technical architecture review for migration of the legacy monolithic application to a cloud-native microservices architecture on AWS, including infrastructure-as-code specifications, security controls, and operational runbooks.");
        doc.AppendParagraph("The review covers compute, networking, storage, identity and access management, observability, and disaster recovery components across three AWS regions: eu-west-1 (primary), eu-west-2 (secondary), and eu-central-1 (DR).");
        doc.AddSection("Executive_Summary", 0);
        doc.AppendParagraph("The migration programme covers 47 microservices decomposed from the legacy monolith, targeting a 99.95% SLA across the platform.");
        doc.AddSection("Architecture_Overview", 1);
        doc.AppendParagraph("Container orchestration via Amazon EKS with Fargate for serverless compute, service mesh via AWS App Mesh, API gateway via Amazon API Gateway v2.");
        doc.AddSection("Security_Controls", 2);
        doc.AppendParagraph("Zero-trust network model implemented via AWS PrivateLink, KMS-managed encryption at rest and in transit, IAM roles with least-privilege access.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionName_NoThrow()
    {
        var doc = CreateSectionDoc();
        var ex = Record.Exception(() => doc.GetSectionName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionName_NonNull()
    {
        var doc = CreateSectionDoc();
        Assert.NotNull(doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_Consistent()
    {
        var doc = CreateSectionDoc();
        Assert.Equal(doc.GetSectionName(0), doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_SaveLoad_Consistent()
    {
        var doc = CreateSectionDoc();
        var before = doc.GetSectionName(0);
        var path = TempFile("gsn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionName(0));
    }

    // -------------------------------------------------------------------------
    // RenameSection
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSection_NoThrow()
    {
        var doc = CreateSectionDoc();
        var ex = Record.Exception(() => doc.RenameSection(0, "Renamed_Section"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSection_Then_GetSectionName_Updated()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(0, "Updated_Executive_Summary");
        Assert.Equal("Updated_Executive_Summary", doc.GetSectionName(0));
    }

    [Fact]
    public void RenameSection_Then_GetSectionCount_Unchanged()
    {
        var doc = CreateSectionDoc();
        var before = doc.GetSectionCount();
        doc.RenameSection(0, "Renamed_Section");
        Assert.Equal(before, doc.GetSectionCount());
    }

    [Fact]
    public void RenameSection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(1, "Arch_Overview_Renamed");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSection_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(2, "Security_Controls_v2");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void RenameSection_SaveLoad_Persists()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(0, "Exec_Summary_Renamed");
        var path = TempFile("rs_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal("Exec_Summary_Renamed", loaded.GetSectionName(0));
    }

    [Fact]
    public void RenameSection_MultipleSections()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(0, "Exec_v2");
        doc.RenameSection(1, "Arch_v2");
        doc.RenameSection(2, "Sec_v2");
        Assert.Equal("Exec_v2", doc.GetSectionName(0));
        Assert.Equal("Arch_v2", doc.GetSectionName(1));
        Assert.Equal("Sec_v2", doc.GetSectionName(2));
    }

    [Fact]
    public void RenameSection_Then_GetWordCount_Positive()
    {
        var doc = CreateSectionDoc();
        doc.RenameSection(0, "Renamed");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSection_GetSectionName_RenameSection_SaveToFile_Pipeline()
    {
        // Regulatory — MHRA Clinical Trials Regulation (UK) 2004 — Clinical Study Protocol
        // Section management for a Phase III adaptive trial protocol document
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Clinical Study Protocol: PINNACLE-2 — Phase III Adaptive Randomised Controlled Trial of Pembranivimab Plus Chemotherapy in PD-L1-High Metastatic NSCLC", 1);
        doc.AppendParagraph("Protocol Version 3.2, dated 14 March 2024. EudraCT Number: 2023-004521-38. MHRA Notification Reference: CTA/2023/00847.");
        doc.AppendParagraph("This protocol governs the conduct of the PINNACLE-2 trial at 94 participating sites across the United Kingdom, Ireland, France, Germany, Spain, Italy, and the Netherlands. The trial is sponsored by Nexagen Biosciences Ltd, a UK-registered clinical stage biopharmaceutical company.");

        doc.InsertHeading(3, "Background and Rationale", 2);
        doc.AppendParagraph("Non-small cell lung cancer (NSCLC) with high PD-L1 tumour proportion score (TPS ≥50%) represents approximately 28% of newly diagnosed advanced NSCLC and is associated with a median overall survival of 16.7 months with pembrolizumab monotherapy (KEYNOTE-024). The PINNACLE-2 trial tests whether addition of platinum-doublet chemotherapy improves outcomes in this select population.");
        doc.AppendParagraph("Preclinical data from syngeneic mouse models demonstrate synergistic tumour control with pembranivimab plus carboplatin/nab-paclitaxel, mediated by immunogenic cell death and enhanced tumour antigen presentation. Phase I/II data (n=78) show a manageable safety profile with ORR of 67% (95% CI: 55-77%).");

        // Add sections
        doc.AddSection("Protocol_Summary", 0);
        doc.AppendParagraph("Study design: open-label, two-arm, randomised 1:1. Stratification: ECOG PS (0 vs 1), histology (squamous vs non-squamous), prior immunotherapy (yes vs no).");

        doc.AddSection("Study_Objectives", 1);
        doc.AppendParagraph("Primary objective: to evaluate whether pembranivimab 200 mg Q3W plus carboplatin AUC5 plus nab-paclitaxel 100 mg/m² improves overall survival compared with pembrolizumab 200 mg Q3W monotherapy in patients with metastatic NSCLC with TPS ≥50%.");
        doc.AppendParagraph("Key secondary objectives: PFS per RECIST 1.1 by BICR; ORR; DOR; safety and tolerability; HRQL by EORTC QLQ-C30 and QLQ-LC13.");

        doc.AddSection("Eligibility_Criteria", 2);
        doc.AppendParagraph("Key inclusion: age ≥18 years; confirmed metastatic NSCLC with TPS ≥50% by validated 22C3 IHC assay; ECOG PS 0-1; measurable disease per RECIST 1.1; adequate organ function.");
        doc.AppendParagraph("Key exclusion: prior systemic anticancer therapy for metastatic disease; known EGFR sensitising mutation or ALK/ROS1 rearrangement; active autoimmune disease requiring systemic treatment within 2 years.");

        doc.AddSection("Statistical_Analysis_Plan", 3);
        doc.AppendParagraph("Primary analysis: hierarchical testing strategy, OS alpha=0.025 (one-sided); planned at 420 OS events (80% power to detect HR 0.75 assuming 24-month median OS in comparator arm at 5% one-sided alpha). Interim analysis at 210 events for futility (O'Brien-Fleming boundary).");

        doc.AddSection("Safety_Monitoring", 4);
        doc.AppendParagraph("Independent Data Safety Monitoring Board (DSMB) constitution: 3 independent oncologists, 1 statistician. DSMB charter mandates unblinded safety review every 6 months and review triggered by pre-specified stopping rules.");

        Assert.Equal(5, doc.GetSectionCount());

        // GetSectionName
        var name0 = doc.GetSectionName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetSectionName(0)); // consistent

        var name1 = doc.GetSectionName(1);
        Assert.NotNull(name1);

        var name2 = doc.GetSectionName(2);
        Assert.NotNull(name2);

        // RenameSection — version control rename for protocol amendment
        doc.RenameSection(0, "Protocol_Summary_v3_2");
        Assert.Equal("Protocol_Summary_v3_2", doc.GetSectionName(0));
        Assert.Equal(5, doc.GetSectionCount()); // unchanged

        doc.RenameSection(3, "SAP_v3_2");
        Assert.Equal("SAP_v3_2", doc.GetSectionName(3));

        doc.RenameSection(4, "Safety_Monitoring_DSMB");
        Assert.Equal("Safety_Monitoring_DSMB", doc.GetSectionName(4));

        // Other sections unchanged
        Assert.Equal(name1, doc.GetSectionName(1));
        Assert.Equal(name2, doc.GetSectionName(2));

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
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_pinnacle2_protocol.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetSectionCount());
        Assert.Equal("Protocol_Summary_v3_2", loaded.GetSectionName(0));
        Assert.Equal("SAP_v3_2", loaded.GetSectionName(3));
        Assert.Equal("Safety_Monitoring_DSMB", loaded.GetSectionName(4));
        Assert.Equal(name1, loaded.GetSectionName(1));
        Assert.True(loaded.GetParagraphCount() > 0);

        // RenameSection on loaded
        loaded.RenameSection(1, "Study_Objectives_v3_2");
        Assert.Equal("Study_Objectives_v3_2", loaded.GetSectionName(1));

        // AddSection on loaded
        loaded.AddSection("Appendices_v3_2", 5);
        loaded.AppendParagraph("Appendix A: Investigator Brochure v7.1. Appendix B: Informed Consent Form templates (UK, IE, FR, DE, ES, IT, NL versions). Appendix C: DSMB Charter.");
        Assert.Equal(6, loaded.GetSectionCount());
        Assert.NotNull(loaded.GetSectionName(5));

        // Final save
        var path2 = TempFile("dogfood_pinnacle2_protocol_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetSectionCount());
        Assert.Equal("Study_Objectives_v3_2", loaded2.GetSectionName(1));
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.RenameSection(0, "Protocol_Summary_Final"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
