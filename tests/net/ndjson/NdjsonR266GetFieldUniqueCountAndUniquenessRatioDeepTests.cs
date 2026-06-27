// Tests for NdjsonDocument.GetFieldUniqueCount, GetFieldUniquenessRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R266

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R266: Tests for NdjsonDocument.GetFieldUniqueCount, GetFieldUniquenessRatio deeper.
/// GetFieldUniqueCount(fieldName): returns count of distinct non-null values in the field.
/// GetFieldUniquenessRatio(fieldName): returns uniqueCount / RecordCount ∈ [0,1].
/// Covers: GetFieldUniqueCount no-throw; GetFieldUniqueCount non-negative; GetFieldUniqueCount consistent;
/// GetFieldUniqueCount one for constant; GetFieldUniqueCount equals RecordCount for unique;
/// GetFieldUniqueCount save-load; GetFieldUniquenessRatio no-throw;
/// GetFieldUniquenessRatio in-range; GetFieldUniquenessRatio one for all-unique;
/// GetFieldUniquenessRatio zero-to-near-zero for constant; GetFieldUniquenessRatio consistent;
/// GetFieldUniquenessRatio save-load;
/// dogfood CreateDoc→GetFieldUniqueCount→GetFieldUniquenessRatio pipeline.
/// </summary>
public class NdjsonR266GetFieldUniqueCountAndUniquenessRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR266GetFieldUniqueCountAndUniquenessRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR266_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(20240901);
        string[] categories = { "A", "B", "C" };
        string[] statuses = { "Active", "Inactive", "Pending" };
        for (int i = 0; i < 60; i++)
        {
            string id = $"REC{i:D4}";
            string cat = categories[rng.Next(categories.Length)];
            string status = statuses[i % statuses.Length];
            int value = rng.Next(1000);
            sb.AppendLine($"{{\"id\":\"{id}\",\"category\":\"{cat}\",\"status\":\"{status}\",\"value\":{value},\"source\":\"NHS\"}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantFieldNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"type\":\"fixed\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateAllUniqueNdjson()
    {
        var path = TempFile("unique.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{{\"uid\":\"ID-{i:D4}\",\"val\":{i}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldUniqueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldUniqueCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldUniqueCount("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldUniqueCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldUniqueCount("category") >= 0);
    }

    [Fact]
    public void GetFieldUniqueCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldUniqueCount("status"), doc.GetFieldUniqueCount("status"));
    }

    [Fact]
    public void GetFieldUniqueCount_One_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantFieldNdjson());
        Assert.Equal(1, doc.GetFieldUniqueCount("type"));
    }

    [Fact]
    public void GetFieldUniqueCount_Equals_RecordCount_ForAllUnique()
    {
        var doc = NdjsonDocument.LoadFile(CreateAllUniqueNdjson());
        Assert.Equal(doc.RecordCount, doc.GetFieldUniqueCount("uid"));
    }

    [Fact]
    public void GetFieldUniqueCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldUniqueCount("category");
        var path = TempFile("uc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldUniqueCount("category"));
    }

    // -------------------------------------------------------------------------
    // GetFieldUniquenessRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldUniquenessRatio_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldUniquenessRatio("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldUniquenessRatio_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ur = doc.GetFieldUniquenessRatio("status");
        Assert.True(ur >= 0.0 && ur <= 1.0);
    }

    [Fact]
    public void GetFieldUniquenessRatio_One_ForAllUnique()
    {
        var doc = NdjsonDocument.LoadFile(CreateAllUniqueNdjson());
        Assert.Equal(1.0, doc.GetFieldUniquenessRatio("uid"), precision: 8);
    }

    [Fact]
    public void GetFieldUniquenessRatio_Near_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantFieldNdjson());
        // 1 unique / 40 records = 0.025
        Assert.True(doc.GetFieldUniquenessRatio("type") <= 0.1);
    }

    [Fact]
    public void GetFieldUniquenessRatio_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var v1 = doc.GetFieldUniquenessRatio("category");
        var v2 = doc.GetFieldUniquenessRatio("category");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetFieldUniquenessRatio_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldUniquenessRatio("category");
        var path = TempFile("ur_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldUniquenessRatio("category"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldUniqueCount_GetFieldUniquenessRatio_Pipeline()
    {
        // Health — NHS GP practice prescribing data (open data, NHSBSA)
        // Monthly prescribing records: uniqueness analysis for data quality and cardinality checks
        var path = TempFile("nhs_prescribing.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241101);

        // GP Practice codes (clustered: ~50 practices across 200 records)
        string[] practiceCodes = new string[50];
        for (int i = 0; i < 50; i++)
            practiceCodes[i] = $"E{81000 + i:D6}";

        // BNF chapter names (20 chapters — non-unique field)
        string[] bnfChapters = {
            "Gastro-Intestinal", "Cardiovascular", "Respiratory", "CNS", "Infections",
            "Endocrine", "Obstetrics", "Malignant Disease", "Nutrition", "Musculoskeletal",
            "Eye", "Ear Nose Throat", "Skin", "Immunological", "Anaesthesia",
            "Emergency Treatment", "Other Drugs", "Dressings", "Appliances", "Dental"
        };

        // Drug names (40 common drugs)
        string[] drugs = {
            "Amlodipine", "Atorvastatin", "Bisoprolol", "Lisinopril", "Metformin",
            "Omeprazole", "Ramipril", "Salbutamol", "Simvastatin", "Lansoprazole",
            "Levothyroxine", "Sertraline", "Amoxicillin", "Flucloxacillin", "Doxycycline",
            "Warfarin", "Aspirin", "Codeine", "Paracetamol", "Ibuprofen",
            "Furosemide", "Spironolactone", "Prednisolone", "Allopurinol", "Gabapentin",
            "Citalopram", "Fluoxetine", "Venlafaxine", "Risperidone", "Quetiapine",
            "Methotrexate", "Hydroxychloroquine", "Adalimumab", "Etanercept", "Apixaban",
            "Rivaroxaban", "Dabigatran", "Dapagliflozin", "Empagliflozin", "Sitagliptin"
        };

        // Each prescription record: unique rx_id, non-unique practice/drug/chapter
        for (int i = 0; i < 200; i++)
        {
            string rxId = $"RX-2024-{i + 1:D6}"; // unique
            string practice = practiceCodes[rng.Next(practiceCodes.Length)];
            string drug = drugs[rng.Next(drugs.Length)];
            string chapter = bnfChapters[rng.Next(bnfChapters.Length)];
            int qty = 28 + rng.Next(56);
            double cost = 0.50 + rng.NextDouble() * 49.50;
            string month = $"2024-{(i % 12) + 1:D2}";
            sb.AppendLine($"{{\"rx_id\":\"{rxId}\",\"practice_code\":\"{practice}\",\"drug_name\":\"{drug}\",\"bnf_chapter\":\"{chapter}\",\"quantity\":{qty},\"net_cost_gbp\":{cost:F2},\"month\":\"{month}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldUniqueCount — rx_id: should be 200 (all unique)
        var ucRxId = doc.GetFieldUniqueCount("rx_id");
        Assert.Equal(200, ucRxId);

        // practice_code: ~50 unique practices across 200 records
        var ucPractice = doc.GetFieldUniqueCount("practice_code");
        Assert.True(ucPractice >= 1 && ucPractice <= 200);
        Assert.Equal(ucPractice, doc.GetFieldUniqueCount("practice_code")); // consistent

        // drug_name: up to 40 unique drugs
        var ucDrug = doc.GetFieldUniqueCount("drug_name");
        Assert.True(ucDrug >= 1 && ucDrug <= 40);

        // bnf_chapter: up to 20 unique chapters
        var ucChapter = doc.GetFieldUniqueCount("bnf_chapter");
        Assert.True(ucChapter >= 1 && ucChapter <= 20);

        // month: up to 12 unique months
        var ucMonth = doc.GetFieldUniqueCount("month");
        Assert.True(ucMonth >= 1 && ucMonth <= 12);

        // GetFieldUniquenessRatio — rx_id: all unique → ratio = 1.0
        var urRxId = doc.GetFieldUniquenessRatio("rx_id");
        Assert.Equal(1.0, urRxId, precision: 8);

        // practice_code: ~50/200 = 0.25
        var urPractice = doc.GetFieldUniquenessRatio("practice_code");
        Assert.True(urPractice >= 0.0 && urPractice <= 1.0);
        // rx_id uniqueness > practice uniqueness (50 vs 200)
        Assert.True(urRxId > urPractice);

        // bnf_chapter: ~20/200 = 0.10 — less unique than practice
        var urChapter = doc.GetFieldUniquenessRatio("bnf_chapter");
        Assert.True(urChapter >= 0.0 && urChapter <= 1.0);
        Assert.True(urPractice >= urChapter);

        // Consistent
        Assert.Equal(urPractice, doc.GetFieldUniquenessRatio("practice_code"));
        Assert.Equal(urChapter, doc.GetFieldUniquenessRatio("bnf_chapter"));

        // SaveToFile
        var outPath = TempFile("nhs_prescribing_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(ucRxId, loaded.GetFieldUniqueCount("rx_id"));
        Assert.Equal(urRxId, loaded.GetFieldUniquenessRatio("rx_id"), precision: 8);
        Assert.Equal(ucPractice, loaded.GetFieldUniqueCount("practice_code"));
        Assert.Equal(urPractice, loaded.GetFieldUniquenessRatio("practice_code"), precision: 8);

        // Constant field test
        var path2 = TempFile("constant_prescribing.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{{\"ref\":{i},\"dataset\":\"NHSBSA_MO\"}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(1, doc2.GetFieldUniqueCount("dataset"));
        Assert.True(doc2.GetFieldUniquenessRatio("dataset") <= 0.1);
    }
}
