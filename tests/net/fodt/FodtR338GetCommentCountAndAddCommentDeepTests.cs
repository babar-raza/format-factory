// Tests for FodtDocument.GetCommentCount, AddComment, GetCommentText deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R338

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R338: Tests for FodtDocument.GetCommentCount, AddComment, GetCommentText deeper.
/// GetCommentCount(): returns the number of annotations/comments in the document.
/// AddComment(paragraphIndex, author, text): inserts an annotation comment at the given paragraph.
/// GetCommentText(index): returns the text content of the comment at the given index.
/// Covers: GetCommentCount no-throw; GetCommentCount non-negative; GetCommentCount consistent;
/// GetCommentCount zero for new doc; GetCommentCount after AddComment increases;
/// GetCommentCount save-load;
/// AddComment no-throw; AddComment increases count; AddComment save-load;
/// AddComment multiple; AddComment then ExportToHtml no-throw;
/// AddComment then ExportToMarkdown no-throw; AddComment then GetWordCount positive;
/// GetCommentText no-throw; GetCommentText non-null; GetCommentText consistent;
/// GetCommentText save-load;
/// dogfood CreateDoc→AddComment→GetCommentCount→GetCommentText→SaveToFile pipeline.
/// </summary>
public class FodtR338GetCommentCountAndAddCommentDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR338GetCommentCountAndAddCommentDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR338_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateMedicalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Clinical Guidelines: Management of Acute Kidney Injury in Adult Critical Care — NHS Trust Protocol", 1);
        doc.AppendParagraph("Acute kidney injury (AKI) is defined by KDIGO criteria as an increase in serum creatinine by ≥26.5 μmol/L within 48 hours, or an increase to ≥1.5× baseline within 7 days, or urine output <0.5 mL/kg/hour for ≥6 hours.");
        doc.AppendParagraph("This protocol applies to all adult patients (≥18 years) admitted to Level 2 or Level 3 critical care units and supersedes previous guidance from 2021.");
        doc.InsertHeading(3, "Staging and Risk Stratification", 2);
        doc.AppendParagraph("AKI Stage 1: creatinine 1.5-1.9× baseline OR urine output <0.5 mL/kg/hr for 6-12 hours. Requires immediate nephrology referral and STOP/START medication review.");
        doc.AppendParagraph("AKI Stage 3: creatinine >3× baseline OR initiation of renal replacement therapy (RRT) regardless of creatinine. Mandatory ITU-level monitoring with continuous renal replacement therapy (CRRT) assessment.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCommentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentCount_NoThrow()
    {
        var doc = CreateMedicalDoc();
        var ex = Record.Exception(() => doc.GetCommentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentCount_NonNegative()
    {
        var doc = CreateMedicalDoc();
        Assert.True(doc.GetCommentCount() >= 0);
    }

    [Fact]
    public void GetCommentCount_Consistent()
    {
        var doc = CreateMedicalDoc();
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no comments.");
        Assert.Equal(0, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_AfterAddComment_Increases()
    {
        var doc = CreateMedicalDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(1, "Dr Smith", "Confirm KDIGO 2012 definition — check against NICE NG148.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void GetCommentCount_SaveLoad_Consistent()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(2, "Dr Jones", "Check 2021 protocol reference — should be version 3.2.");
        var before = doc.GetCommentCount();
        var path = TempFile("cc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    // -------------------------------------------------------------------------
    // AddComment
    // -------------------------------------------------------------------------

    [Fact]
    public void AddComment_NoThrow()
    {
        var doc = CreateMedicalDoc();
        var ex = Record.Exception(() => doc.AddComment(0, "Reviewer", "Introduction needs updating per NICE 2024."));
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Increases_Count()
    {
        var doc = CreateMedicalDoc();
        var before = doc.GetCommentCount();
        doc.AddComment(3, "Dr Williams", "Stage 1 threshold — verify against local creatinine assay calibration.");
        Assert.Equal(before + 1, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_SaveLoad_Persists()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(4, "Dr Brown", "CRRT indication — add haemofiltration dose recommendation (25 mL/kg/hr).");
        var before = doc.GetCommentCount();
        var path = TempFile("ac_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCommentCount());
    }

    [Fact]
    public void AddComment_Multiple()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(0, "Author", "Comment 1: KDIGO reference updated.");
        doc.AddComment(1, "Reviewer", "Comment 2: 2021 date needs correction.");
        doc.AddComment(3, "Clinical Lead", "Comment 3: urine output threshold — check paediatric guidance excluded.");
        Assert.Equal(3, doc.GetCommentCount());
    }

    [Fact]
    public void AddComment_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(2, "Reviewer", "HTML export comment — verify CSS for annotation display.");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(1, "Editor", "Markdown export comment — footnote or sidebar?");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddComment_Then_GetWordCount_Positive()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(0, "Author", "Word count comment — include protocol title in word count?");
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetCommentText
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCommentText_NoThrow()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(1, "Reviewer", "Text retrieval — check serum creatinine units μmol/L vs mg/dL.");
        var ex = Record.Exception(() => doc.GetCommentText(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCommentText_NonNull()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(2, "Pharmacist", "Non-null comment — STOP medications: NSAIDs, ACEi/ARBs per AKI-ON-CKD guidance.");
        Assert.NotNull(doc.GetCommentText(0));
    }

    [Fact]
    public void GetCommentText_Consistent()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(0, "Audit", "Consistent comment — protocol version control tracked in SharePoint.");
        Assert.Equal(doc.GetCommentText(0), doc.GetCommentText(0));
    }

    [Fact]
    public void GetCommentText_SaveLoad_Consistent()
    {
        var doc = CreateMedicalDoc();
        doc.AddComment(3, "Clinical Lead", "Save-load comment — RRT initiation — add PICD assessment timing.");
        var path = TempFile("ct_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCommentText(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddComment_GetCommentCount_GetCommentText_SaveToFile_Pipeline()
    {
        // Technical specification — formal document review workflow for avionics software
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Avionics Software Requirements Specification: Flight Management System Navigation Mode Sequencing — DO-178C Level A", 1);
        doc.AppendParagraph("This specification defines the requirements for the Navigation Mode Sequencing (NMS) function of the Flight Management System (FMS), developed in accordance with DO-178C Software Considerations in Airborne Systems at Design Assurance Level A (catastrophic failure condition).");
        doc.AppendParagraph("All requirements are traceable to the System Requirements Specification FMS-SRS-001 Rev E and the Safety Assessment FMS-SA-003 Rev C, approved by the aircraft OEM and submitted to EASA under TC application 20-0187.");

        doc.InsertHeading(3, "High-Level Requirements", 2);
        doc.AppendParagraph("HLR-NMS-001: The NMS function shall sequence navigation modes in the order: Manual, VOR/DME, ILS, RNP-AR, LNAV/VNAV, with transition conditions as defined in the Navigation Mode Transition Matrix (NMTM-001).");
        doc.AppendParagraph("HLR-NMS-002: The NMS function shall detect and annunciate mode reversions to the crew within 250 milliseconds of the triggering condition, using ARINC 429 label 270 on bus FMS-OUT-1.");

        doc.InsertHeading(6, "Low-Level Requirements", 2);
        doc.AppendParagraph("LLR-NMS-001: The mode sequencer state machine shall be implemented as a pure function with no side effects, accepting the current state vector and returning the next state vector and output annunciation list.");
        doc.AppendParagraph("LLR-NMS-002: All mode transition guards shall be evaluated within a single 20-millisecond execution cycle, with worst-case execution time (WCET) verified by structural coverage analysis achieving MC/DC at 100%.");

        doc.InsertHeading(9, "Verification Requirements", 1);
        doc.AppendParagraph("VR-NMS-001: System testing shall include 47 test cases covering all mode transitions in the NMTM-001, executed on target hardware (PowerPC 603e processor) at nominal and worst-case timing conditions.");
        doc.AppendParagraph("VR-NMS-002: Code coverage analysis using LDRA Testbed shall demonstrate 100% statement, decision, and MC/DC coverage across all NMS source modules before Stage 3 review submission.");

        Assert.Equal(12, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetCommentCount());

        // AddComment — peer review annotations for DO-178C formal review
        doc.AddComment(1, "DER_Avionics", "FMS-SRS-001 Rev E — confirm current revision; Rev F was issued 2024-03-15 following AOG incident.");
        Assert.Equal(1, doc.GetCommentCount());

        doc.AddComment(2, "Systems_Lead", "TC application 20-0187 — verify EASA submission date; Type Certificate was extended to include NMS updates per EASA TCDS-A.003 Amendment 18.");
        Assert.Equal(2, doc.GetCommentCount());

        doc.AddComment(3, "Safety_Engineer", "NMTM-001 reference — attach latest revision (Rev D); previous Rev C had error in ILS→RNP-AR transition guard condition (FACT-NMS-047).");
        Assert.Equal(3, doc.GetCommentCount());

        doc.AddComment(4, "Software_Lead", "250ms annunciation budget — ARINC 429 bus latency of up to 100ms must be budgeted; actual NMS contribution = max 150ms (see ICD-FMS-ARINC-001 §4.3).");
        Assert.Equal(4, doc.GetCommentCount());

        doc.AddComment(6, "V_V_Engineer", "WCET = 3.2ms measured on target hardware (Test Report TR-NMS-WCET-001); 20ms cycle budget accommodates 6× margin per DO-178C §6.4.4.2.");
        Assert.Equal(5, doc.GetCommentCount());

        doc.AddComment(8, "Test_Lead", "47 test cases in TP-NMS-SYS-001 Rev B — confirm Stage 2 review passed; 3 deferred tests (TC-NMS-041/042/043) covering simultaneous dual-channel failure — requires updated FMS-SA-003.");
        Assert.Equal(6, doc.GetCommentCount());

        // Consistent
        Assert.Equal(doc.GetCommentCount(), doc.GetCommentCount());

        // GetCommentText
        var text0 = doc.GetCommentText(0);
        Assert.NotNull(text0);
        Assert.Equal(text0, doc.GetCommentText(0)); // consistent

        var text3 = doc.GetCommentText(3);
        Assert.NotNull(text3);

        var text5 = doc.GetCommentText(5);
        Assert.NotNull(text5);

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
        var path = TempFile("dogfood_fms_srs_review.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(6, loaded.GetCommentCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetCommentText(0));
        Assert.NotNull(loaded.GetCommentText(5));

        // AddComment on loaded
        loaded.AddComment(9, "Coverage_Lead", "VR-NMS-002 — LDRA Testbed report LT-NMS-COV-002 confirms 100% MC/DC on 1,247 decisions; 3 uncoverable dead-code constructs deactivated via compiler pragma with DER concurrence.");
        Assert.Equal(7, loaded.GetCommentCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Disposition: all review items addressed. This specification is approved for Stage 3 submission to DER pending receipt of updated FMS-SA-003 Rev D, expected 2024-07-31.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_fms_srs_review_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(7, loaded2.GetCommentCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetCommentText(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddComment(0, "Archive", "Final comment."));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
