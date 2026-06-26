// Tests for FodsDocument.FilterRows dedicated coverage.
// Sprint: ff-sprint-s170-dotnet-deepening-20260628
// Ledger: PC-FODS-R177

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R177: Dedicated tests for FodsDocument.FilterRows(string sheetName, int col, string value).
/// Returns rows where column `col` exactly matches `value` (case-sensitive, ordinal).
/// Header row (row 0) is ALWAYS included in the result.
/// Returns empty list if the sheet does not exist.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws ArgumentNullException for null value.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws;
/// null value throws ArgumentNullException; nonexistent sheet returns empty;
/// header row always included; no match returns header-only;
/// single match returns header + 1 row; case-sensitive (no match for wrong case);
/// IReadOnlyList of IReadOnlyList; dogfood AddSheet->SetCells->FilterRows.
/// </summary>
public class FodsR177FilterRowsDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests — throws
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.FilterRows(null!, 0, "val"));
    }

    [Fact]
    public void FilterRows_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.FilterRows("   ", 0, "val"));
    }

    [Fact]
    public void FilterRows_NullValue_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentNullException>(() => doc.FilterRows("Data", 0, null!));
    }

    // -------------------------------------------------------------------------
    // Null return — nonexistent sheet
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NonexistentSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var result = doc.FilterRows("NoSuchSheet", 0, "val");
        Assert.Empty(result);
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRows_NoDataRows_ReturnsHeaderOnly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name"); // header only
        var result = doc.FilterRows("Sheet1", 0, "Alice");
        // Header row always included; no data rows match
        Assert.Single(result);
    }

    [Fact]
    public void FilterRows_MatchingRow_ReturnsHeaderPlusMatch()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(2, 0, "Bob");
        var result = doc.FilterRows("Sheet1", 0, "Alice");
        // Header + Alice row = 2 rows
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void FilterRows_ReturnsIReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        var result = doc.FilterRows("Sheet1", 0, "Alice");
        Assert.IsAssignableFrom<IReadOnlyList<IReadOnlyList<string?>>>(result);
    }

    [Fact]
    public void FilterRows_CaseSensitive_NoMatchForWrongCase()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(1, 0, "Alice");
        // Search for "alice" (lowercase) — should not match "Alice"
        var result = doc.FilterRows("Sheet1", 0, "alice");
        Assert.Single(result); // header only
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_SetCells_FilterRows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Employees");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Dept");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "Eng");
        doc.SetCellValue(2, 0, "Bob");
        doc.SetCellValue(2, 1, "HR");
        doc.SetCellValue(3, 0, "Carol");
        doc.SetCellValue(3, 1, "Eng");
        // Filter by Dept == "Eng": header + Alice + Carol = 3 rows
        var result = doc.FilterRows("Employees", 1, "Eng");
        Assert.Equal(3, result.Count);
    }
}
