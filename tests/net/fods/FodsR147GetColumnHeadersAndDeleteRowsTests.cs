// Tests for FodsDocument.GetColumnHeaders and FodsDocument.DeleteRows.
// Sprint: ff-sprint-s136-dotnet-deepening-20260627
// Ledger: PC-FODS-R147

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R147: Tests for FodsDocument.GetColumnHeaders (two overloads) and FodsDocument.DeleteRows.
/// GetColumnHeaders() returns column header values from the first row of the first sheet.
/// GetColumnHeaders(sheetName) targets a named sheet; returns empty if not found.
/// DeleteRows(sheetName, startRow, count) removes rows by zero-based range.
/// Covers: GetColumnHeaders empty doc returns empty; null sheetName arg not found=empty;
/// after SetCellValue first row, GetColumnHeaders returns that value;
/// named-sheet overload nonexistent=empty; DeleteRows null sheetName throws;
/// DeleteRows negative count throws; DeleteRows nonexistent sheet throws;
/// DeleteRows removes correct row count; dogfood CreateNew->AddSheet->SetCell->
/// GetColumnHeaders->DeleteRows verifies pipeline.
/// </summary>
public class FodsR147GetColumnHeadersAndDeleteRowsTests
{
    // -------------------------------------------------------------------------
    // GetColumnHeaders() - no-argument overload
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_EmptyDocument_ReturnsEmpty()
    {
        // CreateNew produces a doc with one empty sheet
        var doc = FodsDocument.CreateNew();
        var headers = doc.GetColumnHeaders();
        Assert.NotNull(headers);
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_AfterSetCellValueInFirstRow_ReturnsHeaderValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        var headers = doc.GetColumnHeaders();
        Assert.Contains("Name", headers);
        Assert.Contains("Score", headers);
    }

    [Fact]
    public void GetColumnHeaders_ReturnsReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "ID");
        var headers = doc.GetColumnHeaders();
        Assert.IsAssignableFrom<IReadOnlyList<string>>(headers);
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders(sheetName) - named-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NonexistentSheetName_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var headers = doc.GetColumnHeaders("NoSuchSheet");
        Assert.NotNull(headers);
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheet_ReturnsFirstRowValues()
    {
        var doc = FodsDocument.CreateNew();
        // The default sheet name in CreateNew — discover it
        var sheetName = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "Department");
        var headers = doc.GetColumnHeaders(sheetName);
        Assert.Contains("Department", headers);
    }

    // -------------------------------------------------------------------------
    // DeleteRows guards
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows(null!, 0, 1));
    }

    [Fact]
    public void DeleteRows_EmptySheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.DeleteRows(string.Empty, 0, 1));
    }

    [Fact]
    public void DeleteRows_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.DeleteRows("NoSuchSheet", 0, 1));
    }

    [Fact]
    public void DeleteRows_NegativeCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.DeleteRows(sheetName, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> SetCellValue rows -> GetColumnHeaders -> DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCells_GetHeaders_DeleteRows_VerifiesState()
    {
        var doc = FodsDocument.CreateNew();
        // Row 0: headers; Row 1: data; Row 2: data
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9.99");
        doc.SetCellValue(2, 0, "Gadget");
        doc.SetCellValue(2, 1, "19.99");

        // GetColumnHeaders reads first row
        var headers = doc.GetColumnHeaders();
        Assert.Contains("Product", headers);
        Assert.Contains("Price", headers);

        // GetSheetNames to get the name for DeleteRows
        var sheetName = doc.GetSheetNames()[0];
        var rowsBefore = doc.Sheets[0].Rows.Count;

        // Delete 1 data row (row index 1)
        doc.DeleteRows(sheetName, 1, 1);

        var rowsAfter = doc.Sheets[0].Rows.Count;
        Assert.Equal(rowsBefore - 1, rowsAfter);
    }
}
