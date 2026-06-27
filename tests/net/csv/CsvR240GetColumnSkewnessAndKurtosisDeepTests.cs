// Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R240

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R240: Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnStdDev deeper.
/// GetColumnSkewness(columnName): returns the skewness of numeric values in the column.
/// GetColumnKurtosis(columnName): returns the excess kurtosis of numeric values in the column.
/// GetColumnStdDev(columnName): returns the standard deviation of numeric values in the column.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness consistent;
/// GetColumnSkewness near-zero for symmetric data;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev consistent;
/// GetColumnStdDev zero for constant; GetColumnStdDev save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetColumnStdDev pipeline.
/// </summary>
public class CsvR240GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR240GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR240_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateInsuranceClaims()
    {
        var path = TempFile("claims.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "claim_id,policy_type,claim_amount,processing_days,fraud_score,settlement_ratio",
            "CLM001,Motor,2400,12,0.12,0.88",
            "CLM002,Property,85000,45,0.03,0.92",
            "CLM003,Motor,650,5,0.08,0.95",
            "CLM004,Liability,12000,30,0.25,0.75",
            "CLM005,Motor,3200,15,0.15,0.82",
            "CLM006,Property,145000,60,0.01,0.97",
            "CLM007,Health,8500,20,0.05,0.91",
            "CLM008,Motor,950,7,0.09,0.93",
            "CLM009,Liability,35000,40,0.31,0.68",
            "CLM010,Property,22000,35,0.07,0.89",
            "CLM011,Health,4200,18,0.11,0.87",
            "CLM012,Motor,1800,10,0.06,0.94",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        File.WriteAllLines(path, new[]
        {
            "id,score,label",
            "A1,100,X",
            "A2,100,Y",
            "A3,100,X",
            "A4,100,Z",
            "A5,100,X",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        var ex = Record.Exception(() => doc.GetColumnSkewness("claim_amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        var skew = doc.GetColumnSkewness("claim_amount");
        Assert.True(double.IsFinite(skew));
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        Assert.Equal(doc.GetColumnSkewness("fraud_score"), doc.GetColumnSkewness("fraud_score"));
    }

    [Fact]
    public void GetColumnSkewness_NearZero_ForSymmetricData()
    {
        var path = TempFile("symmetric.csv");
        File.WriteAllLines(path, new[]
        {
            "id,value",
            "A,-4",
            "B,-2",
            "C,-1",
            "D,0",
            "E,1",
            "F,2",
            "G,4",
        });
        var doc = CsvDocument.LoadFile(path);
        var skew = doc.GetColumnSkewness("value");
        Assert.True(Math.Abs(skew) < 0.5);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("claim_amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("claim_amount")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        Assert.Equal(doc.GetColumnKurtosis("settlement_ratio"), doc.GetColumnKurtosis("settlement_ratio"));
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        var ex = Record.Exception(() => doc.GetColumnStdDev("claim_amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        Assert.True(doc.GetColumnStdDev("claim_amount") >= 0);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        Assert.Equal(doc.GetColumnStdDev("processing_days"), doc.GetColumnStdDev("processing_days"));
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForConstantColumn()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("score"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInsuranceClaims());
        var before = doc.GetColumnStdDev("fraud_score");
        var path = TempFile("sd_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnStdDev("fraud_score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetColumnStdDev_Pipeline()
    {
        // Actuarial — individual life insurance mortality experience study
        var path = TempFile("mortality_experience.csv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("policy_id,age_at_issue,sum_assured,smoker_flag,bmi,policy_year,actual_deaths,expected_deaths,ae_ratio");
        var rng = new Random(20240601);
        for (int i = 0; i < 120; i++)
        {
            int age = 25 + (i % 45);
            double sa = 100000 + rng.Next(0, 900000);
            int smoker = rng.NextDouble() < 0.18 ? 1 : 0;
            double bmi = 18.5 + rng.NextDouble() * 22.0;
            int year = 1 + (i % 20);
            int actual = rng.NextDouble() < 0.02 ? 1 : 0;
            double expected = 0.005 + (age - 25) * 0.0003 + smoker * 0.002;
            double ae = actual == 0 ? 0.0 : actual / expected;
            lines.Add($"POL{i:D5},{age},{sa:F0},{smoker},{bmi:F1},{year},{actual},{expected:F4},{ae:F2}");
        }
        File.WriteAllLines(path, lines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnStdDev
        var ageStd = doc.GetColumnStdDev("age_at_issue");
        Assert.True(ageStd > 0);
        var bmiStd = doc.GetColumnStdDev("bmi");
        Assert.True(bmiStd > 0);
        var saStd = doc.GetColumnStdDev("sum_assured");
        Assert.True(saStd > ageStd); // sum assured has much higher variance
        Assert.Equal(ageStd, doc.GetColumnStdDev("age_at_issue")); // consistent

        // GetColumnSkewness
        var saSkew = doc.GetColumnSkewness("sum_assured");
        Assert.True(double.IsFinite(saSkew));
        var bmiSkew = doc.GetColumnSkewness("bmi");
        Assert.True(double.IsFinite(bmiSkew));
        Assert.Equal(saSkew, doc.GetColumnSkewness("sum_assured")); // consistent

        // GetColumnKurtosis
        var saKurt = doc.GetColumnKurtosis("sum_assured");
        Assert.True(double.IsFinite(saKurt));
        var aeKurt = doc.GetColumnKurtosis("ae_ratio");
        Assert.True(double.IsFinite(aeKurt));
        Assert.Equal(saKurt, doc.GetColumnKurtosis("sum_assured")); // consistent

        // Verify all numeric columns
        foreach (var col in new[] { "age_at_issue", "sum_assured", "bmi", "expected_deaths" })
        {
            Assert.True(doc.GetColumnStdDev(col) >= 0);
            Assert.True(double.IsFinite(doc.GetColumnSkewness(col)));
            Assert.True(double.IsFinite(doc.GetColumnKurtosis(col)));
        }

        // SaveToFile
        var outPath = TempFile("mortality_experience_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(ageStd, loaded.GetColumnStdDev("age_at_issue"), precision: 6);
        Assert.True(double.IsFinite(loaded.GetColumnSkewness("sum_assured")));
        Assert.True(double.IsFinite(loaded.GetColumnKurtosis("bmi")));
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Mean/min/max consistency with StdDev
        var mean = doc.GetColumnMean("age_at_issue");
        var min = doc.GetColumnMin("age_at_issue");
        var max = doc.GetColumnMax("age_at_issue");
        var std = doc.GetColumnStdDev("age_at_issue");
        Assert.True(mean >= min);
        Assert.True(mean <= max);
        Assert.True(std <= (max - min));
    }
}
