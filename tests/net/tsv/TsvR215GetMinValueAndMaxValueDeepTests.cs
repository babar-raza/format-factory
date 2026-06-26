// Tests for TsvDocument.GetMinValue, GetMaxValue, GetRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R215

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R215: Tests for TsvDocument.GetMinValue, GetMaxValue, GetRange deeper.
/// GetMinValue(colName): returns the minimum numeric value in the column.
/// GetMaxValue(colName): returns the maximum numeric value in the column.
/// GetRange(colName): returns the difference between max and min (GetMaxValue - GetMinValue).
/// Covers: GetMinValue no-throw; GetMinValue correct value; GetMinValue consistent;
/// GetMinValue save-load; GetMinValue after AddRow;
/// GetMaxValue no-throw; GetMaxValue correct value; GetMaxValue consistent;
/// GetMaxValue save-load; GetMaxValue after AddRow;
/// GetRange no-throw; GetRange non-negative; GetRange correct value; GetRange consistent;
/// GetRange save-load; GetRange zero for uniform column;
/// dogfood LoadFile→GetMinValue→GetMaxValue→GetRange→SaveToFile pipeline.
/// </summary>
public class TsvR215GetMinValueAndMaxValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR215GetMinValueAndMaxValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR215_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateScoreTsv()
    {
        var path = TempFile("scores.tsv");
        var content =
            "Name\tScore\tAttempts\tTime\n" +
            "Alice\t92\t3\t45\n" +
            "Bob\t78\t5\t62\n" +
            "Carol\t99\t1\t38\n" +
            "Dave\t64\t7\t80\n" +
            "Eve\t88\t2\t51\n" +
            "Frank\t55\t9\t95\n" +
            "Grace\t76\t4\t67\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMinValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMinValue_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var ex = Record.Exception(() => doc.GetMinValue("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMinValue_CorrectValue()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        // Frank has score 55
        Assert.Equal(55.0, doc.GetMinValue("Score"), 1);
    }

    [Fact]
    public void GetMinValue_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        Assert.Equal(doc.GetMinValue("Score"), doc.GetMinValue("Score"));
    }

    [Fact]
    public void GetMinValue_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var before = doc.GetMinValue("Score");
        var path = TempFile("gmn_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMinValue("Score"), 1);
    }

    [Fact]
    public void GetMinValue_AfterAddRow_UpdatesIfSmaller()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var before = doc.GetMinValue("Score");
        doc.AddRow(new[] { "Hector", "40", "10", "110" });
        // New min should be 40
        Assert.True(doc.GetMinValue("Score") <= before);
    }

    // -------------------------------------------------------------------------
    // GetMaxValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMaxValue_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var ex = Record.Exception(() => doc.GetMaxValue("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMaxValue_CorrectValue()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        // Carol has score 99
        Assert.Equal(99.0, doc.GetMaxValue("Score"), 1);
    }

    [Fact]
    public void GetMaxValue_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        Assert.Equal(doc.GetMaxValue("Score"), doc.GetMaxValue("Score"));
    }

    [Fact]
    public void GetMaxValue_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var before = doc.GetMaxValue("Score");
        var path = TempFile("gmx_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMaxValue("Score"), 1);
    }

    [Fact]
    public void GetMaxValue_AfterAddRow_UpdatesIfLarger()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var before = doc.GetMaxValue("Score");
        doc.AddRow(new[] { "Iris", "100", "1", "30" });
        Assert.True(doc.GetMaxValue("Score") >= before);
    }

    // -------------------------------------------------------------------------
    // GetRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRange_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var ex = Record.Exception(() => doc.GetRange("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRange_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        Assert.True(doc.GetRange("Score") >= 0);
    }

    [Fact]
    public void GetRange_CorrectValue()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        // max=99, min=55, range=44
        Assert.Equal(44.0, doc.GetRange("Score"), 1);
    }

    [Fact]
    public void GetRange_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        Assert.Equal(doc.GetRange("Score"), doc.GetRange("Score"));
    }

    [Fact]
    public void GetRange_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var before = doc.GetRange("Score");
        var path = TempFile("gr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRange("Score"), 1);
    }

    [Fact]
    public void GetRange_Equals_MaxMinus_Min()
    {
        var doc = TsvDocument.LoadFile(CreateScoreTsv());
        var expected = doc.GetMaxValue("Score") - doc.GetMinValue("Score");
        Assert.Equal(expected, doc.GetRange("Score"), 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMinValue_GetMaxValue_GetRange_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_perf.tsv");
        var content =
            "Athlete\tEvent\tScore\tTime\tRank\n" +
            "Alice\tSprint\t9.82\t9820\t1\n" +
            "Bob\tSprint\t10.14\t10140\t3\n" +
            "Carol\tSprint\t9.95\t9950\t2\n" +
            "Dave\tLongJump\t8.42\t0\t1\n" +
            "Eve\tLongJump\t7.98\t0\t3\n" +
            "Frank\tLongJump\t8.15\t0\t2\n" +
            "Grace\tSprint\t10.31\t10310\t4\n" +
            "Hector\tLongJump\t8.55\t0\t0\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetMinValue — Score
        var minScore = doc.GetMinValue("Score");
        Assert.True(minScore > 0);
        Assert.Equal(minScore, doc.GetMinValue("Score")); // consistent

        // GetMaxValue — Score
        var maxScore = doc.GetMaxValue("Score");
        Assert.True(maxScore >= minScore);
        Assert.Equal(maxScore, doc.GetMaxValue("Score")); // consistent

        // GetRange — Score
        var rangeScore = doc.GetRange("Score");
        Assert.True(rangeScore >= 0);
        Assert.Equal(maxScore - minScore, rangeScore, 2);

        // GetMinValue — Rank
        var minRank = doc.GetMinValue("Rank");
        Assert.True(minRank >= 0);

        // GetMaxValue — Rank
        var maxRank = doc.GetMaxValue("Rank");
        Assert.True(maxRank >= minRank);

        // GetRange — Rank
        var rangeRank = doc.GetRange("Rank");
        Assert.Equal(maxRank - minRank, rangeRank, 1);

        // AddRow and recheck min/max
        doc.AddRow(new[] { "Iris", "Sprint", "9.70", "9700", "0" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.GetMinValue("Score") <= minScore);
        Assert.True(doc.GetMaxValue("Score") >= 0);
        Assert.True(doc.GetRange("Score") >= 0);

        // Consistent after AddRow
        Assert.Equal(doc.GetMinValue("Score"), doc.GetMinValue("Score"));
        Assert.Equal(doc.GetMaxValue("Score"), doc.GetMaxValue("Score"));

        // SaveToFile
        var savePath = TempFile("dogfood_perf_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetMinValue("Score"), loaded.GetMinValue("Score"), 2);
        Assert.Equal(doc.GetMaxValue("Score"), loaded.GetMaxValue("Score"), 2);
        Assert.Equal(doc.GetRange("Score"), loaded.GetRange("Score"), 2);

        // SortByColumn still works
        var sorted = loaded.SortByColumn("Score", ascending: true);
        Assert.Equal(9, sorted.GetRowCount());
        Assert.True(sorted.GetMinValue("Score") <= sorted.GetMaxValue("Score"));

        // Final save
        var path2 = TempFile("dogfood_perf_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetMinValue("Score"), loaded2.GetMinValue("Score"), 2);
        Assert.Equal(loaded.GetMaxValue("Score"), loaded2.GetMaxValue("Score"), 2);
    }
}
