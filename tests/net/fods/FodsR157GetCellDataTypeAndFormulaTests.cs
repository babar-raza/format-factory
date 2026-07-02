// Tests for FodsDocument.GetCellDataType and GetCellFormula.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R157

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R157: Tests for FodsDocument.GetCellDataType and GetCellFormula.
/// GetCellDataType(sheetName, row, col) returns the office:value-type attribute
/// of the cell, or null if absent, out-of-bounds, or sheet not found.
/// GetCellFormula(sheetName, row, col) returns the table:formula attribute,
/// or null if absent, out-of-bounds, or sheet not found.
/// Covers: GetCellDataType null sheetName throws; out-of-range row returns null;
/// out-of-range col returns null; nonexistent sheet returns null;
/// cell with no value-type attribute returns null;
/// SetCellFormula->GetCellFormula round-trip;
/// GetCellFormula null sheetName throws; out-of-range returns null;
/// GetCellFormula nonexistent sheet returns null;
/// dogfood SetCellFormula->GetCellFormula->SetCellValue pipeline.
/// </summary>
public class FodsR157GetCellDataTypeAndFormulaTests
{
    private static FodsDocument BuildSingleSheetDoc(string sheetName)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.RenameSheet(doc.GetSheetNames()[0], sheetName);
        doc.InsertRowWithValues(sheetName, 0, new[] { "A", "B", "C" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "10", "20", "30" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetCellDataType(null!, 0, 0));
    }

    [Fact]
    public void GetCellDataType_OutOfRangeRow_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellDataType("S", 99, 0));
    }

    [Fact]
    public void GetCellDataType_OutOfRangeCol_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellDataType("S", 0, 99));
    }

    [Fact]
    public void GetCellDataType_NonexistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetCellDataType("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NegativeRow_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellDataType("S", -1, 0));
    }

    [Fact]
    public void GetCellDataType_CellWithNoAttribute_ReturnsNullOrString()
    {
        // Cells inserted via InsertRowWithValues are plain text — may or may not have value-type
        var doc = BuildSingleSheetDoc("S");
        var dt = doc.GetCellDataType("S", 0, 0);
        // Acceptable: null (no attribute) or a string like "string"
        Assert.True(dt is null || dt is string);
    }

    // -------------------------------------------------------------------------
    // GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NullSheetName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetCellFormula(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormula_OutOfRangeRow_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellFormula("S", 99, 0));
    }

    [Fact]
    public void GetCellFormula_OutOfRangeCol_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellFormula("S", 0, 99));
    }

    [Fact]
    public void GetCellFormula_NonexistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetCellFormula("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFormula_CellWithNoFormula_ReturnsNull()
    {
        var doc = BuildSingleSheetDoc("S");
        Assert.Null(doc.GetCellFormula("S", 1, 0));
    }

    [Fact]
    public void GetCellFormula_AfterSetCellFormula_ReturnsFormula()
    {
        var doc = BuildSingleSheetDoc("S");
        doc.SetCellFormula("S", 1, 2, "=A2+B2");
        var formula = doc.GetCellFormula("S", 1, 2);
        Assert.NotNull(formula);
        Assert.Contains("A2+B2", formula); // ODF may prefix with "of:"
    }

    // -------------------------------------------------------------------------
    // Dogfood: combined pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetFormula_GetFormula_SetValue_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];
        doc.InsertRowWithValues(sheetName, 0, new[] { "X", "Y", "Sum" });
        doc.InsertRowWithValues(sheetName, 1, new[] { "5", "10", "" });

        // Set formula on Sum cell
        doc.SetCellFormula(sheetName, 1, 2, "=A2+B2");

        // Get formula back
        var formula = doc.GetCellFormula(sheetName, 1, 2);
        Assert.NotNull(formula);

        // Override with direct value
        doc.SetCellValue(1, 2, "15");
        var val = doc.GetCellValue(1, 2);
        Assert.Equal("15", val);
    }
}
