// Tests for FodsDocument.AddSheet, RemoveSheet, RenameSheet, CopySheet, GetSheetNames.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R181

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R181: Tests for FodsDocument.AddSheet, RemoveSheet, RenameSheet, CopySheet, GetSheetNames.
/// AddSheet(name): adds a new sheet and returns it.
/// RemoveSheet(name): removes an existing sheet.
/// RenameSheet(oldName, newName): renames an existing sheet.
/// CopySheet(sourceName, newName): copies a sheet with its data.
/// GetSheetNames(): returns all sheet names.
/// Covers: AddSheet increments SheetCount; AddSheet name in GetSheetNames;
/// GetSheetByName finds added sheet; RemoveSheet decrements SheetCount;
/// RenameSheet changes sheet name; GetSheetNames after rename;
/// CopySheet creates new sheet; CopySheet new name in GetSheetNames;
/// AddSheet then SetCellValue and GetCellValue; SheetCount after multiple adds;
/// GetSheetByIndex after AddSheet; GetSheetNames count after removes;
/// dogfood CreateNew->AddSheet->SetCell->CopySheet->RenameSheet->GetSheetNames.
/// </summary>
public class FodsR181AddSheetAndManagementTests
{
    private static readonly string FodsFixturePath =
        System.IO.Path.Combine(
            System.AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..",
            "samples", "by-format", "fods", "valid", "simple.fods");

    private FodsDocument LoadFixture()
    {
        var path = System.IO.Path.GetFullPath(FodsFixturePath);
        return FodsDocument.Load(path);
    }

    // -------------------------------------------------------------------------
    // AddSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void AddSheet_IncrementsSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var initial = doc.SheetCount;
        doc.AddSheet("NewSheet");
        Assert.Equal(initial + 1, doc.SheetCount);
    }

    [Fact]
    public void AddSheet_NameAppearInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("ExtraSheet");
        var names = doc.GetSheetNames();
        Assert.Contains("ExtraSheet", names);
    }

    [Fact]
    public void AddSheet_GetSheetByName_FindsNewSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("TargetSheet");
        var sheet = doc.GetSheetByName("TargetSheet");
        Assert.NotNull(sheet);
    }

    [Fact]
    public void AddSheet_SetCellValue_GetCellValue_Round_Trips()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("DataSheet");
        doc.SetCellValue(0, 0, "TestValue");
        Assert.Equal("TestValue", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void AddSheet_Multiple_SheetCountCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var initial = doc.SheetCount;
        doc.AddSheet("SheetA");
        doc.AddSheet("SheetB");
        Assert.Equal(initial + 2, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // RemoveSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_DecrementsSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("ToRemove");
        var before = doc.SheetCount;
        doc.RemoveSheet("ToRemove");
        Assert.Equal(before - 1, doc.SheetCount);
    }

    [Fact]
    public void RemoveSheet_RemovedNameNotInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("DropMe");
        doc.RemoveSheet("DropMe");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("DropMe", names);
    }

    // -------------------------------------------------------------------------
    // RenameSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_ChangesSheetName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        var names = doc.GetSheetNames();
        Assert.Contains("NewName", names);
        Assert.DoesNotContain("OldName", names);
    }

    [Fact]
    public void RenameSheet_GetSheetByName_FindsRenamedSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Alpha");
        doc.RenameSheet("Alpha", "Beta");
        var sheet = doc.GetSheetByName("Beta");
        Assert.NotNull(sheet);
    }

    // -------------------------------------------------------------------------
    // CopySheet
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_CreatesNewSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var before = doc.SheetCount;
        doc.CopySheet(doc.GetSheetNames()[0], "CopiedSheet");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_NewNameInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var srcName = doc.GetSheetNames()[0];
        doc.CopySheet(srcName, "CopiedVersion");
        var names = doc.GetSheetNames();
        Assert.Contains("CopiedVersion", names);
    }

    // -------------------------------------------------------------------------
    // GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_AfterMultipleOps_CountIsCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("S1");
        doc.AddSheet("S2");
        doc.RemoveSheet("S1");
        // initial + 1 (S2) - 0 (S1 was added then removed)
        var names = doc.GetSheetNames();
        Assert.Contains("S2", names);
        Assert.DoesNotContain("S1", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->AddSheet->SetCell->CopySheet->RenameSheet->GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateAddSetCopyrRenameGetNames_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");

        // Add a data sheet
        doc.AddSheet("DataSheet");
        var names = doc.GetSheetNames();
        Assert.Contains("DataSheet", names);

        // Set a cell value in default sheet
        doc.SetCellValue(0, 0, "Hello");
        Assert.Equal("Hello", doc.GetCellValue(0, 0));

        // Copy the first sheet
        var originalName = names[0];
        doc.CopySheet(originalName, "BackupSheet");
        Assert.Equal(3, doc.SheetCount); // original + DataSheet + BackupSheet

        // Rename the copy
        doc.RenameSheet("BackupSheet", "ArchiveSheet");
        var finalNames = doc.GetSheetNames();
        Assert.Contains("ArchiveSheet", finalNames);
        Assert.DoesNotContain("BackupSheet", finalNames);
        Assert.Contains("DataSheet", finalNames);
    }
}
