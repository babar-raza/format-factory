// Tests for TsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R263

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R263: Tests for TsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
/// GetColumnZScore(colName, value): returns the z-score of the given value relative to the column distribution.
/// GetColumnStandardizedValues(colName): returns the list of z-scores for all values in the column.
/// Covers: GetColumnZScore no-throw; GetColumnZScore zero for mean; GetColumnZScore consistent;
/// GetColumnZScore save-load; GetColumnStandardizedValues no-throw;
/// GetColumnStandardizedValues count equals RowCount; GetColumnStandardizedValues consistent;
/// GetColumnStandardizedValues mean near zero; GetColumnStandardizedValues save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnStandardizedValues pipeline.
/// </summary>
public class TsvR263GetColumnZScoreAndStandardizedValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR263GetColumnZScoreAndStandardizedValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR263_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tscore\tage\tsalary");
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            int score = 40 + rng.Next(60);
            int age = 22 + rng.Next(43);
            double salary = Math.Round(25000 + rng.NextDouble() * 75000, 2);
            sb.AppendLine($"{i}\t{score}\t{age}\t{salary}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        double mean = doc.GetColumnMean("score");
        var ex = Record.Exception(() => doc.GetColumnZScore("score", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Zero_ForMean()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        double mean = doc.GetColumnMean("score");
        Assert.Equal(0.0, doc.GetColumnZScore("score", mean), precision: 6);
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnZScore("score", 70.0), doc.GetColumnZScore("score", 70.0));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnZScore("score", 75.0);
        var path = TempFile("zs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("score", 75.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnStandardizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStandardizedValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnStandardizedValues("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStandardizedValues_Count_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnStandardizedValues("score").Count);
    }

    [Fact]
    public void GetColumnStandardizedValues_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnStandardizedValues("score");
        var v2 = doc.GetColumnStandardizedValues("score");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnStandardizedValues_Mean_Near_Zero()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var vals = doc.GetColumnStandardizedValues("score");
        double sum = 0;
        foreach (var v in vals) sum += v;
        double mean = sum / vals.Count;
        Assert.Equal(0.0, mean, precision: 4); // mean of z-scores ≈ 0
    }

    [Fact]
    public void GetColumnStandardizedValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnStandardizedValues("age");
        var path = TempFile("sv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnStandardizedValues("age");
        Assert.Equal(before.Count, after.Count);
        for (int i = 0; i < before.Count; i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnStandardizedValues_Pipeline()
    {
        // Education — Department for Education: School Performance Tables 2024
        // Z-score analysis of GCSE Attainment 8 scores to identify outlier schools
        var path = TempFile("dfe_school_performance.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("urn\tschool_name\tla_code\tphase\tattainment8\tprogress8\tebac_pct\tabs_pct\tfsm_pct");

        var rng = new Random(20240901);
        string[] phases = { "Secondary", "Academy", "Free School", "Studio School" };
        string[] las = { "E08000035", "E09000033", "E10000012", "E06000024", "E08000003" };

        for (int i = 0; i < 200; i++)
        {
            int urn = 100000 + i;
            string phase = phases[i % phases.Length];
            string la = las[i % las.Length];
            double att8 = Math.Round(35 + rng.NextDouble() * 30, 1); // 35-65
            double prog8 = Math.Round(-1.5 + rng.NextDouble() * 3.0, 2); // -1.5 to +1.5
            double ebac = Math.Round(10 + rng.NextDouble() * 70, 1);
            double abs = Math.Round(90 + rng.NextDouble() * 8, 1);
            double fsm = Math.Round(5 + rng.NextDouble() * 40, 1);
            sb.AppendLine($"{urn}\tSchool {i}\t{la}\t{phase}\t{att8}\t{prog8}\t{ebac}\t{abs}\t{fsm}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnZScore for attainment8
        double meanAtt8 = doc.GetColumnMean("attainment8");
        Assert.True(meanAtt8 > 0);
        var zMean = doc.GetColumnZScore("attainment8", meanAtt8);
        Assert.Equal(0.0, zMean, precision: 4); // z-score of mean = 0
        Assert.Equal(zMean, doc.GetColumnZScore("attainment8", meanAtt8)); // consistent

        // Z-score for a value 1 StdDev above mean
        double sdAtt8 = doc.GetColumnStdDev("attainment8");
        Assert.True(sdAtt8 > 0);
        var zPlusOne = doc.GetColumnZScore("attainment8", meanAtt8 + sdAtt8);
        Assert.Equal(1.0, zPlusOne, precision: 4); // z-score of mean+1sd = 1

        // Z-score for a value 2 StdDevs below mean
        var zMinusTwo = doc.GetColumnZScore("attainment8", meanAtt8 - 2 * sdAtt8);
        Assert.Equal(-2.0, zMinusTwo, precision: 4); // z-score of mean-2sd = -2

        // GetColumnStandardizedValues for attainment8
        var stdAtt8 = doc.GetColumnStandardizedValues("attainment8");
        Assert.Equal(doc.RowCount, stdAtt8.Count);
        double sumZ = 0; foreach (var v in stdAtt8) sumZ += v;
        Assert.Equal(0.0, sumZ / stdAtt8.Count, precision: 4); // mean of z-scores ≈ 0
        Assert.Equal(stdAtt8, doc.GetColumnStandardizedValues("attainment8")); // consistent

        // GetColumnStandardizedValues for progress8
        var stdProg8 = doc.GetColumnStandardizedValues("progress8");
        Assert.Equal(doc.RowCount, stdProg8.Count);
        double sumZProg = 0; foreach (var v in stdProg8) sumZProg += v;
        Assert.Equal(0.0, sumZProg / stdProg8.Count, precision: 4);

        // SaveToFile
        var outPath = TempFile("dfe_performance_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(doc.GetColumnZScore("attainment8", 50.0),
                     loaded.GetColumnZScore("attainment8", 50.0), precision: 6);
        var loadedStd = loaded.GetColumnStandardizedValues("attainment8");
        Assert.Equal(stdAtt8.Count, loadedStd.Count);
        for (int i = 0; i < stdAtt8.Count; i++)
            Assert.Equal(stdAtt8[i], loadedStd[i], precision: 6);
    }
}
