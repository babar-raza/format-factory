// Tests for TsvDocument.GetColumnCoefficientOfVariation, GetColumnZScore, GetColumnNormalized deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R243

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R243: Tests for TsvDocument.GetColumnCoefficientOfVariation, GetColumnZScore, GetColumnNormalized deeper.
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
public class TsvR243GetColumnCoefficientOfVariationAndZScoreDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR243GetColumnCoefficientOfVariationAndZScoreDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR243_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateManufacturingTsv()
    {
        var path = TempFile("manufacturing.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "batch_id\tline\ttemperature_c\tpressure_bar\tcycle_time_sec\tdefect_count",
            "B001\tLine_A\t185.2\t3.4\t42\t0",
            "B002\tLine_A\t186.1\t3.5\t41\t1",
            "B003\tLine_B\t184.8\t3.3\t43\t0",
            "B004\tLine_B\t185.9\t3.6\t40\t0",
            "B005\tLine_A\t187.2\t3.4\t44\t2",
            "B006\tLine_C\t184.5\t3.2\t45\t0",
            "B007\tLine_C\t185.0\t3.5\t42\t1",
            "B008\tLine_A\t186.8\t3.7\t41\t0",
            "B009\tLine_B\t185.4\t3.4\t43\t0",
            "B010\tLine_C\t184.9\t3.3\t44\t3",
            "B011\tLine_A\t186.2\t3.5\t42\t0",
            "B012\tLine_B\t185.7\t3.6\t41\t1",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var lines = new string[]
        {
            "id\tvalue\tlabel",
            "R1\t50\tA",
            "R2\t50\tB",
            "R3\t50\tA",
            "R4\t50\tC",
            "R5\t50\tB",
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
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var ex = Record.Exception(() => doc.GetColumnCoefficientOfVariation("temperature_c"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        Assert.True(doc.GetColumnCoefficientOfVariation("temperature_c") >= 0);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        Assert.Equal(
            doc.GetColumnCoefficientOfVariation("pressure_bar"),
            doc.GetColumnCoefficientOfVariation("pressure_bar"));
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnCoefficientOfVariation("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var ex = Record.Exception(() => doc.GetColumnZScore("temperature_c", 185.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var z = doc.GetColumnZScore("temperature_c", 185.0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        Assert.Equal(
            doc.GetColumnZScore("pressure_bar", 3.5),
            doc.GetColumnZScore("pressure_bar", 3.5));
    }

    [Fact]
    public void GetColumnZScore_Zero_ForMeanValue()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var mean = doc.GetColumnMean("temperature_c");
        var z = doc.GetColumnZScore("temperature_c", mean);
        Assert.Equal(0.0, z, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalized
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalized_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var ex = Record.Exception(() => doc.GetColumnNormalized("temperature_c"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalized_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        Assert.NotNull(doc.GetColumnNormalized("cycle_time_sec"));
    }

    [Fact]
    public void GetColumnNormalized_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var n1 = doc.GetColumnNormalized("pressure_bar");
        var n2 = doc.GetColumnNormalized("pressure_bar");
        Assert.Equal(n1.Count, n2.Count);
    }

    [Fact]
    public void GetColumnNormalized_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateManufacturingTsv());
        var before = doc.GetColumnNormalized("temperature_c").Count;
        var path = TempFile("cn_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnNormalized("temperature_c").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCoefficientOfVariation_GetColumnZScore_GetColumnNormalized_Pipeline()
    {
        // Pharmaceutical manufacturing — tablet dissolution testing QC data
        var path = TempFile("dissolution_testing.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("test_id\tbatch\tvessel\ttime_min\tdissolved_pct\tph\ttemperature_c\tapparatus");
        var rng = new Random(20240501);
        string[] batches = { "BAT-2024-001", "BAT-2024-002", "BAT-2024-003" };
        string[] apparatus = { "USP_I_Basket", "USP_II_Paddle" };
        for (int i = 0; i < 120; i++)
        {
            var batch = batches[i % 3];
            int vessel = (i % 6) + 1;
            int time = (i % 6 + 1) * 10; // 10, 20, 30, 40, 50, 60 min timepoints
            // Dissolution % increases with time, with slight between-vessel variation
            double diss = Math.Min(100.0, 15.0 * (time / 10.0) + rng.NextDouble() * 5 - 2);
            double ph = 6.8 + rng.NextDouble() * 0.4 - 0.2;
            double temp = 37.0 + rng.NextDouble() * 0.5 - 0.25;
            var app = apparatus[i % 2];
            lines.Add($"T{i:D4}\t{batch}\t{vessel}\t{time}\t{diss:F1}\t{ph:F2}\t{temp:F2}\t{app}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnCoefficientOfVariation — low CV for tightly controlled temperature
        var tempCV = doc.GetColumnCoefficientOfVariation("temperature_c");
        Assert.True(tempCV >= 0);
        var dissCV = doc.GetColumnCoefficientOfVariation("dissolved_pct");
        Assert.True(dissCV >= 0);
        Assert.Equal(tempCV, doc.GetColumnCoefficientOfVariation("temperature_c")); // consistent

        // GetColumnZScore — z-score for specific dissolution value
        var z85 = doc.GetColumnZScore("dissolved_pct", 85.0);
        Assert.True(double.IsFinite(z85));
        Assert.Equal(z85, doc.GetColumnZScore("dissolved_pct", 85.0)); // consistent

        // Mean should have z-score of 0
        var mean = doc.GetColumnMean("dissolved_pct");
        var zMean = doc.GetColumnZScore("dissolved_pct", mean);
        Assert.Equal(0.0, zMean, precision: 6);

        // GetColumnNormalized
        var normDiss = doc.GetColumnNormalized("dissolved_pct");
        Assert.NotNull(normDiss);
        Assert.Equal(120, normDiss.Count);
        Assert.Equal(normDiss.Count, doc.GetColumnNormalized("dissolved_pct").Count); // consistent

        var normTemp = doc.GetColumnNormalized("temperature_c");
        Assert.NotNull(normTemp);
        Assert.Equal(120, normTemp.Count);

        // SaveToFile
        var outPath = TempFile("dissolution_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(tempCV, loaded.GetColumnCoefficientOfVariation("temperature_c"), precision: 6);
        Assert.Equal(z85, loaded.GetColumnZScore("dissolved_pct", 85.0), precision: 6);
        Assert.Equal(normDiss.Count, loaded.GetColumnNormalized("dissolved_pct").Count);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional column stats
        var minDiss = doc.GetColumnMin("dissolved_pct");
        var maxDiss = doc.GetColumnMax("dissolved_pct");
        Assert.True(minDiss >= 0);
        Assert.True(maxDiss <= 100.0);
    }
}
