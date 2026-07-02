// Tests for FodsDocument.GetRowValues, InsertRowWithValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R206

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R206: Tests for FodsDocument.GetRowValues, InsertRowWithValues deeper coverage.
/// GetRowValues(sheet, row): returns list of cell values in the given row.
/// InsertRowWithValues(sheet, row, values): inserts a new row at the given index with values.
/// Covers: GetRowValues non-null; GetRowValues correct count; GetRowValues correct values;
/// GetRowValues after SetCellValue reflects mutation; GetRowValues different rows;
/// InsertRowWithValues increases RowCount; InsertRowWithValues row values accessible;
/// InsertRowWithValues shifts existing rows; InsertRowWithValues at index 0 is first row;
/// InsertRowWithValues at last index appends; InsertRowWithValues then GetRowValues correct;
/// dogfood CreateEmpty->SetCellValues->GetRowValues->InsertRowWithValues->GetRowValues verify.
/// </summary>
public class FodsR206GetRowValuesAndInsertRowDeepTests
{
    private static FodsDocument CreateThreeRowDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Alice");
        doc.SetCellValue("Sheet1", 0, 1, "Eng");
        doc.SetCellValue("Sheet1", 0, 2, "95");
        doc.SetCellValue("Sheet1", 1, 0, "Bob");
        doc.SetCellValue("Sheet1", 1, 1, "Finance");
        doc.SetCellValue("Sheet1", 1, 2, "82");
        doc.SetCellValue("Sheet1", 2, 0, "Carol");
        doc.SetCellValue("Sheet1", 2, 1, "Eng");
        doc.SetCellValue("Sheet1", 2, 2, "88");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetRowValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NonNull()
    {
        var doc = CreateThreeRowDoc();
        Assert.NotNull(doc.GetRowValues("Sheet1", 0));
    }

    [Fact]
    public void GetRowValues_FirstRow_CountCorrect()
    {
        var doc = CreateThreeRowDoc();
        var row = doc.GetRowValues("Sheet1", 0);
        Assert.Equal(3, row.Count);
    }

    [Fact]
    public void GetRowValues_FirstRow_ValuesCorrect()
    {
        var doc = CreateThreeRowDoc();
        var row = doc.GetRowValues("Sheet1", 0);
        Assert.Equal("Alice", row[0]);
        Assert.Equal("Eng", row[1]);
        Assert.Equal("95", row[2]);
    }

    [Fact]
    public void GetRowValues_SecondRow_ValuesCorrect()
    {
        var doc = CreateThreeRowDoc();
        var row = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("Bob", row[0]);
        Assert.Equal("Finance", row[1]);
        Assert.Equal("82", row[2]);
    }

    [Fact]
    public void GetRowValues_ThirdRow_ValuesCorrect()
    {
        var doc = CreateThreeRowDoc();
        var row = doc.GetRowValues("Sheet1", 2);
        Assert.Equal("Carol", row[0]);
    }

    [Fact]
    public void GetRowValues_AfterSetCellValue_ReflectsMutation()
    {
        var doc = CreateThreeRowDoc();
        doc.SetCellValue("Sheet1", 0, 0, "Alicia");
        var row = doc.GetRowValues("Sheet1", 0);
        Assert.Equal("Alicia", row[0]);
    }

    // -------------------------------------------------------------------------
    // InsertRowWithValues
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertRowWithValues_IncreasesRowCount()
    {
        var doc = CreateThreeRowDoc();
        var before = doc.GetRowCount("Sheet1");
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Dave", "HR", "77" });
        Assert.Equal(before + 1, doc.GetRowCount("Sheet1"));
    }

    [Fact]
    public void InsertRowWithValues_RowValues_Accessible()
    {
        var doc = CreateThreeRowDoc();
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Dave", "HR", "77" });
        var row = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("Dave", row[0]);
        Assert.Equal("HR", row[1]);
        Assert.Equal("77", row[2]);
    }

    [Fact]
    public void InsertRowWithValues_ShiftsExistingRows()
    {
        var doc = CreateThreeRowDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Header", "Col2", "Col3" });
        var oldFirstRow = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("Alice", oldFirstRow[0]);
    }

    [Fact]
    public void InsertRowWithValues_AtIndex0_BecomesFirst()
    {
        var doc = CreateThreeRowDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "New First", "X", "0" });
        var firstRow = doc.GetRowValues("Sheet1", 0);
        Assert.Equal("New First", firstRow[0]);
    }

    [Fact]
    public void InsertRowWithValues_Multiple_CountCorrect()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Row A", "Val 1" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Row B", "Val 2" });
        doc.InsertRowWithValues("Sheet1", 2, new[] { "Row C", "Val 3" });
        Assert.Equal(3, doc.GetRowCount("Sheet1"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellValuesGetRowValuesInsertRowGetRowValuesVerify_Pipeline()
    {
        // Create and populate
        var doc = CreateThreeRowDoc();
        Assert.Equal(3, doc.GetRowCount("Sheet1"));

        // GetRowValues for all rows
        var row0 = doc.GetRowValues("Sheet1", 0);
        Assert.Equal("Alice", row0[0]);

        var row1 = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("Bob", row1[0]);

        // InsertRowWithValues at position 1 (between Alice and Bob)
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Anna", "Eng", "91" });
        Assert.Equal(4, doc.GetRowCount("Sheet1"));

        // New row at index 1
        var newRow = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("Anna", newRow[0]);
        Assert.Equal("91", newRow[2]);

        // Bob shifted to index 2
        var shiftedBob = doc.GetRowValues("Sheet1", 2);
        Assert.Equal("Bob", shiftedBob[0]);

        // SetCellValue on newly inserted row
        doc.SetCellValue("Sheet1", 1, 2, "92");
        var updated = doc.GetRowValues("Sheet1", 1);
        Assert.Equal("92", updated[2]);

        // InsertRowWithValues at end
        doc.InsertRowWithValues("Sheet1", 4, new[] { "Eve", "HR", "70" });
        Assert.Equal(5, doc.GetRowCount("Sheet1"));
        var lastRow = doc.GetRowValues("Sheet1", 4);
        Assert.Equal("Eve", lastRow[0]);
    }
}
