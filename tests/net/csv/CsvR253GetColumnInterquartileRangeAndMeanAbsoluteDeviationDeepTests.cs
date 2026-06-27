// Tests for CsvDocument.GetColumnInterquartileRange, GetColumnMeanAbsoluteDeviation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R253

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R253: Tests for CsvDocument.GetColumnInterquartileRange, GetColumnMeanAbsoluteDeviation deeper.
/// GetColumnInterquartileRange(colName): returns Q3-Q1 for a numeric column.
/// GetColumnMeanAbsoluteDeviation(colName): returns mean(|x - mean(x)|) for a numeric column.
/// Covers: GetColumnInterquartileRange no-throw; GetColumnInterquartileRange non-negative;
/// GetColumnInterquartileRange zero for constant; GetColumnInterquartileRange consistent;
/// GetColumnInterquartileRange save-load;
/// GetColumnMeanAbsoluteDeviation no-throw; GetColumnMeanAbsoluteDeviation non-negative;
/// GetColumnMeanAbsoluteDeviation zero for constant; GetColumnMeanAbsoluteDeviation consistent;
/// GetColumnMeanAbsoluteDeviation save-load;
/// dogfood CreateDoc→GetColumnIQR→GetColumnMAD pipeline.
/// </summary>
public class CsvR253GetColumnInterquartileRangeAndMeanAbsoluteDeviationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR253GetColumnInterquartileRangeAndMeanAbsoluteDeviationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR253_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("subject_id,age,weight_kg,height_cm,egfr,creatinine_umol");
        var rng = new Random(20240615);
        for (int i = 0; i < 80; i++)
            sb.AppendLine($"SUB{i:D4},{(20 + rng.Next(65))},{(50.0 + rng.NextDouble() * 80.0):F1},{(155.0 + rng.NextDouble() * 40.0):F1},{(30 + rng.NextDouble() * 90):F1},{(50 + rng.NextDouble() * 200):F0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,score,category");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},75,A");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnInterquartileRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnInterquartileRange_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnInterquartileRange("age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnInterquartileRange_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnInterquartileRange("age") >= 0.0);
    }

    [Fact]
    public void GetColumnInterquartileRange_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnInterquartileRange("score"), precision: 6);
    }

    [Fact]
    public void GetColumnInterquartileRange_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnInterquartileRange("weight_kg");
        var v2 = doc.GetColumnInterquartileRange("weight_kg");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnInterquartileRange_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnInterquartileRange("egfr");
        var path = TempFile("iqr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnInterquartileRange("egfr"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnMeanAbsoluteDeviation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnMeanAbsoluteDeviation("age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnMeanAbsoluteDeviation("age") >= 0.0);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnMeanAbsoluteDeviation("score"), precision: 6);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnMeanAbsoluteDeviation("creatinine_umol");
        var v2 = doc.GetColumnMeanAbsoluteDeviation("creatinine_umol");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnMeanAbsoluteDeviation("height_cm");
        var path = TempFile("mad_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMeanAbsoluteDeviation("height_cm"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnIQR_GetColumnMAD_Pipeline()
    {
        // Clinical pharmacology — multicentre Phase II dose-finding study
        // Pharmacokinetic parameters for novel JAK3 inhibitor (tofetinib analogue) in RA patients
        var path = TempFile("phase2_pk_study.csv");
        var sb = new StringBuilder();
        sb.AppendLine("patient_id,centre,dose_mg,cmax_ng_ml,tmax_h,auc0t_ng_h_ml,auc0inf_ng_h_ml,t_half_h,cl_l_h,vd_l,f_percent,creatinine_clearance_ml_min,alt_iu_l,ast_iu_l");
        var rng = new Random(20240315);
        string[] centres = { "UCL", "Edinburgh", "Manchester", "Birmingham", "Bristol" };
        double[] doses = { 5.0, 10.0, 20.0, 40.0 };
        for (int i = 0; i < 160; i++)
        {
            var centre = centres[i % centres.Length];
            var dose = doses[i % doses.Length];
            double cmax = dose * (8 + rng.NextDouble() * 6) + rng.NextDouble() * 20;
            double tmax = 1.5 + rng.NextDouble() * 3.0;
            double aucT = cmax * (8 + rng.NextDouble() * 4);
            double aucInf = aucT * (1.05 + rng.NextDouble() * 0.15);
            double tHalf = 4 + rng.NextDouble() * 8;
            double cl = dose / aucInf * 1000;
            double vd = cl * tHalf / 0.693;
            double f = 55 + rng.NextDouble() * 35;
            double crcl = 60 + rng.NextDouble() * 60;
            double alt = 15 + rng.NextDouble() * 45;
            double ast = 12 + rng.NextDouble() * 35;
            sb.AppendLine($"PT{1000 + i},{centre},{dose:F0},{cmax:F2},{tmax:F2},{aucT:F1},{aucInf:F1},{tHalf:F2},{cl:F3},{vd:F1},{f:F1},{crcl:F1},{alt:F1},{ast:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(160, doc.RowCount);
        Assert.Equal(14, doc.ColumnCount);

        // GetColumnInterquartileRange
        var iqrCmax = doc.GetColumnInterquartileRange("cmax_ng_ml");
        Assert.True(iqrCmax >= 0.0);
        Assert.Equal(iqrCmax, doc.GetColumnInterquartileRange("cmax_ng_ml")); // consistent

        var iqrAuc = doc.GetColumnInterquartileRange("auc0t_ng_h_ml");
        Assert.True(iqrAuc >= 0.0);

        var iqrTHalf = doc.GetColumnInterquartileRange("t_half_h");
        Assert.True(iqrTHalf >= 0.0);

        var iqrCl = doc.GetColumnInterquartileRange("cl_l_h");
        Assert.True(iqrCl >= 0.0);

        var iqrF = doc.GetColumnInterquartileRange("f_percent");
        Assert.True(iqrF >= 0.0);

        // GetColumnMeanAbsoluteDeviation
        var madCmax = doc.GetColumnMeanAbsoluteDeviation("cmax_ng_ml");
        Assert.True(madCmax >= 0.0);
        Assert.Equal(madCmax, doc.GetColumnMeanAbsoluteDeviation("cmax_ng_ml")); // consistent

        var madAuc = doc.GetColumnMeanAbsoluteDeviation("auc0t_ng_h_ml");
        Assert.True(madAuc >= 0.0);

        var madTmax = doc.GetColumnMeanAbsoluteDeviation("tmax_h");
        Assert.True(madTmax >= 0.0);

        var madAlt = doc.GetColumnMeanAbsoluteDeviation("alt_iu_l");
        Assert.True(madAlt >= 0.0);

        // IQR ≤ full range
        var rangeCmax = doc.GetColumnMax("cmax_ng_ml") - doc.GetColumnMin("cmax_ng_ml");
        Assert.True(iqrCmax <= rangeCmax + 1e-9);

        // MAD ≤ StdDev
        var stdCmax = doc.GetColumnStdDev("cmax_ng_ml");
        Assert.True(madCmax <= stdCmax + 1e-9);

        // Quantile cross-check
        var q25 = doc.GetColumnQuantile("auc0t_ng_h_ml", 0.25);
        var q75 = doc.GetColumnQuantile("auc0t_ng_h_ml", 0.75);
        Assert.True(q25 <= q75);
        Assert.Equal(q75 - q25, iqrAuc, precision: 6);

        // Basic stats
        Assert.True(doc.GetColumnMin("dose_mg") <= doc.GetColumnMax("dose_mg"));
        Assert.True(doc.GetColumnMean("creatinine_clearance_ml_min") > 0.0);

        // SaveToFile
        var outPath = TempFile("phase2_pk_study_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(iqrCmax, loaded.GetColumnInterquartileRange("cmax_ng_ml"), precision: 8);
        Assert.Equal(iqrTHalf, loaded.GetColumnInterquartileRange("t_half_h"), precision: 8);
        Assert.Equal(madCmax, loaded.GetColumnMeanAbsoluteDeviation("cmax_ng_ml"), precision: 8);
        Assert.Equal(madAuc, loaded.GetColumnMeanAbsoluteDeviation("auc0t_ng_h_ml"), precision: 8);

        // Constant column
        var path2 = TempFile("constant_pk.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("patient,bioavailability_fixed,clearance");
        for (int i = 0; i < 40; i++)
            sb2.AppendLine($"P{i:D3},0.65,{(10.0 + i * 0.2):F2}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnInterquartileRange("bioavailability_fixed"), precision: 6);
        Assert.Equal(0.0, doc2.GetColumnMeanAbsoluteDeviation("bioavailability_fixed"), precision: 6);
        Assert.True(doc2.GetColumnInterquartileRange("clearance") > 0.0);
        Assert.True(doc2.GetColumnMeanAbsoluteDeviation("clearance") > 0.0);
    }
}
