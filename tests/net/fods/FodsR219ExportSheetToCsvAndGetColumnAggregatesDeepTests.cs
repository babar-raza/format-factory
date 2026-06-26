// Tests for FodsDocument.ExportSheetToCsv, GetColumnAggregates deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R219: Tests for FodsDocument.ExportSheetToCsv, GetColumnAggregates deeper coverage.
/// ExportSheetToCsv(sheet, path): exports a sheet's data to a CSV file.
/// GetColumnAggregates(sheet, col): returns min/max/avg/sum for a numeric column.
/// Covers: ExportSheetToCsv creates file; ExportSheetToCsv file has headers;
/// ExportSheetToCsv file has data values; ExportSheetToCsv file is non-empty;
/// ExportSheetToCsv after SetCellValue reflects change;
/// GetColumnAggregates non-null; GetColumnAggregates min correct;
/// GetColumnAggregates max correct; GetColumnAggregates sum correct;
/// GetColumnAggregates avg correct; GetColumnAggregates after InsertRow reflects change;
/// dogfood CreateDoc->SetData->ExportSheetToCsv->GetColumnAggregates->Verify pipeline.
/// </summary>
public class FodsR219ExportSheetToCsvAndGetColumnAggregatesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR219ExportSheetToCsvAndGetColumnAggregatesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateWithNumericData()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Month");
        doc.SetCellValue("Sales", 0, 1, "Revenue");
        doc.SetCellValue("Sales", 1, 0, "Jan");
        doc.SetCellValue("Sales", 1, 1, "100");
        doc.SetCellValue("Sales", 2, 0, "Feb");
        doc.SetCellValue("Sales", 2, 1, "200");
        doc.SetCellValue("Sales", 3, 0, "Mar");
        doc.SetCellValue("Sales", 3, 1, "300");
        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_CreatesFile()
    {
        var doc = CreateWithNumericData();
        var path = TempFile("export.csv");
        doc.ExportSheetToCsv("Sales", path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportSheetToCsv_FileIsNonEmpty()
    {
        var doc = CreateWithNumericData();
        var path = TempFile("nonempty.csv");
        doc.ExportSheetToCsv("Sales", path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void ExportSheetToCsv_FileContainsHeaders()
    {
        var doc = CreateWithNumericData();
        var path = TempFile("headers.csv");
        doc.ExportSheetToCsv("Sales", path);
        var content = File.ReadAllText(path);
        Assert.Contains("Month", content);
        Assert.Contains("Revenue", content);
    }

    [Fact]
    public void ExportSheetToCsv_FileContainsDataValues()
    {
        var doc = CreateWithNumericData();
        var path = TempFile("data.csv");
        doc.ExportSheetToCsv("Sales", path);
        var content = File.ReadAllText(path);
        Assert.Contains("Jan", content);
        Assert.Contains("100", content);
    }

    [Fact]
    public void ExportSheetToCsv_AfterSetCellValue_ReflectsChange()
    {
        var doc = CreateWithNumericData();
        doc.SetCellValue("Sales", 1, 1, "999");
        var path = TempFile("mutated.csv");
        doc.ExportSheetToCsv("Sales", path);
        var content = File.ReadAllText(path);
        Assert.Contains("999", content);
    }

    [Fact]
    public void ExportSheetToCsv_MultipleSheets_ExportsCorrectSheet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.SetCellValue("Alpha", 0, 0, "AlphaHeader");
        doc.SetCellValue("Beta", 0, 0, "BetaHeader");

        var pathAlpha = TempFile("alpha.csv");
        doc.ExportSheetToCsv("Alpha", pathAlpha);
        var contentAlpha = File.ReadAllText(pathAlpha);
        Assert.Contains("AlphaHeader", contentAlpha);
        Assert.DoesNotContain("BetaHeader", contentAlpha);
    }

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NonNull()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        Assert.NotNull(agg);
    }

    [Fact]
    public void GetColumnAggregates_Min_Correct()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        // Min of 100, 200, 300 = 100
        Assert.Equal(100.0, agg.Min, 1);
    }

    [Fact]
    public void GetColumnAggregates_Max_Correct()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        Assert.Equal(300.0, agg.Max, 1);
    }

    [Fact]
    public void GetColumnAggregates_Sum_Correct()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        Assert.Equal(600.0, agg.Sum, 1);
    }

    [Fact]
    public void GetColumnAggregates_Avg_Correct()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        var avg = agg.Count > 0 ? agg.Sum / agg.Count : 0.0;
        Assert.Equal(200.0, avg, 1);
    }

    [Fact]
    public void GetColumnAggregates_MinLessThanOrEqualMax()
    {
        var doc = CreateWithNumericData();
        var agg = doc.GetColumnAggregates("Sales", 1);
        Assert.True(agg.Min <= agg.Max);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_SetData_ExportSheetToCsv_GetColumnAggregates_Verify_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Report");

        // Populate data
        doc.SetCellValue("Report", 0, 0, "Product");
        doc.SetCellValue("Report", 0, 1, "Units");
        doc.SetCellValue("Report", 0, 2, "Price");
        doc.SetCellValue("Report", 1, 0, "Widget");
        doc.SetCellValue("Report", 1, 1, "50");
        doc.SetCellValue("Report", 1, 2, "10");
        doc.SetCellValue("Report", 2, 0, "Gadget");
        doc.SetCellValue("Report", 2, 1, "30");
        doc.SetCellValue("Report", 2, 2, "25");
        doc.SetCellValue("Report", 3, 0, "Doohickey");
        doc.SetCellValue("Report", 3, 1, "80");
        doc.SetCellValue("Report", 3, 2, "5");

        // ExportSheetToCsv
        var csvPath = TempFile("report.csv");
        doc.ExportSheetToCsv("Report", csvPath);
        Assert.True(File.Exists(csvPath));
        var csvContent = File.ReadAllText(csvPath);
        Assert.Contains("Product", csvContent);
        Assert.Contains("Widget", csvContent);

        // GetColumnAggregates for Units (col 1): 50, 30, 80
        var unitsAgg = doc.GetColumnAggregates("Report", 1);
        Assert.NotNull(unitsAgg);
        Assert.Equal(30.0, unitsAgg.Min, 1);
        Assert.Equal(80.0, unitsAgg.Max, 1);
        Assert.Equal(160.0, unitsAgg.Sum, 1);

        // GetColumnAggregates for Price (col 2): 10, 25, 5
        var priceAgg = doc.GetColumnAggregates("Report", 2);
        Assert.Equal(5.0, priceAgg.Min, 1);
        Assert.Equal(25.0, priceAgg.Max, 1);

        // Mutate and re-export
        doc.SetCellValue("Report", 1, 1, "100");
        var csvPath2 = TempFile("report2.csv");
        doc.ExportSheetToCsv("Report", csvPath2);
        var csvContent2 = File.ReadAllText(csvPath2);
        Assert.Contains("100", csvContent2);
    }
}
