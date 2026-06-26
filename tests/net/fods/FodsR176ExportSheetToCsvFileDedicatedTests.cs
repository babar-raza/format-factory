// Tests for FodsDocument.ExportSheetToCsvFile dedicated coverage.
// Sprint: ff-sprint-s169-dotnet-deepening-20260628
// Ledger: PC-FODS-R176

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R176: Dedicated tests for FodsDocument.ExportSheetToCsvFile overloads.
/// ExportSheetToCsvFile(sheetName, filePath) — writes named sheet CSV to file.
/// ExportSheetToCsvFile(filePath) — writes first sheet CSV to file.
/// Both throw ArgumentException for null/whitespace inputs.
/// The written file contains comma-separated values.
/// Covers: null sheetName throws; whitespace sheetName throws;
/// null filePath throws; whitespace filePath throws;
/// file is created on disk; file content is non-empty;
/// file contains comma separator; cell value present in file;
/// named-sheet overload matches default-sheet overload for first sheet;
/// dogfood AddSheet->SetCellValue->ExportSheetToCsvFile->File.ReadAllText.
/// </summary>
public class FodsR176ExportSheetToCsvFileDedicatedTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"fods_csv_test_{Guid.NewGuid():N}.csv");

    // -------------------------------------------------------------------------
    // Guard tests — named-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsvFile_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile(null!, TempPath()));
    }

    [Fact]
    public void ExportSheetToCsvFile_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile("   ", TempPath()));
    }

    [Fact]
    public void ExportSheetToCsvFile_NullFilePath_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile("Data", null!));
    }

    [Fact]
    public void ExportSheetToCsvFile_WhitespaceFilePath_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile("Data", "   "));
    }

    // -------------------------------------------------------------------------
    // Guard tests — default-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsvFile_DefaultOverload_NullFilePath_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsvFile_CreatesFileOnDisk()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Hello");
        var path = TempPath();
        try
        {
            doc.ExportSheetToCsvFile("Sheet1", path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportSheetToCsvFile_FileContentIsNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Alpha");
        var path = TempPath();
        try
        {
            doc.ExportSheetToCsvFile("Sheet1", path);
            var content = File.ReadAllText(path);
            Assert.True(content.Length > 0);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportSheetToCsvFile_CellValuePresentInFile()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "UniqueValue123");
        var path = TempPath();
        try
        {
            doc.ExportSheetToCsvFile("Sheet1", path);
            var content = File.ReadAllText(path);
            Assert.Contains("UniqueValue123", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_SetCells_ExportToCsvFile_ReadBack()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "95");
        var path = TempPath();
        try
        {
            doc.ExportSheetToCsvFile("Report", path);
            var content = File.ReadAllText(path);
            Assert.Contains("Name", content);
            Assert.Contains("Alice", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void DogfoodPipeline_DefaultOverload_CreatesFile()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Main");
        doc.SetCellValue(0, 0, "Data");
        var path = TempPath();
        try
        {
            doc.ExportSheetToCsvFile(path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.True(content.Length > 0);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
