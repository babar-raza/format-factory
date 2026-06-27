// Tests for NdjsonDocument.GetFieldUniqueCount, GetFieldMode deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R279

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R279: Tests for NdjsonDocument.GetFieldUniqueCount, GetFieldMode deeper.
/// GetFieldUniqueCount(field): returns the number of distinct non-null values in the named field.
/// GetFieldMode(field): returns the most frequently occurring value string in the named field.
/// Covers: GetFieldUniqueCount no-throw; GetFieldUniqueCount positive;
/// GetFieldUniqueCount one for uniform; GetFieldUniqueCount consistent;
/// GetFieldUniqueCount save-load;
/// GetFieldMode no-throw; GetFieldMode non-null-or-empty;
/// GetFieldMode is most frequent value; GetFieldMode consistent;
/// GetFieldMode save-load; dogfood pipeline.
/// </summary>
public class NdjsonR279GetFieldUniqueCountAndFieldModeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR279GetFieldUniqueCountAndFieldModeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR279_" + Guid.NewGuid().ToString("N"));
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
        var lines = new StringBuilder();
        // 15 records: status "active"(8), "pending"(5), "closed"(2)
        for (int i = 0; i < 8; i++)
            lines.AppendLine($"{{\"id\":{i},\"status\":\"active\",\"score\":{i * 5}}}");
        for (int i = 8; i < 13; i++)
            lines.AppendLine($"{{\"id\":{i},\"status\":\"pending\",\"score\":{i * 5}}}");
        for (int i = 13; i < 15; i++)
            lines.AppendLine($"{{\"id\":{i},\"status\":\"closed\",\"score\":{i * 5}}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"category\":\"electronics\"}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldUniqueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldUniqueCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldUniqueCount("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldUniqueCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldUniqueCount("status") > 0);
    }

    [Fact]
    public void GetFieldUniqueCount_One_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(1, doc.GetFieldUniqueCount("category"));
    }

    [Fact]
    public void GetFieldUniqueCount_Three_ForThreeValues()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(3, doc.GetFieldUniqueCount("status"));
    }

    [Fact]
    public void GetFieldUniqueCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldUniqueCount("status"), doc.GetFieldUniqueCount("status"));
    }

    [Fact]
    public void GetFieldUniqueCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldUniqueCount("status");
        var path = TempFile("uc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldUniqueCount("status"));
    }

    // -------------------------------------------------------------------------
    // GetFieldMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMode_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMode("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMode_NonNullOrEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.False(string.IsNullOrEmpty(doc.GetFieldMode("status")));
    }

    [Fact]
    public void GetFieldMode_Is_MostFrequent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal("active", doc.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMode("status"), doc.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMode("status");
        var path = TempFile("mode_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMode("status"));
    }

    [Fact]
    public void GetFieldMode_ForUniform_ReturnsThatValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal("electronics", doc.GetFieldMode("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldUniqueCount_GetFieldMode_Pipeline()
    {
        // Transport — DfT / DVSA: MOT Test Results 2023-24
        // Annual vehicle test records: outcome distribution, fault class frequency, and adviser info
        // Unique count and mode track pass/fail distributions and most common fault categories

        var path = TempFile("dvsa_mot_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240401);

        string[] outcomes = { "Pass", "Pass", "Pass", "Pass", "Fail", "Fail", "Advisory" };
        string[] faultClasses = { "C1_Dangerous", "C2_Major", "C3_Minor", "Advisory_Item", "None" };
        string[] faultClassDist = { "None", "None", "None", "C3_Minor", "C3_Minor", "C2_Major", "Advisory_Item" };
        string[] testStations = {
            "MOT001", "MOT002", "MOT003", "MOT004", "MOT005",
            "MOT001", "MOT001", "MOT001", "MOT002", "MOT002"  // MOT001 most common
        };
        string[] vehicleClasses = { "Class_4", "Class_4", "Class_4", "Class_4", "Class_7", "Class_7", "Class_1" };
        string[] fuelTypes = { "Petrol", "Petrol", "Diesel", "Diesel", "Electric", "Hybrid", "Petrol" };

        for (int i = 0; i < 500; i++)
        {
            string outcome = outcomes[rng.Next(outcomes.Length)];
            string faultClass = outcome == "Pass" ? "None"
                              : outcome == "Advisory" ? "Advisory_Item"
                              : faultClassDist[rng.Next(faultClassDist.Length)];
            string station = testStations[rng.Next(testStations.Length)];
            string vehicleClass = vehicleClasses[rng.Next(vehicleClasses.Length)];
            string fuelType = fuelTypes[rng.Next(fuelTypes.Length)];
            int mileage = 5000 + rng.Next(0, 150000);
            int vehicleAge = 1 + rng.Next(0, 25);
            double testDuration = 30 + rng.NextDouble() * 45;

            sb.AppendLine($"{{\"test_id\":\"MOT{i:D6}\",\"outcome\":\"{outcome}\"," +
                          $"\"fault_class\":\"{faultClass}\",\"test_station\":\"{station}\"," +
                          $"\"vehicle_class\":\"{vehicleClass}\",\"fuel_type\":\"{fuelType}\"," +
                          $"\"mileage\":{mileage},\"vehicle_age_years\":{vehicleAge}," +
                          $"\"test_duration_mins\":{testDuration:F1}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(500, doc.RecordCount);

        // Outcome unique count (Pass, Fail, Advisory = 3)
        var outcomeUnique = doc.GetFieldUniqueCount("outcome");
        Assert.Equal(3, outcomeUnique);

        // Outcome mode should be Pass (most frequent in sampling array)
        var outcomeMode = doc.GetFieldMode("outcome");
        Assert.Equal("Pass", outcomeMode);
        Assert.Equal(outcomeMode, doc.GetFieldMode("outcome")); // consistent

        // Fault class unique count (C2_Major, C3_Minor, Advisory_Item, None = 4 or fewer)
        var faultUnique = doc.GetFieldUniqueCount("fault_class");
        Assert.True(faultUnique >= 1 && faultUnique <= 5);
        Assert.Equal(faultUnique, doc.GetFieldUniqueCount("fault_class")); // consistent

        // Fault class mode (None or C3_Minor likely most common)
        var faultMode = doc.GetFieldMode("fault_class");
        Assert.False(string.IsNullOrEmpty(faultMode));
        Assert.Equal(faultMode, doc.GetFieldMode("fault_class")); // consistent

        // Station unique count (≤10 distinct stations)
        var stationUnique = doc.GetFieldUniqueCount("test_station");
        Assert.True(stationUnique >= 1 && stationUnique <= 10);

        // Station mode should be MOT001 (appears most often in sampling array)
        var stationMode = doc.GetFieldMode("test_station");
        Assert.Equal("MOT001", stationMode);

        // Fuel type unique count (≤7)
        var fuelUnique = doc.GetFieldUniqueCount("fuel_type");
        Assert.True(fuelUnique >= 1 && fuelUnique <= 7);

        // Vehicle class unique count (≤3)
        var classUnique = doc.GetFieldUniqueCount("vehicle_class");
        Assert.True(classUnique >= 1 && classUnique <= 3);

        // Vehicle class mode should be Class_4 (most frequent in sampling)
        var classMode = doc.GetFieldMode("vehicle_class");
        Assert.Equal("Class_4", classMode);

        // SaveToFile
        var outPath = TempFile("dvsa_mot_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(outcomeUnique, loaded.GetFieldUniqueCount("outcome"));
        Assert.Equal(outcomeMode, loaded.GetFieldMode("outcome"));
        Assert.Equal(stationUnique, loaded.GetFieldUniqueCount("test_station"));
        Assert.Equal(stationMode, loaded.GetFieldMode("test_station"));
        Assert.Equal(faultUnique, loaded.GetFieldUniqueCount("fault_class"));

        var ex1 = Record.Exception(() => loaded.GetFieldUniqueCount("outcome"));
        var ex2 = Record.Exception(() => loaded.GetFieldMode("fault_class"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
