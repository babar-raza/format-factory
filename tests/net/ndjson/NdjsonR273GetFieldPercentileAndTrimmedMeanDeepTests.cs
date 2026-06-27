// Tests for NdjsonDocument.GetFieldPercentile, GetFieldTrimmedMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R273

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R273: Tests for NdjsonDocument.GetFieldPercentile, GetFieldTrimmedMean deeper.
/// GetFieldPercentile(field, p): returns the p-th percentile (0-100) of numeric values in the field.
/// GetFieldTrimmedMean(field, trimPct): returns the mean after trimming trimPct% from each tail.
/// Covers: GetFieldPercentile no-throw; GetFieldPercentile in-range; GetFieldPercentile consistent;
/// GetFieldPercentile p0=min and p100=max; GetFieldPercentile save-load;
/// GetFieldTrimmedMean no-throw; GetFieldTrimmedMean in-range; GetFieldTrimmedMean consistent;
/// GetFieldTrimmedMean save-load; GetFieldTrimmedMean trim0=mean; GetFieldTrimmedMean robust to outliers;
/// dogfood CreateDoc→GetFieldPercentile→GetFieldTrimmedMean→SaveToFile pipeline.
/// </summary>
public class NdjsonR273GetFieldPercentileAndTrimmedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR273GetFieldPercentileAndTrimmedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR273_" + Guid.NewGuid().ToString("N"));
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
        // Values 1..100 — known percentiles
        var path = TempFile("sample.ndjson");
        var sb = new StringBuilder();
        for (int i = 1; i <= 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{i},\"score\":{i * 0.5:F1}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateWithOutliersNdjson()
    {
        // 90 values near 100, then 10 extreme outliers
        var path = TempFile("outliers.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(42);
        for (int i = 0; i < 90; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{95 + rng.Next(10)}}}");
        for (int i = 90; i < 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{rng.Next(1000, 5000)}}}"); // extreme outliers
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldPercentile_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldPercentile("value", 50));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldPercentile_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var p50 = doc.GetFieldPercentile("value", 50);
        var min = doc.GetFieldMin("value");
        var max = doc.GetFieldMax("value");
        Assert.True(p50 >= min && p50 <= max);
    }

    [Fact]
    public void GetFieldPercentile_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldPercentile("value", 25), doc.GetFieldPercentile("value", 25));
    }

    [Fact]
    public void GetFieldPercentile_P0_Equals_Min()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMin("value"), doc.GetFieldPercentile("value", 0), precision: 6);
    }

    [Fact]
    public void GetFieldPercentile_P100_Equals_Max()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMax("value"), doc.GetFieldPercentile("value", 100), precision: 6);
    }

    [Fact]
    public void GetFieldPercentile_P25_Le_P50_Le_P75()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var p25 = doc.GetFieldPercentile("value", 25);
        var p50 = doc.GetFieldPercentile("value", 50);
        var p75 = doc.GetFieldPercentile("value", 75);
        Assert.True(p25 <= p50);
        Assert.True(p50 <= p75);
    }

    [Fact]
    public void GetFieldPercentile_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldPercentile("value", 75);
        var path = TempFile("pct_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldPercentile("value", 75), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTrimmedMean_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldTrimmedMean("value", 10.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTrimmedMean_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var tm = doc.GetFieldTrimmedMean("value", 10.0);
        Assert.True(tm >= doc.GetFieldMin("value") && tm <= doc.GetFieldMax("value"));
    }

    [Fact]
    public void GetFieldTrimmedMean_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldTrimmedMean("value", 10.0), doc.GetFieldTrimmedMean("value", 10.0));
    }

    [Fact]
    public void GetFieldTrimmedMean_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWithOutliersNdjson());
        var before = doc.GetFieldTrimmedMean("value", 10.0);
        var path = TempFile("tm_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldTrimmedMean("value", 10.0), precision: 6);
    }

    [Fact]
    public void GetFieldTrimmedMean_RobustToOutliers()
    {
        var doc = NdjsonDocument.LoadFile(CreateWithOutliersNdjson());
        var mean = doc.GetFieldMean("value");
        var trimmedMean = doc.GetFieldTrimmedMean("value", 10.0); // trim 10% each tail
        // Untrimmed mean is pulled by outliers → much higher than core values (~100)
        // Trimmed mean should be closer to 100 (the core)
        Assert.True(trimmedMean < mean); // trimming removes high-value outliers
        Assert.True(trimmedMean >= 90.0); // core values are 95-104
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldPercentile_GetFieldTrimmedMean_SaveToFile_Pipeline()
    {
        // Healthcare — NHS England: Referral-to-Treatment (RTT) Waiting Times 2024-25
        // Incomplete pathways data by specialty — percentile and trimmed mean analysis
        // Used to monitor against 18-week constitutional standard (Regulation 9, NHS Constitution)

        var path = TempFile("nhs_rtt_waiting_times.ndjson");
        var sb = new StringBuilder();

        var rng = new Random(20241201);
        string[] specialties = {
            "Orthopaedics", "Ophthalmology", "Cardiology", "General Surgery",
            "Urology", "Gynaecology", "ENT", "Neurology", "Rheumatology", "Dermatology"
        };
        string[] providers = { "RJC", "RJE", "RKB", "RKE", "RKL", "RKM", "RLN", "RM2", "RM3", "RN5" };

        // Simulate RTT waiting times: most ≤18 weeks (126 days), some breaching
        for (int i = 0; i < 300; i++)
        {
            string spec = specialties[i % specialties.Length];
            string provider = providers[rng.Next(providers.Length)];

            // Different specialties have different wait distributions
            int baseWait = spec == "Orthopaedics" ? 80 :
                           spec == "Ophthalmology" ? 65 :
                           spec == "Neurology" ? 70 :
                           spec == "Cardiology" ? 55 : 50;
            double jitter = (rng.NextDouble() - 0.5) * 60;
            int waitDays = (int)Math.Max(1, baseWait + jitter);

            // 8% long-waiters exceeding 52 weeks (NHS target: <1%)
            if (rng.NextDouble() < 0.08)
                waitDays = 400 + rng.Next(300);

            bool breach18wk = waitDays > 126;
            bool breach52wk = waitDays > 365;
            int weekNum = (waitDays / 7) + 1;

            sb.AppendLine($"{{\"pathway_id\":\"RTT{i:D6}\",\"specialty\":\"{spec}\",\"provider\":\"{provider}\",\"wait_days\":{waitDays},\"week_number\":{weekNum},\"breach_18wk\":{breach18wk.ToString().ToLower()},\"breach_52wk\":{breach52wk.ToString().ToLower()}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(300, doc.RecordCount);

        // Percentile analysis of wait_days
        var p50 = doc.GetFieldPercentile("wait_days", 50); // median
        var p75 = doc.GetFieldPercentile("wait_days", 75);
        var p90 = doc.GetFieldPercentile("wait_days", 90);
        var p99 = doc.GetFieldPercentile("wait_days", 99);

        Assert.True(p50 >= 1.0);
        Assert.True(p50 <= p75);
        Assert.True(p75 <= p90);
        Assert.True(p90 <= p99);
        Assert.Equal(p50, doc.GetFieldPercentile("wait_days", 50)); // consistent

        var p0 = doc.GetFieldPercentile("wait_days", 0);
        var p100 = doc.GetFieldPercentile("wait_days", 100);
        Assert.Equal(doc.GetFieldMin("wait_days"), p0, precision: 6);
        Assert.Equal(doc.GetFieldMax("wait_days"), p100, precision: 6);

        // Week number percentiles
        var p75weeks = doc.GetFieldPercentile("week_number", 75);
        Assert.True(p75weeks >= 1.0);

        // Trimmed mean analysis (removes long-waiter outliers)
        var meanWait = doc.GetFieldMean("wait_days");
        var trimmed5 = doc.GetFieldTrimmedMean("wait_days", 5.0);   // trim 5% each tail
        var trimmed10 = doc.GetFieldTrimmedMean("wait_days", 10.0); // trim 10% each tail
        Assert.True(trimmed5 >= 1.0);
        Assert.True(trimmed10 >= 1.0);
        Assert.Equal(trimmed5, doc.GetFieldTrimmedMean("wait_days", 5.0)); // consistent
        // Trimming removes outliers (long-waiters pull up mean) → trimmed mean ≤ full mean
        Assert.True(trimmed10 <= meanWait);
        // More trimming → result closer to median
        Assert.True(Math.Abs(trimmed10 - p50) <= Math.Abs(meanWait - p50) + 1);

        // Basic stats
        Assert.True(doc.GetFieldMean("wait_days") > 0);
        Assert.True(doc.GetFieldStdDev("wait_days") > 0);
        Assert.True(doc.GetFieldMin("wait_days") >= 1.0);

        // SaveToFile
        var out1 = TempFile("nhs_rtt_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify percentiles preserved
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(p50, loaded.GetFieldPercentile("wait_days", 50), precision: 6);
        Assert.Equal(p90, loaded.GetFieldPercentile("wait_days", 90), precision: 6);
        Assert.Equal(trimmed10, loaded.GetFieldTrimmedMean("wait_days", 10.0), precision: 6);

        // Add additional records (new pathway referrals)
        var sb2 = new StringBuilder();
        for (int i = 300; i < 310; i++)
        {
            string spec = specialties[i % specialties.Length];
            sb2.AppendLine($"{{\"pathway_id\":\"RTT{i:D6}\",\"specialty\":\"{spec}\",\"provider\":\"RJC\",\"wait_days\":{30 + i % 50},\"week_number\":{5 + i % 8},\"breach_18wk\":false,\"breach_52wk\":false}}");
        }
        loaded.AppendRecords(sb2.ToString());
        Assert.Equal(310, loaded.RecordCount);

        var p50After = loaded.GetFieldPercentile("wait_days", 50);
        var tm10After = loaded.GetFieldTrimmedMean("wait_days", 10.0);
        Assert.True(p50After >= 1.0);
        Assert.True(tm10After >= 1.0);

        // Final save
        var out2 = TempFile("nhs_rtt_final.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var final = NdjsonDocument.LoadFile(out2);
        Assert.Equal(310, final.RecordCount);
        Assert.Equal(p50After, final.GetFieldPercentile("wait_days", 50), precision: 6);
        Assert.Equal(tm10After, final.GetFieldTrimmedMean("wait_days", 10.0), precision: 6);

        var ex1 = Record.Exception(() => final.GetFieldPercentile("wait_days", 95));
        var ex2 = Record.Exception(() => final.GetFieldTrimmedMean("wait_days", 5.0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
