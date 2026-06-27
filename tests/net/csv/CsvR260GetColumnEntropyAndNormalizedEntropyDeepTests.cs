// Tests for CsvDocument.GetColumnEntropy, GetColumnNormalizedEntropy deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R260

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R260: Tests for CsvDocument.GetColumnEntropy, GetColumnNormalizedEntropy deeper.
/// GetColumnEntropy(colName): returns Shannon entropy (in bits) of the column's value distribution.
/// GetColumnNormalizedEntropy(colName): returns entropy normalised to [0,1] by log2(uniqueValues).
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant; GetColumnEntropy save-load;
/// GetColumnNormalizedEntropy no-throw; GetColumnNormalizedEntropy in-range;
/// GetColumnNormalizedEntropy zero for constant; GetColumnNormalizedEntropy one for uniform;
/// GetColumnNormalizedEntropy consistent; GetColumnNormalizedEntropy save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnNormalizedEntropy pipeline.
/// </summary>
public class CsvR260GetColumnEntropyAndNormalizedEntropyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR260GetColumnEntropyAndNormalizedEntropyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR260_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("applicant_id,outcome,sector,region,score");
        var rng = new Random(20240820);
        string[] outcomes = { "Approved", "Declined", "Referred", "Withdrawn" };
        string[] sectors = { "Retail", "Hospitality", "Manufacturing", "Tech", "Finance" };
        string[] regions = { "London", "South East", "North West", "Yorkshire", "Scotland" };
        for (int i = 0; i < 100; i++)
        {
            string outcome = outcomes[rng.Next(outcomes.Length)];
            string sector = sectors[i % sectors.Length];
            string region = regions[rng.Next(regions.Length)];
            int score = 300 + rng.Next(600);
            sb.AppendLine($"APP{i:D4},{outcome},{sector},{region},{score}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantCsv()
    {
        var path = TempFile("constant.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,status");
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i},Active");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,quarter");
        string[] quarters = { "Q1", "Q2", "Q3", "Q4" };
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i},{quarters[i % quarters.Length]}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("outcome"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnEntropy("outcome") >= 0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnEntropy("sector"), doc.GetColumnEntropy("sector"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("status"), precision: 8);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnEntropy("outcome");
        var path = TempFile("ent_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("outcome"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalizedEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalizedEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnNormalizedEntropy("outcome"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ne = doc.GetColumnNormalizedEntropy("outcome");
        Assert.True(ne >= 0.0 && ne <= 1.0);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_Zero_ForConstant()
    {
        var doc = CsvDocument.LoadFile(CreateConstantCsv());
        Assert.Equal(0.0, doc.GetColumnNormalizedEntropy("status"), precision: 8);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_One_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        // 4 equally distributed quarters → normalised entropy = 1.0
        Assert.Equal(1.0, doc.GetColumnNormalizedEntropy("quarter"), precision: 8);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnNormalizedEntropy("region");
        var v2 = doc.GetColumnNormalizedEntropy("region");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnNormalizedEntropy("sector");
        var path = TempFile("ne_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnNormalizedEntropy("sector"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnNormalizedEntropy_Pipeline()
    {
        // Financial crime — UK National Crime Agency (NCA) Financial Investigation Unit
        // Suspicious Activity Reports (SARs) metadata for entropy-based category profiling
        // Entropy analysis used to identify dominated vs distributed anomaly types
        var path = TempFile("nca_sar_metadata.csv");
        var sb = new StringBuilder();
        sb.AppendLine("sar_ref,submission_date,reporter_type,sector_code,anomaly_type,risk_tier,amount_gbp,jurisdiction,action_taken");

        var rng = new Random(20241010);
        // Reporter types: banks dominate SARs
        string[] reporterTypes = {
            "Bank", "Bank", "Bank", "Bank", "Bank", "Bank", "Bank",
            "MSB", "MSB", "Accountant", "Solicitor", "Casino", "Estate Agent"
        };
        string[] sectorCodes = { "S0810", "S0820", "S0830", "S0840", "S0850" };
        string[] anomalyTypes = {
            "Structuring", "Structuring", "Structuring",
            "Unusual Cash", "Unusual Cash",
            "Third Party Payment", "Third Party Payment",
            "Unexplained Wealth", "Smurfing", "Trade Finance"
        };
        string[] riskTiers = { "High", "High", "High", "Medium", "Medium", "Low" };
        string[] jurisdictions = {
            "UK", "UK", "UK", "UK", "UK", "UK", "UK", "UK",
            "EU", "EU", "Offshore", "Other"
        };
        string[] actions = {
            "Consent Granted", "Consent Granted", "Consent Granted", "Consent Granted",
            "Consent Granted", "Consent Granted",
            "Consent Refused", "Under Investigation", "NFA"
        };

        for (int i = 0; i < 200; i++)
        {
            string sarRef = $"SAR-2024-{i + 1:D6}";
            string date = $"2024-{(i % 12) + 1:D2}-{(i % 28) + 1:D2}";
            string reporter = reporterTypes[rng.Next(reporterTypes.Length)];
            string sector = sectorCodes[rng.Next(sectorCodes.Length)];
            string anomaly = anomalyTypes[rng.Next(anomalyTypes.Length)];
            string risk = riskTiers[rng.Next(riskTiers.Length)];
            double amount = 1000 + rng.NextDouble() * 499000;
            string jurisdiction = jurisdictions[rng.Next(jurisdictions.Length)];
            string action = actions[rng.Next(actions.Length)];
            sb.AppendLine($"{sarRef},{date},{reporter},{sector},{anomaly},{risk},{amount:F2},{jurisdiction},{action}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnEntropy — reporter_type: banks dominate → low entropy
        var entropyReporter = doc.GetColumnEntropy("reporter_type");
        Assert.True(entropyReporter >= 0);
        Assert.Equal(entropyReporter, doc.GetColumnEntropy("reporter_type")); // consistent

        // anomaly_type: structuring dominates → moderate entropy
        var entropyAnomaly = doc.GetColumnEntropy("anomaly_type");
        Assert.True(entropyAnomaly >= 0);

        // risk_tier: 3 values, high dominates → low-moderate entropy
        var entropyRisk = doc.GetColumnEntropy("risk_tier");
        Assert.True(entropyRisk >= 0);

        // jurisdiction: UK dominates heavily → low entropy
        var entropyJurisdiction = doc.GetColumnEntropy("jurisdiction");
        Assert.True(entropyJurisdiction >= 0);

        // More unique values → more entropy (sectorCodes: 5 uniform → action: 9 non-uniform)
        var entropySector = doc.GetColumnEntropy("sector_code");
        Assert.True(entropySector >= 0);

        // GetColumnNormalizedEntropy
        var neReporter = doc.GetColumnNormalizedEntropy("reporter_type");
        Assert.True(neReporter >= 0.0 && neReporter <= 1.0);

        var neAnomaly = doc.GetColumnNormalizedEntropy("anomaly_type");
        Assert.True(neAnomaly >= 0.0 && neAnomaly <= 1.0);

        var neRisk = doc.GetColumnNormalizedEntropy("risk_tier");
        Assert.True(neRisk >= 0.0 && neRisk <= 1.0);

        // Consistent
        Assert.Equal(neReporter, doc.GetColumnNormalizedEntropy("reporter_type"));
        Assert.Equal(neAnomaly, doc.GetColumnNormalizedEntropy("anomaly_type"));

        // sector_code: 5 nearly-equal categories → near 1.0 normalized entropy
        Assert.True(doc.GetColumnNormalizedEntropy("sector_code") >= 0.0);

        // SaveToFile
        var outPath = TempFile("nca_sar_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(entropyReporter, loaded.GetColumnEntropy("reporter_type"), precision: 8);
        Assert.Equal(neReporter, loaded.GetColumnNormalizedEntropy("reporter_type"), precision: 8);
        Assert.Equal(entropyAnomaly, loaded.GetColumnEntropy("anomaly_type"), precision: 8);

        // Constant column test
        var path2 = TempFile("constant_sar.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("ref,data_type");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"R{i},Suspicious Activity Report");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnEntropy("data_type"), precision: 8);
        Assert.Equal(0.0, doc2.GetColumnNormalizedEntropy("data_type"), precision: 8);
    }
}
