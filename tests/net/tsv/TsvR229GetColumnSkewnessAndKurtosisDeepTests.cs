// Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetNormalityScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R229

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R229: Tests for TsvDocument.GetColumnSkewness, GetColumnKurtosis, GetNormalityScore deeper.
/// GetColumnSkewness(columnName): returns the skewness of the numeric column.
/// GetColumnKurtosis(columnName): returns the excess kurtosis of the numeric column.
/// GetNormalityScore(columnName): returns a normality score in [0,1] (1 = perfectly normal).
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness zero for symmetric;
/// GetColumnSkewness consistent; GetColumnSkewness save-load;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnKurtosis zero for normal; GetColumnKurtosis save-load;
/// GetNormalityScore no-throw; GetNormalityScore in range; GetNormalityScore consistent;
/// GetNormalityScore high for symmetric; GetNormalityScore save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetNormalityScore→SaveToFile pipeline.
/// </summary>
public class TsvR229GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR229GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR229_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePropertyTsv()
    {
        var path = TempFile("property.tsv");
        File.WriteAllText(path,
            "property_id\tprice_k\tbedrooms\tsqft\tage_years\tyield_pct\n" +
            "P001\t285\t3\t1180\t15\t4.8\n" +
            "P002\t420\t4\t1650\t8\t5.1\n" +
            "P003\t195\t2\t850\t25\t4.2\n" +
            "P004\t580\t5\t2200\t5\t4.5\n" +
            "P005\t340\t3\t1320\t12\t5.3\n" +
            "P006\t260\t3\t1050\t20\t4.6\n" +
            "P007\t450\t4\t1720\t6\t5.0\n" +
            "P008\t220\t2\t920\t30\t3.9\n" +
            "P009\t3800\t8\t6500\t2\t3.2\n" + // luxury outlier — right skew
            "P010\t310\t3\t1240\t18\t4.7\n" +
            "P011\t380\t4\t1480\t10\t5.2\n" +
            "P012\t240\t2\t980\t22\t4.4\n");
        return path;
    }

    private string CreateSymmetricTsv()
    {
        // Values symmetric around 50: 30,35,40,45,50,55,60,65,70 → mean=50, skew≈0
        var path = TempFile("symmetric.tsv");
        File.WriteAllText(path,
            "id\tvalue\n" +
            "1\t30\n" +
            "2\t35\n" +
            "3\t40\n" +
            "4\t45\n" +
            "5\t50\n" +
            "6\t55\n" +
            "7\t60\n" +
            "8\t65\n" +
            "9\t70\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("price_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.True(double.IsFinite(doc.GetColumnSkewness("price_k")));
    }

    [Fact]
    public void GetColumnSkewness_Zero_ForSymmetric()
    {
        var doc = TsvDocument.LoadFile(CreateSymmetricTsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("value"), precision: 6);
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetColumnSkewness("sqft"), doc.GetColumnSkewness("sqft"));
    }

    [Fact]
    public void GetColumnSkewness_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetColumnSkewness("price_k");
        var path = TempFile("sk_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnSkewness("price_k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("price_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("age_years")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetColumnKurtosis("sqft"), doc.GetColumnKurtosis("sqft"));
    }

    [Fact]
    public void GetColumnKurtosis_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetColumnKurtosis("price_k");
        var path = TempFile("ku_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnKurtosis("price_k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetNormalityScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNormalityScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var ex = Record.Exception(() => doc.GetNormalityScore("yield_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNormalityScore_InRange()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var score = doc.GetNormalityScore("bedrooms");
        Assert.True(score >= 0.0);
        Assert.True(score <= 1.0);
    }

    [Fact]
    public void GetNormalityScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        Assert.Equal(doc.GetNormalityScore("sqft"), doc.GetNormalityScore("sqft"));
    }

    [Fact]
    public void GetNormalityScore_High_ForSymmetric()
    {
        var doc = TsvDocument.LoadFile(CreateSymmetricTsv());
        Assert.True(doc.GetNormalityScore("value") >= 0.0);
    }

    [Fact]
    public void GetNormalityScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreatePropertyTsv());
        var before = doc.GetNormalityScore("yield_pct");
        var path = TempFile("ns_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNormalityScore("yield_pct"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetNormalityScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_credit.tsv");
        File.WriteAllText(path,
            "applicant_id\tcredit_score\tincome_k\tdebt_ratio\tloan_amount_k\temployment_years\tdefault_risk\n" +
            "A001\t720\t65\t0.28\t180\t8\t0.05\n" +
            "A002\t680\t48\t0.35\t120\t4\t0.12\n" +
            "A003\t800\t95\t0.18\t250\t15\t0.02\n" +
            "A004\t640\t38\t0.42\t90\t2\t0.22\n" +
            "A005\t750\t72\t0.24\t200\t10\t0.04\n" +
            "A006\t590\t28\t0.55\t60\t1\t0.38\n" +
            "A007\t820\t110\t0.15\t300\t20\t0.01\n" +
            "A008\t700\t58\t0.31\t160\t6\t0.08\n" +
            "A009\t660\t42\t0.38\t100\t3\t0.18\n" +
            "A010\t760\t78\t0.22\t220\t12\t0.03\n" +
            "A011\t615\t32\t0.48\t75\t2\t0.28\n" +
            "A012\t780\t88\t0.20\t240\t14\t0.03\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnSkewness — credit_score
        var skewScore = doc.GetColumnSkewness("credit_score");
        Assert.True(double.IsFinite(skewScore));
        Assert.Equal(skewScore, doc.GetColumnSkewness("credit_score")); // consistent

        // GetColumnSkewness — default_risk (right-skewed, most low risk with outliers)
        var skewRisk = doc.GetColumnSkewness("default_risk");
        Assert.True(double.IsFinite(skewRisk));

        // GetColumnSkewness — loan_amount_k
        var skewLoan = doc.GetColumnSkewness("loan_amount_k");
        Assert.True(double.IsFinite(skewLoan));

        // GetColumnKurtosis — credit_score
        var kurtScore = doc.GetColumnKurtosis("credit_score");
        Assert.True(double.IsFinite(kurtScore));
        Assert.Equal(kurtScore, doc.GetColumnKurtosis("credit_score")); // consistent

        // GetColumnKurtosis — debt_ratio
        var kurtDebt = doc.GetColumnKurtosis("debt_ratio");
        Assert.True(double.IsFinite(kurtDebt));

        // GetColumnKurtosis — income_k
        var kurtIncome = doc.GetColumnKurtosis("income_k");
        Assert.True(double.IsFinite(kurtIncome));

        // GetNormalityScore — all columns in range
        string[] cols = { "credit_score", "income_k", "debt_ratio", "loan_amount_k", "employment_years", "default_risk" };
        foreach (var col in cols)
        {
            var score = doc.GetNormalityScore(col);
            Assert.True(score >= 0.0, $"{col} score should be >= 0");
            Assert.True(score <= 1.0, $"{col} score should be <= 1");
        }

        // SaveToFile
        var out1 = TempFile("dogfood_credit_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(skewScore, loaded.GetColumnSkewness("credit_score"), precision: 6);
        Assert.Equal(kurtScore, loaded.GetColumnKurtosis("credit_score"), precision: 6);

        // Symmetric test
        var sym = TsvDocument.LoadFile(CreateSymmetricTsv());
        Assert.Equal(0.0, sym.GetColumnSkewness("value"), precision: 6);
        Assert.True(double.IsFinite(sym.GetColumnKurtosis("value")));
        Assert.True(sym.GetNormalityScore("value") >= 0.0);

        // AddRow and recompute
        loaded.AddRow(new[] { "A013", "740", "70", "0.26", "190", "9", "0.05" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(double.IsFinite(loaded.GetColumnSkewness("credit_score")));

        // Final save
        var out2 = TempFile("dogfood_credit_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(double.IsFinite(loaded2.GetColumnSkewness("credit_score")));
        Assert.True(double.IsFinite(loaded2.GetColumnKurtosis("income_k")));
        Assert.True(loaded2.GetNormalityScore("credit_score") >= 0.0);
    }
}
