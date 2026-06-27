// Tests for TsvDocument.GetColumnEntropy, GetColumnCardinality deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R273

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R273: Tests for TsvDocument.GetColumnEntropy, GetColumnCardinality deeper.
/// GetColumnEntropy(colName): returns the Shannon entropy of the value distribution in the column.
/// GetColumnCardinality(colName): returns the count of distinct values in the column.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy zero for uniform;
/// GetColumnEntropy consistent; GetColumnEntropy save-load;
/// GetColumnCardinality no-throw; GetColumnCardinality positive;
/// GetColumnCardinality one for uniform; GetColumnCardinality consistent;
/// GetColumnCardinality save-load; GetColumnCardinality leq RowCount; dogfood pipeline.
/// </summary>
public class TsvR273GetColumnEntropyAndCardinalityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR273GetColumnEntropyAndCardinalityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR273_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tcategory\tvalue");
        // category: A(4), B(3), C(2), D(1)
        for (int i = 0; i < 4; i++) sb.AppendLine($"R{(i):D2}\tA\t{i * 10}");
        for (int i = 4; i < 7; i++) sb.AppendLine($"R{i:D2}\tB\t{i * 10}");
        for (int i = 7; i < 9; i++) sb.AppendLine($"R{i:D2}\tC\t{i * 10}");
        sb.AppendLine("R09\tD\t90");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tregion");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2}\tNorth");
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
        var ex = Record.Exception(() => doc.GetColumnEntropy("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnEntropy("category") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("region"), precision: 6);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnEntropy("category"), doc.GetColumnEntropy("category"));
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnEntropy("category");
        var path = TempFile("ent_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnEntropy("category"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCardinality
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCardinality_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnCardinality("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCardinality_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnCardinality("category") > 0);
    }

    [Fact]
    public void GetColumnCardinality_One_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(1, doc.GetColumnCardinality("region"));
    }

    [Fact]
    public void GetColumnCardinality_Four_ForFourValues()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(4, doc.GetColumnCardinality("category"));
    }

    [Fact]
    public void GetColumnCardinality_Leq_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnCardinality("category") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnCardinality_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnCardinality("category"), doc.GetColumnCardinality("category"));
    }

    [Fact]
    public void GetColumnCardinality_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnCardinality("category");
        var path = TempFile("card_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnCardinality("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnCardinality_Pipeline()
    {
        // Education — UCAS / HESA: University Application and Admissions Data 2024
        // Subject area and institution diversity metrics for widening participation analysis
        // Entropy and cardinality quantify subject diversity and application concentration

        var path = TempFile("ucas_admissions_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("application_id\tinstitution\tsubject_jacs\tqualification_type\tapplicant_domicile\tentry_tariff\tstatus\tgender\tethnic_group\tage_group");

        var rng = new Random(20240901);
        string[] institutions = {
            "Oxford", "Cambridge", "Imperial", "UCL", "LSE",
            "Manchester", "Birmingham", "Bristol", "Edinburgh", "Warwick",
            "Sheffield", "Leeds", "Nottingham", "Liverpool", "Durham",
            "Southampton", "Newcastle", "Cardiff", "Leicester", "Exeter"
        };
        string[] jacs = {
            "A_Medicine", "B_Subjects_Allied_Medicine", "C_Biological_Sciences",
            "D_Veterinary_Sciences", "F_Physical_Sciences", "G_Mathematical_Sciences",
            "H_Engineering", "I_Computer_Sciences", "J_Technologies",
            "K_Architecture", "L_Social_Studies", "M_Law",
            "N_Business_Admin", "P_Mass_Communications", "Q_Linguistics",
            "R_European_Languages", "T_Eastern_Languages", "V_Historical_Philosophical",
            "W_Creative_Arts", "X_Education"
        };
        string[] qualTypes = { "A_Level", "A_Level", "A_Level", "BTEC", "IB", "Scottish_Highers", "Access_HE", "Other" };
        string[] domiciles = { "England", "England", "England", "Scotland", "Wales", "Northern_Ireland", "EU", "International" };
        string[] statuses = { "Accepted", "Accepted", "Accepted", "Rejected", "Withdrawn", "Conditional" };
        string[] genders = { "Female", "Male", "Non_Binary_Other" };
        string[] ethnicGroups = { "White", "Asian", "Black", "Mixed", "Other_Ethnic", "Not_Stated" };
        string[] ageGroups = { "17", "18", "18", "18", "19", "20", "21_Plus" };

        for (int i = 0; i < 500; i++)
        {
            string inst = institutions[rng.Next(institutions.Length)];
            string jac = jacs[rng.Next(jacs.Length)];
            string qual = qualTypes[rng.Next(qualTypes.Length)];
            string dom = domiciles[rng.Next(domiciles.Length)];
            int tariff = qual == "IB" ? 600 + rng.Next(0, 240)
                       : qual == "BTEC" ? 160 + rng.Next(0, 192)
                       : 80 + rng.Next(0, 280);
            string status = statuses[rng.Next(statuses.Length)];
            string gender = genders[rng.Next(genders.Length)];
            string ethnic = ethnicGroups[rng.Next(ethnicGroups.Length)];
            string age = ageGroups[rng.Next(ageGroups.Length)];
            sb.AppendLine($"APP{i:D6}\t{inst}\t{jac}\t{qual}\t{dom}\t{tariff}\t{status}\t{gender}\t{ethnic}\t{age}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(500, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Institution entropy and cardinality (20 institutions)
        var instEnt = doc.GetColumnEntropy("institution");
        var instCard = doc.GetColumnCardinality("institution");
        Assert.True(instEnt >= 0.0);
        Assert.True(instCard >= 1 && instCard <= 20);
        Assert.Equal(instEnt, doc.GetColumnEntropy("institution")); // consistent
        Assert.Equal(instCard, doc.GetColumnCardinality("institution")); // consistent

        // Subject JACS entropy and cardinality (up to 20)
        var jacEnt = doc.GetColumnEntropy("subject_jacs");
        var jacCard = doc.GetColumnCardinality("subject_jacs");
        Assert.True(jacEnt >= 0.0);
        Assert.True(jacCard >= 1 && jacCard <= 20);

        // Status cardinality (≤6)
        var statusCard = doc.GetColumnCardinality("status");
        Assert.True(statusCard >= 1 && statusCard <= 6);
        var statusEnt = doc.GetColumnEntropy("status");
        Assert.True(statusEnt >= 0.0);

        // Gender cardinality (≤3)
        var genderCard = doc.GetColumnCardinality("gender");
        Assert.True(genderCard >= 1 && genderCard <= 3);

        // All cardinalities ≤ RowCount
        Assert.True(instCard <= doc.RowCount);
        Assert.True(jacCard <= doc.RowCount);

        // SaveToFile
        var outPath = TempFile("ucas_admissions_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(instEnt, loaded.GetColumnEntropy("institution"), precision: 6);
        Assert.Equal(instCard, loaded.GetColumnCardinality("institution"));
        Assert.Equal(jacEnt, loaded.GetColumnEntropy("subject_jacs"), precision: 6);
        Assert.Equal(statusCard, loaded.GetColumnCardinality("status"));
    }
}
