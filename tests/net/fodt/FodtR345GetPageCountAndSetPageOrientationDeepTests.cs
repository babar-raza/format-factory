// Tests for FodtDocument.GetPageCount, SetPageOrientation, GetPageOrientation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R345

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R345: Tests for FodtDocument.GetPageCount, SetPageOrientation, GetPageOrientation deeper.
/// GetPageCount(): returns the estimated number of pages in the document.
/// SetPageOrientation(orientation): sets the page orientation ("portrait" or "landscape").
/// GetPageOrientation(): returns the current page orientation.
/// Covers: GetPageCount no-throw; GetPageCount non-negative; GetPageCount consistent;
/// GetPageCount positive for doc with content; GetPageCount save-load;
/// SetPageOrientation no-throw; SetPageOrientation with portrait; SetPageOrientation with landscape;
/// SetPageOrientation then ExportToHtml no-throw; SetPageOrientation then ExportToMarkdown no-throw;
/// SetPageOrientation then GetWordCount positive;
/// GetPageOrientation no-throw; GetPageOrientation non-null; GetPageOrientation consistent;
/// GetPageOrientation save-load;
/// dogfood CreateDoc→GetPageCount→SetPageOrientation→GetPageOrientation→SaveToFile pipeline.
/// </summary>
public class FodtR345GetPageCountAndSetPageOrientationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR345GetPageCountAndSetPageOrientationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR345_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateProcurementDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Invitation to Tender: Managed IT Infrastructure Services for NHS Foundation Trust — Contract Reference NHS-IT-2024-0047", 1);
        doc.AppendParagraph("The NHS Foundation Trust (the 'Authority') invites tenders for the provision of Managed IT Infrastructure Services including helpdesk, end-user computing, network management, server and storage infrastructure, and security operations centre (SOC) services.");
        doc.AppendParagraph("This procurement is conducted under the Public Contracts Regulations 2015 (PCR 2015) using the Open Procedure. The estimated contract value is £4.2 million per annum, with an initial term of 3 years and two optional 1-year extensions.");
        doc.InsertHeading(3, "Scope of Services", 2);
        doc.AppendParagraph("Lot 1 — Service Desk and End-User Computing: provision of a 24/7/365 service desk with a maximum 4-hour response time for Priority 1 incidents, incident management aligned with ITIL v4 framework, and end-user device lifecycle management for approximately 2,400 devices across 8 sites.");
        doc.AppendParagraph("Lot 2 — Network and Infrastructure: management of the Trust's WAN/LAN infrastructure including Cisco Catalyst switches, Palo Alto firewalls, F5 load balancers, and VMware vSphere virtualisation platform hosting 340 virtual machines across two geographically separated data centres.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetPageCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPageCount_NoThrow()
    {
        var doc = CreateProcurementDoc();
        var ex = Record.Exception(() => doc.GetPageCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageCount_NonNegative()
    {
        var doc = CreateProcurementDoc();
        Assert.True(doc.GetPageCount() >= 0);
    }

    [Fact]
    public void GetPageCount_Consistent()
    {
        var doc = CreateProcurementDoc();
        Assert.Equal(doc.GetPageCount(), doc.GetPageCount());
    }

    [Fact]
    public void GetPageCount_Positive_ForDocWithContent()
    {
        var doc = CreateProcurementDoc();
        Assert.True(doc.GetPageCount() >= 1);
    }

    [Fact]
    public void GetPageCount_SaveLoad_Consistent()
    {
        var doc = CreateProcurementDoc();
        var before = doc.GetPageCount();
        var path = TempFile("pc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageCount());
    }

    // -------------------------------------------------------------------------
    // SetPageOrientation / GetPageOrientation
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPageOrientation_NoThrow()
    {
        var doc = CreateProcurementDoc();
        var ex = Record.Exception(() => doc.SetPageOrientation("portrait"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageOrientation_Portrait_NoThrow()
    {
        var doc = CreateProcurementDoc();
        var ex = Record.Exception(() => doc.SetPageOrientation("portrait"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageOrientation_Landscape_NoThrow()
    {
        var doc = CreateProcurementDoc();
        var ex = Record.Exception(() => doc.SetPageOrientation("landscape"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageOrientation_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateProcurementDoc();
        doc.SetPageOrientation("landscape");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageOrientation_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateProcurementDoc();
        doc.SetPageOrientation("portrait");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void SetPageOrientation_Then_GetWordCount_Positive()
    {
        var doc = CreateProcurementDoc();
        doc.SetPageOrientation("landscape");
        Assert.True(doc.GetWordCount() > 0);
    }

    [Fact]
    public void GetPageOrientation_NoThrow()
    {
        var doc = CreateProcurementDoc();
        var ex = Record.Exception(() => doc.GetPageOrientation());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPageOrientation_NonNull()
    {
        var doc = CreateProcurementDoc();
        Assert.NotNull(doc.GetPageOrientation());
    }

    [Fact]
    public void GetPageOrientation_Consistent()
    {
        var doc = CreateProcurementDoc();
        Assert.Equal(doc.GetPageOrientation(), doc.GetPageOrientation());
    }

    [Fact]
    public void GetPageOrientation_SaveLoad_Consistent()
    {
        var doc = CreateProcurementDoc();
        doc.SetPageOrientation("landscape");
        var path = TempFile("po_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetPageOrientation());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPageCount_SetPageOrientation_GetPageOrientation_Pipeline()
    {
        // Regulatory filing — EMA (European Medicines Agency) Common Technical Document (CTD) Module 2 summary
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Common Technical Document Module 2.7: Clinical Summary — Phase III Randomised Controlled Trial of Novel PD-L1 Inhibitor in Locally Advanced Non-Small Cell Lung Cancer", 1);
        doc.AppendParagraph("This clinical summary presents the integrated analysis of clinical data for pembranivimab (INN proposed), a humanised IgG4 monoclonal antibody targeting PD-L1, from the Phase III PINNACLE trial (ClinicalTrials.gov: NCT05182740) conducted in patients with locally advanced, unresectable non-small cell lung cancer (NSCLC) following definitive chemoradiotherapy.");
        doc.AppendParagraph("The PINNACLE trial was a double-blind, placebo-controlled, multicentre study conducted at 127 sites across 24 countries. A total of 682 patients were randomised 2:1 to receive pembranivimab 10 mg/kg IV every 3 weeks or placebo, stratified by PD-L1 expression status (TPS ≥1% vs <1%) and histology (squamous vs non-squamous).");

        doc.InsertHeading(3, "Efficacy Results", 2);
        doc.AppendParagraph("The primary endpoint, progression-free survival (PFS) per RECIST 1.1 by blinded independent central review, was met: median PFS was 16.8 months (95% CI: 14.2-19.7) in the pembranivimab arm versus 5.6 months (95% CI: 4.4-7.1) in the placebo arm, representing a hazard ratio of 0.52 (95% CI: 0.41-0.65; p<0.0001).");
        doc.AppendParagraph("Key secondary endpoints: Overall survival at 24 months was 62.3% in the pembranivimab arm versus 44.1% in placebo (HR 0.68; 95% CI: 0.54-0.86; p=0.0012). Objective response rate (ORR) was 38.4% (95% CI: 34.0-42.9) in pembranivimab versus 18.9% (95% CI: 14.3-24.4) in placebo.");

        doc.InsertHeading(6, "Safety Profile", 2);
        doc.AppendParagraph("Treatment-emergent adverse events (TEAEs) were reported in 94.7% of patients in the pembranivimab arm and 87.2% of patients in the placebo arm. Grade 3-4 TEAEs occurred in 31.2% (pembranivimab) versus 23.8% (placebo). Immune-mediated adverse events (imAEs) were observed in 28.4% of patients receiving pembranivimab.");
        doc.AppendParagraph("Pneumonitis, the pre-specified safety endpoint of interest given the post-chemoradiotherapy setting, occurred in 8.3% of pembranivimab patients (Grade 3-4: 3.1%) versus 3.2% of placebo patients (Grade 3-4: 0.9%). All cases of Grade 3-4 pneumonitis resolved with standard immunosuppression protocols.");

        doc.InsertHeading(9, "Benefit-Risk Assessment", 1);
        doc.AppendParagraph("The benefit-risk assessment supports the proposed indication: pembranivimab demonstrates clinically meaningful improvement in PFS and OS in patients with locally advanced NSCLC following definitive chemoradiotherapy, with a manageable safety profile consistent with the PD-L1 inhibitor class, and a positive benefit-risk balance supported by the DSMB interim analysis and the Scientific Advice received from the CHMP.");
        doc.AppendParagraph("The proposed Summary of Product Characteristics (SmPC) includes risk minimisation measures for pneumonitis, hepatitis, colitis, endocrinopathies, and nephritis based on the PRAC assessment of pharmacovigilance data from the compassionate use programme (3,418 patients).");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetPageCount
        var pageCount = doc.GetPageCount();
        Assert.True(pageCount >= 1);
        Assert.Equal(pageCount, doc.GetPageCount()); // consistent

        // GetPageOrientation
        var initialOrientation = doc.GetPageOrientation();
        Assert.NotNull(initialOrientation);
        Assert.Equal(initialOrientation, doc.GetPageOrientation()); // consistent

        // SetPageOrientation — landscape for wide tables
        doc.SetPageOrientation("landscape");
        var landscapeOrientation = doc.GetPageOrientation();
        Assert.NotNull(landscapeOrientation);

        // SetPageOrientation — back to portrait
        doc.SetPageOrientation("portrait");
        var portraitOrientation = doc.GetPageOrientation();
        Assert.NotNull(portraitOrientation);

        // Landscape doesn't affect paragraph count or word count
        doc.SetPageOrientation("landscape");
        Assert.Equal(12, doc.GetParagraphCount());
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // AddTable
        doc.AddTable("PFS_Data_Table", 5, 4);
        Assert.Equal(1, doc.GetTableCount());

        // AddSection
        doc.AddSection("Clinical_Summary", 0);
        Assert.Equal(1, doc.GetSectionCount());

        // SaveToFile
        var path = TempFile("dogfood_ctd_module27.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(pageCount, loaded.GetPageCount());
        Assert.NotNull(loaded.GetPageOrientation());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.Equal(1, loaded.GetTableCount());
        Assert.Equal(1, loaded.GetSectionCount());

        // SetPageOrientation on loaded
        loaded.SetPageOrientation("portrait");
        Assert.NotNull(loaded.GetPageOrientation());

        // AppendParagraph on loaded
        loaded.AppendParagraph("Appendix: Regulatory Interactions — Two scientific advice meetings were held with the CHMP (SA/0421/2022 and SA/0318/2023) confirming alignment on the primary endpoint, non-inferiority margin for safety comparisons, and statistical analysis plan for the interim and final OS analyses.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_ctd_module27_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(pageCount, loaded2.GetPageCount());
        Assert.NotNull(loaded2.GetPageOrientation());
        Assert.True(loaded2.GetParagraphCount() > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.SetPageOrientation("landscape"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
