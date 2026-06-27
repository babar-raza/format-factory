// Tests for FodsDocument.GetCellBorder, SetCellBorder deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R375

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R375: Tests for FodsDocument.GetCellBorder, SetCellBorder deeper.
/// GetCellBorder(sheetName, row, col): returns border style for the cell at (row, col).
/// SetCellBorder(sheetName, row, col, borderStyle): sets the border style for a cell.
/// Covers: GetCellBorder no-throw; GetCellBorder consistent; GetCellBorder save-load;
/// SetCellBorder no-throw; SetCellBorder then GetCellBorder non-null;
/// SetCellBorder then GetSheetCount unchanged; SetCellBorder then ExportToCsv no-throw;
/// SetCellBorder then GetCellValue non-null; SetCellBorder save-load;
/// SetCellBorder multiple cells; SetCellBorder with various styles;
/// dogfood CreateDoc→SetCellBorder→GetCellBorder→SaveToFile pipeline.
/// </summary>
public class FodsR375GetCellBorderAndSetCellBorderDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR375GetCellBorderAndSetCellBorderDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR375_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateReportDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Summary");
        doc.SetCellValue("Summary", 0, 0, "Metric");
        doc.SetCellValue("Summary", 0, 1, "Q1_2024");
        doc.SetCellValue("Summary", 0, 2, "Q2_2024");
        doc.SetCellValue("Summary", 0, 3, "Q3_2024");
        doc.SetCellValue("Summary", 0, 4, "Q4_2024");
        string[] metrics = { "Revenue_GBPm", "EBITDA_GBPm", "FCF_GBPm", "Headcount", "Customer_NPS" };
        string[][] values = {
            new[] { "142.3", "156.8", "161.2", "174.9" },
            new[] { "28.4", "31.2", "33.7", "38.1" },
            new[] { "15.2", "18.7", "21.3", "24.6" },
            new[] { "1842", "1891", "1923", "1987" },
            new[] { "42", "45", "47", "51" }
        };
        for (int r = 0; r < metrics.Length; r++)
        {
            doc.SetCellValue("Summary", r + 1, 0, metrics[r]);
            for (int c = 0; c < 4; c++)
                doc.SetCellValue("Summary", r + 1, c + 1, values[r][c]);
        }
        doc.AddSheet("Detail");
        doc.SetCellValue("Detail", 0, 0, "Category");
        doc.SetCellValue("Detail", 0, 1, "Value");
        doc.SetCellValue("Detail", 1, 0, "Cost_A");
        doc.SetCellValue("Detail", 1, 1, "45600");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellBorder
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellBorder_NoThrow()
    {
        var doc = CreateReportDoc();
        var ex = Record.Exception(() => doc.GetCellBorder("Summary", 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellBorder_Consistent()
    {
        var doc = CreateReportDoc();
        Assert.Equal(doc.GetCellBorder("Summary", 0, 0), doc.GetCellBorder("Summary", 0, 0));
    }

    [Fact]
    public void GetCellBorder_SaveLoad_Consistent()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        var path = TempFile("gcb_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellBorder("Summary", 0, 0));
    }

    // -------------------------------------------------------------------------
    // SetCellBorder
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellBorder_NoThrow()
    {
        var doc = CreateReportDoc();
        var ex = Record.Exception(() => doc.SetCellBorder("Summary", 0, 0, "thin"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBorder_Then_GetCellBorder_NonNull()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        Assert.NotNull(doc.GetCellBorder("Summary", 0, 0));
    }

    [Fact]
    public void SetCellBorder_Then_GetSheetCount_Unchanged()
    {
        var doc = CreateReportDoc();
        var before = doc.GetSheetCount();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        Assert.Equal(before, doc.GetSheetCount());
    }

    [Fact]
    public void SetCellBorder_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        var ex = Record.Exception(() => doc.ExportToCsv("Summary"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellBorder_Then_GetCellValue_NonNull()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        Assert.NotNull(doc.GetCellValue("Summary", 0, 0));
    }

    [Fact]
    public void SetCellBorder_SaveLoad_Persists()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thick");
        var path = TempFile("scb_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetCellBorder("Summary", 0, 0));
    }

    [Fact]
    public void SetCellBorder_MultipleCells()
    {
        var doc = CreateReportDoc();
        doc.SetCellBorder("Summary", 0, 0, "thin");
        doc.SetCellBorder("Summary", 0, 1, "thin");
        doc.SetCellBorder("Summary", 0, 2, "thin");
        Assert.NotNull(doc.GetCellBorder("Summary", 0, 0));
        Assert.NotNull(doc.GetCellBorder("Summary", 0, 1));
        Assert.NotNull(doc.GetCellBorder("Summary", 0, 2));
    }

    [Fact]
    public void SetCellBorder_WithDottedStyle_NoThrow()
    {
        var doc = CreateReportDoc();
        var ex = Record.Exception(() => doc.SetCellBorder("Summary", 1, 1, "dotted"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellBorder_GetCellBorder_SaveToFile_Pipeline()
    {
        // Professional services — Big 4 audit workpaper: ISA 540 accounting estimate testing
        // Formatted with cell borders for professional report presentation
        var doc = FodsDocument.CreateEmpty();

        // Estimates Summary sheet — management vs auditor estimates
        doc.AddSheet("Estimates_Summary");
        string[] estHeaders = {
            "Estimate_Description", "Accounting_Standard", "Mgmt_Estimate_GBP",
            "Auditor_Point_Estimate_GBP", "Auditor_Range_Low_GBP", "Auditor_Range_High_GBP",
            "Difference_GBP", "Tolerable_Misstatement_GBP", "Within_Range_YN", "Risk_Assessment"
        };
        for (int c = 0; c < estHeaders.Length; c++)
            doc.SetCellValue("Estimates_Summary", 0, c, estHeaders[c]);

        string[] estimates = {
            "Provisions_for_credit_losses",
            "Warranty_provisions",
            "Defined_benefit_obligation",
            "Goodwill_impairment",
            "Revenue_recognition_POC",
            "Environmental_remediation_provision",
            "Legal_contingencies",
            "Restructuring_provision",
            "Fair_value_Level_3_instruments",
            "Deferred_tax_asset_recoverability"
        };
        var rng = new Random(20241220);
        string[] standards = { "IAS_37", "IFRS_15", "IAS_19", "IAS_36", "IFRS_9", "IFRS_13" };
        string[] risks = { "Low", "Moderate", "High", "Significant" };
        for (int r = 0; r < estimates.Length; r++)
        {
            double mgmt = 1000000 + rng.NextDouble() * 49000000;
            double auditorPt = mgmt * (0.9 + rng.NextDouble() * 0.2);
            double rangeLow = auditorPt * 0.85;
            double rangeHigh = auditorPt * 1.15;
            double diff = mgmt - auditorPt;
            double tolerable = Math.Abs(mgmt) * 0.05;
            bool withinRange = mgmt >= rangeLow && mgmt <= rangeHigh;
            doc.SetCellValue("Estimates_Summary", r + 1, 0, estimates[r]);
            doc.SetCellValue("Estimates_Summary", r + 1, 1, standards[r % standards.Length]);
            doc.SetCellValue("Estimates_Summary", r + 1, 2, $"{mgmt:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 3, $"{auditorPt:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 4, $"{rangeLow:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 5, $"{rangeHigh:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 6, $"{diff:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 7, $"{tolerable:F0}");
            doc.SetCellValue("Estimates_Summary", r + 1, 8, withinRange ? "Y" : "N");
            doc.SetCellValue("Estimates_Summary", r + 1, 9, risks[rng.Next(risks.Length)]);
        }

        // Audit Findings sheet
        doc.AddSheet("Audit_Findings");
        string[] findHeaders = {
            "Finding_Ref", "Description", "IAS_ISA_Ref", "Nature",
            "Proposed_Adjustment_GBP", "Management_Response", "Auditor_Conclusion"
        };
        for (int c = 0; c < findHeaders.Length; c++)
            doc.SetCellValue("Audit_Findings", 0, c, findHeaders[c]);
        string[] findNatures = { "Misstatement", "Disclosure_deficiency", "Control_deficiency", "Going_concern" };
        for (int r = 1; r <= 6; r++)
        {
            doc.SetCellValue("Audit_Findings", r, 0, $"AF-2024-{r:D3}");
            doc.SetCellValue("Audit_Findings", r, 1, $"Audit_finding_{r}");
            doc.SetCellValue("Audit_Findings", r, 2, standards[r % standards.Length]);
            doc.SetCellValue("Audit_Findings", r, 3, findNatures[r % findNatures.Length]);
            doc.SetCellValue("Audit_Findings", r, 4, $"{(rng.NextDouble() * 2000000):F0}");
            doc.SetCellValue("Audit_Findings", r, 5, rng.NextDouble() < 0.7 ? "Accepted" : "Rejected");
            doc.SetCellValue("Audit_Findings", r, 6, rng.NextDouble() < 0.8 ? "Resolved" : "Open");
        }

        Assert.Equal(2, doc.GetSheetCount());
        Assert.Null(doc.GetCellBorder("Estimates_Summary", 0, 0));

        // SetCellBorder — professional formatting for audit workpaper
        // Header row: thick bottom border
        for (int c = 0; c < estHeaders.Length; c++)
            doc.SetCellBorder("Estimates_Summary", 0, c, "thick");

        Assert.NotNull(doc.GetCellBorder("Estimates_Summary", 0, 0));
        Assert.NotNull(doc.GetCellBorder("Estimates_Summary", 0, 1));

        // Data rows: thin borders
        for (int r = 1; r <= estimates.Length; r++)
            for (int c = 0; c < estHeaders.Length; c++)
                doc.SetCellBorder("Estimates_Summary", r, c, "thin");

        Assert.NotNull(doc.GetCellBorder("Estimates_Summary", 1, 0));

        // Audit Findings: mixed borders
        for (int c = 0; c < findHeaders.Length; c++)
            doc.SetCellBorder("Audit_Findings", 0, c, "thick");
        for (int r = 1; r <= 6; r++)
            doc.SetCellBorder("Audit_Findings", r, 4, "dotted"); // proposed adjustments highlighted

        Assert.NotNull(doc.GetCellBorder("Audit_Findings", 0, 0));

        // Sheet count unchanged
        Assert.Equal(2, doc.GetSheetCount());

        // Consistent
        Assert.Equal(doc.GetCellBorder("Estimates_Summary", 0, 0), doc.GetCellBorder("Estimates_Summary", 0, 0));

        // ExportToCsv
        var csv = doc.ExportToCsv("Estimates_Summary");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // GetCellValue
        Assert.Equal("Estimate_Description", doc.GetCellValue("Estimates_Summary", 0, 0));

        // SaveToFile
        var path = TempFile("dogfood_audit_workpaper_isa540.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetSheetCount());
        Assert.NotNull(loaded.GetCellBorder("Estimates_Summary", 0, 0));
        Assert.Equal("Estimate_Description", loaded.GetCellValue("Estimates_Summary", 0, 0));

        // Additional sheet with borders
        loaded.AddSheet("Materiality");
        loaded.SetCellValue("Materiality", 0, 0, "Benchmark");
        loaded.SetCellValue("Materiality", 0, 1, "Amount_GBP");
        loaded.SetCellValue("Materiality", 1, 0, "Overall_Materiality");
        loaded.SetCellValue("Materiality", 1, 1, "4200000");
        loaded.SetCellBorder("Materiality", 0, 0, "thin");
        loaded.SetCellBorder("Materiality", 0, 1, "thin");
        Assert.Equal(3, loaded.GetSheetCount());
        Assert.NotNull(loaded.GetCellBorder("Materiality", 0, 0));

        // Final save
        var path2 = TempFile("dogfood_audit_workpaper_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(3, loaded2.GetSheetCount());
        Assert.NotNull(loaded2.GetCellBorder("Estimates_Summary", 0, 0));
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Estimates_Summary"));
        var ex2 = Record.Exception(() => loaded2.SetCellBorder("Materiality", 1, 0, "thick"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
