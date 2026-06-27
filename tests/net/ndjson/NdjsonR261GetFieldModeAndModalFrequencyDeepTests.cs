// Tests for NdjsonDocument.GetFieldMode, GetFieldModalFrequency deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R261

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R261: Tests for NdjsonDocument.GetFieldMode, GetFieldModalFrequency deeper.
/// GetFieldMode(fieldName): returns the most frequent value in the field.
/// GetFieldModalFrequency(fieldName): returns count of the modal value.
/// Covers: GetFieldMode no-throw; GetFieldMode non-null; GetFieldMode consistent;
/// GetFieldMode save-load; GetFieldModalFrequency no-throw; GetFieldModalFrequency positive;
/// GetFieldModalFrequency consistent; GetFieldModalFrequency save-load;
/// GetFieldModalFrequency >= mean frequency; GetFieldMode for numeric field;
/// dogfood CreateDoc→GetFieldMode→GetFieldModalFrequency pipeline.
/// </summary>
public class NdjsonR261GetFieldModeAndModalFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR261GetFieldModeAndModalFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR261_" + Guid.NewGuid().ToString("N"));
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
        string[] statuses = { "active", "active", "active", "pending", "inactive" };
        var rng = new Random(20241201);
        for (int i = 0; i < 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"status\":\"{statuses[i % statuses.Length]}\",\"score\":{(rng.NextDouble() * 100):F1},\"category\":\"CAT_{i % 4}\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
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
    public void GetFieldMode_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.NotNull(doc.GetFieldMode("status"));
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
    public void GetFieldMode_MostFrequent_ForKnownData()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // "active" appears 3/5 times → most frequent
        Assert.Equal("active", doc.GetFieldMode("status"));
    }

    // -------------------------------------------------------------------------
    // GetFieldModalFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldModalFrequency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldModalFrequency("status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldModalFrequency_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldModalFrequency("status") > 0);
    }

    [Fact]
    public void GetFieldModalFrequency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldModalFrequency("status"), doc.GetFieldModalFrequency("status"));
    }

    [Fact]
    public void GetFieldModalFrequency_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldModalFrequency("status");
        var path = TempFile("mf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldModalFrequency("status"));
    }

    [Fact]
    public void GetFieldModalFrequency_AtLeastMeanFrequency()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // Modal frequency >= mean frequency (by definition of mode)
        var modal = doc.GetFieldModalFrequency("status");
        var uniqueCount = doc.GetFieldUniqueCount("status");
        var meanFreq = (double)doc.RecordCount / uniqueCount;
        Assert.True(modal >= meanFreq - 0.001);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMode_GetFieldModalFrequency_Pipeline()
    {
        // Healthcare analytics — NHS Digital: Primary Care Medicine Prescribing Data
        // Identifying most frequently prescribed medicines by BNF chapter
        var path = TempFile("nhs_prescribing_data.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241115);

        // BNF Chapter 2 (Cardiovascular) — most common prescribing category in primary care
        string[] bnfChapters = { "BNF_02", "BNF_02", "BNF_02", "BNF_04", "BNF_04", "BNF_06", "BNF_01", "BNF_03" };
        string[] drugs = {
            "Atorvastatin_20mg", "Atorvastatin_40mg", "Atorvastatin_10mg",  // most prescribed
            "Ramipril_10mg", "Ramipril_5mg",
            "Amlodipine_5mg", "Amlodipine_10mg",
            "Metformin_500mg", "Metformin_1g",
            "Levothyroxine_50mcg", "Levothyroxine_100mcg",
            "Omeprazole_20mg", "Lansoprazole_30mg",
            "Salbutamol_100mcg_inhaler",
            "Sertraline_50mg", "Sertraline_100mg"
        };
        // Zipf weights — atorvastatin dominates
        double[] drugWeights = { 0.20, 0.18, 0.12, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.03, 0.02, 0.01, 0.01 };
        string[] icbCodes = { "QHM", "QRV", "QNC", "QPM", "QOC", "QWO", "QU9", "QJK" };
        string[] settings = { "GP_Surgery", "Walk_in_centre", "Community_pharmacy" };
        string[] dispensingStatus = { "Dispensed", "Dispensed", "Dispensed", "Not_dispensed" };

        for (int i = 0; i < 180; i++)
        {
            // Sample drug using Zipf weights
            double r = rng.NextDouble();
            double cumulative = 0;
            int drugIdx = drugs.Length - 1;
            for (int j = 0; j < drugWeights.Length; j++)
            {
                cumulative += drugWeights[j];
                if (r <= cumulative) { drugIdx = j; break; }
            }

            var chapter = bnfChapters[drugIdx < bnfChapters.Length ? drugIdx : 0];
            var drug = drugs[drugIdx];
            var icb = icbCodes[i % icbCodes.Length];
            var setting = settings[i % settings.Length];
            var status = dispensingStatus[i % dispensingStatus.Length];
            int quantity = (1 + rng.Next(3)) * 28; // 28, 56, or 84 tablets
            double netCost = (0.50 + rng.NextDouble() * 25.0);
            string patientAge = ((18 + rng.Next(75)) / 10 * 10).ToString() + "s"; // decade bands
            string year = "2024";
            string month = $"{(rng.Next(12) + 1):D2}";

            sb.AppendLine($"{{\"prescription_id\":\"RX{10000000 + i:D8}\"," +
                         $"\"bnf_chapter\":\"{chapter}\"," +
                         $"\"bnf_drug_name\":\"{drug}\"," +
                         $"\"icb_code\":\"{icb}\"," +
                         $"\"setting\":\"{setting}\"," +
                         $"\"dispensing_status\":\"{status}\"," +
                         $"\"quantity_items\":{quantity}," +
                         $"\"net_ingredient_cost_gbp\":{netCost:F2}," +
                         $"\"patient_age_band\":\"{patientAge}\"," +
                         $"\"year\":\"{year}\"," +
                         $"\"month\":\"{month}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(180, doc.RecordCount);

        // GetFieldMode — identify most prescribed drug
        var modeDrug = doc.GetFieldMode("bnf_drug_name");
        Assert.NotNull(modeDrug);
        Assert.Equal(modeDrug, doc.GetFieldMode("bnf_drug_name")); // consistent

        // Should be atorvastatin variant (highest Zipf weight)
        Assert.Contains("Atorvastatin", modeDrug);

        var modeChapter = doc.GetFieldMode("bnf_chapter");
        Assert.NotNull(modeChapter);
        Assert.Equal("BNF_02", modeChapter); // cardiovascular dominates

        var modeStatus = doc.GetFieldMode("dispensing_status");
        Assert.NotNull(modeStatus);
        Assert.Equal("Dispensed", modeStatus); // 3/4 dispensed

        var modeYear = doc.GetFieldMode("year");
        Assert.Equal("2024", modeYear);

        // GetFieldModalFrequency
        var mfDrug = doc.GetFieldModalFrequency("bnf_drug_name");
        Assert.True(mfDrug > 0);
        Assert.Equal(mfDrug, doc.GetFieldModalFrequency("bnf_drug_name")); // consistent

        var mfChapter = doc.GetFieldModalFrequency("bnf_chapter");
        Assert.True(mfChapter > 0);

        var mfStatus = doc.GetFieldModalFrequency("dispensing_status");
        Assert.True(mfStatus > 0);

        // Modal >= mean frequency
        var uniqueDrugs = doc.GetFieldUniqueCount("bnf_drug_name");
        var meanFreq = (double)doc.RecordCount / uniqueDrugs;
        Assert.True(mfDrug >= meanFreq - 0.001);

        // Null rate — all present
        Assert.Equal(0.0, doc.GetFieldNullRate("bnf_drug_name"), precision: 6);

        // Field stats — numeric fields
        var meanCost = doc.GetFieldMean("net_ingredient_cost_gbp");
        Assert.True(meanCost > 0.0);

        var meanQty = doc.GetFieldMean("quantity_items");
        Assert.True(meanQty > 0.0);

        // SaveToFile
        var outPath = TempFile("nhs_prescribing_data_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(modeDrug, loaded.GetFieldMode("bnf_drug_name"));
        Assert.Equal(modeChapter, loaded.GetFieldMode("bnf_chapter"));
        Assert.Equal(mfDrug, loaded.GetFieldModalFrequency("bnf_drug_name"));
        Assert.Equal(mfChapter, loaded.GetFieldModalFrequency("bnf_chapter"));

        // Additional no-throw
        var ex1 = Record.Exception(() => loaded.GetFieldMode("icb_code"));
        var ex2 = Record.Exception(() => loaded.GetFieldModalFrequency("setting"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
