// Tests for NdjsonDocument.GetFieldDataType, GetFieldTypeConsistency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R265

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R265: Tests for NdjsonDocument.GetFieldDataType, GetFieldTypeConsistency deeper.
/// GetFieldDataType(fieldName): returns the inferred dominant type of the field ("string","number","boolean","null","mixed").
/// GetFieldTypeConsistency(fieldName): returns the fraction of records where the field has the dominant type (0-1).
/// Covers: GetFieldDataType no-throw; GetFieldDataType non-null; GetFieldDataType non-empty;
/// GetFieldDataType consistent; GetFieldDataType save-load; GetFieldDataType numeric field;
/// GetFieldTypeConsistency no-throw; GetFieldTypeConsistency in [0,1];
/// GetFieldTypeConsistency consistent; GetFieldTypeConsistency one for uniform type;
/// GetFieldTypeConsistency save-load;
/// dogfood CreateDoc→GetFieldDataType→GetFieldTypeConsistency pipeline.
/// </summary>
public class NdjsonR265GetFieldDataTypeAndTypeConsistencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR265GetFieldDataTypeAndTypeConsistencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR265_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTypedNdjson()
    {
        var path = TempFile("typed.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);
        for (int i = 0; i < 80; i++)
        {
            double price = 10 + rng.NextDouble() * 990;
            int qty = rng.Next(1, 100);
            bool active = rng.NextDouble() > 0.3;
            string tag = $"TAG{i % 5}";
            // Mixed field: mostly string but occasionally number
            string mixed = (rng.NextDouble() < 0.8) ? $"\"label_{i % 10}\"" : $"{i * 3}";
            sb.AppendLine($"{{\"id\":{i},\"price\":{price:F2},\"quantity\":{qty},\"active\":{active.ToString().ToLower()},\"tag\":\"{tag}\",\"mixed\":{mixed}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldDataType_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var ex = Record.Exception(() => doc.GetFieldDataType("price"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldDataType_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        Assert.NotNull(doc.GetFieldDataType("price"));
    }

    [Fact]
    public void GetFieldDataType_NonEmpty()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        Assert.NotEmpty(doc.GetFieldDataType("price"));
    }

    [Fact]
    public void GetFieldDataType_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        Assert.Equal(doc.GetFieldDataType("tag"), doc.GetFieldDataType("tag"));
    }

    [Fact]
    public void GetFieldDataType_NumericField()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var dtype = doc.GetFieldDataType("price");
        // Price field is always numeric
        Assert.Equal("number", dtype);
    }

    [Fact]
    public void GetFieldDataType_StringField()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var dtype = doc.GetFieldDataType("tag");
        Assert.Equal("string", dtype);
    }

    [Fact]
    public void GetFieldDataType_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var before = doc.GetFieldDataType("quantity");
        var path = TempFile("dt_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldDataType("quantity"));
    }

    // -------------------------------------------------------------------------
    // GetFieldTypeConsistency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldTypeConsistency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var ex = Record.Exception(() => doc.GetFieldTypeConsistency("price"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldTypeConsistency_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var tc = doc.GetFieldTypeConsistency("price");
        Assert.True(tc >= 0.0 && tc <= 1.0);
    }

    [Fact]
    public void GetFieldTypeConsistency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        Assert.Equal(doc.GetFieldTypeConsistency("tag"), doc.GetFieldTypeConsistency("tag"));
    }

    [Fact]
    public void GetFieldTypeConsistency_One_ForUniformField()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        // Price is always number
        Assert.Equal(1.0, doc.GetFieldTypeConsistency("price"), precision: 6);
    }

    [Fact]
    public void GetFieldTypeConsistency_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateTypedNdjson());
        var before = doc.GetFieldTypeConsistency("tag");
        var path = TempFile("tc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldTypeConsistency("tag"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldDataType_GetFieldTypeConsistency_Pipeline()
    {
        // Data engineering — NHS Digital FHIR R4 resource stream quality validation
        // Observation resources: type schema validation for clinical data pipeline ingestion
        var path = TempFile("fhir_observations.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] loincCodes = {
            "8867-4",  // Heart rate
            "59408-5", // SpO2
            "8310-5",  // Body temperature
            "8480-6",  // Systolic BP
            "8462-4",  // Diastolic BP
            "29463-7", // Body weight
            "8302-2",  // Body height
            "39156-5"  // BMI
        };
        string[] units = { "beats/min", "%", "Cel", "mm[Hg]", "mm[Hg]", "kg", "cm", "kg/m2" };
        double[][] ranges = {
            new[] {40.0, 180.0}, new[] {88.0, 100.0}, new[] {35.5, 40.0},
            new[] {90.0, 200.0}, new[] {55.0, 120.0}, new[] {45.0, 150.0},
            new[] {140.0, 210.0}, new[] {15.0, 60.0}
        };

        for (int i = 0; i < 200; i++)
        {
            int obsIdx = rng.Next(loincCodes.Length);
            string loinc = loincCodes[obsIdx];
            string unit = units[obsIdx];
            double value = ranges[obsIdx][0] + rng.NextDouble() * (ranges[obsIdx][1] - ranges[obsIdx][0]);

            // status: always string "final" or "amended"
            string status = rng.NextDouble() < 0.9 ? "final" : "amended";

            // subject_id: always string reference
            string subjectId = $"Patient/{1000 + rng.Next(500)}";

            // timestamp: always string ISO-8601
            string timestamp = $"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}T{rng.Next(24):D2}:00:00+00:00";

            // reliability: always boolean (true=verified, false=unverified)
            bool reliable = rng.NextDouble() > 0.05;

            // note_count: always integer (number of associated notes)
            int noteCount = rng.NextDouble() < 0.7 ? 0 : rng.Next(1, 5);

            // mixed_field: sometimes string, sometimes number (data quality issue)
            string mixedField = rng.NextDouble() < 0.75 ? $"\"obs_{i:D6}\"" : $"{i}";

            sb.AppendLine($"{{\"resource_id\":\"Observation/{i:D6}\"," +
                         $"\"loinc_code\":\"{loinc}\"," +
                         $"\"value_quantity\":{value:F2}," +
                         $"\"unit\":\"{unit}\"," +
                         $"\"status\":\"{status}\"," +
                         $"\"subject_ref\":\"{subjectId}\"," +
                         $"\"effective_datetime\":\"{timestamp}\"," +
                         $"\"verified\":{reliable.ToString().ToLower()}," +
                         $"\"note_count\":{noteCount}," +
                         $"\"mixed_ref\":{mixedField}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldDataType — validate schema types
        var dtValue = doc.GetFieldDataType("value_quantity");
        Assert.Equal("number", dtValue);
        Assert.Equal(dtValue, doc.GetFieldDataType("value_quantity")); // consistent

        var dtStatus = doc.GetFieldDataType("status");
        Assert.Equal("string", dtStatus);

        var dtLoinc = doc.GetFieldDataType("loinc_code");
        Assert.Equal("string", dtLoinc);

        var dtVerified = doc.GetFieldDataType("verified");
        Assert.Equal("boolean", dtVerified);

        var dtNoteCount = doc.GetFieldDataType("note_count");
        Assert.Equal("number", dtNoteCount);

        // Mixed field: mostly string but some numbers — should be "string" (dominant) or "mixed"
        var dtMixed = doc.GetFieldDataType("mixed_ref");
        Assert.NotNull(dtMixed);
        Assert.NotEmpty(dtMixed);

        // GetFieldTypeConsistency
        var tcValue = doc.GetFieldTypeConsistency("value_quantity");
        Assert.Equal(1.0, tcValue, precision: 6); // always numeric
        Assert.Equal(tcValue, doc.GetFieldTypeConsistency("value_quantity")); // consistent

        var tcStatus = doc.GetFieldTypeConsistency("status");
        Assert.Equal(1.0, tcStatus, precision: 6); // always string

        var tcVerified = doc.GetFieldTypeConsistency("verified");
        Assert.Equal(1.0, tcVerified, precision: 6); // always boolean

        var tcMixed = doc.GetFieldTypeConsistency("mixed_ref");
        Assert.True(tcMixed >= 0.0 && tcMixed <= 1.0); // mixed — should be < 1.0 for dominant type
        Assert.True(tcMixed < 1.0); // not fully consistent (has both strings and numbers)

        // SaveToFile
        var outPath = TempFile("fhir_obs_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(200, loaded.RecordCount);
        Assert.Equal(dtValue, loaded.GetFieldDataType("value_quantity"));
        Assert.Equal(dtStatus, loaded.GetFieldDataType("status"));
        Assert.Equal(dtVerified, loaded.GetFieldDataType("verified"));
        Assert.Equal(tcValue, loaded.GetFieldTypeConsistency("value_quantity"), precision: 8);
        Assert.Equal(tcStatus, loaded.GetFieldTypeConsistency("status"), precision: 8);

        // Additional no-throw
        var ex1 = Record.Exception(() => loaded.GetFieldDataType("subject_ref"));
        var ex2 = Record.Exception(() => loaded.GetFieldTypeConsistency("note_count"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Equal("string", loaded.GetFieldDataType("subject_ref"));
        Assert.Equal(1.0, loaded.GetFieldTypeConsistency("note_count"), precision: 6);
    }
}
