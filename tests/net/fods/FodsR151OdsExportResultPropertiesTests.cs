// Tests for FodsOdsExportResult properties.
// Sprint: ff-sprint-s142-dotnet-deepening-20260627
// Ledger: PC-FODS-R151

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R151: Tests for FodsOdsExportResult properties.
/// FodsOdsExportResult is the return type of FodsOdsExporter.ExportToOds.
/// It exposes OutputPath (the written file path), SheetCount, TotalRowsExported,
/// and TotalCellsExported. All are init-only properties.
/// Covers: OutputPath default empty; SheetCount default 0; TotalRowsExported default 0;
/// TotalCellsExported default 0; OutputPath set via object initializer; SheetCount set;
/// TotalRowsExported set; TotalCellsExported set; ExportToOds returns non-null result;
/// dogfood CreateNew->SetCellValue->ExportToOds->OdsExportResult properties non-zero.
/// </summary>
public class FodsR151OdsExportResultPropertiesTests
{
    // -------------------------------------------------------------------------
    // Default property values
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsOdsExportResult_OutputPath_DefaultIsEmpty()
    {
        var result = new FodsOdsExportResult();
        Assert.Equal(string.Empty, result.OutputPath);
    }

    [Fact]
    public void FodsOdsExportResult_SheetCount_DefaultIsZero()
    {
        var result = new FodsOdsExportResult();
        Assert.Equal(0, result.SheetCount);
    }

    [Fact]
    public void FodsOdsExportResult_TotalRowsExported_DefaultIsZero()
    {
        var result = new FodsOdsExportResult();
        Assert.Equal(0, result.TotalRowsExported);
    }

    [Fact]
    public void FodsOdsExportResult_TotalCellsExported_DefaultIsZero()
    {
        var result = new FodsOdsExportResult();
        Assert.Equal(0, result.TotalCellsExported);
    }

    // -------------------------------------------------------------------------
    // Object initializer
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsOdsExportResult_OutputPath_SetViaObjectInitializer()
    {
        var result = new FodsOdsExportResult { OutputPath = "/out/file.ods" };
        Assert.Equal("/out/file.ods", result.OutputPath);
    }

    [Fact]
    public void FodsOdsExportResult_SheetCount_SetViaObjectInitializer()
    {
        var result = new FodsOdsExportResult { SheetCount = 3 };
        Assert.Equal(3, result.SheetCount);
    }

    [Fact]
    public void FodsOdsExportResult_TotalRowsExported_SetViaObjectInitializer()
    {
        var result = new FodsOdsExportResult { TotalRowsExported = 42 };
        Assert.Equal(42, result.TotalRowsExported);
    }

    [Fact]
    public void FodsOdsExportResult_TotalCellsExported_SetViaObjectInitializer()
    {
        var result = new FodsOdsExportResult { TotalCellsExported = 126 };
        Assert.Equal(126, result.TotalCellsExported);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> SetCellValue -> ExportToOds -> verify result properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ExportToOds_ResultPropertiesNonZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Revenue");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9500");

        var path = Path.Combine(Path.GetTempPath(), $"fods_r151_{Guid.NewGuid():N}.ods");
        try
        {
            var result = FodsOdsExporter.ExportToOds(doc, path);
            Assert.NotNull(result);
            Assert.Equal(path, result.OutputPath);
            Assert.True(result.SheetCount >= 1, $"Expected SheetCount >= 1, got {result.SheetCount}");
            Assert.True(result.TotalRowsExported >= 1, $"Expected TotalRowsExported >= 1, got {result.TotalRowsExported}");
            Assert.True(result.TotalCellsExported >= 1, $"Expected TotalCellsExported >= 1, got {result.TotalCellsExported}");
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
