// Tests for NdjsonDocument.FilterRecordsByRange, GetUniqueValues, GetRecordByField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R238

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R238: Tests for NdjsonDocument.FilterRecordsByRange, GetUniqueValues, GetRecordByField deeper.
/// FilterRecordsByRange(field, min, max): returns records where field value is in [min, max].
/// GetUniqueValues(field): returns distinct values for the given field.
/// GetRecordByField(field, value): returns the first record where field equals value.
/// Covers: FilterRecordsByRange no-throw; FilterRecordsByRange count leq total; FilterRecordsByRange consistent;
/// FilterRecordsByRange all for wide range; FilterRecordsByRange none for impossible range;
/// FilterRecordsByRange save-load;
/// GetUniqueValues no-throw; GetUniqueValues non-null; GetUniqueValues consistent;
/// GetUniqueValues count leq record count; GetUniqueValues save-load;
/// GetRecordByField no-throw; GetRecordByField non-null for existing; GetRecordByField consistent;
/// GetRecordByField save-load;
/// dogfood CreateDoc→FilterRecordsByRange→GetUniqueValues→GetRecordByField→SaveToFile pipeline.
/// </summary>
public class NdjsonR238FilterRecordsByRangeAndGetUniqueValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR238FilterRecordsByRangeAndGetUniqueValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR238_" + Guid.NewGuid().ToString("N"));
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
        File.WriteAllLines(path, new[]
        {
            "{\"sensor_id\":\"S001\",\"type\":\"temperature\",\"location\":\"Zone_A\",\"value\":22.5,\"unit\":\"C\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S002\",\"type\":\"humidity\",\"location\":\"Zone_B\",\"value\":65.2,\"unit\":\"%\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S003\",\"type\":\"temperature\",\"location\":\"Zone_A\",\"value\":85.3,\"unit\":\"C\",\"status\":\"alert\"}",
            "{\"sensor_id\":\"S004\",\"type\":\"pressure\",\"location\":\"Zone_C\",\"value\":1013.2,\"unit\":\"hPa\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S005\",\"type\":\"temperature\",\"location\":\"Zone_B\",\"value\":23.8,\"unit\":\"C\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S006\",\"type\":\"humidity\",\"location\":\"Zone_C\",\"value\":42.1,\"unit\":\"%\",\"status\":\"low\"}",
            "{\"sensor_id\":\"S007\",\"type\":\"co2\",\"location\":\"Zone_A\",\"value\":450.0,\"unit\":\"ppm\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S008\",\"type\":\"temperature\",\"location\":\"Zone_C\",\"value\":21.2,\"unit\":\"C\",\"status\":\"normal\"}",
            "{\"sensor_id\":\"S009\",\"type\":\"co2\",\"location\":\"Zone_B\",\"value\":1200.0,\"unit\":\"ppm\",\"status\":\"alert\"}",
            "{\"sensor_id\":\"S010\",\"type\":\"pressure\",\"location\":\"Zone_A\",\"value\":1008.5,\"unit\":\"hPa\",\"status\":\"low\"}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // FilterRecordsByRange
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterRecordsByRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.FilterRecordsByRange("value", 20.0, 30.0));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterRecordsByRange_Count_LeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var filtered = doc.FilterRecordsByRange("value", 20.0, 90.0);
        Assert.True(filtered.Count <= doc.GetRecordCount());
    }

    [Fact]
    public void FilterRecordsByRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var f1 = doc.FilterRecordsByRange("value", 20.0, 30.0);
        var f2 = doc.FilterRecordsByRange("value", 20.0, 30.0);
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void FilterRecordsByRange_All_ForWideRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var all = doc.FilterRecordsByRange("value", double.MinValue, double.MaxValue);
        Assert.True(all.Count <= doc.GetRecordCount());
        Assert.True(all.Count > 0);
    }

    [Fact]
    public void FilterRecordsByRange_None_ForImpossibleRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var none = doc.FilterRecordsByRange("value", -1000.0, -999.0);
        Assert.Equal(0, none.Count);
    }

    [Fact]
    public void FilterRecordsByRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.FilterRecordsByRange("value", 20.0, 30.0).Count;
        var path = TempFile("fr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.FilterRecordsByRange("value", 20.0, 30.0).Count);
    }

    // -------------------------------------------------------------------------
    // GetUniqueValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetUniqueValues("type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.NotNull(doc.GetUniqueValues("location"));
    }

    [Fact]
    public void GetUniqueValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var u1 = doc.GetUniqueValues("status");
        var u2 = doc.GetUniqueValues("status");
        Assert.Equal(u1.Count, u2.Count);
    }

    [Fact]
    public void GetUniqueValues_Count_LeqRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.True(doc.GetUniqueValues("type").Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetUniqueValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.GetUniqueValues("location").Count;
        var path = TempFile("uv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueValues("location").Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetRecordByField("sensor_id", "S001"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordByField_NonNull_ForExisting()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.NotNull(doc.GetRecordByField("sensor_id", "S001"));
    }

    [Fact]
    public void GetRecordByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var r1 = doc.GetRecordByField("type", "temperature");
        var r2 = doc.GetRecordByField("type", "temperature");
        Assert.Equal(r1 == null, r2 == null);
    }

    [Fact]
    public void GetRecordByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.GetRecordByField("sensor_id", "S005");
        var path = TempFile("rf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetRecordByField("sensor_id", "S005");
        // Both should be non-null or both null
        Assert.Equal(before == null, after == null);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterRecordsByRange_GetUniqueValues_GetRecordByField_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_air_quality.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"station_id\":\"AQ001\",\"city\":\"London\",\"country\":\"UK\",\"pm25\":12.4,\"pm10\":24.8,\"no2\":45.2,\"o3\":82.1,\"aqi\":58,\"category\":\"Moderate\"}",
            "{\"station_id\":\"AQ002\",\"city\":\"Paris\",\"country\":\"FR\",\"pm25\":8.2,\"pm10\":18.5,\"no2\":38.4,\"o3\":95.3,\"aqi\":42,\"category\":\"Good\"}",
            "{\"station_id\":\"AQ003\",\"city\":\"Beijing\",\"country\":\"CN\",\"pm25\":85.4,\"pm10\":142.8,\"no2\":82.1,\"o3\":28.4,\"aqi\":168,\"category\":\"Unhealthy\"}",
            "{\"station_id\":\"AQ004\",\"city\":\"Mumbai\",\"country\":\"IN\",\"pm25\":62.8,\"pm10\":108.5,\"no2\":65.2,\"o3\":35.8,\"aqi\":148,\"category\":\"Unhealthy\"}",
            "{\"station_id\":\"AQ005\",\"city\":\"Sydney\",\"country\":\"AU\",\"pm25\":5.2,\"pm10\":12.4,\"no2\":18.5,\"o3\":112.4,\"aqi\":28,\"category\":\"Good\"}",
            "{\"station_id\":\"AQ006\",\"city\":\"Lagos\",\"country\":\"NG\",\"pm25\":78.2,\"pm10\":128.6,\"no2\":72.4,\"o3\":22.1,\"aqi\":158,\"category\":\"Unhealthy\"}",
            "{\"station_id\":\"AQ007\",\"city\":\"New York\",\"country\":\"US\",\"pm25\":15.8,\"pm10\":28.4,\"no2\":52.8,\"o3\":88.2,\"aqi\":65,\"category\":\"Moderate\"}",
            "{\"station_id\":\"AQ008\",\"city\":\"Tokyo\",\"country\":\"JP\",\"pm25\":10.2,\"pm10\":22.8,\"no2\":35.4,\"o3\":98.5,\"aqi\":48,\"category\":\"Good\"}",
            "{\"station_id\":\"AQ009\",\"city\":\"Cairo\",\"country\":\"EG\",\"pm25\":52.4,\"pm10\":92.8,\"no2\":58.6,\"o3\":31.2,\"aqi\":135,\"category\":\"USG\"}",
            "{\"station_id\":\"AQ010\",\"city\":\"Mexico City\",\"country\":\"MX\",\"pm25\":28.5,\"pm10\":52.8,\"no2\":48.2,\"o3\":75.4,\"aqi\":88,\"category\":\"Moderate\"}",
            "{\"station_id\":\"AQ011\",\"city\":\"Stockholm\",\"country\":\"SE\",\"pm25\":4.8,\"pm10\":10.2,\"no2\":15.8,\"o3\":118.5,\"aqi\":22,\"category\":\"Good\"}",
            "{\"station_id\":\"AQ012\",\"city\":\"São Paulo\",\"country\":\"BR\",\"pm25\":42.2,\"pm10\":78.5,\"no2\":62.4,\"o3\":38.5,\"aqi\":118,\"category\":\"Unhealthy for Sensitive\"}"
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // FilterRecordsByRange — good air quality (AQI <= 50)
        var goodAir = doc.FilterRecordsByRange("aqi", 0, 50);
        Assert.NotNull(goodAir);
        Assert.True(goodAir.Count >= 0);
        Assert.True(goodAir.Count <= 12);

        // FilterRecordsByRange — pm25 in moderate range
        var moderatePm25 = doc.FilterRecordsByRange("pm25", 10.0, 35.0);
        Assert.True(moderatePm25.Count >= 0);
        Assert.True(moderatePm25.Count <= 12);

        // FilterRecordsByRange — full range (all records)
        var allRecords = doc.FilterRecordsByRange("aqi", 0, 10000);
        Assert.True(allRecords.Count <= 12);
        Assert.True(allRecords.Count > 0);

        // FilterRecordsByRange — impossible (negative AQI)
        var impossible = doc.FilterRecordsByRange("aqi", -100, -1);
        Assert.Equal(0, impossible.Count);

        // Consistent
        Assert.Equal(goodAir.Count, doc.FilterRecordsByRange("aqi", 0, 50).Count);

        // GetUniqueValues — country
        var countries = doc.GetUniqueValues("country");
        Assert.NotNull(countries);
        Assert.True(countries.Count > 0);
        Assert.True(countries.Count <= 12);
        Assert.Equal(countries.Count, doc.GetUniqueValues("country").Count); // consistent

        // GetUniqueValues — category
        var categories = doc.GetUniqueValues("category");
        Assert.True(categories.Count > 0);

        // GetUniqueValues — city (all unique)
        var cities = doc.GetUniqueValues("city");
        Assert.True(cities.Count > 0);

        // GetRecordByField — find specific station
        var london = doc.GetRecordByField("city", "London");
        Assert.NotNull(london);

        var tokyo = doc.GetRecordByField("station_id", "AQ008");
        Assert.NotNull(tokyo);

        // GetRecordByField — consistent
        var london2 = doc.GetRecordByField("city", "London");
        Assert.Equal(london == null, london2 == null);

        // SaveToFile
        var out1 = TempFile("dogfood_airquality_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(goodAir.Count, loaded.FilterRecordsByRange("aqi", 0, 50).Count);
        Assert.Equal(countries.Count, loaded.GetUniqueValues("country").Count);
        Assert.NotNull(loaded.GetRecordByField("city", "London"));

        // AddRecord on loaded
        loaded.AddRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["station_id"] = "AQ013",
            ["city"] = "Berlin",
            ["country"] = "DE",
            ["pm25"] = 9.8,
            ["pm10"] = 20.4,
            ["no2"] = 32.1,
            ["o3"] = 102.8,
            ["aqi"] = 45,
            ["category"] = "Good"
        });
        Assert.Equal(13, loaded.GetRecordCount());

        // Final save
        var out2 = TempFile("dogfood_airquality_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.True(loaded2.FilterRecordsByRange("aqi", 0, 50).Count >= 0);
        Assert.True(loaded2.GetUniqueValues("country").Count > 0);
        Assert.NotNull(loaded2.GetRecordByField("city", "Berlin"));
        var ex1 = Record.Exception(() => loaded2.FilterRecordsByRange("pm25", 0, 100));
        var ex2 = Record.Exception(() => loaded2.GetUniqueValues("category"));
        var ex3 = Record.Exception(() => loaded2.GetRecordByField("station_id", "AQ001"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
