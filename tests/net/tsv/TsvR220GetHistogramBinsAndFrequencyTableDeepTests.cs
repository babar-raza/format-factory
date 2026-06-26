// Tests for TsvDocument.GetHistogramBins, GetFrequencyTable, GetBinCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R220

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R220: Tests for TsvDocument.GetHistogramBins, GetFrequencyTable, GetBinCount deeper.
/// GetHistogramBins(colName, binCount): partitions the column values into binCount equal-width bins.
/// GetFrequencyTable(colName): returns each distinct value and its count.
/// GetBinCount(colName, binCount): returns the number of values in each bin as an array.
/// Covers: GetHistogramBins no-throw; GetHistogramBins non-null; GetHistogramBins length equals binCount;
/// GetHistogramBins consistent; GetHistogramBins save-load;
/// GetFrequencyTable no-throw; GetFrequencyTable non-null; GetFrequencyTable non-empty;
/// GetFrequencyTable consistent; GetFrequencyTable save-load; GetFrequencyTable sum equals row count;
/// GetBinCount no-throw; GetBinCount non-null; GetBinCount length equals binCount;
/// GetBinCount sum leq row count; GetBinCount consistent; GetBinCount save-load;
/// dogfood LoadFile→GetHistogramBins→GetFrequencyTable→GetBinCount→SaveToFile pipeline.
/// </summary>
public class TsvR220GetHistogramBinsAndFrequencyTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR220GetHistogramBinsAndFrequencyTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR220_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateGradeTsv()
    {
        var path = TempFile("grades.tsv");
        var content =
            "Student\tGrade\tSubject\tYear\n" +
            "Alice\t92\tMath\t2023\n" +
            "Bob\t78\tMath\t2023\n" +
            "Carol\t88\tMath\t2023\n" +
            "Dave\t65\tMath\t2023\n" +
            "Eve\t95\tMath\t2023\n" +
            "Frank\t72\tMath\t2023\n" +
            "Grace\t85\tMath\t2023\n" +
            "Hector\t60\tScience\t2023\n" +
            "Iris\t90\tScience\t2023\n" +
            "Jack\t77\tScience\t2023\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetHistogramBins
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogramBins_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var ex = Record.Exception(() => doc.GetHistogramBins("Grade", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogramBins_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.NotNull(doc.GetHistogramBins("Grade", 5));
    }

    [Fact]
    public void GetHistogramBins_Length_Equals_BinCount()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.Equal(5, doc.GetHistogramBins("Grade", 5).Length);
    }

    [Fact]
    public void GetHistogramBins_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var b1 = doc.GetHistogramBins("Grade", 4);
        var b2 = doc.GetHistogramBins("Grade", 4);
        Assert.Equal(b1.Length, b2.Length);
    }

    [Fact]
    public void GetHistogramBins_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var before = doc.GetHistogramBins("Grade", 4);
        var path = TempFile("hb_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetHistogramBins("Grade", 4);
        Assert.Equal(before.Length, after.Length);
    }

    [Fact]
    public void GetHistogramBins_DifferentBinCounts()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.Equal(3, doc.GetHistogramBins("Grade", 3).Length);
        Assert.Equal(10, doc.GetHistogramBins("Grade", 10).Length);
    }

    // -------------------------------------------------------------------------
    // GetFrequencyTable
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrequencyTable_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var ex = Record.Exception(() => doc.GetFrequencyTable("Subject"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrequencyTable_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.NotNull(doc.GetFrequencyTable("Subject"));
    }

    [Fact]
    public void GetFrequencyTable_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.NotEmpty(doc.GetFrequencyTable("Subject"));
    }

    [Fact]
    public void GetFrequencyTable_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var f1 = doc.GetFrequencyTable("Subject");
        var f2 = doc.GetFrequencyTable("Subject");
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void GetFrequencyTable_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var before = doc.GetFrequencyTable("Subject").Count;
        var path = TempFile("ft_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrequencyTable("Subject").Count);
    }

    [Fact]
    public void GetFrequencyTable_Sum_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var table = doc.GetFrequencyTable("Subject");
        int total = 0;
        foreach (var count in table.Values) total += count;
        Assert.Equal(doc.GetRowCount(), total);
    }

    // -------------------------------------------------------------------------
    // GetBinCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBinCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var ex = Record.Exception(() => doc.GetBinCount("Grade", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBinCount_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.NotNull(doc.GetBinCount("Grade", 5));
    }

    [Fact]
    public void GetBinCount_Length_Equals_BinCount()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        Assert.Equal(5, doc.GetBinCount("Grade", 5).Length);
    }

    [Fact]
    public void GetBinCount_Sum_Leq_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var bins = doc.GetBinCount("Grade", 5);
        int total = 0;
        foreach (var c in bins) total += c;
        Assert.True(total <= doc.GetRowCount());
    }

    [Fact]
    public void GetBinCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var b1 = doc.GetBinCount("Grade", 4);
        var b2 = doc.GetBinCount("Grade", 4);
        Assert.Equal(b1.Length, b2.Length);
        for (int i = 0; i < b1.Length; i++) Assert.Equal(b1[i], b2[i]);
    }

    [Fact]
    public void GetBinCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateGradeTsv());
        var before = doc.GetBinCount("Grade", 4);
        var path = TempFile("bc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetBinCount("Grade", 4);
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++) Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetHistogramBins_GetFrequencyTable_GetBinCount_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_survey.tsv");
        var content =
            "RespondentId\tAge\tIncome\tSatisfaction\tRegion\n" +
            "R001\t28\t45000\t4\tNorth\n" +
            "R002\t35\t72000\t3\tSouth\n" +
            "R003\t42\t95000\t5\tEast\n" +
            "R004\t55\t125000\t4\tNorth\n" +
            "R005\t29\t48000\t2\tWest\n" +
            "R006\t38\t81000\t4\tSouth\n" +
            "R007\t47\t110000\t5\tEast\n" +
            "R008\t31\t55000\t3\tNorth\n" +
            "R009\t62\t145000\t4\tWest\n" +
            "R010\t24\t38000\t2\tSouth\n" +
            "R011\t45\t92000\t5\tEast\n" +
            "R012\t33\t65000\t3\tNorth\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetHistogramBins — Age
        var ageBins = doc.GetHistogramBins("Age", 4);
        Assert.NotNull(ageBins);
        Assert.Equal(4, ageBins.Length);
        Assert.Equal(ageBins.Length, doc.GetHistogramBins("Age", 4).Length); // consistent

        // GetHistogramBins — Income
        var incomeBins = doc.GetHistogramBins("Income", 5);
        Assert.NotNull(incomeBins);
        Assert.Equal(5, incomeBins.Length);

        // GetFrequencyTable — Region
        var regionFreq = doc.GetFrequencyTable("Region");
        Assert.NotNull(regionFreq);
        Assert.NotEmpty(regionFreq);
        // Sum of frequencies = row count
        int regionTotal = 0;
        foreach (var cnt in regionFreq.Values) regionTotal += cnt;
        Assert.Equal(12, regionTotal);

        // GetFrequencyTable — Satisfaction
        var satFreq = doc.GetFrequencyTable("Satisfaction");
        Assert.NotNull(satFreq);
        int satTotal = 0;
        foreach (var cnt in satFreq.Values) satTotal += cnt;
        Assert.Equal(12, satTotal);

        // GetBinCount — Age (4 bins)
        var ageBinCount = doc.GetBinCount("Age", 4);
        Assert.NotNull(ageBinCount);
        Assert.Equal(4, ageBinCount.Length);
        int totalInBins = 0;
        foreach (var c in ageBinCount) totalInBins += c;
        Assert.True(totalInBins <= 12);

        // GetBinCount — Income (5 bins)
        var incBinCount = doc.GetBinCount("Income", 5);
        Assert.Equal(5, incBinCount.Length);

        // All consistent
        Assert.Equal(regionFreq.Count, doc.GetFrequencyTable("Region").Count);

        // AddRow and recheck
        doc.AddRow(new[] { "R013", "39", "85000", "4", "East" });
        Assert.Equal(13, doc.GetRowCount());
        var newRegionFreq = doc.GetFrequencyTable("Region");
        int newRegionTotal = 0;
        foreach (var cnt in newRegionFreq.Values) newRegionTotal += cnt;
        Assert.Equal(13, newRegionTotal);

        // SaveToFile
        var savePath = TempFile("dogfood_survey_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(13, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetHistogramBins("Age", 4).Length);
        Assert.Equal(regionFreq.Count, loaded.GetFrequencyTable("Region").Count);
        Assert.Equal(4, loaded.GetBinCount("Age", 4).Length);

        // Final save
        var path2 = TempFile("dogfood_survey_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetFrequencyTable("Region").Count, loaded2.GetFrequencyTable("Region").Count);
    }
}
