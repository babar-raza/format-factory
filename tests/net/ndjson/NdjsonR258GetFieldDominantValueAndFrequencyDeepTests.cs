// Tests for NdjsonDocument.GetFieldDominantValue, GetFieldDominantValueFrequency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R258

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R258: Tests for NdjsonDocument.GetFieldDominantValue, GetFieldDominantValueFrequency deeper.
/// GetFieldDominantValue(fieldName): returns the most frequently occurring value for the field.
/// GetFieldDominantValueFrequency(fieldName): returns the count of the dominant value occurrences.
/// Covers: GetFieldDominantValue no-throw; GetFieldDominantValue non-null; GetFieldDominantValue consistent;
/// GetFieldDominantValue in unique values;
/// GetFieldDominantValueFrequency no-throw; GetFieldDominantValueFrequency positive;
/// GetFieldDominantValueFrequency consistent; GetFieldDominantValueFrequency at-least-mean-frequency;
/// GetFieldDominantValueFrequency save-load;
/// dogfood CreateDoc→GetFieldDominantValue→GetFieldDominantValueFrequency pipeline.
/// </summary>
public class NdjsonR258GetFieldDominantValueAndFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR258GetFieldDominantValueAndFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR258_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(33);
        string[] statuses = { "active", "active", "active", "inactive", "pending" }; // active dominant
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{{\"id\":{i},\"status\":\"{statuses[rng.Next(statuses.Length)]}\",\"score\":{rng.Next(100)},\"region\":\"UK\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateKnownDominantNdjson()
    {
        var path = TempFile("known_dominant.ndjson");
        var sb = new StringBuilder();
        // 80% "confirmed", 15% "pending", 5% "rejected"
        for (int i = 0; i < 40; i++) sb.AppendLine($"{{\"id\":{i},\"state\":\"confirmed\"}}");
        for (int i = 40; i < 47; i++) sb.AppendLine($"{{\"id\":{i},\"state\":\"pending\"}}");
        for (int i = 47; i < 50; i++) sb.AppendLine($"{{\"id\":{i},\"state\":\"rejected\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldDominantValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldDominantValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldDominantValue("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldDominantValue_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GetFieldDominantValue("status"));
    }

    [Fact]
    public void GetFieldDominantValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldDominantValue("status"), doc.GetFieldDominantValue("status"));
    }

    [Fact]
    public void GetFieldDominantValue_Is_In_UniqueValues()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownDominantNdjson());
        var dominant = doc.GetFieldDominantValue("state");
        var unique = doc.GetFieldUniqueValues("state");
        Assert.Contains(dominant, unique.Keys);
    }

    [Fact]
    public void GetFieldDominantValue_Known_Dominant()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownDominantNdjson());
        Assert.Equal("confirmed", doc.GetFieldDominantValue("state"));
    }

    // -------------------------------------------------------------------------
    // GetFieldDominantValueFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldDominantValueFrequency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldDominantValueFrequency("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldDominantValueFrequency_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldDominantValueFrequency("status") > 0);
    }

    [Fact]
    public void GetFieldDominantValueFrequency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldDominantValueFrequency("status"), doc.GetFieldDominantValueFrequency("status"));
    }

    [Fact]
    public void GetFieldDominantValueFrequency_Known_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownDominantNdjson());
        Assert.Equal(40, doc.GetFieldDominantValueFrequency("state"));
    }

    [Fact]
    public void GetFieldDominantValueFrequency_AtLeast_Mean_Frequency()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var unique = doc.GetFieldUniqueValues("status");
        double meanFreq = (double)doc.RecordCount / unique.Count;
        Assert.True(doc.GetFieldDominantValueFrequency("status") >= (int)meanFreq);
    }

    [Fact]
    public void GetFieldDominantValueFrequency_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownDominantNdjson());
        var before = doc.GetFieldDominantValueFrequency("state");
        var path = TempFile("dvf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldDominantValueFrequency("state"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldDominantValue_GetFieldDominantValueFrequency_Pipeline()
    {
        // Logistics — last-mile delivery event stream (courier tracking events)
        var path = TempFile("delivery_events.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20250801);

        string[] eventTypes = { "OUT_FOR_DELIVERY", "OUT_FOR_DELIVERY", "OUT_FOR_DELIVERY",
            "DELIVERED", "DELIVERED", "DELIVERY_ATTEMPTED", "RETURNED_TO_DEPOT", "EXCEPTION" };
        string[] depots = { "LHR_001", "LHR_002", "GLA_001", "MAN_001", "BHX_001" };
        string[] failureReasons = { "NOT_HOME", "ACCESS_RESTRICTED", "REFUSED", "DAMAGED_PARCEL", null };
        string[] carriers = { "DPD", "DPD", "DPD", "Royal_Mail", "Royal_Mail", "DHL", "Hermes" };

        int totalEvents = 150;
        int deliveredCount = 0, outForDeliveryCount = 0;
        for (int i = 0; i < totalEvents; i++)
        {
            var evType = eventTypes[rng.Next(eventTypes.Length)];
            if (evType == "DELIVERED") deliveredCount++;
            if (evType == "OUT_FOR_DELIVERY") outForDeliveryCount++;
            var depot = depots[rng.Next(depots.Length)];
            var carrier = carriers[rng.Next(carriers.Length)];
            var ts = $"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}T{rng.Next(24):D2}:{rng.Next(60):D2}:00Z";
            bool hasFail = evType == "DELIVERY_ATTEMPTED";
            var fail = hasFail ? failureReasons[rng.Next(failureReasons.Length - 1)] : null;

            var parts = new System.Collections.Generic.List<string>
            {
                $"\"event_id\":\"EVT{i:D8}\"",
                $"\"parcel_id\":\"PCL{(i / 3):D6}\"",
                $"\"event_type\":\"{evType}\"",
                $"\"depot_code\":\"{depot}\"",
                $"\"carrier\":\"{carrier}\"",
                $"\"timestamp\":\"{ts}\"",
                $"\"sequence\":{(i % 3 + 1)}"
            };
            if (fail != null)
                parts.Add($"\"failure_reason\":\"{fail}\"");
            else
                parts.Add("\"failure_reason\":null");

            sb.AppendLine("{" + string.Join(",", parts) + "}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(totalEvents, doc.RecordCount);

        // GetFieldDominantValue
        var domEventType = doc.GetFieldDominantValue("event_type");
        Assert.NotNull(domEventType);
        Assert.Equal(domEventType, doc.GetFieldDominantValue("event_type")); // consistent

        // Dominant event type should be in unique values
        var uniqueEventTypes = doc.GetFieldUniqueValues("event_type");
        Assert.Contains(domEventType, uniqueEventTypes.Keys);

        var domCarrier = doc.GetFieldDominantValue("carrier");
        Assert.NotNull(domCarrier);
        Assert.Equal("DPD", domCarrier); // DPD appears 3/7 of the time — most frequent

        var domDepot = doc.GetFieldDominantValue("depot_code");
        Assert.NotNull(domDepot);

        // GetFieldDominantValueFrequency
        var freqEventType = doc.GetFieldDominantValueFrequency("event_type");
        Assert.True(freqEventType > 0);
        Assert.Equal(freqEventType, doc.GetFieldDominantValueFrequency("event_type")); // consistent

        // Frequency should be at least 1/number_of_unique_values * total
        var uniqueCount = uniqueEventTypes.Count;
        double meanFreq = (double)totalEvents / uniqueCount;
        Assert.True(freqEventType >= (int)meanFreq);

        var freqCarrier = doc.GetFieldDominantValueFrequency("carrier");
        Assert.True(freqCarrier > 0);
        // DPD frequency should be highest
        var uniqueCarriers = doc.GetFieldUniqueValues("carrier");
        double meanCarrierFreq = (double)totalEvents / uniqueCarriers.Count;
        Assert.True(freqCarrier >= (int)meanCarrierFreq);

        var freqDepot = doc.GetFieldDominantValueFrequency("depot_code");
        Assert.True(freqDepot > 0);

        // Field stats
        Assert.True(doc.GetFieldMean("sequence") > 0.0);
        var allEventTypes = doc.GetFieldUniqueValues("event_type");
        Assert.True(allEventTypes.Count >= 1);

        // Null pattern for failure_reason
        var nullFailure = doc.GetFieldNullPattern("failure_reason");
        Assert.True(nullFailure >= 0);

        // SaveToFile
        var outPath = TempFile("delivery_events_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(totalEvents, loaded.RecordCount);
        Assert.Equal(domEventType, loaded.GetFieldDominantValue("event_type"));
        Assert.Equal(freqEventType, loaded.GetFieldDominantValueFrequency("event_type"));
        Assert.Equal(domCarrier, loaded.GetFieldDominantValue("carrier"));

        // Known dominant test
        var path2 = TempFile("known_counts.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 70; i++) sb2.AppendLine($"{{\"id\":{i},\"status\":\"ACTIVE\"}}");
        for (int i = 70; i < 90; i++) sb2.AppendLine($"{{\"id\":{i},\"status\":\"INACTIVE\"}}");
        for (int i = 90; i < 100; i++) sb2.AppendLine($"{{\"id\":{i},\"status\":\"SUSPENDED\"}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal("ACTIVE", doc2.GetFieldDominantValue("status"));
        Assert.Equal(70, doc2.GetFieldDominantValueFrequency("status"));
    }
}
