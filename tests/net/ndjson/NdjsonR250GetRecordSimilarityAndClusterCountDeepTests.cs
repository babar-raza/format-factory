// Tests for NdjsonDocument.GetRecordSimilarity, GetClusterCount, GetFieldCooccurrenceCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R250

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R250: Tests for NdjsonDocument.GetRecordSimilarity, GetClusterCount, GetFieldCooccurrenceCount deeper.
/// GetRecordSimilarity(indexA, indexB): returns a similarity score [0–1] between two records.
/// GetClusterCount(): returns the number of distinct record clusters based on field patterns.
/// GetFieldCooccurrenceCount(fieldA, valueA, fieldB, valueB): counts records where both field conditions hold.
/// Covers: GetRecordSimilarity no-throw; GetRecordSimilarity in [0,1]; GetRecordSimilarity consistent;
/// GetRecordSimilarity self-similarity one;
/// GetClusterCount no-throw; GetClusterCount positive; GetClusterCount consistent;
/// GetFieldCooccurrenceCount no-throw; GetFieldCooccurrenceCount non-negative;
/// GetFieldCooccurrenceCount consistent; GetFieldCooccurrenceCount zero for impossible combo;
/// GetFieldCooccurrenceCount save-load;
/// dogfood CreateDoc→GetRecordSimilarity→GetClusterCount→GetFieldCooccurrenceCount pipeline.
/// </summary>
public class NdjsonR250GetRecordSimilarityAndClusterCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR250GetRecordSimilarityAndClusterCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR250_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUserSegmentNdjson()
    {
        var path = TempFile("user_segments.ndjson");
        string[] segments = { "Premium", "Standard", "Freemium" };
        string[] regions = { "EMEA", "APAC", "AMER" };
        string[] plans = { "Annual", "Monthly", "Trial" };
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var seg = segments[i % 3];
            var reg = regions[i % 3];
            var plan = plans[i % 3];
            int mau = 50 + (i % 3) * 100;
            lines.Add($"{{\"user_id\":\"U{i:D4}\",\"segment\":\"{seg}\",\"region\":\"{reg}\",\"plan_type\":\"{plan}\",\"mau\":{mau}}}");
        }
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordSimilarity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordSimilarity_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        var ex = Record.Exception(() => doc.GetRecordSimilarity(0, 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordSimilarity_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        var sim = doc.GetRecordSimilarity(0, 1);
        Assert.True(sim >= 0.0 && sim <= 1.0);
    }

    [Fact]
    public void GetRecordSimilarity_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.Equal(doc.GetRecordSimilarity(0, 2), doc.GetRecordSimilarity(0, 2));
    }

    [Fact]
    public void GetRecordSimilarity_SelfSimilarity_One()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.Equal(1.0, doc.GetRecordSimilarity(0, 0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetClusterCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetClusterCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        var ex = Record.Exception(() => doc.GetClusterCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetClusterCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.True(doc.GetClusterCount() > 0);
    }

    [Fact]
    public void GetClusterCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.Equal(doc.GetClusterCount(), doc.GetClusterCount());
    }

    // -------------------------------------------------------------------------
    // GetFieldCooccurrenceCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCooccurrenceCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        var ex = Record.Exception(() => doc.GetFieldCooccurrenceCount("segment", "Premium", "region", "EMEA"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCooccurrenceCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.True(doc.GetFieldCooccurrenceCount("segment", "Standard", "plan_type", "Annual") >= 0);
    }

    [Fact]
    public void GetFieldCooccurrenceCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.Equal(
            doc.GetFieldCooccurrenceCount("segment", "Premium", "region", "EMEA"),
            doc.GetFieldCooccurrenceCount("segment", "Premium", "region", "EMEA"));
    }

    [Fact]
    public void GetFieldCooccurrenceCount_Zero_ForImpossibleCombo()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        Assert.Equal(0, doc.GetFieldCooccurrenceCount("segment", "NoSuchSegment_XYZ", "region", "EMEA"));
    }

    [Fact]
    public void GetFieldCooccurrenceCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUserSegmentNdjson());
        var before = doc.GetFieldCooccurrenceCount("segment", "Freemium", "plan_type", "Trial");
        var path = TempFile("fcc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldCooccurrenceCount("segment", "Freemium", "plan_type", "Trial"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordSimilarity_GetClusterCount_GetFieldCooccurrenceCount_Pipeline()
    {
        // Financial risk — credit bureau application fraud detection event stream
        var path = TempFile("fraud_events.ndjson");
        string[] products = { "Personal_Loan", "Credit_Card", "Mortgage", "Auto_Finance" };
        string[] channels = { "Branch", "Online", "Broker", "Mobile_App" };
        string[] employment = { "Employed_FT", "Self_Employed", "Part_Time", "Retired" };
        string[] outcomes = { "Approved", "Declined", "Referred", "Fraud_Confirmed" };
        var rng = new Random(20240601);
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var prod = products[i % 4];
            var ch = channels[i % 4];
            var emp = employment[i % 4];
            // Fraud events cluster around Online + Personal_Loan or Mobile_App + Credit_Card
            var outcome = (prod == "Personal_Loan" && ch == "Online") ? "Fraud_Confirmed" :
                          (prod == "Credit_Card" && ch == "Mobile_App") ? "Fraud_Confirmed" :
                          outcomes[i % 4];
            double amount = 2000 + rng.NextDouble() * 48000;
            int score = 300 + rng.Next(0, 550);
            lines.Add($"{{\"app_id\":\"APP{i:D5}\",\"product\":\"{prod}\",\"channel\":\"{ch}\",\"employment\":\"{emp}\",\"outcome\":\"{outcome}\",\"amount\":{amount:F0},\"credit_score\":{score}}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetRecordSimilarity — same record = 1.0
        Assert.Equal(1.0, doc.GetRecordSimilarity(0, 0), precision: 6);

        // Different records should be in [0,1]
        var sim01 = doc.GetRecordSimilarity(0, 1);
        Assert.True(sim01 >= 0.0 && sim01 <= 1.0);
        Assert.Equal(sim01, doc.GetRecordSimilarity(0, 1)); // consistent

        var sim03 = doc.GetRecordSimilarity(0, 3);
        Assert.True(sim03 >= 0.0 && sim03 <= 1.0);

        // GetClusterCount
        var clusters = doc.GetClusterCount();
        Assert.True(clusters > 0);
        Assert.Equal(clusters, doc.GetClusterCount()); // consistent

        // GetFieldCooccurrenceCount
        var fraudOnline = doc.GetFieldCooccurrenceCount("channel", "Online", "outcome", "Fraud_Confirmed");
        Assert.True(fraudOnline >= 0);
        Assert.Equal(fraudOnline, doc.GetFieldCooccurrenceCount("channel", "Online", "outcome", "Fraud_Confirmed")); // consistent

        var approvedBranch = doc.GetFieldCooccurrenceCount("channel", "Branch", "outcome", "Approved");
        Assert.True(approvedBranch >= 0);

        // Impossible combination
        var impossibleCount = doc.GetFieldCooccurrenceCount("outcome", "NonExistentOutcome_XYZ", "channel", "Branch");
        Assert.Equal(0, impossibleCount);

        // SaveToFile
        var outPath = TempFile("fraud_events_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(fraudOnline, loaded.GetFieldCooccurrenceCount("channel", "Online", "outcome", "Fraud_Confirmed"));
        Assert.True(loaded.GetClusterCount() > 0);
        Assert.Equal(1.0, loaded.GetRecordSimilarity(0, 0), precision: 6);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // GetRecord consistency
        var record0 = loaded.GetRecord(0);
        Assert.NotNull(record0);

        var ex1 = Record.Exception(() => loaded.GetRecordSimilarity(0, 1));
        var ex2 = Record.Exception(() => loaded.GetClusterCount());
        var ex3 = Record.Exception(() => loaded.GetFieldCooccurrenceCount("product", "Mortgage", "employment", "Employed_FT"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
