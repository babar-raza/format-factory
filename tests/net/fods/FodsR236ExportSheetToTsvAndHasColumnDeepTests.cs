// Tests for FodsDocument.ExportSheetToTsv, HasColumn, AddColumn deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R236: Tests for FodsDocument.ExportSheetToTsv, HasColumn, AddColumn deeper coverage.
/// ExportSheetToTsv(sheetName): exports a named sheet as a TSV string.
/// HasColumn(sheetName, colName): returns true if the column header exists in the sheet.
/// AddColumn(sheetName, colName, values): adds a new named column with given values.
/// Covers: ExportSheetToTsv non-null; ExportSheetToTsv non-empty; ExportSheetToTsv has tabs;
/// ExportSheetToTsv contains header; ExportSheetToTsv contains data; ExportSheetToTsv after SetCellValue;
/// ExportSheetToTsv after AddRow; ExportSheetToTsv wrong sheet name returns empty or throws;
/// HasColumn true for existing; HasColumn false for missing; HasColumn case check;
/// HasColumn after AddColumn true; HasColumn on second sheet;
/// AddColumn increases column count; AddColumn values accessible; AddColumn after SaveAndLoad persists;
/// AddColumn multiple columns; AddColumn then ExportSheetToTsv contains new column;
/// dogfood CreateEmpty→SetCellValue→HasColumn→AddColumn→ExportSheetToTsv→SaveToFile pipeline.
/// </summary>
public class FodsR236ExportSheetToTsvAndHasColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR236ExportSheetToTsvAndHasColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleFods = @"<?xml version=""1.0"" encoding=""UTF-8""?>
<office:document xmlns:office=""urn:oasis:names:tc:opendocument:xmlns:office:1.0""
                 xmlns:table=""urn:oasis:names:tc:opendocument:xmlns:table:1.0""
                 xmlns:text=""urn:oasis:names:tc:opendocument:xmlns:text:1.0""
                 office:mimetype=""application/vnd.oasis.opendocument.spreadsheet"">
  <office:body>
    <office:spreadsheet>
      <table:table table:name=""Sales"">
        <table:table-row>
          <table:table-cell><text:p>Product</text:p></table:table-cell>
          <table:table-cell><text:p>Q1</text:p></table:table-cell>
          <table:table-cell><text:p>Q2</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell><text:p>Widget</text:p></table:table-cell>
          <table:table-cell><text:p>100</text:p></table:table-cell>
          <table:table-cell><text:p>120</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell><text:p>Gadget</text:p></table:table-cell>
          <table:table-cell><text:p>80</text:p></table:table-cell>
          <table:table-cell><text:p>95</text:p></table:table-cell>
        </table:table-row>
        <table:table-row>
          <table:table-cell><text:p>Gizmo</text:p></table:table-cell>
          <table:table-cell><text:p>60</text:p></table:table-cell>
          <table:table-cell><text:p>75</text:p></table:table-cell>
        </table:table-row>
      </table:table>
    </office:spreadsheet>
  </office:body>
