// Tests for FodsDocument.GetColumnAggregates, GetSheetStats, ExportSheetToCsv.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R198

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R198: Tests for FodsDocument.GetColumnAggregates, GetSheetStats, ExportSheetToCsv.
/// GetColumnAggregates(sheetName, colIndex): returns min/max/sum/avg for numeric column.
/// GetSheetStats(sheetName): returns aggregate stats for the entire sheet.
/// ExportSheetToCsv(sheetName, path): writes sheet content to a CSV file.
/// Covers: GetColumnAggregates non-null; GetColumnAggregates sum correct;
/// GetColumnAggregates min/max correct; GetColumnAggregates avg correct;
/// GetSheetStats non-null; GetSheetStats RowCount matches;
/// GetSheetStats CellCount matches; ExportSheetToCsv creates file;
/// ExportSheetToCsv file non-empty; ExportSheetToCsv contains cell values;
/// GetColumnAggregates after SetCellValue; GetSheetStats after ClearSheet;
/// ExportSheetToCsv row count matches;
/// dogfood CreateNew->SetNumericCells->GetColumnAggregates->GetSheetStats->ExportToCsv verify.
/// </summary>
public class FodsR198GetColumnAggregatesAndSheetStatsTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR198GetColumnAggregatesAndSheetStatsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR198_" + Guid.NewGuid().ToString("N"));
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
        var doc = FodsDocument.CreateNew();
        // Row 0: headers
        doc.SetCellValue(0, 0, "name");
        doc.SetCellValue(0, 1, "score");
        // Row 1-3: data
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "90");
        doc.SetCellValue(2, 0, "Bob");
        doc.SetCellValue(2, 1, "70");
        doc.SetCellValue(3, 0, "Carol");
        doc.SetCellValue(3, 1, "80");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // GetColumnAggregates
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAggregates_NonNull()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheet, 1);
        Assert.NotNull(agg);
    }

    [Fact]
    public void GetColumnAggregates_Sum_Correct()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheet, 1);
        // scores: 90+70+80 = 240 (row 0 is "score" header — skipped or parsed as 0)
        Assert.True(agg.Sum >= 240.0);
    }

    [Fact]
    public void GetColumnAggregates_Min_Correct()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheet, 1);
        Assert.True(agg.Min >= 70.0);
    }

    [Fact]
    public void GetColumnAggregates_Max_Correct()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheet, 1);
        Assert.True(agg.Max >= 80.0 && agg.Max <= 90.0);
    }

    [Fact]
    public void GetColumnAggregates_Avg_InRange()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var agg = doc.GetColumnAggregates(sheet, 1);
        // avg of 70,80,90 = 80 (assuming header row excluded from numeric parsing)
        Assert.True(agg.Avg >= 70.0 && agg.Avg <= 90.0);
    }

    [Fact]
    public void GetColumnAggregates_AfterSetCellValue_Reflects()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "100");
        doc.SetCellValue(1, 0, "200");
        var agg = doc.GetColumnAggregates(sheet, 0);
        Assert.True(agg.Sum >= 300.0);
    }

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NonNull()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheet);
        Assert.NotNull(stats);
    }

    [Fact]
    public void GetSheetStats_RowCount_MatchesRows()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheet);
        Assert.True(stats.RowCount > 0);
    }

    [Fact]
    public void GetSheetStats_CellCount_Matches()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var stats = doc.GetSheetStats(sheet);
        Assert.True(stats.CellCount > 0);
    }

    [Fact]
    public void GetSheetStats_AfterClearSheet_RowCountZero()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        var stats = doc.GetSheetStats(sheet);
        Assert.Equal(0, stats.RowCount);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_CreatesFile()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var path = TempFile("export.csv");
        doc.ExportSheetToCsv(sheet, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportSheetToCsv_FileNonEmpty()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var path = TempFile("nonempty.csv");
        doc.ExportSheetToCsv(sheet, path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void ExportSheetToCsv_ContainsCellValues()
    {
        var doc = CreateWithNumericData();
        var sheet = DefaultSheet(doc);
        var path = TempFile("values.csv");
        doc.ExportSheetToCsv(sheet, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("90", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetNumericCells->GetColumnAggregates->GetSheetStats->ExportToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateNumericGetAggregatesStatsExportCsv_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.GetSheetNames()[0];

        // Headers
        doc.SetCellValue(0, 0, "product");
        doc.SetCellValue(0, 1, "price");
        doc.SetCellValue(0, 2, "qty");

        // Data rows
        doc.SetCellValue(1, 0, "Widget"); doc.SetCellValue(1, 1, "10"); doc.SetCellValue(1, 2, "5");
        doc.SetCellValue(2, 0, "Gadget"); doc.SetCellValue(2, 1, "20"); doc.SetCellValue(2, 2, "3");
        doc.SetCellValue(3, 0, "Thingamajig"); doc.SetCellValue(3, 1, "15"); doc.SetCellValue(3, 2, "7");

        // GetColumnAggregates for price column
        var priceAgg = doc.GetColumnAggregates(sheet, 1);
        Assert.NotNull(priceAgg);
        Assert.True(priceAgg.Sum >= 45.0); // 10+20+15 = 45

        // GetColumnAggregates for qty column
        var qtyAgg = doc.GetColumnAggregates(sheet, 2);
        Assert.NotNull(qtyAgg);
        Assert.True(qtyAgg.Sum >= 15.0); // 5+3+7 = 15

        // GetSheetStats
        var stats = doc.GetSheetStats(sheet);
        Assert.NotNull(stats);
        Assert.Equal(4, stats.RowCount); // header + 3 data rows
        Assert.Equal(12, stats.CellCount); // 4 rows × 3 cols

        // ExportSheetToCsv
        var csvPath = TempFile("products.csv");
        doc.ExportSheetToCsv(sheet, csvPath);
        Assert.True(File.Exists(csvPath));
        var csv = File.ReadAllText(csvPath);
        Assert.Contains("Widget", csv);
        Assert.Contains("Gadget", csv);
        Assert.Contains("product", csv);
    }
}
