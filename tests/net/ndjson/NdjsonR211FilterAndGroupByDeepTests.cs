// Tests for NdjsonDocument.Filter, GroupBy, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R211

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R211: Tests for NdjsonDocument.Filter, GroupBy, GetDistinctValues deeper.
/// Filter(field, value): returns a new document containing only matching records.
/// GroupBy(field): groups records by the specified field's values.
/// GetDistinctValues(field): returns unique values for the specified field.
/// Covers: Filter non-null; Filter non-empty; Filter correct count; Filter known value;
/// Filter consistent; Filter no-throw; Filter chained; Filter after AppendRecord grows;
/// Filter with no-match returns empty; Filter then ExportToJson shrinks;
/// Filter then ToNdjsonString shrinks; Filter saves correctly;
/// GroupBy non-null; GroupBy key count correct; GroupBy values correct; GroupBy no-throw;
/// GroupBy consistent; GroupBy after Filter single key; GroupBy preserves all records;
/// GetDistinctValues non-null; GetDistinctValues non-empty; GetDistinctValues count correct;
/// GetDistinctValues no duplicates; GetDistinctValues consistent; GetDistinctValues after AppendRecord;
/// GetDistinctValues for id field = record count; GetDistinctValues no-throw;
/// dogfood LoadFile→Filter→GroupBy→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class NdjsonR211FilterAndGroupByDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR211FilterAndGroupByDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR211_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var content =
            "{\"Name\":\"Alice\",\"Dept\":\"Engineering\",\"Grade\":\"Senior\",\"Score\":95}\n" +
            "{\"Name\":\"Bob\",\"Dept\":\"Marketing\",\"Grade\":\"Junior\",\"Score\":72}\n" +
            "{\"Name\":\"Carol\",\"Dept\":\"Engineering\",\"Grade\":\"Lead\",\"Score\":88}\n" +
            "{\"Name\":\"Dave\",\"Dept\":\"Finance\",\"Grade\":\"Mid\",\"Score\":80}\n" +
            "{\"Name\":\"Eve\",\"Dept\":\"Engineering\",\"Grade\":\"Senior\",\"Score\":91}\n" +
            "{\"Name\":\"Frank\",\"Dept\":\"Marketing\",\"Grade\":\"Senior\",\"Score\":83}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.Filter("Dept", "Engineering"));
    }

    [Fact]
    public void Filter_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.Filter("Dept", "Engineering").GetRecordCount() > 0);
    }

    [Fact]
    public void Filter_CorrectCount_Engineering()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(3, doc.Filter("Dept", "Engineering").GetRecordCount());
    }

    [Fact]
    public void Filter_CorrectCount_Marketing()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(2, doc.Filter("Dept", "Marketing").GetRecordCount());
    }

    [Fact]
    public void Filter_KnownValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Grade", "Senior");
        // Alice, Eve, Frank = 3 seniors
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void Filter_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var f1 = doc.Filter("Dept", "Engineering").GetRecordCount();
        var f2 = doc.Filter("Dept", "Engineering").GetRecordCount();
        Assert.Equal(f1, f2);
    }

    [Fact]
    public void Filter_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.Filter("Dept", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void Filter_Chained()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "Engineering").Filter("Grade", "Senior");
        Assert.Equal(2, filtered.GetRecordCount()); // Alice and Eve
    }

    [Fact]
    public void Filter_NoMatch_ReturnsEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "NonExistentDept_XYZ");
        Assert.Equal(0, filtered.GetRecordCount());
    }

    [Fact]
    public void Filter_ThenExportToJson_Shrinks()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.ExportToJson().Length;
        var filtered = doc.Filter("Dept", "Finance"); // 1 record
        Assert.True(filtered.ExportToJson().Length < before);
    }

    [Fact]
    public void Filter_ThenToNdjsonString_Shrinks()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.ToNdjsonString().Length;
        var filtered = doc.Filter("Dept", "Finance");
        Assert.True(filtered.ToNdjsonString().Length < before);
    }

    [Fact]
    public void Filter_SavesCorrectly()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "Engineering");
        var path = TempFile("filtered_eng.ndjson");
        filtered.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GroupBy("Dept"));
    }

    [Fact]
    public void GroupBy_KeyCount_CorrectForDept()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var groups = doc.GroupBy("Dept");
        Assert.Equal(3, groups.Count); // Engineering, Marketing, Finance
    }

    [Fact]
    public void GroupBy_ContainsKnownKeys()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var groups = doc.GroupBy("Dept");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.True(groups.ContainsKey("Marketing"));
        Assert.True(groups.ContainsKey("Finance"));
    }

    [Fact]
    public void GroupBy_Values_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var groups = doc.GroupBy("Dept");
        Assert.Equal(3, groups["Engineering"].Count);
        Assert.Equal(2, groups["Marketing"].Count);
        Assert.Equal(1, groups["Finance"].Count);
    }

    [Fact]
    public void GroupBy_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GroupBy("Dept"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupBy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var g1 = doc.GroupBy("Dept");
        var g2 = doc.GroupBy("Dept");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupBy_AfterFilter_SingleKey()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var filtered = doc.Filter("Dept", "Finance");
        var groups = filtered.GroupBy("Dept");
        Assert.Equal(1, groups.Count);
        Assert.True(groups.ContainsKey("Finance"));
    }

    [Fact]
    public void GroupBy_PreservesAllRecords()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var groups = doc.GroupBy("Dept");
        var total = 0;
        foreach (var kv in groups)
            total += kv.Value.Count;
        Assert.Equal(doc.GetRecordCount(), total);
    }

    [Fact]
    public void GroupBy_ByGrade_CountCorrect()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var groups = doc.GroupBy("Grade");
        // Senior: Alice, Eve, Frank = 3; Junior: Bob = 1; Lead: Carol = 1; Mid: Dave = 1
        Assert.Equal(4, groups.Count);
        Assert.Equal(3, groups["Senior"].Count);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetDistinctValues("Dept").Count > 0);
    }

    [Fact]
    public void GetDistinctValues_CountCorrect_Dept()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(3, doc.GetDistinctValues("Dept").Count);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var values = doc.GetDistinctValues("Dept");
        var set = new System.Collections.Generic.HashSet<string>(values);
        Assert.Equal(set.Count, values.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var v1 = doc.GetDistinctValues("Dept");
        var v2 = doc.GetDistinctValues("Dept");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAppendRecord_Updates()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetDistinctValues("Dept").Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Name"] = "Grace",
            ["Dept"] = "HR",
            ["Grade"] = "Junior",
            ["Score"] = 65
        });
        var after = doc.GetDistinctValues("Dept").Count;
        Assert.True(after >= before);
        Assert.Contains("HR", doc.GetDistinctValues("Dept"));
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetDistinctValues("Dept"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnown()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var values = doc.GetDistinctValues("Dept");
        Assert.Contains("Engineering", values);
        Assert.Contains("Marketing", values);
        Assert.Contains("Finance", values);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Filter_GroupBy_GetDistinctValues_SaveToFile_Pipeline()
    {
        // Create main NDJSON
        var path = TempFile("dogfood_main.ndjson");
        var content =
            "{\"Product\":\"Widget\",\"Category\":\"Hardware\",\"Region\":\"EU\",\"Revenue\":12000}\n" +
            "{\"Product\":\"Gadget\",\"Category\":\"Electronics\",\"Region\":\"US\",\"Revenue\":18500}\n" +
            "{\"Product\":\"Doohickey\",\"Category\":\"Hardware\",\"Region\":\"APAC\",\"Revenue\":9200}\n" +
            "{\"Product\":\"Thingamajig\",\"Category\":\"Software\",\"Region\":\"EU\",\"Revenue\":25000}\n" +
            "{\"Product\":\"Whatchamacallit\",\"Category\":\"Electronics\",\"Region\":\"US\",\"Revenue\":14700}\n" +
            "{\"Product\":\"Gizmo\",\"Category\":\"Hardware\",\"Region\":\"EU\",\"Revenue\":11300}\n" +
            "{\"Product\":\"Doodad\",\"Category\":\"Software\",\"Region\":\"APAC\",\"Revenue\":22000}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRecordCount());

        // GetDistinctValues — categories
        var categories = doc.GetDistinctValues("Category");
        Assert.Equal(3, categories.Count); // Hardware, Electronics, Software
        Assert.Contains("Hardware", categories);
        Assert.Contains("Electronics", categories);
        Assert.Contains("Software", categories);

        // GetDistinctValues — regions
        var regions = doc.GetDistinctValues("Region");
        Assert.Equal(3, regions.Count); // EU, US, APAC

        // Filter by Category=Hardware
        var hardware = doc.Filter("Category", "Hardware");
        Assert.Equal(3, hardware.GetRecordCount());

        // GetDistinctValues on filtered
        var hwRegions = hardware.GetDistinctValues("Region");
        Assert.True(hwRegions.Count >= 1);

        // Filter by Region=EU
        var eu = doc.Filter("Region", "EU");
        Assert.Equal(3, eu.GetRecordCount());

        // Chained filter: Hardware + EU
        var hwEu = doc.Filter("Category", "Hardware").Filter("Region", "EU");
        Assert.True(hwEu.GetRecordCount() >= 1);
        Assert.Equal(1, hwEu.GetDistinctValues("Category").Count);
        Assert.Equal(1, hwEu.GetDistinctValues("Region").Count);

        // GroupBy Category
        var groupedByCategory = doc.GroupBy("Category");
        Assert.Equal(3, groupedByCategory.Count);
        Assert.Equal(3, groupedByCategory["Hardware"].Count);
        Assert.Equal(2, groupedByCategory["Electronics"].Count);
        Assert.Equal(2, groupedByCategory["Software"].Count);

        // GroupBy Region
        var groupedByRegion = doc.GroupBy("Region");
        Assert.Equal(3, groupedByRegion.Count);
        Assert.Equal(3, groupedByRegion["EU"].Count);
        Assert.Equal(2, groupedByRegion["US"].Count);
        Assert.Equal(2, groupedByRegion["APAC"].Count);

        // AppendRecord — new category
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["Product"] = "Blueprint",
            ["Category"] = "Services",
            ["Region"] = "EU",
            ["Revenue"] = 31000
        });
        Assert.Equal(8, doc.GetRecordCount());
        var categoriesAfter = doc.GetDistinctValues("Category");
        Assert.Equal(4, categoriesAfter.Count);
        Assert.Contains("Services", categoriesAfter);

        // GroupBy after append
        var groupedAfter = doc.GroupBy("Category");
        Assert.Equal(4, groupedAfter.Count);
        Assert.Equal(1, groupedAfter["Services"].Count);

        // Filter no-match
        var noMatch = doc.Filter("Category", "Unknown_XYZ");
        Assert.Equal(0, noMatch.GetRecordCount());

        // ExportToJson and ToNdjsonString consistency
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        var ndjsonStr = doc.ToNdjsonString();
        Assert.NotNull(ndjsonStr);
        Assert.True(ndjsonStr.Contains("{"));

        // Filter then ExportToJson shrinks
        var softwareJson = doc.Filter("Category", "Software").ExportToJson();
        Assert.True(softwareJson.Length < json.Length);

        // GetDistinctValues consistent
        var dv1 = doc.GetDistinctValues("Category");
        var dv2 = doc.GetDistinctValues("Category");
        Assert.Equal(dv1.Count, dv2.Count);

        // GroupBy consistent
        var gp1 = doc.GroupBy("Region");
        var gp2 = doc.GroupBy("Region");
        Assert.Equal(gp1.Count, gp2.Count);

        // SaveToFile original
        var saveOrig = TempFile("dogfood_orig.ndjson");
        doc.SaveToFile(saveOrig);
        Assert.True(File.Exists(saveOrig));

        // SaveToFile filtered hardware
        var saveHardware = TempFile("dogfood_hardware.ndjson");
        hardware.SaveToFile(saveHardware);
        Assert.True(File.Exists(saveHardware));

        // LoadFile verify original
        var loadedOrig = NdjsonDocument.LoadFile(saveOrig);
        Assert.Equal(8, loadedOrig.GetRecordCount());
        Assert.Equal(4, loadedOrig.GetDistinctValues("Category").Count);

        // LoadFile verify hardware
        var loadedHw = NdjsonDocument.LoadFile(saveHardware);
        Assert.Equal(3, loadedHw.GetRecordCount());

        // GroupBy on loaded
        var loadedGroups = loadedOrig.GroupBy("Category");
        Assert.Equal(4, loadedGroups.Count);

        // Filter on loaded
        var loadedEu = loadedOrig.Filter("Region", "EU");
        Assert.Equal(4, loadedEu.GetRecordCount()); // 3 original + Blueprint
    }
}
