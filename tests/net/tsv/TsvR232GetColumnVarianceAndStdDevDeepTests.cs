// Tests for TsvDocument.GetColumnVariance, GetColumnStdDev, GetCoefficientOfVariation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R232

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R232: Tests for TsvDocument.GetColumnVariance, GetColumnStdDev, GetCoefficientOfVariation deeper.
/// GetColumnVariance(columnName): returns the variance of numeric values in the column.
/// GetColumnStdDev(columnName): returns the standard deviation of numeric values in the column.
/// GetCoefficientOfVariation(columnName): returns the CV (stdDev/mean * 100) for the column.
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance consistent;
/// GetColumnVariance zero for uniform; GetColumnVariance save-load;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev consistent;
/// GetColumnStdDev zero for uniform; GetColumnStdDev save-load;
/// GetCoefficientOfVariation no-throw; GetCoefficientOfVariation non-negative; GetCoefficientOfVariation consistent;
/// GetCoefficientOfVariation save-load;
/// dogfood CreateDoc→GetColumnVariance→GetColumnStdDev→GetCoefficientOfVariation→SaveToFile pipeline.
/// </summary>
public class TsvR232GetColumnVarianceAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR232GetColumnVarianceAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR232_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductionTsv()
    {
        var path = TempFile("production.tsv");
        File.WriteAllText(path,
            "plant\tshift\tunits_produced\tdefect_rate\tdowntime_min\tefficiency_pct\n" +
            "Plant_A\tMorning\t1850\t0.012\t15\t94.2\n" +
            "Plant_A\tAfternoon\t1920\t0.008\t8\t96.8\n" +
            "Plant_A\tNight\t1680\t0.021\t42\t88.5\n" +
            "Plant_B\tMorning\t2140\t0.006\t5\t98.2\n" +
            "Plant_B\tAfternoon\t2080\t0.009\t12\t97.1\n" +
            "Plant_B\tNight\t1950\t0.015\t28\t92.4\n" +
            "Plant_C\tMorning\t1620\t0.025\t55\t85.6\n" +
            "Plant_C\tAfternoon\t1780\t0.018\t32\t89.3\n" +
            "Plant_C\tNight\t1550\t0.032\t68\t82.1\n" +
            "Plant_D\tMorning\t2280\t0.004\t3\t99.1\n" +
            "Plant_D\tAfternoon\t2210\t0.007\t9\t97.8\n" +
            "Plant_D\tNight\t2050\t0.011\t18\t95.5\n");
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        File.WriteAllText(path,
            "id\tvalue\n" +
            "1\t100\n2\t100\n3\t100\n4\t100\n5\t100\n6\t100\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("units_produced"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.True(doc.GetColumnVariance("units_produced") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.Equal(doc.GetColumnVariance("defect_rate"), doc.GetColumnVariance("defect_rate"));
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnVariance("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var before = doc.GetColumnVariance("efficiency_pct");
        var path = TempFile("var_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnVariance("efficiency_pct"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("units_produced"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.True(doc.GetColumnStdDev("downtime_min") >= 0.0);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.Equal(doc.GetColumnStdDev("efficiency_pct"), doc.GetColumnStdDev("efficiency_pct"));
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_Leq_Variance_When_Variance_Gte_One()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var variance = doc.GetColumnVariance("units_produced");
        var stdDev = doc.GetColumnStdDev("units_produced");
        // For variance >= 1, stdDev = sqrt(variance) <= variance
        if (variance >= 1.0)
            Assert.True(stdDev <= variance);
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var before = doc.GetColumnStdDev("downtime_min");
        var path = TempFile("std_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnStdDev("downtime_min"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetCoefficientOfVariation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCoefficientOfVariation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var ex = Record.Exception(() => doc.GetCoefficientOfVariation("units_produced"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCoefficientOfVariation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.True(doc.GetCoefficientOfVariation("defect_rate") >= 0.0);
    }

    [Fact]
    public void GetCoefficientOfVariation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        Assert.Equal(doc.GetCoefficientOfVariation("efficiency_pct"), doc.GetCoefficientOfVariation("efficiency_pct"));
    }

    [Fact]
    public void GetCoefficientOfVariation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateProductionTsv());
        var before = doc.GetCoefficientOfVariation("units_produced");
        var path = TempFile("cv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCoefficientOfVariation("units_produced"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnStdDev_GetCoefficientOfVariation_SaveToFile_Pipeline()
    {
        // Pharmaceutical clinical trial — biomarker variability analysis
        var path = TempFile("dogfood_biomarker.tsv");
        File.WriteAllText(path,
            "patient_id\tage\tbaseline_ldl\tpost_treatment_ldl\tldl_reduction\thdl_increase\thba1c_baseline\thba1c_endpoint\n" +
            "P001\t52\t185.4\t124.2\t61.2\t8.5\t7.8\t6.9\n" +
            "P002\t61\t210.8\t138.5\t72.3\t11.2\t8.4\t7.1\n" +
            "P003\t45\t168.2\t118.6\t49.6\t6.8\t7.2\t6.5\n" +
            "P004\t58\t225.6\t148.3\t77.3\t14.5\t9.1\t7.8\n" +
            "P005\t49\t172.5\t122.8\t49.7\t7.9\t7.5\t6.7\n" +
            "P006\t67\t241.8\t158.4\t83.4\t16.2\t9.4\t8.0\n" +
            "P007\t54\t195.3\t132.6\t62.7\t9.8\t8.0\t7.0\n" +
            "P008\t43\t162.8\t115.2\t47.6\t5.9\t7.0\t6.3\n" +
            "P009\t72\t254.2\t165.8\t88.4\t18.5\t9.8\t8.3\n" +
            "P010\t56\t198.5\t136.2\t62.3\t10.4\t8.2\t7.2\n" +
            "P011\t48\t175.8\t124.5\t51.3\t8.1\t7.6\t6.8\n" +
            "P012\t63\t228.4\t152.6\t75.8\t13.8\t9.0\t7.7\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetColumnVariance — LDL reduction spread
        var varLdl = doc.GetColumnVariance("ldl_reduction");
        Assert.True(varLdl >= 0.0);
        Assert.Equal(varLdl, doc.GetColumnVariance("ldl_reduction")); // consistent

        var varAge = doc.GetColumnVariance("age");
        Assert.True(varAge >= 0.0);

        // GetColumnStdDev — HbA1c endpoint spread
        var stdHba1c = doc.GetColumnStdDev("hba1c_endpoint");
        Assert.True(stdHba1c >= 0.0);
        Assert.Equal(stdHba1c, doc.GetColumnStdDev("hba1c_endpoint")); // consistent

        // stdDev^2 ≈ variance for same column
        var varHba1c = doc.GetColumnVariance("hba1c_endpoint");
        Assert.True(Math.Abs(stdHba1c * stdHba1c - varHba1c) < 0.1);

        // GetCoefficientOfVariation — relative variability
        var cvLdl = doc.GetCoefficientOfVariation("ldl_reduction");
        Assert.True(cvLdl >= 0.0);
        Assert.Equal(cvLdl, doc.GetCoefficientOfVariation("ldl_reduction")); // consistent

        var cvHdl = doc.GetCoefficientOfVariation("hdl_increase");
        Assert.True(cvHdl >= 0.0);

        // Consistent
        Assert.Equal(doc.GetColumnVariance("baseline_ldl"), doc.GetColumnVariance("baseline_ldl"));

        // SaveToFile
        var out1 = TempFile("dogfood_biomarker_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(varLdl, loaded.GetColumnVariance("ldl_reduction"), precision: 4);
        Assert.Equal(stdHba1c, loaded.GetColumnStdDev("hba1c_endpoint"), precision: 4);
        Assert.Equal(cvLdl, loaded.GetCoefficientOfVariation("ldl_reduction"), precision: 4);

        // AddRow and re-verify
        loaded.AddRow(new[] { "P013", "55", "188.5", "128.4", "60.1", "9.2", "7.9", "7.0" });
        Assert.Equal(13, loaded.GetRowCount());
        var newVar = loaded.GetColumnVariance("ldl_reduction");
        Assert.True(newVar >= 0.0); // still valid after row addition

        // Final save
        var out2 = TempFile("dogfood_biomarker_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnVariance("age") >= 0.0);
        Assert.True(loaded2.GetColumnStdDev("ldl_reduction") >= 0.0);
        Assert.True(loaded2.GetCoefficientOfVariation("hdl_increase") >= 0.0);
    }
}
