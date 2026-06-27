// Tests for NdjsonDocument.GetFieldMin, GetFieldMax deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R282

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R282: Tests for NdjsonDocument.GetFieldMin, GetFieldMax deeper.
/// GetFieldMin(field): returns the minimum numeric value in the named field.
/// GetFieldMax(field): returns the maximum numeric value in the named field; ≥ GetFieldMin.
/// Covers: GetFieldMin no-throw; GetFieldMin correct for known data;
/// GetFieldMin consistent; GetFieldMin save-load;
/// GetFieldMax no-throw; GetFieldMax correct for known data;
/// GetFieldMax consistent; GetFieldMax save-load;
/// GetFieldMin leq GetFieldMax; GetFieldMin eq GetFieldMax for uniform;
/// dogfood pipeline.
/// </summary>
public class NdjsonR282GetFieldMinAndFieldMaxDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR282GetFieldMinAndFieldMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR282_" + Guid.NewGuid().ToString("N"));
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
        // values: 10, 20, 30, 40, 50 — min=10, max=50
        for (int i = 1; i <= 5; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":{i * 10.0}}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":42.0}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMin_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMin("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMin_Correct_ForKnownData()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(10.0, doc.GetFieldMin("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMin_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMin("score"), doc.GetFieldMin("score"));
    }

    [Fact]
    public void GetFieldMin_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMin("score");
        var path = TempFile("min_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldMin("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMax_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMax("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMax_Correct_ForKnownData()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(50.0, doc.GetFieldMax("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMax_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMax("score"), doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMax_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMax("score");
        var path = TempFile("max_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldMax("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMin_Leq_GetFieldMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMin("score") <= doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMin_Equals_GetFieldMax_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(doc.GetFieldMin("value"), doc.GetFieldMax("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMin_GetFieldMax_Pipeline()
    {
        // Finance — Bank of England / FCA: Retail Banking Consumer Duty Outcome Metrics 2024
        // Firm-level Consumer Duty metrics tracking fair value, support, and complaint resolution
        // Min/max detect outlier firms deviating from sector benchmark thresholds

        var path = TempFile("boe_fca_consumer_duty_metrics_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240315);

        string[] firms = {
            "Lloyds_Banking_Group", "Barclays_Retail", "NatWest_Group", "HSBC_UK", "Santander_UK",
            "Nationwide_BS", "Monzo_Bank", "Starling_Bank", "Metro_Bank", "TSB_Bank",
            "Virgin_Money_UK", "Clydesdale_Bank", "Co_operative_Bank", "Aldermore", "Shawbrook",
            "Paragon_Banking", "OSB_Group", "Secure_Trust_Bank", "Close_Brothers", "Atom_Bank"
        };
        string[] firmTypes = {
            "High_Street_Bank", "High_Street_Bank", "High_Street_Bank", "High_Street_Bank", "High_Street_Bank",
            "Building_Society", "Digital_Challenger", "Digital_Challenger", "Challenger_Bank", "High_Street_Bank",
            "Digital_Bank", "Regional_Bank", "Ethical_Bank", "Specialist_Lender", "Specialist_Lender",
            "Buy_To_Let", "Specialist_Savings", "Specialist_Lender", "Merchant_Finance", "Digital_Challenger"
        };

        for (int i = 0; i < firms.Length; i++)
        {
            // Fair value score (0-100, higher = better value for customers)
            double fairValueScore = 55 + rng.NextDouble() * 40 + (i < 6 ? 0 : i < 10 ? 5 : -5);
            fairValueScore = Math.Min(100, Math.Max(10, fairValueScore));

            // Consumer support adequacy (staff per 1000 customers)
            double supportRatio = 1.5 + rng.NextDouble() * 6 + (firmTypes[i] == "Digital_Challenger" ? -1.0 : 0);
            supportRatio = Math.Max(0.5, supportRatio);

            // Complaint resolution rate (%)
            double complaintResolution = 70 + rng.NextDouble() * 28;
            complaintResolution = Math.Min(100, complaintResolution);

            // Complaint upheld rate (%)
            double complaintUpheld = 15 + rng.NextDouble() * 50;

            // Average time to resolve (days)
            double resolutionDays = 2 + rng.NextDouble() * 26;

            // Products with good consumer outcomes (%)
            double goodOutcomes = 60 + rng.NextDouble() * 35;

            // Vulnerable customer identification rate (%)
            double vulnIdRate = 8 + rng.NextDouble() * 20;

            sb.AppendLine($"{{" +
                          $"\"firm_id\":\"FRN{i:D6}\"," +
                          $"\"firm_name\":\"{firms[i]}\"," +
                          $"\"firm_type\":\"{firmTypes[i]}\"," +
                          $"\"fair_value_score\":{fairValueScore:F1}," +
                          $"\"support_ratio_per_1000\":{supportRatio:F2}," +
                          $"\"complaint_resolution_pct\":{complaintResolution:F1}," +
                          $"\"complaint_upheld_pct\":{complaintUpheld:F1}," +
                          $"\"avg_resolution_days\":{resolutionDays:F1}," +
                          $"\"good_outcomes_pct\":{goodOutcomes:F1}," +
                          $"\"vulnerable_id_rate_pct\":{vulnIdRate:F1}" +
                          $"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(firms.Length, doc.RecordCount);

        // Fair value score min/max
        var fvMin = doc.GetFieldMin("fair_value_score");
        var fvMax = doc.GetFieldMax("fair_value_score");
        Assert.True(fvMin >= 0.0);
        Assert.True(fvMax <= 100.0);
        Assert.True(fvMin <= fvMax);
        Assert.Equal(fvMin, doc.GetFieldMin("fair_value_score")); // consistent
        Assert.Equal(fvMax, doc.GetFieldMax("fair_value_score")); // consistent

        // Complaint resolution rate min/max
        var crMin = doc.GetFieldMin("complaint_resolution_pct");
        var crMax = doc.GetFieldMax("complaint_resolution_pct");
        Assert.True(crMin >= 0.0);
        Assert.True(crMax <= 100.0);
        Assert.True(crMin <= crMax);

        // Resolution days min/max
        var rdMin = doc.GetFieldMin("avg_resolution_days");
        var rdMax = doc.GetFieldMax("avg_resolution_days");
        Assert.True(rdMin >= 0.0);
        Assert.True(rdMin <= rdMax);

        // Good outcomes min/max
        var goMin = doc.GetFieldMin("good_outcomes_pct");
        var goMax = doc.GetFieldMax("good_outcomes_pct");
        Assert.True(goMin >= 0.0);
        Assert.True(goMax <= 100.0);
        Assert.True(goMin <= goMax);

        // Mean is between min and max
        var fvMean = doc.GetFieldMean("fair_value_score");
        Assert.True(fvMean >= fvMin && fvMean <= fvMax);

        // SaveToFile
        var outPath = TempFile("boe_consumer_duty_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(fvMin, loaded.GetFieldMin("fair_value_score"), precision: 6);
        Assert.Equal(fvMax, loaded.GetFieldMax("fair_value_score"), precision: 6);
        Assert.Equal(crMin, loaded.GetFieldMin("complaint_resolution_pct"), precision: 6);
        Assert.Equal(crMax, loaded.GetFieldMax("complaint_resolution_pct"), precision: 6);
        Assert.Equal(rdMin, loaded.GetFieldMin("avg_resolution_days"), precision: 6);
        Assert.Equal(goMax, loaded.GetFieldMax("good_outcomes_pct"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldMin("fair_value_score"));
        var ex2 = Record.Exception(() => loaded.GetFieldMax("complaint_resolution_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
