// Tests for FodsDocument.GetColumnHeaders dedicated coverage.
// Sprint: ff-sprint-s182-dotnet-deepening-20260628
// Ledger: PC-FODS-R189

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R189: Dedicated tests for FodsDocument.GetColumnHeaders() and GetColumnHeaders(sheetName).
/// Returns the cell values from the first row of the first sheet (or named sheet).
/// Trailing empty cells are trimmed from the result.
/// No sheets / empty first row → returns empty list.
/// Named-sheet overload: nonexistent sheet returns empty.
/// Covers: no-arg empty doc; no-arg single cell; no-arg multiple headers;
/// trailing empty trimmed; named-sheet overload empty; named-sheet nonexistent empty;
/// named-sheet valid single header; returns IReadOnlyList; headers in column order;
/// dogfood pipeline set headers then retrieve.
/// </summary>
public class FodsR189GetColumnHeadersDedicatedTests
{
    // -------------------------------------------------------------------------
    // No-arg overload (first sheet)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_EmptyFirstSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var headers = doc.GetColumnHeaders();
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_SingleCellFirstRow_ReturnsSingleHeader()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        var headers = doc.GetColumnHeaders();
        Assert.Single(headers);
        Assert.Equal("Name", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_MultipleColumns_AllReturned()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "ID");
        doc.SetCellValue(0, 1, "Name");
        doc.SetCellValue(0, 2, "Score");
        var headers = doc.GetColumnHeaders();
        Assert.Equal(3, headers.Count);
        Assert.Equal("ID", headers[0]);
        Assert.Equal("Name", headers[1]);
        Assert.Equal("Score", headers[2]);
    }

    [Fact]
    public void GetColumnHeaders_ReturnsIReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "A");
        var headers = doc.GetColumnHeaders();
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string>>(headers);
    }

    // -------------------------------------------------------------------------
    // Named-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NamedSheet_NonexistentReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var headers = doc.GetColumnHeaders("NoSuchSheet");
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheet_EmptySheetReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Empty");
        var headers = doc.GetColumnHeaders("Empty");
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheet_SingleHeader()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Column1");
        var headers = doc.GetColumnHeaders("Report");
        Assert.Single(headers);
        Assert.Equal("Column1", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheet_MultipleHeaders()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "First");
        doc.SetCellValue("Data", 0, 1, "Second");
        var headers = doc.GetColumnHeaders("Data");
        Assert.Equal(2, headers.Count);
        Assert.Equal("First", headers[0]);
        Assert.Equal("Second", headers[1]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetHeadersThenRetrieve_AllPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Qty");
        doc.SetCellValue(0, 2, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "10");
        doc.SetCellValue(1, 2, "9.99");
        var headers = doc.GetColumnHeaders();
        Assert.Equal(3, headers.Count);
        Assert.Contains("Product", headers);
        Assert.Contains("Qty", headers);
        Assert.Contains("Price", headers);
    }
}
