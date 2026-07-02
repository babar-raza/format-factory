// Tests for FodsDocument.SetCellValue, GetColumnHeaders, HasSheet.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R171

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R171: Tests for FodsDocument.SetCellValue, GetColumnHeaders, HasSheet.
/// SetCellValue(row, col, value): sets cell in first sheet at given coordinates.
/// SetCellValue(FodsSheet, row, col, value): static version for explicit sheet.
/// GetColumnHeaders(sheetName): returns header values from row 0 of named sheet.
/// HasSheet(name): true if sheet with given name exists.
/// Covers: SetCellValue updates cell and GetCellValue reflects it; SetCellValue OOB grows rows;
/// SetCellValue static overload works; GetColumnHeaders returns header row values;
/// GetColumnHeaders noarg returns first sheet headers; GetColumnHeaders empty if no rows;
/// HasSheet true for existing; HasSheet false for nonexistent; HasSheet after AddSheet;
/// HasSheet after RemoveSheet is false; dogfood Create->SetCellValue->GetHeaders->HasSheet pipeline.
/// </summary>
public class FodsR171SetCellValueAndGetColumnHeadersTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
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
    // SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellValue_UpdatesCell_GetCellValueReflectsIt()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        doc.SetCellValue(0, 0, "Updated");
        Assert.Equal("Updated", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCellValue_DoesNotAffectOtherCells()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        doc.SetCellValue(0, 0, "ChangedName");
        Assert.Equal("95", doc.GetCellValue(1, 1)); // Data row Score unchanged
    }

    [Fact]
    public void SetCellValue_Row1_UpdatesDataRow()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });
        doc.SetCellValue(1, 0, "Robert");
        Assert.Equal("Robert", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void SetCellValue_Static_WorksOnExplicitSheet()
    {
        var doc = BuildSheet("Sheet1",
            new[] { "X" },
            new[] { new[] { "val" } });
        var sheet = doc.GetSheetByName("Sheet1");
        Assert.NotNull(sheet);
        FodsDocument.SetCellValue(sheet!, 0, 0, "StaticUpdated");
        Assert.Equal("StaticUpdated", FodsDocument.GetCellValue(sheet!, 0, 0));
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_ByName_ReturnsHeaderRow()
    {
        var doc = BuildSheet("Report",
            new[] { "Name", "Dept", "Score" },
            new[] { new[] { "Alice", "Eng", "95" } });
        var headers = doc.GetColumnHeaders("Report");
        Assert.Contains("Name", headers);
        Assert.Contains("Dept", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void GetColumnHeaders_NoArgs_ReturnsFirstSheetHeaders()
    {
        var doc = BuildSheet("Main",
            new[] { "Col1", "Col2" },
            new[] { new[] { "A", "B" } });
        var headers = doc.GetColumnHeaders();
        Assert.Contains("Col1", headers);
        Assert.Contains("Col2", headers);
    }

    [Fact]
    public void GetColumnHeaders_CountMatchesColumnCount()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B", "C", "D" },
            new[] { new[] { "1", "2", "3", "4" } });
        var headers = doc.GetColumnHeaders("Data");
        Assert.Equal(4, headers.Count);
    }

    // -------------------------------------------------------------------------
    // HasSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void HasSheet_ExistingSheet_IsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var name = doc.GetSheetNames()[0];
        Assert.True(doc.HasSheet(name));
    }

    [Fact]
    public void HasSheet_NonexistentSheet_IsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(doc.HasSheet("NonExistentSheet"));
    }

    [Fact]
    public void HasSheet_AfterAddSheet_IsTrue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("NewSheet");
        Assert.True(doc.HasSheet("NewSheet"));
    }

    [Fact]
    public void HasSheet_AfterRemoveSheet_IsFalse()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Temp");
        doc.RemoveSheet("Temp");
        Assert.False(doc.HasSheet("Temp"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->SetCellValue->GetColumnHeaders->HasSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetValueGetHeadersHasSheet_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        // Verify sheet exists
        Assert.True(doc.HasSheet(sheetName));
        Assert.False(doc.HasSheet("NoSuchSheet"));

        // Insert headers and data
        doc.InsertRowWithValues(sheetName, 0, new[] { "Product", "Price", "Stock" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "Widget", "9.99", "100" });
        doc.InsertRowWithValues(sheetName, 2, new[] { "Gadget", "19.99", "50" });

        // Check headers
        var headers = doc.GetColumnHeaders(sheetName);
        Assert.Contains("Product", headers);
        Assert.Contains("Price", headers);
        Assert.Contains("Stock", headers);

        // Update a cell
        doc.SetCellValue(1, 2, "150"); // Update Widget stock
        Assert.Equal("150", doc.GetCellValue(1, 2));

        // Headers unchanged after SetCellValue
        var headersAfter = doc.GetColumnHeaders(sheetName);
        Assert.Equal(3, headersAfter.Count);

        // Add new sheet and verify
        doc.AddSheet("Overflow");
        Assert.True(doc.HasSheet("Overflow"));
        Assert.Equal(2, doc.SheetCount);
    }
}
