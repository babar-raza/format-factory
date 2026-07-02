// Tests for FodsDocument.AddSheet, RenameSheet, GetSheetNames, RemoveSheet.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R200

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R200: Tests for FodsDocument.AddSheet, RenameSheet, GetSheetNames, RemoveSheet.
/// AddSheet(name): adds a new sheet to the document.
/// RenameSheet(oldName, newName): renames an existing sheet.
/// GetSheetNames(): returns list of sheet names.
/// RemoveSheet(name): removes a sheet from the document.
/// Covers: GetSheetNames non-null; GetSheetNames non-empty for new doc;
/// AddSheet increases sheet count; AddSheet name appears in GetSheetNames;
/// RenameSheet new name in GetSheetNames; RenameSheet old name absent;
/// RemoveSheet decreases sheet count; RemoveSheet name absent after removal;
/// AddSheet->SetCellValue->GetCellValue on new sheet;
/// AddSheet multiple sheets all accessible; GetSheetNames count correct;
/// RenameSheet->SetCellValue->GetCellValue on renamed sheet;
/// AddSheet->RenameSheet->RemoveSheet pipeline;
/// dogfood CreateNew->GetSheetNames->AddSheet->RenameSheet->SetCells->RemoveSheet verify.
/// </summary>
public class FodsR200AddSheetAndRenameTests
{
    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.NotNull(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_NonEmpty_ForNewDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.NotEmpty(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_CountIsOne_ForNewDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Equal(1, doc.GetSheetNames().Count);
    }

    // -------------------------------------------------------------------------
    // AddSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_IncreasesSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var before = doc.GetSheetNames().Count;
        doc.AddSheet("NewSheet");
        Assert.Equal(before + 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void AddSheet_NameAppearsInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("DataSheet");
        Assert.Contains("DataSheet", doc.GetSheetNames());
    }

    [Fact]
    public void AddSheet_SetCellValue_GetCellValue_Works()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("NewSheet");
        doc.SetCellValue("NewSheet", 0, 0, "HelloNewSheet");
        var val = doc.GetCellValue("NewSheet", 0, 0);
        Assert.Equal("HelloNewSheet", val);
    }

    [Fact]
    public void AddSheet_Multiple_AllAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");
        var names = doc.GetSheetNames();
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    // -------------------------------------------------------------------------
    // RenameSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_NewNameInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var original = doc.GetSheetNames()[0];
        doc.RenameSheet(original, "Renamed");
        Assert.Contains("Renamed", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_OldNameAbsent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var original = doc.GetSheetNames()[0];
        doc.RenameSheet(original, "NewName");
        Assert.DoesNotContain(original, doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_SetCellValue_GetCellValue_OnRenamedSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var original = doc.GetSheetNames()[0];
        doc.SetCellValue(original, 0, 0, "BeforeRename");
        doc.RenameSheet(original, "AfterRename");
        var val = doc.GetCellValue("AfterRename", 0, 0);
        Assert.Equal("BeforeRename", val);
    }

    [Fact]
    public void RenameSheet_SheetCount_Unchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var before = doc.GetSheetNames().Count;
        var original = doc.GetSheetNames()[0];
        doc.RenameSheet(original, "Renamed");
        Assert.Equal(before, doc.GetSheetNames().Count);
    }

    // -------------------------------------------------------------------------
    // RemoveSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_DecreasesSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Extra");
        var before = doc.GetSheetNames().Count;
        doc.RemoveSheet("Extra");
        Assert.Equal(before - 1, doc.GetSheetNames().Count);
    }

    [Fact]
    public void RemoveSheet_NameAbsentAfterRemoval()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("ToRemove");
        doc.RemoveSheet("ToRemove");
        Assert.DoesNotContain("ToRemove", doc.GetSheetNames());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateGetNamesAddRenameSetCellsRemoveVerify_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");

        // GetSheetNames — initial state
        var names = doc.GetSheetNames();
        Assert.Equal(1, names.Count);
        var defaultSheet = names[0];

        // SetCellValue on default sheet
        doc.SetCellValue(defaultSheet, 0, 0, "MainData");

        // AddSheet
        doc.AddSheet("Summary");
        Assert.Equal(2, doc.GetSheetNames().Count);
        Assert.Contains("Summary", doc.GetSheetNames());

        // SetCellValue on new sheet
        doc.SetCellValue("Summary", 0, 0, "SummaryData");
        Assert.Equal("SummaryData", doc.GetCellValue("Summary", 0, 0));

        // RenameSheet
        doc.RenameSheet("Summary", "Overview");
        Assert.Contains("Overview", doc.GetSheetNames());
        Assert.DoesNotContain("Summary", doc.GetSheetNames());

        // Data preserved after rename
        Assert.Equal("SummaryData", doc.GetCellValue("Overview", 0, 0));

        // AddSheet and RemoveSheet
        doc.AddSheet("Temp");
        Assert.Equal(3, doc.GetSheetNames().Count);
        doc.RemoveSheet("Temp");
        Assert.Equal(2, doc.GetSheetNames().Count);
        Assert.DoesNotContain("Temp", doc.GetSheetNames());

        // Default sheet data still intact
        Assert.Equal("MainData", doc.GetCellValue(defaultSheet, 0, 0));
    }
}
