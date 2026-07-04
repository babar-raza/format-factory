// Tests for CsvDocument.GetColumn(int index) and GetColumn(string headerName).
// Sprint: FORMAT-FACTORY-CSV-GET-COLUMN-20260626
// Ledger: R118-GOVERNED-DOTNET-CSV-GET-COLUMN-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R118: CsvDocument.GetColumn(int index) — returns all values in a column by index,
/// including the header row when present. GetColumn(string headerName) — returns column
/// values by header name, excluding the header itself. Both handle edge cases such as
/// empty documents, out-of-bounds indices, and missing header names.
/// </summary>
public class CsvR118GetColumnTests
{
    private static CsvDocument LoadCsv(string content, bool hasHeaders = true)
        => CsvDocument.Load(content, hasHeaders);

    // ---- GetColumn(int): basic retrieval ----

    [Fact]
    public void GetColumn_ByIndex_FirstColumn_ReturnsAllValues()
    {
        var doc = LoadCsv("Name,Age,City\nAlice,30,NYC\nBob,25,LA\n");

        var col = doc.GetColumn(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Bob", col);
    }

    [Fact]
    public void GetColumn_ByIndex_SecondColumn_ReturnsCorrectValues()
    {
        var doc = LoadCsv("Name,Age,City\nAlice,30,NYC\nBob,25,LA\n");

        var col = doc.GetColumn(1);
        Assert.Contains("30", col);
        Assert.Contains("25", col);
    }

    [Fact]
    public void GetColumn_ByIndex_ThirdColumn_ReturnsCorrectValues()
    {
        var doc = LoadCsv("Name,Age,City\nAlice,30,NYC\nBob,25,LA\n");

        var col = doc.GetColumn(2);
        Assert.Contains("NYC", col);
        Assert.Contains("LA", col);
    }

    [Fact]
    public void GetColumn_ByIndex_CountMatchesRowCount()
    {
        var doc = LoadCsv("A,B\n1,2\n3,4\n5,6\n");

        // 3 data rows (headers excluded)
        var col = doc.GetColumn(0);
        Assert.Equal(doc.RowCount, col.Count);
    }

    // ---- GetColumn(int): edge cases ----

    [Fact]
    public void GetColumn_ByIndex_NegativeIndex_ThrowsArgumentOutOfRange()
    {
        var doc = LoadCsv("A,B\n1,2\n");

        Assert.ThrowsAny<ArgumentOutOfRangeException>(() => doc.GetColumn(-1));
    }

    [Fact]
    public void GetColumn_ByIndex_EmptyDocument_ReturnsEmptyList()
    {
        var doc = LoadCsv("A,B\n");

        var col = doc.GetColumn(0);
        Assert.Empty(col);
    }

    // ---- GetColumn(string): by header name ----

    [Fact]
    public void GetColumn_ByName_ExistingHeader_ReturnsValues()
    {
        var doc = LoadCsv("Name,Score\nAlice,95\nBob,87\n");

        var col = doc.GetColumn("Score");
        Assert.Contains("95", col);
        Assert.Contains("87", col);
    }

    [Fact]
    public void GetColumn_ByName_ExcludesHeaderRow()
    {
        var doc = LoadCsv("Name,Score\nAlice,95\n");

        var col = doc.GetColumn("Name");
        // "Name" itself should NOT appear as a data value
        Assert.DoesNotContain("Name", col);
        Assert.Contains("Alice", col);
    }

    [Fact]
    public void GetColumn_ByName_MissingHeader_ThrowsOrEmpty()
    {
        var doc = LoadCsv("A,B\n1,2\n");

        // Either throws KeyNotFoundException/ArgumentException or returns empty
        try
        {
            var result = doc.GetColumn("Z");
            Assert.Empty(result);
        }
        catch (Exception ex) when (ex is ArgumentException || ex is System.Collections.Generic.KeyNotFoundException)
        {
            // Also acceptable
        }
    }

    // ---- Dogfood: GetColumn then mutation consistency ----

    [Fact]
    public void DogfoodPipeline_GetColumnAndToCsvConsistency()
    {
        var doc = LoadCsv("Product,Price,Qty\nApple,1.20,50\nBanana,0.50,100\n");

        var names = doc.GetColumn("Product");
        var prices = doc.GetColumn("Price");

        Assert.Equal(doc.RowCount, names.Count);
        Assert.Equal(doc.RowCount, prices.Count);

        // Values match what's in the CSV
        Assert.Equal("Apple", names[0]);
        Assert.Equal("1.20", prices[0]);
        Assert.Equal("Banana", names[1]);
        Assert.Equal("0.50", prices[1]);

        // Serialization still works after column queries
        var csv = doc.ToCsv();
        Assert.Contains("Apple", csv);
        Assert.Contains("Product", csv);
    }
}
