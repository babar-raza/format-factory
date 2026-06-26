// Tests for TsvDocument ColumnCount, Headers, HasHeaders deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R144

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R144: Tests for TsvDocument ColumnCount, Headers, HasHeaders deeper coverage.
/// ColumnCount: number of columns, inferred from Headers or first row.
/// Headers: string[] from first row when hasHeaders=true; null otherwise.
/// HasHeaders: true when document was loaded with hasHeaders=true.
/// GetCellValue: returns cell value by row/col indices.
/// Covers: ColumnCount with 3-column TSV; ColumnCount with 1-column TSV;
/// ColumnCount with 5-column TSV; ColumnCount after row added;
/// Headers not null with hasHeaders=true; Headers contains column names;
/// Headers count equals ColumnCount with hasHeaders; HasHeaders true when set;
/// HasHeaders false when not set; GetCellValue first row first col;
/// GetCellValue last row last col; GetCellValue returns null for OOB;
/// dogfood Load->Headers->GetCellValue->ColumnCount consistency pipeline.
/// </summary>
public class TsvR144ColumnCountAndHeadersTests
{
    private const string ThreeColumnTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82";

    private const string OneColumnTsv =
        "Name\n" +
        "Alice\n" +
        "Bob";

    private const string FiveColumnTsv =
        "A\tB\tC\tD\tE\n" +
        "1\t2\t3\t4\t5";

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_ThreeColumnTsv_IsThree()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_OneColumnTsv_IsOne()
    {
        var doc = TsvDocument.Load(OneColumnTsv);
        Assert.Equal(1, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_FiveColumnTsv_IsFive()
    {
        var doc = TsvDocument.Load(FiveColumnTsv);
        Assert.Equal(5, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_AfterRowAdded_RemainsConsistent()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        doc.Rows.Add(new[] { "Carol", "Eng", "88" });
        // ColumnCount should still be 3 (from first row)
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_EmptyDoc_IsZero()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // Headers
    // -------------------------------------------------------------------------

    [Fact]
    public void Headers_WithHasHeaders_IsNotNull()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv, hasHeaders: true);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_ContainsColumnNames()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv, hasHeaders: true);
        Assert.Contains("Name", doc.Headers!);
        Assert.Contains("Dept", doc.Headers!);
        Assert.Contains("Score", doc.Headers!);
    }

    [Fact]
    public void Headers_CountEqualsColumnCount()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv, hasHeaders: true);
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);
    }

    [Fact]
    public void Headers_FiveColumns_HasFiveEntries()
    {
        var doc = TsvDocument.Load(FiveColumnTsv, hasHeaders: true);
        Assert.Equal(5, doc.Headers!.Length);
        Assert.Contains("A", doc.Headers!);
        Assert.Contains("E", doc.Headers!);
    }

    // -------------------------------------------------------------------------
    // HasHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void HasHeaders_TrueWhenSet()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void HasHeaders_FalseWhenNotSet()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellValue_FirstRowFirstCol_IsCorrect()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        Assert.Equal("Name", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void GetCellValue_LastRowLastCol_IsCorrect()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        // Row 2 = Bob,Finance,82; col 2 = 82
        Assert.Equal("82", doc.GetCellValue(2, 2));
    }

    [Fact]
    public void GetCellValue_OobRow_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        Assert.Null(doc.GetCellValue(999, 0));
    }

    [Fact]
    public void GetCellValue_OobCol_ReturnsNull()
    {
        var doc = TsvDocument.Load(ThreeColumnTsv);
        Assert.Null(doc.GetCellValue(0, 999));
    }

    // -------------------------------------------------------------------------
    // Dogfood: consistency across ColumnCount, Headers, GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ColumnCountHeadersGetCellValueConsistency()
    {
        var doc = TsvDocument.Load(FiveColumnTsv, hasHeaders: true);

        // Column count
        Assert.Equal(5, doc.ColumnCount);

        // Headers line up with column count
        Assert.Equal(5, doc.Headers!.Length);

        // Row 0 = headers (A-E), row 1 = data (1-5)
        // With hasHeaders=true, headers are extracted but rows still include header row
        var colCount = doc.ColumnCount;
        Assert.Equal(5, colCount);

        // GetCellValue at (0,0) should be "A" (header row)
        Assert.Equal("A", doc.GetCellValue(0, 0));

        // HasHeaders
        Assert.True(doc.HasHeaders);
    }
}
