// Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance, GetLinearRegressionSlope deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R235

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R235: Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance, GetLinearRegressionSlope deeper.
/// GetColumnCorrelation(col1, col2): returns the Pearson correlation coefficient [-1,1].
/// GetColumnCovariance(col1, col2): returns the covariance of the two columns.
/// GetLinearRegressionSlope(xCol, yCol): returns the OLS regression slope of y on x.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in range; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical; GetColumnCorrelation save-load;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent; GetColumnCovariance save-load;
/// GetLinearRegressionSlope no-throw; GetLinearRegressionSlope consistent; GetLinearRegressionSlope save-load;
/// dogfood CreateDoc→GetColumnCorrelation→GetColumnCovariance→GetLinearRegressionSlope→SaveToFile pipeline.
/// </summary>
public class CsvR235GetColumnCorrelationAndLinearRegressionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR235GetColumnCorrelationAndLinearRegressionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR235_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEducationCsv()
    {
        var path = TempFile("education.csv");
        File.WriteAllText(path,
            "school_id,avg_score,pupil_teacher_ratio,spending_per_pupil,attendance_pct,poverty_index\n" +
            "SCH001,72.5,18.2,8500,94.2,42.5\n" +
            "SCH002,85.8,14.5,11200,97.5,18.2\n" +
            "SCH003,61.2,22.8,6800,88.5,65.8\n" +
            "SCH004,78.4,16.8,9800,95.8,28.4\n" +
            "SCH005,58.6,24.5,6200,85.2,72.5\n" +
            "SCH006,91.2,12.2,13500,98.8,8.5\n" +
            "SCH007,69.8,19.5,7800,92.4,48.2\n" +
            "SCH008,82.5,15.2,10500,96.8,22.5\n" +
            "SCH009,55.4,26.2,5800,83.5,78.4\n" +
            "SCH010,88.6,13.5,12200,98.2,12.8\n" +
            "SCH011,75.2,17.5,9200,95.2,35.6\n" +
            "SCH012,64.8,21.2,7200,90.4,58.2\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("avg_score", "spending_per_pupil"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var corr = doc.GetColumnCorrelation("avg_score", "pupil_teacher_ratio");
        Assert.True(corr >= -1.0);
        Assert.True(corr <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        Assert.Equal(
            doc.GetColumnCorrelation("avg_score", "poverty_index"),
            doc.GetColumnCorrelation("avg_score", "poverty_index"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdentical()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        Assert.Equal(1.0, doc.GetColumnCorrelation("avg_score", "avg_score"), precision: 6);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var before = doc.GetColumnCorrelation("spending_per_pupil", "avg_score");
        var path = TempFile("corr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("spending_per_pupil", "avg_score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("avg_score", "spending_per_pupil"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        Assert.Equal(
            doc.GetColumnCovariance("avg_score", "poverty_index"),
            doc.GetColumnCovariance("avg_score", "poverty_index"));
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var before = doc.GetColumnCovariance("attendance_pct", "avg_score");
        var path = TempFile("cov_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("attendance_pct", "avg_score"), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionSlope
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionSlope_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionSlope("spending_per_pupil", "avg_score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionSlope_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        Assert.Equal(
            doc.GetLinearRegressionSlope("poverty_index", "avg_score"),
            doc.GetLinearRegressionSlope("poverty_index", "avg_score"));
    }

    [Fact]
    public void GetLinearRegressionSlope_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateEducationCsv());
        var before = doc.GetLinearRegressionSlope("pupil_teacher_ratio", "avg_score");
        var path = TempFile("slope_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionSlope("pupil_teacher_ratio", "avg_score"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_GetLinearRegressionSlope_SaveToFile_Pipeline()
    {
        // Environmental economics — 12-country carbon emissions and economic indicators
        var path = TempFile("dogfood_emissions.csv");
        File.WriteAllText(path,
            "country,co2_per_capita,gdp_per_capita_k,renewable_pct,carbon_tax_usd,energy_intensity,forest_coverage_pct\n" +
            "Norway,6.8,89.5,98.2,52,85.2,33.2\n" +
            "Sweden,3.9,55.8,65.8,130,72.5,68.5\n" +
            "Finland,6.2,48.5,45.2,85,92.4,73.2\n" +
            "Denmark,4.8,62.5,62.5,27,80.5,14.8\n" +
            "Germany,8.4,52.8,46.5,25,92.8,32.5\n" +
            "France,4.5,44.8,24.8,45,82.5,31.2\n" +
            "United Kingdom,5.2,46.5,42.5,20,85.8,13.2\n" +
            "Netherlands,8.9,58.2,38.5,30,112.5,11.5\n" +
            "Belgium,8.1,48.5,32.5,0,108.2,22.8\n" +
            "Austria,6.4,52.2,78.5,25,98.5,47.2\n" +
            "Switzerland,3.8,87.5,62.5,0,78.5,31.5\n" +
            "Canada,14.8,55.8,68.5,50,148.5,38.5\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnCorrelation — GDP per capita vs CO2 per capita
        var corrGdpCo2 = doc.GetColumnCorrelation("gdp_per_capita_k", "co2_per_capita");
        Assert.True(corrGdpCo2 >= -1.0);
        Assert.True(corrGdpCo2 <= 1.0);
        Assert.Equal(corrGdpCo2, doc.GetColumnCorrelation("gdp_per_capita_k", "co2_per_capita")); // consistent

        // Renewable % vs CO2 (should be negative correlation)
        var corrRenewCo2 = doc.GetColumnCorrelation("renewable_pct", "co2_per_capita");
        Assert.True(corrRenewCo2 >= -1.0);
        Assert.True(corrRenewCo2 <= 1.0);

        // Self-correlation
        Assert.Equal(1.0, doc.GetColumnCorrelation("co2_per_capita", "co2_per_capita"), precision: 6);

        // Energy intensity vs CO2 (should be positive)
        var corrEnerCo2 = doc.GetColumnCorrelation("energy_intensity", "co2_per_capita");
        Assert.True(corrEnerCo2 >= -1.0);
        Assert.True(corrEnerCo2 <= 1.0);

        // GetColumnCovariance
        var covGdpCo2 = doc.GetColumnCovariance("gdp_per_capita_k", "co2_per_capita");
        Assert.Equal(covGdpCo2, doc.GetColumnCovariance("gdp_per_capita_k", "co2_per_capita")); // consistent

        var covRenewCarbonTax = doc.GetColumnCovariance("renewable_pct", "carbon_tax_usd");
        Assert.Equal(covRenewCarbonTax, doc.GetColumnCovariance("renewable_pct", "carbon_tax_usd"));

        // GetLinearRegressionSlope — energy intensity predicting CO2
        var slopeEnerCo2 = doc.GetLinearRegressionSlope("energy_intensity", "co2_per_capita");
        Assert.Equal(slopeEnerCo2, doc.GetLinearRegressionSlope("energy_intensity", "co2_per_capita")); // consistent

        var slopeRenewCo2 = doc.GetLinearRegressionSlope("renewable_pct", "co2_per_capita");
        Assert.Equal(slopeRenewCo2, doc.GetLinearRegressionSlope("renewable_pct", "co2_per_capita"));

        // SaveToFile
        var out1 = TempFile("dogfood_emissions_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(corrGdpCo2, loaded.GetColumnCorrelation("gdp_per_capita_k", "co2_per_capita"), precision: 6);
        Assert.Equal(covGdpCo2, loaded.GetColumnCovariance("gdp_per_capita_k", "co2_per_capita"), precision: 2);
        Assert.Equal(slopeEnerCo2, loaded.GetLinearRegressionSlope("energy_intensity", "co2_per_capita"), precision: 4);

        // AddRow — additional country
        loaded.AddRow(new[] { "Japan", "8.5", "43.2", "22.5", "0", "105.4", "67.2" });
        Assert.Equal(13, loaded.GetRowCount());

        // Metrics still valid after row addition
        var newCorr = loaded.GetColumnCorrelation("gdp_per_capita_k", "co2_per_capita");
        Assert.True(newCorr >= -1.0);
        Assert.True(newCorr <= 1.0);

        // Final save
        var out2 = TempFile("dogfood_emissions_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnCorrelation("renewable_pct", "co2_per_capita") >= -1.0);
        Assert.True(loaded2.GetColumnCorrelation("renewable_pct", "co2_per_capita") <= 1.0);
        Assert.Equal(1.0, loaded2.GetColumnCorrelation("energy_intensity", "energy_intensity"), precision: 6);
    }
}
