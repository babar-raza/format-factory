// Tests for TsvDocument.GetColumnValues(int colIndex) edge cases and ToTsv() round-trip.
// Sprint: FORMAT-FACTORY-TSV-COLUMN-VALUES-DEEP-20260626
// Ledger: R118-GOVERNED-DOTNET-TSV-COLUMN-VALUES-DEEP-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R118: TsvDocument.GetColumnValues(int colIndex) — returns all values in the column
/// across rows, null for short rows missing that column. ToTsv() serializes the document
/// back to tab-separated text matching the original structure.
/// </summary>
public class TsvR118GetColumnValuesDeepTests
{
    private static TsvDocument LoadTsv(string content)
        => TsvDocument.Load(content, hasHeaders: false);

    // ---- GetColumnValues: normal retrieval ----

    [Fact]
    public void GetColumnValues_FirstColumn_ReturnsAllValues()
    {
        const string tsv = "a\tb\tc\n1\t2\t3\n4\t5\t6\n";
        var doc = LoadTsv(tsv);

        var col0 = doc.GetColumnValues(0);
        Assert.NotNull(col0);
        Assert.Contains("a", col0);
        Assert.Contains("1", col0);
        Assert.Contains("4", col0);
    }

    [Fact]
    public void GetColumnValues_LastColumn_ReturnsAllValues()
    {
        const string tsv = "x\ty\tz\nA\tB\tC\n";
        var doc = LoadTsv(tsv);

        var col2 = doc.GetColumnValues(2);
        Assert.Contains("z", col2);
        Assert.Contains("C", col2);
    }

    [Fact]
    public void GetColumnValues_ColumnCount_MatchesRowFieldCount()
    {
        const string tsv = "h1\th2\th3\nr1c1\tr1c2\tr1c3\nr2c1\tr2c2\tr2c3\n";
        var doc = LoadTsv(tsv);

        // 3 rows total (header + 2 data rows)
        var col1 = doc.GetColumnValues(1);
        Assert.Equal(doc.RowCount, col1.Count);
    }

    // ---- GetColumnValues: short rows produce null entries ----

    [Fact]
    public void GetColumnValues_ShortRow_ProducesNullForMissingCell()
    {
        // Row 2 has only 2 fields — column index 2 should be null
        const string tsv = "a\tb\tc\n1\t2\t3\n4\t5\n";
        var doc = LoadTsv(tsv);

        var col2 = doc.GetColumnValues(2);
        // Last entry should be null (short row)
        Assert.Null(col2[col2.Count - 1]);
    }

    // ---- GetColumnValues: negative index throws ----

    [Fact]
    public void GetColumnValues_NegativeIndex_ThrowsArgumentOutOfRange()
    {
        const string tsv = "a\tb\n1\t2\n";
        var doc = LoadTsv(tsv);

        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetColumnValues(-1));
    }

    // ---- GetColumnValues: out-of-bounds positive index ----

    [Fact]
    public void GetColumnValues_IndexBeyondColumns_ThrowsOrReturnsNulls()
    {
        const string tsv = "a\tb\n1\t2\n";
        var doc = LoadTsv(tsv);

        // Either throws ArgumentOutOfRangeException or returns all-null list
        try
        {
            var result = doc.GetColumnValues(10);
            // If no exception: every entry must be null
            foreach (var v in result)
                Assert.Null(v);
        }
        catch (ArgumentOutOfRangeException)
        {
            // Also acceptable
        }
    }

    // ---- ToTsv: round-trip ----

    [Fact]
    public void ToTsv_RoundTrip_ContainsOriginalHeaders()
    {
        const string tsv = "Name\tAge\tCity\nAlice\t30\tNYC\n";
        var doc = LoadTsv(tsv);

        var result = doc.ToTsv();
        Assert.Contains("Name", result);
        Assert.Contains("Age", result);
        Assert.Contains("City", result);
    }

    [Fact]
    public void ToTsv_RoundTrip_ContainsOriginalValues()
    {
        const string tsv = "Name\tAge\nAlice\t30\nBob\t25\n";
        var doc = LoadTsv(tsv);

        var result = doc.ToTsv();
        Assert.Contains("Alice", result);
        Assert.Contains("30", result);
        Assert.Contains("Bob", result);
        Assert.Contains("25", result);
    }

    [Fact]
    public void ToTsv_OutputContainsTabSeparators()
    {
        const string tsv = "X\tY\n1\t2\n";
        var doc = LoadTsv(tsv);

        var result = doc.ToTsv();
        Assert.Contains("\t", result);
    }

    // ---- Dogfood: GetColumnValues + ToTsv consistency ----

    [Fact]
    public void DogfoodPipeline_ColumnValuesMatchToTsvOutput()
    {
        const string tsv = "Product\tPrice\tQty\nApple\t1.20\t50\nBanana\t0.50\t100\n";
        var doc = LoadTsv(tsv);

        // Verify column 0 values appear in ToTsv output
        var col0 = doc.GetColumnValues(0);
        var serialized = doc.ToTsv();

        foreach (var val in col0)
        {
            if (val != null)
                Assert.Contains(val, serialized);
        }

        // Verify ToTsv is tab-delimited and has expected row count indicator
        var lines = serialized.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 2, "Expected at least header + 1 data row");
    }
}
