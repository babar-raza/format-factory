// Tests for FodsDocument.ExportSheetToHtml(sheetName) named-sheet overload
// and FodsDocument.GetColumnHeaders(sheetName) named-sheet overload.
// Sprint: FORMAT-FACTORY-FODS-EXPORT-BY-NAME-R132-20260626
// Ledger: R132-GOVERNED-DOTNET-FODS-EXPORTBYNAME-001

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R132: FodsDocument.ExportSheetToHtml(sheetName) — exports a named sheet to HTML.
/// FodsDocument.GetColumnHeaders(sheetName) — returns first-row headers from a named sheet.
/// Both overloads operate on a specific sheet by name rather than defaulting to sheet[0].
/// </summary>
public class FodsR132ExportSheetByNameTests
{
    private static FodsDocument BuildTwoSheetDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");

        // Sheet1 — product inventory
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "SKU");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 1, "Product");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 2, "Price");
        FodsDocument.SetCellValue(doc.Sheets[0], 1, 0, "P001");
        FodsDocument.SetCellValue(doc.Sheets[0], 1, 1, "Widget");
        FodsDocument.SetCellValue(doc.Sheets[0], 1, 2, "9.99");

        // Add Sheet2 — customer list
        var sheet2 = doc.AddSheet("Customers");
        FodsDocument.SetCellValue(sheet2, 0, 0, "CustomerID");
        FodsDocument.SetCellValue(sheet2, 0, 1, "Name");
        FodsDocument.SetCellValue(sheet2, 1, 0, "C001");
        FodsDocument.SetCellValue(sheet2, 1, 1, "Alice");

        return doc;
    }

    // ---- ExportSheetToHtml(sheetName): HTML structure ----

    [Fact]
    public void ExportSheetToHtml_NamedSheet_ContainsTableTag()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "Item");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 1, "Value");

        var html = doc.ExportSheetToHtml(doc.Sheets[0].Name);
        Assert.Contains("<table>", html);
    }

    [Fact]
    public void ExportSheetToHtml_NamedSheet_ContainsCellValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "Alpha");
        FodsDocument.SetCellValue(doc.Sheets[0], 1, 0, "Beta");

        var html = doc.ExportSheetToHtml(doc.Sheets[0].Name);
        Assert.Contains("Alpha", html);
        Assert.Contains("Beta", html);
    }

    [Fact]
    public void ExportSheetToHtml_SecondSheet_ContainsSecondSheetData()
    {
        var doc = BuildTwoSheetDoc();

        var html = doc.ExportSheetToHtml("Customers");
        Assert.Contains("CustomerID", html);
        Assert.Contains("Alice", html);
    }

    [Fact]
    public void ExportSheetToHtml_SecondSheet_DoesNotContainFirstSheetData()
    {
        var doc = BuildTwoSheetDoc();

        var html = doc.ExportSheetToHtml("Customers");
        // Widget is only in Sheet1, not Customers
        Assert.DoesNotContain("Widget", html);
    }

    [Fact]
    public void ExportSheetToHtml_FirstSheet_ContainsFirstSheetData()
    {
        var doc = BuildTwoSheetDoc();
        var sheet1Name = doc.Sheets[0].Name;

        var html = doc.ExportSheetToHtml(sheet1Name);
        Assert.Contains("SKU",    html);
        Assert.Contains("Widget", html);
        Assert.Contains("9.99",   html);
    }

    // ---- GetColumnHeaders(sheetName): named-sheet overload ----

    [Fact]
    public void GetColumnHeaders_NamedSheet_ReturnsFirstRowValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "Name");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 1, "Email");
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 2, "Phone");

        var headers = doc.GetColumnHeaders(doc.Sheets[0].Name);
        Assert.Equal("Name",  headers[0]);
        Assert.Equal("Email", headers[1]);
        Assert.Equal("Phone", headers[2]);
    }

    [Fact]
    public void GetColumnHeaders_SecondSheet_ReturnsSecondSheetHeaders()
    {
        var doc = BuildTwoSheetDoc();
        var headers = doc.GetColumnHeaders("Customers");
        Assert.Equal("CustomerID", headers[0]);
        Assert.Equal("Name",       headers[1]);
    }

    [Fact]
    public void GetColumnHeaders_NamedMatchesDefaultForFirstSheet()
    {
        var doc = BuildTwoSheetDoc();
        var defaultHeaders = doc.GetColumnHeaders();
        var namedHeaders   = doc.GetColumnHeaders(doc.Sheets[0].Name);
        Assert.Equal(defaultHeaders, namedHeaders);
    }

    // ---- Dogfood: two-sheet pipeline ----

    [Fact]
    public void DogfoodPipeline_TwoSheetExport_BothSheetsExportedCorrectly()
    {
        var doc = BuildTwoSheetDoc();
        var sheet1Name = doc.Sheets[0].Name;

        var html1 = doc.ExportSheetToHtml(sheet1Name);
        var html2 = doc.ExportSheetToHtml("Customers");
        var headers1 = doc.GetColumnHeaders(sheet1Name);
        var headers2 = doc.GetColumnHeaders("Customers");

        // Sheet1 content
        Assert.Contains("SKU",    html1);
        Assert.Contains("Widget", html1);
        Assert.Equal("SKU",    headers1[0]);
        Assert.Equal("Product",headers1[1]);

        // Sheet2 content
        Assert.Contains("CustomerID", html2);
        Assert.Contains("Alice",      html2);
        Assert.Equal("CustomerID", headers2[0]);
        Assert.Equal("Name",       headers2[1]);

        // Cross-contamination check
        Assert.DoesNotContain("Widget",     html2);
        Assert.DoesNotContain("CustomerID", html1);
    }
}
