// Tests for FodsDocument.GetWorksheetProtection, SetWorksheetProtection deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R425

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R425: Tests for FodsDocument.GetWorksheetProtection, SetWorksheetProtection deeper.
/// GetWorksheetProtection(sheetIndex): returns true if the sheet at the given index is protected.
/// SetWorksheetProtection(sheetIndex, protect): enables or disables protection on the given sheet.
/// Covers: GetWorksheetProtection no-throw; GetWorksheetProtection returns bool;
/// GetWorksheetProtection false for new sheet; GetWorksheetProtection consistent;
/// GetWorksheetProtection save-load;
/// SetWorksheetProtection no-throw; SetWorksheetProtection enables protection;
/// SetWorksheetProtection disables protection; SetWorksheetProtection toggleable;
/// SetWorksheetProtection save-load; dogfood pipeline.
/// </summary>
public class FodsR425GetWorksheetProtectionAndSetWorksheetProtectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR425GetWorksheetProtectionAndSetWorksheetProtectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR425_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateMultiSheetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Summary");
        doc.SetCellValue(0, 0, 0, "Report");
        doc.SetCellValue(0, 0, 1, "Value");
        doc.AddSheet("Calculations");
        doc.SetCellValue(1, 0, 0, "Formula");
        doc.AddSheet("Config");
        doc.SetCellValue(2, 0, 0, "Parameter");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWorksheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWorksheetProtection_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.GetWorksheetProtection(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetWorksheetProtection_ReturnsBool()
    {
        var doc = CreateMultiSheetDoc();
        var result = doc.GetWorksheetProtection(0);
        Assert.True(result == true || result == false);
    }

    [Fact]
    public void GetWorksheetProtection_False_ForNewSheet()
    {
        var doc = CreateMultiSheetDoc();
        Assert.False(doc.GetWorksheetProtection(0));
    }

    [Fact]
    public void GetWorksheetProtection_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal(doc.GetWorksheetProtection(0), doc.GetWorksheetProtection(0));
    }

    [Fact]
    public void GetWorksheetProtection_SaveLoad_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(0, true);
        var before = doc.GetWorksheetProtection(0);
        var path = TempFile("wp_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWorksheetProtection(0));
    }

    // -------------------------------------------------------------------------
    // SetWorksheetProtection
    // -------------------------------------------------------------------------

    [Fact]
    public void SetWorksheetProtection_NoThrow()
    {
        var doc = CreateMultiSheetDoc();
        var ex = Record.Exception(() => doc.SetWorksheetProtection(0, true));
        Assert.Null(ex);
    }

    [Fact]
    public void SetWorksheetProtection_Enables_Protection()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(0, true);
        Assert.True(doc.GetWorksheetProtection(0));
    }

    [Fact]
    public void SetWorksheetProtection_Disables_Protection()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(0, true);
        doc.SetWorksheetProtection(0, false);
        Assert.False(doc.GetWorksheetProtection(0));
    }

    [Fact]
    public void SetWorksheetProtection_Toggleable()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(1, true);
        Assert.True(doc.GetWorksheetProtection(1));
        doc.SetWorksheetProtection(1, false);
        Assert.False(doc.GetWorksheetProtection(1));
        doc.SetWorksheetProtection(1, true);
        Assert.True(doc.GetWorksheetProtection(1));
    }

    [Fact]
    public void SetWorksheetProtection_SaveLoad_Consistent()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(2, true);
        var path = TempFile("wp_set_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.GetWorksheetProtection(2));
        Assert.False(loaded.GetWorksheetProtection(0)); // other sheets unaffected
    }

    [Fact]
    public void SetWorksheetProtection_Independent_PerSheet()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetWorksheetProtection(0, false);
        doc.SetWorksheetProtection(1, true);
        doc.SetWorksheetProtection(2, false);
        Assert.False(doc.GetWorksheetProtection(0));
        Assert.True(doc.GetWorksheetProtection(1));
        Assert.False(doc.GetWorksheetProtection(2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWorksheetProtection_SetWorksheetProtection_Pipeline()
    {
        // Finance — HM Treasury / Debt Management Office: Gilt Issuance Programme Workbook
        // Multi-sheet model with protected formula sheets and unprotected input sheets
        // Worksheet protection prevents accidental formula overwrite in distributed models

        var doc = FodsDocument.CreateEmpty();

        // Sheet 0: Input assumptions (editable — no protection)
        doc.AddSheet("Assumptions");
        doc.SetCellValue(0, 0, 0, "Parameter");
        doc.SetCellValue(0, 0, 1, "Value");
        doc.SetCellValue(0, 0, 2, "Notes");
        string[] params_ = {
            "Gross_Issuance_GBPbn", "Net_Financing_Requirement_GBPbn",
            "Short_Gilt_Share_Pct", "Long_Gilt_Share_Pct", "Index_Linked_Share_Pct",
            "Base_Rate_Pct", "OBR_GDP_Growth_Pct"
        };
        double[] vals = { 278.0, 138.5, 35.0, 45.0, 20.0, 5.25, 1.8 };
        for (int i = 0; i < params_.Length; i++)
        {
            doc.SetCellValue(0, i + 1, 0, params_[i]);
            doc.SetCellValue(0, i + 1, 1, vals[i].ToString("F2"));
            doc.SetCellValue(0, i + 1, 2, "Editable");
        }

        // Sheet 1: Calculations (protected)
        doc.AddSheet("Calculations");
        doc.SetCellValue(1, 0, 0, "Metric");
        doc.SetCellValue(1, 0, 1, "Q1_GBPbn");
        doc.SetCellValue(1, 0, 2, "Q2_GBPbn");
        doc.SetCellValue(1, 0, 3, "Q3_GBPbn");
        doc.SetCellValue(1, 0, 4, "Q4_GBPbn");
        doc.SetCellValue(1, 1, 0, "Short_Gilts");
        doc.SetCellValue(1, 1, 1, "24.3");
        doc.SetCellValue(1, 1, 2, "25.1");
        doc.SetCellValue(1, 1, 3, "23.8");
        doc.SetCellValue(1, 1, 4, "24.7");
        doc.SetCellValue(1, 2, 0, "Long_Gilts");
        doc.SetCellValue(1, 2, 1, "31.2");
        doc.SetCellValue(1, 2, 2, "30.8");
        doc.SetCellValue(1, 2, 3, "32.4");
        doc.SetCellValue(1, 2, 4, "30.1");

        // Sheet 2: Summary dashboard (protected)
        doc.AddSheet("Summary");
        doc.SetCellValue(2, 0, 0, "DMO_Gilt_Issuance_Programme_2024-25");
        doc.SetCellValue(2, 1, 0, "Total_Gross_Issuance");
        doc.SetCellValue(2, 1, 1, "278.0");
        doc.SetCellValue(2, 2, 0, "Net_Financing_Requirement");
        doc.SetCellValue(2, 2, 1, "138.5");

        // Sheet 3: Audit log (editable)
        doc.AddSheet("Audit_Log");
        doc.SetCellValue(3, 0, 0, "Date");
        doc.SetCellValue(3, 0, 1, "Editor");
        doc.SetCellValue(3, 0, 2, "Change_Description");

        // Verify initial state (all unprotected)
        Assert.False(doc.GetWorksheetProtection(0));
        Assert.False(doc.GetWorksheetProtection(1));
        Assert.False(doc.GetWorksheetProtection(2));
        Assert.False(doc.GetWorksheetProtection(3));

        // Protect calculation and summary sheets
        doc.SetWorksheetProtection(1, true);
        doc.SetWorksheetProtection(2, true);

        Assert.False(doc.GetWorksheetProtection(0)); // Assumptions: editable
        Assert.True(doc.GetWorksheetProtection(1));  // Calculations: protected
        Assert.True(doc.GetWorksheetProtection(2));  // Summary: protected
        Assert.False(doc.GetWorksheetProtection(3)); // Audit_Log: editable

        // Consistency
        Assert.Equal(doc.GetWorksheetProtection(1), doc.GetWorksheetProtection(1));

        // SaveToFile
        var path1 = TempFile("dmo_gilt_issuance.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify protection states preserved
        var loaded = FodsDocument.LoadFile(path1);
        Assert.False(loaded.GetWorksheetProtection(0));
        Assert.True(loaded.GetWorksheetProtection(1));
        Assert.True(loaded.GetWorksheetProtection(2));
        Assert.False(loaded.GetWorksheetProtection(3));

        // Update model: unprotect calculations for Q2 revision
        loaded.SetWorksheetProtection(1, false);
        loaded.SetCellValue(1, 1, 2, "26.3"); // updated Q2 Short_Gilts
        loaded.SetWorksheetProtection(1, true); // re-protect after edit

        Assert.True(loaded.GetWorksheetProtection(1));

        // Log the edit
        loaded.SetCellValue(3, 1, 0, "2024-07-15");
        loaded.SetCellValue(3, 1, 1, "DMO_Analyst");
        loaded.SetCellValue(3, 1, 2, "Q2_Short_Gilts_updated_from_25.1_to_26.3");

        var path2 = TempFile("dmo_gilt_issuance_q2_revised.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.False(final.GetWorksheetProtection(0));
        Assert.True(final.GetWorksheetProtection(1));
        Assert.True(final.GetWorksheetProtection(2));
        Assert.False(final.GetWorksheetProtection(3));

        var ex1 = Record.Exception(() => final.GetWorksheetProtection(0));
        var ex2 = Record.Exception(() => final.SetWorksheetProtection(3, true));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
