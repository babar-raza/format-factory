// Tests for CsvDocument.GetHistogramBins, GetFrequencyTable, GetBinCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R222: Tests for CsvDocument.GetHistogramBins, GetFrequencyTable, GetBinCount deeper.
/// GetHistogramBins(colName, binCount): partitions values into binCount equal-width bins.
/// GetFrequencyTable(colName): returns each distinct value with its count.
/// GetBinCount(colName, binCount): returns per-bin counts as an integer array.
/// Covers: GetHistogramBins no-throw; GetHistogramBins non-null; GetHistogramBins length;
/// GetHistogramBins consistent; GetHistogramBins save-load;
/// GetFrequencyTable no-throw; GetFrequencyTable non-null; GetFrequencyTable non-empty;
/// GetFrequencyTable consistent; GetFrequencyTable save-load; GetFrequencyTable sum equals row count;
/// GetBinCount no-throw; GetBinCount non-null; GetBinCount length; GetBinCount all non-negative;
/// GetBinCount consistent; GetBinCount save-load;
/// dogfood LoadFile→GetHistogramBins→GetFrequencyTable→GetBinCount→SaveToFile pipeline.
/// </summary>
public class CsvR222GetHistogramBinsAndFrequencyTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR222GetHistogramBinsAndFrequencyTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR222_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductCsv()
    {
        var path = TempFile("products.csv");
        var content =
            "Category,Price,Rating,InStock\n" +
            "Electronics,299.99,4.5,Yes\n" +
            "Clothing,49.99,3.8,Yes\n" +
            "Electronics,89.99,4.2,Yes\n" +
            "Books,14.99,4.7,Yes\n" +
            "Electronics,549.99,4.6,No\n" +
            "Clothing,79.99,4.0,Yes\n" +
            "Books,22.99,4.3,Yes\n" +
            "Toys,34.99,3.9,Yes\n" +
            "Electronics,199.99,4.4,Yes\n" +
            "Clothing,59.99,3.7,No\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHistogramBins
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogramBins_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.GetHistogramBins("Price", 4));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogramBins_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.NotNull(doc.GetHistogramBins("Price", 4));
    }

    [Fact]
    public void GetHistogramBins_Length_Equals_BinCount()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(4, doc.GetHistogramBins("Price", 4).Length);
    }

    [Fact]
    public void GetHistogramBins_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var b1 = doc.GetHistogramBins("Price", 5);
        var b2 = doc.GetHistogramBins("Price", 5);
        Assert.Equal(b1.Length, b2.Length);
    }

    [Fact]
    public void GetHistogramBins_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var before = doc.GetHistogramBins("Price", 4).Length;
        var path = TempFile("hb_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHistogramBins("Price", 4).Length);
    }

    [Fact]
    public void GetHistogramBins_Three_Bins()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(3, doc.GetHistogramBins("Price", 3).Length);
    }

    // -------------------------------------------------------------------------
    // GetFrequencyTable
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrequencyTable_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.GetFrequencyTable("Category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrequencyTable_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.NotNull(doc.GetFrequencyTable("Category"));
    }

    [Fact]
    public void GetFrequencyTable_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.NotEmpty(doc.GetFrequencyTable("Category"));
    }

    [Fact]
    public void GetFrequencyTable_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var f1 = doc.GetFrequencyTable("Category");
        var f2 = doc.GetFrequencyTable("Category");
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void GetFrequencyTable_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var before = doc.GetFrequencyTable("Category").Count;
        var path = TempFile("ft_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrequencyTable("Category").Count);
    }

    [Fact]
    public void GetFrequencyTable_Sum_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var table = doc.GetFrequencyTable("Category");
        int total = 0;
        foreach (var cnt in table.Values) total += cnt;
        Assert.Equal(doc.GetRowCount(), total);
    }

    // -------------------------------------------------------------------------
    // GetBinCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBinCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var ex = Record.Exception(() => doc.GetBinCount("Price", 4));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBinCount_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.NotNull(doc.GetBinCount("Price", 4));
    }

    [Fact]
    public void GetBinCount_Length_Equals_BinCount()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        Assert.Equal(4, doc.GetBinCount("Price", 4).Count);
    }

    [Fact]
    public void GetBinCount_All_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var bins = doc.GetBinCount("Price", 5);
        foreach (var c in bins) Assert.True(c >= 0);
    }

    [Fact]
    public void GetBinCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var b1 = doc.GetBinCount("Price", 4);
        var b2 = doc.GetBinCount("Price", 4);
        for (int i = 0; i < b1.Count; i++) Assert.Equal(b1[i], b2[i]);
    }

    [Fact]
    public void GetBinCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateProductCsv());
        var before = doc.GetBinCount("Price", 4);
        var path = TempFile("bc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetBinCount("Price", 4);
        for (int i = 0; i < before.Count; i++) Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHistogramBins_GetFrequencyTable_GetBinCount_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_responses.csv");
        var content =
            "ResponseId,Score,Category,Priority,Resolved\n" +
            "001,82,Bug,High,Yes\n" +
            "002,45,Feature,Low,No\n" +
            "003,91,Bug,Critical,Yes\n" +
            "004,73,Improvement,Medium,Yes\n" +
            "005,88,Bug,High,Yes\n" +
            "006,55,Feature,Medium,No\n" +
            "007,96,Bug,Critical,Yes\n" +
            "008,68,Improvement,Low,Yes\n" +
            "009,42,Feature,Low,No\n" +
            "010,79,Bug,High,Yes\n" +
            "011,61,Improvement,Medium,Yes\n" +
            "012,85,Feature,High,No\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetHistogramBins — Score (4 bins)
        var scoreBins = doc.GetHistogramBins("Score", 4);
        Assert.NotNull(scoreBins);
        Assert.Equal(4, scoreBins.Length);
        Assert.Equal(4, doc.GetHistogramBins("Score", 4).Length); // consistent

        // GetHistogramBins — different bin counts
        Assert.Equal(3, doc.GetHistogramBins("Score", 3).Length);
        Assert.Equal(6, doc.GetHistogramBins("Score", 6).Length);

        // GetFrequencyTable — Category
        var catFreq = doc.GetFrequencyTable("Category");
        Assert.NotNull(catFreq);
        Assert.NotEmpty(catFreq);
        int catTotal = 0;
        foreach (var cnt in catFreq.Values) catTotal += cnt;
        Assert.Equal(12, catTotal);

        // GetFrequencyTable — Priority
        var priFreq = doc.GetFrequencyTable("Priority");
        Assert.NotNull(priFreq);
        int priTotal = 0;
        foreach (var cnt in priFreq.Values) priTotal += cnt;
        Assert.Equal(12, priTotal);

        // GetFrequencyTable — Resolved
        var resolvedFreq = doc.GetFrequencyTable("Resolved");
        Assert.NotNull(resolvedFreq);
        int resTotal = 0;
        foreach (var cnt in resolvedFreq.Values) resTotal += cnt;
        Assert.Equal(12, resTotal);

        // GetBinCount — Score (4 bins)
        var scoreBinCount = doc.GetBinCount("Score", 4);
        Assert.NotNull(scoreBinCount);
        Assert.Equal(4, scoreBinCount.Count);
        foreach (var c in scoreBinCount) Assert.True(c >= 0);
        int binTotal = 0;
        foreach (var c in scoreBinCount) binTotal += c;
        Assert.True(binTotal <= 12);

        // Consistent
        Assert.Equal(catFreq.Count, doc.GetFrequencyTable("Category").Count);

        // AddRow and recheck
        doc.AddRow(new[] { "013", "77", "Bug", "Medium", "Yes" });
        Assert.Equal(13, doc.GetRowCount());
        var newCatFreq = doc.GetFrequencyTable("Category");
        int newCatTotal = 0;
        foreach (var cnt in newCatFreq.Values) newCatTotal += cnt;
        Assert.Equal(13, newCatTotal);

        // SaveToFile
        var savePath = TempFile("dogfood_responses_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(13, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetHistogramBins("Score", 4).Length);
        Assert.Equal(catFreq.Count, loaded.GetFrequencyTable("Category").Count);
        Assert.Equal(4, loaded.GetBinCount("Score", 4).Count);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("Score", cols);
        Assert.Contains("Category", cols);

        // Final save
        var path2 = TempFile("dogfood_responses_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetFrequencyTable("Category").Count, loaded2.GetFrequencyTable("Category").Count);
    }
}
