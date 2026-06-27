// Tests for NdjsonDocument.GetFieldTypeConsistency, GetFieldTypeDistribution deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R257

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R257: Tests for NdjsonDocument.GetFieldTypeConsistency, GetFieldTypeDistribution deeper.
/// GetFieldTypeConsistency(fieldName): returns fraction of non-null records where the field has the dominant type.
/// GetFieldTypeDistribution(fieldName): returns a dictionary mapping type names to counts.
/// Covers: GetFieldTypeConsistency no-throw; GetFieldTypeConsistency in [0,1]; GetFieldTypeConsistency consistent;
/// GetFieldTypeConsistency one for uniform type;
/// GetFieldTypeDistribution no-throw; GetFieldTypeDistribution non-null; GetFieldTypeDistribution consistent;
/// GetFieldTypeDistribution sum equals present count; GetFieldTypeDistribution save-load;
/// dogfood CreateDoc→GetFieldTypeConsistency→GetFieldTypeDistribution pipeline.
/// </summary>
public class NdjsonR257GetFieldTypeConsistencyAndTypeDistributionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR257GetFieldTypeConsistencyAndTypeDistributionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR257_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformTypedNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{i * 2.5:F2},\"label\":\"item_{i}\",\"active\":{(i % 2 == 0 ? "true" : "false")}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateMixedTypedNdjson()
    {
        var path = TempFile("mixed.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(66);
        for (int i = 0; i < 50; i++)
        {
            // 'score' field: 80% numeric, 20% string ("N/A")
            string scoreVal = rng.Next(5) == 0 ? "\"N/A\"" : $"{(50 + rng.NextDouble() * 50.0):F1}";
            sb.AppendLine($"{{\"id\":{i},\"name\":\"rec_{i}\",\"score\":{scoreVal}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldTypeConsistency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTypeConsistency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var ex = Record.Exception(() => doc.GetFieldTypeConsistency("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTypeConsistency_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var c = doc.GetFieldTypeConsistency("value");
        Assert.True(c >= 0.0 && c <= 1.0);
    }

    [Fact]
    public void GetFieldTypeConsistency_One_ForUniformType()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        Assert.Equal(1.0, doc.GetFieldTypeConsistency("value"), precision: 6);
    }

    [Fact]
    public void GetFieldTypeConsistency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedTypedNdjson());
        Assert.Equal(doc.GetFieldTypeConsistency("score"), doc.GetFieldTypeConsistency("score"));
    }

    [Fact]
    public void GetFieldTypeConsistency_LessThanOne_ForMixed()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedTypedNdjson());
        Assert.True(doc.GetFieldTypeConsistency("score") < 1.0);
    }

    // -------------------------------------------------------------------------
    // GetFieldTypeDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTypeDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var ex = Record.Exception(() => doc.GetFieldTypeDistribution("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTypeDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        Assert.NotNull(doc.GetFieldTypeDistribution("value"));
    }

    [Fact]
    public void GetFieldTypeDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var d1 = doc.GetFieldTypeDistribution("label");
        var d2 = doc.GetFieldTypeDistribution("label");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetFieldTypeDistribution_Sum_Equals_PresentCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var dist = doc.GetFieldTypeDistribution("value");
        int total = 0;
        foreach (var kv in dist) total += kv.Value;
        var presentCount = (int)Math.Round(doc.GetFieldPresentRate("value") * doc.RecordCount);
        Assert.Equal(presentCount, total);
    }

    [Fact]
    public void GetFieldTypeDistribution_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformTypedNdjson());
        var before = doc.GetFieldTypeDistribution("value");
        var path = TempFile("ftd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetFieldTypeDistribution("value");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldTypeConsistency_GetFieldTypeDistribution_Pipeline()
    {
        // Financial services — regulatory transaction monitoring data (AML/KYC raw feed)
        var path = TempFile("aml_transaction_feed.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20250301);
        string[] currencies = { "GBP", "EUR", "USD", "CHF", "JPY" };
        string[] txnTypes = { "WIRE", "SEPA", "CHAPS", "ACH", "SWIFT" };
        string[] riskLevels = { "LOW", "MEDIUM", "HIGH", "CRITICAL" };

        int totalRecords = 150;
        for (int i = 0; i < totalRecords; i++)
        {
            var parts = new System.Collections.Generic.List<string>
            {
                $"\"txn_id\":\"TXN{i:D8}\"",
                $"\"timestamp\":\"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}T{rng.Next(24):D2}:{rng.Next(60):D2}:00Z\"",
                $"\"amount\":{(100 + rng.NextDouble() * 499900):F2}",
                $"\"currency\":\"{currencies[rng.Next(currencies.Length)]}\"",
                $"\"txn_type\":\"{txnTypes[rng.Next(txnTypes.Length)]}\"",
            };

            // amount_eur: 85% numeric, 15% string ("PENDING_FX") — mixed type
            if (rng.Next(100) < 85)
                parts.Add($"\"amount_eur\":{(100 + rng.NextDouble() * 499900):F2}");
            else
                parts.Add("\"amount_eur\":\"PENDING_FX\"");

            // risk_score: 70% numeric, 20% string label, 10% null
            int rs = rng.Next(10);
            if (rs < 7)
                parts.Add($"\"risk_score\":{rng.NextDouble() * 100.0:F3}");
            else if (rs < 9)
                parts.Add($"\"risk_score\":\"{riskLevels[rng.Next(riskLevels.Length)]}\"");
            else
                parts.Add("\"risk_score\":null");

            // risk_level: always string (uniform type)
            parts.Add($"\"risk_level\":\"{riskLevels[rng.Next(riskLevels.Length)]}\"");

            // account_id: always integer (uniform type)
            parts.Add($"\"account_id\":{100000 + rng.Next(899999)}");

            // flag: always boolean (uniform type)
            parts.Add($"\"flag\":{(rng.Next(10) < 2 ? "true" : "false")}");

            sb.AppendLine("{" + string.Join(",", parts) + "}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(totalRecords, doc.RecordCount);

        // GetFieldTypeConsistency — uniform fields
        var consistencyAmount = doc.GetFieldTypeConsistency("amount");
        Assert.Equal(1.0, consistencyAmount, precision: 6); // amount is always numeric
        Assert.Equal(consistencyAmount, doc.GetFieldTypeConsistency("amount")); // consistent

        var consistencyRiskLevel = doc.GetFieldTypeConsistency("risk_level");
        Assert.Equal(1.0, consistencyRiskLevel, precision: 6); // always string

        var consistencyFlag = doc.GetFieldTypeConsistency("flag");
        Assert.Equal(1.0, consistencyFlag, precision: 6); // always boolean

        // GetFieldTypeConsistency — mixed fields
        var consistencyAmountEur = doc.GetFieldTypeConsistency("amount_eur");
        Assert.True(consistencyAmountEur >= 0.0 && consistencyAmountEur <= 1.0);
        Assert.True(consistencyAmountEur < 1.0); // has PENDING_FX strings

        var consistencyRiskScore = doc.GetFieldTypeConsistency("risk_score");
        Assert.True(consistencyRiskScore >= 0.0 && consistencyRiskScore <= 1.0);
        Assert.True(consistencyRiskScore < 1.0); // mixed numeric/string

        // GetFieldTypeDistribution
        var distAmount = doc.GetFieldTypeDistribution("amount");
        Assert.NotNull(distAmount);
        Assert.True(distAmount.Count >= 1);
        // Sum should equal record count (amount always present)
        int totalAmount = 0;
        foreach (var kv in distAmount) totalAmount += kv.Value;
        Assert.Equal(totalRecords, totalAmount);

        var distRiskLevel = doc.GetFieldTypeDistribution("risk_level");
        Assert.NotNull(distRiskLevel);
        int totalRl = 0;
        foreach (var kv in distRiskLevel) totalRl += kv.Value;
        Assert.Equal(totalRecords, totalRl);
        Assert.Equal(distRiskLevel.Count, doc.GetFieldTypeDistribution("risk_level").Count); // consistent

        var distAmountEur = doc.GetFieldTypeDistribution("amount_eur");
        Assert.NotNull(distAmountEur);
        // Should have at least 2 types (number + string)
        Assert.True(distAmountEur.Count >= 2);

        var distRiskScore = doc.GetFieldTypeDistribution("risk_score");
        Assert.NotNull(distRiskScore);
        // Has number, string, and null variants
        int totalRs = 0;
        foreach (var kv in distRiskScore) totalRs += kv.Value;
        Assert.True(totalRs <= totalRecords);

        // Field stats
        Assert.True(doc.GetFieldMean("amount") > 0.0);
        Assert.True(doc.GetFieldMin("amount") > 0.0);
        var uniqueCurrencies = doc.GetFieldUniqueValues("currency");
        Assert.True(uniqueCurrencies.Count >= 1);

        // SaveToFile
        var outPath = TempFile("aml_transaction_feed_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(totalRecords, loaded.RecordCount);
        Assert.Equal(consistencyAmount, loaded.GetFieldTypeConsistency("amount"), precision: 8);
        var loadedDist = loaded.GetFieldTypeDistribution("amount");
        Assert.Equal(distAmount.Count, loadedDist.Count);

        // Uniform type consistency preserved
        Assert.Equal(1.0, loaded.GetFieldTypeConsistency("risk_level"), precision: 6);
        Assert.Equal(1.0, loaded.GetFieldTypeConsistency("flag"), precision: 6);
    }
}
