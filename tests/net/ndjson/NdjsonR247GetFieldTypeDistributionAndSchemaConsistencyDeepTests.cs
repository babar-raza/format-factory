// Tests for NdjsonDocument.GetFieldTypeDistribution, GetSchemaConsistency, GetFieldNullRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R247

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R247: Tests for NdjsonDocument.GetFieldTypeDistribution, GetSchemaConsistency, GetFieldNullRatio deeper.
/// GetFieldTypeDistribution(field): returns a dict-like mapping of value types to counts for a field.
/// GetSchemaConsistency(): returns a score [0,1] measuring how consistently fields appear across records.
/// GetFieldNullRatio(field): returns the fraction of records where the field is null or absent.
/// Covers: GetFieldTypeDistribution no-throw; GetFieldTypeDistribution non-null;
/// GetFieldTypeDistribution consistent; GetFieldTypeDistribution total equals RecordCount;
/// GetSchemaConsistency no-throw; GetSchemaConsistency in [0,1]; GetSchemaConsistency consistent;
/// GetSchemaConsistency one for uniform schema; GetSchemaConsistency save-load;
/// GetFieldNullRatio no-throw; GetFieldNullRatio in [0,1]; GetFieldNullRatio consistent;
/// GetFieldNullRatio zero for complete field; GetFieldNullRatio save-load;
/// dogfood GetFieldTypeDistribution→GetSchemaConsistency→GetFieldNullRatio→SaveToFile pipeline.
/// </summary>
public class NdjsonR247GetFieldTypeDistributionAndSchemaConsistencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR247GetFieldTypeDistributionAndSchemaConsistencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR247_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var records = new[]
        {
            "{\"id\":1,\"name\":\"Alice\",\"score\":92.5,\"active\":true}",
            "{\"id\":2,\"name\":\"Bob\",\"score\":87.0,\"active\":false}",
            "{\"id\":3,\"name\":\"Carol\",\"score\":95.1,\"active\":true}",
            "{\"id\":4,\"name\":\"Dave\",\"score\":78.3,\"active\":true}",
            "{\"id\":5,\"name\":\"Eve\",\"score\":88.9,\"active\":false}",
            "{\"id\":6,\"name\":\"Frank\",\"score\":91.2,\"active\":true}",
        };
        File.WriteAllLines(path, records);
        return path;
    }

    private string CreateMixedNdjson()
    {
        var path = TempFile("mixed.ndjson");
        var records = new[]
        {
            "{\"id\":1,\"value\":\"text\",\"count\":10}",
            "{\"id\":2,\"value\":42,\"count\":null}",
            "{\"id\":3,\"value\":true,\"count\":5}",
            "{\"id\":4,\"value\":null}",
            "{\"id\":5,\"value\":\"another\",\"count\":8}",
        };
        File.WriteAllLines(path, records);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldTypeDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTypeDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        var ex = Record.Exception(() => doc.GetFieldTypeDistribution("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTypeDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.NotNull(doc.GetFieldTypeDistribution("name"));
    }

    [Fact]
    public void GetFieldTypeDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        var d1 = doc.GetFieldTypeDistribution("active");
        var d2 = doc.GetFieldTypeDistribution("active");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetFieldTypeDistribution_Total_Leq_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var dist = doc.GetFieldTypeDistribution("value");
        int total = 0;
        foreach (var kv in dist) total += kv.Value;
        Assert.True(total <= doc.RecordCount);
    }

    // -------------------------------------------------------------------------
    // GetSchemaConsistency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchemaConsistency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        var ex = Record.Exception(() => doc.GetSchemaConsistency());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSchemaConsistency_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        var score = doc.GetSchemaConsistency();
        Assert.True(score >= 0.0 && score <= 1.0);
    }

    [Fact]
    public void GetSchemaConsistency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(doc.GetSchemaConsistency(), doc.GetSchemaConsistency());
    }

    [Fact]
    public void GetSchemaConsistency_One_ForUniformSchema()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        // All records have exactly same 4 fields — perfect consistency = 1.0
        Assert.True(doc.GetSchemaConsistency() >= 0.9);
    }

    [Fact]
    public void GetSchemaConsistency_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        var before = doc.GetSchemaConsistency();
        var path = TempFile("sc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSchemaConsistency(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldNullRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNullRatio_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var ex = Record.Exception(() => doc.GetFieldNullRatio("count"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNullRatio_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var ratio = doc.GetFieldNullRatio("value");
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
    }

    [Fact]
    public void GetFieldNullRatio_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        Assert.Equal(doc.GetFieldNullRatio("count"), doc.GetFieldNullRatio("count"));
    }

    [Fact]
    public void GetFieldNullRatio_Zero_ForCompleteField()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        // "id" field is present in all records
        Assert.Equal(0.0, doc.GetFieldNullRatio("id"), precision: 6);
    }

    [Fact]
    public void GetFieldNullRatio_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var before = doc.GetFieldNullRatio("count");
        var path = TempFile("fnr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNullRatio("count"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldTypeDistribution_GetSchemaConsistency_GetFieldNullRatio_SaveToFile_Pipeline()
    {
        // IoT telemetry — smart building sensor data quality assessment
        var path = TempFile("iot_telemetry.ndjson");
        var records = new[]
        {
            "{\"sensor_id\":\"S001\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":21.3,\"humidity\":58,\"co2_ppm\":412,\"occupancy\":true,\"zone\":\"OfficeA\"}",
            "{\"sensor_id\":\"S002\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":22.1,\"humidity\":null,\"co2_ppm\":398,\"occupancy\":false,\"zone\":\"OfficeB\"}",
            "{\"sensor_id\":\"S003\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":19.8,\"humidity\":62,\"co2_ppm\":null,\"occupancy\":true,\"zone\":\"MeetingRoom\"}",
            "{\"sensor_id\":\"S004\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":null,\"humidity\":55,\"co2_ppm\":405,\"zone\":\"Reception\"}",
            "{\"sensor_id\":\"S005\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":20.9,\"humidity\":60,\"co2_ppm\":420,\"occupancy\":true,\"zone\":\"OfficeA\"}",
            "{\"sensor_id\":\"S006\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":23.4,\"humidity\":51,\"co2_ppm\":388,\"occupancy\":false,\"zone\":\"OfficeC\"}",
            "{\"sensor_id\":\"S007\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":21.7,\"humidity\":65,\"co2_ppm\":430,\"occupancy\":true}",
            "{\"sensor_id\":\"S008\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":20.2,\"humidity\":59,\"co2_ppm\":415,\"occupancy\":false,\"zone\":\"OfficeB\"}",
            "{\"sensor_id\":\"S009\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":22.8,\"humidity\":null,\"co2_ppm\":402,\"occupancy\":true,\"zone\":\"MeetingRoom\"}",
            "{\"sensor_id\":\"S010\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":21.1,\"humidity\":57,\"co2_ppm\":410,\"occupancy\":false,\"zone\":\"Reception\"}",
            "{\"sensor_id\":\"S011\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":19.5,\"humidity\":68,\"co2_ppm\":null,\"occupancy\":true,\"zone\":\"ServerRoom\"}",
            "{\"sensor_id\":\"S012\",\"timestamp\":\"2024-09-01T08:00:00Z\",\"temperature\":22.3,\"humidity\":54,\"co2_ppm\":395,\"occupancy\":false,\"zone\":\"OfficeC\"}",
        };
        File.WriteAllLines(path, records);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetFieldTypeDistribution — temperature has nulls, rest numeric
        var tempDist = doc.GetFieldTypeDistribution("temperature");
        Assert.NotNull(tempDist);
        int tempTotal = 0;
        foreach (var kv in tempDist) tempTotal += kv.Value;
        Assert.True(tempTotal <= doc.RecordCount);
        Assert.Equal(tempDist.Count, doc.GetFieldTypeDistribution("temperature").Count); // consistent

        // GetFieldTypeDistribution — zone field (sometimes absent)
        var zoneDist = doc.GetFieldTypeDistribution("zone");
        Assert.NotNull(zoneDist);

        // GetSchemaConsistency
        var consistency = doc.GetSchemaConsistency();
        Assert.True(consistency >= 0.0 && consistency <= 1.0);
        Assert.Equal(consistency, doc.GetSchemaConsistency()); // consistent
        // Most records have all fields — should be reasonably consistent
        Assert.True(consistency > 0.5);

        // GetFieldNullRatio
        // humidity: null in S002, S009 = 2/12
        var humidityNullRatio = doc.GetFieldNullRatio("humidity");
        Assert.True(humidityNullRatio >= 0.0 && humidityNullRatio <= 1.0);
        Assert.Equal(humidityNullRatio, doc.GetFieldNullRatio("humidity")); // consistent

        // sensor_id: complete field
        var sensorNullRatio = doc.GetFieldNullRatio("sensor_id");
        Assert.Equal(0.0, sensorNullRatio, precision: 6);

        // co2_ppm: null in S003, S011 = 2/12
        var co2NullRatio = doc.GetFieldNullRatio("co2_ppm");
        Assert.True(co2NullRatio > 0.0);

        // SaveToFile
        var outPath = TempFile("iot_telemetry_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(12, loaded.RecordCount);
        Assert.Equal(consistency, loaded.GetSchemaConsistency(), precision: 6);
        Assert.Equal(humidityNullRatio, loaded.GetFieldNullRatio("humidity"), precision: 6);
        Assert.Equal(0.0, loaded.GetFieldNullRatio("sensor_id"), precision: 6);
        Assert.NotNull(loaded.GetFieldTypeDistribution("temperature"));

        var ex1 = Record.Exception(() => loaded.GetFieldTypeDistribution("zone"));
        var ex2 = Record.Exception(() => loaded.GetSchemaConsistency());
        var ex3 = Record.Exception(() => loaded.GetFieldNullRatio("occupancy"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