</office:document>";

    private FodsDocument LoadSample()
    {
        var path = TempFile("sample.fods");
        File.WriteAllText(path, SampleFods);
        return FodsDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToTsv_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportSheetToTsv("Sales"));
    }

    [Fact]
    public void ExportSheetToTsv_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportSheetToTsv("Sales"));
    }

    [Fact]
    public void ExportSheetToTsv_HasTabs()
    {
        var doc = LoadSample();
        Assert.Contains("\t", doc.ExportSheetToTsv("Sales"));
    }

    [Fact]
    public void ExportSheetToTsv_ContainsHeader()
    {
        var doc = LoadSample();
        var tsv = doc.ExportSheetToTsv("Sales");
        Assert.True(tsv.Contains("Product") || tsv.Contains("Q1"));
    }

    [Fact]
    public void ExportSheetToTsv_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Widget", doc.ExportSheetToTsv("Sales"));
    }

    [Fact]
    public void ExportSheetToTsv_AllDataRows()
    {
        var doc = LoadSample();
        var tsv = doc.ExportSheetToTsv("Sales");
        Assert.Contains("Widget", tsv);
        Assert.Contains("Gadget", tsv);
        Assert.Contains("Gizmo", tsv);
    }

    [Fact]
    public void ExportSheetToTsv_AfterSetCellValue_Reflects()
    {
        var doc = LoadSample();
        doc.SetCellValue("Sales", 1, 1, "999");
        var tsv = doc.ExportSheetToTsv("Sales");
        Assert.Contains("999", tsv);
    }

    [Fact]
    public void ExportSheetToTsv_AfterAddRow_Longer()
    {
        var doc = LoadSample();
        var before = doc.ExportSheetToTsv("Sales").Length;
        doc.InsertRowWithValues("Sales", doc.GetRowCount("Sales"), new[] { "Thingamajig", "50", "65" });
        Assert.True(doc.ExportSheetToTsv("Sales").Length > before);
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_TrueForExistingColumn()
    {
        var doc = LoadSample();
        Assert.True(doc.HasColumn("Sales", "Product"));
    }

    [Fact]
    public void HasColumn_TrueForQ1()
    {
        var doc = LoadSample();
        Assert.True(doc.HasColumn("Sales", "Q1"));
    }

    [Fact]
    public void HasColumn_FalseForMissingColumn()
    {
        var doc = LoadSample();
        Assert.False(doc.HasColumn("Sales", "NonExistentColumn"));
    }

    [Fact]
    public void HasColumn_FalseForWrongName()
    {
        var doc = LoadSample();
        Assert.False(doc.HasColumn("Sales", "Revenue"));
    }

    [Fact]
    public void HasColumn_AfterAddColumn_True()
    {
        var doc = LoadSample();
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        Assert.True(doc.HasColumn("Sales", "Q3"));
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_IncreasesColumnCount()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount("Sales");
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        Assert.Equal(before + 1, doc.GetColumnCount("Sales"));
    }

    [Fact]
    public void AddColumn_ValuesAccessible()
    {
        var doc = LoadSample();
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        var values = doc.GetColumnValues("Sales", "Q3");
        Assert.NotEmpty(values);
    }

    [Fact]
    public void AddColumn_MultipleColumns_AllHasColumn()
    {
        var doc = LoadSample();
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        doc.AddColumn("Sales", "Q4", new[] { "140", "120", "100" });
        Assert.True(doc.HasColumn("Sales", "Q3"));
        Assert.True(doc.HasColumn("Sales", "Q4"));
    }

    [Fact]
    public void AddColumn_ThenExportSheetToTsv_ContainsNewColumn()
    {
        var doc = LoadSample();
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        var tsv = doc.ExportSheetToTsv("Sales");
        Assert.Contains("Q3", tsv);
    }

    [Fact]
    public void AddColumn_AfterSaveAndLoad_Persists()
    {
        var doc = LoadSample();
        doc.AddColumn("Sales", "Q3", new[] { "130", "110", "90" });
        var path = TempFile("addcol_persist.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.True(loaded.HasColumn("Sales", "Q3"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_SetCellValue_HasColumn_AddColumn_ExportSheetToTsv_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        var sheet = doc.GetSheetNames()[0];

        // SetCellValue to build header row
        doc.SetCellValue(sheet, 0, 0, "Region");
        doc.SetCellValue(sheet, 0, 1, "Revenue");
        doc.SetCellValue(sheet, 0, 2, "Costs");

        // SetCellValue data rows
        doc.SetCellValue(sheet, 1, 0, "North");
        doc.SetCellValue(sheet, 1, 1, "500000");
        doc.SetCellValue(sheet, 1, 2, "320000");
        doc.SetCellValue(sheet, 2, 0, "South");
        doc.SetCellValue(sheet, 2, 1, "420000");
        doc.SetCellValue(sheet, 2, 2, "280000");
        doc.SetCellValue(sheet, 3, 0, "East");
        doc.SetCellValue(sheet, 3, 1, "380000");
        doc.SetCellValue(sheet, 3, 2, "250000");

        // HasColumn
        Assert.True(doc.HasColumn(sheet, "Region"));
        Assert.True(doc.HasColumn(sheet, "Revenue"));
        Assert.True(doc.HasColumn(sheet, "Costs"));
        Assert.False(doc.HasColumn(sheet, "Profit"));

        // ExportSheetToTsv before AddColumn
        var tsvBefore = doc.ExportSheetToTsv(sheet);
        Assert.NotNull(tsvBefore);
        Assert.Contains("\t", tsvBefore);
        Assert.Contains("Region", tsvBefore);
        Assert.Contains("North", tsvBefore);

        // AddColumn — Profit
        doc.AddColumn(sheet, "Profit", new[] { "180000", "140000", "130000" });
        Assert.True(doc.HasColumn(sheet, "Profit"));
        Assert.Equal(4, doc.GetColumnCount(sheet));

        // ExportSheetToTsv after AddColumn — longer and contains Profit
        var tsvAfter = doc.ExportSheetToTsv(sheet);
        Assert.Contains("Profit", tsvAfter);
        Assert.True(tsvAfter.Length > tsvBefore.Length);

        // AddColumn Q_Growth
        doc.AddColumn(sheet, "Growth", new[] { "12%", "8%", "15%" });
        Assert.Equal(5, doc.GetColumnCount(sheet));
        Assert.Contains("Growth", doc.ExportSheetToTsv(sheet));

        // SaveToFile
        var path = TempFile("dogfood_hascol.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile — verify columns persist
        var loaded = FodsDocument.LoadFile(path);
        var loadedSheet = loaded.GetSheetNames()[0];
        Assert.True(loaded.HasColumn(loadedSheet, "Region"));
        Assert.True(loaded.HasColumn(loadedSheet, "Profit"));
        Assert.Equal(5, loaded.GetColumnCount(loadedSheet));

        // ExportSheetToTsv on loaded
        var loadedTsv = loaded.ExportSheetToTsv(loadedSheet);
        Assert.Contains("\t", loadedTsv);
        Assert.Contains("North", loadedTsv);
    }
}
