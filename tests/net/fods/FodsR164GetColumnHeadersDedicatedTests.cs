// Tests for FodsDocument.GetColumnHeaders dedicated coverage.
// Sprint: ff-sprint-s157-dotnet-deepening-20260628
// Ledger: PC-FODS-R164

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R164: Dedicated tests for FodsDocument.GetColumnHeaders() and GetColumnHeaders(string sheetName).
/// GetColumnHeaders() returns headers from the first row of the first sheet.
/// GetColumnHeaders(sheetName) returns headers from the first row of the named sheet.
/// Returns empty list for empty doc, no sheets, empty row, or nonexistent sheet (named overload).
/// Covers: empty document returns empty; no sheets returns empty; empty first row returns empty;
/// single cell returns one header; multiple cells return multiple headers;
/// named sheet overload nonexistent returns empty; named sheet overload returns correct headers;
/// headers are in order; dogfood CreateNew->AddSheet->SetCellValue->GetColumnHeaders;
/// dogfood named overload matches first overload for first sheet.
/// </summary>
public class FodsR164GetColumnHeadersDedicatedTests
{
    // -------------------------------------------------------------------------
    // Zero / empty tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_EmptyDocument_NoSheets_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var headers = doc.GetColumnHeaders();
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_EmptyFirstRow_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var headers = doc.GetColumnHeaders();
        Assert.Empty(headers);
    }

    // -------------------------------------------------------------------------
    // Functional tests — no-arg overload
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_SingleCell_ReturnsOneHeader()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Name");
        var headers = doc.GetColumnHeaders();
        Assert.Single(headers);
        Assert.Equal("Name", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_MultipleCells_ReturnsMultipleHeaders()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "ID");
        doc.SetCellValue("Sheet1", 0, 1, "Name");
        doc.SetCellValue("Sheet1", 0, 2, "Score");
        var headers = doc.GetColumnHeaders();
        Assert.Equal(3, headers.Count);
    }

    [Fact]
    public void GetColumnHeaders_HeadersInOrder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Alpha");
        doc.SetCellValue("Sheet1", 0, 1, "Beta");
        doc.SetCellValue("Sheet1", 0, 2, "Gamma");
        var headers = doc.GetColumnHeaders();
        Assert.Equal("Alpha", headers[0]);
        Assert.Equal("Beta", headers[1]);
        Assert.Equal("Gamma", headers[2]);
    }

    // -------------------------------------------------------------------------
    // Functional tests — named sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NamedSheet_NonexistentSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var headers = doc.GetColumnHeaders("NoSuchSheet");
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheet_ReturnsCorrectHeaders()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Product");
        doc.SetCellValue("Data", 0, 1, "Price");
        var headers = doc.GetColumnHeaders("Data");
        Assert.Equal(2, headers.Count);
        Assert.Equal("Product", headers[0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_GetColumnHeaders()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Month");
        doc.SetCellValue("Report", 0, 1, "Revenue");
        doc.SetCellValue("Report", 0, 2, "Expenses");
        var headers = doc.GetColumnHeaders();
        Assert.Equal(3, headers.Count);
        Assert.Contains("Month", headers);
    }

    [Fact]
    public void DogfoodPipeline_NamedOverload_MatchesFirstOverload()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Primary");
        doc.SetCellValue("Primary", 0, 0, "Col1");
        doc.SetCellValue("Primary", 0, 1, "Col2");
        var byDefault = doc.GetColumnHeaders();
        var byName = doc.GetColumnHeaders("Primary");
        Assert.Equal(byDefault.Count, byName.Count);
        Assert.Equal(byDefault[0], byName[0]);
    }
}
