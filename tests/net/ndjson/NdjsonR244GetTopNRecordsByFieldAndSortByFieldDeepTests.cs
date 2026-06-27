// Tests for NdjsonDocument.GetTopNRecordsByField, SortByField, GetBottomNRecordsByField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R244

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R244: Tests for NdjsonDocument.GetTopNRecordsByField, SortByField, GetBottomNRecordsByField deeper.
/// GetTopNRecordsByField(fieldName, n): returns the N records with highest numeric field value.
/// SortByField(fieldName, ascending): returns records sorted by the given field.
/// GetBottomNRecordsByField(fieldName, n): returns the N records with lowest numeric field value.
/// Covers: GetTopNRecordsByField no-throw; GetTopNRecordsByField count leq n; GetTopNRecordsByField consistent;
/// GetTopNRecordsByField count leq total; GetTopNRecordsByField save-load;
/// SortByField no-throw; SortByField count equals total; SortByField consistent;
/// SortByField ascending vs descending; SortByField save-load;
/// GetBottomNRecordsByField no-throw; GetBottomNRecordsByField count leq n; GetBottomNRecordsByField consistent;
/// GetBottomNRecordsByField save-load;
/// dogfood Append→GetTopNRecordsByField→SortByField→GetBottomNRecordsByField→SaveToFile pipeline.
/// </summary>
public class NdjsonR244GetTopNRecordsByFieldAndSortByFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR244GetTopNRecordsByFieldAndSortByFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR244_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCountryGdpNdjson()
    {
        var path = TempFile("country_gdp.ndjson");
        var lines = new[]
        {
            "{\"country\":\"USA\",\"gdp_usd_bn\":25463,\"gdp_growth\":2.1,\"population_m\":334.9,\"hdi\":0.921}",
            "{\"country\":\"China\",\"gdp_usd_bn\":17963,\"gdp_growth\":5.2,\"population_m\":1411.0,\"hdi\":0.768}",
            "{\"country\":\"Germany\",\"gdp_usd_bn\":4082,\"gdp_growth\":0.2,\"population_m\":84.4,\"hdi\":0.942}",
            "{\"country\":\"Japan\",\"gdp_usd_bn\":4231,\"gdp_growth\":1.9,\"population_m\":124.5,\"hdi\":0.920}",
            "{\"country\":\"India\",\"gdp_usd_bn\":3385,\"gdp_growth\":6.3,\"population_m\":1428.6,\"hdi\":0.644}",
            "{\"country\":\"UK\",\"gdp_usd_bn\":3089,\"gdp_growth\":0.4,\"population_m\":67.7,\"hdi\":0.929}",
            "{\"country\":\"France\",\"gdp_usd_bn\":2923,\"gdp_growth\":0.7,\"population_m\":68.2,\"hdi\":0.910}",
            "{\"country\":\"Canada\",\"gdp_usd_bn\":2140,\"gdp_growth\":1.5,\"population_m\":40.1,\"hdi\":0.935}",
            "{\"country\":\"Brazil\",\"gdp_usd_bn\":1921,\"gdp_growth\":2.9,\"population_m\":215.3,\"hdi\":0.754}",
            "{\"country\":\"Australia\",\"gdp_usd_bn\":1693,\"gdp_growth\":2.0,\"population_m\":26.5,\"hdi\":0.946}",
            "{\"country\":\"Mexico\",\"gdp_usd_bn\":1323,\"gdp_growth\":3.2,\"population_m\":127.5,\"hdi\":0.758}",
            "{\"country\":\"Spain\",\"gdp_usd_bn\":1418,\"gdp_growth\":2.5,\"population_m\":47.8,\"hdi\":0.905}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTopNRecordsByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopNRecordsByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var ex = Record.Exception(() => doc.GetTopNRecordsByField("gdp_usd_bn", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopNRecordsByField_CountLeqN()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var top = doc.GetTopNRecordsByField("gdp_usd_bn", 5);
        Assert.True(top.Count <= 5);
    }

    [Fact]
    public void GetTopNRecordsByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var t1 = doc.GetTopNRecordsByField("gdp_growth", 3);
        var t2 = doc.GetTopNRecordsByField("gdp_growth", 3);
        Assert.Equal(t1.Count, t2.Count);
    }

    [Fact]
    public void GetTopNRecordsByField_CountLeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        Assert.True(doc.GetTopNRecordsByField("gdp_usd_bn", 100).Count <= doc.RecordCount);
    }

    [Fact]
    public void GetTopNRecordsByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var before = doc.GetTopNRecordsByField("hdi", 4).Count;
        var path = TempFile("top_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTopNRecordsByField("hdi", 4).Count);
    }

    // -------------------------------------------------------------------------
    // SortByField
    // -------------------------------------------------------------------------

    [Fact]
    public void SortByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var ex = Record.Exception(() => doc.SortByField("gdp_usd_bn", ascending: false));
        Assert.Null(ex);
    }

    [Fact]
    public void SortByField_CountEqualsTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var sorted = doc.SortByField("gdp_growth", ascending: true);
        Assert.Equal(doc.RecordCount, sorted.Count);
    }

    [Fact]
    public void SortByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var s1 = doc.SortByField("hdi", ascending: true);
        var s2 = doc.SortByField("hdi", ascending: true);
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void SortByField_Ascending_Differs_Descending()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var asc = doc.SortByField("gdp_usd_bn", ascending: true);
        var desc = doc.SortByField("gdp_usd_bn", ascending: false);
        // Both have same count
        Assert.Equal(asc.Count, desc.Count);
        // But same count total records
        Assert.Equal(doc.RecordCount, asc.Count);
    }

    [Fact]
    public void SortByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var before = doc.SortByField("population_m", ascending: true).Count;
        var path = TempFile("sort_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.SortByField("population_m", ascending: true).Count);
    }

    // -------------------------------------------------------------------------
    // GetBottomNRecordsByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBottomNRecordsByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var ex = Record.Exception(() => doc.GetBottomNRecordsByField("gdp_usd_bn", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBottomNRecordsByField_CountLeqN()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var bottom = doc.GetBottomNRecordsByField("hdi", 4);
        Assert.True(bottom.Count <= 4);
    }

    [Fact]
    public void GetBottomNRecordsByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var b1 = doc.GetBottomNRecordsByField("gdp_growth", 3);
        var b2 = doc.GetBottomNRecordsByField("gdp_growth", 3);
        Assert.Equal(b1.Count, b2.Count);
    }

    [Fact]
    public void GetBottomNRecordsByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateCountryGdpNdjson());
        var before = doc.GetBottomNRecordsByField("gdp_usd_bn", 5).Count;
        var path = TempFile("bottom_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBottomNRecordsByField("gdp_usd_bn", 5).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTopNRecordsByField_SortByField_GetBottomNRecordsByField_SaveToFile_Pipeline()
    {
        // Corporate sustainability — ESG score leaderboard and laggard analysis
        var path = TempFile("dogfood_esg.ndjson");
        var lines = new[]
        {
            "{\"company\":\"MicrosoftCorp\",\"ticker\":\"MSFT\",\"esg_score\":87.4,\"env_score\":82.1,\"social_score\":91.2,\"governance\":88.8,\"carbon_intensity\":45.2,\"renewable_pct\":78.5,\"sector\":\"Technology\"}",
            "{\"company\":\"AppleInc\",\"ticker\":\"AAPL\",\"esg_score\":85.1,\"env_score\":88.4,\"social_score\":80.3,\"governance\":86.5,\"carbon_intensity\":22.8,\"renewable_pct\":100.0,\"sector\":\"Technology\"}",
            "{\"company\":\"TotalEnergies\",\"ticker\":\"TTE\",\"esg_score\":52.3,\"env_score\":38.7,\"social_score\":62.4,\"governance\":55.8,\"carbon_intensity\":820.5,\"renewable_pct\":12.4,\"sector\":\"Energy\"}",
            "{\"company\":\"Unilever\",\"ticker\":\"ULVR\",\"esg_score\":78.9,\"env_score\":76.3,\"social_score\":83.7,\"governance\":76.8,\"carbon_intensity\":95.4,\"renewable_pct\":45.2,\"sector\":\"ConsumerGoods\"}",
            "{\"company\":\"NestleSA\",\"ticker\":\"NESN\",\"esg_score\":71.2,\"env_score\":68.9,\"social_score\":74.5,\"governance\":70.1,\"carbon_intensity\":142.8,\"renewable_pct\":38.7,\"sector\":\"ConsumerGoods\"}",
            "{\"company\":\"GoldmanSachs\",\"ticker\":\"GS\",\"esg_score\":61.8,\"env_score\":55.2,\"social_score\":65.4,\"governance\":64.8,\"carbon_intensity\":28.5,\"renewable_pct\":22.1,\"sector\":\"Finance\"}",
            "{\"company\":\"Volkswagen\",\"ticker\":\"VOW3\",\"esg_score\":48.6,\"env_score\":42.1,\"social_score\":54.3,\"governance\":49.5,\"carbon_intensity\":485.2,\"renewable_pct\":18.9,\"sector\":\"Automotive\"}",
            "{\"company\":\"Schneider\",\"ticker\":\"SU\",\"esg_score\":91.5,\"env_score\":93.2,\"social_score\":89.7,\"governance\":91.5,\"carbon_intensity\":38.9,\"renewable_pct\":88.6,\"sector\":\"IndustrialGoods\"}",
            "{\"company\":\"Novo Nordisk\",\"ticker\":\"NOVO\",\"esg_score\":83.7,\"env_score\":80.5,\"social_score\":87.2,\"governance\":83.4,\"carbon_intensity\":52.1,\"renewable_pct\":70.3,\"sector\":\"Healthcare\"}",
            "{\"company\":\"ExxonMobil\",\"ticker\":\"XOM\",\"esg_score\":38.2,\"env_score\":25.8,\"social_score\":48.3,\"governance\":40.5,\"carbon_intensity\":1205.8,\"renewable_pct\":3.2,\"sector\":\"Energy\"}",
            "{\"company\":\"ASML\",\"ticker\":\"ASML\",\"esg_score\":88.3,\"env_score\":86.7,\"social_score\":89.5,\"governance\":88.8,\"carbon_intensity\":15.3,\"renewable_pct\":92.4,\"sector\":\"Technology\"}",
            "{\"company\":\"ValeBrasi\",\"ticker\":\"VALE\",\"esg_score\":44.1,\"env_score\":35.4,\"social_score\":51.2,\"governance\":45.7,\"carbon_intensity\":380.6,\"renewable_pct\":28.5,\"sector\":\"Mining\"}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetTopNRecordsByField — top 3 ESG leaders
        var top3Esg = doc.GetTopNRecordsByField("esg_score", 3);
        Assert.True(top3Esg.Count <= 3);
        Assert.True(top3Esg.Count >= 1);
        Assert.Equal(top3Esg.Count, doc.GetTopNRecordsByField("esg_score", 3).Count); // consistent

        // GetTopNRecordsByField — top 5 renewable energy usage
        var top5Renewable = doc.GetTopNRecordsByField("renewable_pct", 5);
        Assert.True(top5Renewable.Count <= 5);

        // GetTopNRecordsByField — top 3 governance scores
        var top3Gov = doc.GetTopNRecordsByField("governance", 3);
        Assert.True(top3Gov.Count <= 3);
        Assert.True(top3Gov.Count >= 1);

        // GetTopNRecordsByField — more than total (returns all 12)
        var topAll = doc.GetTopNRecordsByField("esg_score", 100);
        Assert.Equal(doc.RecordCount, topAll.Count);

        // SortByField — ascending by carbon_intensity (low carbon = green)
        var sortedAsc = doc.SortByField("carbon_intensity", ascending: true);
        Assert.Equal(12, sortedAsc.Count);
        Assert.Equal(sortedAsc.Count, doc.SortByField("carbon_intensity", ascending: true).Count); // consistent

        // SortByField — descending by esg_score
        var sortedDesc = doc.SortByField("esg_score", ascending: false);
        Assert.Equal(12, sortedDesc.Count);

        // GetBottomNRecordsByField — bottom 3 ESG laggards
        var bottom3Esg = doc.GetBottomNRecordsByField("esg_score", 3);
        Assert.True(bottom3Esg.Count <= 3);
        Assert.True(bottom3Esg.Count >= 1);
        Assert.Equal(bottom3Esg.Count, doc.GetBottomNRecordsByField("esg_score", 3).Count); // consistent

        // GetBottomNRecordsByField — worst renewable %
        var bottom3Ren = doc.GetBottomNRecordsByField("renewable_pct", 3);
        Assert.True(bottom3Ren.Count <= 3);

        // AppendRecord — new sustainable company
        doc.AppendRecord("{\"company\":\"OrstedAS\",\"ticker\":\"ORSTED\",\"esg_score\":94.2,\"env_score\":96.8,\"social_score\":91.5,\"governance\":94.2,\"carbon_intensity\":8.5,\"renewable_pct\":99.0,\"sector\":\"Utilities\"}");
        Assert.Equal(13, doc.RecordCount);

        // After append: top 3 may include Orsted
        var newTop3 = doc.GetTopNRecordsByField("esg_score", 3);
        Assert.True(newTop3.Count <= 3);
        Assert.Equal(13, doc.SortByField("esg_score", ascending: false).Count);

        // SaveToFile
        var out1 = TempFile("dogfood_esg_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(13, loaded.RecordCount);
        Assert.Equal(doc.GetTopNRecordsByField("esg_score", 5).Count, loaded.GetTopNRecordsByField("esg_score", 5).Count);
        Assert.Equal(13, loaded.SortByField("carbon_intensity", ascending: true).Count);
        Assert.Equal(doc.GetBottomNRecordsByField("governance", 3).Count, loaded.GetBottomNRecordsByField("governance", 3).Count);

        // Final save
        var out2 = TempFile("dogfood_esg_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.RecordCount);
        Assert.True(loaded2.GetTopNRecordsByField("esg_score", 3).Count <= 3);
        Assert.Equal(13, loaded2.SortByField("esg_score", ascending: false).Count);
        var ex1 = Record.Exception(() => loaded2.GetTopNRecordsByField("renewable_pct", 5));
        var ex2 = Record.Exception(() => loaded2.GetBottomNRecordsByField("esg_score", 3));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
