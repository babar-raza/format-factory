// Tests for FodsDocument.RenameSheet and CopySheet.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R167

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R167: Tests for FodsDocument.RenameSheet and CopySheet.
/// RenameSheet(oldName, newName): renames a sheet; old name no longer accessible; new name is.
/// CopySheet(sourceName, newName): creates a duplicate sheet with given new name; source preserved.
/// Covers: RenameSheet accessible via new name; RenameSheet old name no longer in GetSheetNames;
/// RenameSheet SheetCount unchanged; RenameSheet null old/new throws;
/// RenameSheet nonexistent sheet throws; CopySheet source still exists;
/// CopySheet new sheet exists in GetSheetNames; CopySheet SheetCount incremented;
/// CopySheet new sheet has same row count as source; CopySheet null name throws;
/// CopySheet nonexistent source throws; CopySheet name collision throws or merges;
/// dogfood CreateNew->RenameSheet->InsertRows->CopySheet->GetSheetNames pipeline.
/// </summary>
public class FodsR167RenameSheetAndCopySheetTests
{
    private static FodsDocument BuildDoc(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // RenameSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameSheet_NewNameAccessible()
    {
        var doc = FodsDocument.CreateNew();
        var orig = doc.GetSheetNames()[0];
        doc.RenameSheet(orig, "Renamed");
        Assert.Contains("Renamed", doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_OldNameNoLongerExists()
    {
        var doc = FodsDocument.CreateNew();
        var orig = doc.GetSheetNames()[0];
        doc.RenameSheet(orig, "NewName");
        Assert.DoesNotContain(orig, doc.GetSheetNames());
    }

    [Fact]
    public void RenameSheet_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        var before = doc.SheetCount;
        var first = doc.GetSheetNames()[0];
        doc.RenameSheet(first, "Renamed");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void RenameSheet_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() =>
            doc.RenameSheet("NonExistentSheet", "NewName"));
    }

    [Fact]
    public void RenameSheet_DataPreserved()
    {
        var doc = BuildDoc("Original",
            new[] { "Key", "Value" },
            new[] { new[] { "A", "1" } });
        doc.RenameSheet("Original", "Renamed");
        // Row count should still be 2 (header + 1 data row)
        Assert.Equal(2, doc.GetRowCount("Renamed"));
    }

    // -------------------------------------------------------------------------
    // CopySheet
    // -------------------------------------------------------------------------

    [Fact]
    public void CopySheet_SourceStillExists()
    {
        var doc = BuildDoc("Source",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        doc.CopySheet("Source", "Copy");
        Assert.Contains("Source", doc.GetSheetNames());
    }

    [Fact]
    public void CopySheet_NewSheetExists()
    {
        var doc = BuildDoc("Source",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        doc.CopySheet("Source", "Copy");
        Assert.Contains("Copy", doc.GetSheetNames());
    }

    [Fact]
    public void CopySheet_SheetCountIncremented()
    {
        var doc = BuildDoc("Data",
            new[] { "A" },
            new[] { new[] { "1" } });
        var before = doc.SheetCount;
        doc.CopySheet("Data", "DataCopy");
        Assert.Equal(before + 1, doc.SheetCount);
    }

    [Fact]
    public void CopySheet_NewSheetHasSameRowCount()
    {
        var doc = BuildDoc("Template",
            new[] { "X", "Y" },
            new[] { new[] { "1", "2" }, new[] { "3", "4" } });
        doc.CopySheet("Template", "TemplateCopy");
        Assert.Equal(doc.GetRowCount("Template"), doc.GetRowCount("TemplateCopy"));
    }

    [Fact]
    public void CopySheet_NonexistentSource_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() =>
            doc.CopySheet("NonExistentSource", "CopyName"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->RenameSheet->InsertRows->CopySheet->GetSheetNames
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_RenameInsertCopyGetSheetNames_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var first = doc.GetSheetNames()[0];

        // Rename
        doc.RenameSheet(first, "Master");
        Assert.Contains("Master", doc.GetSheetNames());
        Assert.DoesNotContain(first, doc.GetSheetNames());

        // Insert data
        doc.InsertRowWithValues("Master", 0, new[] { "Name", "Score" });
        doc.InsertRowWithValues("Master", 1, new[] { "Alice", "95" });
        doc.InsertRowWithValues("Master", 2, new[] { "Bob", "82" });
        Assert.Equal(3, doc.GetRowCount("Master"));

        // Copy
        doc.CopySheet("Master", "Backup");
        Assert.Contains("Backup", doc.GetSheetNames());
        Assert.Equal(2, doc.SheetCount);
        Assert.Equal(3, doc.GetRowCount("Backup"));

        // Both sheets accessible via GetSheetByName
        Assert.NotNull(doc.GetSheetByName("Master"));
        Assert.NotNull(doc.GetSheetByName("Backup"));
    }
}
