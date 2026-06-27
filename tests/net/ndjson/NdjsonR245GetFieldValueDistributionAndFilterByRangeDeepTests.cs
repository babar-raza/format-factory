// Tests for NdjsonDocument.GetFieldValueDistribution, FilterByNumericRange, GetNumericFieldStats deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R245

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R245: Tests for NdjsonDocument.GetFieldValueDistribution, FilterByNumericRange, GetNumericFieldStats deeper.
/// GetFieldValueDistribution(fieldName): returns a dictionary of value → count for the field.
/// FilterByNumericRange(fieldName, min, max): returns records where the field value is in [min, max].
/// GetNumericFieldStats(fieldName): returns an object with count, sum, min, max, mean, stddev.
/// Covers: GetFieldValueDistribution no-throw; GetFieldValueDistribution non-null; GetFieldValueDistribution consistent;
/// GetFieldValueDistribution total equals record count; GetFieldValueDistribution save-load;
/// FilterByNumericRange no-throw; FilterByNumericRange count leq total; FilterByNumericRange consistent;
/// FilterByNumericRange all for wide range; FilterByNumericRange none for impossible range; FilterByNumericRange save-load;
/// GetNumericFieldStats no-throw; GetNumericFieldStats non-null; GetNumericFieldStats consistent;
/// GetNumericFieldStats mean in range; GetNumericFieldStats save-load;
/// dogfood Append→GetFieldValueDistribution→FilterByNumericRange→GetNumericFieldStats→SaveToFile pipeline.
/// </summary>
public class NdjsonR245GetFieldValueDistributionAndFilterByRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR245GetFieldValueDistributionAndFilterByRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR245_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSensorNdjson()
    {
        var path = TempFile("sensors.ndjson");
        var lines = new[]
        {
            "{\"sensor_id\":\"S001\",\"type\":\"temperature\",\"value\":22.5,\"unit\":\"C\",\"status\":\"Normal\",\"location\":\"Zone-A\"}",
            "{\"sensor_id\":\"S002\",\"type\":\"humidity\",\"value\":58.3,\"unit\":\"%\",\"status\":\"Normal\",\"location\":\"Zone-B\"}",
            "{\"sensor_id\":\"S003\",\"type\":\"temperature\",\"value\":35.2,\"unit\":\"C\",\"status\":\"Warning\",\"location\":\"Zone-A\"}",
            "{\"sensor_id\":\"S004\",\"type\":\"pressure\",\"value\":1013.5,\"unit\":\"hPa\",\"status\":\"Normal\",\"location\":\"Zone-C\"}",
            "{\"sensor_id\":\"S005\",\"type\":\"temperature\",\"value\":20.1,\"unit\":\"C\",\"status\":\"Normal\",\"location\":\"Zone-B\"}",
            "{\"sensor_id\":\"S006\",\"type\":\"humidity\",\"value\":72.8,\"unit\":\"%\",\"status\":\"Warning\",\"location\":\"Zone-C\"}",
            "{\"sensor_id\":\"S007\",\"type\":\"temperature\",\"value\":28.7,\"unit\":\"C\",\"status\":\"Normal\",\"location\":\"Zone-A\"}",
            "{\"sensor_id\":\"S008\",\"type\":\"co2\",\"value\":850.0,\"unit\":\"ppm\",\"status\":\"Warning\",\"location\":\"Zone-B\"}",
            "{\"sensor_id\":\"S009\",\"type\":\"temperature\",\"value\":18.5,\"unit\":\"C\",\"status\":\"Normal\",\"location\":\"Zone-C\"}",
            "{\"sensor_id\":\"S010\",\"type\":\"humidity\",\"value\":45.2,\"unit\":\"%\",\"status\":\"Normal\",\"location\":\"Zone-A\"}",
            "{\"sensor_id\":\"S011\",\"type\":\"co2\",\"value\":420.0,\"unit\":\"ppm\",\"status\":\"Normal\",\"location\":\"Zone-C\"}",
            "{\"sensor_id\":\"S012\",\"type\":\"pressure\",\"value\":1008.2,\"unit\":\"hPa\",\"status\":\"Normal\",\"location\":\"Zone-B\"}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldValueDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueDistribution("type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.NotNull(doc.GetFieldValueDistribution("status"));
    }

    [Fact]
    public void GetFieldValueDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var d1 = doc.GetFieldValueDistribution("type");
        var d2 = doc.GetFieldValueDistribution("type");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetFieldValueDistribution_TotalEqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var dist = doc.GetFieldValueDistribution("type");
        int total = 0;
        foreach (var v in dist.Values) total += v;
        Assert.Equal(doc.RecordCount, total);
    }

    [Fact]
    public void GetFieldValueDistribution_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.GetFieldValueDistribution("location").Count;
        var path = TempFile("fvd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldValueDistribution("location").Count);
    }

    // -------------------------------------------------------------------------
    // FilterByNumericRange
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterByNumericRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.FilterByNumericRange("value", 0, 100));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterByNumericRange_CountLeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var filtered = doc.FilterByNumericRange("value", 20, 40);
        Assert.True(filtered.Count <= doc.RecordCount);
    }

    [Fact]
    public void FilterByNumericRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var f1 = doc.FilterByNumericRange("value", 15, 30);
        var f2 = doc.FilterByNumericRange("value", 15, 30);
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void FilterByNumericRange_AllForWideRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var all = doc.FilterByNumericRange("value", -1000000, 1000000);
        Assert.Equal(doc.RecordCount, all.Count);
    }

    [Fact]
    public void FilterByNumericRange_NoneForImpossibleRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var none = doc.FilterByNumericRange("value", 99999, 99999.9);
        Assert.Empty(none);
    }

    [Fact]
    public void FilterByNumericRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.FilterByNumericRange("value", 0, 100).Count;
        var path = TempFile("fbr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.FilterByNumericRange("value", 0, 100).Count);
    }

    // -------------------------------------------------------------------------
    // GetNumericFieldStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericFieldStats_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetNumericFieldStats("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNumericFieldStats_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.NotNull(doc.GetNumericFieldStats("value"));
    }

    [Fact]
    public void GetNumericFieldStats_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var s1 = doc.GetNumericFieldStats("value");
        var s2 = doc.GetNumericFieldStats("value");
        Assert.Equal(s1.Mean, s2.Mean, precision: 4);
    }

    [Fact]
    public void GetNumericFieldStats_MeanInRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var stats = doc.GetNumericFieldStats("value");
        Assert.True(stats.Mean >= stats.Min);
        Assert.True(stats.Mean <= stats.Max);
    }

    [Fact]
    public void GetNumericFieldStats_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.GetNumericFieldStats("value").Mean;
        var path = TempFile("nfs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNumericFieldStats("value").Mean, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldValueDistribution_FilterByNumericRange_GetNumericFieldStats_SaveToFile_Pipeline()
    {
        // Supply chain analytics — container port throughput and vessel tracking
        var path = TempFile("dogfood_port.ndjson");
        var lines = new[]
        {
            "{\"vessel_id\":\"V001\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":18000,\"teu_loaded\":15840,\"load_factor\":0.88,\"berth_hours\":18.5,\"port\":\"Shanghai\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V002\",\"flag\":\"Liberia\",\"vessel_type\":\"BulkCarrier\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":24.2,\"port\":\"Rotterdam\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V003\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":24000,\"teu_loaded\":22080,\"load_factor\":0.92,\"berth_hours\":22.1,\"port\":\"Singapore\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V004\",\"flag\":\"Marshall\",\"vessel_type\":\"Tanker\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":16.8,\"port\":\"Busan\",\"status\":\"InProgress\"}",
            "{\"vessel_id\":\"V005\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":14500,\"teu_loaded\":11600,\"load_factor\":0.80,\"berth_hours\":15.3,\"port\":\"Shanghai\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V006\",\"flag\":\"Bahamas\",\"vessel_type\":\"RORO\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":12.5,\"port\":\"Rotterdam\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V007\",\"flag\":\"Liberia\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":20000,\"teu_loaded\":18600,\"load_factor\":0.93,\"berth_hours\":20.8,\"port\":\"Singapore\",\"status\":\"InProgress\"}",
            "{\"vessel_id\":\"V008\",\"flag\":\"Marshall\",\"vessel_type\":\"BulkCarrier\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":30.2,\"port\":\"Shanghai\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V009\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":8500,\"teu_loaded\":7225,\"load_factor\":0.85,\"berth_hours\":10.2,\"port\":\"Busan\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V010\",\"flag\":\"Bahamas\",\"vessel_type\":\"Tanker\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":20.4,\"port\":\"Rotterdam\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V011\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":11500,\"teu_loaded\":9315,\"load_factor\":0.81,\"berth_hours\":14.6,\"port\":\"Singapore\",\"status\":\"Completed\"}",
            "{\"vessel_id\":\"V012\",\"flag\":\"Liberia\",\"vessel_type\":\"RORO\",\"teu_capacity\":0,\"teu_loaded\":0,\"load_factor\":0.0,\"berth_hours\":11.8,\"port\":\"Busan\",\"status\":\"InProgress\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetFieldValueDistribution — vessel_type
        var typeDist = doc.GetFieldValueDistribution("vessel_type");
        Assert.NotNull(typeDist);
        Assert.True(typeDist.Count >= 3);
        // Total counts = 12
        int typeTotal = 0;
        foreach (var v in typeDist.Values) typeTotal += v;
        Assert.Equal(12, typeTotal);
        Assert.Equal(typeDist.Count, doc.GetFieldValueDistribution("vessel_type").Count); // consistent

        // GetFieldValueDistribution — flag (Panama×5, Liberia×3, Marshall×2, Bahamas×2)
        var flagDist = doc.GetFieldValueDistribution("flag");
        Assert.NotNull(flagDist);
        Assert.Equal(4, flagDist.Count);
        int flagTotal = 0;
        foreach (var v in flagDist.Values) flagTotal += v;
        Assert.Equal(12, flagTotal);

        // GetFieldValueDistribution — status (Completed×9, InProgress×3)
        var statusDist = doc.GetFieldValueDistribution("status");
        Assert.NotNull(statusDist);
        Assert.Equal(2, statusDist.Count);

        // FilterByNumericRange — high load factor container ships (0.85 ≤ load_factor ≤ 1.0)
        var highLoad = doc.FilterByNumericRange("load_factor", 0.85, 1.0);
        Assert.True(highLoad.Count >= 0);
        Assert.True(highLoad.Count <= doc.RecordCount);
        Assert.Equal(highLoad.Count, doc.FilterByNumericRange("load_factor", 0.85, 1.0).Count); // consistent

        // FilterByNumericRange — quick berth (under 16 hours)
        var quickBerth = doc.FilterByNumericRange("berth_hours", 0, 16.0);
        Assert.True(quickBerth.Count >= 0);
        Assert.True(quickBerth.Count <= doc.RecordCount);

        // FilterByNumericRange — wide range (all records)
        var allRecords = doc.FilterByNumericRange("berth_hours", 0, 100);
        Assert.Equal(doc.RecordCount, allRecords.Count);

        // FilterByNumericRange — impossible range
        var none = doc.FilterByNumericRange("teu_capacity", 999999, 9999999);
        Assert.Empty(none);

        // GetNumericFieldStats — berth_hours
        var berthStats = doc.GetNumericFieldStats("berth_hours");
        Assert.NotNull(berthStats);
        Assert.True(berthStats.Min >= 0);
        Assert.True(berthStats.Max <= 35);
        Assert.True(berthStats.Mean >= berthStats.Min);
        Assert.True(berthStats.Mean <= berthStats.Max);
        Assert.Equal(berthStats.Mean, doc.GetNumericFieldStats("berth_hours").Mean, precision: 4); // consistent

        // GetNumericFieldStats — teu_capacity
        var teuStats = doc.GetNumericFieldStats("teu_capacity");
        Assert.NotNull(teuStats);
        Assert.True(teuStats.Min >= 0);

        // AppendRecord — additional vessel
        doc.AppendRecord("{\"vessel_id\":\"V013\",\"flag\":\"Panama\",\"vessel_type\":\"ContainerShip\",\"teu_capacity\":22000,\"teu_loaded\":19580,\"load_factor\":0.89,\"berth_hours\":21.4,\"port\":\"Shanghai\",\"status\":\"Completed\"}");
        Assert.Equal(13, doc.RecordCount);

        // After append: distribution sums still match
        var newTypeDist = doc.GetFieldValueDistribution("vessel_type");
        int newTotal = 0;
        foreach (var v in newTypeDist.Values) newTotal += v;
        Assert.Equal(13, newTotal);

        // SaveToFile
        var out1 = TempFile("dogfood_port_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(13, loaded.RecordCount);
        Assert.Equal(typeDist.Count, loaded.GetFieldValueDistribution("vessel_type").Count);
        Assert.Equal(doc.FilterByNumericRange("berth_hours", 0, 20).Count, loaded.FilterByNumericRange("berth_hours", 0, 20).Count);
        Assert.Equal(berthStats.Mean, loaded.GetNumericFieldStats("berth_hours").Mean, precision: 2);

        // Final save
        var out2 = TempFile("dogfood_port_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.RecordCount);
        Assert.NotNull(loaded2.GetFieldValueDistribution("flag"));
        Assert.True(loaded2.FilterByNumericRange("load_factor", 0, 1).Count > 0);
        var ex1 = Record.Exception(() => loaded2.GetNumericFieldStats("teu_capacity"));
        var ex2 = Record.Exception(() => loaded2.GetFieldValueDistribution("status"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
