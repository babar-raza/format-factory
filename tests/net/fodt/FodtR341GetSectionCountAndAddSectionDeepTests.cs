// Tests for FodtDocument.GetSectionCount, AddSection, GetSectionName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R341

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R341: Tests for FodtDocument.GetSectionCount, AddSection, GetSectionName deeper.
/// GetSectionCount(): returns the number of named sections in the document.
/// AddSection(name, paragraphIndex): inserts a named section boundary at the given paragraph.
/// GetSectionName(index): returns the name of the section at the given index.
/// Covers: GetSectionCount no-throw; GetSectionCount non-negative; GetSectionCount consistent;
/// GetSectionCount zero for new doc; GetSectionCount after AddSection increases;
/// GetSectionCount save-load;
/// AddSection no-throw; AddSection increases count; AddSection save-load;
/// AddSection multiple; AddSection then ExportToHtml no-throw;
/// AddSection then ExportToMarkdown no-throw; AddSection then GetWordCount positive;
/// GetSectionName no-throw; GetSectionName non-null; GetSectionName consistent;
/// GetSectionName save-load;
/// dogfood CreateDoc→AddSection→GetSectionCount→GetSectionName→SaveToFile pipeline.
/// </summary>
public class FodtR341GetSectionCountAndAddSectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR341GetSectionCountAndAddSectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR341_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreatePolicyDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Information Security Policy: ISMS Framework and Controls — ISO 27001:2022 Aligned", 1);
        doc.AppendParagraph("This Information Security Management System (ISMS) policy establishes the framework for protecting the confidentiality, integrity, and availability of information assets across all business units of the organisation, in accordance with ISO/IEC 27001:2022.");
        doc.AppendParagraph("The policy applies to all employees, contractors, third-party suppliers, and any individual accessing organisation information systems, regardless of location, device ownership, or employment classification.");
        doc.InsertHeading(3, "Scope and Applicability", 2);
        doc.AppendParagraph("The ISMS scope encompasses all information processing facilities operated directly or through outsourcing arrangements, including cloud-hosted systems, on-premises data centres, and remote working infrastructure.");
        doc.AppendParagraph("Information assets are classified according to the Asset Classification Standard (ACS-001) as Public, Internal, Confidential, or Highly Restricted, with corresponding handling, storage, and disposal requirements.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_NoThrow()
    {
        var doc = CreatePolicyDoc();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_NonNegative()
    {
        var doc = CreatePolicyDoc();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void GetSectionCount_Consistent()
    {
        var doc = CreatePolicyDoc();
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no named sections.");
        Assert.Equal(0, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_AfterAddSection_Increases()
    {
        var doc = CreatePolicyDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("Introduction", 1);
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_SaveLoad_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Scope", 2);
        var before = doc.GetSectionCount();
        var path = TempFile("sc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    // -------------------------------------------------------------------------
    // AddSection
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSection_NoThrow()
    {
        var doc = CreatePolicyDoc();
        var ex = Record.Exception(() => doc.AddSection("Policy_Introduction", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Increases_Count()
    {
        var doc = CreatePolicyDoc();
        var before = doc.GetSectionCount();
        doc.AddSection("Scope_Section", 3);
        Assert.Equal(before + 1, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_SaveLoad_Persists()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Asset_Classification", 4);
        var before = doc.GetSectionCount();
        var path = TempFile("as_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void AddSection_Multiple()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Section_1", 0);
        doc.AddSection("Section_2", 1);
        doc.AddSection("Section_3", 3);
        Assert.Equal(3, doc.GetSectionCount());
    }

    [Fact]
    public void AddSection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("HTML_Section", 2);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Markdown_Section", 1);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddSection_Then_GetWordCount_Positive()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("WordCount_Section", 0);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetSectionName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionName_NoThrow()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Retrieve_Section", 1);
        var ex = Record.Exception(() => doc.GetSectionName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionName_NonNull()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("NonNull_Section", 2);
        Assert.NotNull(doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("Consistent_Section", 0);
        Assert.Equal(doc.GetSectionName(0), doc.GetSectionName(0));
    }

    [Fact]
    public void GetSectionName_SaveLoad_Consistent()
    {
        var doc = CreatePolicyDoc();
        doc.AddSection("SaveLoad_Section", 3);
        var path = TempFile("sn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetSectionName(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddSection_GetSectionCount_GetSectionName_SaveToFile_Pipeline()
    {
        // Engineering manual — pipeline integrity management system for subsea infrastructure
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Subsea Pipeline Integrity Management System: Risk-Based Inspection Framework for High-Pressure Hydrocarbon Service — API 1160 / ASME B31.4 Compliant", 1);
        doc.AppendParagraph("This Integrity Management System (IMS) defines the risk-based inspection programme, anomaly management procedures, and fitness-for-service assessment methodology for subsea hydrocarbon pipelines operating above MAOP 250 bar in water depths exceeding 300m.");
        doc.AppendParagraph("The framework aligns with API Standard 1160 (Managing System Integrity for Hazardous Liquid Pipelines), ASME B31.4 (Pipeline Transportation Systems for Liquids and Slurries), and DNV-RP-F101 (Corroded Pipelines).");

        doc.InsertHeading(3, "Threat Identification and Assessment", 2);
        doc.AppendParagraph("Active threats identified through hierarchical fault tree analysis include: external corrosion (CO2/H2S), internal erosion-corrosion, third-party interference, geohazards (slope instability, seabed movement), and thermal fatigue at riser-pipeline interfaces.");
        doc.AppendParagraph("Consequence analysis using SAFETI-NL quantitative risk modelling assigns each threat a Potential Impact Radius (PIR) and F/N curve position, informing the High Consequence Area (HCA) designations under 49 CFR Part 195.");

        doc.InsertHeading(6, "Inspection Programme", 2);
        doc.AppendParagraph("In-Line Inspection (ILI) using magnetic flux leakage (MFL) and ultrasonic wall measurement (UTWM) tools is scheduled on a risk-ranked basis, with HCA segments inspected at maximum 5-year intervals and low-consequence segments at 10-year intervals.");
        doc.AppendParagraph("Remotely Operated Vehicle (ROV) visual surveys at 6-month intervals detect freespanning, coating damage, anode depletion, and marine growth accumulation, with findings logged in the MAXIMO asset management system.");

        doc.InsertHeading(9, "Anomaly Management", 1);
        doc.AppendParagraph("ILI-detected anomalies are classified per RSTRENG effective area method and POF analysis: Immediate Repair (>80% wt), Scheduled Repair (60-80% wt), and Monitor (< 60% wt) conditions trigger the appropriate work order in SAP PM.");
        doc.AppendParagraph("Fitness-for-service assessments for pressurised dents exceeding 6% OD, composite repairs, and weld anomalies follow BS 7910 Level 2 fracture mechanics analysis with Monte Carlo uncertainty quantification at 95th percentile confidence.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetSectionCount());

        // AddSection — document sections for regulatory cross-reference
        doc.AddSection("Preamble_and_Scope", 0);
        Assert.Equal(1, doc.GetSectionCount());

        doc.AddSection("Regulatory_Framework", 1);
        Assert.Equal(2, doc.GetSectionCount());

        doc.AddSection("Threat_Identification", 3);
        Assert.Equal(3, doc.GetSectionCount());

        doc.AddSection("Consequence_Analysis", 4);
        Assert.Equal(4, doc.GetSectionCount());

        doc.AddSection("ILI_Programme", 5);
        Assert.Equal(5, doc.GetSectionCount());

        doc.AddSection("ROV_Inspection", 6);
        Assert.Equal(6, doc.GetSectionCount());

        // Consistent
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());

        // GetSectionName
        var name0 = doc.GetSectionName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetSectionName(0)); // consistent

        var name3 = doc.GetSectionName(3);
        Assert.NotNull(name3);

        var name5 = doc.GetSectionName(5);
        Assert.NotNull(name5);

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
        var path = TempFile("dogfood_pipeline_ims.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetSectionCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetSectionName(0));
        Assert.NotNull(loaded.GetSectionName(5));

        // AddSection on loaded
        loaded.AddSection("Anomaly_Management_Procedure", 8);
        Assert.Equal(7, loaded.GetSectionCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the risk-based IMS framework ensures systematic prioritisation of inspection resources on high-consequence pipeline segments, demonstrating ALARP compliance to regulatory bodies and minimising the probability of catastrophic loss of containment events.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_pipeline_ims_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetSectionCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetSectionName(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddSection("Final_Section", 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
