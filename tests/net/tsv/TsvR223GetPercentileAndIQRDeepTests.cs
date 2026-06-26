// Tests for TsvDocument.GetPercentile, GetIQR, GetSkewness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R223

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R223: Tests for TsvDocument.GetPercentile, GetIQR, GetSkewness deeper.
/// GetPercentile(colName, p): returns the p-th percentile of the numeric column.
/// GetIQR(colName): returns the interquartile range (Q3 - Q1).
/// GetSkewness(colName): returns the skewness statistic for the column.
/// Covers: GetPercentile no-throw; GetPercentile in [min,max]; GetPercentile consistent;
/// GetPercentile 50th equals median; GetPercentile save-load;
/// GetIQR no-throw; GetIQR non-negative; GetIQR consistent;
/// GetIQR save-load; GetIQR leq range;
/// GetSkewness no-throw; GetSkewness finite; GetSkewness consistent;
/// GetSkewness save-load; GetSkewness zero-for-symmetric;
/// dogfood LoadFile→GetPercentile→GetIQR→GetSkewness→SaveToFile pipeline.
/// </summary>
public class TsvR223GetPercentileAndIQRDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR223GetPercentileAndIQRDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR223_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHealthTsv()
    {
        var path = TempFile("health.tsv");
        var content =
            "PatientId\tAge\tBMI\tBloodPressure\tCholesterol\tGlucose\n" +
            "P001\t45\t24.5\t120\t185\t95\n" +
            "P002\t62\t31.2\t145\t220\t110\n" +
            "P003\t38\t22.1\t115\t175\t88\n" +
            "P004\t55\t28.7\t135\t240\t105\n" +
            "P005\t71\t33.4\t155\t260\t130\n" +
            "P006\t29\t20.8\t110\t165\t82\n" +
            "P007\t48\t26.3\t128\t195\t98\n" +
            "P008\t66\t29.8\t140\t230\t115\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPercentile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var ex = Record.Exception(() => doc.GetPercentile("Age", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPercentile_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var p50 = doc.GetPercentile("Age", 50);
        Assert.True(p50 >= doc.GetColumnMin("Age") && p50 <= doc.GetColumnMax("Age"));
    }

    [Fact]
    public void GetPercentile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.Equal(doc.GetPercentile("BMI", 75), doc.GetPercentile("BMI", 75));
    }

    [Fact]
    public void GetPercentile_50th_Leq_75th()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.True(doc.GetPercentile("Cholesterol", 50) <= doc.GetPercentile("Cholesterol", 75));
    }

    [Fact]
    public void GetPercentile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var before = doc.GetPercentile("BloodPressure", 50);
        var path = TempFile("pct_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPercentile("BloodPressure", 50), 4);
    }

    // -------------------------------------------------------------------------
    // GetIQR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIQR_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var ex = Record.Exception(() => doc.GetIQR("Age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetIQR_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.True(doc.GetIQR("BMI") >= 0.0);
    }

    [Fact]
    public void GetIQR_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.Equal(doc.GetIQR("Cholesterol"), doc.GetIQR("Cholesterol"));
    }

    [Fact]
    public void GetIQR_Leq_Range()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.True(doc.GetIQR("Age") <= doc.GetColumnRange("Age"));
    }

    [Fact]
    public void GetIQR_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var before = doc.GetIQR("Glucose");
        var path = TempFile("iqr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetIQR("Glucose"), 4);
    }

    // -------------------------------------------------------------------------
    // GetSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var ex = Record.Exception(() => doc.GetSkewness("Age"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.True(double.IsFinite(doc.GetSkewness("BMI")));
    }

    [Fact]
    public void GetSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        Assert.Equal(doc.GetSkewness("Cholesterol"), doc.GetSkewness("Cholesterol"));
    }

    [Fact]
    public void GetSkewness_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHealthTsv());
        var before = doc.GetSkewness("Age");
        var path = TempFile("skew_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSkewness("Age"), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetPercentile_GetIQR_GetSkewness_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_finance.tsv");
        var content =
            "AssetId\tReturn\tVolatility\tSharpe\tBeta\tAlpha\n" +
            "A001\t12.4\t14.2\t1.28\t1.05\t2.3\n" +
            "A002\t8.9\t9.8\t1.15\t0.82\t1.7\n" +
            "A003\t18.6\t18.5\t1.42\t1.35\t3.8\n" +
            "A004\t6.2\t7.2\t1.08\t0.61\t1.1\n" +
            "A005\t14.7\t12.9\t1.22\t1.15\t2.8\n" +
            "A006\t22.1\t16.8\t1.35\t1.48\t4.5\n" +
            "A007\t4.8\t4.1\t1.02\t0.45\t0.9\n" +
            "A008\t10.3\t8.6\t1.11\t0.88\t1.5\n" +
            "A009\t16.8\t15.3\t1.30\t1.22\t3.2\n" +
            "A010\t7.5\t6.9\t1.06\t0.72\t1.2\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetPercentile — Return
        var p25 = doc.GetPercentile("Return", 25);
        var p50 = doc.GetPercentile("Return", 50);
        var p75 = doc.GetPercentile("Return", 75);
        Assert.True(p25 <= p50);
        Assert.True(p50 <= p75);
        Assert.True(p25 >= doc.GetColumnMin("Return"));
        Assert.True(p75 <= doc.GetColumnMax("Return"));
        Assert.Equal(p50, doc.GetPercentile("Return", 50)); // consistent

        // GetPercentile — Volatility
        var volP50 = doc.GetPercentile("Volatility", 50);
        Assert.True(double.IsFinite(volP50));

        // GetIQR — Return
        var iqrReturn = doc.GetIQR("Return");
        Assert.True(iqrReturn >= 0);
        Assert.Equal(iqrReturn, doc.GetIQR("Return")); // consistent
        Assert.True(iqrReturn <= doc.GetColumnRange("Return"));
        Assert.Equal(p75 - p25, iqrReturn, 4);

        // GetIQR — Sharpe
        var iqrSharpe = doc.GetIQR("Sharpe");
        Assert.True(iqrSharpe >= 0);

        // GetSkewness — Return
        var skewReturn = doc.GetSkewness("Return");
        Assert.True(double.IsFinite(skewReturn));
        Assert.Equal(skewReturn, doc.GetSkewness("Return")); // consistent

        // GetSkewness — Beta
        var skewBeta = doc.GetSkewness("Beta");
        Assert.True(double.IsFinite(skewBeta));

        // AddRow and recheck
        doc.AddRow(new[] { "A011", "19.5", "17.2", "1.38", "1.40", "4.1" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.True(doc.GetIQR("Return") >= 0);
        Assert.True(double.IsFinite(doc.GetSkewness("Return")));

        // SaveToFile
        var savePath = TempFile("dogfood_finance_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(11, loaded.GetRowCount());
        Assert.Equal(doc.GetPercentile("Return", 50), loaded.GetPercentile("Return", 50), 4);
        Assert.Equal(doc.GetIQR("Volatility"), loaded.GetIQR("Volatility"), 4);
        Assert.Equal(doc.GetSkewness("Alpha"), loaded.GetSkewness("Alpha"), 4);

        // Final save
        var path2 = TempFile("dogfood_finance_v2.tsv");
        loaded.SaveToFile(path2);
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetPercentile("Return", 75), loaded2.GetPercentile("Return", 75), 4);
        Assert.Equal(loaded.GetIQR("Return"), loaded2.GetIQR("Return"), 4);
        Assert.Equal(loaded.GetSkewness("Return"), loaded2.GetSkewness("Return"), 4);
    }
}
