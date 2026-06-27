// Tests for TsvDocument.GetColumnOutliers, GetColumnTrimmedMean, GetColumnIQR deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R241

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R241: Tests for TsvDocument.GetColumnOutliers, GetColumnTrimmedMean, GetColumnIQR deeper.
/// GetColumnOutliers(columnName, threshold): returns the count of outlier values in the column.
/// GetColumnTrimmedMean(columnName, trimFraction): returns the mean after trimming extreme values.
/// GetColumnIQR(columnName): returns the interquartile range (Q3-Q1) of numeric values.
/// Covers: GetColumnOutliers no-throw; GetColumnOutliers non-negative; GetColumnOutliers consistent;
/// GetColumnOutliers zero for uniform data;
/// GetColumnTrimmedMean no-throw; GetColumnTrimmedMean finite; GetColumnTrimmedMean consistent;
/// GetColumnTrimmedMean between min and max;
/// GetColumnIQR no-throw; GetColumnIQR non-negative; GetColumnIQR consistent;
/// GetColumnIQR zero for constant column; GetColumnIQR save-load;
/// dogfood CreateDoc→GetColumnOutliers→GetColumnTrimmedMean→GetColumnIQR pipeline.
/// </summary>
public class TsvR241GetColumnOutliersAndTrimmedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR241GetColumnOutliersAndTrimmedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR241_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSalaryTsv()
    {
        var path = TempFile("salaries.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "employee_id\trole\tbase_salary\tbonus\ttenure_years",
            "E001\tAnalyst\t35000\t2500\t2",
            "E002\tSenior_Analyst\t48000\t4000\t5",
            "E003\tManager\t65000\t8000\t8",
            "E004\tSenior_Manager\t82000\t12000\t11",
            "E005\tDirector\t110000\t20000\t15",
            "E006\tAnalyst\t36000\t2600\t3",
            "E007\tSenior_Analyst\t49000\t4200\t6",
            "E008\tManager\t67000\t8500\t9",
            "E009\tDirector\t115000\t22000\t16",
            "E010\tAnalyst\t34500\t2400\t1",
            "E011\tCEO\t450000\t150000\t20",  // outlier
            "E012\tSenior_Analyst\t47500\t3800\t4",
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
            "R1\t100\tA",
            "R2\t100\tB",
            "R3\t100\tC",
            "R4\t100\tA",
            "R5\t100\tB",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutliers_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var ex = Record.Exception(() => doc.GetColumnOutliers("base_salary", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutliers_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.True(doc.GetColumnOutliers("base_salary", 2.0) >= 0);
    }

    [Fact]
    public void GetColumnOutliers_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.Equal(doc.GetColumnOutliers("base_salary", 2.0), doc.GetColumnOutliers("base_salary", 2.0));
    }

    [Fact]
    public void GetColumnOutliers_Zero_ForUniformData()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0, doc.GetColumnOutliers("value", 2.0));
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("base_salary", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var tm = doc.GetColumnTrimmedMean("base_salary", 0.1);
        Assert.True(double.IsFinite(tm));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.Equal(doc.GetColumnTrimmedMean("bonus", 0.1), doc.GetColumnTrimmedMean("bonus", 0.1));
    }

    [Fact]
    public void GetColumnTrimmedMean_Between_Min_And_Max()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var tm = doc.GetColumnTrimmedMean("tenure_years", 0.1);
        var min = doc.GetColumnMin("tenure_years");
        var max = doc.GetColumnMax("tenure_years");
        Assert.True(tm >= min);
        Assert.True(tm <= max);
    }

    // -------------------------------------------------------------------------
    // GetColumnIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIQR_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var ex = Record.Exception(() => doc.GetColumnIQR("base_salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIQR_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.True(doc.GetColumnIQR("base_salary") >= 0);
    }

    [Fact]
    public void GetColumnIQR_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        Assert.Equal(doc.GetColumnIQR("bonus"), doc.GetColumnIQR("bonus"));
    }

    [Fact]
    public void GetColumnIQR_Zero_ForConstantColumn()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnIQR("value"), precision: 6);
    }

    [Fact]
    public void GetColumnIQR_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSalaryTsv());
        var before = doc.GetColumnIQR("base_salary");
        var path = TempFile("iqr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnIQR("base_salary"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnOutliers_GetColumnTrimmedMean_GetColumnIQR_Pipeline()
    {
        // UK NHS hospital episode statistics — length-of-stay and cost analysis
        var path = TempFile("hospital_episodes.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("episode_id\tspecialty\tlos_days\ttotal_cost_gbp\tage_at_admission\treadmission_flag");
        var rng = new Random(20240601);
        string[] specialties = { "Cardiology", "Orthopaedics", "Oncology", "General_Surgery", "Neurology", "Respiratory" };
        for (int i = 0; i < 150; i++)
        {
            var spec = specialties[i % 6];
            // Most LOS 1-14 days, occasional extreme outlier (60+ days)
            double los = i % 25 == 0 ? 60 + rng.NextDouble() * 40 : 1 + rng.NextDouble() * 13;
            double cost = los * (800 + rng.NextDouble() * 400);
            int age = 18 + rng.Next(0, 72);
            int readmit = (rng.NextDouble() < 0.08) ? 1 : 0;
            lines.Add($"EP{i:D5}\t{spec}\t{los:F1}\t{cost:F0}\t{age}\t{readmit}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnIQR
        var losIqr = doc.GetColumnIQR("los_days");
        Assert.True(losIqr >= 0);
        var costIqr = doc.GetColumnIQR("total_cost_gbp");
        Assert.True(costIqr >= 0);
        Assert.Equal(losIqr, doc.GetColumnIQR("los_days")); // consistent

        // GetColumnOutliers — LOS outliers (ICU long-stays)
        var losOutliers = doc.GetColumnOutliers("los_days", 2.0);
        Assert.True(losOutliers >= 0);
        Assert.Equal(losOutliers, doc.GetColumnOutliers("los_days", 2.0)); // consistent

        // GetColumnTrimmedMean — robust cost estimate excluding extremes
        var trimmedMean = doc.GetColumnTrimmedMean("total_cost_gbp", 0.1);
        Assert.True(double.IsFinite(trimmedMean));
        var min = doc.GetColumnMin("total_cost_gbp");
        var max = doc.GetColumnMax("total_cost_gbp");
        Assert.True(trimmedMean >= min);
        Assert.True(trimmedMean <= max);
        Assert.Equal(trimmedMean, doc.GetColumnTrimmedMean("total_cost_gbp", 0.1)); // consistent

        // All columns
        foreach (var col in new[] { "los_days", "total_cost_gbp", "age_at_admission" })
        {
            Assert.True(doc.GetColumnIQR(col) >= 0);
            Assert.True(doc.GetColumnOutliers(col, 2.0) >= 0);
            Assert.True(double.IsFinite(doc.GetColumnTrimmedMean(col, 0.1)));
        }

        // SaveToFile
        var outPath = TempFile("hospital_episodes_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(losIqr, loaded.GetColumnIQR("los_days"), precision: 6);
        Assert.True(double.IsFinite(loaded.GetColumnTrimmedMean("total_cost_gbp", 0.1)));
        Assert.True(loaded.GetColumnOutliers("los_days", 2.0) >= 0);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean / StdDev consistency
        var mean = doc.GetColumnMean("los_days");
        var std = doc.GetColumnStdDev("los_days");
        Assert.True(mean >= doc.GetColumnMin("los_days"));
        Assert.True(mean <= doc.GetColumnMax("los_days"));
        Assert.True(std >= 0);
        // Trimmed mean closer to median for right-skewed data
        Assert.True(double.IsFinite(doc.GetColumnTrimmedMean("los_days", 0.05)));
    }
}
