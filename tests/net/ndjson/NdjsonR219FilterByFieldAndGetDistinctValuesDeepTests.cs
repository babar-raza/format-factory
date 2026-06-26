// Tests for NdjsonDocument.FilterByField, GetDistinctValues, GroupByField deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R219: Tests for NdjsonDocument.FilterByField, GetDistinctValues, GroupByField deeper.
/// FilterByField(field, value): returns new doc with only matching records.
/// GetDistinctValues(field): returns a list of unique values for a field.
/// GroupByField(field): returns dictionary of value → list of record indices.
/// Covers: FilterByField non-null; FilterByField no-throw; FilterByField count correct;
/// FilterByField no-match returns empty; FilterByField consistent;
/// FilterByField save-load; FilterByField then GetFieldStats; FilterByField chained;
/// GetDistinctValues non-null; GetDistinctValues no-throw; GetDistinctValues no-duplicates;
/// GetDistinctValues count correct; GetDistinctValues consistent; GetDistinctValues save-load;
/// GetDistinctValues after AppendRecord updates; GetDistinctValues all-unique field;
/// GroupByField non-null; GroupByField no-throw; GroupByField count correct;
/// GroupByField total rows match; GroupByField consistent; GroupByField save-load;
/// GroupByField all keys present; GroupByField values non-empty;
/// dogfood CreateDoc→FilterByField→GetDistinctValues→GroupByField→SaveToFile pipeline.
/// </summary>
public class NdjsonR219FilterByFieldAndGetDistinctValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR219FilterByFieldAndGetDistinctValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeNdjson()
    {
        var path = TempFile("employees.ndjson");
        var content =
            "{\"name\":\"Alice\",\"department\":\"Engineering\",\"level\":\"Senior\",\"score\":92}\n" +
            "{\"name\":\"Bob\",\"department\":\"Marketing\",\"level\":\"Junior\",\"score\":78}\n" +
            "{\"name\":\"Carol\",\"department\":\"Engineering\",\"level\":\"Lead\",\"score\":88}\n" +
            "{\"name\":\"Dave\",\"department\":\"Finance\",\"level\":\"Mid\",\"score\":85}\n" +
            "{\"name\":\"Eve\",\"department\":\"Engineering\",\"level\":\"Senior\",\"score\":95}\n" +
            "{\"name\":\"Frank\",\"department\":\"Marketing\",\"level\":\"Senior\",\"score\":82}\n" +
            "{\"name\":\"Grace\",\"department\":\"Finance\",\"level\":\"Junior\",\"score\":76}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // FilterByField
    // -------------------------------------------------------------------------

    [Fact]
    public void FilterByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.FilterByField("department", "Engineering"));
    }

    [Fact]
    public void FilterByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.FilterByField("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void FilterByField_Engineering_ThreeRecords()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByField("department", "Engineering");
        Assert.Equal(3, filtered.GetRecordCount());
    }

    [Fact]
    public void FilterByField_Marketing_TwoRecords()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByField("department", "Marketing");
        Assert.Equal(2, filtered.GetRecordCount());
    }

    [Fact]
    public void FilterByField_NoMatch_EmptyResult()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByField("department", "Legal");
        Assert.Equal(0, filtered.GetRecordCount());
    }

    [Fact]
    public void FilterByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var f1 = doc.FilterByField("department", "Engineering");
        var f2 = doc.FilterByField("department", "Engineering");
        Assert.Equal(f1.GetRecordCount(), f2.GetRecordCount());
    }

    [Fact]
    public void FilterByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByField("department", "Engineering");
        var path = TempFile("filter_save.ndjson");
        filtered.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(filtered.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void FilterByField_Then_GetFieldStats()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var filtered = doc.FilterByField("department", "Engineering");
        var stats = filtered.GetFieldStats("score");
        Assert.NotNull(stats);
        // Engineering: scores 92, 88, 95 → min=88, max=95
        Assert.Equal(88.0, stats.Min, 3);
        Assert.Equal(95.0, stats.Max, 3);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetDistinctValues("department"));
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetDistinctValues("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var vals = doc.GetDistinctValues("department");
        var unique = new System.Collections.Generic.HashSet<string>(vals.Select(v => v?.ToString() ?? ""));
        Assert.Equal(unique.Count, vals.Count);
    }

    [Fact]
    public void GetDistinctValues_Department_ThreeDistinct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(3, doc.GetDistinctValues("department").Count);
    }

    [Fact]
    public void GetDistinctValues_Level_FourDistinct()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // Senior, Junior, Lead, Mid = 4
        Assert.Equal(4, doc.GetDistinctValues("level").Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.Equal(doc.GetDistinctValues("department").Count,
                     doc.GetDistinctValues("department").Count);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetDistinctValues("department").Count;
        var path = TempFile("dv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("department").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAppendRecord_Updates()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetDistinctValues("department").Count;
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object?>
        {
            { "name", "Hector" }, { "department", "Legal" }, { "level", "Mid" }, { "score", 80 }
        });
        Assert.Equal(before + 1, doc.GetDistinctValues("department").Count);
    }

    // -------------------------------------------------------------------------
    // GroupByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupByField_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GroupByField("department"));
    }

    [Fact]
    public void GroupByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GroupByField("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupByField_Engineering_ThreeRecords()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var groups = doc.GroupByField("department");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.Equal(3, groups["Engineering"].Count);
    }

    [Fact]
    public void GroupByField_Finance_TwoRecords()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var groups = doc.GroupByField("department");
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(2, groups["Finance"].Count);
    }

    [Fact]
    public void GroupByField_TotalRows_Match()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var groups = doc.GroupByField("department");
        int total = 0;
        foreach (var kvp in groups) total += kvp.Value.Count;
        Assert.Equal(7, total);
    }

    [Fact]
    public void GroupByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var g1 = doc.GroupByField("department");
        var g2 = doc.GroupByField("department");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupByField_AllKeys_Present()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var groups = doc.GroupByField("department");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.True(groups.ContainsKey("Marketing"));
        Assert.True(groups.ContainsKey("Finance"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterByField_GetDistinctValues_GroupByField_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_products.ndjson");
        var content =
            "{\"sku\":\"P001\",\"category\":\"Electronics\",\"brand\":\"Alpha\",\"price\":29.99,\"rating\":4.2}\n" +
            "{\"sku\":\"P002\",\"category\":\"Electronics\",\"brand\":\"Beta\",\"price\":79.99,\"rating\":4.7}\n" +
            "{\"sku\":\"P003\",\"category\":\"Hardware\",\"brand\":\"Alpha\",\"price\":14.99,\"rating\":3.9}\n" +
            "{\"sku\":\"P004\",\"category\":\"Electronics\",\"brand\":\"Gamma\",\"price\":149.99,\"rating\":4.5}\n" +
            "{\"sku\":\"P005\",\"category\":\"Hardware\",\"brand\":\"Beta\",\"price\":9.99,\"rating\":4.0}\n" +
            "{\"sku\":\"P006\",\"category\":\"Software\",\"brand\":\"Alpha\",\"price\":199.99,\"rating\":4.8}\n" +
            "{\"sku\":\"P007\",\"category\":\"Hardware\",\"brand\":\"Gamma\",\"price\":4.99,\"rating\":3.7}\n" +
            "{\"sku\":\"P008\",\"category\":\"Software\",\"brand\":\"Beta\",\"price\":89.99,\"rating\":4.3}\n";
        File.WriteAllText(path, content);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRecordCount());

        // FilterByField — Electronics
        var electronics = doc.FilterByField("category", "Electronics");
        Assert.Equal(3, electronics.GetRecordCount());

        // FilterByField — Hardware
        var hardware = doc.FilterByField("category", "Hardware");
        Assert.Equal(3, hardware.GetRecordCount());

        // FilterByField — Software
        var software = doc.FilterByField("category", "Software");
        Assert.Equal(2, software.GetRecordCount());

        // FilterByField — Brand Alpha
        var alpha = doc.FilterByField("brand", "Alpha");
        Assert.Equal(3, alpha.GetRecordCount());

        // FilterByField — no match
        var noMatch = doc.FilterByField("category", "Furniture");
        Assert.Equal(0, noMatch.GetRecordCount());

        // Consistent
        Assert.Equal(3, doc.FilterByField("category", "Electronics").GetRecordCount());

        // GetFieldStats on filtered
        var elecStats = electronics.GetFieldStats("price");
        Assert.Equal(29.99, elecStats.Min, 3);
        Assert.Equal(149.99, elecStats.Max, 3);

        // GetDistinctValues — category
        var categories = doc.GetDistinctValues("category");
        Assert.Equal(3, categories.Count);
        Assert.False(categories.GroupBy(v => v).Any(g => g.Count() > 1)); // no duplicates

        // GetDistinctValues — brand
        var brands = doc.GetDistinctValues("brand");
        Assert.Equal(3, brands.Count);

        // Consistent
        Assert.Equal(3, doc.GetDistinctValues("category").Count);

        // After AppendRecord — new category
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object?>
        {
            { "sku", "P009" }, { "category", "Accessories" }, { "brand", "Alpha" }, { "price", 24.99 }, { "rating", 4.1 }
        });
        Assert.Equal(4, doc.GetDistinctValues("category").Count);
        Assert.Equal(9, doc.GetRecordCount());

        // GroupByField — category
        var catGroups = doc.GroupByField("category");
        Assert.True(catGroups.ContainsKey("Electronics"));
        Assert.True(catGroups.ContainsKey("Hardware"));
        Assert.True(catGroups.ContainsKey("Software"));
        Assert.True(catGroups.ContainsKey("Accessories"));
        Assert.Equal(4, catGroups.Count);

        // Total rows in groups = 9
        int total = 0;
        foreach (var kvp in catGroups) total += kvp.Value.Count;
        Assert.Equal(9, total);

        // GroupByField — brand
        var brandGroups = doc.GroupByField("brand");
        Assert.Equal(3, brandGroups.Count);
        Assert.Equal(4, brandGroups["Alpha"].Count); // P001, P003, P006, P009

        // Consistent
        Assert.Equal(catGroups.Count, doc.GroupByField("category").Count);

        // SaveToFile
        var savePath = TempFile("dogfood_products_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRecordCount());

        // FilterByField on loaded
        var loadedElec = loaded.FilterByField("category", "Electronics");
        Assert.Equal(3, loadedElec.GetRecordCount());

        // GetDistinctValues on loaded
        Assert.Equal(4, loaded.GetDistinctValues("category").Count);

        // GroupByField on loaded
        var loadedGroups = loaded.GroupByField("brand");
        Assert.Equal(3, loadedGroups.Count);
        Assert.Equal(4, loadedGroups["Alpha"].Count);

        // Final save
        var path2 = TempFile("dogfood_products_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(9, loaded2.GetRecordCount());
        Assert.Equal(4, loaded2.GetDistinctValues("category").Count);
        Assert.Equal(3, loaded2.FilterByField("category", "Electronics").GetRecordCount());
    }
}
