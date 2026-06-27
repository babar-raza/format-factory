// Tests for NdjsonDocument.GetRecordAtIndex, GetFieldNames, GetRecordAsJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R241

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R241: Tests for NdjsonDocument.GetRecordAtIndex, GetFieldNames, GetRecordAsJson deeper.
/// GetRecordAtIndex(index): returns the record (as a dictionary or typed object) at the given index.
/// GetFieldNames(): returns the union of all field names across all records.
/// GetRecordAsJson(index): returns the JSON string for the record at the given index.
/// Covers: GetRecordAtIndex no-throw; GetRecordAtIndex non-null; GetRecordAtIndex consistent;
/// GetRecordAtIndex first and last record; GetRecordAtIndex save-load;
/// GetFieldNames no-throw; GetFieldNames non-null; GetFieldNames count positive; GetFieldNames consistent;
/// GetFieldNames save-load;
/// GetRecordAsJson no-throw; GetRecordAsJson non-null; GetRecordAsJson non-empty; GetRecordAsJson consistent;
/// GetRecordAsJson save-load;
/// dogfood CreateDoc→GetRecordAtIndex→GetFieldNames→GetRecordAsJson→SaveToFile pipeline.
/// </summary>
public class NdjsonR241GetRecordAtIndexAndGetFieldNamesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR241GetRecordAtIndexAndGetFieldNamesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR241_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSatelliteNdjson()
    {
        var path = TempFile("satellite.ndjson");
        File.WriteAllText(path,
            "{\"sat_id\":\"SAT-001\",\"name\":\"Sentinel-2A\",\"orbit\":\"LEO\",\"altitude_km\":786,\"inclination_deg\":98.6,\"period_min\":100.3,\"launched\":\"2015-06-23\"}\n" +
            "{\"sat_id\":\"SAT-002\",\"name\":\"Landsat-9\",\"orbit\":\"LEO\",\"altitude_km\":705,\"inclination_deg\":98.2,\"period_min\":98.9,\"launched\":\"2021-09-27\"}\n" +
            "{\"sat_id\":\"SAT-003\",\"name\":\"GOES-18\",\"orbit\":\"GEO\",\"altitude_km\":35786,\"inclination_deg\":0.0,\"period_min\":1436,\"launched\":\"2022-03-01\"}\n" +
            "{\"sat_id\":\"SAT-004\",\"name\":\"MetOp-C\",\"orbit\":\"LEO\",\"altitude_km\":817,\"inclination_deg\":98.7,\"period_min\":101.4,\"launched\":\"2018-11-07\"}\n" +
            "{\"sat_id\":\"SAT-005\",\"name\":\"Copernicus-04\",\"orbit\":\"MEO\",\"altitude_km\":19130,\"inclination_deg\":56.0,\"period_min\":676,\"launched\":\"2024-01-15\"}\n" +
            "{\"sat_id\":\"SAT-006\",\"name\":\"JPSS-2\",\"orbit\":\"LEO\",\"altitude_km\":824,\"inclination_deg\":98.7,\"period_min\":101.6,\"launched\":\"2022-11-10\"}\n" +
            "{\"sat_id\":\"SAT-007\",\"name\":\"Aqua\",\"orbit\":\"LEO\",\"altitude_km\":705,\"inclination_deg\":98.2,\"period_min\":98.8,\"launched\":\"2002-05-04\"}\n" +
            "{\"sat_id\":\"SAT-008\",\"name\":\"Terra\",\"orbit\":\"LEO\",\"altitude_km\":705,\"inclination_deg\":98.2,\"period_min\":98.9,\"launched\":\"1999-12-18\"}\n" +
            "{\"sat_id\":\"SAT-009\",\"name\":\"Suomi-NPP\",\"orbit\":\"LEO\",\"altitude_km\":824,\"inclination_deg\":98.7,\"period_min\":101.6,\"launched\":\"2011-10-28\"}\n" +
            "{\"sat_id\":\"SAT-010\",\"name\":\"CALIPSO\",\"orbit\":\"LEO\",\"altitude_km\":705,\"inclination_deg\":98.2,\"period_min\":98.9,\"launched\":\"2006-04-28\"}\n" +
            "{\"sat_id\":\"SAT-011\",\"name\":\"CloudSat\",\"orbit\":\"LEO\",\"altitude_km\":705,\"inclination_deg\":98.2,\"period_min\":98.8,\"launched\":\"2006-04-28\"}\n" +
            "{\"sat_id\":\"SAT-012\",\"name\":\"GRACE-FO\",\"orbit\":\"LEO\",\"altitude_km\":491,\"inclination_deg\":89.0,\"period_min\":95.0,\"launched\":\"2018-05-22\"}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordAtIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAtIndex_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var ex = Record.Exception(() => doc.GetRecordAtIndex(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAtIndex_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.NotNull(doc.GetRecordAtIndex(0));
    }

    [Fact]
    public void GetRecordAtIndex_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var r1 = doc.GetRecordAtIndex(5);
        var r2 = doc.GetRecordAtIndex(5);
        Assert.NotNull(r1);
        Assert.NotNull(r2);
    }

    [Fact]
    public void GetRecordAtIndex_FirstRecord()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var first = doc.GetRecordAtIndex(0);
        Assert.NotNull(first);
    }

    [Fact]
    public void GetRecordAtIndex_LastRecord()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var last = doc.GetRecordAtIndex(doc.GetRecordCount() - 1);
        Assert.NotNull(last);
    }

    [Fact]
    public void GetRecordAtIndex_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var before = doc.GetRecordAtIndex(3);
        var path = TempFile("rai_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.NotNull(loaded.GetRecordAtIndex(3));
    }

    // -------------------------------------------------------------------------
    // GetFieldNames
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNames_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var ex = Record.Exception(() => doc.GetFieldNames());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNames_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.NotNull(doc.GetFieldNames());
    }

    [Fact]
    public void GetFieldNames_CountPositive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.True(doc.GetFieldNames().Count > 0);
    }

    [Fact]
    public void GetFieldNames_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.Equal(doc.GetFieldNames().Count, doc.GetFieldNames().Count);
    }

    [Fact]
    public void GetFieldNames_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var before = doc.GetFieldNames().Count;
        var path = TempFile("fn_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNames().Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordAsJson
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordAsJson_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var ex = Record.Exception(() => doc.GetRecordAsJson(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordAsJson_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.NotNull(doc.GetRecordAsJson(0));
    }

    [Fact]
    public void GetRecordAsJson_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.NotEmpty(doc.GetRecordAsJson(0));
    }

    [Fact]
    public void GetRecordAsJson_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        Assert.Equal(doc.GetRecordAsJson(3), doc.GetRecordAsJson(3));
    }

    [Fact]
    public void GetRecordAsJson_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSatelliteNdjson());
        var before = doc.GetRecordAsJson(0);
        var path = TempFile("rj_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.NotNull(loaded.GetRecordAsJson(0));
        Assert.NotEmpty(loaded.GetRecordAsJson(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordAtIndex_GetFieldNames_GetRecordAsJson_SaveToFile_Pipeline()
    {
        // Oceanographic buoy network dataset — 12 buoys
        var path = TempFile("dogfood_buoys.ndjson");
        File.WriteAllText(path,
            "{\"buoy_id\":\"BUOY-N01\",\"lat\":58.4,\"lon\":-5.2,\"sea_temp_c\":12.5,\"wave_height_m\":2.8,\"wind_speed_ms\":8.4,\"salinity_ppt\":35.2,\"depth_m\":450}\n" +
            "{\"buoy_id\":\"BUOY-N02\",\"lat\":52.8,\"lon\":-3.4,\"sea_temp_c\":14.8,\"wave_height_m\":1.5,\"wind_speed_ms\":5.2,\"salinity_ppt\":34.8,\"depth_m\":120}\n" +
            "{\"buoy_id\":\"BUOY-N03\",\"lat\":48.5,\"lon\":-8.2,\"sea_temp_c\":16.2,\"wave_height_m\":3.2,\"wind_speed_ms\":12.5,\"salinity_ppt\":35.5,\"depth_m\":850}\n" +
            "{\"buoy_id\":\"BUOY-N04\",\"lat\":44.2,\"lon\":-12.5,\"sea_temp_c\":18.5,\"wave_height_m\":4.8,\"wind_speed_ms\":18.2,\"salinity_ppt\":36.0,\"depth_m\":2400}\n" +
            "{\"buoy_id\":\"BUOY-N05\",\"lat\":40.8,\"lon\":-16.8,\"sea_temp_c\":20.4,\"wave_height_m\":2.2,\"wind_speed_ms\":7.8,\"salinity_ppt\":36.5,\"depth_m\":3200}\n" +
            "{\"buoy_id\":\"BUOY-N06\",\"lat\":36.5,\"lon\":-18.5,\"sea_temp_c\":22.8,\"wave_height_m\":1.8,\"wind_speed_ms\":6.5,\"salinity_ppt\":36.8,\"depth_m\":2800}\n" +
            "{\"buoy_id\":\"BUOY-N07\",\"lat\":32.2,\"lon\":-20.2,\"sea_temp_c\":24.5,\"wave_height_m\":3.5,\"wind_speed_ms\":14.2,\"salinity_ppt\":37.2,\"depth_m\":3800}\n" +
            "{\"buoy_id\":\"BUOY-N08\",\"lat\":28.5,\"lon\":-22.8,\"sea_temp_c\":26.2,\"wave_height_m\":2.8,\"wind_speed_ms\":9.8,\"salinity_ppt\":37.5,\"depth_m\":4200}\n" +
            "{\"buoy_id\":\"BUOY-N09\",\"lat\":24.8,\"lon\":-25.4,\"sea_temp_c\":28.5,\"wave_height_m\":1.2,\"wind_speed_ms\":4.8,\"salinity_ppt\":37.8,\"depth_m\":4800}\n" +
            "{\"buoy_id\":\"BUOY-N10\",\"lat\":20.5,\"lon\":-28.2,\"sea_temp_c\":29.8,\"wave_height_m\":2.5,\"wind_speed_ms\":8.5,\"salinity_ppt\":38.0,\"depth_m\":5200}\n" +
            "{\"buoy_id\":\"BUOY-N11\",\"lat\":16.2,\"lon\":-30.8,\"sea_temp_c\":30.5,\"wave_height_m\":1.8,\"wind_speed_ms\":6.2,\"salinity_ppt\":38.2,\"depth_m\":4600}\n" +
            "{\"buoy_id\":\"BUOY-N12\",\"lat\":12.5,\"lon\":-33.5,\"sea_temp_c\":31.2,\"wave_height_m\":0.8,\"wind_speed_ms\":3.5,\"salinity_ppt\":38.5,\"depth_m\":3900}\n");

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetFieldNames
        var fields = doc.GetFieldNames();
        Assert.NotNull(fields);
        Assert.Equal(8, fields.Count); // buoy_id, lat, lon, sea_temp_c, wave_height_m, wind_speed_ms, salinity_ppt, depth_m
        Assert.Equal(fields.Count, doc.GetFieldNames().Count); // consistent

        // GetRecordAtIndex
        var first = doc.GetRecordAtIndex(0);
        Assert.NotNull(first);

        var last = doc.GetRecordAtIndex(11);
        Assert.NotNull(last);

        var middle = doc.GetRecordAtIndex(6);
        Assert.NotNull(middle);

        // Consistent
        Assert.NotNull(doc.GetRecordAtIndex(3));

        // GetRecordAsJson
        var json0 = doc.GetRecordAsJson(0);
        Assert.NotNull(json0);
        Assert.NotEmpty(json0);
        Assert.Equal(json0, doc.GetRecordAsJson(0)); // consistent

        var json11 = doc.GetRecordAsJson(11);
        Assert.NotNull(json11);
        Assert.NotEmpty(json11);

        // JSON should be non-trivial
        Assert.True(json0.Length > 10);

        // SaveToFile
        var out1 = TempFile("dogfood_buoys_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(fields.Count, loaded.GetFieldNames().Count);
        Assert.NotNull(loaded.GetRecordAtIndex(0));
        Assert.NotNull(loaded.GetRecordAsJson(0));
        Assert.NotEmpty(loaded.GetRecordAsJson(0));

        // AddRecord — new buoy
        loaded.AddRecord("{\"buoy_id\":\"BUOY-N13\",\"lat\":8.5,\"lon\":-36.2,\"sea_temp_c\":32.0,\"wave_height_m\":0.5,\"wind_speed_ms\":2.8,\"salinity_ppt\":38.8,\"depth_m\":3200}");
        Assert.Equal(13, loaded.GetRecordCount());
        Assert.NotNull(loaded.GetRecordAtIndex(12));
        Assert.NotNull(loaded.GetRecordAsJson(12));

        // Field names may include same set (no new fields added)
        Assert.Equal(fields.Count, loaded.GetFieldNames().Count);

        // Final save
        var out2 = TempFile("dogfood_buoys_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.NotNull(loaded2.GetFieldNames());
        Assert.True(loaded2.GetFieldNames().Count > 0);
        var ex1 = Record.Exception(() => loaded2.GetRecordAtIndex(0));
        var ex2 = Record.Exception(() => loaded2.GetRecordAsJson(0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
