// Tests for NdjsonDocument.GetFieldMode, GetFieldModeCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R271

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R271: Tests for NdjsonDocument.GetFieldMode, GetFieldModeCount deeper.
/// GetFieldMode(fieldName): returns the most frequently occurring value in the field.
/// GetFieldModeCount(fieldName): returns the count of occurrences of the modal value.
/// Covers: GetFieldMode no-throw; GetFieldMode non-null; GetFieldMode consistent;
/// GetFieldMode save-load; GetFieldModeCount no-throw; GetFieldModeCount positive;
/// GetFieldModeCount consistent; GetFieldModeCount save-load;
/// GetFieldModeCount le RecordCount; GetFieldModeCount equals RecordCount for constant;
/// dogfood CreateDoc→GetFieldMode→GetFieldModeCount pipeline.
/// </summary>
public class NdjsonR271GetFieldModeAndModeCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR271GetFieldModeAndModeCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR271_" + Guid.NewGuid().ToString("N"));
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
        var sb = new StringBuilder();
        string[] statuses = { "Active", "Active", "Active", "Inactive", "Pending" };
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            string status = statuses[rng.Next(statuses.Length)];
            int priority = rng.Next(5) + 1;
            sb.AppendLine($"{{\"id\":{i},\"status\":\"{status}\",\"priority\":{priority}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"status\":\"Active\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMode_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMode("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMode_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMode("status"), doc.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMode("status");
        var path = TempFile("mode_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_Constant_Returns_That_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal("Active", doc.GetFieldMode("status"));
    }

    // -------------------------------------------------------------------------
    // GetFieldModeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldModeCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldModeCount("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldModeCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldModeCount("status") > 0);
    }

    [Fact]
    public void GetFieldModeCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldModeCount("priority"), doc.GetFieldModeCount("priority"));
    }

    [Fact]
    public void GetFieldModeCount_Le_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldModeCount("status") <= doc.RecordCount);
    }

    [Fact]
    public void GetFieldModeCount_Equals_RecordCount_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(doc.RecordCount, doc.GetFieldModeCount("status"));
    }

    [Fact]
    public void GetFieldModeCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldModeCount("status");
        var path = TempFile("mc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldModeCount("status"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMode_GetFieldModeCount_Pipeline()
    {
        // Regulatory — Financial Conduct Authority (FCA): Consumer Duty Breach Notifications
        // NDJSON stream of firm notifications categorised by breach type and severity
        var path = TempFile("fca_consumer_duty_notifications.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] breachTypes = {
            "Price and Value", "Price and Value", "Price and Value", // most common
            "Products and Services", "Products and Services",
            "Consumer Support",
            "Consumer Understanding",
            "Consumer Understanding"
        };
        string[] severities = { "Minor", "Minor", "Moderate", "Moderate", "Serious" };
        string[] sectors = { "Retail Banking", "General Insurance", "Investments", "Mortgages",
                             "Consumer Credit", "Pensions", "Payments" };
        string[] outcomes = { "Remediation Required", "Remediation Required", "Remediation Required",
                              "Enhanced Supervision", "Board Attestation", "Enforcement Referral" };

        for (int i = 0; i < 200; i++)
        {
            string notifId = $"CD-{2024000 + i}";
            string firmRef = $"FR{100000 + rng.Next(400000)}";
            string breach = breachTypes[rng.Next(breachTypes.Length)];
            string severity = severities[rng.Next(severities.Length)];
            string sector = sectors[rng.Next(sectors.Length)];
            string outcome = outcomes[rng.Next(outcomes.Length)];
            int daysToResolve = 30 + rng.Next(150);
            double financialImpact = Math.Round(10000 + rng.NextDouble() * 2000000, 2);
            bool classAction = rng.Next(10) < 2; // 20% class action risk
            sb.AppendLine($"{{\"notification_id\":\"{notifId}\",\"firm_ref\":\"{firmRef}\"," +
                          $"\"breach_type\":\"{breach}\",\"severity\":\"{severity}\"," +
                          $"\"sector\":\"{sector}\",\"required_outcome\":\"{outcome}\"," +
                          $"\"days_to_resolve\":{daysToResolve},\"financial_impact\":{financialImpact}," +
                          $"\"class_action_risk\":{classAction.ToString().ToLower()}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldMode for breach_type — "Price and Value" should be most common
        var modeBreach = doc.GetFieldMode("breach_type");
        Assert.NotNull(modeBreach);
        Assert.Equal(modeBreach, doc.GetFieldMode("breach_type")); // consistent

        // GetFieldModeCount for breach_type
        var modeCountBreach = doc.GetFieldModeCount("breach_type");
        Assert.True(modeCountBreach > 0);
        Assert.True(modeCountBreach <= doc.RecordCount);
        Assert.Equal(modeCountBreach, doc.GetFieldModeCount("breach_type")); // consistent

        // GetFieldMode for severity
        var modeSeverity = doc.GetFieldMode("severity");
        Assert.NotNull(modeSeverity);
        var modeCountSeverity = doc.GetFieldModeCount("severity");
        Assert.True(modeCountSeverity > 0);
        Assert.True(modeCountSeverity <= doc.RecordCount);

        // GetFieldMode for required_outcome — "Remediation Required" most likely
        var modeOutcome = doc.GetFieldMode("required_outcome");
        Assert.NotNull(modeOutcome);
        var modeCountOutcome = doc.GetFieldModeCount("required_outcome");
        Assert.True(modeCountOutcome > 0);

        // GetFieldMode for sector
        var modeSector = doc.GetFieldMode("sector");
        Assert.NotNull(modeSector);
        var modeCountSector = doc.GetFieldModeCount("sector");
        Assert.True(modeCountSector > 0);

        // Basic field stats
        Assert.True(doc.GetFieldMean("days_to_resolve") > 0);
        Assert.True(doc.GetFieldSum("financial_impact") > 0);

        // SaveToFile
        var outPath = TempFile("fca_notifications_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(modeBreach, loaded.GetFieldMode("breach_type"));
        Assert.Equal(modeCountBreach, loaded.GetFieldModeCount("breach_type"));
        Assert.Equal(modeSeverity, loaded.GetFieldMode("severity"));

        // Constant mode sub-test
        var path2 = TempFile("constant_notifications.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{{\"id\":{i},\"breach_type\":\"Price and Value\"}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal("Price and Value", doc2.GetFieldMode("breach_type"));
        Assert.Equal(50, doc2.GetFieldModeCount("breach_type"));

        var ex1 = Record.Exception(() => loaded.GetFieldMode("sector"));
        var ex2 = Record.Exception(() => loaded.GetFieldModeCount("sector"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
