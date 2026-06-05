// R107 Wave 2: FODS ExportSheetToCsv tests
// Ledger: R107-FODS-EXPORTSHEETTOCSV

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR107ExportSheetToCsvTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void ExportSheetToCsv_DefaultSheet_ProducesCsvLines()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var csv = doc.ExportSheetToCsv();
        Assert.False(string.IsNullOrEmpty(csv));
        // CSV should have at least one line with content
        Assert.Contains("\n", csv);
    }

    [Fact]
    public void ExportSheetToCsv_NamedSheet_ProducesCsvLines()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.False(string.IsNullOrEmpty(csv));
    }

    [Fact]
    public void ExportSheetToCsv_EmptySheet_ProducesEmptyString()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Equal("", csv);
    }

    [Fact]
    public void ExportSheetToCsv_ValuesWithCommas_AreQuoted()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "hello,world");
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("\"hello,world\"", csv);
    }

    [Fact]
    public void ExportSheetToCsv_ValuesWithQuotes_AreDoubled()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.SetCellValue(0, 0, "say \"hi\"");
        var csv = doc.ExportSheetToCsv(sheet);
        Assert.Contains("\"say \"\"hi\"\"\"", csv);
    }

    [Fact]
    public void ExportSheetToCsv_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.ExportSheetToCsv("NoSuchSheet"));
    }

    [Fact]
    public void ExportSheetToCsv_NullSheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsv((string)null!));
    }

    [Fact]
    public void ExportSheetToCsv_RowCount_MatchesLineCount()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int rowCount = doc.GetRowCount(sheet);
        var csv = doc.ExportSheetToCsv(sheet);
        // Each row produces one line ending in \r\n or \n
        var lines = csv.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        // Trim trailing empty entries from \r
        int nonEmpty = 0;
        foreach (var line in lines)
            if (line.Trim().Length > 0) nonEmpty++;
        Assert.Equal(rowCount, nonEmpty);
    }
}
