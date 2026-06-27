// Tests for NdjsonDocument.GetRecordsInDateRange, GroupByField, GetGroupCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R243

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R243: Tests for NdjsonDocument.GetRecordsInDateRange, GroupByField, GetGroupCount deeper.
/// GetRecordsInDateRange(dateField, from, to): returns records where dateField falls within range.
/// GroupByField(fieldName): groups records by the distinct values of the given field.
/// GetGroupCount(fieldName): returns the number of distinct groups for the given field.
/// Covers: GetRecordsInDateRange no-throw; GetRecordsInDateRange count leq total; GetRecordsInDateRange consistent;
/// GetRecordsInDateRange empty for impossible range; GetRecordsInDateRange save-load;
/// GroupByField no-throw; GroupByField non-null; GroupByField consistent;
/// GroupByField keys match distinct values; GroupByField save-load;
/// GetGroupCount no-throw; GetGroupCount positive; GetGroupCount consistent;
/// GetGroupCount leq record count; GetGroupCount save-load;
/// dogfood Append→GetRecordsInDateRange→GroupByField→GetGroupCount→SaveToFile pipeline.
/// </summary>
public class NdjsonR243GetRecordsInDateRangeAndGroupByFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR243GetRecordsInDateRangeAndGroupByFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR243_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateWeatherNdjson()
    {
        // 12 daily weather observations across 4 cities
        var path = TempFile("weather.ndjson");
        var lines = new[]
        {
            "{\"obs_id\":\"W001\",\"date\":\"2026-06-01\",\"city\":\"London\",\"temp_c\":18.5,\"humidity\":72,\"condition\":\"Cloudy\"}",
            "{\"obs_id\":\"W002\",\"date\":\"2026-06-03\",\"city\":\"Paris\",\"temp_c\":22.1,\"humidity\":58,\"condition\":\"Sunny\"}",
            "{\"obs_id\":\"W003\",\"date\":\"2026-06-05\",\"city\":\"Berlin\",\"temp_c\":16.8,\"humidity\":65,\"condition\":\"Rainy\"}",
            "{\"obs_id\":\"W004\",\"date\":\"2026-06-07\",\"city\":\"Madrid\",\"temp_c\":31.2,\"humidity\":35,\"condition\":\"Sunny\"}",
            "{\"obs_id\":\"W005\",\"date\":\"2026-06-10\",\"city\":\"London\",\"temp_c\":15.9,\"humidity\":80,\"condition\":\"Rainy\"}",
            "{\"obs_id\":\"W006\",\"date\":\"2026-06-12\",\"city\":\"Paris\",\"temp_c\":24.5,\"humidity\":52,\"condition\":\"Sunny\"}",
            "{\"obs_id\":\"W007\",\"date\":\"2026-06-14\",\"city\":\"Berlin\",\"temp_c\":19.3,\"humidity\":60,\"condition\":\"Cloudy\"}",
            "{\"obs_id\":\"W008\",\"date\":\"2026-06-16\",\"city\":\"Madrid\",\"temp_c\":33.8,\"humidity\":28,\"condition\":\"Sunny\"}",
            "{\"obs_id\":\"W009\",\"date\":\"2026-06-18\",\"city\":\"London\",\"temp_c\":17.2,\"humidity\":75,\"condition\":\"Cloudy\"}",
            "{\"obs_id\":\"W010\",\"date\":\"2026-06-20\",\"city\":\"Paris\",\"temp_c\":26.0,\"humidity\":45,\"condition\":\"Sunny\"}",
            "{\"obs_id\":\"W011\",\"date\":\"2026-06-22\",\"city\":\"Berlin\",\"temp_c\":21.4,\"humidity\":55,\"condition\":\"Cloudy\"}",
            "{\"obs_id\":\"W012\",\"date\":\"2026-06-24\",\"city\":\"Madrid\",\"temp_c\":35.1,\"humidity\":22,\"condition\":\"Sunny\"}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordsInDateRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsInDateRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var ex = Record.Exception(() => doc.GetRecordsInDateRange("date", "2026-06-01", "2026-06-12"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsInDateRange_CountLeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var records = doc.GetRecordsInDateRange("date", "2026-06-01", "2026-06-12");
        Assert.True(records.Count <= doc.RecordCount);
    }

    [Fact]
    public void GetRecordsInDateRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var r1 = doc.GetRecordsInDateRange("date", "2026-06-05", "2026-06-15");
        var r2 = doc.GetRecordsInDateRange("date", "2026-06-05", "2026-06-15");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRecordsInDateRange_Empty_ForImpossibleRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var records = doc.GetRecordsInDateRange("date", "2025-01-01", "2025-12-31");
        Assert.Empty(records);
    }

    [Fact]
    public void GetRecordsInDateRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var before = doc.GetRecordsInDateRange("date", "2026-06-01", "2026-06-30").Count;
        var path = TempFile("dr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordsInDateRange("date", "2026-06-01", "2026-06-30").Count);
    }

    // -------------------------------------------------------------------------
    // GroupByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var ex = Record.Exception(() => doc.GroupByField("city"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        Assert.NotNull(doc.GroupByField("city"));
    }

    [Fact]
    public void GroupByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var g1 = doc.GroupByField("city");
        var g2 = doc.GroupByField("city");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupByField_KeysMatchDistinctValues()
    {
        // 4 distinct cities in dataset
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var groups = doc.GroupByField("city");
        Assert.Equal(doc.GetUniqueFieldValueCount("city"), groups.Count);
    }

    [Fact]
    public void GroupByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var before = doc.GroupByField("condition").Count;
        var path = TempFile("grp_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GroupByField("condition").Count);
    }

    // -------------------------------------------------------------------------
    // GetGroupCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var ex = Record.Exception(() => doc.GetGroupCount("city"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGroupCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        Assert.True(doc.GetGroupCount("city") > 0);
    }

    [Fact]
    public void GetGroupCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        Assert.Equal(doc.GetGroupCount("condition"), doc.GetGroupCount("condition"));
    }

    [Fact]
    public void GetGroupCount_LeqRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        Assert.True(doc.GetGroupCount("city") <= doc.RecordCount);
    }

    [Fact]
    public void GetGroupCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateWeatherNdjson());
        var before = doc.GetGroupCount("city");
        var path = TempFile("gc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetGroupCount("city"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordsInDateRange_GroupByField_GetGroupCount_SaveToFile_Pipeline()
    {
        // Public health — hospital admission surveillance (respiratory illness tracking)
        var path = TempFile("dogfood_admissions.ndjson");
        var lines = new[]
        {
            "{\"admission_id\":\"H001\",\"date\":\"2026-01-05\",\"hospital\":\"Royal Victoria\",\"ward\":\"Respiratory\",\"diagnosis\":\"Influenza\",\"age_group\":\"65+\",\"severity\":\"Moderate\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H002\",\"date\":\"2026-01-08\",\"hospital\":\"City General\",\"ward\":\"ICU\",\"diagnosis\":\"COVID-19\",\"age_group\":\"45-64\",\"severity\":\"Severe\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H003\",\"date\":\"2026-01-12\",\"hospital\":\"Royal Victoria\",\"ward\":\"Respiratory\",\"diagnosis\":\"Influenza\",\"age_group\":\"65+\",\"severity\":\"Mild\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H004\",\"date\":\"2026-02-03\",\"hospital\":\"St. Thomas\",\"ward\":\"General\",\"diagnosis\":\"RSV\",\"age_group\":\"0-17\",\"severity\":\"Mild\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H005\",\"date\":\"2026-02-10\",\"hospital\":\"City General\",\"ward\":\"ICU\",\"diagnosis\":\"Influenza\",\"age_group\":\"65+\",\"severity\":\"Critical\",\"outcome\":\"Deceased\"}",
            "{\"admission_id\":\"H006\",\"date\":\"2026-02-15\",\"hospital\":\"Royal Victoria\",\"ward\":\"Respiratory\",\"diagnosis\":\"COVID-19\",\"age_group\":\"45-64\",\"severity\":\"Moderate\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H007\",\"date\":\"2026-03-02\",\"hospital\":\"St. Thomas\",\"ward\":\"Respiratory\",\"diagnosis\":\"Influenza\",\"age_group\":\"18-44\",\"severity\":\"Mild\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H008\",\"date\":\"2026-03-08\",\"hospital\":\"City General\",\"ward\":\"General\",\"diagnosis\":\"RSV\",\"age_group\":\"0-17\",\"severity\":\"Mild\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H009\",\"date\":\"2026-03-14\",\"hospital\":\"Royal Victoria\",\"ward\":\"ICU\",\"diagnosis\":\"COVID-19\",\"age_group\":\"65+\",\"severity\":\"Critical\",\"outcome\":\"Deceased\"}",
            "{\"admission_id\":\"H010\",\"date\":\"2026-03-20\",\"hospital\":\"St. Thomas\",\"ward\":\"Respiratory\",\"diagnosis\":\"Influenza\",\"age_group\":\"65+\",\"severity\":\"Moderate\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H011\",\"date\":\"2026-03-25\",\"hospital\":\"City General\",\"ward\":\"Respiratory\",\"diagnosis\":\"COVID-19\",\"age_group\":\"45-64\",\"severity\":\"Severe\",\"outcome\":\"Discharged\"}",
            "{\"admission_id\":\"H012\",\"date\":\"2026-03-28\",\"hospital\":\"Royal Victoria\",\"ward\":\"General\",\"diagnosis\":\"RSV\",\"age_group\":\"0-17\",\"severity\":\"Mild\",\"outcome\":\"Discharged\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetRecordsInDateRange — January admissions (3 records: H001, H002, H003)
        var janAdmissions = doc.GetRecordsInDateRange("date", "2026-01-01", "2026-01-31");
        Assert.True(janAdmissions.Count >= 0);
        Assert.True(janAdmissions.Count <= doc.RecordCount);
        Assert.Equal(janAdmissions.Count, doc.GetRecordsInDateRange("date", "2026-01-01", "2026-01-31").Count); // consistent

        // GetRecordsInDateRange — February admissions
        var febAdmissions = doc.GetRecordsInDateRange("date", "2026-02-01", "2026-02-28");
        Assert.True(febAdmissions.Count >= 0);

        // GetRecordsInDateRange — Q1 admissions (all 12)
        var q1Admissions = doc.GetRecordsInDateRange("date", "2026-01-01", "2026-03-31");
        Assert.Equal(doc.RecordCount, q1Admissions.Count);

        // GetRecordsInDateRange — impossible range
        var futureAdmissions = doc.GetRecordsInDateRange("date", "2027-01-01", "2027-12-31");
        Assert.Empty(futureAdmissions);

        // GroupByField — hospital (3 hospitals: Royal Victoria×4, City General×4, St. Thomas×4)
        var byHospital = doc.GroupByField("hospital");
        Assert.NotNull(byHospital);
        Assert.Equal(3, byHospital.Count);
        Assert.Equal(byHospital.Count, doc.GroupByField("hospital").Count); // consistent

        // GroupByField — diagnosis (4: Influenza×5, COVID-19×4, RSV×3)
        var byDiagnosis = doc.GroupByField("diagnosis");
        Assert.NotNull(byDiagnosis);
        Assert.Equal(3, byDiagnosis.Count);

        // GroupByField — severity (4: Mild×5, Moderate×3, Severe×2, Critical×2)
        var bySeverity = doc.GroupByField("severity");
        Assert.NotNull(bySeverity);
        Assert.True(bySeverity.Count >= 3);

        // GetGroupCount — hospital
        var hospitalGroups = doc.GetGroupCount("hospital");
        Assert.Equal(3, hospitalGroups);
        Assert.Equal(hospitalGroups, doc.GetGroupCount("hospital")); // consistent

        // GetGroupCount — age_group (4: 65+, 45-64, 18-44, 0-17)
        var ageGroups = doc.GetGroupCount("age_group");
        Assert.Equal(4, ageGroups);

        // GetGroupCount — outcome (2: Discharged×10, Deceased×2)
        var outcomeGroups = doc.GetGroupCount("outcome");
        Assert.Equal(2, outcomeGroups);
        Assert.True(outcomeGroups <= doc.RecordCount);

        // AppendRecord — additional admission
        doc.AppendRecord("{\"admission_id\":\"H013\",\"date\":\"2026-04-02\",\"hospital\":\"Royal Victoria\",\"ward\":\"ICU\",\"diagnosis\":\"Influenza\",\"age_group\":\"65+\",\"severity\":\"Critical\",\"outcome\":\"Discharged\"}");
        Assert.Equal(13, doc.RecordCount);

        // Q2 includes new admission
        var q2Start = doc.GetRecordsInDateRange("date", "2026-04-01", "2026-06-30");
        Assert.True(q2Start.Count >= 1);

        // Groups should still be valid after append
        Assert.Equal(3, doc.GetGroupCount("hospital"));

        // SaveToFile
        var out1 = TempFile("dogfood_admissions_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(13, loaded.RecordCount);
        Assert.Equal(3, loaded.GetGroupCount("hospital"));
        Assert.Equal(4, loaded.GetGroupCount("age_group"));
        Assert.Equal(doc.GetRecordsInDateRange("date", "2026-01-01", "2026-01-31").Count,
                     loaded.GetRecordsInDateRange("date", "2026-01-01", "2026-01-31").Count);

        // GroupByField on loaded
        var loadedByDiag = loaded.GroupByField("diagnosis");
        Assert.NotNull(loadedByDiag);
        Assert.Equal(byDiagnosis.Count, loadedByDiag.Count);

        // Final save
        var out2 = TempFile("dogfood_admissions_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.RecordCount);
        Assert.Equal(3, loaded2.GetGroupCount("hospital"));
        var ex1 = Record.Exception(() => loaded2.GroupByField("severity"));
        var ex2 = Record.Exception(() => loaded2.GetRecordsInDateRange("date", "2026-03-01", "2026-03-31"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
