// Tests for CsvDocument.GetColumnEntropy, GetColumnCardinality deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R275

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R275: Tests for CsvDocument.GetColumnEntropy, GetColumnCardinality deeper.
/// GetColumnEntropy(colName): returns the Shannon entropy of the value distribution in the column.
/// GetColumnCardinality(colName): returns the count of distinct values in the column.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy zero for uniform;
/// GetColumnEntropy consistent; GetColumnEntropy save-load;
/// GetColumnCardinality no-throw; GetColumnCardinality positive;
/// GetColumnCardinality one for uniform; GetColumnCardinality consistent;
/// GetColumnCardinality save-load; GetColumnCardinality leq RowCount; dogfood pipeline.
/// </summary>
public class CsvR275GetColumnEntropyAndCardinalityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR275GetColumnEntropyAndCardinalityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR275_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,category,value");
        for (int i = 0; i < 4; i++) sb.AppendLine($"R{i:D2},A,{i * 10}");
        for (int i = 4; i < 7; i++) sb.AppendLine($"R{i:D2},B,{i * 10}");
        for (int i = 7; i < 9; i++) sb.AppendLine($"R{i:D2},C,{i * 10}");
        sb.AppendLine("R09,D,90");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,region");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2},North");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnEntropy("category") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("region"), precision: 6);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnEntropy("category"), doc.GetColumnEntropy("category"));
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnEntropy("category");
        var path = TempFile("ent_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnEntropy("category"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCardinality
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCardinality_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCardinality("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCardinality_Positive()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnCardinality("category") > 0);
    }

    [Fact]
    public void GetColumnCardinality_One_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(1, doc.GetColumnCardinality("region"));
    }

    [Fact]
    public void GetColumnCardinality_Four_ForFourValues()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(4, doc.GetColumnCardinality("category"));
    }

    [Fact]
    public void GetColumnCardinality_Leq_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnCardinality("category") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnCardinality_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnCardinality("category"), doc.GetColumnCardinality("category"));
    }

    [Fact]
    public void GetColumnCardinality_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCardinality("category");
        var path = TempFile("card_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnCardinality("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnCardinality_Pipeline()
    {
        // Public Health — UKHSA / NHS: Contact Tracing Programme Data 2024
        // Epidemiological records for infectious disease outbreak investigation
        // Entropy of exposure setting and cardinality of pathogen strain inform cluster analysis

        var path = TempFile("ukhsa_contact_tracing_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("case_id,pathogen,strain,exposure_setting,transmission_route,case_outcome,phe_region,sex,age_group,vaccination_status");

        var rng = new Random(20240115);
        string[] pathogens = { "Influenza_A", "Influenza_B", "RSV", "COVID_19", "Norovirus",
                                "Campylobacter", "Salmonella", "E_coli_O157", "MRSA", "TB" };
        string[] strains = { "H1N1", "H3N2", "B_Yamagata", "BA.2.86", "GII.4_Sydney",
                              "ST21", "Enteritidis", "O157:H7", "USA300", "Beijing" };
        string[] settings = { "Household", "Household", "Household", "Care_Home", "Hospital",
                               "School", "Restaurant", "Workplace", "Community", "Travel" };
        string[] routes = { "Droplet", "Airborne", "Contact", "Foodborne", "Waterborne", "Unknown" };
        string[] outcomes = { "Recovered", "Recovered", "Recovered", "Hospitalised", "Fatal", "Under_Investigation" };
        string[] regions = { "London", "South_East", "East_of_England", "South_West", "West_Midlands",
                              "East_Midlands", "Yorkshire", "North_West", "North_East", "Wales" };
        string[] sexes = { "Male", "Female", "Unknown" };
        string[] ageGrps = { "0-4", "5-14", "15-24", "25-44", "45-64", "65-74", "75+" };
        string[] vaccStatus = { "Unvaccinated", "Partially_Vaccinated", "Fully_Vaccinated", "Boosted", "Unknown" };

        for (int i = 0; i < 450; i++)
        {
            string pathogen = pathogens[rng.Next(pathogens.Length)];
            string strain = strains[rng.Next(strains.Length)];
            string setting = settings[rng.Next(settings.Length)];
            string route = routes[rng.Next(routes.Length)];
            string outcome = outcomes[rng.Next(outcomes.Length)];
            string region = regions[rng.Next(regions.Length)];
            string sex = sexes[rng.Next(sexes.Length)];
            string age = ageGrps[rng.Next(ageGrps.Length)];
            string vacc = vaccStatus[rng.Next(vaccStatus.Length)];
            sb.AppendLine($"CT{i:D6},{pathogen},{strain},{setting},{route},{outcome},{region},{sex},{age},{vacc}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(450, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Pathogen entropy and cardinality (up to 10)
        var pathEnt = doc.GetColumnEntropy("pathogen");
        var pathCard = doc.GetColumnCardinality("pathogen");
        Assert.True(pathEnt >= 0.0);
        Assert.True(pathCard >= 1 && pathCard <= 10);
        Assert.Equal(pathEnt, doc.GetColumnEntropy("pathogen")); // consistent
        Assert.Equal(pathCard, doc.GetColumnCardinality("pathogen")); // consistent

        // Exposure setting entropy and cardinality
        var settingEnt = doc.GetColumnEntropy("exposure_setting");
        var settingCard = doc.GetColumnCardinality("exposure_setting");
        Assert.True(settingEnt >= 0.0);
        Assert.True(settingCard >= 1 && settingCard <= 10);

        // Outcome cardinality (≤6)
        var outcomeCard = doc.GetColumnCardinality("case_outcome");
        Assert.True(outcomeCard >= 1 && outcomeCard <= 6);
        var outcomeEnt = doc.GetColumnEntropy("case_outcome");
        Assert.True(outcomeEnt >= 0.0);

        // Region cardinality (≤10)
        var regionCard = doc.GetColumnCardinality("phe_region");
        Assert.True(regionCard >= 1 && regionCard <= 10);

        // All cardinalities ≤ RowCount
        Assert.True(pathCard <= doc.RowCount);
        Assert.True(settingCard <= doc.RowCount);

        // SaveToFile
        var outPath = TempFile("ukhsa_ct_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(pathEnt, loaded.GetColumnEntropy("pathogen"), precision: 6);
        Assert.Equal(pathCard, loaded.GetColumnCardinality("pathogen"));
        Assert.Equal(settingEnt, loaded.GetColumnEntropy("exposure_setting"), precision: 6);
        Assert.Equal(outcomeCard, loaded.GetColumnCardinality("case_outcome"));
    }
}
