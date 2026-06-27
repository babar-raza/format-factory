// Tests for CsvDocument.GetColumnCoefficientOfVariation, GetColumnRelativeRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R250

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R250: Tests for CsvDocument.GetColumnCoefficientOfVariation, GetColumnRelativeRange deeper.
/// GetColumnCoefficientOfVariation(colName): returns std/mean for a numeric column (CV = sigma/mu).
/// GetColumnRelativeRange(colName): returns (max-min)/mean for a numeric column.
/// Covers: GetColumnCoefficientOfVariation no-throw; GetColumnCoefficientOfVariation non-negative;
/// GetColumnCoefficientOfVariation zero for constant; GetColumnCoefficientOfVariation consistent;
/// GetColumnCoefficientOfVariation save-load;
/// GetColumnRelativeRange no-throw; GetColumnRelativeRange non-negative;
/// GetColumnRelativeRange zero for constant; GetColumnRelativeRange consistent;
/// GetColumnRelativeRange save-load;
/// dogfood CreateDoc→GetColumnCoefficientOfVariation→GetColumnRelativeRange pipeline.
/// </summary>
public class CsvR250GetColumnCoefficientOfVariationAndRelativeRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR250GetColumnCoefficientOfVariationAndRelativeRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR250_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("loan_id,principal,interest_rate,term_months,monthly_payment");
        var rng = new Random(77);
        for (int i = 0; i < 60; i++)
        {
            double principal = 5000 + rng.NextDouble() * 45000;
            double rate = 3.5 + rng.NextDouble() * 12.5;
            int term = (rng.Next(4) + 1) * 12;
            double payment = principal * (rate / 1200) / (1 - Math.Pow(1 + rate / 1200, -term));
            sb.AppendLine($"LN{i:D4},{principal:F2},{rate:F3},{term},{payment:F2}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,score,label");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i},75.0,pass");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCoefficientOfVariation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCoefficientOfVariation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCoefficientOfVariation("principal"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnCoefficientOfVariation("principal") >= 0.0);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnCoefficientOfVariation("score"), precision: 6);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnCoefficientOfVariation("interest_rate");
        var v2 = doc.GetColumnCoefficientOfVariation("interest_rate");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCoefficientOfVariation("monthly_payment");
        var path = TempFile("cv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCoefficientOfVariation("monthly_payment"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnRelativeRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRelativeRange_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRelativeRange("principal"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRelativeRange_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnRelativeRange("principal") >= 0.0);
    }

    [Fact]
    public void GetColumnRelativeRange_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnRelativeRange("score"), precision: 6);
    }

    [Fact]
    public void GetColumnRelativeRange_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnRelativeRange("interest_rate");
        var v2 = doc.GetColumnRelativeRange("interest_rate");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnRelativeRange_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRelativeRange("monthly_payment");
        var path = TempFile("rr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRelativeRange("monthly_payment"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCoefficientOfVariation_GetColumnRelativeRange_Pipeline()
    {
        // Clinical trials — phase III randomised controlled trial pharmacokinetic data
        var path = TempFile("pk_trial_data.csv");
        var sb = new StringBuilder();
        sb.AppendLine("subject_id,arm,dose_mg,cmax_ng_ml,tmax_hours,auc_0_24,auc_0_inf,t_half_hours,cl_l_hr,vd_litres");
        var rng = new Random(20240801);
        string[] arms = { "10mg_QD", "20mg_QD", "40mg_QD", "Placebo" };
        double[] doses = { 10, 20, 40, 0 };
        for (int i = 0; i < 150; i++)
        {
            int armIdx = i % 4;
            double dose = doses[armIdx];
            double cmax = dose > 0 ? dose * 8 + rng.NextDouble() * dose * 4 : rng.NextDouble() * 5;
            double tmax = 1.5 + rng.NextDouble() * 2.5;
            double auc24 = dose > 0 ? dose * 30 + rng.NextDouble() * dose * 15 : rng.NextDouble() * 20;
            double aucInf = auc24 * (1 + rng.NextDouble() * 0.3);
            double thalf = 6 + rng.NextDouble() * 8;
            double cl = dose > 0 ? dose / aucInf * 1000 : 0;
            double vd = cl * thalf / 0.693;
            sb.AppendLine($"SUB{i + 1:D3},{arms[armIdx]},{dose:F1},{cmax:F2},{tmax:F2},{auc24:F1},{aucInf:F1},{thalf:F2},{cl:F3},{vd:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // GetColumnCoefficientOfVariation
        var cvCmax = doc.GetColumnCoefficientOfVariation("cmax_ng_ml");
        Assert.True(cvCmax >= 0.0);
        Assert.Equal(cvCmax, doc.GetColumnCoefficientOfVariation("cmax_ng_ml")); // consistent

        var cvAuc = doc.GetColumnCoefficientOfVariation("auc_0_24");
        Assert.True(cvAuc >= 0.0);

        var cvTmax = doc.GetColumnCoefficientOfVariation("tmax_hours");
        Assert.True(cvTmax >= 0.0);

        var cvThalf = doc.GetColumnCoefficientOfVariation("t_half_hours");
        Assert.True(cvThalf >= 0.0);

        // GetColumnRelativeRange
        var rrCmax = doc.GetColumnRelativeRange("cmax_ng_ml");
        Assert.True(rrCmax >= 0.0);
        Assert.Equal(rrCmax, doc.GetColumnRelativeRange("cmax_ng_ml")); // consistent

        var rrAuc = doc.GetColumnRelativeRange("auc_0_inf");
        Assert.True(rrAuc >= 0.0);

        var rrVd = doc.GetColumnRelativeRange("vd_litres");
        Assert.True(rrVd >= 0.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("cmax_ng_ml") >= 0.0);
        Assert.True(doc.GetColumnMax("cmax_ng_ml") > doc.GetColumnMin("cmax_ng_ml"));
        Assert.True(doc.GetColumnMean("t_half_hours") > 0.0);
        Assert.True(doc.GetColumnStdDev("auc_0_24") >= 0.0);

        // Quantile
        var q25 = doc.GetColumnQuantile("cmax_ng_ml", 0.25);
        var q75 = doc.GetColumnQuantile("cmax_ng_ml", 0.75);
        Assert.True(q25 <= q75);

        // SaveToFile
        var outPath = TempFile("pk_trial_data_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(cvCmax, loaded.GetColumnCoefficientOfVariation("cmax_ng_ml"), precision: 8);
        Assert.Equal(rrCmax, loaded.GetColumnRelativeRange("cmax_ng_ml"), precision: 8);

        // Constant column test
        var path2 = TempFile("constant_dose.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("subject,fixed_dose,cmax");
        for (int i = 0; i < 30; i++)
            sb2.AppendLine($"S{i:D2},20.0,{(150 + i * 2.5):F1}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnCoefficientOfVariation("fixed_dose"), precision: 6);
        Assert.Equal(0.0, doc2.GetColumnRelativeRange("fixed_dose"), precision: 6);
        Assert.True(doc2.GetColumnCoefficientOfVariation("cmax") > 0.0);
    }
}
