// Tests for TsvDocument.GetColumnMode, GetColumnUniqueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R274

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R274: Tests for TsvDocument.GetColumnMode, GetColumnUniqueCount deeper.
/// GetColumnMode(colName): returns the most frequently occurring value in the column.
/// GetColumnUniqueCount(colName): returns the number of distinct values in the column.
/// Covers: GetColumnMode no-throw; GetColumnMode correct for known data;
/// GetColumnMode consistent; GetColumnMode save-load;
/// GetColumnUniqueCount no-throw; GetColumnUniqueCount 1 for uniform;
/// GetColumnUniqueCount leq RowCount; GetColumnUniqueCount consistent;
/// GetColumnUniqueCount save-load; dogfood pipeline.
/// </summary>
public class TsvR274GetColumnModeAndUniqueCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR274GetColumnModeAndUniqueCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR274_" + Guid.NewGuid().ToString("N"));
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
        // category A appears 5 times, B 3 times, C 2 times
        string[] cats = { "A", "A", "B", "A", "C", "B", "A", "C", "A", "B" };
        for (int i = 0; i < cats.Length; i++)
            sb.AppendLine($"{i}\t{cats[i]}\t{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tstatus");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\tACTIVE");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnMode("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_Correct_ForKnownData()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal("A", doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnMode("category"), doc.GetColumnMode("category"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnMode("category");
        var path = TempFile("mode_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnMode("category"));
    }

    // -------------------------------------------------------------------------
    // GetColumnUniqueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniqueCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnUniqueCount("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniqueCount_One_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(1, doc.GetColumnUniqueCount("status"));
    }

    [Fact]
    public void GetColumnUniqueCount_Three_ForThreeValues()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(3, doc.GetColumnUniqueCount("category"));
    }

    [Fact]
    public void GetColumnUniqueCount_Leq_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnUniqueCount("category") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnUniqueCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnUniqueCount("category"), doc.GetColumnUniqueCount("category"));
    }

    [Fact]
    public void GetColumnUniqueCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnUniqueCount("category");
        var path = TempFile("uc_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnUniqueCount("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnUniqueCount_Pipeline()
    {
        // Education — ESFA / DfE: Post-16 Education and Training Provider Census 2024
        // Provider-level data on qualification type, funding model, and inspection outcome
        // Mode identifies the most common inspection grade; unique count shows grade distribution breadth

        var path = TempFile("esfa_provider_census_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("provider_ukprn\tprovider_name\tprovider_type\tregion\tofsted_grade\tfunding_band\tlearner_count\tcompletion_rate_pct\temployability_score");

        var rng = new Random(20240901);
        string[] types = { "FE_College", "Sixth_Form_College", "Independent_Training_Provider",
                            "Employer_Provider", "Higher_Education_Institution", "School_Based_Sixth_Form" };
        string[] regions = { "East_Midlands", "East_of_England", "London", "North_East",
                              "North_West", "South_East", "South_West", "West_Midlands",
                              "Yorkshire", "Wales" };
        // Ofsted grade distribution: 1=Outstanding(rare), 2=Good(modal), 3=Requires_Improvement, 4=Inadequate
        // Grade 2 "Good" should be the mode
        string[] gradePool = {
            "1","2","2","2","2","2","2","2","3","3","3","4"
        };
        string[] fundingBands = { "Band_A", "Band_B", "Band_C", "Band_D" };

        string[] providerNames = {
            "Leeds_College_of_Building", "South_Essex_College", "Wigan_and_Leigh_College",
            "Exeter_College", "Gateshead_College", "Hartlepool_College", "Kendal_College",
            "Lancaster_and_Morecambe_College", "Newcastle_College", "North_Tyneside_College",
            "Blackburn_College", "Burnley_College", "Bury_College", "Hopwood_Hall_College",
            "Myerscough_College", "Nelson_and_Colne_College", "Oldham_College", "Pendleton_College",
            "Preston_College", "Runshaw_College", "Salford_City_College", "Tameside_College",
            "Trafford_College", "Wigan_and_Leigh", "Barnet_and_Southgate",
            "City_of_Westminster", "Tower_Hamlets", "Lambeth", "Southwark",
            "Greenwich_Community"
        };

        for (int i = 0; i < 30; i++)
        {
            string type = types[i % types.Length];
            string region = regions[rng.Next(regions.Length)];
            string grade = gradePool[rng.Next(gradePool.Length)];
            string band = fundingBands[rng.Next(fundingBands.Length)];
            int learners = 200 + rng.Next(8000);
            double completion = 65 + rng.NextDouble() * 30;
            int employability = 50 + rng.Next(50);
            sb.AppendLine($"1{100000 + i}\t{providerNames[i]}\t{type}\t{region}\t{grade}\t{band}\t{learners}\t{completion:F1}\t{employability}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(30, doc.RowCount);

        // Ofsted grade mode (should be "2" — "Good")
        var gradeMode = doc.GetColumnMode("ofsted_grade");
        Assert.NotNull(gradeMode);
        Assert.NotEmpty(gradeMode);
        Assert.Equal(gradeMode, doc.GetColumnMode("ofsted_grade")); // consistent

        // Ofsted grade unique count (1, 2, 3, 4 → up to 4 distinct values)
        var gradeUniqueCount = doc.GetColumnUniqueCount("ofsted_grade");
        Assert.True(gradeUniqueCount >= 1);
        Assert.True(gradeUniqueCount <= doc.RowCount);
        Assert.Equal(gradeUniqueCount, doc.GetColumnUniqueCount("ofsted_grade")); // consistent

        // Provider type mode
        var typeMode = doc.GetColumnMode("provider_type");
        Assert.NotNull(typeMode);
        Assert.Equal(typeMode, doc.GetColumnMode("provider_type")); // consistent

        // Provider type unique count (6 types defined)
        var typeUniqueCount = doc.GetColumnUniqueCount("provider_type");
        Assert.True(typeUniqueCount >= 1);
        Assert.True(typeUniqueCount <= 6);

        // Region unique count
        var regionUnique = doc.GetColumnUniqueCount("region");
        Assert.True(regionUnique >= 1);
        Assert.True(regionUnique <= doc.RowCount);

        // Funding band unique count (up to 4 bands)
        var bandUnique = doc.GetColumnUniqueCount("funding_band");
        Assert.True(bandUnique >= 1);
        Assert.True(bandUnique <= 4);

        // SaveToFile
        var outPath = TempFile("esfa_provider_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(gradeMode, loaded.GetColumnMode("ofsted_grade"));
        Assert.Equal(gradeUniqueCount, loaded.GetColumnUniqueCount("ofsted_grade"));
        Assert.Equal(typeMode, loaded.GetColumnMode("provider_type"));
        Assert.Equal(typeUniqueCount, loaded.GetColumnUniqueCount("provider_type"));
        Assert.Equal(regionUnique, loaded.GetColumnUniqueCount("region"));

        var ex1 = Record.Exception(() => loaded.GetColumnMode("ofsted_grade"));
        var ex2 = Record.Exception(() => loaded.GetColumnUniqueCount("provider_type"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
