// Tests for FodsDocument.GetSheetName, SetSheetName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R421

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R421: Tests for FodsDocument.GetSheetName, SetSheetName deeper.
/// GetSheetName(sheetIndex): returns the name of the sheet at the given zero-based index.
/// SetSheetName(sheetIndex, name): renames the sheet at the given index to the new name.
/// Covers: GetSheetName no-throw; GetSheetName non-null-or-empty; GetSheetName consistent;
/// GetSheetName save-load; GetSheetName returns default for new sheet;
/// SetSheetName no-throw; SetSheetName updates GetSheetName; SetSheetName overwritable;
/// SetSheetName save-load; dogfood pipeline.
/// </summary>
public class FodsR421GetSheetNameAndSetSheetNameDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR421GetSheetNameAndSetSheetNameDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR421_" + Guid.NewGuid().ToString("N"));
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
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, 0, "Region");
        doc.SetCellValue(0, 0, 1, "Revenue");
        doc.SetCellValue(0, 1, 0, "North");
        doc.SetCellValue(0, 1, 1, "125000");
        return doc;
    }

    private static FodsDocument CreateMultiSheetDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Summary");
        doc.AddSheet("Detail");
        doc.AddSheet("Config");
        doc.SetCellValue(0, 0, 0, "Total");
        doc.SetCellValue(1, 0, 0, "Line Items");
        doc.SetCellValue(2, 0, 0, "Settings");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetSheetName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetName_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.GetSheetName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSheetName_NonNullOrEmpty()
    {
        var doc = CreateSampleDoc();
        Assert.False(string.IsNullOrEmpty(doc.GetSheetName(0)));
    }

    [Fact]
    public void GetSheetName_Consistent()
    {
        var doc = CreateSampleDoc();
        Assert.Equal(doc.GetSheetName(0), doc.GetSheetName(0));
    }

    [Fact]
    public void GetSheetName_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        var before = doc.GetSheetName(0);
        var path = TempFile("sn_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSheetName(0));
    }

    [Fact]
    public void GetSheetName_ReturnsSetName_ForMultipleSheets()
    {
        var doc = CreateMultiSheetDoc();
        Assert.Equal("Summary", doc.GetSheetName(0));
        Assert.Equal("Detail", doc.GetSheetName(1));
        Assert.Equal("Config", doc.GetSheetName(2));
    }

    // -------------------------------------------------------------------------
    // SetSheetName
    // -------------------------------------------------------------------------

    [Fact]
    public void SetSheetName_NoThrow()
    {
        var doc = CreateSampleDoc();
        var ex = Record.Exception(() => doc.SetSheetName(0, "Renamed"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetSheetName_UpdatesGetSheetName()
    {
        var doc = CreateSampleDoc();
        doc.SetSheetName(0, "RevenueByRegion");
        Assert.Equal("RevenueByRegion", doc.GetSheetName(0));
    }

    [Fact]
    public void SetSheetName_Overwritable()
    {
        var doc = CreateSampleDoc();
        doc.SetSheetName(0, "First");
        doc.SetSheetName(0, "Second");
        Assert.Equal("Second", doc.GetSheetName(0));
    }

    [Fact]
    public void SetSheetName_SaveLoad_Consistent()
    {
        var doc = CreateSampleDoc();
        doc.SetSheetName(0, "FinancialData");
        var path = TempFile("sn_set_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal("FinancialData", loaded.GetSheetName(0));
    }

    [Fact]
    public void SetSheetName_MultiSheet_Independent()
    {
        var doc = CreateMultiSheetDoc();
        doc.SetSheetName(1, "Transactions");
        Assert.Equal("Summary", doc.GetSheetName(0));
        Assert.Equal("Transactions", doc.GetSheetName(1));
        Assert.Equal("Config", doc.GetSheetName(2));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetSheetName_SetSheetName_Pipeline()
    {
        // Finance — HM Treasury / OBR: Public Sector Finances Databank 2024
        // Multi-sheet spreadsheet tracking fiscal aggregates, debt, and forecasts
        // Sheet naming conventions align with OBR Table identifiers (PSF Tables 1-5)

        var doc = FodsDocument.CreateEmpty();

        // Sheet 0: PSF Table 1 — Public sector current receipts
        doc.AddSheet("Table_1_Current_Receipts");
        doc.SetCellValue(0, 0, 0, "Category");
        doc.SetCellValue(0, 0, 1, "2022-23_Outturn");
        doc.SetCellValue(0, 0, 2, "2023-24_Outturn");
        doc.SetCellValue(0, 0, 3, "2024-25_Forecast");
        doc.SetCellValue(0, 1, 0, "Income_Tax");
        doc.SetCellValue(0, 1, 1, "246.1");
        doc.SetCellValue(0, 1, 2, "256.7");
        doc.SetCellValue(0, 1, 3, "266.2");
        doc.SetCellValue(0, 2, 0, "NICs");
        doc.SetCellValue(0, 2, 1, "177.4");
        doc.SetCellValue(0, 2, 2, "181.3");
        doc.SetCellValue(0, 2, 3, "189.5");
        doc.SetCellValue(0, 3, 0, "Corporation_Tax");
        doc.SetCellValue(0, 3, 1, "67.1");
        doc.SetCellValue(0, 3, 2, "85.2");
        doc.SetCellValue(0, 3, 3, "89.1");

        Assert.Equal("Table_1_Current_Receipts", doc.GetSheetName(0));

        // Sheet 1: PSF Table 2 — Public sector expenditure
        doc.AddSheet("Table_2_Expenditure");
        doc.SetCellValue(1, 0, 0, "Department");
        doc.SetCellValue(1, 0, 1, "DEL_GBPbn");
        doc.SetCellValue(1, 0, 2, "AME_GBPbn");
        doc.SetCellValue(1, 1, 0, "DHSC");
        doc.SetCellValue(1, 1, 1, "168.4");
        doc.SetCellValue(1, 1, 2, "212.6");
        doc.SetCellValue(1, 2, 0, "DWP");
        doc.SetCellValue(1, 2, 1, "12.8");
        doc.SetCellValue(1, 2, 2, "245.3");

        Assert.Equal("Table_2_Expenditure", doc.GetSheetName(1));

        // Sheet 2: PSF Table 3 — Public sector net borrowing
        doc.AddSheet("Table_3_Net_Borrowing");
        doc.SetCellValue(2, 0, 0, "Fiscal_Year");
        doc.SetCellValue(2, 0, 1, "PSNB_GBPbn");
        doc.SetCellValue(2, 0, 2, "PSNB_pct_GDP");
        for (int yr = 2020; yr <= 2024; yr++)
        {
            double psnb = 60 + (yr - 2022) * 15;
            doc.SetCellValue(2, yr - 2019, 0, $"{yr}-{(yr + 1) % 100:D2}");
            doc.SetCellValue(2, yr - 2019, 1, $"{psnb:F1}");
            doc.SetCellValue(2, yr - 2019, 2, $"{psnb / 2600.0 * 100:F1}");
        }

        Assert.Equal("Table_3_Net_Borrowing", doc.GetSheetName(2));
        Assert.Equal(doc.GetSheetName(2), doc.GetSheetName(2)); // consistent

        // Rename sheets using official OBR shorthand
        doc.SetSheetName(0, "PSF_T1_Receipts");
        doc.SetSheetName(1, "PSF_T2_Expenditure");
        doc.SetSheetName(2, "PSF_T3_Borrowing");

        Assert.Equal("PSF_T1_Receipts", doc.GetSheetName(0));
        Assert.Equal("PSF_T2_Expenditure", doc.GetSheetName(1));
        Assert.Equal("PSF_T3_Borrowing", doc.GetSheetName(2));

        // SaveToFile
        var path1 = TempFile("obr_psf_databank.fods");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path1);
        Assert.Equal("PSF_T1_Receipts", loaded.GetSheetName(0));
        Assert.Equal("PSF_T2_Expenditure", loaded.GetSheetName(1));
        Assert.Equal("PSF_T3_Borrowing", loaded.GetSheetName(2));
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Rename again after reload (overwrite)
        loaded.SetSheetName(0, "Receipts_Final");
        Assert.Equal("Receipts_Final", loaded.GetSheetName(0));
        Assert.Equal("PSF_T2_Expenditure", loaded.GetSheetName(1)); // others unchanged

        var path2 = TempFile("obr_psf_databank_final.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodsDocument.LoadFile(path2);
        Assert.Equal("Receipts_Final", final.GetSheetName(0));
        Assert.Equal("PSF_T2_Expenditure", final.GetSheetName(1));
        Assert.Equal("PSF_T3_Borrowing", final.GetSheetName(2));

        var ex1 = Record.Exception(() => final.GetSheetName(0));
        var ex2 = Record.Exception(() => final.SetSheetName(2, "PSF_T3_Revised"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
