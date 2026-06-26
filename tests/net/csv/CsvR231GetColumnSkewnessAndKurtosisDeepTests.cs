// Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetNormalityScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R231

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R231: Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis, GetNormalityScore deeper.
/// GetColumnSkewness(columnName): returns the skewness of the numeric column.
/// GetColumnKurtosis(columnName): returns the excess kurtosis of the numeric column.
/// GetNormalityScore(columnName): returns a normality score in [0,1] (1 = perfectly normal).
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness zero for symmetric;
/// GetColumnSkewness consistent; GetColumnSkewness save-load;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite; GetColumnKurtosis consistent;
/// GetColumnKurtosis save-load;
/// GetNormalityScore no-throw; GetNormalityScore in range; GetNormalityScore consistent;
/// GetNormalityScore save-load;
/// dogfood CreateDoc→GetColumnSkewness→GetColumnKurtosis→GetNormalityScore→SaveToFile pipeline.
/// </summary>
public class CsvR231GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR231GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR231_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateIncomeDistributionCsv()
    {
        var path = TempFile("income.csv");
        File.WriteAllText(path,
            "household_id,income_k,savings_rate,wealth_k,education_years,expenditure_k\n" +
            "H001,35,0.08,12,12,32\n" +
            "H002,52,0.12,28,14,46\n" +
            "H003,78,0.18,95,16,64\n" +
            "H004,125,0.22,280,18,98\n" +
            "H005,42,0.10,18,13,38\n" +
            "H006,68,0.15,62,15,58\n" +
            "H007,1850,0.45,8200,20,1020\n" + // high earner — strong right skew
            "H008,48,0.11,22,13,43\n" +
            "H009,95,0.20,145,17,76\n" +
            "H010,60,0.14,48,15,52\n" +
            "H011,38,0.09,14,12,35\n" +
            "H012,112,0.21,230,18,88\n");
        return path;
    }

    private string CreateSymmetricCsv()
    {
        // Perfectly symmetric around 100
        var path = TempFile("symmetric.csv");
        File.WriteAllText(path,
            "id,value\n" +
            "1,70\n" +
            "2,80\n" +
            "3,90\n" +
            "4,100\n" +
            "5,110\n" +
            "6,120\n" +
            "7,130\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("income_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        Assert.True(double.IsFinite(doc.GetColumnSkewness("income_k")));
    }

    [Fact]
    public void GetColumnSkewness_Zero_ForSymmetric()
    {
        var doc = CsvDocument.LoadFile(CreateSymmetricCsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("value"), precision: 6);
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        Assert.Equal(doc.GetColumnSkewness("savings_rate"), doc.GetColumnSkewness("savings_rate"));
    }

    [Fact]
    public void GetColumnSkewness_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var before = doc.GetColumnSkewness("income_k");
        var path = TempFile("sk_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnSkewness("income_k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("income_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        Assert.True(double.IsFinite(doc.GetColumnKurtosis("wealth_k")));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        Assert.Equal(doc.GetColumnKurtosis("income_k"), doc.GetColumnKurtosis("income_k"));
    }

    [Fact]
    public void GetColumnKurtosis_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var before = doc.GetColumnKurtosis("income_k");
        var path = TempFile("ku_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnKurtosis("income_k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetNormalityScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNormalityScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var ex = Record.Exception(() => doc.GetNormalityScore("expenditure_k"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNormalityScore_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var score = doc.GetNormalityScore("savings_rate");
        Assert.True(score >= 0.0);
        Assert.True(score <= 1.0);
    }

    [Fact]
    public void GetNormalityScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        Assert.Equal(doc.GetNormalityScore("income_k"), doc.GetNormalityScore("income_k"));
    }

    [Fact]
    public void GetNormalityScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateIncomeDistributionCsv());
        var before = doc.GetNormalityScore("expenditure_k");
        var path = TempFile("ns_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNormalityScore("expenditure_k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_GetNormalityScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_emissions.csv");
        File.WriteAllText(path,
            "country,gdp_per_capita,co2_per_capita,renewable_share,energy_intensity,forest_cover,ev_penetration\n" +
            "Norway,89000,6.2,0.98,0.08,33.2,0.87\n" +
            "Sweden,55000,3.8,0.65,0.10,68.9,0.42\n" +
            "Germany,50000,7.2,0.46,0.12,32.8,0.25\n" +
            "France,43000,4.5,0.25,0.11,31.4,0.22\n" +
            "UK,46000,4.8,0.42,0.09,13.2,0.28\n" +
            "USA,65000,14.2,0.22,0.16,33.8,0.09\n" +
            "China,12000,7.4,0.30,0.20,23.0,0.06\n" +
            "India,2500,1.8,0.22,0.25,24.0,0.01\n" +
            "Japan,40000,8.5,0.21,0.13,68.4,0.04\n" +
            "Australia,55000,15.2,0.32,0.18,16.8,0.05\n" +
            "Canada,52000,14.8,0.66,0.15,38.2,0.07\n" +
            "Brazil,9000,2.2,0.83,0.12,59.2,0.02\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnSkewness
        var skewGdp = doc.GetColumnSkewness("gdp_per_capita");
        Assert.True(double.IsFinite(skewGdp));
        Assert.Equal(skewGdp, doc.GetColumnSkewness("gdp_per_capita")); // consistent

        var skewCo2 = doc.GetColumnSkewness("co2_per_capita");
        Assert.True(double.IsFinite(skewCo2));

        var skewRenew = doc.GetColumnSkewness("renewable_share");
        Assert.True(double.IsFinite(skewRenew));

        // GetColumnKurtosis
        var kurtGdp = doc.GetColumnKurtosis("gdp_per_capita");
        Assert.True(double.IsFinite(kurtGdp));
        Assert.Equal(kurtGdp, doc.GetColumnKurtosis("gdp_per_capita")); // consistent

        var kurtEnergy = doc.GetColumnKurtosis("energy_intensity");
        Assert.True(double.IsFinite(kurtEnergy));

        var kurtForest = doc.GetColumnKurtosis("forest_cover");
        Assert.True(double.IsFinite(kurtForest));

        // GetNormalityScore — all columns in range
        string[] cols = { "gdp_per_capita", "co2_per_capita", "renewable_share", "energy_intensity", "forest_cover", "ev_penetration" };
        foreach (var col in cols)
        {
            var score = doc.GetNormalityScore(col);
            Assert.True(score >= 0.0, $"{col} normality score should be >= 0");
            Assert.True(score <= 1.0, $"{col} normality score should be <= 1");
        }

        // SaveToFile
        var out1 = TempFile("dogfood_emissions_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(skewGdp, loaded.GetColumnSkewness("gdp_per_capita"), precision: 6);
        Assert.Equal(kurtGdp, loaded.GetColumnKurtosis("gdp_per_capita"), precision: 6);

        // Symmetric test
        var sym = CsvDocument.LoadFile(CreateSymmetricCsv());
        Assert.Equal(0.0, sym.GetColumnSkewness("value"), precision: 6);
        Assert.True(double.IsFinite(sym.GetColumnKurtosis("value")));
        Assert.True(sym.GetNormalityScore("value") >= 0.0);

        // AddRow and recompute
        loaded.AddRow(new[] { "Netherlands", "54000", "8.8", "0.33", "0.11", "11.2", "0.30" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(double.IsFinite(loaded.GetColumnSkewness("gdp_per_capita")));

        // Final save
        var out2 = TempFile("dogfood_emissions_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(double.IsFinite(loaded2.GetColumnSkewness("co2_per_capita")));
        Assert.True(double.IsFinite(loaded2.GetColumnKurtosis("renewable_share")));
        Assert.True(loaded2.GetNormalityScore("energy_intensity") >= 0.0);
    }
}
