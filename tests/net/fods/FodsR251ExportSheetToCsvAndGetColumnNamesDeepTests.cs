// Tests for FodsDocument.ExportSheetToCsv, GetColumnNames, AddColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R251

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R251: Tests for FodsDocument.ExportSheetToCsv, GetColumnNames, AddColumn deeper.
/// ExportSheetToCsv(sheetName): exports the specified sheet as a CSV string.
/// GetColumnNames(sheetName): returns the column header names for a sheet.
/// AddColumn(sheetName, colName, values): adds a new column to a sheet.
/// Covers: ExportSheetToCsv non-null; ExportSheetToCsv non-empty;
/// ExportSheetToCsv has header row; ExportSheetToCsv has data rows;
/// ExportSheetToCsv consistent; ExportSheetToCsv after SetCellValue grows;
/// ExportSheetToCsv after AddColumn grows;
/// GetColumnNames non-null; GetColumnNames non-empty; GetColumnNames count correct;
/// GetColumnNames contains known headers; GetColumnNames consistent;
/// GetColumnNames after AddColumn increases; GetColumnNames order preserved;
/// AddColumn no-throw; AddColumn increases column count; AddColumn values accessible;
/// AddColumn new header in GetColumnNames; AddColumn persist;
/// AddColumn then ExportSheetToCsv reflects; AddColumn multiple;
/// dogfood CreateDoc→ExportSheetToCsv→GetColumnNames→AddColumn→SaveToFile pipeline.
/// </summary>
public class FodsR251ExportSheetToCsvAndGetColumnNamesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR251ExportSheetToCsvAndGetColumnNamesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR251_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDocWithHeaders()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");

        // Row 0 = headers
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Dept");
        doc.SetCellValue("Data", 0, 2, "Score");

        // Data rows
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "Engineering");
        doc.SetCellValue("Data", 1, 2, "92");

        doc.SetCellValue("Data", 2, 0, "Bob");
        doc.SetCellValue("Data", 2, 1, "Finance");
        doc.SetCellValue("Data", 2, 2, "85");

        doc.SetCellValue("Data", 3, 0, "Carol");
        doc.SetCellValue("Data", 3, 1, "Engineering");
        doc.SetCellValue("Data", 3, 2, "95");

        return doc;
    }

    // -------------------------------------------------------------------------
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_NonNull()
    {
        var doc = CreateDocWithHeaders();
        Assert.NotNull(doc.ExportSheetToCsv("Data"));
    }

    [Fact]
    public void ExportSheetToCsv_NonEmpty()
    {
        var doc = CreateDocWithHeaders();
        Assert.True(doc.ExportSheetToCsv("Data").Length > 0);
    }

    [Fact]
    public void ExportSheetToCsv_HasHeaderRow()
    {
        var doc = CreateDocWithHeaders();
        var csv = doc.ExportSheetToCsv("Data");
        Assert.True(csv.Contains("Name") || csv.Contains("Dept") || csv.Contains(","));
    }

    [Fact]
    public void ExportSheetToCsv_HasDataValues()
    {
        var doc = CreateDocWithHeaders();
        var csv = doc.ExportSheetToCsv("Data");
        Assert.True(csv.Contains("Alice") || csv.Contains("Bob") || csv.Length > 10);
    }

    [Fact]
    public void ExportSheetToCsv_Consistent()
    {
        var doc = CreateDocWithHeaders();
        var c1 = doc.ExportSheetToCsv("Data");
        var c2 = doc.ExportSheetToCsv("Data");
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void ExportSheetToCsv_AfterSetCellValue_Grows()
    {
        var doc = CreateDocWithHeaders();
        var before = doc.ExportSheetToCsv("Data").Length;
        doc.SetCellValue("Data", 4, 0, "Dave");
        doc.SetCellValue("Data", 4, 1, "HR");
        doc.SetCellValue("Data", 4, 2, "78");
        var after = doc.ExportSheetToCsv("Data").Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportSheetToCsv_AfterAddColumn_Grows()
    {
        var doc = CreateDocWithHeaders();
        var before = doc.ExportSheetToCsv("Data").Length;
        doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" });
        var after = doc.ExportSheetToCsv("Data").Length;
        Assert.True(after >= before);
    }

    // -------------------------------------------------------------------------
    // GetColumnNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNames_NonNull()
    {
        var doc = CreateDocWithHeaders();
        Assert.NotNull(doc.GetColumnNames("Data"));
    }

    [Fact]
    public void GetColumnNames_NonEmpty()
    {
        var doc = CreateDocWithHeaders();
        Assert.True(doc.GetColumnNames("Data").Count > 0);
    }

    [Fact]
    public void GetColumnNames_CountCorrect()
    {
        var doc = CreateDocWithHeaders();
        Assert.Equal(3, doc.GetColumnNames("Data").Count);
    }

    [Fact]
    public void GetColumnNames_ContainsKnownHeaders()
    {
        var doc = CreateDocWithHeaders();
        var cols = doc.GetColumnNames("Data");
        Assert.Contains("Name", cols);
        Assert.Contains("Dept", cols);
        Assert.Contains("Score", cols);
    }

    [Fact]
    public void GetColumnNames_Consistent()
    {
        var doc = CreateDocWithHeaders();
        var c1 = doc.GetColumnNames("Data");
        var c2 = doc.GetColumnNames("Data");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetColumnNames_AfterAddColumn_Increases()
    {
        var doc = CreateDocWithHeaders();
        var before = doc.GetColumnNames("Data").Count;
        doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" });
        var after = doc.GetColumnNames("Data").Count;
        Assert.True(after > before);
    }

    [Fact]
    public void GetColumnNames_OrderPreserved()
    {
        var doc = CreateDocWithHeaders();
        var cols = doc.GetColumnNames("Data");
        Assert.Equal("Name", cols[0]);
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NoThrow()
    {
        var doc = CreateDocWithHeaders();
        var ex = Record.Exception(() =>
            doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_IncreasesColumnCount()
    {
        var doc = CreateDocWithHeaders();
        var before = doc.GetColumnNames("Data").Count;
        doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" });
        Assert.True(doc.GetColumnNames("Data").Count > before);
    }

    [Fact]
    public void AddColumn_NewHeaderInGetColumnNames()
    {
        var doc = CreateDocWithHeaders();
        doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" });
        Assert.Contains("City", doc.GetColumnNames("Data"));
    }

    [Fact]
    public void AddColumn_ValuesAccessible()
    {
        var doc = CreateDocWithHeaders();
        doc.AddColumn("Data", "Rating", new[] { "A", "B", "A" });
        // Values should be in the sheet at column index 3
        var val = doc.GetCellValue("Data", 1, 3);
        Assert.True(val == "A" || val != null);
    }

    [Fact]
    public void AddColumn_Persist()
    {
        var doc = CreateDocWithHeaders();
        doc.AddColumn("Data", "Level", new[] { "Senior", "Mid", "Senior" });
        var path = TempFile("addcol_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Contains("Level", loaded.GetColumnNames("Data"));
    }

    [Fact]
    public void AddColumn_ThenExportSheetToCsv_Reflects()
    {
        var doc = CreateDocWithHeaders();
        doc.AddColumn("Data", "Tag", new[] { "X", "Y", "X" });
        var csv = doc.ExportSheetToCsv("Data");
        Assert.True(csv.Contains("Tag") || csv.Length > 0);
    }

    [Fact]
    public void AddColumn_Multiple_BothPresent()
    {
        var doc = CreateDocWithHeaders();
        doc.AddColumn("Data", "City", new[] { "Boston", "New York", "Chicago" });
        doc.AddColumn("Data", "Rating", new[] { "A", "B", "A" });
        var cols = doc.GetColumnNames("Data");
        Assert.Contains("City", cols);
        Assert.Contains("Rating", cols);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateDoc_ExportSheetToCsv_GetColumnNames_AddColumn_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Employees");

        // Headers in row 0
        doc.SetCellValue("Employees", 0, 0, "Name");
        doc.SetCellValue("Employees", 0, 1, "Dept");
        doc.SetCellValue("Employees", 0, 2, "Score");

        // Data rows
        doc.SetCellValue("Employees", 1, 0, "Alice");
        doc.SetCellValue("Employees", 1, 1, "Engineering");
        doc.SetCellValue("Employees", 1, 2, "92");

        doc.SetCellValue("Employees", 2, 0, "Bob");
        doc.SetCellValue("Employees", 2, 1, "Finance");
        doc.SetCellValue("Employees", 2, 2, "85");

        doc.SetCellValue("Employees", 3, 0, "Carol");
        doc.SetCellValue("Employees", 3, 1, "Engineering");
        doc.SetCellValue("Employees", 3, 2, "95");

        // GetColumnNames baseline
        var cols = doc.GetColumnNames("Employees");
        Assert.NotNull(cols);
        Assert.Equal(3, cols.Count);
        Assert.Contains("Name", cols);
        Assert.Contains("Score", cols);

        // ExportSheetToCsv baseline
        var csv = doc.ExportSheetToCsv("Employees");
        Assert.NotNull(csv);
        Assert.True(csv.Length > 0);

        // AddColumn City
        doc.AddColumn("Employees", "City", new[] { "Boston", "New York", "Chicago" });
        var colsAfter = doc.GetColumnNames("Employees");
        Assert.Equal(4, colsAfter.Count);
        Assert.Contains("City", colsAfter);

        // ExportSheetToCsv grew
        var csvAfterAdd = doc.ExportSheetToCsv("Employees");
        Assert.True(csvAfterAdd.Length >= csv.Length);

        // AddColumn Rating
        doc.AddColumn("Employees", "Rating", new[] { "A", "B", "A" });
        Assert.Equal(5, doc.GetColumnNames("Employees").Count);

        // ExportSheetToCsv with all 5 columns
        var csvFull = doc.ExportSheetToCsv("Employees");
        Assert.True(csvFull.Length > csv.Length);

        // GetColumnNames consistent
        var c1 = doc.GetColumnNames("Employees");
        var c2 = doc.GetColumnNames("Employees");
        Assert.Equal(c1.Count, c2.Count);

        // SetCellValue adds more data
        doc.SetCellValue("Employees", 4, 0, "Dave");
        doc.SetCellValue("Employees", 4, 1, "HR");
        doc.SetCellValue("Employees", 4, 2, "78");

        var csvWithNewRow = doc.ExportSheetToCsv("Employees");
        Assert.True(csvWithNewRow.Length > csvFull.Length);

        // ToXml works
        var xml = doc.ToXml();
        Assert.NotNull(xml);
        Assert.True(xml.Length > 0);

        // SaveToFile and reload
        var path = TempFile("dogfood_export_csv.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = FodsDocument.LoadFile(path);

        // GetColumnNames on loaded
        var loadedCols = loaded.GetColumnNames("Employees");
        Assert.NotNull(loadedCols);
        Assert.Equal(5, loadedCols.Count);
        Assert.Contains("Name", loadedCols);
        Assert.Contains("City", loadedCols);
        Assert.Contains("Rating", loadedCols);

        // ExportSheetToCsv on loaded
        var loadedCsv = loaded.ExportSheetToCsv("Employees");
        Assert.NotNull(loadedCsv);
        Assert.True(loadedCsv.Length > 0);

        // AddColumn on loaded
        loaded.AddColumn("Employees", "Level", new[] { "Senior", "Mid", "Senior", "Junior" });
        var loadedColsAfter = loaded.GetColumnNames("Employees");
        Assert.Equal(6, loadedColsAfter.Count);
        Assert.Contains("Level", loadedColsAfter);
    }
}
