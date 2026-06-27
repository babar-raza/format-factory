// Tests for NdjsonDocument.GetFieldMissingRate, GetFieldFillRate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R275

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R275: Tests for NdjsonDocument.GetFieldMissingRate, GetFieldFillRate deeper.
/// GetFieldMissingRate(field): returns the fraction of records where the field is null or absent; [0,1].
/// GetFieldFillRate(field): returns the fraction of records where the field has a non-null value; [0,1].
/// Covers: GetFieldMissingRate no-throw; GetFieldMissingRate in-range; GetFieldMissingRate zero for fully-populated;
/// GetFieldMissingRate one for fully-absent; GetFieldMissingRate consistent; GetFieldMissingRate save-load;
/// GetFieldFillRate no-throw; GetFieldFillRate in-range; GetFieldFillRate one for fully-populated;
/// GetFieldFillRate zero for fully-absent; MissingRate + FillRate = 1;
/// GetFieldFillRate consistent; GetFieldFillRate save-load; dogfood pipeline.
/// </summary>
public class NdjsonR275GetFieldMissingRateAndFillRateDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR275GetFieldMissingRateAndFillRateDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR275_" + Guid.NewGuid().ToString("N"));
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
        // 10 records: 'name' always present; 'email' present in 7; 'phone' present in 3
        for (int i = 0; i < 10; i++)
        {
            string email = i < 7 ? $",\"email\":\"user{i}@example.com\"" : ",\"email\":null";
            string phone = i < 3 ? $",\"phone\":\"+44700000000{i}\"" : "";
            lines.AppendLine($"{{\"id\":{i},\"name\":\"User{i}\"{email}{phone}}}");
        }
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateFullyPopulatedNdjson()
    {
        var path = TempFile("full.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":\"v{i}\"}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateFullyAbsentNdjson()
    {
        var path = TempFile("absent.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 15; i++)
            lines.AppendLine($"{{\"id\":{i}}}"); // no 'score' field at all
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMissingRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMissingRate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMissingRate("email"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMissingRate_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r = doc.GetFieldMissingRate("email");
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetFieldMissingRate_Zero_ForFullyPopulated()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyPopulatedNdjson());
        Assert.Equal(0.0, doc.GetFieldMissingRate("value"), precision: 6);
    }

    [Fact]
    public void GetFieldMissingRate_One_ForFullyAbsent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyAbsentNdjson());
        Assert.Equal(1.0, doc.GetFieldMissingRate("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMissingRate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMissingRate("email"), doc.GetFieldMissingRate("email"));
    }

    [Fact]
    public void GetFieldMissingRate_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMissingRate("email");
        var path = TempFile("mr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMissingRate("email"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldFillRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldFillRate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldFillRate("email"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldFillRate_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r = doc.GetFieldFillRate("email");
        Assert.True(r >= 0.0 && r <= 1.0);
    }

    [Fact]
    public void GetFieldFillRate_One_ForFullyPopulated()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyPopulatedNdjson());
        Assert.Equal(1.0, doc.GetFieldFillRate("value"), precision: 6);
    }

    [Fact]
    public void GetFieldFillRate_Zero_ForFullyAbsent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyAbsentNdjson());
        Assert.Equal(0.0, doc.GetFieldFillRate("score"), precision: 6);
    }

    [Fact]
    public void GetFieldFillRate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldFillRate("email"), doc.GetFieldFillRate("email"));
    }

    [Fact]
    public void GetFieldFillRate_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldFillRate("email");
        var path = TempFile("fr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldFillRate("email"), precision: 6);
    }

    [Fact]
    public void MissingRate_Plus_FillRate_Equals_One()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var mr = doc.GetFieldMissingRate("email");
        var fr = doc.GetFieldFillRate("email");
        Assert.Equal(1.0, mr + fr, precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMissingRate_GetFieldFillRate_Pipeline()
    {
        // Public Health — ONS/NHS: COVID-19 Vaccination Programme Records (Anonymised)
        // Individual vaccination event records — testing data completeness for eligibility,
        // dose, and adverse event fields across early (2021) and later (2022) rollout phases

        var path = TempFile("nhs_vacc_records.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20211201);

        string[] sites = { "RGT01", "RJC01", "RJE01", "RKB01", "RRV01", "RRK01",
                            "RXQ01", "RYJ01", "REN01", "RYR01" };
        string[] vaccines = { "Comirnaty", "Spikevax", "Vaxzevria", "Nuvaxovid" };
        string[] ageGroups = { "18-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+" };
        string[] doses = { "Dose_1", "Dose_2", "Booster_1", "Booster_2" };

        for (int i = 0; i < 400; i++)
        {
            string site = sites[rng.Next(sites.Length)];
            string vaccine = vaccines[rng.Next(vaccines.Length)];
            string ageGrp = ageGroups[rng.Next(ageGroups.Length)];
            string dose = doses[rng.Next(doses.Length)];
            // batch_number: 80% complete (early records missing)
            string batchNum = rng.NextDouble() < 0.80 ? $"\"batch_number\":\"{vaccine.Substring(0,3)}{rng.Next(100000, 999999)}\"" : "\"batch_number\":null";
            // adverse_event: only 5% of records (most have no adverse event)
            string adverse = rng.NextDouble() < 0.05 ? $"\"adverse_event\":\"Mild_arm_soreness\"" : "\"adverse_event\":null";
            // eligibility_ref: 60% complete (system captured from 2021-Q2 onwards)
            string eligRef = rng.NextDouble() < 0.60 ? $"\"eligibility_ref\":\"EL{rng.Next(10000,99999)}\"" : "\"eligibility_ref\":null";

            sb.AppendLine($"{{\"record_id\":\"VAC{i:D6}\",\"site_code\":\"{site}\",\"vaccine\":\"{vaccine}\"," +
                          $"\"age_group\":\"{ageGrp}\",\"dose_number\":\"{dose}\"," +
                          $"{batchNum},{adverse},{eligRef}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(400, doc.RecordCount);

        // Fully-populated mandatory fields
        var mrSite = doc.GetFieldMissingRate("site_code");
        Assert.Equal(0.0, mrSite, precision: 6);
        var frSite = doc.GetFieldFillRate("site_code");
        Assert.Equal(1.0, frSite, precision: 6);
        Assert.Equal(1.0, mrSite + frSite, precision: 6);

        var mrVaccine = doc.GetFieldMissingRate("vaccine");
        Assert.Equal(0.0, mrVaccine, precision: 6);
        var frVaccine = doc.GetFieldFillRate("vaccine");
        Assert.Equal(1.0, frVaccine, precision: 6);

        // batch_number: ~80% complete → missing rate ~20%
        var mrBatch = doc.GetFieldMissingRate("batch_number");
        var frBatch = doc.GetFieldFillRate("batch_number");
        Assert.True(mrBatch >= 0.0 && mrBatch <= 1.0);
        Assert.True(frBatch >= 0.0 && frBatch <= 1.0);
        Assert.Equal(1.0, mrBatch + frBatch, precision: 6);
        Assert.True(frBatch > 0.5); // majority filled

        // adverse_event: ~95% null → missing rate ~95%
        var mrAdverse = doc.GetFieldMissingRate("adverse_event");
        var frAdverse = doc.GetFieldFillRate("adverse_event");
        Assert.True(mrAdverse >= 0.0 && mrAdverse <= 1.0);
        Assert.Equal(1.0, mrAdverse + frAdverse, precision: 6);
        Assert.True(mrAdverse > frAdverse); // missing > filled for rare event

        // eligibility_ref: ~60% complete → missing rate ~40%
        var mrElig = doc.GetFieldMissingRate("eligibility_ref");
        var frElig = doc.GetFieldFillRate("eligibility_ref");
        Assert.True(mrElig >= 0.0 && mrElig <= 1.0);
        Assert.Equal(1.0, mrElig + frElig, precision: 6);
        Assert.True(frElig > mrElig); // more filled than missing

        // Consistency
        Assert.Equal(mrBatch, doc.GetFieldMissingRate("batch_number"));
        Assert.Equal(frElig, doc.GetFieldFillRate("eligibility_ref"));

        // Site with no adverse events should be fully missing for adverse_event field
        Assert.True(mrAdverse > 0.8); // ≥80% of records have null adverse_event

        // SaveToFile
        var outPath = TempFile("nhs_vacc_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(mrBatch, loaded.GetFieldMissingRate("batch_number"), precision: 6);
        Assert.Equal(frBatch, loaded.GetFieldFillRate("batch_number"), precision: 6);
        Assert.Equal(mrAdverse, loaded.GetFieldMissingRate("adverse_event"), precision: 6);
        Assert.Equal(frElig, loaded.GetFieldFillRate("eligibility_ref"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldMissingRate("site_code"));
        var ex2 = Record.Exception(() => loaded.GetFieldFillRate("adverse_event"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
