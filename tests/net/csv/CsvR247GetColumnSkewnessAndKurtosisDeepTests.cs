// Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnMoment deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R247: Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetColumnMoment deeper.
/// GetColumnSkewness(columnName): returns the sample skewness of numeric values in the column.
/// GetColumnKurtosis(columnName): returns the sample excess kurtosis (Kurt − 3) of numeric values.
/// GetColumnMoment(columnName, order): returns the sample central moment of the given order.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness consistent;
/// GetColumnSkewness zero for symmetric data;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnKurtosis negative for uniform distribution;
/// GetColumnMoment no-throw; GetColumnMoment zero for first moment; GetColumnMoment consistent;
/// GetColumnMoment save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetColumnMoment pipeline.
/// </summary>
public class CsvR247GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR247GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateIncomeCsv()
    {
        var path = TempFile("incomes.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "household_id,region,gross_income,net_income,num_earners",
            "H001,North_West,28500,23100,1",
            "H002,London,52000,39800,2",
            "H003,South_East,41000,32500,1",
            "H004,Yorkshire,24800,20400,1",
            "H005,London,87000,61200,2",
            "H006,Midlands,32000,26100,2",
            "H007,Scotland,29500,24000,1",
            "H008,London,135000,88000,2",
            "H009,South_West,38000,30500,1",
            "H010,North_East,22000,18600,1",
            "H011,London,220000,140000,2",
            "H012,Midlands,34500,27800,2",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateSymmetricCsv()
    {
        var path = TempFile("symmetric.csv");
        var lines = new string[]
        {
            "id,value",
            "1,-3",
            "2,-2",
            "3,-1",
            "4,0",
            "5,1",
            "6,2",
            "7,3",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("gross_income"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.True(double.IsFinite(doc.GetColumnSkewness("gross_income")));
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.Equal(doc.GetColumnSkewness("gross_income"), doc.GetColumnSkewness("gross_income"));
    }

    [Fact]
    public void GetColumnSkewness_Zero_For_Symmetric()
    {
        var doc = CsvDocument.LoadFile(CreateSymmetricCsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("gross_income"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("gross_income")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.Equal(doc.GetColumnKurtosis("net_income"), doc.GetColumnKurtosis("net_income"));
    }

    [Fact]
    public void GetColumnKurtosis_Negative_For_Uniform_Like()
    {
        var doc = CsvDocument.LoadFile(CreateSymmetricCsv());
        var kurt = doc.GetColumnKurtosis("value");
        Assert.True(double.IsFinite(kurt));
        Assert.True(kurt < 0); // uniform-like has negative excess kurtosis
    }

    // -------------------------------------------------------------------------
    // GetColumnMoment
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMoment_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        var ex = Record.Exception(() => doc.GetColumnMoment("gross_income", 2));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMoment_First_Moment_Zero()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.Equal(0.0, doc.GetColumnMoment("gross_income", 1), precision: 6);
    }

    [Fact]
    public void GetColumnMoment_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        Assert.Equal(doc.GetColumnMoment("net_income", 2), doc.GetColumnMoment("net_income", 2));
    }

    [Fact]
    public void GetColumnMoment_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeCsv());
        var before = doc.GetColumnMoment("gross_income", 2);
        var path = TempFile("moment_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMoment("gross_income", 2), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetColumnMoment_Pipeline()
    {
        // Insurance — motor third party liability claims distribution analysis
        var path = TempFile("motor_claims.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("claim_id,policy_type,claim_amount_gbp,injury_claim_gbp,repair_cost_gbp,settlement_days,at_fault");
        var rng = new Random(20240701);
        string[] policyTypes = { "Third_Party", "Third_Party_Fire_Theft", "Comprehensive" };
        for (int i = 0; i < 150; i++)
        {
            // Claims are right-skewed: most are moderate, some are very large
            double claimBase = Math.Exp(6 + rng.NextDouble() * 3); // £400–£160K
            double injuryFrac = rng.NextDouble() < 0.3 ? rng.NextDouble() * 0.6 : 0;
            double injuryClaim = claimBase * injuryFrac;
            double repairCost = claimBase * (1 - injuryFrac * 0.5);
            int settleDays = (int)(10 + Math.Exp(rng.NextDouble() * 4));
            int atFault = rng.NextDouble() < 0.4 ? 1 : 0;
            string pType = policyTypes[i % 3];
            csvLines.Add($"CLM{i:D5},{pType},{claimBase:F0},{injuryClaim:F0},{repairCost:F0},{settleDays},{atFault}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);

        // GetColumnSkewness — claim_amount_gbp (expect positive skew)
        var claimSkew = doc.GetColumnSkewness("claim_amount_gbp");
        Assert.True(double.IsFinite(claimSkew));
        Assert.Equal(claimSkew, doc.GetColumnSkewness("claim_amount_gbp")); // consistent

        // GetColumnSkewness — settlement_days (also right-skewed)
        var daysSkew = doc.GetColumnSkewness("settlement_days");
        Assert.True(double.IsFinite(daysSkew));

        // GetColumnKurtosis — claim_amount_gbp (heavy tail, positive kurtosis expected)
        var claimKurt = doc.GetColumnKurtosis("claim_amount_gbp");
        Assert.True(double.IsFinite(claimKurt));
        Assert.Equal(claimKurt, doc.GetColumnKurtosis("claim_amount_gbp")); // consistent

        // GetColumnKurtosis — repair_cost_gbp
        var repairKurt = doc.GetColumnKurtosis("repair_cost_gbp");
        Assert.True(double.IsFinite(repairKurt));

        // GetColumnMoment — 2nd central moment (variance)
        var claimVar = doc.GetColumnMoment("claim_amount_gbp", 2);
        Assert.True(claimVar > 0);
        Assert.Equal(claimVar, doc.GetColumnMoment("claim_amount_gbp", 2)); // consistent

        // GetColumnMoment — 1st central moment = 0
        Assert.Equal(0.0, doc.GetColumnMoment("claim_amount_gbp", 1), precision: 6);

        // GetColumnMoment — 3rd central moment
        var m3 = doc.GetColumnMoment("claim_amount_gbp", 3);
        Assert.True(double.IsFinite(m3));

        // All numeric columns
        foreach (var col in new[] { "claim_amount_gbp", "injury_claim_gbp", "repair_cost_gbp", "settlement_days" })
        {
            Assert.True(double.IsFinite(doc.GetColumnSkewness(col)));
            Assert.True(double.IsFinite(doc.GetColumnKurtosis(col)));
            Assert.Equal(0.0, doc.GetColumnMoment(col, 1), precision: 6);
        }

        // SaveToFile
        var outPath = TempFile("motor_claims_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(claimSkew, loaded.GetColumnSkewness("claim_amount_gbp"), precision: 6);
        Assert.Equal(claimKurt, loaded.GetColumnKurtosis("claim_amount_gbp"), precision: 6);
        Assert.Equal(claimVar, loaded.GetColumnMoment("claim_amount_gbp", 2), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // Additional stats
        var meanClaim = doc.GetColumnMean("claim_amount_gbp");
        Assert.True(meanClaim > 0);
        var maxClaim = doc.GetColumnMax("claim_amount_gbp");
        Assert.True(maxClaim >= meanClaim);
    }
}
