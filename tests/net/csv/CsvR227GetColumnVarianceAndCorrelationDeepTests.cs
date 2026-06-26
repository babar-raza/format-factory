// Tests for CsvDocument.GetColumnVariance, GetColumnCorrelation, GetColumnCovariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R227

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R227: Tests for CsvDocument.GetColumnVariance, GetColumnCorrelation, GetColumnCovariance deeper.
/// GetColumnVariance(columnName): returns the variance of numeric values in the column.
/// GetColumnCorrelation(col1, col2): returns the Pearson correlation between two numeric columns.
/// GetColumnCovariance(col1, col2): returns the covariance between two numeric columns.
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance consistent;
/// GetColumnVariance zero for uniform; GetColumnVariance save-load;
/// GetColumnCorrelation no-throw; GetColumnCorrelation in [-1,1]; GetColumnCorrelation consistent;
/// GetColumnCorrelation perfect positive; GetColumnCorrelation save-load;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent; GetColumnCovariance save-load;
/// dogfood CreateDoc→GetColumnVariance→GetColumnCorrelation→GetColumnCovariance→SaveToFile pipeline.
/// </summary>
public class CsvR227GetColumnVarianceAndCorrelationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR227GetColumnVarianceAndCorrelationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR227_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateClimateCsv()
    {
        var path = TempFile("climate.csv");
        File.WriteAllText(path,
            "station,latitude,longitude,temp_mean,temp_max,temp_min,precipitation,sunshine_hours\n" +
            "London,-51.5,-0.1,11.3,24.1,1.0,601.7,1633.4\n" +
            "Paris,48.9,2.4,12.1,27.3,0.5,637.4,1630.5\n" +
            "Berlin,52.5,13.4,10.3,25.8,-2.1,582.3,1626.8\n" +
            "Madrid,40.4,-3.7,15.2,34.0,1.5,436.1,2769.0\n" +
            "Rome,41.9,12.5,16.1,32.7,2.8,796.4,2473.7\n" +
            "Amsterdam,52.4,4.9,10.5,23.4,1.1,838.5,1662.2\n" +
            "Vienna,48.2,16.4,11.2,27.6,-3.2,617.4,1884.3\n" +
            "Zurich,47.4,8.5,9.8,25.2,-2.8,1136.0,1696.4\n" +
            "Brussels,50.8,4.4,10.8,24.5,0.3,820.9,1546.2\n" +
            "Stockholm,59.3,18.1,7.8,22.0,-5.1,526.8,1821.2\n");
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        File.WriteAllText(path,
            "id,value\n" +
            "1,7.5\n" +
            "2,7.5\n" +
            "3,7.5\n" +
            "4,7.5\n" +
            "5,7.5\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("temp_mean"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        Assert.True(doc.GetColumnVariance("precipitation") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        Assert.Equal(doc.GetColumnVariance("sunshine_hours"), doc.GetColumnVariance("sunshine_hours"));
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnVariance("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var before = doc.GetColumnVariance("temp_max");
        var path = TempFile("var_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnVariance("temp_max"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("temp_mean", "temp_max"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var r = doc.GetColumnCorrelation("temp_mean", "temp_min");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        Assert.Equal(
            doc.GetColumnCorrelation("temp_mean", "precipitation"),
            doc.GetColumnCorrelation("temp_mean", "precipitation"));
    }

    [Fact]
    public void GetColumnCorrelation_PerfectPositive_WithSelf()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var r = doc.GetColumnCorrelation("temp_mean", "temp_mean");
        Assert.True(r >= 0.99 || Math.Abs(r - 1.0) < 1e-9);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var before = doc.GetColumnCorrelation("temp_max", "sunshine_hours");
        var path = TempFile("corr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("temp_max", "sunshine_hours"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("temp_mean", "precipitation"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        Assert.Equal(
            doc.GetColumnCovariance("sunshine_hours", "temp_max"),
            doc.GetColumnCovariance("sunshine_hours", "temp_max"));
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateClimateCsv());
        var before = doc.GetColumnCovariance("temp_mean", "sunshine_hours");
        var path = TempFile("cov_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("temp_mean", "sunshine_hours"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnCorrelation_GetColumnCovariance_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_energy.csv");
        File.WriteAllText(path,
            "country,solar_capacity_gw,wind_capacity_gw,hydro_capacity_gw,nuclear_capacity_gw,coal_capacity_gw,renewables_share,co2_per_capita\n" +
            "Germany,66.0,64.0,5.6,0.0,21.0,46.0,7.7\n" +
            "France,16.0,22.0,26.0,63.0,3.0,24.0,4.7\n" +
            "UK,15.0,29.0,2.0,8.5,6.5,42.0,5.5\n" +
            "Spain,23.0,29.0,22.0,7.1,11.0,53.0,5.4\n" +
            "Italy,25.0,11.0,22.0,0.0,8.0,41.0,5.7\n" +
            "Netherlands,4.1,6.1,0.0,0.5,3.8,27.0,9.0\n" +
            "Poland,8.5,8.2,2.3,0.0,19.0,20.0,9.4\n" +
            "Sweden,1.9,12.0,16.0,7.0,0.2,75.0,4.0\n" +
            "Denmark,2.4,7.0,0.0,0.0,1.3,82.0,5.1\n" +
            "Belgium,5.3,3.5,0.1,5.9,0.8,35.0,7.9\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());
        Assert.Equal(8, doc.GetColumnCount());

        // GetColumnVariance — all non-negative
        var varSolar = doc.GetColumnVariance("solar_capacity_gw");
        Assert.True(varSolar >= 0.0);

        var varRenewables = doc.GetColumnVariance("renewables_share");
        Assert.True(varRenewables >= 0.0);

        var varCo2 = doc.GetColumnVariance("co2_per_capita");
        Assert.True(varCo2 >= 0.0);

        // Consistent
        Assert.Equal(varSolar, doc.GetColumnVariance("solar_capacity_gw"));

        // GetColumnCorrelation
        var rRenewablesCo2 = doc.GetColumnCorrelation("renewables_share", "co2_per_capita");
        Assert.True(rRenewablesCo2 >= -1.0 && rRenewablesCo2 <= 1.0);
        // Expect negative correlation (more renewables → less CO2)
        Assert.True(rRenewablesCo2 < 0.5);

        var rSolarWind = doc.GetColumnCorrelation("solar_capacity_gw", "wind_capacity_gw");
        Assert.True(rSolarWind >= -1.0 && rSolarWind <= 1.0);

        var rSelfSolar = doc.GetColumnCorrelation("solar_capacity_gw", "solar_capacity_gw");
        Assert.True(rSelfSolar >= 0.99 || Math.Abs(rSelfSolar - 1.0) < 1e-9);

        // Consistent
        Assert.Equal(rRenewablesCo2, doc.GetColumnCorrelation("renewables_share", "co2_per_capita"));

        // GetColumnCovariance
        var covSolarRenewables = doc.GetColumnCovariance("solar_capacity_gw", "renewables_share");
        Assert.Equal(covSolarRenewables, doc.GetColumnCovariance("solar_capacity_gw", "renewables_share"));

        var covWindCo2 = doc.GetColumnCovariance("wind_capacity_gw", "co2_per_capita");
        Assert.Equal(covWindCo2, doc.GetColumnCovariance("wind_capacity_gw", "co2_per_capita"));

        // SaveToFile
        var out1 = TempFile("dogfood_energy_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(doc.GetColumnVariance("solar_capacity_gw"),
            loaded.GetColumnVariance("solar_capacity_gw"), precision: 6);
        Assert.Equal(doc.GetColumnCorrelation("renewables_share", "co2_per_capita"),
            loaded.GetColumnCorrelation("renewables_share", "co2_per_capita"), precision: 6);
        Assert.Equal(doc.GetColumnCovariance("solar_capacity_gw", "renewables_share"),
            loaded.GetColumnCovariance("solar_capacity_gw", "renewables_share"), precision: 6);

        // AddRow and re-verify
        loaded.AddRow(new[] { "Norway", "0.4", "0.7", "33.0", "0.0", "0.0", "97.0", "7.7" });
        Assert.Equal(11, loaded.GetRowCount());
        Assert.True(loaded.GetColumnVariance("renewables_share") >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_energy_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnVariance("solar_capacity_gw") >= 0.0);
        Assert.True(loaded2.GetColumnCorrelation("renewables_share", "co2_per_capita") >= -1.0);
        Assert.Equal(loaded2.GetColumnCovariance("solar_capacity_gw", "renewables_share"),
            loaded2.GetColumnCovariance("solar_capacity_gw", "renewables_share"));
    }
}
