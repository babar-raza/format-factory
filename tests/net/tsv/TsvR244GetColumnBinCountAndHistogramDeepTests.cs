// Tests for TsvDocument.GetColumnBinCount, GetColumnHistogram, GetColumnBinEdges deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R244

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R244: Tests for TsvDocument.GetColumnBinCount, GetColumnHistogram, GetColumnBinEdges deeper.
/// GetColumnBinCount(columnName, binCount): returns count of values per bin across the value range.
/// GetColumnHistogram(columnName, binCount): returns a histogram as a list of (edge, count) pairs.
/// GetColumnBinEdges(columnName, binCount): returns the bin boundary values.
/// Covers: GetColumnBinCount no-throw; GetColumnBinCount non-null; GetColumnBinCount sum equals row count;
/// GetColumnBinCount consistent;
/// GetColumnHistogram no-throw; GetColumnHistogram non-null; GetColumnHistogram count equals binCount;
/// GetColumnHistogram consistent;
/// GetColumnBinEdges no-throw; GetColumnBinEdges non-null; GetColumnBinEdges count equals binCount+1;
/// GetColumnBinEdges save-load;
/// dogfood CreateDoc→GetColumnBinCount→GetColumnHistogram→GetColumnBinEdges pipeline.
/// </summary>
public class TsvR244GetColumnBinCountAndHistogramDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR244GetColumnBinCountAndHistogramDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR244_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateIncomeTsv()
    {
        var path = TempFile("income.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "taxpayer_id\tincome_band\tgross_income_gbp\ttax_paid_gbp\tage_group",
            "TP001\tBasic\t18500\t1420\t25-34",
            "TP002\tBasic\t24000\t2380\t35-44",
            "TP003\tHigher\t52000\t12860\t45-54",
            "TP004\tBasic\t31000\t4020\t25-34",
            "TP005\tHigher\t65000\t17860\t55-64",
            "TP006\tBasic\t22000\t2060\t18-24",
            "TP007\tHigher\t48000\t11420\t35-44",
            "TP008\tAdditional\t115000\t40860\t45-54",
            "TP009\tBasic\t27500\t3020\t25-34",
            "TP010\tHigher\t75000\t21860\t55-64",
            "TP011\tBasic\t19800\t1660\t18-24",
            "TP012\tAdditional\t180000\t72860\t65+",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnBinCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnBinCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var ex = Record.Exception(() => doc.GetColumnBinCount("gross_income_gbp", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnBinCount_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        Assert.NotNull(doc.GetColumnBinCount("gross_income_gbp", 5));
    }

    [Fact]
    public void GetColumnBinCount_Sum_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var bins = doc.GetColumnBinCount("gross_income_gbp", 5);
        int total = 0;
        foreach (var count in bins) total += count;
        Assert.Equal(doc.RowCount, total);
    }

    [Fact]
    public void GetColumnBinCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var bins1 = doc.GetColumnBinCount("gross_income_gbp", 4);
        var bins2 = doc.GetColumnBinCount("gross_income_gbp", 4);
        Assert.Equal(bins1.Count, bins2.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHistogram_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var ex = Record.Exception(() => doc.GetColumnHistogram("gross_income_gbp", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnHistogram_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        Assert.NotNull(doc.GetColumnHistogram("gross_income_gbp", 5));
    }

    [Fact]
    public void GetColumnHistogram_Count_Equals_BinCount()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var hist = doc.GetColumnHistogram("gross_income_gbp", 5);
        Assert.Equal(5, hist.Count);
    }

    [Fact]
    public void GetColumnHistogram_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var h1 = doc.GetColumnHistogram("tax_paid_gbp", 4);
        var h2 = doc.GetColumnHistogram("tax_paid_gbp", 4);
        Assert.Equal(h1.Count, h2.Count);
    }

    // -------------------------------------------------------------------------
    // GetColumnBinEdges
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnBinEdges_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var ex = Record.Exception(() => doc.GetColumnBinEdges("gross_income_gbp", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnBinEdges_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        Assert.NotNull(doc.GetColumnBinEdges("gross_income_gbp", 5));
    }

    [Fact]
    public void GetColumnBinEdges_Count_Equals_BinCountPlusOne()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var edges = doc.GetColumnBinEdges("gross_income_gbp", 5);
        Assert.Equal(6, edges.Count); // binCount + 1
    }

    [Fact]
    public void GetColumnBinEdges_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateIncomeTsv());
        var before = doc.GetColumnBinEdges("gross_income_gbp", 4).Count;
        var path = TempFile("be_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnBinEdges("gross_income_gbp", 4).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnBinCount_GetColumnHistogram_GetColumnBinEdges_Pipeline()
    {
        // UK education — A-level score distribution analysis for university admissions
        var path = TempFile("alevels.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("student_id\tsubject\tucas_points\tbest3_grade\tschool_type\tregion");
        var rng = new Random(20240901);
        string[] subjects = { "Mathematics", "Further_Maths", "Physics", "Chemistry", "Biology", "Economics", "History", "English_Lit" };
        string[] grades = { "A*A*A*", "A*A*A", "A*AA", "AAA", "AAB", "ABB", "BBB", "BBC", "BCC" };
        string[] schools = { "Grammar", "Independent", "Comprehensive", "Sixth_Form_College" };
        string[] regions = { "London", "South_East", "North_West", "Yorkshire", "Midlands", "South_West" };
        for (int i = 0; i < 150; i++)
        {
            var subj = subjects[i % 8];
            // UCAS points 72-168 (BBB to A*A*A*)
            int points = 72 + rng.Next(0, 97);
            var grade = grades[Math.Max(0, (168 - points) / 12)];
            var school = schools[i % 4];
            var region = regions[i % 6];
            lines.Add($"STU{i:D5}\t{subj}\t{points}\t{grade}\t{school}\t{region}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnBinCount — 6 bins for UCAS points distribution
        var bins6 = doc.GetColumnBinCount("ucas_points", 6);
        Assert.NotNull(bins6);
        Assert.Equal(6, bins6.Count);
        int binTotal = 0;
        foreach (var cnt in bins6) binTotal += cnt;
        Assert.Equal(150, binTotal);
        var bins6Again = doc.GetColumnBinCount("ucas_points", 6);
        Assert.Equal(bins6.Count, bins6Again.Count); // consistent

        // GetColumnHistogram — 8 bins matching grade boundaries
        var hist8 = doc.GetColumnHistogram("ucas_points", 8);
        Assert.NotNull(hist8);
        Assert.Equal(8, hist8.Count);
        var hist8Again = doc.GetColumnHistogram("ucas_points", 8);
        Assert.Equal(hist8.Count, hist8Again.Count); // consistent

        // GetColumnBinEdges
        var edges8 = doc.GetColumnBinEdges("ucas_points", 8);
        Assert.NotNull(edges8);
        Assert.Equal(9, edges8.Count); // 8 bins = 9 edges
        // Edges should be monotonically increasing
        for (int i = 0; i < edges8.Count - 1; i++)
            Assert.True(edges8[i] <= edges8[i + 1]);
        var edges8Again = doc.GetColumnBinEdges("ucas_points", 8);
        Assert.Equal(edges8.Count, edges8Again.Count); // consistent

        // SaveToFile
        var outPath = TempFile("alevels_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(bins6.Count, loaded.GetColumnBinCount("ucas_points", 6).Count);
        Assert.Equal(hist8.Count, loaded.GetColumnHistogram("ucas_points", 8).Count);
        Assert.Equal(edges8.Count, loaded.GetColumnBinEdges("ucas_points", 8).Count);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean and GetColumnStdDev consistency
        var mean = doc.GetColumnMean("ucas_points");
        var std = doc.GetColumnStdDev("ucas_points");
        Assert.True(mean >= 72 && mean <= 168);
        Assert.True(std >= 0);
    }
}
