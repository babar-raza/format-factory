// Tests for NdjsonDocument.GetRecordValidationCount, GetSchemaConformanceRate, GetInvalidRecordIndices deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R254

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R254: Tests for NdjsonDocument.GetRecordValidationCount, GetSchemaConformanceRate, GetInvalidRecordIndices deeper.
/// GetRecordValidationCount(fieldName): returns the number of records where the specified field is present and non-null.
/// GetSchemaConformanceRate(requiredFields): returns the fraction of records conforming to the required fields schema.
/// GetInvalidRecordIndices(fieldName): returns a list of record indices where the specified field is missing or null.
/// Covers: GetRecordValidationCount no-throw; GetRecordValidationCount non-negative;
/// GetRecordValidationCount ≤ RecordCount; GetRecordValidationCount consistent;
/// GetSchemaConformanceRate no-throw; GetSchemaConformanceRate in [0,1];
/// GetSchemaConformanceRate 1.0 for fully conformant; GetSchemaConformanceRate consistent;
/// GetInvalidRecordIndices no-throw; GetInvalidRecordIndices non-null;
/// GetInvalidRecordIndices count + valid count = RecordCount; GetInvalidRecordIndices save-load;
/// dogfood CreateDoc→GetRecordValidationCount→GetSchemaConformanceRate→GetInvalidRecordIndices pipeline.
/// </summary>
public class NdjsonR254GetRecordValidationAndSchemaConformanceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR254GetRecordValidationAndSchemaConformanceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR254_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMixedNdjson()
    {
        // Some records have all fields, some are missing optional/required fields
        var path = TempFile("mixed.ndjson");
        var lines = new string[]
        {
            "{\"id\":\"R001\",\"name\":\"Alpha\",\"value\":100,\"status\":\"active\"}",
            "{\"id\":\"R002\",\"name\":\"Beta\",\"value\":200}",                   // missing status
            "{\"id\":\"R003\",\"name\":\"Gamma\",\"status\":\"inactive\"}",        // missing value
            "{\"id\":\"R004\",\"value\":400,\"status\":\"active\"}",               // missing name
            "{\"id\":\"R005\",\"name\":\"Epsilon\",\"value\":500,\"status\":\"active\"}",
            "{\"id\":\"R006\",\"name\":\"Zeta\",\"value\":600,\"status\":\"inactive\"}",
            "{\"id\":\"R007\",\"name\":\"Eta\",\"value\":700,\"status\":\"active\"}",
            "{\"id\":\"R008\",\"name\":\"Theta\",\"value\":null,\"status\":\"active\"}",  // null value
            "{\"id\":\"R009\",\"name\":\"Iota\",\"value\":900,\"status\":\"active\"}",
            "{\"id\":\"R010\",\"name\":\"Kappa\",\"value\":1000,\"status\":\"inactive\"}",
            "{\"id\":\"R011\",\"name\":\"Lambda\",\"value\":1100,\"status\":\"active\"}",
            "{\"id\":\"R012\",\"name\":\"Mu\",\"value\":1200,\"status\":\"active\"}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateFullNdjson()
    {
        var path = TempFile("full.ndjson");
        var lines = new string[]
        {
            "{\"id\":\"A1\",\"name\":\"One\",\"score\":10}",
            "{\"id\":\"A2\",\"name\":\"Two\",\"score\":20}",
            "{\"id\":\"A3\",\"name\":\"Three\",\"score\":30}",
            "{\"id\":\"A4\",\"name\":\"Four\",\"score\":40}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordValidationCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordValidationCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var ex = Record.Exception(() => doc.GetRecordValidationCount("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordValidationCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        Assert.True(doc.GetRecordValidationCount("value") >= 0);
    }

    [Fact]
    public void GetRecordValidationCount_LessOrEqual_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        Assert.True(doc.GetRecordValidationCount("value") <= doc.RecordCount);
    }

    [Fact]
    public void GetRecordValidationCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        Assert.Equal(doc.GetRecordValidationCount("status"), doc.GetRecordValidationCount("status"));
    }

    // -------------------------------------------------------------------------
    // GetSchemaConformanceRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSchemaConformanceRate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var ex = Record.Exception(() => doc.GetSchemaConformanceRate(new[] { "id", "name", "value", "status" }));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSchemaConformanceRate_In_Range()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var rate = doc.GetSchemaConformanceRate(new[] { "id", "name", "value", "status" });
        Assert.True(rate >= 0.0 && rate <= 1.0);
    }

    [Fact]
    public void GetSchemaConformanceRate_One_For_Fully_Conformant()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullNdjson());
        Assert.Equal(1.0, doc.GetSchemaConformanceRate(new[] { "id", "name", "score" }), precision: 6);
    }

    [Fact]
    public void GetSchemaConformanceRate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var fields = new[] { "id", "value" };
        Assert.Equal(doc.GetSchemaConformanceRate(fields), doc.GetSchemaConformanceRate(fields));
    }

    // -------------------------------------------------------------------------
    // GetInvalidRecordIndices
    // -------------------------------------------------------------------------

    [Fact]
    public void GetInvalidRecordIndices_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var ex = Record.Exception(() => doc.GetInvalidRecordIndices("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetInvalidRecordIndices_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        Assert.NotNull(doc.GetInvalidRecordIndices("value"));
    }

    [Fact]
    public void GetInvalidRecordIndices_Plus_Valid_Equals_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var invalid = doc.GetInvalidRecordIndices("value");
        var valid = doc.GetRecordValidationCount("value");
        Assert.Equal(doc.RecordCount, invalid.Count + valid);
    }

    [Fact]
    public void GetInvalidRecordIndices_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMixedNdjson());
        var before = doc.GetInvalidRecordIndices("status").Count;
        var path = TempFile("inv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetInvalidRecordIndices("status").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordValidationCount_GetSchemaConformanceRate_GetInvalidRecordIndices_Pipeline()
    {
        // Data quality monitoring — IoT sensor telemetry stream with partial record failures
        var path = TempFile("iot_telemetry.ndjson");
        var lines = new System.Collections.Generic.List<string>();
        var rng = new Random(20250201);
        string[] sensors = { "TEMP_01", "TEMP_02", "HUMID_01", "PRESS_01", "CO2_01", "LIGHT_01" };
        for (int i = 0; i < 150; i++)
        {
            string sensor = sensors[i % 6];
            bool hasCoreFields = rng.NextDouble() > 0.1; // 90% have all core fields
            bool hasQuality = rng.NextDouble() > 0.15;   // 85% have quality indicator

            var sb = new System.Text.StringBuilder();
            sb.Append("{");
            sb.Append($"\"message_id\":\"MSG{i:D6}\"");
            sb.Append($",\"sensor_id\":\"{sensor}\"");
            sb.Append($",\"timestamp\":\"2024-01-{(i % 28 + 1):D2}T{(i % 24):D2}:00:00Z\"");

            if (hasCoreFields)
            {
                double value = sensor.StartsWith("TEMP") ? 15 + rng.NextDouble() * 25 :
                               sensor.StartsWith("HUMID") ? 30 + rng.NextDouble() * 60 :
                               sensor.StartsWith("PRESS") ? 990 + rng.NextDouble() * 30 :
                               sensor.StartsWith("CO2") ? 400 + rng.NextDouble() * 800 :
                               rng.NextDouble() * 1000;
                sb.Append($",\"reading\":{value:F2}");
                sb.Append($",\"unit\":\"{(sensor.StartsWith("TEMP") ? "C" : sensor.StartsWith("HUMID") ? "pct" : "hPa")}\"");
            }

            if (hasQuality)
                sb.Append($",\"quality\":{(rng.NextDouble() > 0.05 ? "\"GOOD\"" : "\"BAD\"")}");

            sb.Append("}");
            lines.Add(sb.ToString());
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150, doc.RecordCount);

        // GetRecordValidationCount — reading field (90% complete)
        var validReading = doc.GetRecordValidationCount("reading");
        Assert.True(validReading >= 0 && validReading <= doc.RecordCount);
        Assert.Equal(validReading, doc.GetRecordValidationCount("reading")); // consistent

        // GetRecordValidationCount — quality field (85% complete)
        var validQuality = doc.GetRecordValidationCount("quality");
        Assert.True(validQuality >= 0 && validQuality <= doc.RecordCount);

        // GetSchemaConformanceRate — minimal required fields
        var coreRate = doc.GetSchemaConformanceRate(new[] { "message_id", "sensor_id", "timestamp" });
        Assert.True(coreRate >= 0.0 && coreRate <= 1.0);
        Assert.Equal(coreRate, doc.GetSchemaConformanceRate(new[] { "message_id", "sensor_id", "timestamp" })); // consistent

        // Full schema rate (reading + quality)
        var fullRate = doc.GetSchemaConformanceRate(new[] { "message_id", "sensor_id", "timestamp", "reading", "quality" });
        Assert.True(fullRate >= 0.0 && fullRate <= coreRate);

        // GetInvalidRecordIndices — reading field
        var invalidReading = doc.GetInvalidRecordIndices("reading");
        Assert.NotNull(invalidReading);
        Assert.Equal(doc.RecordCount, invalidReading.Count + validReading);
        Assert.Equal(invalidReading.Count, doc.GetInvalidRecordIndices("reading").Count); // consistent

        // GetInvalidRecordIndices — quality field
        var invalidQuality = doc.GetInvalidRecordIndices("quality");
        Assert.NotNull(invalidQuality);
        Assert.Equal(doc.RecordCount, invalidQuality.Count + validQuality);

        // SaveToFile
        var outPath = TempFile("iot_telemetry_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(validReading, loaded.GetRecordValidationCount("reading"));
        Assert.Equal(coreRate, loaded.GetSchemaConformanceRate(new[] { "message_id", "sensor_id", "timestamp" }), precision: 6);
        Assert.Equal(invalidReading.Count, loaded.GetInvalidRecordIndices("reading").Count);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // Additional stats
        var uniqueSensors = doc.GetFieldUniqueValues("sensor_id");
        Assert.NotNull(uniqueSensors);
        Assert.True(uniqueSensors.Count > 0);
    }
}
