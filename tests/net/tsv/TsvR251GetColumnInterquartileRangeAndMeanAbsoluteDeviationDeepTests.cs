// Tests for TsvDocument.GetColumnInterquartileRange, GetColumnMeanAbsoluteDeviation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R251

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R251: Tests for TsvDocument.GetColumnInterquartileRange, GetColumnMeanAbsoluteDeviation deeper.
/// GetColumnInterquartileRange(colName): returns Q3-Q1 for a numeric column (IQR).
/// GetColumnMeanAbsoluteDeviation(colName): returns mean(|x - mean(x)|) for a numeric column.
/// Covers: GetColumnInterquartileRange no-throw; GetColumnInterquartileRange non-negative;
/// GetColumnInterquartileRange zero for constant; GetColumnInterquartileRange consistent;
/// GetColumnInterquartileRange save-load;
/// GetColumnMeanAbsoluteDeviation no-throw; GetColumnMeanAbsoluteDeviation non-negative;
/// GetColumnMeanAbsoluteDeviation zero for constant; GetColumnMeanAbsoluteDeviation consistent;
/// GetColumnMeanAbsoluteDeviation save-load;
/// dogfood CreateDoc→GetColumnInterquartileRange→GetColumnMeanAbsoluteDeviation pipeline.
/// </summary>
public class TsvR251GetColumnInterquartileRangeAndMeanAbsoluteDeviationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR251GetColumnInterquartileRangeAndMeanAbsoluteDeviationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR251_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("patient_id\tage\tbmi\tsystolic_bp\tdiastolic_bp");
        var rng = new Random(20240601);
        for (int i = 0; i < 80; i++)
            sb.AppendLine($"P{i:D4}\t{(18 + rng.Next(62))}\t{(18.5 + rng.NextDouble() * 22.0):F1}\t{(100 + rng.Next(80))}\t{(60 + rng.Next(40))}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue\tgroup");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t100\tX");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnInterquartileRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnInterquartileRange_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnInterquartileRange("age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnInterquartileRange_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnInterquartileRange("age") >= 0.0);
    }

    [Fact]
    public void GetColumnInterquartileRange_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnInterquartileRange("value"), precision: 6);
    }

    [Fact]
    public void GetColumnInterquartileRange_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnInterquartileRange("bmi");
        var v2 = doc.GetColumnInterquartileRange("bmi");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnInterquartileRange_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnInterquartileRange("systolic_bp");
        var path = TempFile("iqr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnInterquartileRange("systolic_bp"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnMeanAbsoluteDeviation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMeanAbsoluteDeviation("age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnMeanAbsoluteDeviation("age") >= 0.0);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnMeanAbsoluteDeviation("value"), precision: 6);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnMeanAbsoluteDeviation("diastolic_bp");
        var v2 = doc.GetColumnMeanAbsoluteDeviation("diastolic_bp");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnMeanAbsoluteDeviation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMeanAbsoluteDeviation("bmi");
        var path = TempFile("mad_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMeanAbsoluteDeviation("bmi"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnIQR_GetColumnMAD_Pipeline()
    {
        // Clinical epidemiology — UK Biobank metabolomics cohort baseline characteristics
        var path = TempFile("ukb_metabolomics_baseline.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("eid\tage_recruited\tbmi_kgm2\twaist_cm\thip_cm\tsystolic_mmhg\tdiastolic_mmhg\ttotal_chol_mmol\tldl_mmol\thdl_mmol\ttriglycerides_mmol\tglucose_mmol\thba1c_mmol_mol");
        var rng = new Random(20240101);
        string[] ethnicities = { "White_British", "South_Asian", "Black_African", "Chinese", "Mixed" };
        for (int i = 0; i < 200; i++)
        {
            double age = 40 + rng.NextDouble() * 30;
            double bmi = 22 + rng.NextDouble() * 18;
            double waist = 75 + rng.NextDouble() * 45;
            double hip = 90 + rng.NextDouble() * 30;
            double sbp = 100 + rng.NextDouble() * 80;
            double dbp = 60 + rng.NextDouble() * 40;
            double tc = 3.5 + rng.NextDouble() * 4.0;
            double ldl = 1.5 + rng.NextDouble() * 3.0;
            double hdl = 0.8 + rng.NextDouble() * 2.2;
            double trig = 0.5 + rng.NextDouble() * 4.0;
            double gluc = 4.0 + rng.NextDouble() * 8.0;
            double hba1c = 30 + rng.NextDouble() * 60;
            sb.AppendLine($"{1000000 + i}\t{age:F1}\t{bmi:F1}\t{waist:F1}\t{hip:F1}\t{sbp:F0}\t{dbp:F0}\t{tc:F2}\t{ldl:F2}\t{hdl:F2}\t{trig:F2}\t{gluc:F2}\t{hba1c:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(13, doc.ColumnCount);

        // GetColumnInterquartileRange
        var iqrAge = doc.GetColumnInterquartileRange("age_recruited");
        Assert.True(iqrAge >= 0.0);
        Assert.Equal(iqrAge, doc.GetColumnInterquartileRange("age_recruited")); // consistent

        var iqrBmi = doc.GetColumnInterquartileRange("bmi_kgm2");
        Assert.True(iqrBmi >= 0.0);

        var iqrSbp = doc.GetColumnInterquartileRange("systolic_mmhg");
        Assert.True(iqrSbp >= 0.0);

        var iqrLdl = doc.GetColumnInterquartileRange("ldl_mmol");
        Assert.True(iqrLdl >= 0.0);

        var iqrHba1c = doc.GetColumnInterquartileRange("hba1c_mmol_mol");
        Assert.True(iqrHba1c >= 0.0);

        // GetColumnMeanAbsoluteDeviation
        var madAge = doc.GetColumnMeanAbsoluteDeviation("age_recruited");
        Assert.True(madAge >= 0.0);
        Assert.Equal(madAge, doc.GetColumnMeanAbsoluteDeviation("age_recruited")); // consistent

        var madBmi = doc.GetColumnMeanAbsoluteDeviation("bmi_kgm2");
        Assert.True(madBmi >= 0.0);

        var madTrig = doc.GetColumnMeanAbsoluteDeviation("triglycerides_mmol");
        Assert.True(madTrig >= 0.0);

        var madGluc = doc.GetColumnMeanAbsoluteDeviation("glucose_mmol");
        Assert.True(madGluc >= 0.0);

        // Basic stats cross-check
        Assert.True(doc.GetColumnMin("age_recruited") <= doc.GetColumnMax("age_recruited"));
        Assert.True(doc.GetColumnMean("bmi_kgm2") > 0.0);
        Assert.True(doc.GetColumnStdDev("systolic_mmhg") >= 0.0);

        // IQR <= range
        var rangeAge = doc.GetColumnMax("age_recruited") - doc.GetColumnMin("age_recruited");
        Assert.True(iqrAge <= rangeAge + 1e-9);

        // MAD <= StdDev (MAD ≤ std for any distribution)
        var stdAge = doc.GetColumnStdDev("age_recruited");
        Assert.True(madAge <= stdAge + 1e-9);

        // Quantiles
        var q25 = doc.GetColumnQuantile("ldl_mmol", 0.25);
        var q75 = doc.GetColumnQuantile("ldl_mmol", 0.75);
        Assert.True(q25 <= q75);
        Assert.Equal(q75 - q25, iqrLdl, precision: 6);

        // SaveToFile
        var outPath = TempFile("ukb_metabolomics_baseline_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(iqrAge, loaded.GetColumnInterquartileRange("age_recruited"), precision: 8);
        Assert.Equal(iqrBmi, loaded.GetColumnInterquartileRange("bmi_kgm2"), precision: 8);
        Assert.Equal(madAge, loaded.GetColumnMeanAbsoluteDeviation("age_recruited"), precision: 8);
        Assert.Equal(madBmi, loaded.GetColumnMeanAbsoluteDeviation("bmi_kgm2"), precision: 8);

        // Constant column
        var path2 = TempFile("constant_metabolomics.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("subject\thdl_fixed\ttriglycerides");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"S{i:D3}\t1.2\t{(0.5 + i * 0.05):F2}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnInterquartileRange("hdl_fixed"), precision: 6);
        Assert.Equal(0.0, doc2.GetColumnMeanAbsoluteDeviation("hdl_fixed"), precision: 6);
        Assert.True(doc2.GetColumnInterquartileRange("triglycerides") > 0.0);
        Assert.True(doc2.GetColumnMeanAbsoluteDeviation("triglycerides") > 0.0);
    }
}
