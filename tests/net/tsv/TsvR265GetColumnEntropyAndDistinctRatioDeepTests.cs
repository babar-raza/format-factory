// Tests for TsvDocument.GetColumnEntropy, GetColumnDistinctRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R265

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R265: Tests for TsvDocument.GetColumnEntropy, GetColumnDistinctRatio deeper.
/// GetColumnEntropy(colName): returns Shannon entropy of the value distribution in the column (bits).
/// GetColumnDistinctRatio(colName): returns (distinct count / total row count) as a fraction 0..1.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant; GetColumnEntropy save-load;
/// GetColumnDistinctRatio no-throw; GetColumnDistinctRatio in-range;
/// GetColumnDistinctRatio one for all-unique; GetColumnDistinctRatio near-zero for constant;
/// GetColumnDistinctRatio consistent; GetColumnDistinctRatio save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnDistinctRatio→SaveToFile pipeline.
/// </summary>
public class TsvR265GetColumnEntropyAndDistinctRatioDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR265GetColumnEntropyAndDistinctRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR265_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("patient_id\tdiagnosis_code\tseverity\tage_group\ttreatment");
        string[] diags = { "A001", "B002", "C003", "D004", "E005", "F006", "G007", "H008" };
        string[] severities = { "Low", "Medium", "High", "Critical" };
        string[] ages = { "18-30", "31-45", "46-60", "61-75", "75+" };
        string[] treatments = { "Medication", "Surgery", "Physiotherapy", "Monitoring" };
        var rng = new Random(20240820);
        for (int i = 0; i < 160; i++)
        {
            sb.AppendLine($"P{i:D5}\t{diags[rng.Next(diags.Length)]}\t{severities[rng.Next(severities.Length)]}\t{ages[rng.Next(ages.Length)]}\t{treatments[rng.Next(treatments.Length)]}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tregion");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{i}\tNorth");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniqueTsv()
    {
        var path = TempFile("unique.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("record_id\tvalue");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"R{i:D5}\t{i * 1000}"); // all unique
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("severity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnEntropy("severity") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnEntropy("severity"), doc.GetColumnEntropy("severity"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("region"), precision: 8);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnEntropy("severity");
        var path = TempFile("ent_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("severity"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnDistinctRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDistinctRatio_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnDistinctRatio("severity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDistinctRatio_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var dr = doc.GetColumnDistinctRatio("severity");
        Assert.True(dr >= 0.0 && dr <= 1.0);
    }

    [Fact]
    public void GetColumnDistinctRatio_One_ForAllUnique()
    {
        var doc = TsvDocument.LoadFile(CreateUniqueTsv());
        Assert.Equal(1.0, doc.GetColumnDistinctRatio("record_id"), precision: 6);
    }

    [Fact]
    public void GetColumnDistinctRatio_NearZero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        // 1 distinct value / 50 rows = 0.02
        var dr = doc.GetColumnDistinctRatio("region");
        Assert.True(dr <= 0.1);
    }

    [Fact]
    public void GetColumnDistinctRatio_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnDistinctRatio("severity"), doc.GetColumnDistinctRatio("severity"));
    }

    [Fact]
    public void GetColumnDistinctRatio_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnDistinctRatio("diagnosis_code");
        var path = TempFile("dr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnDistinctRatio("diagnosis_code"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnDistinctRatio_Pipeline()
    {
        // Healthcare — NHS England: Emergency Department Activity Statistics 2024-25
        // Winter pressures data — patient flow, triage categories, admission routes
        // Entropy analysis to detect data quality issues (too-uniform distributions may indicate coding errors)

        var path = TempFile("nhs_ed_activity.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("attendance_id\tsite_code\ttriage_category\tarrival_mode\tattendance_category\tdisposal_code\twait_time_mins\tdepartment_type");

        var rng = new Random(20241101);
        string[] sites = { "RJC01", "RJE01", "RJF01", "RJL01", "RJN01", "RJQ01", "RJR01", "RJT01",
                            "RJW01", "RJX01", "RKB01", "RKE01", "RKL01", "RKM01", "RKN01" };
        // Triage: 1=Immediate, 2=Very Urgent, 3=Urgent, 4=Standard, 5=Non-Urgent
        string[] triages = { "1", "2", "3", "3", "3", "4", "4", "4", "4", "5" }; // 3 and 4 dominate
        string[] modes = { "Ambulance", "Walk-in", "Walk-in", "Walk-in", "Self-referral", "GP-referral", "Other" };
        string[] attendCats = { "First", "Follow-up" };
        string[] disposals = { "Admitted", "Discharged", "Referred", "Left before treatment", "Transferred" };
        string[] deptTypes = { "Type1_MajorED", "Type1_MajorED", "Type1_MajorED", "Type2_Minor", "Type3_UTC" };

        for (int i = 0; i < 250; i++)
        {
            string site = sites[rng.Next(sites.Length)];
            string triage = triages[rng.Next(triages.Length)];
            string mode = modes[rng.Next(modes.Length)];
            string cat = attendCats[rng.Next(attendCats.Length)];
            string disposal = disposals[rng.Next(disposals.Length)];
            string dept = deptTypes[rng.Next(deptTypes.Length)];
            int wait = triage == "1" ? rng.Next(1, 5) :
                       triage == "2" ? rng.Next(5, 30) :
                       triage == "3" ? rng.Next(30, 120) :
                       rng.Next(60, 300);
            sb.AppendLine($"ED{i:D6}\t{site}\t{triage}\t{mode}\t{cat}\t{disposal}\t{wait}\t{dept}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(250, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Entropy of triage_category — skewed distribution (3 and 4 dominate)
        var entTriage = doc.GetColumnEntropy("triage_category");
        Assert.True(entTriage >= 0.0);
        Assert.Equal(entTriage, doc.GetColumnEntropy("triage_category")); // consistent

        // Entropy of site_code — roughly uniform across 15 sites → high entropy
        var entSite = doc.GetColumnEntropy("site_code");
        Assert.True(entSite >= 0.0);
        Assert.True(entSite > entTriage); // 15 sites vs 5 categories → more variety

        // Entropy of attendance_category — binary (First/Follow-up) → lower entropy
        var entCat = doc.GetColumnEntropy("attendance_category");
        Assert.True(entCat >= 0.0);
        Assert.True(entCat <= 2.0); // max entropy for binary = 1 bit; allow up to 2 for imprecision

        // Entropy of wait_time_mins — continuous-like → relatively high
        var entWait = doc.GetColumnEntropy("wait_time_mins");
        Assert.True(entWait >= 0.0);

        // DistinctRatio of triage_category — 5 categories / 250 rows = 0.02
        var drTriage = doc.GetColumnDistinctRatio("triage_category");
        Assert.True(drTriage >= 0.0 && drTriage <= 1.0);
        Assert.True(drTriage <= 0.1); // very few distinct values relative to rows

        // DistinctRatio of attendance_id — all unique → ratio = 1
        var drId = doc.GetColumnDistinctRatio("attendance_id");
        Assert.Equal(1.0, drId, precision: 6);

        // DistinctRatio of site_code — 15 sites / 250 rows ≈ 0.06
        var drSite = doc.GetColumnDistinctRatio("site_code");
        Assert.True(drSite >= 0.0 && drSite <= 1.0);
        Assert.True(drSite < 0.2); // bounded number of sites

        // Entropy for constant column sanity: use a synthetic constant column
        var pathConst = TempFile("const.tsv");
        var sbConst = new StringBuilder();
        sbConst.AppendLine("id\tregion");
        for (int i = 0; i < 100; i++) sbConst.AppendLine($"{i}\tLondon");
        File.WriteAllText(pathConst, sbConst.ToString());
        var docConst = TsvDocument.LoadFile(pathConst);
        Assert.Equal(0.0, docConst.GetColumnEntropy("region"), precision: 8);
        Assert.True(docConst.GetColumnDistinctRatio("region") <= 0.05);

        // Basic column stats
        Assert.True(doc.GetColumnMean("wait_time_mins") > 0);

        // SaveToFile
        var outPath = TempFile("nhs_ed_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(entTriage, loaded.GetColumnEntropy("triage_category"), precision: 8);
        Assert.Equal(drId, loaded.GetColumnDistinctRatio("attendance_id"), precision: 8);
        Assert.Equal(entSite, loaded.GetColumnEntropy("site_code"), precision: 8);
        Assert.Equal(drSite, loaded.GetColumnDistinctRatio("site_code"), precision: 8);
    }
}
