// Tests for FodsDocument.RenameSheet() and CopySheet() operations.
// Sprint: FORMAT-FACTORY-FODS-RENAME-COPY-SHEET-20260626
// Ledger: R130-GOVERNED-DOTNET-FODS-RENAME-COPY-SHEET-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R130: FodsDocument.RenameSheet(oldName, newName) updates the sheet's Name and
/// GetSheetNames() result. FodsDocument.CopySheet(sourceName, newName) produces a
/// second sheet with the same data. Both operations leave SheetCount consistent.
/// </summary>
public class FodsR130RenameAndCopySheetTests
{
    // ---- RenameSheet: basic ----

    [Fact]
    public void RenameSheet_OldNameNoLongerExists()
    {
        var doc = FodsDocument.CreateNew();
        doc.RenameSheet("Sheet1", "Report");

        Assert.DoesNotContain("Sheet1", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_NewNameAppearsInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.RenameSheet("Sheet1", "Summary");

        Assert.Contains("Summary", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        var before = doc.SheetCount;
        doc.RenameSheet("Sheet1", "Renamed");

        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void RenameSheet_DataPreservedAfterRename()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Alpha", "Beta" });

        doc.RenameSheet("Sheet1", "DataSheet");

        var val = doc.GetSheetByName("DataSheet")!;
        Assert.Equal("Alpha", FodsDocument.GetCellValue(val, 0, 0));
    }

    // ---- RenameSheet: GetSheetByName works with new name ----

    [Fact]
    public void RenameSheet_GetSheetByNewName_ReturnsSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.RenameSheet("Sheet1", "MySheet");

        var sheet = doc.GetSheetByName("MySheet");
        Assert.NotNull(sheet);
    }

    [Fact]
    public void RenameSheet_GetSheetByOldName_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.RenameSheet("Sheet1", "MySheet");

        var sheet = doc.GetSheetByName("Sheet1");
        Assert.Null(sheet);
    }

    // ---- CopySheet: basic ----

    [Fact]
    public void CopySheet_NewSheetExistsInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "X", "Y" });

        doc.CopySheet("Sheet1", "Sheet1Copy");

        Assert.Contains("Sheet1Copy", doc.GetSheetNames());
    }

    [Fact]
    public void CopySheet_OriginalSheetStillExists()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B" });

        doc.CopySheet("Sheet1", "CopyOfSheet1");

        Assert.Contains("Sheet1", doc.GetSheetNames());
    }

    [Fact]
    public void CopySheet_SheetCountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        var before = doc.SheetCount;

        doc.CopySheet("Sheet1", "Sheet1_Dup");

        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_CopiedSheetHasSameData()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Orig1", "Orig2", "Orig3" });

        doc.CopySheet("Sheet1", "Clone");

        var clone = doc.GetSheetByName("Clone")!;
        Assert.Equal("Orig1", FodsDocument.GetCellValue(clone, 0, 0));
        Assert.Equal("Orig2", FodsDocument.GetCellValue(clone, 0, 1));
        Assert.Equal("Orig3", FodsDocument.GetCellValue(clone, 0, 2));
    }

    // ---- Dogfood: rename + copy pipeline ----

    [Fact]
    public void DogfoodPipeline_RenameThenCopy_BothSheetsAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "v1", "v2" });

        // Rename source
        doc.RenameSheet("Sheet1", "Primary");
        // Copy renamed sheet
        doc.CopySheet("Primary", "Backup");

        var sheetNames = doc.GetSheetNames();
        Assert.Contains("Primary", sheetNames);
        Assert.Contains("Backup", sheetNames);
        Assert.Equal(2, doc.SheetCount);

        // Both sheets have the data
        var primary = doc.GetSheetByName("Primary")!;
        var backup  = doc.GetSheetByName("Backup")!;
        Assert.Equal("v1", FodsDocument.GetCellValue(primary, 0, 0));
        Assert.Equal("v1", FodsDocument.GetCellValue(backup, 0, 0));
    }
}
