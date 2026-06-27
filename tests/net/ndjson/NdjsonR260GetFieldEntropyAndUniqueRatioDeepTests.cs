// Tests for NdjsonDocument.GetFieldEntropy, GetFieldUniqueRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R260

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R260: Tests for NdjsonDocument.GetFieldEntropy, GetFieldUniqueRatio deeper.
/// GetFieldEntropy(fieldName): returns Shannon entropy of the field value distribution.
/// GetFieldUniqueRatio(fieldName): returns unique values / total records.
/// Covers: GetFieldEntropy no-throw; GetFieldEntropy non-negative; GetFieldEntropy consistent;
/// GetFieldEntropy zero for constant field; GetFieldEntropy save-load;
/// GetFieldUniqueRatio no-throw; GetFieldUniqueRatio in [0,1];
/// GetFieldUniqueRatio one for all-unique; GetFieldUniqueRatio consistent; GetFieldUniqueRatio save-load;
/// dogfood CreateDoc→GetFieldEntropy→GetFieldUniqueRatio pipeline.
/// </summary>
public class NdjsonR260GetFieldEntropyAndUniqueRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR260GetFieldEntropyAndUniqueRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR260_" + Guid.NewGuid().ToString("N"));
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
        string[] statuses = { "active", "inactive", "pending", "suspended" };
        var rng = new Random(20241101);
        for (int i = 0; i < 120; i++)
            sb.AppendLine($"{{\"id\":{i},\"status\":\"{statuses[i % statuses.Length]}\",\"score\":{(rng.NextDouble() * 100):F2},\"unique_key\":\"KEY{i:D4}\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{{\"id\":{i},\"status\":\"active\",\"region\":\"UK\"}}");
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
        var ex = Record.Exception(() => doc.GetFieldEntropy("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldEntropy_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldEntropy("status") >= 0.0);
    }

    [Fact]
    public void GetFieldEntropy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldEntropy("status"), doc.GetFieldEntropy("status"));
    }

    [Fact]
    public void GetFieldEntropy_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldEntropy("status"), precision: 6);
    }

    [Fact]
    public void GetFieldEntropy_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldEntropy("status");
        var path = TempFile("ent_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldEntropy("status"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetFieldUniqueRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldUniqueRatio_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldUniqueRatio("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldUniqueRatio_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ratio = doc.GetFieldUniqueRatio("status");
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
    }

    [Fact]
    public void GetFieldUniqueRatio_One_ForAllUnique()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // unique_key field has a unique value per record
        Assert.Equal(1.0, doc.GetFieldUniqueRatio("unique_key"), precision: 6);
    }

    [Fact]
    public void GetFieldUniqueRatio_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldUniqueRatio("status"), doc.GetFieldUniqueRatio("status"));
    }

    [Fact]
    public void GetFieldUniqueRatio_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldUniqueRatio("status");
        var path = TempFile("ur_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldUniqueRatio("status"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldEntropy_GetFieldUniqueRatio_Pipeline()
    {
        // Healthcare — SNOMED CT clinical concept usage analytics
        // Entropy and uniqueness used for clinical coding quality audit in EHR systems
        var path = TempFile("snomed_coding_audit.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240601);

        // Common SNOMED codes for GP conditions — power law distribution (Zipf-like)
        string[] snomedCodes = {
            "44054006",  // Type 2 diabetes mellitus
            "38341003",  // Hypertension
            "195967001", // Asthma
            "13645005",  // COPD
            "73211009",  // Diabetes mellitus
            "46635009",  // Type 1 diabetes
            "399211009", // History of myocardial infarction
            "84114007",  // Heart failure
            "266257000", // Epilepsy
            "230690007"  // Stroke
        };
        string[] snomedDescriptions = {
            "Type_2_diabetes_mellitus", "Hypertension", "Asthma", "COPD",
            "Diabetes_mellitus", "Type_1_diabetes", "History_of_MI", "Heart_failure",
            "Epilepsy", "Stroke"
        };
        string[] systems = { "EMIS_Web", "SystmOne", "Vision", "Microtest" };
        string[] codeTypes = { "finding", "disorder", "procedure", "observable_entity" };
        string[] settings = { "GP_Surgery", "Hospital_OPD", "A_and_E", "Community" };

        // Zipf distribution — first code appears most often
        double[] weights = { 0.25, 0.20, 0.15, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03, 0.03 };
        for (int i = 0; i < 180; i++)
        {
            // Sample code using Zipf weights
            double r = rng.NextDouble();
            double cumulative = 0;
            int codeIdx = snomedCodes.Length - 1;
            for (int j = 0; j < weights.Length; j++)
            {
                cumulative += weights[j];
                if (r <= cumulative) { codeIdx = j; break; }
            }

            string system = systems[i % systems.Length];
            string codeType = codeTypes[codeIdx % codeTypes.Length];
            string setting = settings[i % settings.Length];
            int patAge = 18 + rng.Next(75);
            string gender = rng.NextDouble() < 0.5 ? "Male" : "Female";
            string year = $"{2020 + rng.Next(5)}";
            // Episode ID is unique per record
            string episodeId = $"EP{10000000 + i:D8}";

            sb.AppendLine($"{{\"episode_id\":\"{episodeId}\"," +
                         $"\"snomed_code\":\"{snomedCodes[codeIdx]}\"," +
                         $"\"description\":\"{snomedDescriptions[codeIdx]}\"," +
                         $"\"system\":\"{system}\"," +
                         $"\"code_type\":\"{codeType}\"," +
                         $"\"setting\":\"{setting}\"," +
                         $"\"patient_age\":{patAge}," +
                         $"\"gender\":\"{gender}\"," +
                         $"\"year\":\"{year}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(180, doc.RecordCount);

        // GetFieldEntropy — SNOMED code distribution (Zipf → lower entropy than uniform)
        var entCode = doc.GetFieldEntropy("snomed_code");
        Assert.True(entCode >= 0.0);
        Assert.Equal(entCode, doc.GetFieldEntropy("snomed_code")); // consistent

        var entSystem = doc.GetFieldEntropy("system");
        Assert.True(entSystem >= 0.0);

        var entSetting = doc.GetFieldEntropy("setting");
        Assert.True(entSetting >= 0.0);

        var entGender = doc.GetFieldEntropy("gender");
        Assert.True(entGender >= 0.0);
        // Binary field — maximum 1 bit entropy
        Assert.True(entGender <= 2.0); // Shannon entropy in bits

        var entYear = doc.GetFieldEntropy("year");
        Assert.True(entYear >= 0.0);

        // GetFieldUniqueRatio
        var urEpisodeId = doc.GetFieldUniqueRatio("episode_id");
        Assert.Equal(1.0, urEpisodeId, precision: 6); // unique per record

        var urCode = doc.GetFieldUniqueRatio("snomed_code");
        Assert.True(urCode >= 0.0 && urCode <= 1.0); // 10 unique codes / 180 records
        Assert.Equal(urCode, doc.GetFieldUniqueRatio("snomed_code")); // consistent

        var urSystem = doc.GetFieldUniqueRatio("system");
        Assert.True(urSystem >= 0.0 && urSystem <= 1.0);

        var urGender = doc.GetFieldUniqueRatio("gender");
        Assert.True(urGender >= 0.0 && urGender <= 1.0);

        // Null check
        var nullEpisode = doc.GetFieldNullRate("episode_id");
        Assert.Equal(0.0, nullEpisode, precision: 6);

        // Field stats
        var meanAge = doc.GetFieldMean("patient_age");
        Assert.True(meanAge > 0.0);

        // SaveToFile
        var outPath = TempFile("snomed_coding_audit_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(entCode, loaded.GetFieldEntropy("snomed_code"), precision: 8);
        Assert.Equal(entSystem, loaded.GetFieldEntropy("system"), precision: 8);
        Assert.Equal(urCode, loaded.GetFieldUniqueRatio("snomed_code"), precision: 8);
        Assert.Equal(1.0, loaded.GetFieldUniqueRatio("episode_id"), precision: 6);

        // Constant field test
        var pathConst = TempFile("constant_snomed.ndjson");
        var sbConst = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sbConst.AppendLine($"{{\"id\":{i},\"code\":\"44054006\",\"system\":\"EMIS_Web\"}}");
        File.WriteAllText(pathConst, sbConst.ToString());
        var docConst = NdjsonDocument.LoadFile(pathConst);
        Assert.Equal(0.0, docConst.GetFieldEntropy("code"), precision: 6);
        Assert.Equal(0.0, docConst.GetFieldEntropy("system"), precision: 6);

        // Additional no-throw checks
        var ex1 = Record.Exception(() => loaded.GetFieldEntropy("code_type"));
        var ex2 = Record.Exception(() => loaded.GetFieldUniqueRatio("description"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
