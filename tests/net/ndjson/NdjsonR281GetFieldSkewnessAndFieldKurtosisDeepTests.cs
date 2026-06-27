// Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R281

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R281: Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
/// GetFieldSkewness(field): returns the skewness of the numeric value distribution in the named field.
/// GetFieldKurtosis(field): returns the kurtosis of the numeric value distribution in the named field.
/// Covers: GetFieldSkewness no-throw; GetFieldSkewness finite; GetFieldSkewness zero for uniform;
/// GetFieldSkewness consistent; GetFieldSkewness save-load;
/// GetFieldKurtosis no-throw; GetFieldKurtosis finite;
/// GetFieldKurtosis consistent; GetFieldKurtosis save-load;
/// dogfood pipeline.
/// </summary>
public class NdjsonR281GetFieldSkewnessAndFieldKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR281GetFieldSkewnessAndFieldKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR281_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":{i * 5.0}}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":42.0}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSkewness_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldSkewness("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSkewness_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sk = doc.GetFieldSkewness("value");
        Assert.True(!double.IsNaN(sk) && !double.IsInfinity(sk));
    }

    [Fact]
    public void GetFieldSkewness_Zero_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(0.0, doc.GetFieldSkewness("score"), precision: 6);
    }

    [Fact]
    public void GetFieldSkewness_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldSkewness("value"), doc.GetFieldSkewness("value"));
    }

    [Fact]
    public void GetFieldSkewness_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldSkewness("value");
        var path = TempFile("sk_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldKurtosis_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldKurtosis("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldKurtosis_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var kurt = doc.GetFieldKurtosis("value");
        Assert.True(!double.IsNaN(kurt) && !double.IsInfinity(kurt));
    }

    [Fact]
    public void GetFieldKurtosis_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldKurtosis("value"), doc.GetFieldKurtosis("value"));
    }

    [Fact]
    public void GetFieldKurtosis_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldKurtosis("value");
        var path = TempFile("kurt_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldKurtosis("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldSkewness_GetFieldKurtosis_Pipeline()
    {
        // Finance — PRA / BoE: Insurance Sector Solvency Capital Requirement Data
        // Solvency II SCR component distribution across UK insurance firms
        // Skewness/kurtosis of SCR distributions detect capital concentration risk

        var path = TempFile("pra_solvency_ii_scr_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240630);

        string[] firms = {
            "Aviva_UK", "Legal_General", "Prudential_UK", "Standard_Life", "Scottish_Widows",
            "AXA_UK", "Zurich_UK", "RSA_Insurance", "Direct_Line", "Admiral_Group",
            "Hiscox_UK", "Beazley", "QBE_UK", "Markel_UK", "Chaucer",
            "Munich_Re_UK", "Swiss_Re_UK", "Hannover_Re_UK", "Tokio_Marine_HCC", "Liberty_Mutual_UK"
        };
        string[] firmTypes = {
            "Life_Composite", "Life_Composite", "Life_Composite", "Life_Composite", "Life_Composite",
            "Non_Life", "Life_Composite", "Non_Life", "Non_Life", "Non_Life",
            "Specialty", "Specialty", "Specialty", "Specialty", "Specialty",
            "Reinsurance", "Reinsurance", "Reinsurance", "Reinsurance", "Reinsurance"
        };

        for (int i = 0; i < firms.Length; i++)
        {
            // SCR components (GBP millions)
            double marketRisk = 800 + rng.NextDouble() * 4000 + (i < 5 ? 2000 : 0); // life composites larger
            double creditRisk = 200 + rng.NextDouble() * 800;
            double underwritingRisk = 150 + rng.NextDouble() * 600 + (i >= 10 && i < 15 ? 300 : 0); // specialty
            double opRisk = 50 + rng.NextDouble() * 200;
            double totalScr = marketRisk + creditRisk + underwritingRisk + opRisk;
            double scrCoverage = 140 + rng.NextDouble() * 100 + (i == 3 ? 80 : 0); // outlier high coverage
            double tierOneCapital = totalScr * (scrCoverage / 100.0);
            double lossAbsorbency = -0.15 - rng.NextDouble() * 0.3; // negative tax benefit

            sb.AppendLine($"{{\"firm_id\":\"FRN{i:D5}\",\"firm_name\":\"{firms[i]}\"," +
                          $"\"firm_type\":\"{firmTypes[i]}\"," +
                          $"\"market_risk_scr_gbpm\":{marketRisk:F1}," +
                          $"\"credit_risk_scr_gbpm\":{creditRisk:F1}," +
                          $"\"underwriting_risk_scr_gbpm\":{underwritingRisk:F1}," +
                          $"\"operational_risk_scr_gbpm\":{opRisk:F1}," +
                          $"\"total_scr_gbpm\":{totalScr:F1}," +
                          $"\"scr_coverage_ratio_pct\":{scrCoverage:F1}," +
                          $"\"tier1_capital_gbpm\":{tierOneCapital:F1}," +
                          $"\"loss_absorbency_factor\":{lossAbsorbency:F3}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(firms.Length, doc.RecordCount);

        // Total SCR skewness and kurtosis (right-skewed: large life composites)
        var scrSkew = doc.GetFieldSkewness("total_scr_gbpm");
        var scrKurt = doc.GetFieldKurtosis("total_scr_gbpm");
        Assert.True(!double.IsNaN(scrSkew) && !double.IsInfinity(scrSkew));
        Assert.True(!double.IsNaN(scrKurt) && !double.IsInfinity(scrKurt));
        Assert.Equal(scrSkew, doc.GetFieldSkewness("total_scr_gbpm")); // consistent
        Assert.Equal(scrKurt, doc.GetFieldKurtosis("total_scr_gbpm")); // consistent

        // SCR coverage ratio skewness
        var covSkew = doc.GetFieldSkewness("scr_coverage_ratio_pct");
        var covKurt = doc.GetFieldKurtosis("scr_coverage_ratio_pct");
        Assert.True(!double.IsNaN(covSkew) && !double.IsInfinity(covSkew));
        Assert.True(!double.IsNaN(covKurt) && !double.IsInfinity(covKurt));

        // Market risk SCR skewness (dominated by life composites)
        var mktSkew = doc.GetFieldSkewness("market_risk_scr_gbpm");
        var mktKurt = doc.GetFieldKurtosis("market_risk_scr_gbpm");
        Assert.True(!double.IsNaN(mktSkew) && !double.IsInfinity(mktSkew));
        Assert.True(!double.IsNaN(mktKurt) && !double.IsInfinity(mktKurt));

        // Loss absorbency factor (negative values — check skewness finite)
        var lafSkew = doc.GetFieldSkewness("loss_absorbency_factor");
        Assert.True(!double.IsNaN(lafSkew) && !double.IsInfinity(lafSkew));

        // SaveToFile
        var outPath = TempFile("pra_solvency_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(scrSkew, loaded.GetFieldSkewness("total_scr_gbpm"), precision: 6);
        Assert.Equal(scrKurt, loaded.GetFieldKurtosis("total_scr_gbpm"), precision: 6);
        Assert.Equal(covSkew, loaded.GetFieldSkewness("scr_coverage_ratio_pct"), precision: 6);
        Assert.Equal(mktKurt, loaded.GetFieldKurtosis("market_risk_scr_gbpm"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldSkewness("total_scr_gbpm"));
        var ex2 = Record.Exception(() => loaded.GetFieldKurtosis("scr_coverage_ratio_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
