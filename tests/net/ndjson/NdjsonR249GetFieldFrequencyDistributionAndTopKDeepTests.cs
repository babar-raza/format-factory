// Tests for NdjsonDocument.GetFieldFrequencyDistribution, GetTopKFieldValues, GetFieldValueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R249

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R249: Tests for NdjsonDocument.GetFieldFrequencyDistribution, GetTopKFieldValues, GetFieldValueCount deeper.
/// GetFieldFrequencyDistribution(fieldName): returns a dictionary mapping field values to their occurrence counts.
/// GetTopKFieldValues(fieldName, k): returns the k most frequent distinct values for the field.
/// GetFieldValueCount(fieldName, value): returns the number of records with the specified field value.
/// Covers: GetFieldFrequencyDistribution no-throw; GetFieldFrequencyDistribution non-null;
/// GetFieldFrequencyDistribution consistent; GetFieldFrequencyDistribution sum equals record count;
/// GetTopKFieldValues no-throw; GetTopKFieldValues non-null; GetTopKFieldValues count <= k;
/// GetTopKFieldValues consistent;
/// GetFieldValueCount no-throw; GetFieldValueCount non-negative; GetFieldValueCount consistent;
/// GetFieldValueCount zero for absent value; GetFieldValueCount save-load;
/// dogfood CreateDoc→GetFieldFrequencyDistribution→GetTopKFieldValues→GetFieldValueCount pipeline.
/// </summary>
public class NdjsonR249GetFieldFrequencyDistributionAndTopKDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR249GetFieldFrequencyDistributionAndTopKDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR249_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTicketSystemNdjson()
    {
        var path = TempFile("tickets.ndjson");
        string[] priorities = { "Critical", "High", "Medium", "Low" };
        string[] statuses = { "Open", "In_Progress", "Resolved", "Closed" };
        string[] teams = { "Platform", "Security", "Product", "DevOps" };
        var rng = new Random(20240501);
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var p = priorities[i % 4];
            var s = statuses[i % 4];
            var t = teams[i % 4];
            lines.Add($"{{\"ticket_id\":\"TKT{i:D4}\",\"priority\":\"{p}\",\"status\":\"{s}\",\"team\":\"{t}\",\"sla_hours\":{(i % 3 + 1) * 4}}}");
        }
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldFrequencyDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldFrequencyDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var ex = Record.Exception(() => doc.GetFieldFrequencyDistribution("priority"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldFrequencyDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        Assert.NotNull(doc.GetFieldFrequencyDistribution("priority"));
    }

    [Fact]
    public void GetFieldFrequencyDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var dist1 = doc.GetFieldFrequencyDistribution("status");
        var dist2 = doc.GetFieldFrequencyDistribution("status");
        Assert.Equal(dist1.Count, dist2.Count);
    }

    [Fact]
    public void GetFieldFrequencyDistribution_Sum_Equals_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var dist = doc.GetFieldFrequencyDistribution("priority");
        int total = 0;
        foreach (var kv in dist) total += kv.Value;
        Assert.Equal(doc.RecordCount, total);
    }

    // -------------------------------------------------------------------------
    // GetTopKFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopKFieldValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var ex = Record.Exception(() => doc.GetTopKFieldValues("priority", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopKFieldValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        Assert.NotNull(doc.GetTopKFieldValues("priority", 3));
    }

    [Fact]
    public void GetTopKFieldValues_Count_LessOrEqual_K()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var top3 = doc.GetTopKFieldValues("priority", 3);
        Assert.True(top3.Count <= 3);
    }

    [Fact]
    public void GetTopKFieldValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var top1 = doc.GetTopKFieldValues("status", 2);
        var top2 = doc.GetTopKFieldValues("status", 2);
        Assert.Equal(top1.Count, top2.Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldValueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueCount("priority", "Critical"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        Assert.True(doc.GetFieldValueCount("priority", "High") >= 0);
    }

    [Fact]
    public void GetFieldValueCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        Assert.Equal(
            doc.GetFieldValueCount("status", "Open"),
            doc.GetFieldValueCount("status", "Open"));
    }

    [Fact]
    public void GetFieldValueCount_Zero_ForAbsent_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        Assert.Equal(0, doc.GetFieldValueCount("priority", "Catastrophic_NonExistent"));
    }

    [Fact]
    public void GetFieldValueCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTicketSystemNdjson());
        var before = doc.GetFieldValueCount("team", "Platform");
        var path = TempFile("fvc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldValueCount("team", "Platform"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldFrequencyDistribution_GetTopKFieldValues_GetFieldValueCount_Pipeline()
    {
        // E-commerce — customer order event stream for purchase behaviour analytics
        var path = TempFile("order_events.ndjson");
        string[] events = { "cart_add", "cart_remove", "checkout_start", "payment_initiated", "order_confirmed", "order_cancelled" };
        string[] categories = { "Electronics", "Clothing", "Home_Garden", "Sports", "Books", "Beauty" };
        string[] devices = { "Mobile", "Desktop", "Tablet" };
        string[] countries = { "GB", "US", "DE", "FR", "AU", "CA" };
        var rng = new Random(20240401);
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var evt = events[i % 6];
            var cat = categories[i % 6];
            var dev = devices[i % 3];
            var country = countries[i % 6];
            double value = 15.0 + rng.NextDouble() * 285.0;
            lines.Add($"{{\"event_id\":\"EVT{i:D5}\",\"event_type\":\"{evt}\",\"category\":\"{cat}\",\"device\":\"{dev}\",\"country\":\"{country}\",\"order_value\":{value:F2}}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetFieldFrequencyDistribution — event types
        var evtDist = doc.GetFieldFrequencyDistribution("event_type");
        Assert.NotNull(evtDist);
        int total = 0;
        foreach (var kv in evtDist) total += kv.Value;
        Assert.Equal(doc.RecordCount, total);
        var evtDist2 = doc.GetFieldFrequencyDistribution("event_type");
        Assert.Equal(evtDist.Count, evtDist2.Count); // consistent

        // GetFieldFrequencyDistribution — device types
        var devDist = doc.GetFieldFrequencyDistribution("device");
        Assert.NotNull(devDist);
        int devTotal = 0;
        foreach (var kv in devDist) devTotal += kv.Value;
        Assert.Equal(doc.RecordCount, devTotal);

        // GetTopKFieldValues — top 3 categories
        var topCats = doc.GetTopKFieldValues("category", 3);
        Assert.NotNull(topCats);
        Assert.True(topCats.Count <= 3);
        Assert.Equal(topCats.Count, doc.GetTopKFieldValues("category", 3).Count); // consistent

        // GetTopKFieldValues — top 2 countries
        var topCountries = doc.GetTopKFieldValues("country", 2);
        Assert.NotNull(topCountries);
        Assert.True(topCountries.Count <= 2);

        // GetFieldValueCount — specific event type
        var cartAdds = doc.GetFieldValueCount("event_type", "cart_add");
        Assert.True(cartAdds >= 0);
        Assert.Equal(cartAdds, doc.GetFieldValueCount("event_type", "cart_add")); // consistent

        var mobileCount = doc.GetFieldValueCount("device", "Mobile");
        Assert.True(mobileCount >= 0);

        var noneCount = doc.GetFieldValueCount("event_type", "event_does_not_exist");
        Assert.Equal(0, noneCount);

        // SaveToFile
        var outPath = TempFile("order_events_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(cartAdds, loaded.GetFieldValueCount("event_type", "cart_add"));
        Assert.NotNull(loaded.GetFieldFrequencyDistribution("device"));
        Assert.NotNull(loaded.GetTopKFieldValues("category", 3));
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // GetRecord consistency
        var record0 = loaded.GetRecord(0);
        Assert.NotNull(record0);

        var ex1 = Record.Exception(() => loaded.GetFieldFrequencyDistribution("country"));
        var ex2 = Record.Exception(() => loaded.GetTopKFieldValues("device", 5));
        var ex3 = Record.Exception(() => loaded.GetFieldValueCount("category", "Electronics"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
