// Tests for FodsPdfExportResult properties.
// Sprint: ff-sprint-s144-dotnet-deepening-20260627
// Ledger: PC-FODS-R152

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R152: Tests for FodsPdfExportResult properties.
/// FodsPdfExportResult is the return type of FodsPdfExporter.ExportToPdf.
/// It exposes OutputPath, PageCount, SheetCount, and TotalRowsWritten as init-only properties.
/// Covers: OutputPath default empty; PageCount default 0; SheetCount default 0;
/// TotalRowsWritten default 0; OutputPath set via object initializer; PageCount set;
/// SheetCount set; TotalRowsWritten set; ExportToPdf returns non-null result;
/// dogfood CreateNew->SetCellValue->ExportToPdf->result properties verified.
/// </summary>
public class FodsR152PdfExportResultPropertiesTests
{
    // -------------------------------------------------------------------------
    // Default property values
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsPdfExportResult_OutputPath_DefaultIsEmpty()
    {
        var result = new FodsPdfExportResult();
        Assert.Equal(string.Empty, result.OutputPath);
    }

    [Fact]
    public void FodsPdfExportResult_PageCount_DefaultIsZero()
    {
        var result = new FodsPdfExportResult();
        Assert.Equal(0, result.PageCount);
    }

    [Fact]
    public void FodsPdfExportResult_SheetCount_DefaultIsZero()
    {
        var result = new FodsPdfExportResult();
        Assert.Equal(0, result.SheetCount);
    }

    [Fact]
    public void FodsPdfExportResult_TotalRowsWritten_DefaultIsZero()
    {
        var result = new FodsPdfExportResult();
        Assert.Equal(0, result.TotalRowsWritten);
    }

    // -------------------------------------------------------------------------
    // Object initializer
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsPdfExportResult_OutputPath_SetViaObjectInitializer()
    {
        var result = new FodsPdfExportResult { OutputPath = "/out/report.pdf" };
        Assert.Equal("/out/report.pdf", result.OutputPath);
    }

    [Fact]
    public void FodsPdfExportResult_PageCount_SetViaObjectInitializer()
    {
        var result = new FodsPdfExportResult { PageCount = 5 };
        Assert.Equal(5, result.PageCount);
    }

    [Fact]
    public void FodsPdfExportResult_SheetCount_SetViaObjectInitializer()
    {
        var result = new FodsPdfExportResult { SheetCount = 2 };
        Assert.Equal(2, result.SheetCount);
    }

    [Fact]
    public void FodsPdfExportResult_TotalRowsWritten_SetViaObjectInitializer()
    {
        var result = new FodsPdfExportResult { TotalRowsWritten = 100 };
        Assert.Equal(100, result.TotalRowsWritten);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> SetCellValue -> ExportToPdf -> result properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ExportToPdf_ResultPropertiesValid()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Quarter");
        doc.SetCellValue(0, 1, "Revenue");
        doc.SetCellValue(1, 0, "Q1");
        doc.SetCellValue(1, 1, "125000");

        var path = Path.Combine(Path.GetTempPath(), $"fods_r152_{Guid.NewGuid():N}.pdf");
        try
        {
            var result = FodsPdfExporter.ExportToPdf(doc, path);
            Assert.NotNull(result);
            Assert.Equal(path, result.OutputPath);
            Assert.True(result.PageCount >= 1, $"Expected PageCount >= 1, got {result.PageCount}");
            Assert.True(result.SheetCount >= 1, $"Expected SheetCount >= 1, got {result.SheetCount}");
            Assert.True(result.TotalRowsWritten >= 0);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
