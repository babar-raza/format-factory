// Tests for FodtDocument.GetSectionCount, GetPageCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R368

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R368: Tests for FodtDocument.GetSectionCount, GetPageCount deeper.
/// GetSectionCount(): returns the number of sections in the document.
/// GetPageCount(): returns the estimated number of pages in the document.
/// Covers: GetSectionCount no-throw; GetSectionCount non-negative; GetSectionCount consistent;
/// GetSectionCount save-load; GetPageCount no-throw; GetPageCount positive;
/// GetPageCount consistent; GetPageCount save-load;
/// GetPageCount increases as content added; GetSectionCount save-load;
/// InsertSection then GetSectionCount increases; GetPageCount >= 1;
/// dogfood CreateDoc→InsertSection→GetSectionCount→GetPageCount→SaveToFile pipeline.
/// </summary>
public class FodtR368GetSectionCountAndGetPageCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR368GetSectionCountAndGetPageCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR368_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Technical Standard: API Gateway Security Requirements", 1);
        doc.AppendParagraph("This standard defines the security requirements for API gateways deployed within the organisation's technology estate, in accordance with NCSC Cyber Essentials Plus requirements.");
        return doc;
    }

    private static FodtDocument CreateLongDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Information Security Policy Framework", 1);
        for (int i = 0; i < 20; i++)
            doc.AppendParagraph($"This section {i + 1} contains detailed policy requirements governing information security controls across all systems, networks, and data processing activities of the organisation. Each requirement maps directly to ISO/IEC 27001:2022 Annex A controls and must be implemented within the timescales specified in the accompanying Implementation Schedule.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSectionCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSectionCount_NoThrow()
    {
        var doc = CreateShortDoc();
        var ex = Record.Exception(() => doc.GetSectionCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSectionCount_NonNegative()
    {
        var doc = CreateShortDoc();
        Assert.True(doc.GetSectionCount() >= 0);
    }

    [Fact]
    public void GetSectionCount_Consistent()
    {
        var doc = CreateShortDoc();
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount());
    }

    [Fact]
    public void GetSectionCount_SaveLoad_Consistent()
    {
        var doc = CreateShortDoc();
        var before = doc.GetSectionCount();
        var path = TempFile("gsc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSectionCount());
    }

    [Fact]
    public void InsertSection_Then_GetSectionCount_Increases()
    {
        var doc = CreateShortDoc();
        var before = doc.GetSectionCount();
        doc.InsertSection("Annex A: Control Mapping");
        Assert.True(doc.GetSectionCount() > before);
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
    public void GetPageCount_Consistent()
    {
        var doc = CreateShortDoc();
        Assert.Equal(doc.GetPageCount(), doc.GetPageCount());
    }

    [Fact]
    public void GetPageCount_SaveLoad_Consistent()
    {
        var doc = CreateShortDoc();
        var before = doc.GetPageCount();
        var path = TempFile("gpc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPageCount());
    }

    [Fact]
    public void GetPageCount_At_Least_One()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Minimal content.");
        Assert.True(doc.GetPageCount() >= 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSectionCount_GetPageCount_SaveToFile_Pipeline()
    {
        // Legal — UK Cabinet Office Model Services Contract (MSC) v3
        // Long-form government IT services contract with multiple sections
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Model Services Contract v3 — Schedule 2: Service Requirements", 1);
        doc.AppendParagraph("This Schedule sets out the Service Requirements for the provision of Digital Transformation Services to the Crown (the 'Authority') by the Supplier, as defined in the Agreement.");
        doc.AppendParagraph("Words and expressions defined in the Agreement shall have the same meaning in this Schedule unless otherwise defined herein.");

        var initialSectionCount = doc.GetSectionCount();
        Assert.True(initialSectionCount >= 0);
        var initialPageCount = doc.GetPageCount();
        Assert.True(initialPageCount >= 1);

        // Section 1: Service Description
        doc.InsertSection("Part 1: Service Description and Scope");
        doc.InsertHeading(3, "1.1 Service Overview", 2);
        doc.AppendParagraph("The Supplier shall provide the Services described in this Schedule throughout the Service Period in accordance with the Service Levels set out in Schedule 3 and the Charges set out in Schedule 4.");
        doc.AppendParagraph("The Services comprise: (a) application development and maintenance services for the Authority's case management platform; (b) cloud infrastructure management and security monitoring; (c) data engineering and analytics platform support; (d) service desk and end-user computing support; and (e) programme management office services.");

        doc.InsertHeading(3, "1.2 Service Commencement and Transition", 2);
        doc.AppendParagraph("The Supplier shall complete the Transition Period within 90 days of the Commencement Date, in accordance with the Transition Plan agreed pursuant to Clause 12 of the Agreement. During the Transition Period, the Supplier shall shadow the Authority's incumbent supplier and conduct knowledge transfer sessions as specified in the Transition Plan.");
        doc.AppendParagraph("The Supplier shall provide a Transition Progress Report to the Authority's Programme Director no less than fortnightly during the Transition Period, in the format specified in Attachment 2A to this Schedule.");

        var sectionCountAfter1 = doc.GetSectionCount();
        Assert.True(sectionCountAfter1 >= initialSectionCount);

        // Section 2: Technical Requirements
        doc.InsertSection("Part 2: Technical Architecture Requirements");
        doc.InsertHeading(3, "2.1 Architecture Principles", 2);
        doc.AppendParagraph("The Supplier shall ensure that all Services and deliverables comply with the Government Technology Standards and the Authority's Enterprise Architecture principles, including: cloud-first design; API-led integration; zero-trust network architecture; DevSecOps practices; and open standards as mandated by CDDO.");
        doc.AppendParagraph("The Supplier shall not introduce proprietary lock-in technologies without the prior written consent of the Authority's Chief Technology Officer and shall maintain portability of all data and configurations throughout the Service Period and following expiry or termination.");

        doc.InsertHeading(3, "2.2 Security Requirements", 2);
        doc.AppendParagraph("The Supplier shall at all times maintain and demonstrate compliance with Cyber Essentials Plus certification and shall provide the Authority with current certification evidence within 30 days of renewal. The Supplier shall implement and maintain security controls aligned to NCSC Cloud Security Principles and shall participate in the Authority's annual penetration testing programme.");
        doc.AppendParagraph("The Supplier shall comply with the Authority's Security Classification Framework and ensure that all systems processing OFFICIAL-SENSITIVE data are segregated from systems processing lower-classification data. The Supplier shall maintain a Security Management System in accordance with ISO/IEC 27001:2022.");

        var sectionCountAfter2 = doc.GetSectionCount();
        Assert.True(sectionCountAfter2 >= sectionCountAfter1);

        // Section 3: Service Levels
        doc.InsertSection("Part 3: Service Level Requirements");
        doc.InsertHeading(3, "3.1 Service Availability", 2);
        doc.AppendParagraph("The Supplier shall maintain Service Availability of not less than 99.9% measured on a calendar month basis for all Priority 1 services, as defined in the Service Catalogue in Attachment 1A to this Schedule. Service Availability shall be measured excluding Planned Maintenance Windows agreed with the Authority in accordance with the Change Management process.");

        doc.InsertHeading(3, "3.2 Incident Response", 2);
        doc.AppendParagraph("The Supplier shall respond to and resolve Incidents in accordance with the Response and Resolution Times specified in the Service Level Agreement at Attachment 3A. Priority 1 Incidents (Critical — service unavailable) shall be acknowledged within 15 minutes of notification and initial workaround provided within 1 hour, with full resolution within 4 hours.");

        var sectionCountAfter3 = doc.GetSectionCount();
        Assert.True(sectionCountAfter3 >= sectionCountAfter2);
        Assert.Equal(doc.GetSectionCount(), doc.GetSectionCount()); // consistent

        var pageCountAfterContent = doc.GetPageCount();
        Assert.True(pageCountAfterContent >= 1);
        Assert.Equal(doc.GetPageCount(), doc.GetPageCount()); // consistent

        // More content → at least as many pages
        Assert.True(pageCountAfterContent >= initialPageCount);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // GetWordCount and GetCharCount
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);

        // SaveToFile
        var path1 = TempFile("dogfood_msc_schedule2.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(doc.GetSectionCount(), loaded.GetSectionCount());
        Assert.Equal(doc.GetPageCount(), loaded.GetPageCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add further section: Schedule Annex
        loaded.InsertSection("Annex 1: Definitions");
        loaded.InsertHeading(3, "Defined Terms", 2);
        loaded.AppendParagraph("'Agreement' means the Model Services Contract entered into between the Authority and the Supplier with effect from the Commencement Date, comprising the Order Form, Schedules 1-8, and the Attachments thereto.");
        loaded.AppendParagraph("'Commencement Date' means the date specified in the Order Form as the date from which the Services are to commence.");
        loaded.AppendParagraph("'Service Level' means the level of service the Supplier is required to provide pursuant to Part 3 of this Schedule and as further particularised in Schedule 3.");

        Assert.True(loaded.GetSectionCount() > doc.GetSectionCount());

        // Final save
        var path2 = TempFile("dogfood_msc_schedule2_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(loaded.GetSectionCount(), final.GetSectionCount());
        Assert.Equal(loaded.GetPageCount(), final.GetPageCount());

        Assert.True(final.GetWordCount() > 0);

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.ExportToMarkdown());
        var ex3 = Record.Exception(() => final.InsertSection("Annex 2: Change Log"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
        Assert.True(final.GetSectionCount() >= loaded.GetSectionCount());
    }
}
