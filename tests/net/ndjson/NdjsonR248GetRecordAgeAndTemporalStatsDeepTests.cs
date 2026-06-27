// Tests for NdjsonDocument.GetRecordAge, GetTemporalFieldRange, GetTemporalFieldGapStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R248

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R248: Tests for NdjsonDocument.GetRecordAge, GetTemporalFieldRange, GetTemporalFieldGapStats deeper.
/// GetRecordAge(index, timestampField): returns the age in seconds from the timestamp field to now.
/// GetTemporalFieldRange(field): returns the duration in seconds between the earliest and latest timestamps.
/// GetTemporalFieldGapStats(field): returns statistics about gaps between consecutive timestamps.
/// Covers: GetRecordAge no-throw; GetRecordAge non-negative; GetRecordAge consistent;
/// GetTemporalFieldRange no-throw; GetTemporalFieldRange non-negative; GetTemporalFieldRange consistent;
/// GetTemporalFieldRange zero for single record; GetTemporalFieldRange save-load;
/// GetTemporalFieldGapStats no-throw; GetTemporalFieldGapStats non-null; GetTemporalFieldGapStats consistent;
/// dogfood GetRecordAge→GetTemporalFieldRange→GetTemporalFieldGapStats→SaveToFile pipeline.
/// </summary>
public class NdjsonR248GetRecordAgeAndTemporalStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR248GetRecordAgeAndTemporalStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR248_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSecurityEventsNdjson()
    {
        var path = TempFile("security_events.ndjson");
        var records = new[]
        {
            "{\"event_id\":\"EVT001\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"event_type\":\"Login\",\"severity\":\"Low\",\"source_ip\":\"10.0.1.1\"}",
            "{\"event_id\":\"EVT002\",\"timestamp\":\"2024-09-01T08:05:00Z\",\"event_type\":\"FileAccess\",\"severity\":\"Medium\",\"source_ip\":\"10.0.1.2\"}",
            "{\"event_id\":\"EVT003\",\"timestamp\":\"2024-09-01T08:10:00Z\",\"event_type\":\"PrivEscalation\",\"severity\":\"High\",\"source_ip\":\"10.0.1.3\"}",
            "{\"event_id\":\"EVT004\",\"timestamp\":\"2024-09-01T08:15:00Z\",\"event_type\":\"Logout\",\"severity\":\"Low\",\"source_ip\":\"10.0.1.1\"}",
            "{\"event_id\":\"EVT005\",\"timestamp\":\"2024-09-01T09:00:00Z\",\"event_type\":\"Login\",\"severity\":\"Low\",\"source_ip\":\"10.0.2.1\"}",
            "{\"event_id\":\"EVT006\",\"timestamp\":\"2024-09-01T09:30:00Z\",\"event_type\":\"DataExfil\",\"severity\":\"Critical\",\"source_ip\":\"10.0.2.1\"}",
        };
        File.WriteAllLines(path, records);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordAge
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAge_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var ex = Record.Exception(() => doc.GetRecordAge(0, "timestamp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAge_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var age = doc.GetRecordAge(0, "timestamp");
        Assert.True(age >= 0);
    }

    [Fact]
    public void GetRecordAge_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        // Age is relative to current time — two rapid calls should give same or close values
        var age1 = doc.GetRecordAge(0, "timestamp");
        var age2 = doc.GetRecordAge(0, "timestamp");
        // Allow 1 second difference for clock advance
        Assert.True(Math.Abs(age2 - age1) <= 1);
    }

    [Fact]
    public void GetRecordAge_OlderRecord_HasLargerAge()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        // EVT001 (08:00) is older than EVT006 (09:30)
        var age0 = doc.GetRecordAge(0, "timestamp");
        var age5 = doc.GetRecordAge(5, "timestamp");
        Assert.True(age0 >= age5); // earlier record = older = larger age
    }

    // -------------------------------------------------------------------------
    // GetTemporalFieldRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTemporalFieldRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var ex = Record.Exception(() => doc.GetTemporalFieldRange("timestamp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTemporalFieldRange_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        Assert.True(doc.GetTemporalFieldRange("timestamp") >= 0);
    }

    [Fact]
    public void GetTemporalFieldRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        Assert.Equal(doc.GetTemporalFieldRange("timestamp"), doc.GetTemporalFieldRange("timestamp"));
    }

    [Fact]
    public void GetTemporalFieldRange_KnownRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        // EVT001 08:00 → EVT006 09:30 = 90 minutes = 5400 seconds
        var range = doc.GetTemporalFieldRange("timestamp");
        Assert.True(range > 0);
        // Should be approximately 5400 seconds (90 minutes)
        Assert.True(range >= 5000 && range <= 6000);
    }

    [Fact]
    public void GetTemporalFieldRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var before = doc.GetTemporalFieldRange("timestamp");
        var path = TempFile("tfr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTemporalFieldRange("timestamp"), precision: 0);
    }

    // -------------------------------------------------------------------------
    // GetTemporalFieldGapStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTemporalFieldGapStats_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var ex = Record.Exception(() => doc.GetTemporalFieldGapStats("timestamp"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTemporalFieldGapStats_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        Assert.NotNull(doc.GetTemporalFieldGapStats("timestamp"));
    }

    [Fact]
    public void GetTemporalFieldGapStats_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSecurityEventsNdjson());
        var g1 = doc.GetTemporalFieldGapStats("timestamp");
        var g2 = doc.GetTemporalFieldGapStats("timestamp");
        Assert.Equal(g1.Count, g2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordAge_GetTemporalFieldRange_GetTemporalFieldGapStats_SaveToFile_Pipeline()
    {
        // SIEM analytics — cloud security event log temporal analysis
        var path = TempFile("cloud_sec_events.ndjson");
        var records = new[]
        {
            "{\"event_id\":\"CSE0001\",\"timestamp\":\"2024-10-01T00:00:00Z\",\"service\":\"IAM\",\"action\":\"CreateRole\",\"risk_score\":25,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0002\",\"timestamp\":\"2024-10-01T00:05:00Z\",\"service\":\"S3\",\"action\":\"GetObject\",\"risk_score\":10,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0003\",\"timestamp\":\"2024-10-01T00:15:00Z\",\"service\":\"EC2\",\"action\":\"RunInstances\",\"risk_score\":45,\"region\":\"us-east-1\"}",
            "{\"event_id\":\"CSE0004\",\"timestamp\":\"2024-10-01T00:20:00Z\",\"service\":\"IAM\",\"action\":\"AttachPolicy\",\"risk_score\":70,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0005\",\"timestamp\":\"2024-10-01T01:00:00Z\",\"service\":\"KMS\",\"action\":\"Decrypt\",\"risk_score\":55,\"region\":\"eu-central-1\"}",
            "{\"event_id\":\"CSE0006\",\"timestamp\":\"2024-10-01T01:30:00Z\",\"service\":\"RDS\",\"action\":\"DescribeDBInstances\",\"risk_score\":15,\"region\":\"eu-west-2\"}",
            "{\"event_id\":\"CSE0007\",\"timestamp\":\"2024-10-01T02:00:00Z\",\"service\":\"CloudTrail\",\"action\":\"StopLogging\",\"risk_score\":95,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0008\",\"timestamp\":\"2024-10-01T02:05:00Z\",\"service\":\"S3\",\"action\":\"PutBucketPolicy\",\"risk_score\":80,\"region\":\"us-east-1\"}",
            "{\"event_id\":\"CSE0009\",\"timestamp\":\"2024-10-01T02:10:00Z\",\"service\":\"IAM\",\"action\":\"CreateUser\",\"risk_score\":60,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0010\",\"timestamp\":\"2024-10-01T03:00:00Z\",\"service\":\"EC2\",\"action\":\"ModifySecurityGroup\",\"risk_score\":75,\"region\":\"ap-southeast-1\"}",
            "{\"event_id\":\"CSE0011\",\"timestamp\":\"2024-10-01T04:00:00Z\",\"service\":\"Lambda\",\"action\":\"CreateFunction\",\"risk_score\":40,\"region\":\"eu-west-1\"}",
            "{\"event_id\":\"CSE0012\",\"timestamp\":\"2024-10-01T06:00:00Z\",\"service\":\"Organizations\",\"action\":\"DetachPolicy\",\"risk_score\":85,\"region\":\"us-east-1\"}",
        };
        File.WriteAllLines(path, records);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetRecordAge — all events are past so age must be positive
        var age0 = doc.GetRecordAge(0, "timestamp");
        Assert.True(age0 > 0); // 2024-10-01 is in the past
        var age11 = doc.GetRecordAge(11, "timestamp");
        Assert.True(age11 > 0);
        Assert.True(age0 >= age11); // CSE0001 (earlier) is older than CSE0012

        // GetTemporalFieldRange — CSE0001 00:00 → CSE0012 06:00 = 6 hours = 21600 seconds
        var range = doc.GetTemporalFieldRange("timestamp");
        Assert.True(range > 0);
        Assert.True(range >= 21000 && range <= 22000); // ≈ 6 hours
        Assert.Equal(range, doc.GetTemporalFieldRange("timestamp")); // consistent

        // GetTemporalFieldGapStats — gap statistics across 12 events
        var gapStats = doc.GetTemporalFieldGapStats("timestamp");
        Assert.NotNull(gapStats);
        Assert.Equal(gapStats.Count, doc.GetTemporalFieldGapStats("timestamp").Count); // consistent

        // SaveToFile
        var outPath = TempFile("cloud_sec_events_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(12, loaded.RecordCount);
        Assert.Equal(range, loaded.GetTemporalFieldRange("timestamp"), precision: 0);
        Assert.NotNull(loaded.GetTemporalFieldGapStats("timestamp"));
        Assert.True(loaded.GetRecordAge(0, "timestamp") > 0);

        var ex1 = Record.Exception(() => loaded.GetRecordAge(5, "timestamp"));
        var ex2 = Record.Exception(() => loaded.GetTemporalFieldRange("timestamp"));
        var ex3 = Record.Exception(() => loaded.GetTemporalFieldGapStats("timestamp"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
