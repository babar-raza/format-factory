// Tests for TsvDocument.GetColumnVariance, GetColumnStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R276

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R276: Tests for TsvDocument.GetColumnVariance, GetColumnStdDev deeper.
/// GetColumnVariance(colName): returns the sample variance of numeric values in the column.
/// GetColumnStdDev(colName): returns the sample standard deviation; equals sqrt(variance).
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance zero for uniform;
/// GetColumnVariance consistent; GetColumnVariance save-load;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev zero for uniform;
/// GetColumnStdDev consistent; GetColumnStdDev save-load;
/// GetColumnVariance equals GetColumnStdDev squared; dogfood pipeline.
/// </summary>
public class TsvR276GetColumnVarianceAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR276GetColumnVarianceAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR276_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 10; i++)
            sb.AppendLine($"{i}\t{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tmeasure");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t42.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnVariance("value") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnVariance("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnVariance("value"), doc.GetColumnVariance("value"));
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnVariance("value");
        var path = TempFile("var_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnVariance("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnStdDev("value") >= 0.0);
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnStdDev("value"), doc.GetColumnStdDev("value"));
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnStdDev("value");
        var path = TempFile("sd_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Equals_StdDev_Squared()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var sd = doc.GetColumnStdDev("value");
        var var_ = doc.GetColumnVariance("value");
        Assert.Equal(sd * sd, var_, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnStdDev_Pipeline()
    {
        // Finance — FCA / PRA: UK Insurance Premium Tax (IPT) and Premium Rate Distribution 2024
        // Insurance premium rate data for FCA supervisory stress testing of underwriting risk
        // Variance and StdDev detect concentration risk and pricing anomalies by insurance class

        var path = TempFile("fca_insurance_premium_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("insurer_id\tinsurer_name\tinsurance_class\tcombined_ratio_pct\tgross_premium_gbpm\tloss_ratio_pct\texpense_ratio_pct\treserve_ratio_pct\tipt_rate_pct\trisk_margin_pct");

        var rng = new Random(20240801);
        string[] insurers = {
            "Aviva_GI", "AXA_Insurance", "Direct_Line", "Admiral_Personal", "RSA_Insurance",
            "Zurich_Insurance", "AIG_UK", "Allianz_Insurance", "Ageas_UK", "NFU_Mutual",
            "Covea_Insurance", "Hastings_Direct", "Sabre_Insurance", "Esure_Group", "Liverpool_Victoria",
            "Ecclesiastical", "Markel_International", "Hiscox_Insurance", "MS_Amlin", "Beazley_UK"
        };
        string[] insuranceClasses = {
            "Motor_Personal", "Household_Property", "Commercial_Property", "Marine_Aviation",
            "Liability_Public", "Health_Medical", "Pet_Insurance", "Travel_Insurance",
            "Engineering_Risk", "Cyber_Insurance"
        };

        for (int i = 0; i < insurers.Length; i++)
        {
            string cls = insuranceClasses[i % insuranceClasses.Length];
            double lossRatio = 55 + rng.NextDouble() * 30;
            double expRatio = 20 + rng.NextDouble() * 15;
            double combined = lossRatio + expRatio;
            double grossPremium = 50 + rng.NextDouble() * 4000;
            double reserveRatio = 80 + rng.NextDouble() * 60;
            double iptRate = cls == "Health_Medical" ? 0 : 12; // standard IPT rate
            double riskMargin = 5 + rng.NextDouble() * 15;

            sb.AppendLine($"FRN{100000 + i}\t{insurers[i]}\t{cls}\t{combined:F1}\t{grossPremium:F0}\t{lossRatio:F1}\t{expRatio:F1}\t{reserveRatio:F1}\t{iptRate:F1}\t{riskMargin:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(20, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Combined ratio variance and StdDev
        var combinedVar = doc.GetColumnVariance("combined_ratio_pct");
        var combinedSd = doc.GetColumnStdDev("combined_ratio_pct");
        Assert.True(combinedVar >= 0.0);
        Assert.True(combinedSd >= 0.0);
        Assert.True(combinedVar > 0.0); // ratios vary across insurers
        Assert.Equal(combinedSd * combinedSd, combinedVar, precision: 4);
        Assert.Equal(combinedVar, doc.GetColumnVariance("combined_ratio_pct")); // consistent
        Assert.Equal(combinedSd, doc.GetColumnStdDev("combined_ratio_pct")); // consistent

        // Loss ratio variance
        var lossVar = doc.GetColumnVariance("loss_ratio_pct");
        var lossSd = doc.GetColumnStdDev("loss_ratio_pct");
        Assert.True(lossVar >= 0.0);
        Assert.Equal(lossSd * lossSd, lossVar, precision: 4);

        // Gross premium variance (should be substantial)
        var premVar = doc.GetColumnVariance("gross_premium_gbpm");
        var premSd = doc.GetColumnStdDev("gross_premium_gbpm");
        Assert.True(premVar >= 0.0);
        Assert.Equal(premSd * premSd, premVar, precision: 2);

        // Risk margin variance
        var riskVar = doc.GetColumnVariance("risk_margin_pct");
        Assert.True(riskVar >= 0.0);

        // SaveToFile
        var outPath = TempFile("fca_insurance_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(combinedVar, loaded.GetColumnVariance("combined_ratio_pct"), precision: 6);
        Assert.Equal(combinedSd, loaded.GetColumnStdDev("combined_ratio_pct"), precision: 6);
        Assert.Equal(lossVar, loaded.GetColumnVariance("loss_ratio_pct"), precision: 6);
        Assert.Equal(premSd, loaded.GetColumnStdDev("gross_premium_gbpm"), precision: 3);
    }
}
