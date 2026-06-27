// Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount, GetTableColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R344

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R344: Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount, GetTableColumnCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// AddTable(name, rows, columns): inserts a new table with the given dimensions.
/// GetTableRowCount(tableIndex): returns the number of rows in the table at the given index.
/// GetTableColumnCount(tableIndex): returns the number of columns in the table at the given index.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount zero for new doc; GetTableCount after AddTable increases;
/// GetTableCount save-load;
/// AddTable no-throw; AddTable increases count; AddTable save-load;
/// AddTable multiple; AddTable then ExportToHtml no-throw;
/// AddTable then ExportToMarkdown no-throw; AddTable then GetWordCount positive;
/// GetTableRowCount no-throw; GetTableRowCount matches input; GetTableColumnCount no-throw;
/// GetTableColumnCount matches input; GetTableRowCount save-load;
/// dogfood CreateDoc→AddTable→GetTableCount→GetTableRowCount→GetTableColumnCount→SaveToFile pipeline.
/// </summary>
public class FodtR344GetTableCountAndAddTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR344GetTableCountAndAddTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR344_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateReportDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Technical Review: Software System Engineering Standards Compliance Report", 1);
        doc.AppendParagraph("This report presents the findings of the annual technical review conducted in accordance with IEC 61508-3:2010 (Functional Safety) and the organisation's Software Quality Management System (SQMS) requirements.");
        doc.AppendParagraph("The review covers all software components at Safety Integrity Level 2 (SIL 2) or above, including real-time control firmware, safety monitoring subsystems, and the supervisory data acquisition layer.");
        doc.InsertHeading(3, "Scope and Review Criteria", 2);
        doc.AppendParagraph("Software modules under review were selected based on their safety function classification in the Hazard and Risk Assessment (HRA-2024-001) and their change history since the previous review cycle.");
        doc.AppendParagraph("Review criteria are aligned with IEC 61508-3 Annexes A and B requirements for SIL 2, including static analysis, code coverage targets (MC/DC ≥ 95%), and formal document traceability.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateReportDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateReportDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateReportDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no tables.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAddTable_Increases()
    {
        var doc = CreateReportDoc();
        var before = doc.GetTableCount();
        doc.AddTable("Review_Summary", 5, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Coverage_Table", 6, 3);
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // AddTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_NoThrow()
    {
        var doc = CreateReportDoc();
        var ex = Record.Exception(() => doc.AddTable("Test_Table", 3, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Increases_Count()
    {
        var doc = CreateReportDoc();
        var before = doc.GetTableCount();
        doc.AddTable("SIL_Summary", 4, 5);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_SaveLoad_Persists()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Traceability_Matrix", 7, 6);
        var before = doc.GetTableCount();
        var path = TempFile("at_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void AddTable_Multiple()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Table_A", 3, 3);
        doc.AddTable("Table_B", 4, 5);
        doc.AddTable("Table_C", 2, 4);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateReportDoc();
        doc.AddTable("HTML_Table", 4, 3);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Markdown_Table", 3, 4);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_GetWordCount_Positive()
    {
        var doc = CreateReportDoc();
        doc.AddTable("WordCount_Table", 5, 3);
        Assert.True(doc.GetWordCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableRowCount / GetTableColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NoThrow()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Rows_Table", 6, 4);
        var ex = Record.Exception(() => doc.GetTableRowCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableRowCount_Matches_Input()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Rows_Table", 6, 4);
        Assert.Equal(6, doc.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableColumnCount_NoThrow()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Cols_Table", 3, 7);
        var ex = Record.Exception(() => doc.GetTableColumnCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableColumnCount_Matches_Input()
    {
        var doc = CreateReportDoc();
        doc.AddTable("Cols_Table", 3, 7);
        Assert.Equal(7, doc.GetTableColumnCount(0));
    }

    [Fact]
    public void GetTableRowCount_SaveLoad_Consistent()
    {
        var doc = CreateReportDoc();
        doc.AddTable("SaveLoad_Table", 5, 4);
        var path = TempFile("trc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetTableRowCount(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddTable_GetTableCount_GetTableRowCount_GetTableColumnCount_Pipeline()
    {
        // Defence procurement — equipment support contract management document with data tables
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Defence Equipment Support: Through-Life Support Contract Performance Report — DEFCON 5C/MOD Form 640 Compliant", 1);
        doc.AppendParagraph("This report documents contractor performance against Key Performance Indicators (KPIs) defined in the Through-Life Support Contract (TLSC) DE&S/2024/TLS-001, covering availability, reliability, maintainability, and supportability (ARMS) metrics for the equipment programme.");
        doc.AppendParagraph("Contract performance is measured against the Operational Availability (Ao) target of 87% and the Logistic Delay Time (LDT) target of not exceeding 15 days for Category A1 defects, in accordance with the TLSC Statement of Work and Performance Framework.");

        doc.InsertHeading(3, "Platform Availability Summary", 2);
        doc.AppendParagraph("Table 1 presents the monthly Operational Availability (Ao) achieved against the contractual target for each platform variant across the reporting period. Ao is calculated as: Ao = MTBF / (MTBF + MDT) where MDT includes Active Maintenance Time (AMT) and Logistic Delay Time (LDT).");
        doc.AppendParagraph("Platform variant PLATFORM-A achieved average Ao of 88.4% against the 87% target, while PLATFORM-B underperformed at 83.1%, triggering a Contractor Performance Notice (CPN-2024-047) under DEFCON 530.");

        doc.InsertHeading(6, "Defect Analysis", 2);
        doc.AppendParagraph("Category A1 critical defects (affecting mission capability) totalled 23 across the reporting period, of which 19 (82.6%) were resolved within the 15-day LDT target. The 4 exceptions involved Long Lead Time Items (LLTIs) requiring Ministry of Munitions approval under ITAR constraints.");
        doc.AppendParagraph("Category A2 defects (significant mission degradation, 30-day target) showed 97.3% compliance: 36 of 37 defects resolved within target. The single exception involved a specialist avionics component sourced from a single-source supplier in the USA.");

        doc.InsertHeading(9, "DRACAS Reliability Data", 1);
        doc.AppendParagraph("The Defect Reporting, Analysis and Corrective Action System (DRACAS) records 312 field reliability events in the reporting period. Mean Time Between Failures (MTBF) achieved was 847 hours against the contractual target of 800 hours, representing 5.9% margin above target.");
        doc.AppendParagraph("Corrective Action Reports (CARs) issued: 7 open CARs from prior period, 12 new CARs raised, 9 CARs closed. 3 CARs escalated to Defect Investigation Reports (DIRs) for systemic engineering root cause analysis. DIR-2024-003 (fuel system vapour lock) remains open pending contractor design authority response.");

        Assert.Equal(10, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetTableCount());

        // AddTable — contract performance data tables
        doc.AddTable("Ao_Monthly_Summary", 13, 5); // 12 months + header, 5 platform variants + col header
        Assert.Equal(1, doc.GetTableCount());
        Assert.Equal(13, doc.GetTableRowCount(0));
        Assert.Equal(5, doc.GetTableColumnCount(0));

        doc.AddTable("Defect_Category_Summary", 4, 6); // A1/A2/B/C categories + totals
        Assert.Equal(2, doc.GetTableCount());
        Assert.Equal(4, doc.GetTableRowCount(1));
        Assert.Equal(6, doc.GetTableColumnCount(1));

        doc.AddTable("DRACAS_Reliability_Events", 8, 7); // 7 subsystems, 7 metric cols
        Assert.Equal(3, doc.GetTableCount());
        Assert.Equal(8, doc.GetTableRowCount(2));
        Assert.Equal(7, doc.GetTableColumnCount(2));

        doc.AddTable("CAR_Status_Register", 13, 8); // 12 CARs + header
        Assert.Equal(4, doc.GetTableCount());
        Assert.Equal(13, doc.GetTableRowCount(3));
        Assert.Equal(8, doc.GetTableColumnCount(3));

        doc.AddTable("LLTI_Critical_Items", 6, 5); // 5 LLTIs + header
        Assert.Equal(5, doc.GetTableCount());
        Assert.Equal(6, doc.GetTableRowCount(4));
        Assert.Equal(5, doc.GetTableColumnCount(4));

        // Consistent
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());

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
        var path = TempFile("dogfood_tlsc_performance.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetTableCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.Equal(13, loaded.GetTableRowCount(0));
        Assert.Equal(5, loaded.GetTableColumnCount(0));
        Assert.Equal(4, loaded.GetTableRowCount(1));
        Assert.Equal(6, loaded.GetTableColumnCount(1));

        // AddTable on loaded
        loaded.AddTable("KPI_Scorecard", 10, 4);
        Assert.Equal(6, loaded.GetTableCount());
        Assert.Equal(10, loaded.GetTableRowCount(5));
        Assert.Equal(4, loaded.GetTableColumnCount(5));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: contractor performance is broadly compliant with TLSC obligations. Ao target achieved for PLATFORM-A; remediation plan agreed for PLATFORM-B to restore compliance by Q3. DRACAS MTBF target achieved; CAR closure rate requires monitoring.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_tlsc_performance_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(6, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.Equal(13, loaded2.GetTableRowCount(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddTable("Final_Table", 3, 3));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
