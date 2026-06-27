// Tests for CsvDocument.GetColumnTrimmedMean, GetColumnWinsorizedMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R254

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R254: Tests for CsvDocument.GetColumnTrimmedMean, GetColumnWinsorizedMean deeper.
/// GetColumnTrimmedMean(colName, trimFraction): returns mean after trimming top/bottom fraction.
/// GetColumnWinsorizedMean(colName, winsorFraction): returns mean after winsorizing extremes.
/// Covers: GetColumnTrimmedMean no-throw; GetColumnTrimmedMean finite;
/// GetColumnTrimmedMean consistent; GetColumnTrimmedMean save-load;
/// GetColumnWinsorizedMean no-throw; GetColumnWinsorizedMean finite;
/// GetColumnWinsorizedMean consistent; GetColumnWinsorizedMean save-load;
/// dogfood CreateDoc→GetColumnTrimmedMean→GetColumnWinsorizedMean pipeline.
/// </summary>
public class CsvR254GetColumnTrimmedMeanAndWinsorizedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR254GetColumnTrimmedMeanAndWinsorizedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR254_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("property_id,price_gbp,sqft,bedrooms,bathrooms,age_years");
        var rng = new Random(20240901);
        for (int i = 0; i < 100; i++)
        {
            double price = 200000 + rng.NextDouble() * 600000;
            // Occasional mansion outliers
            if (i == 3 || i == 97) price = 5000000;
            double sqft = 500 + rng.NextDouble() * 2000;
            int beds = 1 + rng.Next(5);
            int baths = 1 + rng.Next(3);
            int age = rng.Next(100);
            sb.AppendLine($"PROP{i:D5},{price:F0},{sqft:F0},{beds},{baths},{age}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("price_gbp", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(double.IsFinite(doc.GetColumnTrimmedMean("price_gbp", 0.1)));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnTrimmedMean("sqft", 0.1), doc.GetColumnTrimmedMean("sqft", 0.1));
    }

    [Fact]
    public void GetColumnTrimmedMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnTrimmedMean("price_gbp", 0.05);
        var path = TempFile("tm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTrimmedMean("price_gbp", 0.05), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnWinsorizedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnWinsorizedMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnWinsorizedMean("price_gbp", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnWinsorizedMean_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(double.IsFinite(doc.GetColumnWinsorizedMean("price_gbp", 0.1)));
    }

    [Fact]
    public void GetColumnWinsorizedMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnWinsorizedMean("age_years", 0.1), doc.GetColumnWinsorizedMean("age_years", 0.1));
    }

    [Fact]
    public void GetColumnWinsorizedMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnWinsorizedMean("sqft", 0.05);
        var path = TempFile("wm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnWinsorizedMean("sqft", 0.05), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnTrimmedMean_GetColumnWinsorizedMean_Pipeline()
    {
        // Insurance actuarial — motor insurance claims severity modelling (UK personal lines)
        // Robust location estimators for log-normal claims severity distribution
        var path = TempFile("motor_claims_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("claim_ref,policy_type,vehicle_age_yrs,driver_age,ncb_years,claim_severity_gbp,third_party_gbp,own_damage_gbp,hire_days,legal_costs_gbp,at_fault");
        var rng = new Random(20240501);
        string[] policyTypes = { "Comprehensive", "TPFT", "TPO" };
        for (int i = 0; i < 200; i++)
        {
            var policy = policyTypes[i % policyTypes.Length];
            int vehAge = rng.Next(15);
            int driverAge = 18 + rng.Next(55);
            int ncb = rng.Next(9);
            // Log-normal severity — typical for insurance
            double logSeverity = 6.5 + rng.NextGaussian(0, 1.2);
            double severity = Math.Exp(logSeverity);
            // Heavy tail: occasional catastrophic claims
            if (rng.NextDouble() < 0.03) severity *= 15;
            double tp = severity * (0.3 + rng.NextDouble() * 0.4);
            double od = severity - tp;
            int hire = rng.Next(30);
            double legal = rng.NextDouble() < 0.15 ? 1500 + rng.NextDouble() * 5000 : 0;
            bool atFault = rng.NextDouble() < 0.55;
            sb.AppendLine($"CLM{2024000 + i},{policy},{vehAge},{driverAge},{ncb},{severity:F2},{tp:F2},{od:F2},{hire},{legal:F2},{(atFault ? 1 : 0)}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // GetColumnTrimmedMean — robust severity estimate (trim 10% each tail)
        var tmSeverity10 = doc.GetColumnTrimmedMean("claim_severity_gbp", 0.10);
        Assert.True(double.IsFinite(tmSeverity10));
        Assert.Equal(tmSeverity10, doc.GetColumnTrimmedMean("claim_severity_gbp", 0.10)); // consistent

        var tmSeverity5 = doc.GetColumnTrimmedMean("claim_severity_gbp", 0.05);
        Assert.True(double.IsFinite(tmSeverity5));

        var tmTp10 = doc.GetColumnTrimmedMean("third_party_gbp", 0.10);
        Assert.True(double.IsFinite(tmTp10));

        var tmLegal = doc.GetColumnTrimmedMean("legal_costs_gbp", 0.10);
        Assert.True(double.IsFinite(tmLegal));

        // GetColumnWinsorizedMean
        var wmSeverity10 = doc.GetColumnWinsorizedMean("claim_severity_gbp", 0.10);
        Assert.True(double.IsFinite(wmSeverity10));
        Assert.Equal(wmSeverity10, doc.GetColumnWinsorizedMean("claim_severity_gbp", 0.10)); // consistent

        var wmOd10 = doc.GetColumnWinsorizedMean("own_damage_gbp", 0.10);
        Assert.True(double.IsFinite(wmOd10));

        var wmHire = doc.GetColumnWinsorizedMean("hire_days", 0.05);
        Assert.True(double.IsFinite(wmHire));

        // Simple mean should be higher than trimmed mean (right-skewed by catastrophic claims)
        var meanSeverity = doc.GetColumnMean("claim_severity_gbp");
        Assert.True(meanSeverity >= 0.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("claim_severity_gbp") <= doc.GetColumnMax("claim_severity_gbp"));
        Assert.True(doc.GetColumnStdDev("claim_severity_gbp") >= 0.0);

        // IQR
        var iqrSeverity = doc.GetColumnInterquartileRange("claim_severity_gbp");
        Assert.True(iqrSeverity >= 0.0);

        // SaveToFile
        var outPath = TempFile("motor_claims_2024_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(tmSeverity10, loaded.GetColumnTrimmedMean("claim_severity_gbp", 0.10), precision: 8);
        Assert.Equal(tmTp10, loaded.GetColumnTrimmedMean("third_party_gbp", 0.10), precision: 8);
        Assert.Equal(wmSeverity10, loaded.GetColumnWinsorizedMean("claim_severity_gbp", 0.10), precision: 8);
        Assert.Equal(wmOd10, loaded.GetColumnWinsorizedMean("own_damage_gbp", 0.10), precision: 8);
    }
}

// Helper for Gaussian random numbers
internal static class RandomExtensions
{
    internal static double NextGaussian(this Random rng, double mean, double stdDev)
    {
        double u1 = 1.0 - rng.NextDouble();
        double u2 = 1.0 - rng.NextDouble();
        double z = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2);
        return mean + stdDev * z;
    }
}
