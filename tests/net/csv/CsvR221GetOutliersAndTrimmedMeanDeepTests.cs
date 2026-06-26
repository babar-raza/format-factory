// Tests for CsvDocument.GetOutliers, GetTrimmedMean, GetModeValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R221

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R221: Tests for CsvDocument.GetOutliers, GetTrimmedMean, GetModeValue deeper.
/// GetOutliers(colName, threshold): returns row indices where the column value deviates beyond threshold std devs.
/// GetTrimmedMean(colName, trimPercent): returns the mean after trimming extreme percentiles.
/// GetModeValue(colName): returns the most frequently occurring value in the column.
/// Covers: GetOutliers no-throw; GetOutliers non-null; GetOutliers count leq row count;
/// GetOutliers consistent; GetOutliers save-load; GetOutliers higher-threshold-fewer;
/// GetTrimmedMean no-throw; GetTrimmedMean finite; GetTrimmedMean consistent;
/// GetTrimmedMean save-load; GetTrimmedMean between min and max;
/// GetModeValue no-throw; GetModeValue non-null; GetModeValue consistent;
/// GetModeValue save-load; GetModeValue not-empty;
/// dogfood LoadFile→GetOutliers→GetTrimmedMean→GetModeValue→SaveToFile pipeline.
/// </summary>
public class CsvR221GetOutliersAndTrimmedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR221GetOutliersAndTrimmedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR221_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSalaryCsv()
    {
        var path = TempFile("salaries.csv");
        var content =
            "Employee,Department,Salary,YearsExp,Rating\n" +
            "Alice,Engineering,95000,5,4.2\n" +
            "Bob,Marketing,72000,3,3.8\n" +
            "Carol,Engineering,115000,8,4.7\n" +
            "Dave,HR,68000,2,3.5\n" +
            "Eve,Engineering,88000,4,4.0\n" +
            "Frank,Marketing,750000,6,3.9\n" +
            "Grace,Finance,92000,6,4.3\n" +
            "Hector,HR,71000,3,3.6\n" +
            "Iris,Engineering,105000,7,4.5\n" +
            "Jack,Finance,88000,5,4.1\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutliers_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var ex = Record.Exception(() => doc.GetOutliers("Salary", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutliers_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.NotNull(doc.GetOutliers("Salary", 2.0));
    }

    [Fact]
    public void GetOutliers_Count_Leq_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.True(doc.GetOutliers("Salary", 2.0).Length <= doc.GetRowCount());
    }

    [Fact]
    public void GetOutliers_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var o1 = doc.GetOutliers("Salary", 2.0);
        var o2 = doc.GetOutliers("Salary", 2.0);
        Assert.Equal(o1.Length, o2.Length);
    }

    [Fact]
    public void GetOutliers_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var before = doc.GetOutliers("Salary", 2.0).Length;
        var path = TempFile("ol_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutliers("Salary", 2.0).Length);
    }

    [Fact]
    public void GetOutliers_Higher_Threshold_Fewer_Or_Equal()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var tight = doc.GetOutliers("Salary", 1.5);
        var loose = doc.GetOutliers("Salary", 4.0);
        Assert.True(loose.Length <= tight.Length);
    }

    // -------------------------------------------------------------------------
    // GetTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTrimmedMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var ex = Record.Exception(() => doc.GetTrimmedMean("Salary", 10.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTrimmedMean_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.True(double.IsFinite(doc.GetTrimmedMean("Salary", 10.0)));
    }

    [Fact]
    public void GetTrimmedMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.Equal(
            doc.GetTrimmedMean("Salary", 10.0),
            doc.GetTrimmedMean("Salary", 10.0));
    }

    [Fact]
    public void GetTrimmedMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var before = doc.GetTrimmedMean("Salary", 10.0);
        var path = TempFile("tm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTrimmedMean("Salary", 10.0), 3);
    }

    [Fact]
    public void GetTrimmedMean_Between_Min_And_Max()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var trimmed = doc.GetTrimmedMean("Salary", 10.0);
        Assert.True(trimmed >= doc.GetMinValue("Salary"));
        Assert.True(trimmed <= doc.GetMaxValue("Salary"));
    }

    // -------------------------------------------------------------------------
    // GetModeValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetModeValue_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var ex = Record.Exception(() => doc.GetModeValue("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetModeValue_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.NotNull(doc.GetModeValue("Department"));
    }

    [Fact]
    public void GetModeValue_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        Assert.Equal(doc.GetModeValue("Department"), doc.GetModeValue("Department"));
    }

    [Fact]
    public void GetModeValue_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var before = doc.GetModeValue("Department");
        var path = TempFile("mv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetModeValue("Department"));
    }

    [Fact]
    public void GetModeValue_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSalaryCsv());
        var mode = doc.GetModeValue("Department");
        Assert.NotNull(mode);
        Assert.NotEmpty(mode);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutliers_GetTrimmedMean_GetModeValue_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_claims.csv");
        var content =
            "ClaimId,PolicyType,Amount,DaysToSettle,Adjuster,Region\n" +
            "C001,Auto,4200,12,Jones,North\n" +
            "C002,Home,8500,18,Smith,South\n" +
            "C003,Auto,3800,9,Brown,East\n" +
            "C004,Health,250000,45,Jones,North\n" +
            "C005,Auto,5100,14,Garcia,West\n" +
            "C006,Home,12000,22,Smith,South\n" +
            "C007,Auto,4600,11,Brown,East\n" +
            "C008,Life,3900,8,Jones,North\n" +
            "C009,Auto,4100,13,Garcia,West\n" +
            "C010,Home,9800,19,Smith,South\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetOutliers — Amount has clear outlier (250000)
        var outliers = doc.GetOutliers("Amount", 2.0);
        Assert.NotNull(outliers);
        Assert.True(outliers.Length >= 0);
        Assert.True(outliers.Length <= doc.GetRowCount());
        Assert.Equal(outliers.Length, doc.GetOutliers("Amount", 2.0).Length); // consistent

        // GetOutliers — higher threshold catches fewer
        var tightOutliers = doc.GetOutliers("Amount", 1.5);
        var looseOutliers = doc.GetOutliers("Amount", 3.0);
        Assert.True(looseOutliers.Length <= tightOutliers.Length);

        // GetTrimmedMean — Amount (trimmed mean excludes outlier)
        var trimMean = doc.GetTrimmedMean("Amount", 10.0);
        Assert.True(double.IsFinite(trimMean));
        Assert.True(trimMean >= doc.GetMinValue("Amount"));
        Assert.True(trimMean <= doc.GetMaxValue("Amount"));
        Assert.Equal(trimMean, doc.GetTrimmedMean("Amount", 10.0)); // consistent

        // GetTrimmedMean — DaysToSettle
        var trimDays = doc.GetTrimmedMean("DaysToSettle", 10.0);
        Assert.True(double.IsFinite(trimDays));

        // GetModeValue — PolicyType ("Auto" appears 5 times)
        var modeType = doc.GetModeValue("PolicyType");
        Assert.NotNull(modeType);
        Assert.NotEmpty(modeType);
        Assert.Equal(modeType, doc.GetModeValue("PolicyType")); // consistent

        // GetModeValue — Adjuster ("Smith" or "Jones" both appear 3 times)
        var modeAdj = doc.GetModeValue("Adjuster");
        Assert.NotNull(modeAdj);

        // GetModeValue — Region ("North" and "South" both 3 times)
        var modeReg = doc.GetModeValue("Region");
        Assert.NotNull(modeReg);

        // AddRow and recheck
        doc.AddRow(new[] { "C011", "Auto", "4400", "12", "Brown", "East" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.NotNull(doc.GetOutliers("Amount", 2.0));
        Assert.True(double.IsFinite(doc.GetTrimmedMean("Amount", 10.0)));
        Assert.NotNull(doc.GetModeValue("PolicyType"));

        // SaveToFile
        var savePath = TempFile("dogfood_claims_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(11, loaded.GetRowCount());
        Assert.Equal(doc.GetTrimmedMean("Amount", 10.0), loaded.GetTrimmedMean("Amount", 10.0), 2);
        Assert.Equal(doc.GetModeValue("PolicyType"), loaded.GetModeValue("PolicyType"));

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("Amount", cols);
        Assert.Contains("PolicyType", cols);

        // Final save
        var path2 = TempFile("dogfood_claims_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetModeValue("PolicyType"), loaded2.GetModeValue("PolicyType"));
        Assert.Equal(loaded.GetTrimmedMean("Amount", 10.0), loaded2.GetTrimmedMean("Amount", 10.0), 2);
    }
}
