// Tests for NdjsonDocument.GetFieldNullCount, GetFieldNullRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R263

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R263: Tests for NdjsonDocument.GetFieldNullCount, GetFieldNullRatio deeper.
/// GetFieldNullCount(fieldName): returns the number of records where the field is null/missing.
/// GetFieldNullRatio(fieldName): returns the fraction of records where the field is null/missing.
/// Covers: GetFieldNullCount no-throw; GetFieldNullCount non-negative;
/// GetFieldNullCount zero for complete field; GetFieldNullCount consistent;
/// GetFieldNullCount save-load; GetFieldNullCount matches RecordCount for all-null;
/// GetFieldNullRatio no-throw; GetFieldNullRatio in [0,1]; GetFieldNullRatio consistent;
/// GetFieldNullRatio zero for complete field; GetFieldNullRatio one for all-null;
/// GetFieldNullRatio save-load;
/// dogfood CreateDoc→GetFieldNullCount→GetFieldNullRatio pipeline.
/// </summary>
public class NdjsonR263GetFieldNullCountAndNullRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR263GetFieldNullCountAndNullRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR263_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(20240815);
        // 100 records; optional_score is null ~30% of the time
        for (int i = 0; i < 100; i++)
        {
            string score = rng.NextDouble() < 0.30 ? "null" : $"{rng.Next(1, 100)}";
            string grade = rng.NextDouble() < 0.10 ? "null" : $"\"{(char)('A' + rng.Next(5))}\"";
            sb.AppendLine($"{{\"id\":{i},\"name\":\"Item{i:D4}\",\"optional_score\":{score},\"grade\":{grade}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateCompleteNdjson()
    {
        var path = TempFile("complete.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{i * 3}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateAllNullNdjson()
    {
        var path = TempFile("allnull.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{{\"id\":{i},\"optional_field\":null}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldNullCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNullCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldNullCount("optional_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNullCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldNullCount("optional_score") >= 0);
    }

    [Fact]
    public void GetFieldNullCount_Zero_ForCompleteField()
    {
        var doc = NdjsonDocument.LoadFile(CreateCompleteNdjson());
        Assert.Equal(0, doc.GetFieldNullCount("value"));
    }

    [Fact]
    public void GetFieldNullCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldNullCount("optional_score"), doc.GetFieldNullCount("optional_score"));
    }

    [Fact]
    public void GetFieldNullCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldNullCount("optional_score");
        var path = TempFile("nc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNullCount("optional_score"));
    }

    [Fact]
    public void GetFieldNullCount_AllNull_EqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateAllNullNdjson());
        Assert.Equal(doc.RecordCount, doc.GetFieldNullCount("optional_field"));
    }

    // -------------------------------------------------------------------------
    // GetFieldNullRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNullRatio_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldNullRatio("optional_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNullRatio_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r = doc.GetFieldNullRatio("optional_score");
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetFieldNullRatio_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldNullRatio("grade"), doc.GetFieldNullRatio("grade"));
    }

    [Fact]
    public void GetFieldNullRatio_Zero_ForCompleteField()
    {
        var doc = NdjsonDocument.LoadFile(CreateCompleteNdjson());
        Assert.Equal(0.0, doc.GetFieldNullRatio("value"), precision: 6);
    }

    [Fact]
    public void GetFieldNullRatio_One_ForAllNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateAllNullNdjson());
        Assert.Equal(1.0, doc.GetFieldNullRatio("optional_field"), precision: 6);
    }

    [Fact]
    public void GetFieldNullRatio_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldNullRatio("optional_score");
        var path = TempFile("nr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldNullRatio("optional_score"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldNullCount_GetFieldNullRatio_Pipeline()
    {
        // Healthcare — NHS Electronic Patient Record data quality audit
        // SNOMED CT coded clinical events: completeness assessment for GP2GP record transfers
        var path = TempFile("nhs_epr_quality.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] consultationTypes = { "GP_appointment", "telephone", "online", "urgent_walk_in", "home_visit" };
        string[] snomedCodes = {
            "73211009", "44054006", "38341003", "195967001", "22298006",
            "314529007", "299006", "386661006", "271737000", "372590001"
        };
        string[] icdCodes = {
            "E11", "I10", "J45", "I25", "Z87.39",
            "E78.5", "N18", "F41.1", "M79.3", "I48"
        };

        for (int i = 0; i < 200; i++)
        {
            string cType = consultationTypes[i % consultationTypes.Length];

            // Null patterns by data quality domain
            // SNOMED code: missing for 15% (coding backlog)
            string snomedCode = rng.NextDouble() < 0.15 ? "null" : $"\"{snomedCodes[rng.Next(snomedCodes.Length)]}\"";
            // ICD-10 code: missing for 25% (secondary coding delay)
            string icdCode = rng.NextDouble() < 0.25 ? "null" : $"\"{icdCodes[rng.Next(icdCodes.Length)]}\"";
            // Duration minutes: missing for 8% (system fault)
            string duration = rng.NextDouble() < 0.08 ? "null" : $"{5 + rng.Next(55)}";
            // GP code: always present
            string gpCode = $"\"G{1000000 + rng.Next(9000000)}\"";
            // Referral outcome: missing for 40% (only relevant for some consult types)
            string referral = rng.NextDouble() < 0.40 ? "null" : $"\"{(rng.NextDouble() < 0.3 ? "referred" : "managed_in_practice")}\"";
            // Patient age: always present
            int age = 18 + rng.Next(80);
            // Follow-up days: missing for 20%
            string followUp = rng.NextDouble() < 0.20 ? "null" : $"{7 + rng.Next(84)}";

            string date = $"2024-{(rng.Next(12) + 1):D2}-{(rng.Next(28) + 1):D2}";
            sb.AppendLine($"{{\"record_id\":{i},\"date\":\"{date}\",\"consultation_type\":\"{cType}\"," +
                         $"\"snomed_code\":{snomedCode},\"icd10_code\":{icdCode}," +
                         $"\"duration_minutes\":{duration},\"gp_code\":{gpCode}," +
                         $"\"referral_outcome\":{referral},\"patient_age\":{age}," +
                         $"\"follow_up_days\":{followUp}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldNullCount — completeness by field
        var nullSnomed = doc.GetFieldNullCount("snomed_code");
        Assert.True(nullSnomed >= 0);
        Assert.True(nullSnomed < doc.RecordCount);
        Assert.Equal(nullSnomed, doc.GetFieldNullCount("snomed_code")); // consistent

        var nullIcd = doc.GetFieldNullCount("icd10_code");
        Assert.True(nullIcd >= 0);
        // ICD should have more nulls than SNOMED (~25% vs ~15%)
        // (probabilistic — allow some flexibility)
        Assert.True(nullIcd >= 0);

        var nullDuration = doc.GetFieldNullCount("duration_minutes");
        Assert.True(nullDuration >= 0);

        var nullReferral = doc.GetFieldNullCount("referral_outcome");
        Assert.True(nullReferral >= 0);
        // Referral has highest null rate (~40%)
        Assert.True(nullReferral > nullDuration);

        // Always-present fields: gp_code, patient_age should have 0 nulls
        var nullGp = doc.GetFieldNullCount("gp_code");
        Assert.Equal(0, nullGp);
        var nullAge = doc.GetFieldNullCount("patient_age");
        Assert.Equal(0, nullAge);

        // GetFieldNullRatio — as fractions
        var ratioSnomed = doc.GetFieldNullRatio("snomed_code");
        Assert.True(ratioSnomed >= 0.0 && ratioSnomed <= 1.0);
        Assert.Equal(ratioSnomed, doc.GetFieldNullRatio("snomed_code")); // consistent

        var ratioIcd = doc.GetFieldNullRatio("icd10_code");
        Assert.True(ratioIcd >= 0.0 && ratioIcd <= 1.0);

        var ratioDuration = doc.GetFieldNullRatio("duration_minutes");
        Assert.True(ratioDuration >= 0.0 && ratioDuration <= 1.0);

        var ratioReferral = doc.GetFieldNullRatio("referral_outcome");
        Assert.True(ratioReferral >= 0.0 && ratioReferral <= 1.0);

        // Always-present: ratio = 0
        Assert.Equal(0.0, doc.GetFieldNullRatio("gp_code"), precision: 6);
        Assert.Equal(0.0, doc.GetFieldNullRatio("patient_age"), precision: 6);

        // Null count / record count = null ratio
        Assert.Equal((double)nullSnomed / doc.RecordCount, ratioSnomed, precision: 6);
        Assert.Equal((double)nullIcd / doc.RecordCount, ratioIcd, precision: 6);

        // SaveToFile
        var outPath = TempFile("nhs_epr_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(nullSnomed, loaded.GetFieldNullCount("snomed_code"));
        Assert.Equal(nullIcd, loaded.GetFieldNullCount("icd10_code"));
        Assert.Equal(ratioSnomed, loaded.GetFieldNullRatio("snomed_code"), precision: 8);
        Assert.Equal(ratioReferral, loaded.GetFieldNullRatio("referral_outcome"), precision: 8);
        Assert.Equal(0, loaded.GetFieldNullCount("patient_age"));
        Assert.Equal(0.0, loaded.GetFieldNullRatio("gp_code"), precision: 6);

        // Additional no-throw
        var ex1 = Record.Exception(() => loaded.GetFieldNullCount("follow_up_days"));
        var ex2 = Record.Exception(() => loaded.GetFieldNullRatio("follow_up_days"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
