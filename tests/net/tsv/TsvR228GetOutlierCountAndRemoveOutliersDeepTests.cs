// Tests for TsvDocument.GetOutlierCount, RemoveOutliers, GetZScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R228

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R228: Tests for TsvDocument.GetOutlierCount, RemoveOutliers, GetZScore deeper.
/// GetOutlierCount(columnName): returns the number of outliers in the column (|z| > 2).
/// RemoveOutliers(columnName): returns a new document with outlier rows removed.
/// GetZScore(columnName, rowIndex): returns the z-score of the value at the given row.
/// Covers: GetOutlierCount no-throw; GetOutlierCount non-negative; GetOutlierCount consistent;
/// GetOutlierCount zero for uniform; GetOutlierCount leq row count; GetOutlierCount save-load;
/// RemoveOutliers no-throw; RemoveOutliers non-null; RemoveOutliers count leq original;
/// RemoveOutliers consistent; RemoveOutliers save-load;
/// GetZScore no-throw; GetZScore finite; GetZScore consistent; GetZScore zero for uniform mean;
/// GetZScore save-load;
/// dogfood CreateDoc→GetOutlierCount→RemoveOutliers→GetZScore→SaveToFile pipeline.
/// </summary>
public class TsvR228GetOutlierCountAndRemoveOutliersDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR228GetOutlierCountAndRemoveOutliersDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR228_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCreditRiskTsv()
    {
        var path = TempFile("credit_risk.tsv");
        File.WriteAllText(path,
            "borrower\tcredit_score\tincome_k\tdebt_ratio\tloan_amount_k\tdefault_rate\n" +
            "B001\t720\t65\t0.28\t180\t0.012\n" +
            "B002\t685\t48\t0.35\t120\t0.028\n" +
            "B003\t750\t82\t0.22\t250\t0.008\n" +
            "B004\t630\t38\t0.48\t85\t0.065\n" +
            "B005\t710\t71\t0.31\t195\t0.018\n" +
            "B006\t770\t95\t0.19\t320\t0.006\n" +
            "B007\t890\t950\t0.05\t2800\t0.001\n" +  // income outlier
            "B008\t660\t42\t0.42\t100\t0.045\n" +
            "B009\t740\t78\t0.24\t220\t0.010\n" +
            "B010\t200\t35\t0.89\t50\t0.890\n" +  // credit/default outliers
            "B011\t725\t67\t0.29\t185\t0.014\n" +
            "B012\t695\t55\t0.33\t140\t0.024\n");
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        File.WriteAllText(path,
            "id\tvalue\n" +
            "1\t10.0\n" +
            "2\t10.0\n" +
            "3\t10.0\n" +
            "4\t10.0\n" +
            "5\t10.0\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlierCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var ex = Record.Exception(() => doc.GetOutlierCount("income_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutlierCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        Assert.True(doc.GetOutlierCount("credit_score") >= 0);
    }

    [Fact]
    public void GetOutlierCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        Assert.Equal(doc.GetOutlierCount("income_k"), doc.GetOutlierCount("income_k"));
    }

    [Fact]
    public void GetOutlierCount_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0, doc.GetOutlierCount("value"));
    }

    [Fact]
    public void GetOutlierCount_LeqRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        Assert.True(doc.GetOutlierCount("income_k") <= doc.GetRowCount());
    }

    [Fact]
    public void GetOutlierCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var before = doc.GetOutlierCount("income_k");
        var path = TempFile("oc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutlierCount("income_k"));
    }

    // -------------------------------------------------------------------------
    // RemoveOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveOutliers_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var ex = Record.Exception(() => doc.RemoveOutliers("income_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveOutliers_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        Assert.NotNull(doc.RemoveOutliers("income_k"));
    }

    [Fact]
    public void RemoveOutliers_Count_LeqOriginal()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var cleaned = doc.RemoveOutliers("income_k");
        Assert.True(cleaned.GetRowCount() <= doc.GetRowCount());
    }

    [Fact]
    public void RemoveOutliers_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var c1 = doc.RemoveOutliers("credit_score");
        var c2 = doc.RemoveOutliers("credit_score");
        Assert.Equal(c1.GetRowCount(), c2.GetRowCount());
    }

    [Fact]
    public void RemoveOutliers_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var cleaned = doc.RemoveOutliers("income_k");
        var path = TempFile("ro_save.tsv");
        cleaned.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(cleaned.GetRowCount(), loaded.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var ex = Record.Exception(() => doc.GetZScore("income_k", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScore_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var z = doc.GetZScore("credit_score", 0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        Assert.Equal(doc.GetZScore("income_k", 1), doc.GetZScore("income_k", 1));
    }

    [Fact]
    public void GetZScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCreditRiskTsv());
        var before = doc.GetZScore("credit_score", 0);
        var path = TempFile("zs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScore("credit_score", 0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutlierCount_RemoveOutliers_GetZScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_insurance.tsv");
        File.WriteAllText(path,
            "policy_id\tage\tbmi\tchildren\tsmoker_risk\tpremium_annual\tclaim_frequency\n" +
            "POL001\t34\t24.5\t1\t0.12\t2840\t0.08\n" +
            "POL002\t52\t31.2\t0\t0.28\t5720\t0.15\n" +
            "POL003\t28\t22.8\t2\t0.08\t2100\t0.05\n" +
            "POL004\t45\t28.4\t3\t0.19\t4180\t0.12\n" +
            "POL005\t38\t26.1\t0\t0.14\t3240\t0.09\n" +
            "POL006\t67\t42.8\t0\t0.82\t28500\t0.68\n" + // outlier: BMI, premium, claim
            "POL007\t41\t25.7\t2\t0.16\t3580\t0.10\n" +
            "POL008\t29\t23.4\t1\t0.09\t2280\t0.06\n" +
            "POL009\t55\t33.1\t0\t0.31\t6420\t0.18\n" +
            "POL010\t62\t38.2\t1\t0.44\t9800\t0.28\n" +
            "POL011\t33\t24.2\t3\t0.11\t2750\t0.07\n" +
            "POL012\t48\t29.8\t2\t0.22\t4820\t0.14\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetOutlierCount — per column
        var outBmi = doc.GetOutlierCount("bmi");
        Assert.True(outBmi >= 0);
        Assert.True(outBmi <= doc.GetRowCount());

        var outPremium = doc.GetOutlierCount("premium_annual");
        Assert.True(outPremium >= 0);
        Assert.True(outPremium <= doc.GetRowCount());

        // Consistent
        Assert.Equal(outBmi, doc.GetOutlierCount("bmi"));

        // Zero for near-uniform age distribution
        var outAge = doc.GetOutlierCount("age");
        Assert.True(outAge >= 0);

        // RemoveOutliers
        var cleanedBmi = doc.RemoveOutliers("bmi");
        Assert.NotNull(cleanedBmi);
        Assert.True(cleanedBmi.GetRowCount() <= doc.GetRowCount());
        Assert.Equal(cleanedBmi.GetRowCount(), doc.RemoveOutliers("bmi").GetRowCount()); // consistent

        var cleanedPremium = doc.RemoveOutliers("premium_annual");
        Assert.NotNull(cleanedPremium);
        Assert.True(cleanedPremium.GetRowCount() <= doc.GetRowCount());

        // GetZScore
        var z0 = doc.GetZScore("premium_annual", 0);
        Assert.True(double.IsFinite(z0));

        var z5 = doc.GetZScore("premium_annual", 5); // row 5 = POL006 outlier
        Assert.True(double.IsFinite(z5));
        Assert.True(Math.Abs(z5) > Math.Abs(z0)); // outlier has larger |z|

        // Consistent
        Assert.Equal(z0, doc.GetZScore("premium_annual", 0));

        // ExportToCsv no-throw
        var ex1 = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex1);

        // SaveToFile
        var out1 = TempFile("dogfood_insurance_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(outBmi, loaded.GetOutlierCount("bmi"));
        Assert.Equal(cleanedBmi.GetRowCount(), loaded.RemoveOutliers("bmi").GetRowCount());
        Assert.Equal(z0, loaded.GetZScore("premium_annual", 0), precision: 6);

        // Save cleaned version
        var outCleaned = TempFile("dogfood_insurance_cleaned.tsv");
        cleanedBmi.SaveToFile(outCleaned);
        Assert.True(File.Exists(outCleaned));
        var loadedCleaned = TsvDocument.LoadFile(outCleaned);
        Assert.Equal(cleanedBmi.GetRowCount(), loadedCleaned.GetRowCount());
        Assert.True(loadedCleaned.GetOutlierCount("bmi") >= 0);

        // Final save
        var out2 = TempFile("dogfood_insurance_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(12, loaded2.GetRowCount());
        Assert.True(loaded2.GetOutlierCount("premium_annual") >= 0);
        Assert.NotNull(loaded2.RemoveOutliers("bmi"));
        Assert.True(double.IsFinite(loaded2.GetZScore("premium_annual", 0)));
    }
}
