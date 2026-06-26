// Tests for FodsDocument.ExportSheetToMarkdown dedicated coverage.
// Sprint: ff-sprint-s165-dotnet-deepening-20260628
// Ledger: PC-FODS-R172

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R172: Dedicated tests for FodsDocument.ExportSheetToMarkdown() and ExportSheetToMarkdown(string sheetName).
/// ExportSheetToMarkdown returns a Markdown table string.
/// No-arg overload throws InvalidOperationException if document has no sheets.
/// Named overload throws ArgumentException if sheet not found.
/// Output contains pipe characters (|) for table formatting.
/// First row becomes headers; separator line follows; data rows follow.
/// Covers: no sheets throws InvalidOperationException; named nonexistent throws ArgumentException;
/// result is non-null non-empty string; contains pipe characters;
/// contains cell value in output; named overload returns same as first overload for first sheet;
/// single row output contains separator; dogfood CreateNew->AddSheet->SetCellValue->ExportSheetToMarkdown;
/// dogfood named and unnamed produce equivalent output.
/// </summary>
public class FodsR172ExportSheetToMarkdownDedicatedTests
{
    private static FodsDocument MakeDocWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Name");
        doc.SetCellValue("Sheet1", 0, 1, "Score");
        doc.SetCellValue("Sheet1", 1, 0, "Alice");
        doc.SetCellValue("Sheet1", 1, 1, "95");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NoSheets_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() => doc.ExportSheetToMarkdown());
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedNonexistentSheet_ThrowsArgumentException()
    {
        var doc = MakeDocWithData();
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToMarkdown("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_ResultIsNonNullNonEmpty()
    {
        var doc = MakeDocWithData();
        var result = doc.ExportSheetToMarkdown();
        Assert.NotNull(result);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void ExportSheetToMarkdown_ResultContainsPipeCharacters()
    {
        var doc = MakeDocWithData();
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("|", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_ResultContainsCellValue()
    {
        var doc = MakeDocWithData();
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("Name", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedOverload_ReturnsSameAsFirstSheet()
    {
        var doc = MakeDocWithData();
        var unnamed = doc.ExportSheetToMarkdown();
        var named = doc.ExportSheetToMarkdown("Sheet1");
        Assert.Equal(unnamed, named);
    }

    [Fact]
    public void ExportSheetToMarkdown_OutputContainsSeparatorLine()
    {
        var doc = MakeDocWithData();
        var result = doc.ExportSheetToMarkdown();
        // Markdown separator row uses dashes e.g. | --- | --- |
        Assert.Contains("---", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_ResultContainsDataValue()
    {
        var doc = MakeDocWithData();
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("Alice", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_ExportMarkdown()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Product");
        doc.SetCellValue("Report", 1, 0, "Widget");
        var result = doc.ExportSheetToMarkdown("Report");
        Assert.Contains("Product", result);
        Assert.Contains("Widget", result);
    }

    [Fact]
    public void DogfoodPipeline_NamedAndUnnamed_ProduceEquivalentOutput()
    {
        var doc = MakeDocWithData();
        var resultA = doc.ExportSheetToMarkdown();
        var resultB = doc.ExportSheetToMarkdown("Sheet1");
        Assert.Equal(resultA, resultB);
    }
}
