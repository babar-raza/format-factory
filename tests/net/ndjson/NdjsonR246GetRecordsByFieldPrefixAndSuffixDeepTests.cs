// Tests for NdjsonDocument.GetRecordsByFieldPrefix, GetRecordsByFieldSuffix, GetFieldValueLength deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R246

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R246: Tests for NdjsonDocument.GetRecordsByFieldPrefix, GetRecordsByFieldSuffix, GetFieldValueLength deeper.
/// GetRecordsByFieldPrefix(field, prefix): returns records where the field value starts with the given prefix.
/// GetRecordsByFieldSuffix(field, suffix): returns records where the field value ends with the given suffix.
/// GetFieldValueLength(field, index): returns the string length of the field value in the record at the given index.
/// Covers: GetRecordsByFieldPrefix no-throw; GetRecordsByFieldPrefix count leq RecordCount;
/// GetRecordsByFieldPrefix empty for non-matching prefix; GetRecordsByFieldPrefix all for common prefix;
/// GetRecordsByFieldSuffix no-throw; GetRecordsByFieldSuffix count leq RecordCount;
/// GetRecordsByFieldSuffix empty for non-matching suffix; GetRecordsByFieldSuffix consistent;
/// GetFieldValueLength no-throw; GetFieldValueLength non-negative; GetFieldValueLength consistent;
/// GetFieldValueLength save-load;
/// dogfood GetRecordsByFieldPrefix→GetRecordsByFieldSuffix→GetFieldValueLength→SaveToFile pipeline.
/// </summary>
public class NdjsonR246GetRecordsByFieldPrefixAndSuffixDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR246GetRecordsByFieldPrefixAndSuffixDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR246_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateDrugTrialNdjson()
    {
        var path = TempFile("drug_trial.ndjson");
        var records = new[]
        {
            "{\"trial_id\":\"NCT001\",\"drug\":\"Semaglutide\",\"phase\":\"Phase3\",\"sponsor\":\"NovoNordisk\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT002\",\"drug\":\"Tirzepatide\",\"phase\":\"Phase3\",\"sponsor\":\"EliLilly\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT003\",\"drug\":\"SemaglutideOral\",\"phase\":\"Phase2\",\"sponsor\":\"NovoNordisk\",\"status\":\"Active\"}",
            "{\"trial_id\":\"NCT004\",\"drug\":\"Liraglutide\",\"phase\":\"Phase4\",\"sponsor\":\"NovoNordisk\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT005\",\"drug\":\"Dulaglutide\",\"phase\":\"Phase3\",\"sponsor\":\"EliLilly\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT006\",\"drug\":\"Canagliflozin\",\"phase\":\"Phase3\",\"sponsor\":\"J&J\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT007\",\"drug\":\"Empagliflozin\",\"phase\":\"Phase3\",\"sponsor\":\"Boehringer\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT008\",\"drug\":\"Dapagliflozin\",\"phase\":\"Phase3\",\"sponsor\":\"AstraZeneca\",\"status\":\"Active\"}",
            "{\"trial_id\":\"NCT009\",\"drug\":\"Semaglutide\",\"phase\":\"Phase3b\",\"sponsor\":\"NovoNordisk\",\"status\":\"Active\"}",
            "{\"trial_id\":\"NCT010\",\"drug\":\"Metformin\",\"phase\":\"Phase4\",\"sponsor\":\"Generic\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT011\",\"drug\":\"Insulin Glargine\",\"phase\":\"Phase4\",\"sponsor\":\"Sanofi\",\"status\":\"Completed\"}",
            "{\"trial_id\":\"NCT012\",\"drug\":\"TirZepatideXR\",\"phase\":\"Phase2\",\"sponsor\":\"EliLilly\",\"status\":\"Recruiting\"}",
        };
        File.WriteAllLines(path, records);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordsByFieldPrefix
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByFieldPrefix_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByFieldPrefix("drug", "Sema"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByFieldPrefix_Count_LeqRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var results = doc.GetRecordsByFieldPrefix("drug", "Sema");
        Assert.True(results.Count <= doc.RecordCount);
    }

    [Fact]
    public void GetRecordsByFieldPrefix_Empty_ForNonMatchingPrefix()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var results = doc.GetRecordsByFieldPrefix("drug", "XXXXXXXXXXX");
        Assert.Empty(results);
    }

    [Fact]
    public void GetRecordsByFieldPrefix_All_ForCommonPrefix()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        // All trial_ids start with "NCT"
        var results = doc.GetRecordsByFieldPrefix("trial_id", "NCT");
        Assert.Equal(doc.RecordCount, results.Count);
    }

    [Fact]
    public void GetRecordsByFieldPrefix_CorrectCount_ForKnownPrefix()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        // "Sema" prefix: Semaglutide (NCT001), SemaglutideOral (NCT003), Semaglutide (NCT009) = 3
        var results = doc.GetRecordsByFieldPrefix("drug", "Sema");
        Assert.Equal(3, results.Count);
    }

    // -------------------------------------------------------------------------
    // GetRecordsByFieldSuffix
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByFieldSuffix_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByFieldSuffix("status", "ed"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByFieldSuffix_Count_LeqRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var results = doc.GetRecordsByFieldSuffix("status", "ed");
        Assert.True(results.Count <= doc.RecordCount);
    }

    [Fact]
    public void GetRecordsByFieldSuffix_Empty_ForNonMatchingSuffix()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var results = doc.GetRecordsByFieldSuffix("drug", "ZZZZZZ");
        Assert.Empty(results);
    }

    [Fact]
    public void GetRecordsByFieldSuffix_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var r1 = doc.GetRecordsByFieldSuffix("phase", "3");
        var r2 = doc.GetRecordsByFieldSuffix("phase", "3");
        Assert.Equal(r1.Count, r2.Count);
    }

    [Fact]
    public void GetRecordsByFieldSuffix_CorrectCount_ForKnownSuffix()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        // Sponsor ending with "Lilly": EliLilly (NCT002, NCT005, NCT012) = 3
        var results = doc.GetRecordsByFieldSuffix("sponsor", "Lilly");
        Assert.Equal(3, results.Count);
    }

    // -------------------------------------------------------------------------
    // GetFieldValueLength
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueLength_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueLength("drug", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueLength_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        Assert.True(doc.GetFieldValueLength("drug", 0) >= 0);
    }

    [Fact]
    public void GetFieldValueLength_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        Assert.Equal(doc.GetFieldValueLength("status", 0), doc.GetFieldValueLength("status", 0));
    }

    [Fact]
    public void GetFieldValueLength_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateDrugTrialNdjson());
        var before = doc.GetFieldValueLength("drug", 0);
        var path = TempFile("fvl_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldValueLength("drug", 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordsByFieldPrefix_GetRecordsByFieldSuffix_GetFieldValueLength_SaveToFile_Pipeline()
    {
        // Pharmacovigilance — adverse event signal detection database (EMA/FDA MedDRA coded)
        var path = TempFile("adverse_events.ndjson");
        var records = new[]
        {
            "{\"ae_id\":\"AE00001\",\"drug_name\":\"Semaglutide 2.4mg\",\"meddra_pt\":\"Nausea\",\"meddra_soc\":\"GI disorders\",\"severity\":\"Mild\",\"outcome\":\"Resolved\",\"country\":\"United Kingdom\"}",
            "{\"ae_id\":\"AE00002\",\"drug_name\":\"Semaglutide 2.4mg\",\"meddra_pt\":\"Vomiting\",\"meddra_soc\":\"GI disorders\",\"severity\":\"Moderate\",\"outcome\":\"Resolved\",\"country\":\"Germany\"}",
            "{\"ae_id\":\"AE00003\",\"drug_name\":\"Tirzepatide 15mg\",\"meddra_pt\":\"Pancreatitis\",\"meddra_soc\":\"GI disorders\",\"severity\":\"Severe\",\"outcome\":\"Hospitalised\",\"country\":\"United States\"}",
            "{\"ae_id\":\"AE00004\",\"drug_name\":\"Semaglutide 2.4mg\",\"meddra_pt\":\"Injection site reaction\",\"meddra_soc\":\"Skin disorders\",\"severity\":\"Mild\",\"outcome\":\"Resolved\",\"country\":\"France\"}",
            "{\"ae_id\":\"AE00005\",\"drug_name\":\"Empagliflozin 25mg\",\"meddra_pt\":\"UTI\",\"meddra_soc\":\"Renal disorders\",\"severity\":\"Moderate\",\"outcome\":\"Resolved\",\"country\":\"United States\"}",
            "{\"ae_id\":\"AE00006\",\"drug_name\":\"Empagliflozin 25mg\",\"meddra_pt\":\"DKA\",\"meddra_soc\":\"Metabolic disorders\",\"severity\":\"Life-threatening\",\"outcome\":\"Hospitalised\",\"country\":\"United Kingdom\"}",
            "{\"ae_id\":\"AE00007\",\"drug_name\":\"Semaglutide 1.0mg\",\"meddra_pt\":\"Thyroid neoplasm\",\"meddra_soc\":\"Neoplasms\",\"severity\":\"Severe\",\"outcome\":\"Under investigation\",\"country\":\"Denmark\"}",
            "{\"ae_id\":\"AE00008\",\"drug_name\":\"Tirzepatide 5mg\",\"meddra_pt\":\"Nausea\",\"meddra_soc\":\"GI disorders\",\"severity\":\"Mild\",\"outcome\":\"Resolved\",\"country\":\"Japan\"}",
            "{\"ae_id\":\"AE00009\",\"drug_name\":\"Semaglutide 0.5mg\",\"meddra_pt\":\"Retinopathy\",\"meddra_soc\":\"Eye disorders\",\"severity\":\"Moderate\",\"outcome\":\"Ongoing\",\"country\":\"United States\"}",
            "{\"ae_id\":\"AE00010\",\"drug_name\":\"Empagliflozin 10mg\",\"meddra_pt\":\"Amputation\",\"meddra_soc\":\"Vascular disorders\",\"severity\":\"Severe\",\"outcome\":\"Permanent sequela\",\"country\":\"Brazil\"}",
            "{\"ae_id\":\"AE00011\",\"drug_name\":\"Tirzepatide 10mg\",\"meddra_pt\":\"Gastroparesis\",\"meddra_soc\":\"GI disorders\",\"severity\":\"Severe\",\"outcome\":\"Ongoing\",\"country\":\"United Kingdom\"}",
            "{\"ae_id\":\"AE00012\",\"drug_name\":\"Semaglutide 2.4mg\",\"meddra_pt\":\"Suicidal ideation\",\"meddra_soc\":\"Psychiatric disorders\",\"severity\":\"Severe\",\"outcome\":\"Under investigation\",\"country\":\"Sweden\"}",
        };
        File.WriteAllLines(path, records);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetRecordsByFieldPrefix — Semaglutide drugs
        var semaRecords = doc.GetRecordsByFieldPrefix("drug_name", "Semaglutide");
        Assert.True(semaRecords.Count > 0);
        Assert.True(semaRecords.Count <= doc.RecordCount);
        // NCT001/003/004/007/009/012 = 6 semaglutide records
        Assert.Equal(6, semaRecords.Count);

        // GetRecordsByFieldPrefix — all AE IDs start with "AE"
        var allAeIds = doc.GetRecordsByFieldPrefix("ae_id", "AE");
        Assert.Equal(doc.RecordCount, allAeIds.Count);

        // GetRecordsByFieldPrefix — non-matching
        var noMatch = doc.GetRecordsByFieldPrefix("drug_name", "Insulin");
        Assert.Empty(noMatch);

        // GetRecordsByFieldSuffix — UK country reports
        var ukRecords = doc.GetRecordsByFieldSuffix("country", "Kingdom");
        Assert.True(ukRecords.Count > 0);
        // AE00001 (UK), AE00006 (UK), AE00011 (UK) = 3
        Assert.Equal(3, ukRecords.Count);

        // GetRecordsByFieldSuffix — Resolved outcomes
        var resolved = doc.GetRecordsByFieldSuffix("outcome", "Resolved");
        Assert.True(resolved.Count > 0);

        // GetRecordsByFieldSuffix — non-matching
        var noSuffix = doc.GetRecordsByFieldSuffix("meddra_soc", "ZZZZZ");
        Assert.Empty(noSuffix);

        // GetFieldValueLength
        var drugLen0 = doc.GetFieldValueLength("drug_name", 0);
        Assert.True(drugLen0 > 0); // "Semaglutide 2.4mg" length
        Assert.Equal(drugLen0, doc.GetFieldValueLength("drug_name", 0)); // consistent

        var outcomeLen2 = doc.GetFieldValueLength("outcome", 2);
        Assert.True(outcomeLen2 > 0); // "Hospitalised"

        // SaveToFile
        var outPath = TempFile("adverse_events_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(12, loaded.RecordCount);
        Assert.Equal(6, loaded.GetRecordsByFieldPrefix("drug_name", "Semaglutide").Count);
        Assert.Equal(3, loaded.GetRecordsByFieldSuffix("country", "Kingdom").Count);
        Assert.Equal(drugLen0, loaded.GetFieldValueLength("drug_name", 0));

        // GetRecordsByFieldSuffix on loaded
        var empaRecords = loaded.GetRecordsByFieldSuffix("drug_name", "25mg");
        Assert.True(empaRecords.Count > 0); // Empagliflozin 25mg records

        var ex1 = Record.Exception(() => loaded.GetRecordsByFieldPrefix("severity", "Severe"));
        var ex2 = Record.Exception(() => loaded.GetRecordsByFieldSuffix("meddra_soc", "disorders"));
        var ex3 = Record.Exception(() => loaded.GetFieldValueLength("meddra_pt", 5));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
