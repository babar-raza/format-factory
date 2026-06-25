// Tests for TsvDocument.Headers property invariants: null when hasHeaders=false,
// string[] with correct values when hasHeaders=true.
// Sprint: FORMAT-FACTORY-TSV-HEADERS-PROPERTY-R123-20260627
// Ledger: R123-GOVERNED-DOTNET-TSV-HEADERS-PROPERTY-001

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R123: TsvDocument.Headers is a string[]? property.
/// When loaded with hasHeaders=true: Headers is non-null, has correct column names,
/// and Headers.Length == ColumnCount.
/// When loaded with hasHeaders=false: Headers is null.
/// Mutations (via the raw Rows/Headers properties) are possible because Headers is
/// set directly; modifying Headers does not change RowCount.
/// </summary>
public class TsvR123HeadersPropertyTests
{
    private static TsvDocument LoadHeaders(string tsv) =>
        TsvDocument.Load(tsv, hasHeaders: true);

    private static TsvDocument LoadNoHeaders(string tsv) =>
        TsvDocument.Load(tsv, hasHeaders: false);

    // ---- hasHeaders=true: Headers is non-null ----

    [Fact]
    public void Headers_HasHeadersTrue_IsNotNull()
    {
        var doc = LoadHeaders("Name\tAge\n");
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void Headers_HasHeadersTrue_FirstColumnName()
    {
        var doc = LoadHeaders("Name\tAge\tCity\nAlice\t30\tNYC\n");
        Assert.Equal("Name", doc.Headers![0]);
    }

    [Fact]
    public void Headers_HasHeadersTrue_AllColumnNames()
    {
        var doc = LoadHeaders("Product\tQty\tPrice\nWidget\t10\t9.99\n");
        Assert.Equal("Product", doc.Headers![0]);
        Assert.Equal("Qty",     doc.Headers![1]);
        Assert.Equal("Price",   doc.Headers![2]);
    }

    [Fact]
    public void Headers_HasHeadersTrue_LengthEqualsColumnCount()
    {
        var doc = LoadHeaders("A\tB\tC\tD\n1\t2\t3\t4\n");
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);
    }

    [Fact]
    public void Headers_HasHeadersTrue_FourColumns()
    {
        var doc = LoadHeaders("W\tX\tY\tZ\n");
        Assert.Equal(4, doc.Headers!.Length);
    }

    // ---- hasHeaders=false: Headers is null ----

    [Fact]
    public void Headers_HasHeadersFalse_IsNull()
    {
        var doc = LoadNoHeaders("Alice\t30\nBob\t25\n");
        Assert.Null(doc.Headers);
    }

    [Fact]
    public void Headers_HasHeadersFalse_RowCountIncludesFirstRow()
    {
        var doc = LoadNoHeaders("Alice\t30\nBob\t25\n");
        // All rows treated as data
        Assert.Equal(2, doc.RowCount);
    }

    // ---- HasHeaders property alignment with Headers ----

    [Fact]
    public void HasHeaders_True_WhenHeadersIsNotNull()
    {
        var doc = LoadHeaders("Col1\tCol2\n");
        Assert.True(doc.HasHeaders);
        Assert.NotNull(doc.Headers);
    }

    [Fact]
    public void HasHeaders_False_WhenHeadersIsNull()
    {
        var doc = LoadNoHeaders("v1\tv2\n");
        Assert.False(doc.HasHeaders);
        Assert.Null(doc.Headers);
    }

    // ---- Headers do not affect RowCount ----

    [Fact]
    public void Headers_DoNotCountAsRow()
    {
        var doc = LoadHeaders("H1\tH2\nR1V1\tR1V2\nR2V1\tR2V2\n");
        // 2 data rows; header is separate
        Assert.Equal(2, doc.RowCount);
    }

    // ---- Dogfood: employee roster headers ----

    [Fact]
    public void DogfoodPipeline_EmployeeRoster_HeadersCorrectAndRowsCorrect()
    {
        var tsv =
            "EmployeeID\tName\tDepartment\tSalary\n" +
            "E001\tAlice\tEngineering\t95000\n" +
            "E002\tBob\tMarketing\t72000\n" +
            "E003\tCarol\tEngineering\t105000\n";

        var doc = LoadHeaders(tsv);

        // Headers
        Assert.Equal("EmployeeID",  doc.Headers![0]);
        Assert.Equal("Name",        doc.Headers![1]);
        Assert.Equal("Department",  doc.Headers![2]);
        Assert.Equal("Salary",      doc.Headers![3]);
        Assert.Equal(4, doc.Headers!.Length);
        Assert.Equal(doc.ColumnCount, doc.Headers!.Length);

        // Data rows (3, not counting header)
        Assert.Equal(3, doc.RowCount);

        // First data row
        Assert.Equal("E001",        doc.GetCellValue(0, 0));
        Assert.Equal("Alice",       doc.GetCellValue(0, 1));
        Assert.Equal("Engineering", doc.GetCellValue(0, 2));
    }
}
