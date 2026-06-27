// Tests for TsvDocument.GetColumnEntropy, GetMutualInformation, GetUniqueValueCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R230

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R230: Tests for TsvDocument.GetColumnEntropy, GetMutualInformation, GetUniqueValueCount deeper.
/// GetColumnEntropy(columnName): returns the Shannon entropy of the column value distribution.
/// GetMutualInformation(col1, col2): returns the mutual information between two columns.
/// GetUniqueValueCount(columnName): returns the number of distinct values in the column.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for uniform; GetColumnEntropy save-load;
/// GetMutualInformation no-throw; GetMutualInformation non-negative; GetMutualInformation consistent;
/// GetMutualInformation save-load;
/// GetUniqueValueCount no-throw; GetUniqueValueCount positive; GetUniqueValueCount consistent;
/// GetUniqueValueCount leq row count; GetUniqueValueCount save-load;
/// dogfood CreateDoc→GetColumnEntropy→GetMutualInformation→GetUniqueValueCount→SaveToFile pipeline.
/// </summary>
public class TsvR230GetColumnEntropyAndMutualInformationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR230GetColumnEntropyAndMutualInformationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR230_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSurveyTsv()
    {
        var path = TempFile("survey.tsv");
        File.WriteAllText(path,
            "respondent_id\tage_group\tgender\tincome_band\teducation\tpolitical_lean\tsatisfaction\n" +
            "R001\t25-34\tMale\tLow\tBachelor\tCentre\t3\n" +
            "R002\t35-44\tFemale\tMiddle\tMaster\tLeft\t4\n" +
            "R003\t18-24\tMale\tLow\tHighSchool\tRight\t2\n" +
            "R004\t45-54\tFemale\tHigh\tPhD\tLeft\t5\n" +
            "R005\t25-34\tFemale\tMiddle\tBachelor\tCentre\t4\n" +
            "R006\t55-64\tMale\tHigh\tMaster\tRight\t3\n" +
            "R007\t35-44\tMale\tMiddle\tBachelor\tLeft\t4\n" +
            "R008\t18-24\tFemale\tLow\tHighSchool\tCentre\t2\n" +
            "R009\t45-54\tMale\tHigh\tPhD\tCentre\t5\n" +
            "R010\t25-34\tFemale\tMiddle\tBachelor\tLeft\t4\n" +
            "R011\t65+\tMale\tHigh\tMaster\tRight\t3\n" +
            "R012\t35-44\tFemale\tLow\tBachelor\tCentre\t3\n");
        return path;
    }

    private string CreateUniformCategoryTsv()
    {
        // All same value — entropy = 0
        var path = TempFile("uniform.tsv");
        File.WriteAllText(path,
            "id\tcategory\tvalue\n" +
            "1\tA\t10\n" +
            "2\tA\t10\n" +
            "3\tA\t10\n" +
            "4\tA\t10\n" +
            "5\tA\t10\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("age_group"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.True(doc.GetColumnEntropy("gender") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.Equal(doc.GetColumnEntropy("income_band"), doc.GetColumnEntropy("income_band"));
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformCategoryTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("category"), precision: 6);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var before = doc.GetColumnEntropy("political_lean");
        var path = TempFile("ce_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("political_lean"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMutualInformation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var ex = Record.Exception(() => doc.GetMutualInformation("income_band", "education"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMutualInformation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.True(doc.GetMutualInformation("gender", "political_lean") >= 0.0);
    }

    [Fact]
    public void GetMutualInformation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.Equal(
            doc.GetMutualInformation("age_group", "income_band"),
            doc.GetMutualInformation("age_group", "income_band"));
    }

    [Fact]
    public void GetMutualInformation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var before = doc.GetMutualInformation("income_band", "education");
        var path = TempFile("mi_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMutualInformation("income_band", "education"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetUniqueValueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueValueCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var ex = Record.Exception(() => doc.GetUniqueValueCount("age_group"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueValueCount_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.True(doc.GetUniqueValueCount("gender") > 0);
    }

    [Fact]
    public void GetUniqueValueCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.Equal(doc.GetUniqueValueCount("education"), doc.GetUniqueValueCount("education"));
    }

    [Fact]
    public void GetUniqueValueCount_LeqRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        Assert.True(doc.GetUniqueValueCount("political_lean") <= doc.GetRowCount());
    }

    [Fact]
    public void GetUniqueValueCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSurveyTsv());
        var before = doc.GetUniqueValueCount("income_band");
        var path = TempFile("uv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueValueCount("income_band"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetMutualInformation_GetUniqueValueCount_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_genomics.tsv");
        File.WriteAllText(path,
            "sample_id\tpopulation\thaplogroup\tchr1_snp_count\tchr2_snp_count\tmtdna_haplogroup\ty_haplogroup\tdisease_risk\n" +
            "SAMP001\tEuropean\tH\t42500\t38200\tH2a\tR1b\tLow\n" +
            "SAMP002\tEastAsian\tD\t38400\t35100\tD4b\tO2\tLow\n" +
            "SAMP003\tAfrican\tL\t51200\t47800\tL3b\tE1b\tLow\n" +
            "SAMP004\tEuropean\tU\t41800\t37500\tU5a\tI2a\tMedium\n" +
            "SAMP005\tSouthAsian\tM\t44600\t40300\tM30\tH1a\tLow\n" +
            "SAMP006\tEastAsian\tB\t39200\t35900\tB4a\tO3\tLow\n" +
            "SAMP007\tAfrican\tL\t52100\t48600\tL2a\tE1b\tMedium\n" +
            "SAMP008\tEuropean\tJ\t43200\t39100\tJ1c\tR1a\tLow\n" +
            "SAMP009\tAmerindian\tA\t40100\t36800\tA2\tQ1a\tLow\n" +
            "SAMP010\tSouthAsian\tR\t45800\t41500\tR0a\tR2\tMedium\n" +
            "SAMP011\tEuropean\tK\t42800\t38900\tK1a\tR1b\tLow\n" +
            "SAMP012\tEastAsian\tC\t38800\t35400\tC4\tO2\tHigh\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(8, doc.GetColumnCount());

        // GetColumnEntropy — population
        var entPop = doc.GetColumnEntropy("population");
        Assert.True(entPop >= 0.0);
        Assert.Equal(entPop, doc.GetColumnEntropy("population")); // consistent

        // GetColumnEntropy — disease_risk
        var entRisk = doc.GetColumnEntropy("disease_risk");
        Assert.True(entRisk >= 0.0);

        // GetColumnEntropy — haplogroup (many unique values → higher entropy)
        var entHaplo = doc.GetColumnEntropy("haplogroup");
        Assert.True(entHaplo >= 0.0);

        // GetMutualInformation — population and haplogroup (related)
        var miPopHaplo = doc.GetMutualInformation("population", "haplogroup");
        Assert.True(miPopHaplo >= 0.0);
        Assert.Equal(miPopHaplo, doc.GetMutualInformation("population", "haplogroup")); // consistent

        // GetMutualInformation — population and disease_risk
        var miPopRisk = doc.GetMutualInformation("population", "disease_risk");
        Assert.True(miPopRisk >= 0.0);

        // GetMutualInformation — mtdna_haplogroup and y_haplogroup
        var miMtY = doc.GetMutualInformation("mtdna_haplogroup", "y_haplogroup");
        Assert.True(miMtY >= 0.0);

        // GetUniqueValueCount
        var uvPop = doc.GetUniqueValueCount("population");
        Assert.True(uvPop > 0);
        Assert.True(uvPop <= doc.GetRowCount());
        Assert.Equal(uvPop, doc.GetUniqueValueCount("population")); // consistent

        var uvRisk = doc.GetUniqueValueCount("disease_risk");
        Assert.True(uvRisk > 0);
        Assert.True(uvRisk <= doc.GetRowCount());

        var uvHaplo = doc.GetUniqueValueCount("haplogroup");
        Assert.True(uvHaplo > 0);

        // Uniform column
        var uni = TsvDocument.LoadFile(CreateUniformCategoryTsv());
        Assert.Equal(0.0, uni.GetColumnEntropy("category"), precision: 6);
        Assert.Equal(0.0, uni.GetColumnEntropy("value"), precision: 6);
        Assert.Equal(1, uni.GetUniqueValueCount("category"));

        // SaveToFile
        var out1 = TempFile("dogfood_genomics_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(entPop, loaded.GetColumnEntropy("population"), precision: 6);
        Assert.Equal(uvPop, loaded.GetUniqueValueCount("population"));

        // AddRow and recompute
        loaded.AddRow(new[] { "SAMP013", "European", "T", "41200", "37800", "T2b", "R1b", "Low" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(loaded.GetColumnEntropy("population") >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_genomics_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnEntropy("population") >= 0.0);
        Assert.True(loaded2.GetMutualInformation("population", "haplogroup") >= 0.0);
        Assert.True(loaded2.GetUniqueValueCount("disease_risk") > 0);
    }
}
