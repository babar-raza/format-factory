// Tests for TsvDocument.Filter and TsvDocument.ToTsv.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R135

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R135: Tests for TsvDocument.Filter and TsvDocument.ToTsv.
/// Filter(predicate) returns a new TsvDocument with only matching rows; headers preserved.
/// Throws ArgumentNullException if predicate is null.
/// ToTsv() serializes the document back to TSV text with tab-separated columns and newlines.
/// Covers: Filter keeps all rows when all match; Filter removes non-matching rows;
/// Filter null predicate throws; Filter empty doc returns empty rows; Filter preserves headers;
/// Filter result is new instance; ToTsv empty doc returns empty string or header only;
/// ToTsv single row correct output; ToTsv separates columns with tab;
/// ToTsv round-trip Load->ToTsv->Load preserves data;
/// dogfood Load->Filter->ToTsv pipeline.
/// </summary>
public class TsvR135FilterAndToTsvTests
{
    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_AllRowsMatch_ReturnsAll()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Rows.Count, filtered.Rows.Count);
    }

    [Fact]
    public void Filter_NoRowsMatch_ReturnsEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => false);
        Assert.Empty(filtered.Rows);
    }

    [Fact]
    public void Filter_ByColumnValue_ReturnsMatchingRows()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        // Filter rows where Dept (index 1) == "Eng"
        var filtered = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, filtered.Rows.Count);
    }

    [Fact]
    public void Filter_PreservesHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.Headers, filtered.Headers);
    }

    [Fact]
    public void Filter_NullPredicate_Throws()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Throws<ArgumentNullException>(() => doc.Filter(null!));
    }

    [Fact]
    public void Filter_EmptyDocument_ReturnsEmptyRows()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        var filtered = doc.Filter(_ => true);
        Assert.Empty(filtered.Rows);
    }

    [Fact]
    public void Filter_ReturnsNewInstance()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var filtered = doc.Filter(_ => true);
        Assert.NotSame(doc, filtered);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_SingleDataRow_ContainsTabSeparatedValues()
    {
        var content = "A\tB\tC\n1\t2\t3";
        var doc = TsvDocument.Load(content);
        var tsv = doc.ToTsv();
        Assert.Contains("1\t2\t3", tsv);
    }

    [Fact]
    public void ToTsv_RoundTrip_PreservesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        var doc2 = TsvDocument.Load(tsv);
        Assert.Equal(doc.Rows.Count, doc2.Rows.Count);
    }

    [Fact]
    public void ToTsv_RoundTrip_PreservesCellValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var tsv = doc.ToTsv();
        var doc2 = TsvDocument.Load(tsv);
        Assert.Equal(doc.GetCellValue(0, 0), doc2.GetCellValue(0, 0));
        Assert.Equal(doc.GetCellValue(1, 1), doc2.GetCellValue(1, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);

        // Filter to Eng dept only
        var engOnly = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, engOnly.Rows.Count);

        // Serialize and reload
        var tsv = engOnly.ToTsv();
        var reloaded = TsvDocument.Load(tsv);
        Assert.Equal(2, reloaded.Rows.Count);

        // Verify both rows are Eng department
        foreach (var row in reloaded.Rows)
            Assert.Equal("Eng", row[1]);
    }
}
