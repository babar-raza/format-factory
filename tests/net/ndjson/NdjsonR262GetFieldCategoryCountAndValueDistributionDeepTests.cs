// Tests for NdjsonDocument.GetFieldCategoryCount, GetFieldValueDistribution deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R262

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R262: Tests for NdjsonDocument.GetFieldCategoryCount, GetFieldValueDistribution deeper.
/// GetFieldCategoryCount(fieldName): returns the number of distinct values in the field.
/// GetFieldValueDistribution(fieldName): returns a dictionary/map of value → count.
/// Covers: GetFieldCategoryCount no-throw; GetFieldCategoryCount positive;
/// GetFieldCategoryCount consistent; GetFieldCategoryCount equals GetFieldUniqueCount;
/// GetFieldCategoryCount save-load;
/// GetFieldValueDistribution no-throw; GetFieldValueDistribution non-null;
/// GetFieldValueDistribution counts sum to RecordCount; GetFieldValueDistribution consistent;
/// GetFieldValueDistribution save-load;
/// dogfood CreateDoc→GetFieldCategoryCount→GetFieldValueDistribution pipeline.
/// </summary>
public class NdjsonR262GetFieldCategoryCountAndValueDistributionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR262GetFieldCategoryCountAndValueDistributionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR262_" + Guid.NewGuid().ToString("N"));
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
        var sb = new StringBuilder();
        string[] colours = { "red", "blue", "green", "yellow", "purple" };
        for (int i = 0; i < 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"colour\":\"{colours[i % colours.Length]}\",\"size\":{(i % 3) + 1},\"tag\":\"T{i % 8}\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldCategoryCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCategoryCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldCategoryCount("colour"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCategoryCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldCategoryCount("colour") > 0);
    }

    [Fact]
    public void GetFieldCategoryCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldCategoryCount("colour"), doc.GetFieldCategoryCount("colour"));
    }

    [Fact]
    public void GetFieldCategoryCount_Equals_GetFieldUniqueCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldUniqueCount("colour"), doc.GetFieldCategoryCount("colour"));
    }

    [Fact]
    public void GetFieldCategoryCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldCategoryCount("colour");
        var path = TempFile("cc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldCategoryCount("colour"));
    }

    [Fact]
    public void GetFieldCategoryCount_KnownValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // 5 distinct colours
        Assert.Equal(5, doc.GetFieldCategoryCount("colour"));
    }

    // -------------------------------------------------------------------------
    // GetFieldValueDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueDistribution("colour"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GetFieldValueDistribution("colour"));
    }

    [Fact]
    public void GetFieldValueDistribution_CountsSumToRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dist = doc.GetFieldValueDistribution("colour");
        int total = 0;
        foreach (var kvp in dist)
            total += kvp.Value;
        Assert.Equal(doc.RecordCount, total);
    }

    [Fact]
    public void GetFieldValueDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var d1 = doc.GetFieldValueDistribution("colour");
        var d2 = doc.GetFieldValueDistribution("colour");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetFieldValueDistribution_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldValueDistribution("colour");
        var path = TempFile("vd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetFieldValueDistribution("colour");
        Assert.Equal(before.Count, after.Count);
        foreach (var kvp in before)
        {
            Assert.True(after.ContainsKey(kvp.Key));
            Assert.Equal(kvp.Value, after[kvp.Key]);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldCategoryCount_GetFieldValueDistribution_Pipeline()
    {
        // Housing analytics — Land Registry Price Paid Data transaction stream
        // Category analysis for property types, transaction types, and tenure across regions
        var path = TempFile("land_registry_price_paid.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241210);

        string[] propertyTypes = { "D", "S", "T", "F", "O" }; // Detached, Semi, Terrace, Flat, Other
        string[] propWeights_desc = { "D:0.20", "S:0.30", "T:0.28", "F:0.18", "O:0.04" };
        double[] propWeights = { 0.20, 0.30, 0.28, 0.18, 0.04 };

        string[] txnTypes = { "A", "B" }; // Arms Length, Not Arms Length
        string[] oldNew = { "Y", "N" };   // New build, Established
        string[] duration = { "F", "L" }; // Freehold, Leasehold
        string[] regions = { "London", "South_East", "East_of_England", "South_West", "West_Midlands", "Yorkshire", "North_West", "Scotland" };

        for (int i = 0; i < 180; i++)
        {
            // Sample property type with Zipf weights
            double r = rng.NextDouble();
            double cumProp = 0;
            int propIdx = propertyTypes.Length - 1;
            for (int j = 0; j < propWeights.Length; j++)
            {
                cumProp += propWeights[j];
                if (r <= cumProp) { propIdx = j; break; }
            }

            var ptype = propertyTypes[propIdx];
            var txnType = txnTypes[i % 2 == 0 ? 0 : 0]; // mostly arms length
            var newBuild = rng.NextDouble() < 0.12 ? "Y" : "N";
            var tenure = ptype == "F" ? "L" : (rng.NextDouble() < 0.8 ? "F" : "L");
            var region = regions[i % regions.Length];
            double price = ptype == "D" ? (400000 + rng.NextDouble() * 800000) :
                          ptype == "S" ? (250000 + rng.NextDouble() * 400000) :
                          ptype == "T" ? (200000 + rng.NextDouble() * 300000) :
                          ptype == "F" ? (150000 + rng.NextDouble() * 350000) :
                          (100000 + rng.NextDouble() * 500000);
            if (region == "London") price *= 1.8;
            string postcode = $"{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}{rng.Next(1, 20)} {rng.Next(1, 9)}{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}";
            string transferDate = $"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}";

            sb.AppendLine($"{{\"transaction_id\":\"{{{{A{i:D6}-{rng.Next(10000):D4}-4{rng.Next(10)}{rng.Next(10)}{rng.Next(10)}{rng.Next(10)}}}}}\"," +
                         $"\"price_paid_gbp\":{price:F0}," +
                         $"\"transfer_date\":\"{transferDate}\"," +
                         $"\"postcode\":\"{postcode}\"," +
                         $"\"property_type\":\"{ptype}\"," +
                         $"\"old_new\":\"{newBuild}\"," +
                         $"\"duration\":\"{tenure}\"," +
                         $"\"txn_category_type\":\"{txnType}\"," +
                         $"\"region\":\"{region}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(180, doc.RecordCount);

        // GetFieldCategoryCount
        var ccPtype = doc.GetFieldCategoryCount("property_type");
        Assert.True(ccPtype > 0);
        Assert.Equal(ccPtype, doc.GetFieldCategoryCount("property_type")); // consistent
        Assert.Equal(doc.GetFieldUniqueCount("property_type"), ccPtype); // matches unique count
        Assert.Equal(5, ccPtype); // D, S, T, F, O

        var ccRegion = doc.GetFieldCategoryCount("region");
        Assert.True(ccRegion > 0);
        Assert.Equal(8, ccRegion);

        var ccDuration = doc.GetFieldCategoryCount("duration");
        Assert.True(ccDuration > 0);

        var ccOldNew = doc.GetFieldCategoryCount("old_new");
        Assert.True(ccOldNew <= 2); // Y or N

        // GetFieldValueDistribution
        var distPtype = doc.GetFieldValueDistribution("property_type");
        Assert.NotNull(distPtype);
        int ptypeTotal = 0;
        foreach (var kvp in distPtype) ptypeTotal += kvp.Value;
        Assert.Equal(doc.RecordCount, ptypeTotal);
        Assert.Equal(distPtype, doc.GetFieldValueDistribution("property_type")); // consistent by count

        var distRegion = doc.GetFieldValueDistribution("region");
        Assert.NotNull(distRegion);
        int regionTotal = 0;
        foreach (var kvp in distRegion) regionTotal += kvp.Value;
        Assert.Equal(doc.RecordCount, regionTotal);
        Assert.Equal(8, distRegion.Count);

        var distDuration = doc.GetFieldValueDistribution("duration");
        Assert.NotNull(distDuration);
        int durationTotal = 0;
        foreach (var kvp in distDuration) durationTotal += kvp.Value;
        Assert.Equal(doc.RecordCount, durationTotal);

        // Verify T (Terrace) is present in property type distribution
        Assert.True(distPtype.ContainsKey("T"));
        Assert.True(distPtype["T"] > 0);

        // Field stats — price analysis
        var meanPrice = doc.GetFieldMean("price_paid_gbp");
        Assert.True(meanPrice > 0.0);
        var minPrice = doc.GetFieldMin("price_paid_gbp");
        var maxPrice = doc.GetFieldMax("price_paid_gbp");
        Assert.True(minPrice <= maxPrice);

        // SaveToFile
        var outPath = TempFile("land_registry_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(ccPtype, loaded.GetFieldCategoryCount("property_type"));
        Assert.Equal(ccRegion, loaded.GetFieldCategoryCount("region"));
        var loadedDist = loaded.GetFieldValueDistribution("property_type");
        Assert.Equal(distPtype.Count, loadedDist.Count);
        foreach (var kvp in distPtype)
        {
            Assert.True(loadedDist.ContainsKey(kvp.Key));
            Assert.Equal(kvp.Value, loadedDist[kvp.Key]);
        }

        // Additional no-throw
        var ex1 = Record.Exception(() => loaded.GetFieldCategoryCount("old_new"));
        var ex2 = Record.Exception(() => loaded.GetFieldValueDistribution("region"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
