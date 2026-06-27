// Tests for CsvDocument.GetColumnQuantile, GetColumnPercentile, GetColumnDecile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R248

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R248: Tests for CsvDocument.GetColumnQuantile, GetColumnPercentile, GetColumnDecile deeper.
/// GetColumnQuantile(columnName, q): returns the q-th quantile (0≤q≤1) of numeric column values.
/// GetColumnPercentile(columnName, p): returns the p-th percentile (0≤p≤100) of numeric column values.
/// GetColumnDecile(columnName, d): returns the d-th decile (1≤d≤9) of numeric column values.
/// Covers: GetColumnQuantile no-throw; GetColumnQuantile between min and max; GetColumnQuantile consistent;
/// GetColumnQuantile Q0=min, Q1=max;
/// GetColumnPercentile no-throw; GetColumnPercentile between min and max; GetColumnPercentile consistent;
/// GetColumnPercentile P0=min, P100=max;
/// GetColumnDecile no-throw; GetColumnDecile between min and max; GetColumnDecile consistent;
/// GetColumnDecile save-load;
/// dogfood CreateDoc→GetColumnQuantile→GetColumnPercentile→GetColumnDecile pipeline.
/// </summary>
public class CsvR248GetColumnQuantileAndPercentileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR248GetColumnQuantileAndPercentileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR248_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateExamCsv()
    {
        var path = TempFile("exam_results.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "student_id,subject,marks,grade,year",
            "S001,Mathematics,78,B,2024",
            "S002,Mathematics,92,A,2024",
            "S003,Mathematics,54,D,2024",
            "S004,Mathematics,67,C,2024",
            "S005,Mathematics,88,A,2024",
            "S006,Mathematics,41,E,2024",
            "S007,Mathematics,73,B,2024",
            "S008,Mathematics,95,A*,2024",
            "S009,Mathematics,61,C,2024",
            "S010,Mathematics,82,A,2024",
            "S011,Mathematics,49,E,2024",
            "S012,Mathematics,76,B,2024",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnQuantile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuantile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetColumnQuantile("marks", 0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuantile_Between_Min_And_Max()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var q = doc.GetColumnQuantile("marks", 0.5);
        var min = doc.GetColumnMin("marks");
        var max = doc.GetColumnMax("marks");
        Assert.True(q >= min && q <= max);
    }

    [Fact]
    public void GetColumnQuantile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnQuantile("marks", 0.75), doc.GetColumnQuantile("marks", 0.75));
    }

    [Fact]
    public void GetColumnQuantile_Q0_Equals_Min()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnMin("marks"), doc.GetColumnQuantile("marks", 0.0), precision: 6);
    }

    [Fact]
    public void GetColumnQuantile_Q1_Equals_Max()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnMax("marks"), doc.GetColumnQuantile("marks", 1.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetColumnPercentile("marks", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentile_Between_Min_And_Max()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var p = doc.GetColumnPercentile("marks", 50);
        var min = doc.GetColumnMin("marks");
        var max = doc.GetColumnMax("marks");
        Assert.True(p >= min && p <= max);
    }

    [Fact]
    public void GetColumnPercentile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnPercentile("marks", 90), doc.GetColumnPercentile("marks", 90));
    }

    [Fact]
    public void GetColumnPercentile_P0_Equals_Min()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnMin("marks"), doc.GetColumnPercentile("marks", 0), precision: 6);
    }

    [Fact]
    public void GetColumnPercentile_P100_Equals_Max()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnMax("marks"), doc.GetColumnPercentile("marks", 100), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnDecile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDecile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var ex = Record.Exception(() => doc.GetColumnDecile("marks", 5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDecile_Between_Min_And_Max()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var d = doc.GetColumnDecile("marks", 5);
        var min = doc.GetColumnMin("marks");
        var max = doc.GetColumnMax("marks");
        Assert.True(d >= min && d <= max);
    }

    [Fact]
    public void GetColumnDecile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        Assert.Equal(doc.GetColumnDecile("marks", 7), doc.GetColumnDecile("marks", 7));
    }

    [Fact]
    public void GetColumnDecile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateExamCsv());
        var before = doc.GetColumnDecile("marks", 8);
        var path = TempFile("decile_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnDecile("marks", 8), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnQuantile_GetColumnPercentile_GetColumnDecile_Pipeline()
    {
        // Pharmaceutical — drug trial pharmacokinetic data: Cmax, AUC, Tmax distributions
        var path = TempFile("pk_data.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("subject_id,dose_mg,cmax_ng_ml,auc_ng_ml_h,tmax_h,half_life_h,clearance_l_h");
        var rng = new Random(20250101);
        for (int i = 0; i < 150; i++)
        {
            double dose = (i % 4 + 1) * 50; // 50, 100, 150, 200 mg
            // PK parameters — log-normal distribution
            double cmax = Math.Exp(4.0 + rng.NextDouble() * 1.5) * (dose / 100);
            double auc = cmax * (3 + rng.NextDouble() * 4); // AUC = Cmax × MRT
            double tmax = 0.5 + rng.NextDouble() * 3.5;
            double halfLife = 3 + rng.NextDouble() * 9;
            double clearance = dose / (auc / 1000); // CL = Dose / AUC
            csvLines.Add($"SUB{i:D4},{dose:F0},{cmax:F1},{auc:F0},{tmax:F2},{halfLife:F1},{clearance:F2}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnQuantile — Cmax
        var q25 = doc.GetColumnQuantile("cmax_ng_ml", 0.25);
        var q50 = doc.GetColumnQuantile("cmax_ng_ml", 0.50);
        var q75 = doc.GetColumnQuantile("cmax_ng_ml", 0.75);
        Assert.True(q25 <= q50);
        Assert.True(q50 <= q75);
        Assert.Equal(q50, doc.GetColumnQuantile("cmax_ng_ml", 0.50)); // consistent

        // Q0=min, Q1=max for AUC
        Assert.Equal(doc.GetColumnMin("auc_ng_ml_h"), doc.GetColumnQuantile("auc_ng_ml_h", 0.0), precision: 6);
        Assert.Equal(doc.GetColumnMax("auc_ng_ml_h"), doc.GetColumnQuantile("auc_ng_ml_h", 1.0), precision: 6);

        // GetColumnPercentile — half-life (90th percentile = upper limit for PK)
        var p5 = doc.GetColumnPercentile("half_life_h", 5);
        var p95 = doc.GetColumnPercentile("half_life_h", 95);
        Assert.True(p5 <= p95);
        Assert.Equal(p95, doc.GetColumnPercentile("half_life_h", 95)); // consistent

        // P0=min, P100=max
        Assert.Equal(doc.GetColumnMin("tmax_h"), doc.GetColumnPercentile("tmax_h", 0), precision: 6);
        Assert.Equal(doc.GetColumnMax("tmax_h"), doc.GetColumnPercentile("tmax_h", 100), precision: 6);

        // GetColumnDecile — Cmax
        var d1 = doc.GetColumnDecile("cmax_ng_ml", 1);
        var d5 = doc.GetColumnDecile("cmax_ng_ml", 5);
        var d9 = doc.GetColumnDecile("cmax_ng_ml", 9);
        Assert.True(d1 <= d5);
        Assert.True(d5 <= d9);
        Assert.Equal(d5, doc.GetColumnDecile("cmax_ng_ml", 5)); // consistent

        // Decile monotonicity for AUC
        double prev = double.MinValue;
        for (int d = 1; d <= 9; d++)
        {
            double curr = doc.GetColumnDecile("auc_ng_ml_h", d);
            Assert.True(curr >= prev);
            prev = curr;
        }

        // SaveToFile
        var outPath = TempFile("pk_data_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(q50, loaded.GetColumnQuantile("cmax_ng_ml", 0.50), precision: 6);
        Assert.Equal(p95, loaded.GetColumnPercentile("half_life_h", 95), precision: 6);
        Assert.Equal(d9, loaded.GetColumnDecile("cmax_ng_ml", 9), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var meanCmax = doc.GetColumnMean("cmax_ng_ml");
        Assert.True(meanCmax > 0);
        var maxCmax = doc.GetColumnMax("cmax_ng_ml");
        Assert.True(maxCmax >= meanCmax);
    }
}
