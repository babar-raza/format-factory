// Tests for TsvDocument.GetColumnEntropy, GetColumnNormalizedEntropy deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R258

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R258: Tests for TsvDocument.GetColumnEntropy, GetColumnNormalizedEntropy deeper.
/// GetColumnEntropy(colName): returns Shannon entropy (in bits) of the column's value distribution.
/// GetColumnNormalizedEntropy(colName): returns entropy normalised to [0,1] by log2(uniqueValues).
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for constant; GetColumnEntropy save-load;
/// GetColumnNormalizedEntropy no-throw; GetColumnNormalizedEntropy in-range;
/// GetColumnNormalizedEntropy zero for constant; GetColumnNormalizedEntropy one for uniform;
/// GetColumnNormalizedEntropy consistent; GetColumnNormalizedEntropy save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetColumnNormalizedEntropy pipeline.
/// </summary>
public class TsvR258GetColumnEntropyAndNormalizedEntropyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR258GetColumnEntropyAndNormalizedEntropyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR258_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("student_id\tgrade\tsubject\tscore\tpass_fail");
        var rng = new Random(20240815);
        string[] subjects = { "Maths", "English", "Science", "History", "Geography" };
        string[] grades = { "A", "B", "C", "D", "E" };
        for (int i = 0; i < 100; i++)
        {
            string grade = grades[rng.Next(grades.Length)];
            string subject = subjects[i % subjects.Length];
            int score = 40 + rng.Next(60);
            string pf = score >= 50 ? "Pass" : "Fail";
            sb.AppendLine($"S{i:D4}\t{grade}\t{subject}\t{score}\t{pf}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tcategory");
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i}\tFixed");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tcolour");
        string[] colours = { "Red", "Green", "Blue", "Yellow" };
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{i}\t{colours[i % colours.Length]}");
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
        var ex = Record.Exception(() => doc.GetColumnEntropy("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnEntropy("grade") >= 0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnEntropy("subject"), doc.GetColumnEntropy("subject"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("category"), precision: 8);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnEntropy("grade");
        var path = TempFile("ent_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("grade"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalizedEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalizedEntropy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnNormalizedEntropy("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ne = doc.GetColumnNormalizedEntropy("grade");
        Assert.True(ne >= 0.0 && ne <= 1.0);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnNormalizedEntropy("category"), precision: 8);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_One_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        // 4 equally distributed colours → normalised entropy = 1.0
        Assert.Equal(1.0, doc.GetColumnNormalizedEntropy("colour"), precision: 8);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnNormalizedEntropy("pass_fail");
        var v2 = doc.GetColumnNormalizedEntropy("pass_fail");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnNormalizedEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnNormalizedEntropy("subject");
        var path = TempFile("ne_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnNormalizedEntropy("subject"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnNormalizedEntropy_Pipeline()
    {
        // Public health — NHS England A&E Attendances and Emergency Admissions
        // Monthly dashboard data with attendance types, outcomes, and wait times
        // Entropy analysis to identify dominated categories vs balanced distributions
        var path = TempFile("nhs_ae_data.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("month\tsite_code\tregion\tattendance_type\ttriage_category\tdisposal_type\twait_mins\tadmitted");

        var rng = new Random(20240901);
        string[] regions = { "London", "Midlands", "North West", "North East & Yorkshire", "South East", "South West", "East of England" };
        // Attendance types: Type 1 (major A&E) dominates ~70%, Type 2 (specialist), Type 3 (minor)
        string[] attTypes = { "Type 1", "Type 1", "Type 1", "Type 1", "Type 1", "Type 1", "Type 1", "Type 2", "Type 3", "Type 3" };
        string[] triageCats = { "Immediate", "Very Urgent", "Urgent", "Standard", "Non-Urgent" };
        // Disposals: Admitted ~25%, Discharged ~65%, Left before seen ~5%, Transferred ~5%
        string[] disposals = { "Discharged", "Discharged", "Discharged", "Discharged", "Discharged", "Discharged", "Discharged", "Admitted", "Admitted", "Admitted", "Admitted", "Left before seen", "Transferred" };

        string[] months = { "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09",
                             "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03" };

        for (int i = 0; i < 200; i++)
        {
            string month = months[i % months.Length];
            string siteCode = $"RX{rng.Next(100, 999)}";
            string region = regions[rng.Next(regions.Length)];
            string attType = attTypes[rng.Next(attTypes.Length)];
            string triage = triageCats[rng.Next(triageCats.Length)];
            string disposal = disposals[rng.Next(disposals.Length)];
            int wait = attType == "Type 1" ? (60 + rng.Next(180)) : (15 + rng.Next(60));
            bool admitted = disposal == "Admitted";
            sb.AppendLine($"{month}\t{siteCode}\t{region}\t{attType}\t{triage}\t{disposal}\t{wait}\t{admitted}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnEntropy — attendance_type: Type 1 dominates → low entropy
        var entropyAttType = doc.GetColumnEntropy("attendance_type");
        Assert.True(entropyAttType >= 0);
        Assert.Equal(entropyAttType, doc.GetColumnEntropy("attendance_type")); // consistent

        // triage_category: 5 categories → higher entropy than 2-value columns
        var entropyTriage = doc.GetColumnEntropy("triage_category");
        Assert.True(entropyTriage >= 0);

        // admitted: binary → at most 1 bit of entropy
        var entropyAdmitted = doc.GetColumnEntropy("admitted");
        Assert.True(entropyAdmitted >= 0);
        Assert.True(entropyAdmitted <= 1.01); // binary column ≤ 1 bit

        // region: 7 values → higher entropy
        var entropyRegion = doc.GetColumnEntropy("region");
        Assert.True(entropyRegion >= 0);
        // More unique values → ≥ entropy of binary column
        Assert.True(entropyRegion >= entropyAdmitted);

        // GetColumnNormalizedEntropy
        var neAttType = doc.GetColumnNormalizedEntropy("attendance_type");
        Assert.True(neAttType >= 0.0 && neAttType <= 1.0);

        var neTriage = doc.GetColumnNormalizedEntropy("triage_category");
        Assert.True(neTriage >= 0.0 && neTriage <= 1.0);

        var neAdmitted = doc.GetColumnNormalizedEntropy("admitted");
        Assert.True(neAdmitted >= 0.0 && neAdmitted <= 1.0);

        // Consistent
        Assert.Equal(neAttType, doc.GetColumnNormalizedEntropy("attendance_type"));
        Assert.Equal(neTriage, doc.GetColumnNormalizedEntropy("triage_category"));

        // Basic column stats
        Assert.True(doc.GetColumnMean("wait_mins") > 0);
        Assert.True(doc.GetColumnStdDev("wait_mins") > 0);

        // SaveToFile
        var outPath = TempFile("nhs_ae_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(entropyAttType, loaded.GetColumnEntropy("attendance_type"), precision: 8);
        Assert.Equal(neAttType, loaded.GetColumnNormalizedEntropy("attendance_type"), precision: 8);
        Assert.Equal(entropyTriage, loaded.GetColumnEntropy("triage_category"), precision: 8);

        // Constant column test
        var path2 = TempFile("constant_ae.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("site\tdata_type");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"RX{i:D3}\tA&E Attendance");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnEntropy("data_type"), precision: 8);
        Assert.Equal(0.0, doc2.GetColumnNormalizedEntropy("data_type"), precision: 8);
    }
}
