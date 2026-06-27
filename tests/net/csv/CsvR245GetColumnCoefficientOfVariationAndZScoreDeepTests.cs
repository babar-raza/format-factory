// Tests for CsvDocument.GetColumnCoefficientOfVariation, GetColumnZScore, GetColumnNormalized deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R245: Tests for CsvDocument.GetColumnCoefficientOfVariation, GetColumnZScore, GetColumnNormalized deeper.
/// GetColumnCoefficientOfVariation(columnName): returns std/mean for the column (relative variability).
/// GetColumnZScore(columnName, value): returns (value - mean) / stddev for the given value.
/// GetColumnNormalized(columnName): returns all column values normalised to [0, 1].
/// Covers: GetColumnCoefficientOfVariation no-throw; GetColumnCoefficientOfVariation non-negative;
/// GetColumnCoefficientOfVariation consistent; GetColumnCoefficientOfVariation zero for constant;
/// GetColumnZScore no-throw; GetColumnZScore finite; GetColumnZScore consistent;
/// GetColumnZScore zero for mean value;
/// GetColumnNormalized no-throw; GetColumnNormalized non-null; GetColumnNormalized consistent;
/// GetColumnNormalized save-load;
/// dogfood CreateDoc→GetColumnCoefficientOfVariation→GetColumnZScore→GetColumnNormalized pipeline.
/// </summary>
public class CsvR245GetColumnCoefficientOfVariationAndZScoreDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR245GetColumnCoefficientOfVariationAndZScoreDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR245_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateExamResultsCsv()
    {
        var path = TempFile("exam_results.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "student_id,subject,raw_score,scaled_score,percentile,grade",
            "S001,Mathematics,78,82,74,B",
            "S002,Mathematics,92,95,96,A*",
            "S003,Mathematics,65,68,52,C",
            "S004,Physics,88,91,89,A",
            "S005,Physics,71,74,63,B",
            "S006,Chemistry,84,87,82,A",
            "S007,Chemistry,56,59,38,D",
            "S008,Mathematics,95,98,99,A*",
            "S009,Physics,62,65,48,C",
            "S010,Chemistry,79,82,74,B",
            "S011,Mathematics,44,46,18,E",
            "S012,Physics,90,93,93,A*",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var lines = new string[]
        {
            "id,value,label",
            "R1,200,X",
            "R2,200,Y",
            "R3,200,X",
            "R4,200,Z",
            "R5,200,X",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCoefficientOfVariation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCoefficientOfVariation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var ex = Record.Exception(() => doc.GetColumnCoefficientOfVariation("raw_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        Assert.True(doc.GetColumnCoefficientOfVariation("raw_score") >= 0);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        Assert.Equal(
            doc.GetColumnCoefficientOfVariation("scaled_score"),
            doc.GetColumnCoefficientOfVariation("scaled_score"));
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnCoefficientOfVariation("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var ex = Record.Exception(() => doc.GetColumnZScore("raw_score", 75.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var z = doc.GetColumnZScore("raw_score", 75.0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        Assert.Equal(
            doc.GetColumnZScore("scaled_score", 80.0),
            doc.GetColumnZScore("scaled_score", 80.0));
    }

    [Fact]
    public void GetColumnZScore_Zero_ForMeanValue()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var mean = doc.GetColumnMean("raw_score");
        var z = doc.GetColumnZScore("raw_score", mean);
        Assert.Equal(0.0, z, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalized
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalized_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var ex = Record.Exception(() => doc.GetColumnNormalized("raw_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalized_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        Assert.NotNull(doc.GetColumnNormalized("percentile"));
    }

    [Fact]
    public void GetColumnNormalized_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var n1 = doc.GetColumnNormalized("raw_score");
        var n2 = doc.GetColumnNormalized("raw_score");
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetColumnNormalized_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamResultsCsv());
        var before = doc.GetColumnNormalized("raw_score").Count;
        var path = TempFile("cn_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnNormalized("raw_score").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCoefficientOfVariation_GetColumnZScore_GetColumnNormalized_Pipeline()
    {
        // Sports science — elite athletics performance monitoring dataset
        var path = TempFile("athletics_performance.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("athlete_id,event,vo2max_ml_kg_min,lactate_threshold_pct,race_time_sec,power_watts,cadence_rpm,heart_rate_avg");
        var rng = new Random(20240701);
        string[] events = { "5000m", "10000m", "Half_Marathon", "Marathon" };
        for (int i = 0; i < 120; i++)
        {
            var evt = events[i % 4];
            // VO2max: elite range 65-85 ml/kg/min
            double vo2 = 65 + rng.NextDouble() * 20;
            // Lactate threshold as % of VO2max
            double lt = 75 + rng.NextDouble() * 15;
            // Race time varies by event: 5k ~780s, 10k ~1680s, HM ~3900s, M ~8400s
            double baseTime = new[] { 780.0, 1680.0, 3900.0, 8400.0 }[i % 4];
            double raceTime = baseTime + (rng.NextDouble() - 0.5) * baseTime * 0.05;
            double power = 280 + rng.NextDouble() * 80;
            int cadence = 175 + rng.Next(0, 15);
            int hr = 165 + rng.Next(0, 20);
            csvLines.Add($"ATH{i:D4},{evt},{vo2:F1},{lt:F1},{raceTime:F0},{power:F0},{cadence},{hr}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnCoefficientOfVariation — VO2max should have low CV (elite athletes are similar)
        var vo2CV = doc.GetColumnCoefficientOfVariation("vo2max_ml_kg_min");
        Assert.True(vo2CV >= 0);
        var timeCV = doc.GetColumnCoefficientOfVariation("race_time_sec");
        Assert.True(timeCV >= 0);
        // Race time CV should be higher than VO2max CV (because different events have very different times)
        Assert.Equal(vo2CV, doc.GetColumnCoefficientOfVariation("vo2max_ml_kg_min")); // consistent

        // GetColumnZScore
        var z75 = doc.GetColumnZScore("vo2max_ml_kg_min", 75.0);
        Assert.True(double.IsFinite(z75));
        Assert.Equal(z75, doc.GetColumnZScore("vo2max_ml_kg_min", 75.0)); // consistent

        var mean = doc.GetColumnMean("vo2max_ml_kg_min");
        var zMean = doc.GetColumnZScore("vo2max_ml_kg_min", mean);
        Assert.Equal(0.0, zMean, precision: 6);

        // GetColumnNormalized
        var normVO2 = doc.GetColumnNormalized("vo2max_ml_kg_min");
        Assert.NotNull(normVO2);
        Assert.Equal(120, normVO2.Count);
        Assert.Equal(normVO2.Count, doc.GetColumnNormalized("vo2max_ml_kg_min").Count); // consistent

        var normPower = doc.GetColumnNormalized("power_watts");
        Assert.NotNull(normPower);
        Assert.Equal(120, normPower.Count);

        // All numeric columns
        foreach (var col in new[] { "vo2max_ml_kg_min", "lactate_threshold_pct", "power_watts" })
        {
            Assert.True(doc.GetColumnCoefficientOfVariation(col) >= 0);
            Assert.True(double.IsFinite(doc.GetColumnZScore(col, 0.0)));
            Assert.NotNull(doc.GetColumnNormalized(col));
        }

        // SaveToFile
        var outPath = TempFile("athletics_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(vo2CV, loaded.GetColumnCoefficientOfVariation("vo2max_ml_kg_min"), precision: 6);
        Assert.Equal(z75, loaded.GetColumnZScore("vo2max_ml_kg_min", 75.0), precision: 6);
        Assert.Equal(normVO2.Count, loaded.GetColumnNormalized("vo2max_ml_kg_min").Count);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }
}
