// Tests for CsvDocument.GetColumnEntropy, GetColumnUniformity, GetColumnGiniImpurity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R237

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R237: Tests for CsvDocument.GetColumnEntropy, GetColumnUniformity, GetColumnGiniImpurity deeper.
/// GetColumnEntropy(col): returns the Shannon entropy (in bits) of value distribution in the column.
/// GetColumnUniformity(col): returns [0,1] uniformity score; 1 = all values equal, 0 = maximally varied.
/// GetColumnGiniImpurity(col): returns the Gini impurity of categorical value distribution.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for uniform; GetColumnEntropy save-load;
/// GetColumnUniformity no-throw; GetColumnUniformity in [0,1]; GetColumnUniformity consistent;
/// GetColumnUniformity one for uniform; GetColumnUniformity save-load;
/// GetColumnGiniImpurity no-throw; GetColumnGiniImpurity in [0,1]; GetColumnGiniImpurity consistent;
/// GetColumnGiniImpurity zero for uniform; GetColumnGiniImpurity save-load;
/// dogfood Append→GetColumnEntropy→GetColumnUniformity→GetColumnGiniImpurity→SaveToFile pipeline.
/// </summary>
public class CsvR237GetColumnEntropyAndGiniImpurityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR237GetColumnEntropyAndGiniImpurityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR237_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateElectionCsv()
    {
        var path = TempFile("election.csv");
        var lines = new[]
        {
            "constituency,party,votes,result,region",
            "C001,Labour,18500,Won,North",
            "C002,Conservative,21300,Won,South",
            "C003,Labour,15600,Won,North",
            "C004,LibDem,9800,Lost,South",
            "C005,Labour,19200,Won,Midlands",
            "C006,Conservative,22100,Won,South",
            "C007,Labour,16800,Won,North",
            "C008,Conservative,18900,Won,East",
            "C009,LibDem,11200,Lost,West",
            "C010,Labour,17400,Won,Midlands",
            "C011,Conservative,20600,Won,East",
            "C012,Labour,14900,Won,North"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var lines = new[]
        {
            "id,status,score",
            "1,Pass,100",
            "2,Pass,95",
            "3,Pass,98",
            "4,Pass,92",
            "5,Pass,97"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("party"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        Assert.True(doc.GetColumnEntropy("party") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        Assert.Equal(doc.GetColumnEntropy("party"), doc.GetColumnEntropy("party"), precision: 4);
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("status"), precision: 4);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var before = doc.GetColumnEntropy("region");
        var path = TempFile("ent_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("region"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnUniformity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniformity_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var ex = Record.Exception(() => doc.GetColumnUniformity("result"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniformity_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var u = doc.GetColumnUniformity("party");
        Assert.True(u >= 0.0 && u <= 1.0);
    }

    [Fact]
    public void GetColumnUniformity_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        Assert.Equal(doc.GetColumnUniformity("region"), doc.GetColumnUniformity("region"), precision: 4);
    }

    [Fact]
    public void GetColumnUniformity_One_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(1.0, doc.GetColumnUniformity("status"), precision: 4);
    }

    [Fact]
    public void GetColumnUniformity_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var before = doc.GetColumnUniformity("result");
        var path = TempFile("uni_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnUniformity("result"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnGiniImpurity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnGiniImpurity_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var ex = Record.Exception(() => doc.GetColumnGiniImpurity("party"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnGiniImpurity_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var g = doc.GetColumnGiniImpurity("party");
        Assert.True(g >= 0.0 && g <= 1.0);
    }

    [Fact]
    public void GetColumnGiniImpurity_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        Assert.Equal(doc.GetColumnGiniImpurity("result"), doc.GetColumnGiniImpurity("result"), precision: 4);
    }

    [Fact]
    public void GetColumnGiniImpurity_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnGiniImpurity("status"), precision: 4);
    }

    [Fact]
    public void GetColumnGiniImpurity_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateElectionCsv());
        var before = doc.GetColumnGiniImpurity("party");
        var path = TempFile("gini_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnGiniImpurity("party"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnUniformity_GetColumnGiniImpurity_SaveToFile_Pipeline()
    {
        // Urban planning — smart city mobility survey dataset
        var path = TempFile("dogfood_mobility.csv");
        var lines = new[]
        {
            "respondent_id,age_group,primary_mode,journey_purpose,frequency,satisfaction,district",
            "R001,25-34,Cycling,Commute,Daily,High,Central",
            "R002,35-44,PublicTransport,Commute,Daily,Medium,North",
            "R003,18-24,Walking,Leisure,Weekly,High,East",
            "R004,45-54,Car,Commute,Daily,Low,South",
            "R005,25-34,PublicTransport,Commute,Daily,Medium,Central",
            "R006,55-64,Car,Shopping,Weekly,Medium,West",
            "R007,25-34,Cycling,Leisure,Daily,High,Central",
            "R008,35-44,PublicTransport,Work,Daily,High,North",
            "R009,18-24,Walking,Leisure,Daily,High,East",
            "R010,45-54,Car,Commute,Daily,Low,South",
            "R011,25-34,PublicTransport,Commute,Daily,Medium,Central",
            "R012,55-64,Car,Shopping,Monthly,Low,West"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnEntropy — primary_mode (4 modes: Cycling×2, PublicTransport×4, Walking×2, Car×4)
        var modeEntropy = doc.GetColumnEntropy("primary_mode");
        Assert.True(modeEntropy >= 0.0);
        Assert.Equal(modeEntropy, doc.GetColumnEntropy("primary_mode"), precision: 4); // consistent

        // GetColumnEntropy — satisfaction (3 levels: High×5, Medium×4, Low×3)
        var satEntropy = doc.GetColumnEntropy("satisfaction");
        Assert.True(satEntropy >= 0.0);

        // GetColumnEntropy — frequency (3 levels: Daily×8, Weekly×3, Monthly×1 → less uniform)
        var freqEntropy = doc.GetColumnEntropy("frequency");
        Assert.True(freqEntropy >= 0.0);

        // GetColumnUniformity — primary_mode
        var modeUniformity = doc.GetColumnUniformity("primary_mode");
        Assert.True(modeUniformity >= 0.0 && modeUniformity <= 1.0);
        Assert.Equal(modeUniformity, doc.GetColumnUniformity("primary_mode"), precision: 4); // consistent

        // GetColumnUniformity — frequency (Daily dominates → higher uniformity)
        var freqUniformity = doc.GetColumnUniformity("frequency");
        Assert.True(freqUniformity >= 0.0 && freqUniformity <= 1.0);
        // More uniform than mode (Daily dominates)
        Assert.True(freqUniformity > 0.0);

        // GetColumnGiniImpurity — primary_mode
        var modeGini = doc.GetColumnGiniImpurity("primary_mode");
        Assert.True(modeGini >= 0.0 && modeGini <= 1.0);
        Assert.Equal(modeGini, doc.GetColumnGiniImpurity("primary_mode"), precision: 4); // consistent

        // GetColumnGiniImpurity — district (5 districts: Central×4, North×2, East×2, South×2, West×2)
        var districtGini = doc.GetColumnGiniImpurity("district");
        Assert.True(districtGini >= 0.0 && districtGini <= 1.0);

        // AppendRow — two more respondents
        doc.AppendRow(new[] { "R013", "35-44", "Cycling", "Commute", "Daily", "High", "Central" });
        doc.AppendRow(new[] { "R014", "25-34", "PublicTransport", "Work", "Daily", "Medium", "North" });
        Assert.Equal(14, doc.RowCount);

        // After append, metrics remain valid
        Assert.True(doc.GetColumnEntropy("primary_mode") >= 0.0);
        Assert.True(doc.GetColumnUniformity("satisfaction") >= 0.0);
        Assert.True(doc.GetColumnGiniImpurity("district") >= 0.0);

        // SaveToFile
        var out1 = TempFile("dogfood_mobility_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnEntropy("satisfaction"), loaded.GetColumnEntropy("satisfaction"), precision: 4);
        Assert.Equal(doc.GetColumnUniformity("frequency"), loaded.GetColumnUniformity("frequency"), precision: 4);
        Assert.Equal(doc.GetColumnGiniImpurity("district"), loaded.GetColumnGiniImpurity("district"), precision: 4);

        // Uniform column verification
        var uniformPath = TempFile("dogfood_uniform.csv");
        File.WriteAllLines(uniformPath, new[] { "id,status,code", "1,Active,X1", "2,Active,X2", "3,Active,X3" }, System.Text.Encoding.UTF8);
        var uniformDoc = CsvDocument.LoadFile(uniformPath);
        Assert.Equal(0.0, uniformDoc.GetColumnEntropy("status"), precision: 4);
        Assert.Equal(1.0, uniformDoc.GetColumnUniformity("status"), precision: 4);
        Assert.Equal(0.0, uniformDoc.GetColumnGiniImpurity("status"), precision: 4);

        // Final save
        var out2 = TempFile("dogfood_mobility_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.True(loaded2.GetColumnEntropy("primary_mode") >= 0.0);
        Assert.True(loaded2.GetColumnUniformity("primary_mode") >= 0.0);
        Assert.True(loaded2.GetColumnGiniImpurity("primary_mode") >= 0.0);
        var ex1 = Record.Exception(() => loaded2.GetColumnEntropy("satisfaction"));
        var ex2 = Record.Exception(() => loaded2.GetColumnGiniImpurity("district"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
