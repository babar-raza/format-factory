// Tests for NdjsonDocument.GetFieldEntropy, GetFieldDistinctRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R274

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R274: Tests for NdjsonDocument.GetFieldEntropy, GetFieldDistinctRatio deeper.
/// GetFieldEntropy(field): returns Shannon entropy (bits) of the value distribution in the field.
/// GetFieldDistinctRatio(field): returns (distinct count / record count) as a fraction 0..1.
/// Covers: GetFieldEntropy no-throw; GetFieldEntropy non-negative; GetFieldEntropy consistent;
/// GetFieldEntropy zero for constant; GetFieldEntropy save-load;
/// GetFieldDistinctRatio no-throw; GetFieldDistinctRatio in-range;
/// GetFieldDistinctRatio one for all-unique; GetFieldDistinctRatio near-zero for constant;
/// GetFieldDistinctRatio consistent; GetFieldDistinctRatio save-load;
/// dogfood CreateDoc→GetFieldEntropy→GetFieldDistinctRatio→SaveToFile pipeline.
/// </summary>
public class NdjsonR274GetFieldEntropyAndDistinctRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR274GetFieldEntropyAndDistinctRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR274_" + Guid.NewGuid().ToString("N"));
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
        string[] categories = { "A", "B", "C", "D" };
        var rng = new Random(42);
        for (int i = 0; i < 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"category\":\"{categories[rng.Next(categories.Length)]}\",\"score\":{rng.Next(100)}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{{\"id\":{i},\"region\":\"UK\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniqueNdjson()
    {
        var path = TempFile("unique.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{{\"id\":\"REC{i:D6}\",\"value\":{i}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldEntropy_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldEntropy("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldEntropy_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldEntropy("category") >= 0.0);
    }

    [Fact]
    public void GetFieldEntropy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldEntropy("category"), doc.GetFieldEntropy("category"));
    }

    [Fact]
    public void GetFieldEntropy_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldEntropy("region"), precision: 8);
    }

    [Fact]
    public void GetFieldEntropy_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldEntropy("category");
        var path = TempFile("ent_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldEntropy("category"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetFieldDistinctRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldDistinctRatio_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldDistinctRatio("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldDistinctRatio_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var dr = doc.GetFieldDistinctRatio("category");
        Assert.True(dr >= 0.0 && dr <= 1.0);
    }

    [Fact]
    public void GetFieldDistinctRatio_One_ForAllUnique()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniqueNdjson());
        Assert.Equal(1.0, doc.GetFieldDistinctRatio("id"), precision: 6);
    }

    [Fact]
    public void GetFieldDistinctRatio_NearZero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.True(doc.GetFieldDistinctRatio("region") <= 0.05);
    }

    [Fact]
    public void GetFieldDistinctRatio_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldDistinctRatio("category"), doc.GetFieldDistinctRatio("category"));
    }

    [Fact]
    public void GetFieldDistinctRatio_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldDistinctRatio("category");
        var path = TempFile("dr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldDistinctRatio("category"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldEntropy_GetFieldDistinctRatio_SaveToFile_Pipeline()
    {
        // Government — DVLA: Vehicle Registration and MOT Data Stream 2024
        // Real-time MOT failure event stream — entropy and distinct ratio analysis
        // Used for DVSA fleet risk segmentation and targeted enforcement scheduling

        var path = TempFile("dvla_mot_events.ndjson");
        var sb = new StringBuilder();

        var rng = new Random(20241101);
        string[] makes = { "Ford", "Vauxhall", "Volkswagen", "BMW", "Toyota", "Honda", "Renault", "Peugeot",
                            "Hyundai", "Kia", "Mercedes", "Audi", "Nissan", "Fiat", "Skoda" };
        string[] failureReasons = {
            "Brake_defect", "Brake_defect", "Brake_defect",       // Most common
            "Tyre_condition", "Tyre_condition", "Tyre_condition",   // Second most
            "Lighting_failure", "Lighting_failure",                  // Third
            "Suspension", "Exhaust_emission", "Steering",
            "Windscreen", "Wiper_failure", "Horn", "Seatbelt"       // Less common
        };
        string[] fuels = { "Petrol", "Petrol", "Diesel", "Diesel", "Electric", "Hybrid" };
        string[] ageGroups = { "0-3", "3-5", "5-8", "8-12", "12+" };
        string[] testStations = { "ATL001", "ATL002", "ATL003", "ATL004", "ATL005",
                                   "ATL006", "ATL007", "ATL008", "ATL009", "ATL010",
                                   "ATL011", "ATL012", "ATL013", "ATL014", "ATL015",
                                   "ATL016", "ATL017", "ATL018", "ATL019", "ATL020" };
        string[] outcomes = { "FAIL", "FAIL", "FAIL", "PASS", "ADVISORY" }; // 60% fail rate in stream

        for (int i = 0; i < 350; i++)
        {
            string vrm = $"{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}{rng.Next(10)}{rng.Next(10)}{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}{(char)('A' + rng.Next(26))}";
            string make = makes[rng.Next(makes.Length)];
            string fuel = fuels[rng.Next(fuels.Length)];
            string age = ageGroups[rng.Next(ageGroups.Length)];
            string station = testStations[rng.Next(testStations.Length)];
            string outcome = outcomes[rng.Next(outcomes.Length)];
            string failReason = outcome == "FAIL" ? failureReasons[rng.Next(failureReasons.Length)] : "None";
            int mileage = 5000 + rng.Next(200000);
            double testFee = 54.85;

            sb.AppendLine($"{{\"event_id\":\"MOT{i:D8}\",\"vrm\":\"{vrm}\",\"make\":\"{make}\",\"fuel_type\":\"{fuel}\",\"vehicle_age_band\":\"{age}\",\"test_station\":\"{station}\",\"outcome\":\"{outcome}\",\"failure_reason\":\"{failReason}\",\"mileage\":{mileage},\"test_fee\":{testFee}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(350, doc.RecordCount);

        // Entropy of failure_reason — brake_defect/tyre dominate → medium entropy
        var entFailure = doc.GetFieldEntropy("failure_reason");
        Assert.True(entFailure >= 0.0);
        Assert.Equal(entFailure, doc.GetFieldEntropy("failure_reason")); // consistent

        // Entropy of make — 15 makes roughly uniform → higher entropy
        var entMake = doc.GetFieldEntropy("make");
        Assert.True(entMake >= 0.0);
        Assert.True(entMake > 0.0); // must have some variety

        // Entropy of outcome — 3 outcomes (FAIL/PASS/ADVISORY) → lower than make
        var entOutcome = doc.GetFieldEntropy("outcome");
        Assert.True(entOutcome >= 0.0);
        Assert.True(entOutcome < entMake); // 3 outcomes vs 15 makes

        // Entropy of test_fee — all same (£54.85) → zero entropy
        var entFee = doc.GetFieldEntropy("test_fee");
        Assert.Equal(0.0, entFee, precision: 6);

        // DistinctRatio of event_id — all unique → 1.0
        var drId = doc.GetFieldDistinctRatio("event_id");
        Assert.Equal(1.0, drId, precision: 6);

        // DistinctRatio of make — 15 makes / 350 records ≈ 0.043
        var drMake = doc.GetFieldDistinctRatio("make");
        Assert.True(drMake >= 0.0 && drMake <= 1.0);
        Assert.True(drMake < 0.1);

        // DistinctRatio of outcome — 3 values / 350 → ~0.009
        var drOutcome = doc.GetFieldDistinctRatio("outcome");
        Assert.True(drOutcome >= 0.0 && drOutcome <= 1.0);
        Assert.True(drOutcome <= 0.02); // 3 / 350

        // DistinctRatio of test_fee — constant → near-zero
        var drFee = doc.GetFieldDistinctRatio("test_fee");
        Assert.True(drFee <= 0.01);
        Assert.Equal(0.0, doc.GetFieldEntropy("test_fee"), precision: 6); // entropy = 0

        // SaveToFile
        var out1 = TempFile("dvla_mot_events_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(entFailure, loaded.GetFieldEntropy("failure_reason"), precision: 8);
        Assert.Equal(entMake, loaded.GetFieldEntropy("make"), precision: 8);
        Assert.Equal(drId, loaded.GetFieldDistinctRatio("event_id"), precision: 8);
        Assert.Equal(drMake, loaded.GetFieldDistinctRatio("make"), precision: 8);

        // Append additional records
        var sb2 = new StringBuilder();
        for (int i = 350; i < 360; i++)
            sb2.AppendLine($"{{\"event_id\":\"MOT{i:D8}\",\"vrm\":\"AB12CDE\",\"make\":\"Tesla\",\"fuel_type\":\"Electric\",\"vehicle_age_band\":\"0-3\",\"test_station\":\"ATL001\",\"outcome\":\"PASS\",\"failure_reason\":\"None\",\"mileage\":{5000 + i},\"test_fee\":54.85}}");
        loaded.AppendRecords(sb2.ToString());
        Assert.Equal(360, loaded.RecordCount);

        var entMakeAfter = loaded.GetFieldEntropy("make");
        Assert.True(entMakeAfter >= 0.0); // may change with Tesla added

        // Final save
        var out2 = TempFile("dvla_mot_events_final.ndjson");
        loaded.SaveToFile(out2);
        var final = NdjsonDocument.LoadFile(out2);
        Assert.Equal(360, final.RecordCount);
        Assert.Equal(entMakeAfter, final.GetFieldEntropy("make"), precision: 8);

        var ex1 = Record.Exception(() => final.GetFieldEntropy("outcome"));
        var ex2 = Record.Exception(() => final.GetFieldDistinctRatio("make"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
