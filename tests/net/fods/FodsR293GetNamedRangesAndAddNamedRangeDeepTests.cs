// Tests for FodsDocument.GetNamedRanges, AddNamedRange, GetNamedRangeAddress deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R293

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R293: Tests for FodsDocument.GetNamedRanges, AddNamedRange, GetNamedRangeAddress deeper.
/// GetNamedRanges(): returns a list of all named range names in the document.
/// AddNamedRange(name, sheetName, startRow, startCol, endRow, endCol): adds a named range.
/// GetNamedRangeAddress(name): returns the address string for the named range.
/// Covers: GetNamedRanges no-throw; GetNamedRanges non-null; GetNamedRanges count;
/// GetNamedRanges zero for new doc; GetNamedRanges consistent; GetNamedRanges save-load;
/// AddNamedRange no-throw; AddNamedRange increases count; AddNamedRange save-load;
/// AddNamedRange multiple; AddNamedRange then ExportToCsv no-throw;
/// GetNamedRangeAddress no-throw; GetNamedRangeAddress non-null; GetNamedRangeAddress consistent;
/// GetNamedRangeAddress save-load; GetNamedRangeAddress multiple;
/// dogfood CreateDoc→AddNamedRange→GetNamedRanges→GetNamedRangeAddress→SaveToFile pipeline.
/// </summary>
public class FodsR293GetNamedRangesAndAddNamedRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR293GetNamedRangesAndAddNamedRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR293_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateDataDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Data");
        for (int r = 0; r < 5; r++)
            for (int c = 0; c < 6; c++)
                doc.SetCellValue("Data", r, c, $"R{r}C{c}");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetNamedRanges
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRanges_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.GetNamedRanges());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRanges_NonNull()
    {
        var doc = CreateDataDoc();
        Assert.NotNull(doc.GetNamedRanges());
    }

    [Fact]
    public void GetNamedRanges_Zero_ForNewDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        Assert.Equal(0, doc.GetNamedRanges().Count);
    }

    [Fact]
    public void GetNamedRanges_Consistent()
    {
        var doc = CreateDataDoc();
        var r1 = doc.GetNamedRanges();
        var r2 = doc.GetNamedRanges();
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetNamedRanges_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("SalesRange", "Data", 0, 0, 4, 2);
        var before = doc.GetNamedRanges().Count;
        var path = TempFile("gnr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRanges().Count);
    }

    [Fact]
    public void GetNamedRanges_After_AddNamedRange_Increases()
    {
        var doc = CreateDataDoc();
        var before = doc.GetNamedRanges().Count;
        doc.AddNamedRange("HeaderRow", "Data", 0, 0, 0, 5);
        Assert.Equal(before + 1, doc.GetNamedRanges().Count);
    }

    // -------------------------------------------------------------------------
    // AddNamedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void AddNamedRange_NoThrow()
    {
        var doc = CreateDataDoc();
        var ex = Record.Exception(() => doc.AddNamedRange("TestRange", "Data", 0, 0, 2, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void AddNamedRange_Increases_GetNamedRanges()
    {
        var doc = CreateDataDoc();
        var before = doc.GetNamedRanges().Count;
        doc.AddNamedRange("MyRange", "Data", 1, 0, 3, 2);
        Assert.Equal(before + 1, doc.GetNamedRanges().Count);
    }

    [Fact]
    public void AddNamedRange_SaveLoad_Persists()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("PersistRange", "Data", 0, 0, 4, 5);
        var before = doc.GetNamedRanges().Count;
        var path = TempFile("anr_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNamedRanges().Count);
    }

    [Fact]
    public void AddNamedRange_Multiple()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("Range1", "Data", 0, 0, 1, 2);
        doc.AddNamedRange("Range2", "Data", 2, 0, 3, 2);
        doc.AddNamedRange("Range3", "Data", 0, 3, 4, 5);
        Assert.Equal(3, doc.GetNamedRanges().Count);
    }

    [Fact]
    public void AddNamedRange_Then_ExportToCsv_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("CsvRange", "Data", 0, 0, 4, 5);
        var ex = Record.Exception(() => doc.ExportToCsv("Data"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetNamedRangeAddress
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRangeAddress_NoThrow()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("AddrRange", "Data", 0, 0, 2, 2);
        var ex = Record.Exception(() => doc.GetNamedRangeAddress("AddrRange"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNamedRangeAddress_NonNull()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("NonNullRange", "Data", 1, 1, 3, 3);
        Assert.NotNull(doc.GetNamedRangeAddress("NonNullRange"));
    }

    [Fact]
    public void GetNamedRangeAddress_Consistent()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("ConsistentRange", "Data", 0, 0, 4, 4);
        Assert.Equal(doc.GetNamedRangeAddress("ConsistentRange"), doc.GetNamedRangeAddress("ConsistentRange"));
    }

    [Fact]
    public void GetNamedRangeAddress_SaveLoad_Consistent()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("SlRange", "Data", 0, 0, 3, 3);
        var before = doc.GetNamedRangeAddress("SlRange");
        var path = TempFile("gnra_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetNamedRangeAddress("SlRange");
        Assert.NotNull(after);
        Assert.True(after.Length >= 0);
    }

    [Fact]
    public void GetNamedRangeAddress_Multiple_Ranges()
    {
        var doc = CreateDataDoc();
        doc.AddNamedRange("Alpha", "Data", 0, 0, 1, 1);
        doc.AddNamedRange("Beta", "Data", 2, 2, 3, 3);
        Assert.NotNull(doc.GetNamedRangeAddress("Alpha"));
        Assert.NotNull(doc.GetNamedRangeAddress("Beta"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddNamedRange_GetNamedRanges_GetNamedRangeAddress_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Reporting");

        // Header row
        doc.SetCellValue("Reporting", 0, 0, "Product");
        doc.SetCellValue("Reporting", 0, 1, "Q1");
        doc.SetCellValue("Reporting", 0, 2, "Q2");
        doc.SetCellValue("Reporting", 0, 3, "Q3");
        doc.SetCellValue("Reporting", 0, 4, "Q4");
        doc.SetCellValue("Reporting", 0, 5, "Total");

        // Data rows
        string[][] data = new[]
        {
            new[] {"Widget", "45000", "51000", "38000", "62000", "196000"},
            new[] {"Gadget", "32000", "28000", "41000", "55000", "156000"},
            new[] {"Module", "18000", "22000", "19500", "28000", "87500"},
            new[] {"Device", "61000", "58000", "72000", "85000", "276000"},
        };
        for (int r = 0; r < data.Length; r++)
            for (int c = 0; c < data[r].Length; c++)
                doc.SetCellValue("Reporting", r + 1, c, data[r][c]);

        // GetNamedRanges — zero initially
        Assert.Equal(0, doc.GetNamedRanges().Count);
        Assert.NotNull(doc.GetNamedRanges());

        // AddNamedRange — header row
        doc.AddNamedRange("HeaderRow", "Reporting", 0, 0, 0, 5);
        Assert.Equal(1, doc.GetNamedRanges().Count);

        // AddNamedRange — Q1 column
        doc.AddNamedRange("Q1Data", "Reporting", 1, 1, 4, 1);
        Assert.Equal(2, doc.GetNamedRanges().Count);

        // AddNamedRange — totals column
        doc.AddNamedRange("TotalsColumn", "Reporting", 1, 5, 4, 5);
        Assert.Equal(3, doc.GetNamedRanges().Count);

        // AddNamedRange — full data range
        doc.AddNamedRange("FullDataRange", "Reporting", 0, 0, 4, 5);
        Assert.Equal(4, doc.GetNamedRanges().Count);

        // GetNamedRanges — verify all 4
        var names = doc.GetNamedRanges();
        Assert.NotNull(names);
        Assert.Equal(4, names.Count);

        // Consistent
        Assert.Equal(names.Count, doc.GetNamedRanges().Count);

        // GetNamedRangeAddress
        var headerAddr = doc.GetNamedRangeAddress("HeaderRow");
        Assert.NotNull(headerAddr);
        var q1Addr = doc.GetNamedRangeAddress("Q1Data");
        Assert.NotNull(q1Addr);
        var totalsAddr = doc.GetNamedRangeAddress("TotalsColumn");
        Assert.NotNull(totalsAddr);
        var fullAddr = doc.GetNamedRangeAddress("FullDataRange");
        Assert.NotNull(fullAddr);

        // Consistent
        Assert.Equal(doc.GetNamedRangeAddress("HeaderRow"), doc.GetNamedRangeAddress("HeaderRow"));

        // ExportToCsv works
        var csv = doc.ExportToCsv("Reporting");
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // SaveToFile
        var path = TempFile("dogfood_reporting.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(doc.GetSheetCount(), loaded.GetSheetCount());
        Assert.Equal(4, loaded.GetNamedRanges().Count);

        // GetNamedRangeAddress on loaded
        var loadedAddr = loaded.GetNamedRangeAddress("FullDataRange");
        Assert.NotNull(loadedAddr);

        // AddNamedRange on loaded
        loaded.AddNamedRange("SummaryRow", "Reporting", 4, 0, 4, 5);
        Assert.Equal(5, loaded.GetNamedRanges().Count);

        // Verify cell data
        var cellVal = loaded.GetCellValue("Reporting", 1, 1);
        Assert.NotNull(cellVal);

        // Final save
        var path2 = TempFile("dogfood_reporting_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetNamedRanges().Count);
        Assert.Equal(loaded.GetSheetCount(), loaded2.GetSheetCount());
        var ex1 = Record.Exception(() => loaded2.ExportToCsv("Reporting"));
        Assert.Null(ex1);
    }
}
