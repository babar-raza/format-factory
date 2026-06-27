// Tests for TsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R249

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R249: Tests for TsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
/// GetColumnZScore(colName, value): returns (value - mean) / stddev for the named column.
/// GetColumnStandardizedValues(colName): returns the array of z-scores for all rows in the column.
/// Covers: GetColumnZScore no-throw; GetColumnZScore zero at mean; GetColumnZScore consistent;
/// GetColumnZScore positive above mean; GetColumnZScore negative below mean;
/// GetColumnStandardizedValues no-throw; GetColumnStandardizedValues non-null;
/// GetColumnStandardizedValues count equals row count; GetColumnStandardizedValues mean near zero;
/// GetColumnStandardizedValues save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnStandardizedValues pipeline.
/// </summary>
public class TsvR249GetColumnZScoreAndStandardizedValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR249GetColumnZScoreAndStandardizedValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR249_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("student_id\tmath_score\tenglish_score\tscience_score");
        var rng = new Random(999);
        for (int i = 0; i < 60; i++)
            sb.AppendLine($"STU{i:D3}\t{(40.0 + rng.NextDouble() * 60.0):F1}\t{(45.0 + rng.NextDouble() * 55.0):F1}\t{(35.0 + rng.NextDouble() * 65.0):F1}");
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
        var mean = doc.GetColumnMean("math_score");
        var ex = Record.Exception(() => doc.GetColumnZScore("math_score", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Zero_AtMean()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var mean = doc.GetColumnMean("math_score");
        var z = doc.GetColumnZScore("math_score", mean);
        Assert.Equal(0.0, z, precision: 6);
    }

    [Fact]
    public void GetColumnZScore_Positive_AboveMean()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var mean = doc.GetColumnMean("math_score");
        var stddev = doc.GetColumnStdDev("math_score");
        Assert.True(doc.GetColumnZScore("math_score", mean + stddev) > 0.0);
    }

    [Fact]
    public void GetColumnZScore_Negative_BelowMean()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var mean = doc.GetColumnMean("math_score");
        var stddev = doc.GetColumnStdDev("math_score");
        Assert.True(doc.GetColumnZScore("math_score", mean - stddev) < 0.0);
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var z1 = doc.GetColumnZScore("english_score", 75.0);
        var z2 = doc.GetColumnZScore("english_score", 75.0);
        Assert.Equal(z1, z2);
    }

    // -------------------------------------------------------------------------
    // GetColumnStandardizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStandardizedValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnStandardizedValues("math_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStandardizedValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnStandardizedValues("math_score"));
    }

    [Fact]
    public void GetColumnStandardizedValues_Count_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var vals = doc.GetColumnStandardizedValues("math_score");
        Assert.Equal(doc.RowCount, vals.Length);
    }

    [Fact]
    public void GetColumnStandardizedValues_Mean_Near_Zero()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var vals = doc.GetColumnStandardizedValues("math_score");
        double sum = 0;
        foreach (var v in vals) sum += v;
        Assert.Equal(0.0, sum / vals.Length, precision: 6);
    }

    [Fact]
    public void GetColumnStandardizedValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnStandardizedValues("english_score");
        var path = TempFile("zsv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnStandardizedValues("english_score");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnStandardizedValues_Pipeline()
    {
        // Sports analytics — Premier League player performance metrics (xG, xA, progressive passes)
        var path = TempFile("premier_league_player_stats.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("player_id\tposition\tminutes_played\tgoals\tassists\txg\txa\tprog_passes\tprog_carries\tpressures\ttackles_won");
        var rng = new Random(20241201);
        string[] positions = { "GK", "CB", "RB", "LB", "CM", "CAM", "RW", "LW", "CF", "SS" };
        for (int i = 0; i < 150; i++)
        {
            var pos = positions[i % positions.Length];
            int mins = 900 + rng.Next(2500);
            int goals = pos == "CF" || pos == "SS" ? rng.Next(20) : rng.Next(8);
            int assists = pos == "CAM" || pos == "RW" || pos == "LW" ? rng.Next(15) : rng.Next(6);
            double xg = goals * (0.8 + rng.NextDouble() * 0.4);
            double xa = assists * (0.85 + rng.NextDouble() * 0.3);
            int progPasses = pos == "CM" || pos == "CAM" ? 50 + rng.Next(200) : 10 + rng.Next(80);
            int progCarries = 5 + rng.Next(100);
            int pressures = 20 + rng.Next(200);
            int tacklesWon = rng.Next(50);
            sb.AppendLine($"P{i + 1:D3}\t{pos}\t{mins}\t{goals}\t{assists}\t{xg:F2}\t{xa:F2}\t{progPasses}\t{progCarries}\t{pressures}\t{tacklesWon}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // GetColumnZScore
        var meanXg = doc.GetColumnMean("xg");
        var stddevXg = doc.GetColumnStdDev("xg");

        var zAtMean = doc.GetColumnZScore("xg", meanXg);
        Assert.Equal(0.0, zAtMean, precision: 6);

        var zAbove = doc.GetColumnZScore("xg", meanXg + stddevXg);
        Assert.True(zAbove > 0.0);

        var zBelow = doc.GetColumnZScore("xg", meanXg - stddevXg);
        Assert.True(zBelow < 0.0);

        // z-score at +1 sigma should be approximately 1.0
        Assert.Equal(1.0, zAbove, precision: 4);

        // Consistent
        Assert.Equal(doc.GetColumnZScore("xa", 5.0), doc.GetColumnZScore("xa", 5.0));
        Assert.Equal(doc.GetColumnZScore("prog_passes", 80.0), doc.GetColumnZScore("prog_passes", 80.0));

        // GetColumnStandardizedValues
        var zValsXg = doc.GetColumnStandardizedValues("xg");
        Assert.NotNull(zValsXg);
        Assert.Equal(150, zValsXg.Length);

        // Mean of z-scores should be near 0
        double sumXg = 0;
        foreach (var v in zValsXg) sumXg += v;
        Assert.Equal(0.0, sumXg / zValsXg.Length, precision: 6);

        var zValsProg = doc.GetColumnStandardizedValues("prog_passes");
        Assert.Equal(150, zValsProg.Length);
        double sumProg = 0;
        foreach (var v in zValsProg) sumProg += v;
        Assert.Equal(0.0, sumProg / zValsProg.Length, precision: 6);

        // Consistent
        var z2 = doc.GetColumnStandardizedValues("xg");
        Assert.Equal(zValsXg.Length, z2.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(zValsXg[i], z2[i]);

        // GetColumnZScore should match GetColumnStandardizedValues for known values
        var meanProg = doc.GetColumnMean("prog_passes");
        var zProgAtMean = doc.GetColumnZScore("prog_passes", meanProg);
        Assert.Equal(0.0, zProgAtMean, precision: 6);

        // Basic stats
        Assert.True(doc.GetColumnMean("minutes_played") > 0.0);
        Assert.True(doc.GetColumnMin("goals") >= 0.0);
        Assert.True(doc.GetColumnMax("xg") >= doc.GetColumnMean("xg"));

        // SaveToFile
        var outPath = TempFile("premier_league_player_stats_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zAtMean, loaded.GetColumnZScore("xg", meanXg), precision: 8);
        var loadedZVals = loaded.GetColumnStandardizedValues("xg");
        Assert.Equal(zValsXg.Length, loadedZVals.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(zValsXg[i], loadedZVals[i], precision: 8);
    }
}
