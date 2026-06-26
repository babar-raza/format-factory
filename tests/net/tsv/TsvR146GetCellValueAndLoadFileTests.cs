// Tests for TsvDocument.GetCellValue deeper coverage and LoadFile edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R146

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R146: Tests for TsvDocument.GetCellValue deeper coverage and LoadFile edge cases.
/// GetCellValue(row, col): returns cell value; null for OOB.
/// LoadFile with hasHeaders=true vs false: affects HasHeaders and row indexing.
/// TsvDocument.Load with various content: empty lines, single row, etc.
/// Covers: GetCellValue specific cells; GetCellValue negative row returns null;
/// GetCellValue negative col returns null; LoadFile hasHeaders=true row behavior;
/// LoadFile hasHeaders=false row behavior; Load with single row;
/// Load with single column; Load with trailing newline;
/// GetColumnValues on single-column doc; Filter on single-column doc;
/// IsEmpty after Load empty string; RowCount single row doc;
/// dogfood Load(edge cases)->GetCellValue->Filter->ToTsv pipeline.
/// </summary>
public class TsvR146GetCellValueAndLoadFileTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR146GetCellValueAndLoadFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR146_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // GetCellValue deeper coverage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_Row0Col0_ReturnsFirstCell()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal("Name", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_MiddleCell_ReturnsValue()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal("Eng", doc.GetCellValue(1, 1));
    }

    [Fact]
    public void GetCellValue_LastCell_ReturnsValue()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal("91", doc.GetCellValue(3, 2));
    }

    [Fact]
    public void GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    [Fact]
    public void GetCellValue_NegativeCol_ReturnsNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Null(doc.GetCellValue(0, -1));
    }

    [Fact]
    public void GetCellValue_OobRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Null(doc.GetCellValue(100, 0));
    }

    // -------------------------------------------------------------------------
    // LoadFile hasHeaders behavior
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_WithHeaders_HasHeadersTrue()
    {
        var path = TempFile("headers.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_NoHeaders_HasHeadersFalse()
    {
        var path = TempFile("noheaders.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Edge cases: Load
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_SingleRow_RowCountIsOne()
    {
        var doc = TsvDocument.Load("Name\tScore", hasHeaders: false);
        Assert.Equal(1, doc.RowCount);
    }

    [Fact]
    public void Load_SingleColumn_ColumnCountIsOne()
    {
        var doc = TsvDocument.Load("A\n1\n2", hasHeaders: false);
        Assert.Equal(1, doc.ColumnCount);
    }

    [Fact]
    public void Load_TrailingNewline_DoesNotAddEmptyRow()
    {
        var doc = TsvDocument.Load("A\tB\n1\t2\n", hasHeaders: false);
        // Trailing newline should not create an extra empty row
        Assert.True(doc.RowCount <= 2);
    }

    [Fact]
    public void Load_Empty_IsEmpty()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues on single-column doc
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_SingleColumn_ReturnsAllValues()
    {
        var doc = TsvDocument.Load("Alice\nBob\nCarol", hasHeaders: false);
        var vals = doc.GetColumnValues(0);
        Assert.Equal(3, vals.Count);
        Assert.Contains("Alice", vals);
    }

    // -------------------------------------------------------------------------
    // Filter on single-column doc
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_SingleColumn_WorksCorrectly()
    {
        var doc = TsvDocument.Load("Alice\nBob\nCarol", hasHeaders: false);
        var filtered = doc.Filter(row => row.Length > 0 && row[0] == "Bob");
        Assert.Equal(1, filtered.RowCount);
        Assert.Equal("Bob", filtered.GetCellValue(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load edge cases -> GetCellValue -> Filter -> ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_EdgeCasesGetCellValueFilterToTsv()
    {
        var doc = TsvDocument.Load(FourRowTsv);

        // GetCellValue sanity
        Assert.Equal("Name", doc.GetCellValue(0, 0));
        Assert.Null(doc.GetCellValue(999, 999));

        // Filter
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, finance.RowCount);

        // ToTsv
        var tsv = finance.ToTsv();
        Assert.Contains("Bob", tsv);
        Assert.Contains("Dave", tsv);
        Assert.DoesNotContain("Alice", tsv);

        // Reload
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);
        Assert.Equal("Bob", reloaded.GetCellValue(0, 0));
    }
}
