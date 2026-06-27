// Tests for NdjsonDocument.GetMostFrequentFieldValue, GetFieldStatistics, GetUniqueFieldValueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R242

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R242: Tests for NdjsonDocument.GetMostFrequentFieldValue, GetFieldStatistics, GetUniqueFieldValueCount deeper.
/// GetMostFrequentFieldValue(fieldName): returns the most common value for the given field across all records.
/// GetFieldStatistics(fieldName): returns an object containing min, max, mean, stddev for numeric fields.
/// GetUniqueFieldValueCount(fieldName): returns the number of distinct values for the given field.
/// Covers: GetMostFrequentFieldValue no-throw; GetMostFrequentFieldValue non-null; GetMostFrequentFieldValue consistent;
/// GetMostFrequentFieldValue correct for known data; GetMostFrequentFieldValue save-load;
/// GetFieldStatistics no-throw; GetFieldStatistics non-null; GetFieldStatistics consistent;
/// GetFieldStatistics mean in range; GetFieldStatistics save-load;
/// GetUniqueFieldValueCount no-throw; GetUniqueFieldValueCount positive; GetUniqueFieldValueCount consistent;
/// GetUniqueFieldValueCount leq record count; GetUniqueFieldValueCount save-load;
/// dogfood Append→GetMostFrequentFieldValue→GetFieldStatistics→GetUniqueFieldValueCount→SaveToFile pipeline.
/// </summary>
public class NdjsonR242GetMostFrequentValueAndFieldStatisticsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR242GetMostFrequentValueAndFieldStatisticsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateFlightDataNdjson()
    {
        // 12 international flight records — airline/route/delay/class
        var path = TempFile("flights.ndjson");
        var lines = new[]
        {
            "{\"flight_id\":\"AA101\",\"airline\":\"American\",\"origin\":\"JFK\",\"dest\":\"LAX\",\"delay_min\":15,\"class\":\"Economy\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"UA202\",\"airline\":\"United\",\"origin\":\"ORD\",\"dest\":\"SFO\",\"delay_min\":0,\"class\":\"Business\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"DL303\",\"airline\":\"Delta\",\"origin\":\"ATL\",\"dest\":\"JFK\",\"delay_min\":45,\"class\":\"Economy\",\"status\":\"Delayed\"}",
            "{\"flight_id\":\"AA404\",\"airline\":\"American\",\"origin\":\"DFW\",\"dest\":\"MIA\",\"delay_min\":10,\"class\":\"First\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"SW505\",\"airline\":\"Southwest\",\"origin\":\"DAL\",\"dest\":\"MDW\",\"delay_min\":0,\"class\":\"Economy\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"AA606\",\"airline\":\"American\",\"origin\":\"LAX\",\"dest\":\"ORD\",\"delay_min\":30,\"class\":\"Economy\",\"status\":\"Delayed\"}",
            "{\"flight_id\":\"UA707\",\"airline\":\"United\",\"origin\":\"SFO\",\"dest\":\"EWR\",\"delay_min\":5,\"class\":\"Business\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"DL808\",\"airline\":\"Delta\",\"origin\":\"MSP\",\"dest\":\"ATL\",\"delay_min\":20,\"class\":\"Economy\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"AA909\",\"airline\":\"American\",\"origin\":\"MIA\",\"dest\":\"BOS\",\"delay_min\":0,\"class\":\"Economy\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"SW010\",\"airline\":\"Southwest\",\"origin\":\"PHX\",\"dest\":\"LAS\",\"delay_min\":0,\"class\":\"Economy\",\"status\":\"On-Time\"}",
            "{\"flight_id\":\"UA111\",\"airline\":\"United\",\"origin\":\"IAD\",\"dest\":\"LAX\",\"delay_min\":60,\"class\":\"First\",\"status\":\"Delayed\"}",
            "{\"flight_id\":\"DL212\",\"airline\":\"Delta\",\"origin\":\"SEA\",\"dest\":\"SLC\",\"delay_min\":5,\"class\":\"Economy\",\"status\":\"On-Time\"}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMostFrequentFieldValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMostFrequentFieldValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var ex = Record.Exception(() => doc.GetMostFrequentFieldValue("airline"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMostFrequentFieldValue_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        Assert.NotNull(doc.GetMostFrequentFieldValue("airline"));
    }

    [Fact]
    public void GetMostFrequentFieldValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var v1 = doc.GetMostFrequentFieldValue("airline");
        var v2 = doc.GetMostFrequentFieldValue("airline");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetMostFrequentFieldValue_Correct_ForKnownData()
    {
        // American appears 4 times — most frequent airline
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var most = doc.GetMostFrequentFieldValue("airline");
        Assert.Equal("American", most);
    }

    [Fact]
    public void GetMostFrequentFieldValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var before = doc.GetMostFrequentFieldValue("status");
        var path = TempFile("mfv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMostFrequentFieldValue("status"));
    }

    // -------------------------------------------------------------------------
    // GetFieldStatistics
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldStatistics_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var ex = Record.Exception(() => doc.GetFieldStatistics("delay_min"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldStatistics_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        Assert.NotNull(doc.GetFieldStatistics("delay_min"));
    }

    [Fact]
    public void GetFieldStatistics_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var s1 = doc.GetFieldStatistics("delay_min");
        var s2 = doc.GetFieldStatistics("delay_min");
        Assert.Equal(s1.Mean, s2.Mean, precision: 4);
    }

    [Fact]
    public void GetFieldStatistics_MeanInRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var stats = doc.GetFieldStatistics("delay_min");
        // delay_min values: 15,0,45,10,0,30,5,20,0,0,60,5 → mean=15.83, min=0, max=60
        Assert.True(stats.Mean >= stats.Min);
        Assert.True(stats.Mean <= stats.Max);
    }

    [Fact]
    public void GetFieldStatistics_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var before = doc.GetFieldStatistics("delay_min");
        var path = TempFile("fstat_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetFieldStatistics("delay_min");
        Assert.Equal(before.Mean, after.Mean, precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetUniqueFieldValueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueFieldValueCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var ex = Record.Exception(() => doc.GetUniqueFieldValueCount("airline"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueFieldValueCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        Assert.True(doc.GetUniqueFieldValueCount("airline") > 0);
    }

    [Fact]
    public void GetUniqueFieldValueCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        Assert.Equal(doc.GetUniqueFieldValueCount("class"), doc.GetUniqueFieldValueCount("class"));
    }

    [Fact]
    public void GetUniqueFieldValueCount_Leq_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        Assert.True(doc.GetUniqueFieldValueCount("airline") <= doc.RecordCount);
    }

    [Fact]
    public void GetUniqueFieldValueCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlightDataNdjson());
        var before = doc.GetUniqueFieldValueCount("status");
        var path = TempFile("ufc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueFieldValueCount("status"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMostFrequentFieldValue_GetFieldStatistics_GetUniqueFieldValueCount_SaveToFile_Pipeline()
    {
        // Epidemiology outbreak surveillance — WHO regional disease reporting dataset
        var path = TempFile("dogfood_outbreak.ndjson");
        var lines = new[]
        {
            "{\"report_id\":\"WHO-001\",\"region\":\"Africa\",\"country\":\"Nigeria\",\"disease\":\"Cholera\",\"cases\":1240,\"deaths\":38,\"fatality_rate\":3.06,\"outbreak_week\":22,\"response_team\":\"AFRO\"}",
            "{\"report_id\":\"WHO-002\",\"region\":\"Asia\",\"country\":\"Bangladesh\",\"disease\":\"Dengue\",\"cases\":3820,\"deaths\":12,\"fatality_rate\":0.31,\"outbreak_week\":22,\"response_team\":\"SEARO\"}",
            "{\"report_id\":\"WHO-003\",\"region\":\"Africa\",\"country\":\"DRC\",\"disease\":\"Mpox\",\"cases\":892,\"deaths\":45,\"fatality_rate\":5.04,\"outbreak_week\":23,\"response_team\":\"AFRO\"}",
            "{\"report_id\":\"WHO-004\",\"region\":\"Americas\",\"country\":\"Brazil\",\"disease\":\"Dengue\",\"cases\":52000,\"deaths\":180,\"fatality_rate\":0.35,\"outbreak_week\":22,\"response_team\":\"AMRO\"}",
            "{\"report_id\":\"WHO-005\",\"region\":\"Africa\",\"country\":\"Ethiopia\",\"disease\":\"Cholera\",\"cases\":2100,\"deaths\":65,\"fatality_rate\":3.10,\"outbreak_week\":23,\"response_team\":\"AFRO\"}",
            "{\"report_id\":\"WHO-006\",\"region\":\"Europe\",\"country\":\"Germany\",\"disease\":\"Measles\",\"cases\":145,\"deaths\":0,\"fatality_rate\":0.0,\"outbreak_week\":22,\"response_team\":\"EURO\"}",
            "{\"report_id\":\"WHO-007\",\"region\":\"Asia\",\"country\":\"India\",\"disease\":\"Dengue\",\"cases\":18500,\"deaths\":42,\"fatality_rate\":0.23,\"outbreak_week\":23,\"response_team\":\"SEARO\"}",
            "{\"report_id\":\"WHO-008\",\"region\":\"Africa\",\"country\":\"Somalia\",\"disease\":\"Cholera\",\"cases\":3400,\"deaths\":110,\"fatality_rate\":3.24,\"outbreak_week\":24,\"response_team\":\"AFRO\"}",
            "{\"report_id\":\"WHO-009\",\"region\":\"Americas\",\"country\":\"Colombia\",\"disease\":\"Dengue\",\"cases\":8700,\"deaths\":28,\"fatality_rate\":0.32,\"outbreak_week\":23,\"response_team\":\"AMRO\"}",
            "{\"report_id\":\"WHO-010\",\"region\":\"Asia\",\"country\":\"Philippines\",\"disease\":\"Dengue\",\"cases\":24300,\"deaths\":88,\"fatality_rate\":0.36,\"outbreak_week\":24,\"response_team\":\"WPRO\"}",
            "{\"report_id\":\"WHO-011\",\"region\":\"Africa\",\"country\":\"Sudan\",\"disease\":\"Cholera\",\"cases\":1850,\"deaths\":72,\"fatality_rate\":3.89,\"outbreak_week\":24,\"response_team\":\"EMRO\"}",
            "{\"report_id\":\"WHO-012\",\"region\":\"Europe\",\"country\":\"France\",\"disease\":\"Measles\",\"cases\":89,\"deaths\":0,\"fatality_rate\":0.0,\"outbreak_week\":24,\"response_team\":\"EURO\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetMostFrequentFieldValue — disease (Dengue appears 4 times)
        var mostDisease = doc.GetMostFrequentFieldValue("disease");
        Assert.NotNull(mostDisease);
        Assert.Equal("Dengue", mostDisease);
        Assert.Equal(mostDisease, doc.GetMostFrequentFieldValue("disease")); // consistent

        // GetMostFrequentFieldValue — region (Africa appears 5 times)
        var mostRegion = doc.GetMostFrequentFieldValue("region");
        Assert.NotNull(mostRegion);
        Assert.Equal("Africa", mostRegion);

        // GetMostFrequentFieldValue — response_team (AFRO appears 5 times)
        var mostTeam = doc.GetMostFrequentFieldValue("response_team");
        Assert.NotNull(mostTeam);
        Assert.Equal("AFRO", mostTeam);

        // GetFieldStatistics — fatality_rate (0.0 to 5.04)
        var fatalStats = doc.GetFieldStatistics("fatality_rate");
        Assert.NotNull(fatalStats);
        Assert.True(fatalStats.Min >= 0.0);
        Assert.True(fatalStats.Max <= 6.0);
        Assert.True(fatalStats.Mean >= fatalStats.Min);
        Assert.True(fatalStats.Mean <= fatalStats.Max);
        Assert.Equal(fatalStats.Mean, doc.GetFieldStatistics("fatality_rate").Mean, precision: 4); // consistent

        // GetFieldStatistics — cases (145 to 52000)
        var caseStats = doc.GetFieldStatistics("cases");
        Assert.NotNull(caseStats);
        Assert.True(caseStats.Min >= 0);
        Assert.True(caseStats.Max >= 50000);
        Assert.True(caseStats.Mean > 0);
        Assert.True(caseStats.StdDev >= 0);

        // GetUniqueFieldValueCount — disease (3: Cholera, Dengue, Mpox, Measles = 4 unique)
        var uniqueDiseases = doc.GetUniqueFieldValueCount("disease");
        Assert.True(uniqueDiseases >= 3);
        Assert.True(uniqueDiseases <= doc.RecordCount);
        Assert.Equal(uniqueDiseases, doc.GetUniqueFieldValueCount("disease")); // consistent

        // GetUniqueFieldValueCount — region (4: Africa, Asia, Americas, Europe)
        var uniqueRegions = doc.GetUniqueFieldValueCount("region");
        Assert.True(uniqueRegions >= 4);
        Assert.True(uniqueRegions <= doc.RecordCount);

        // GetUniqueFieldValueCount — response_team (5: AFRO, SEARO, AMRO, EURO, WPRO, EMRO = 6)
        var uniqueTeams = doc.GetUniqueFieldValueCount("response_team");
        Assert.True(uniqueTeams >= 4);
        Assert.True(uniqueTeams <= doc.RecordCount);

        // AppendRecord — add week 25 report
        doc.AppendRecord("{\"report_id\":\"WHO-013\",\"region\":\"Asia\",\"country\":\"Thailand\",\"disease\":\"Dengue\",\"cases\":9800,\"deaths\":30,\"fatality_rate\":0.31,\"outbreak_week\":25,\"response_team\":\"SEARO\"}");
        Assert.Equal(13, doc.RecordCount);
        // Dengue now 5 times — still most frequent
        Assert.Equal("Dengue", doc.GetMostFrequentFieldValue("disease"));

        // SaveToFile
        var out1 = TempFile("dogfood_outbreak_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify persistence
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(13, loaded.RecordCount);
        Assert.Equal("Dengue", loaded.GetMostFrequentFieldValue("disease"));
        Assert.Equal("Africa", loaded.GetMostFrequentFieldValue("region"));

        var loadedFatalStats = loaded.GetFieldStatistics("fatality_rate");
        Assert.NotNull(loadedFatalStats);
        Assert.Equal(fatalStats.Min, loadedFatalStats.Min, precision: 4);

        Assert.True(loaded.GetUniqueFieldValueCount("disease") >= 3);

        // GetRecordAtIndex on loaded
        var rec0 = loaded.GetRecordAtIndex(0);
        Assert.NotNull(rec0);

        // GetFieldNames on loaded
        var fields = loaded.GetFieldNames();
        Assert.NotNull(fields);
        Assert.True(fields.Count > 0);

        // AppendRecord on loaded
        loaded.AppendRecord("{\"report_id\":\"WHO-014\",\"region\":\"Africa\",\"country\":\"Chad\",\"disease\":\"Cholera\",\"cases\":780,\"deaths\":28,\"fatality_rate\":3.59,\"outbreak_week\":25,\"response_team\":\"AFRO\"}");
        Assert.Equal(14, loaded.RecordCount);
        // Africa now 7 times — still most frequent
        Assert.Equal("Africa", loaded.GetMostFrequentFieldValue("region"));

        // Final save
        var out2 = TempFile("dogfood_outbreak_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RecordCount);
        Assert.Equal("Dengue", loaded2.GetMostFrequentFieldValue("disease"));
        Assert.True(loaded2.GetUniqueFieldValueCount("region") >= 4);
        Assert.NotNull(loaded2.GetFieldStatistics("cases"));
        var ex1 = Record.Exception(() => loaded2.GetMostFrequentFieldValue("response_team"));
        var ex2 = Record.Exception(() => loaded2.GetUniqueFieldValueCount("disease"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
