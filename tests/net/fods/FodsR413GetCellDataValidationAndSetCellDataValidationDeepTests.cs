// Tests for FodsDocument.GetCellDataValidation, SetCellDataValidation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R413

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R413: Tests for FodsDocument.GetCellDataValidation, SetCellDataValidation deeper.
/// GetCellDataValidation(sheet, row, col): returns the data validation rule string for the cell, or null if none.
/// SetCellDataValidation(sheet, row, col, rule): sets the data validation rule for the cell.
/// Covers: GetCellDataValidation null for new cell; GetCellDataValidation no-throw;
/// SetCellDataValidation no-throw; GetCellDataValidation non-null after Set;
/// GetCellDataValidation consistent after Set; GetCellDataValidation save-load;
/// SetCellDataValidation overwrite; SetCellDataValidation multiple cells;
/// dogfood UK Government procurement approval workflow.
/// </summary>
public class FodsR413GetCellDataValidationAndSetCellDataValidationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR413GetCellDataValidationAndSetCellDataValidationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR413_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateSampleDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Validation");
        doc.SetCellValue("Validation", 0, 0, "Status");
        doc.SetCellValue("Validation", 0, 1, "Score");
        doc.SetCellValue("Validation", 0, 2, "Category");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellDataValidation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataValidation_Null_ForNewCell()
    {
        var doc = CreateSampleDoc();
        Assert.Null(doc.GetCellDataValidation("Validation", 1, 0));
    }

    [Fact]
    public void GetCellDataValidation_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetCellDataValidation("Validation", 1, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellDataValidation_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellDataValidation_NonNull_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed");
        Assert.NotNull(doc.GetCellDataValidation("Validation", 1, 0));
    }

    [Fact]
    public void GetCellDataValidation_Consistent_AfterSet()
    {
        var doc = CreateSampleDoc();
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed");
        var v1 = doc.GetCellDataValidation("Validation", 1, 0);
        var v2 = doc.GetCellDataValidation("Validation", 1, 0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetCellDataValidation_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed");
        var before = doc.GetCellDataValidation("Validation", 1, 0);
        var path = TempFile("dv_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCellDataValidation("Validation", 1, 0));
    }

    [Fact]
    public void SetCellDataValidation_Overwrite()
    {
        var doc = CreateSampleDoc();
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending");
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed,Rejected");
        var v = doc.GetCellDataValidation("Validation", 1, 0);
        Assert.NotNull(v);
    }

    [Fact]
    public void SetCellDataValidation_MultipleCells()
    {
        var doc = CreateSampleDoc();
        doc.SetCellDataValidation("Validation", 1, 0, "list:Active,Pending,Closed");
        doc.SetCellDataValidation("Validation", 1, 1, "range:0,100");
        doc.SetCellDataValidation("Validation", 1, 2, "list:A,B,C,D");
        Assert.NotNull(doc.GetCellDataValidation("Validation", 1, 0));
        Assert.NotNull(doc.GetCellDataValidation("Validation", 1, 1));
        Assert.NotNull(doc.GetCellDataValidation("Validation", 1, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCellDataValidation_SetCellDataValidation_Pipeline()
    {
        // Finance — Crown Commercial Service (CCS): G-Cloud 14 Procurement Approval Workflow
        // Spreadsheet model for tracking supplier evaluation and approval status
        // Data validation enforces controlled vocabulary across evaluator cells

        var doc = FodsDocument.CreateEmpty();

        // Sheet 1: Supplier evaluation (dropdown list validation for status/tier fields)
        doc.AddSheet("Supplier_Evaluation");
        doc.SetCellValue("Supplier_Evaluation", 0, 0, "supplier_id");
        doc.SetCellValue("Supplier_Evaluation", 0, 1, "supplier_name");
        doc.SetCellValue("Supplier_Evaluation", 0, 2, "service_tier");
        doc.SetCellValue("Supplier_Evaluation", 0, 3, "evaluation_status");
        doc.SetCellValue("Supplier_Evaluation", 0, 4, "security_clearance");
        doc.SetCellValue("Supplier_Evaluation", 0, 5, "contract_value_band");

        // No validation on headers
        Assert.Null(doc.GetCellDataValidation("Supplier_Evaluation", 0, 3));

        // Add data rows with validation
        string[] suppliers = { "G14-001", "G14-002", "G14-003", "G14-004", "G14-005" };
        string[] names = { "Kainos Group", "Mott MacDonald Digital", "Sopra Steria", "Capita IT Services", "CGI UK" };
        for (int i = 0; i < 5; i++)
        {
            doc.SetCellValue("Supplier_Evaluation", i + 1, 0, suppliers[i]);
            doc.SetCellValue("Supplier_Evaluation", i + 1, 1, names[i]);
            doc.SetCellValue("Supplier_Evaluation", i + 1, 2, i % 2 == 0 ? "Tier1" : "Tier2");
            doc.SetCellValue("Supplier_Evaluation", i + 1, 3, i < 3 ? "Approved" : "Pending");
            doc.SetCellValue("Supplier_Evaluation", i + 1, 4, i % 3 == 0 ? "SC" : "BPSS");
            doc.SetCellValue("Supplier_Evaluation", i + 1, 5, i % 2 == 0 ? "Band_A" : "Band_B");

            // Apply dropdown validation to status and tier columns
            doc.SetCellDataValidation("Supplier_Evaluation", i + 1, 2, "list:Tier1,Tier2,Tier3");
            doc.SetCellDataValidation("Supplier_Evaluation", i + 1, 3, "list:Approved,Pending,Rejected,Under_Review");
            doc.SetCellDataValidation("Supplier_Evaluation", i + 1, 4, "list:SC,DV,BPSS,CTC");
            doc.SetCellDataValidation("Supplier_Evaluation", i + 1, 5, "list:Band_A,Band_B,Band_C,Band_D");
        }

        // Verify validations set correctly
        var dv_tier = doc.GetCellDataValidation("Supplier_Evaluation", 1, 2);
        Assert.NotNull(dv_tier);
        var dv_status = doc.GetCellDataValidation("Supplier_Evaluation", 1, 3);
        Assert.NotNull(dv_status);
        Assert.Equal(dv_tier, doc.GetCellDataValidation("Supplier_Evaluation", 1, 2)); // consistent

        // Sheet 2: Financial scoring (numeric range validation)
        doc.AddSheet("Financial_Scoring");
        doc.SetCellValue("Financial_Scoring", 0, 0, "supplier_id");
        doc.SetCellValue("Financial_Scoring", 0, 1, "technical_score");
        doc.SetCellValue("Financial_Scoring", 0, 2, "commercial_score");
        doc.SetCellValue("Financial_Scoring", 0, 3, "social_value_score");

        for (int i = 0; i < 5; i++)
        {
            doc.SetCellValue("Financial_Scoring", i + 1, 0, suppliers[i]);
            doc.SetCellValue("Financial_Scoring", i + 1, 1, (70 + i * 3).ToString());
            doc.SetCellValue("Financial_Scoring", i + 1, 2, (65 + i * 2).ToString());
            doc.SetCellValue("Financial_Scoring", i + 1, 3, (80 + i).ToString());

            // Numeric range validation for score columns (0-100)
            doc.SetCellDataValidation("Financial_Scoring", i + 1, 1, "range:0,100");
            doc.SetCellDataValidation("Financial_Scoring", i + 1, 2, "range:0,100");
            doc.SetCellDataValidation("Financial_Scoring", i + 1, 3, "range:0,100");
        }

        var dv_score = doc.GetCellDataValidation("Financial_Scoring", 1, 1);
        Assert.NotNull(dv_score);

        // Cells without validation
        Assert.Null(doc.GetCellDataValidation("Financial_Scoring", 0, 1)); // header row
        Assert.Null(doc.GetCellDataValidation("Supplier_Evaluation", 0, 0)); // supplier_id header

        // Overwrite validation
        doc.SetCellDataValidation("Supplier_Evaluation", 1, 3, "list:Approved,Pending,Rejected");
        var overwritten = doc.GetCellDataValidation("Supplier_Evaluation", 1, 3);
        Assert.NotNull(overwritten);

        // SaveToFile
        var path = TempFile("ccs_gcloud14_evaluation.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        var loadedDvTier = loaded.GetCellDataValidation("Supplier_Evaluation", 1, 2);
        Assert.Equal(dv_tier, loadedDvTier);
        var loadedDvStatus = loaded.GetCellDataValidation("Supplier_Evaluation", 1, 3);
        Assert.NotNull(loadedDvStatus);
        var loadedDvScore = loaded.GetCellDataValidation("Financial_Scoring", 1, 1);
        Assert.Equal(dv_score, loadedDvScore);

        // Verify no validation on header cells after load
        Assert.Null(loaded.GetCellDataValidation("Supplier_Evaluation", 0, 3));

        var ex1 = Record.Exception(() => loaded.GetCellDataValidation("Supplier_Evaluation", 1, 2));
        var ex2 = Record.Exception(() => loaded.SetCellDataValidation("Supplier_Evaluation", 6, 3, "list:Approved"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
