// Tests for TsvDocument.GetRSquared, GetResidualStdDev, GetMeanAbsoluteError deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R227

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R227: Tests for TsvDocument.GetRSquared, GetResidualStdDev, GetMeanAbsoluteError deeper.
/// GetRSquared(xCol, yCol): returns the coefficient of determination (R²) for the regression.
/// GetResidualStdDev(xCol, yCol): returns the standard deviation of regression residuals.
/// GetMeanAbsoluteError(xCol, yCol): returns the mean absolute error of the regression.
/// Covers: GetRSquared no-throw; GetRSquared in [0,1]; GetRSquared consistent;
/// GetRSquared perfect for linear data; GetRSquared save-load;
/// GetResidualStdDev no-throw; GetResidualStdDev non-negative; GetResidualStdDev consistent;
/// GetResidualStdDev zero for perfect fit; GetResidualStdDev save-load;
/// GetMeanAbsoluteError no-throw; GetMeanAbsoluteError non-negative; GetMeanAbsoluteError consistent;
/// GetMeanAbsoluteError save-load;
/// dogfood CreateDoc→GetRSquared→GetResidualStdDev→GetMeanAbsoluteError→SaveToFile pipeline.
/// </summary>
public class TsvR227GetRSquaredAndResidualDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR227GetRSquaredAndResidualDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR227_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePopulationTsv()
    {
        var path = TempFile("population.tsv");
        File.WriteAllText(path,
            "city\tpopulation_m\tgdp_b\tarea_km2\tdensity\tincome_k\n" +
            "Tokyo\t37.4\t2142\t13572\t2756\t42.8\n" +
            "Delhi\t31.2\t292\t2230\t13989\t3.1\n" +
            "Shanghai\t27.1\t678\t6341\t4273\t18.4\n" +
            "Sao Paulo\t22.4\t358\t7947\t2819\t10.2\n" +
            "Mexico City\t21.7\t411\t7866\t2759\t12.7\n" +
            "Cairo\t21.3\t119\t3085\t6905\t3.8\n" +
            "Mumbai\t20.7\t209\t603\t34327\t5.9\n" +
            "Beijing\t20.4\t532\t16411\t1243\t18.1\n" +
            "Dhaka\t21.0\t103\t1528\t13739\t2.4\n" +
            "Osaka\t19.1\t654\t3300\t5788\t33.1\n");
        return path;
    }

    private string CreateLinearTsv()
    {
        // Perfect linear relationship: y = 2*x + 3
        var path = TempFile("linear.tsv");
        File.WriteAllText(path,
            "x\ty\n" +
            "1\t5\n" +
            "2\t7\n" +
            "3\t9\n" +
            "4\t11\n" +
            "5\t13\n" +
            "6\t15\n" +
            "7\t17\n" +
            "8\t19\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRSquared
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRSquared_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var ex = Record.Exception(() => doc.GetRSquared("population_m", "gdp_b"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRSquared_InRange()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var r2 = doc.GetRSquared("population_m", "gdp_b");
        Assert.True(r2 >= 0.0 && r2 <= 1.0);
    }

    [Fact]
    public void GetRSquared_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        Assert.Equal(
            doc.GetRSquared("population_m", "income_k"),
            doc.GetRSquared("population_m", "income_k"));
    }

    [Fact]
    public void GetRSquared_PerfectFit_ForLinearData()
    {
        var doc = TsvDocument.LoadFile(CreateLinearTsv());
        var r2 = doc.GetRSquared("x", "y");
        Assert.True(r2 >= 0.999); // R² ≈ 1.0 for perfect linear
    }

    [Fact]
    public void GetRSquared_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var before = doc.GetRSquared("population_m", "gdp_b");
        var path = TempFile("r2_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRSquared("population_m", "gdp_b"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetResidualStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetResidualStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var ex = Record.Exception(() => doc.GetResidualStdDev("population_m", "gdp_b"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetResidualStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        Assert.True(doc.GetResidualStdDev("population_m", "gdp_b") >= 0.0);
    }

    [Fact]
    public void GetResidualStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        Assert.Equal(
            doc.GetResidualStdDev("population_m", "income_k"),
            doc.GetResidualStdDev("population_m", "income_k"));
    }

    [Fact]
    public void GetResidualStdDev_Zero_ForPerfectFit()
    {
        var doc = TsvDocument.LoadFile(CreateLinearTsv());
        var stdDev = doc.GetResidualStdDev("x", "y");
        Assert.True(stdDev < 1e-9 || stdDev == 0.0);
    }

    [Fact]
    public void GetResidualStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var before = doc.GetResidualStdDev("population_m", "gdp_b");
        var path = TempFile("rsd_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetResidualStdDev("population_m", "gdp_b"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMeanAbsoluteError
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanAbsoluteError_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var ex = Record.Exception(() => doc.GetMeanAbsoluteError("population_m", "gdp_b"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMeanAbsoluteError_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        Assert.True(doc.GetMeanAbsoluteError("population_m", "gdp_b") >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteError_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        Assert.Equal(
            doc.GetMeanAbsoluteError("population_m", "income_k"),
            doc.GetMeanAbsoluteError("population_m", "income_k"));
    }

    [Fact]
    public void GetMeanAbsoluteError_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePopulationTsv());
        var before = doc.GetMeanAbsoluteError("population_m", "gdp_b");
        var path = TempFile("mae_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMeanAbsoluteError("population_m", "gdp_b"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRSquared_GetResidualStdDev_GetMeanAbsoluteError_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_labour.tsv");
        File.WriteAllText(path,
            "sector\tautomation_risk_pct\tavg_wage_kGBP\tjob_growth_pct\tskills_gap_index\tproductivity_index\n" +
            "Manufacturing\t68.2\t28.5\t-2.4\t0.72\t88.4\n" +
            "Retail\t62.5\t21.3\t-1.8\t0.68\t79.2\n" +
            "Finance\t32.1\t58.7\t1.2\t0.41\t112.6\n" +
            "Healthcare\t18.4\t38.9\t4.6\t0.35\t105.3\n" +
            "Education\t22.8\t35.2\t2.1\t0.38\t98.7\n" +
            "Technology\t8.3\t72.4\t6.8\t0.22\t135.2\n" +
            "Transport\t57.9\t32.1\t-0.9\t0.61\t91.5\n" +
            "Construction\t44.3\t34.8\t0.6\t0.55\t84.3\n" +
            "Hospitality\t71.4\t19.8\t-3.2\t0.74\t76.1\n" +
            "Professional Services\t14.7\t65.3\t3.4\t0.28\t118.9\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());
        Assert.Equal(6, doc.GetColumnCount());

        // GetRSquared — automation risk vs job growth (expect moderate-high R²)
        var r2AutoJob = doc.GetRSquared("automation_risk_pct", "job_growth_pct");
        Assert.True(r2AutoJob >= 0.0 && r2AutoJob <= 1.0);

        // Higher automation risk → lower wage? Get R²
        var r2AutoWage = doc.GetRSquared("automation_risk_pct", "avg_wage_kGBP");
        Assert.True(r2AutoWage >= 0.0 && r2AutoWage <= 1.0);

        // Consistent
        Assert.Equal(r2AutoJob, doc.GetRSquared("automation_risk_pct", "job_growth_pct"));

        // Perfect fit R² check
        var linearDoc = TsvDocument.LoadFile(CreateLinearTsv());
        var r2Perfect = linearDoc.GetRSquared("x", "y");
        Assert.True(r2Perfect >= 0.999);

        // GetResidualStdDev
        var rsdAutoJob = doc.GetResidualStdDev("automation_risk_pct", "job_growth_pct");
        Assert.True(rsdAutoJob >= 0.0);

        var rsdProductivity = doc.GetResidualStdDev("skills_gap_index", "productivity_index");
        Assert.True(rsdProductivity >= 0.0);

        // Consistent
        Assert.Equal(rsdAutoJob, doc.GetResidualStdDev("automation_risk_pct", "job_growth_pct"));

        // Perfect fit residual zero
        var rsdPerfect = linearDoc.GetResidualStdDev("x", "y");
        Assert.True(rsdPerfect < 1e-9 || rsdPerfect == 0.0);

        // GetMeanAbsoluteError
        var maeAutoJob = doc.GetMeanAbsoluteError("automation_risk_pct", "job_growth_pct");
        Assert.True(maeAutoJob >= 0.0);

        var maeWageProductivity = doc.GetMeanAbsoluteError("avg_wage_kGBP", "productivity_index");
        Assert.True(maeWageProductivity >= 0.0);

        // Consistent
        Assert.Equal(maeAutoJob, doc.GetMeanAbsoluteError("automation_risk_pct", "job_growth_pct"));

        // ExportToCsv no-throw
        var ex1 = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex1);

        // SaveToFile
        var out1 = TempFile("dogfood_labour_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(r2AutoJob, loaded.GetRSquared("automation_risk_pct", "job_growth_pct"), precision: 6);
        Assert.Equal(rsdAutoJob, loaded.GetResidualStdDev("automation_risk_pct", "job_growth_pct"), precision: 6);
        Assert.Equal(maeAutoJob, loaded.GetMeanAbsoluteError("automation_risk_pct", "job_growth_pct"), precision: 6);

        // AddRow
        loaded.AddRow(new[] { "Legal", "12.1", "75.2", "1.9", "0.19", "122.4" });
        Assert.Equal(11, loaded.GetRowCount());
        Assert.True(loaded.GetRSquared("automation_risk_pct", "job_growth_pct") >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_labour_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRowCount());
        Assert.True(loaded2.GetRSquared("automation_risk_pct", "avg_wage_kGBP") >= 0.0);
        Assert.True(loaded2.GetResidualStdDev("automation_risk_pct", "job_growth_pct") >= 0.0);
        Assert.True(loaded2.GetMeanAbsoluteError("avg_wage_kGBP", "productivity_index") >= 0.0);
    }
}
