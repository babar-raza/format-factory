// Tests for FodsDocument.GetSheetProtection, SetSheetProtection, IsSheetProtected deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R340

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R340: Tests for FodsDocument.GetSheetProtection, SetSheetProtection, IsSheetProtected deeper.
/// IsSheetProtected(sheet): returns true if the specified sheet has protection enabled.
/// SetSheetProtection(sheet, protect, password): enables or disables protection on the sheet.
/// GetSheetProtection(sheet): returns the protection settings for the specified sheet.
/// Covers: IsSheetProtected no-throw; IsSheetProtected false for unprotected sheet;
/// IsSheetProtected consistent; IsSheetProtected save-load;
/// SetSheetProtection no-throw; SetSheetProtection enables protection; SetSheetProtection save-load;
/// SetSheetProtection multiple sheets; SetSheetProtection then ExportToHtml no-throw;
/// GetSheetProtection no-throw; GetSheetProtection non-null; GetSheetProtection consistent;
/// GetSheetProtection save-load;
/// dogfood CreateDoc→SetSheetProtection→IsSheetProtected→GetSheetProtection→SaveToFile pipeline.
/// </summary>
public class FodsR340GetSheetProtectionAndSetSheetProtectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR340GetSheetProtectionAndSetSheetProtectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR340_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateBudgetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Assumptions");
        doc.SetCellValue("Assumptions", 0, 0, "Revenue Growth Rate");
        doc.SetCellValue("Assumptions", 1, 0, "5.0%");
        doc.SetCellValue("Assumptions", 0, 1, "Inflation Rate");
        doc.SetCellValue("Assumptions", 1, 1, "3.2%");
        doc.AddSheet("P&L");
        doc.SetCellValue("P&L", 0, 0, "Revenue");
        doc.SetCellValue("P&L", 1, 0, "1000000");
        doc.SetCellValue("P&L", 0, 1, "OpEx");
        doc.SetCellValue("P&L", 1, 1, "750000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // IsSheetProtected
    // -------------------------------------------------------------------------

    [Fact]
    public void IsSheetProtected_NoThrow()
    {
        var doc = CreateBudgetDoc();
        var ex = Record.Exception(() => doc.IsSheetProtected("Assumptions"));
        Assert.Null(ex);
    }

    [Fact]
    public void IsSheetProtected_False_ForUnprotectedSheet()
    {
        var doc = CreateBudgetDoc();
        Assert.False(doc.IsSheetProtected("Assumptions"));
    }

    [Fact]
    public void IsSheetProtected_Consistent()
    {
        var doc = CreateBudgetDoc();
        Assert.Equal(doc.IsSheetProtected("P&L"), doc.IsSheetProtected("P&L"));
    }

    [Fact]
    public void IsSheetProtected_SaveLoad_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("Assumptions", true, "SecurePass1");
        var before = doc.IsSheetProtected("Assumptions");
        var path = TempFile("isp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.IsSheetProtected("Assumptions"));
    }

    // -------------------------------------------------------------------------
    // SetSheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSheetProtection_NoThrow()
    {
        var doc = CreateBudgetDoc();
        var ex = Record.Exception(() => doc.SetSheetProtection("Assumptions", true, "TestPass123"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSheetProtection_Enables_Protection()
    {
        var doc = CreateBudgetDoc();
        Assert.False(doc.IsSheetProtected("P&L"));
        doc.SetSheetProtection("P&L", true, "BudgetLock2024");
        Assert.True(doc.IsSheetProtected("P&L"));
    }

    [Fact]
    public void SetSheetProtection_SaveLoad_Persists()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("Assumptions", true, "AssumptionsLock");
        var path = TempFile("ssp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.IsSheetProtected("Assumptions"));
    }

    [Fact]
    public void SetSheetProtection_MultipleSheets()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("Assumptions", true, "Pass1");
        doc.SetSheetProtection("P&L", true, "Pass2");
        Assert.True(doc.IsSheetProtected("Assumptions"));
        Assert.True(doc.IsSheetProtected("P&L"));
    }

    [Fact]
    public void SetSheetProtection_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("P&L", true, "TestPass");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetSheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetProtection_NoThrow()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("Assumptions", true, "Pass");
        var ex = Record.Exception(() => doc.GetSheetProtection("Assumptions"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSheetProtection_NonNull()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("P&L", true, "PLPass");
        Assert.NotNull(doc.GetSheetProtection("P&L"));
    }

    [Fact]
    public void GetSheetProtection_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("Assumptions", true, "Pass");
        Assert.Equal(doc.GetSheetProtection("Assumptions"), doc.GetSheetProtection("Assumptions"));
    }

    [Fact]
    public void GetSheetProtection_SaveLoad_Consistent()
    {
        var doc = CreateBudgetDoc();
        doc.SetSheetProtection("P&L", true, "PLSave");
        var path = TempFile("gsp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.NotNull(loaded.GetSheetProtection("P&L"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetSheetProtection_IsSheetProtected_GetSheetProtection_SaveToFile_Pipeline()
    {
        // Financial model — IFRS 17 insurance contract liability workbook
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inputs");
        doc.SetCellValue("Inputs", 0, 0, "Parameter");
        doc.SetCellValue("Inputs", 0, 1, "Value");
        string[,] inputs = {
            { "Discount Rate (risk-free)", "3.50%" },
            { "Risk Adjustment (CoC)", "4.00%" },
            { "Contract Boundary (months)", "12" },
            { "Expected Claims Loss Ratio", "65%" },
            { "Expense Ratio", "15%" },
            { "Reinsurance Ceded %", "20%" },
        };
        for (int i = 0; i < inputs.GetLength(0); i++)
        {
            doc.SetCellValue("Inputs", i + 1, 0, inputs[i, 0]);
            doc.SetCellValue("Inputs", i + 1, 1, inputs[i, 1]);
        }

        doc.AddSheet("BBA_Model");
        doc.SetCellValue("BBA_Model", 0, 0, "Cohort");
        doc.SetCellValue("BBA_Model", 0, 1, "GIC_Start");
        doc.SetCellValue("BBA_Model", 0, 2, "FCF");
        doc.SetCellValue("BBA_Model", 0, 3, "RA");
        doc.SetCellValue("BBA_Model", 0, 4, "CSM");
        for (int i = 1; i <= 8; i++)
        {
            doc.SetCellValue("BBA_Model", i, 0, $"2024Q{(i - 1) / 2 + 1}");
            doc.SetCellValue("BBA_Model", i, 1, (100000 * i).ToString());
            doc.SetCellValue("BBA_Model", i, 2, (65000 * i).ToString());
            doc.SetCellValue("BBA_Model", i, 3, (4000 * i).ToString());
            doc.SetCellValue("BBA_Model", i, 4, (31000 * i).ToString());
        }

        doc.AddSheet("Audit_Trail");
        doc.SetCellValue("Audit_Trail", 0, 0, "Prepared by");
        doc.SetCellValue("Audit_Trail", 1, 0, "Actuarial Finance Team");
        doc.SetCellValue("Audit_Trail", 0, 1, "Review date");
        doc.SetCellValue("Audit_Trail", 1, 1, "2024-12-31");

        // Verify unprotected initially
        Assert.False(doc.IsSheetProtected("Inputs"));
        Assert.False(doc.IsSheetProtected("BBA_Model"));
        Assert.False(doc.IsSheetProtected("Audit_Trail"));

        // SetSheetProtection — lock Inputs sheet (actuarial assumptions locked)
        doc.SetSheetProtection("Inputs", true, "IFRS17Inputs2024!");
        Assert.True(doc.IsSheetProtected("Inputs"));
        Assert.False(doc.IsSheetProtected("BBA_Model")); // model unlocked for review

        // SetSheetProtection — lock Audit_Trail
        doc.SetSheetProtection("Audit_Trail", true, "AuditLock!");
        Assert.True(doc.IsSheetProtected("Audit_Trail"));

        // Consistent
        Assert.Equal(doc.IsSheetProtected("Inputs"), doc.IsSheetProtected("Inputs"));
        Assert.Equal(doc.IsSheetProtected("BBA_Model"), doc.IsSheetProtected("BBA_Model"));

        // GetSheetProtection
        var inputsProt = doc.GetSheetProtection("Inputs");
        Assert.NotNull(inputsProt);
        Assert.Equal(inputsProt, doc.GetSheetProtection("Inputs")); // consistent

        var auditProt = doc.GetSheetProtection("Audit_Trail");
        Assert.NotNull(auditProt);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // GetCellValue still works through protection
        Assert.Equal("3.50%", doc.GetCellValue("Inputs", 1, 1));
        Assert.Equal("65000", doc.GetCellValue("BBA_Model", 1, 2));

        // SaveToFile
        var path = TempFile("dogfood_ifrs17.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify protection preserved
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.IsSheetProtected("Inputs"));
        Assert.False(loaded.IsSheetProtected("BBA_Model"));
        Assert.True(loaded.IsSheetProtected("Audit_Trail"));
        Assert.NotNull(loaded.GetSheetProtection("Inputs"));

        // SetSheetProtection on loaded — lock model for sign-off
        loaded.SetSheetProtection("BBA_Model", true, "BBAModelFinal!");
        Assert.True(loaded.IsSheetProtected("BBA_Model"));

        // Final save
        var path2 = TempFile("dogfood_ifrs17_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.True(loaded2.IsSheetProtected("Inputs"));
        Assert.True(loaded2.IsSheetProtected("BBA_Model"));
        Assert.True(loaded2.IsSheetProtected("Audit_Trail"));
        Assert.NotNull(loaded2.GetSheetProtection("BBA_Model"));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.GetCellValue("Inputs", 1, 0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
