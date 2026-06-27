// Tests for CsvDocument.GetColumnVariance, GetColumnStdDev, GetCoefficientOfVariation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R234

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R234: Tests for CsvDocument.GetColumnVariance, GetColumnStdDev, GetCoefficientOfVariation deeper.
/// GetColumnVariance(columnName): returns the variance of numeric values in the column.
/// GetColumnStdDev(columnName): returns the standard deviation of numeric values in the column.
/// GetCoefficientOfVariation(columnName): returns the CV (stdDev/mean * 100) for the column.
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance consistent;
/// GetColumnVariance zero for uniform; GetColumnVariance save-load;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev consistent;
/// GetColumnStdDev zero for uniform; GetColumnStdDev save-load;
/// GetCoefficientOfVariation no-throw; GetCoefficientOfVariation non-negative; GetCoefficientOfVariation consistent;
/// GetCoefficientOfVariation save-load;
/// dogfood CreateDoc→GetColumnVariance→GetColumnStdDev→GetCoefficientOfVariation→SaveToFile pipeline.
/// </summary>
public class CsvR234GetColumnVarianceAndCoefficientOfVariationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR234GetColumnVarianceAndCoefficientOfVariationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR234_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateWeatherCsv()
    {
        var path = TempFile("weather.csv");
        File.WriteAllText(path,
            "station,month,temp_max,temp_min,precipitation_mm,sunshine_hours,wind_speed_kmh\n" +
            "London,Jan,8.4,3.2,55.2,1.8,18.5\n" +
            "London,Feb,9.1,3.8,40.8,2.4,17.2\n" +
            "London,Mar,11.2,5.1,42.5,3.8,16.8\n" +
            "London,Apr,14.5,7.3,45.8,5.6,14.2\n" +
            "London,May,17.8,9.8,49.2,6.8,12.5\n" +
            "London,Jun,21.2,12.6,45.8,7.4,11.8\n" +
            "London,Jul,23.5,14.8,38.2,6.8,10.5\n" +
            "London,Aug,23.1,14.5,42.5,6.2,11.2\n" +
            "London,Sep,19.8,11.8,48.5,4.8,13.5\n" +
            "London,Oct,15.2,8.5,68.4,3.2,15.8\n" +
            "London,Nov,11.4,5.8,62.8,1.6,18.2\n" +
            "London,Dec,8.8,3.5,58.5,1.4,19.5\n");
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        File.WriteAllText(path,
            "id,value\n1,50\n2,50\n3,50\n4,50\n5,50\n6,50\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("temp_max"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.True(doc.GetColumnVariance("precipitation_mm") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.Equal(doc.GetColumnVariance("temp_max"), doc.GetColumnVariance("temp_max"));
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
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var before = doc.GetColumnVariance("sunshine_hours");
        var path = TempFile("var_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnVariance("sunshine_hours"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("temp_max"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.True(doc.GetColumnStdDev("wind_speed_kmh") >= 0.0);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.Equal(doc.GetColumnStdDev("precipitation_mm"), doc.GetColumnStdDev("precipitation_mm"));
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var before = doc.GetColumnStdDev("temp_min");
        var path = TempFile("std_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnStdDev("temp_min"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetCoefficientOfVariation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCoefficientOfVariation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var ex = Record.Exception(() => doc.GetCoefficientOfVariation("temp_max"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCoefficientOfVariation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.True(doc.GetCoefficientOfVariation("precipitation_mm") >= 0.0);
    }

    [Fact]
    public void GetCoefficientOfVariation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        Assert.Equal(doc.GetCoefficientOfVariation("sunshine_hours"), doc.GetCoefficientOfVariation("sunshine_hours"));
    }

    [Fact]
    public void GetCoefficientOfVariation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateWeatherCsv());
        var before = doc.GetCoefficientOfVariation("wind_speed_kmh");
        var path = TempFile("cv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCoefficientOfVariation("wind_speed_kmh"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnStdDev_GetCoefficientOfVariation_SaveToFile_Pipeline()
    {
        // Macroeconomic indicators — 12-country OECD panel dataset
        var path = TempFile("dogfood_macro.csv");
        File.WriteAllText(path,
            "country,gdp_growth_pct,unemployment_pct,cpi_inflation,current_account_gdp,debt_gdp,budget_balance_gdp\n" +
            "United States,2.5,3.8,3.2,-3.2,122.5,-5.4\n" +
            "Germany,0.2,3.1,2.8,6.8,66.5,-2.2\n" +
            "France,1.1,7.4,3.5,-1.2,111.8,-4.8\n" +
            "United Kingdom,0.4,4.2,4.1,-3.8,104.5,-4.5\n" +
            "Japan,-0.1,2.6,2.5,3.8,258.4,-3.8\n" +
            "Canada,1.2,5.8,3.1,-1.5,107.2,-2.8\n" +
            "Australia,2.1,3.9,3.8,-2.4,48.5,-1.4\n" +
            "South Korea,2.6,2.8,2.4,3.2,55.8,-2.1\n" +
            "Netherlands,1.5,3.6,3.8,10.2,51.4,-1.8\n" +
            "Sweden,0.5,8.2,2.5,5.8,36.8,0.2\n" +
            "Switzerland,0.7,2.2,1.8,8.4,42.5,1.8\n" +
            "Norway,1.8,3.5,4.2,14.8,38.5,12.5\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnVariance — GDP growth spread
        var varGdp = doc.GetColumnVariance("gdp_growth_pct");
        Assert.True(varGdp >= 0.0);
        Assert.Equal(varGdp, doc.GetColumnVariance("gdp_growth_pct")); // consistent

        var varUnemployment = doc.GetColumnVariance("unemployment_pct");
        Assert.True(varUnemployment >= 0.0);

        var varDebt = doc.GetColumnVariance("debt_gdp");
        Assert.True(varDebt >= 0.0);

        // GetColumnStdDev — CPI inflation spread
        var stdCpi = doc.GetColumnStdDev("cpi_inflation");
        Assert.True(stdCpi >= 0.0);
        Assert.Equal(stdCpi, doc.GetColumnStdDev("cpi_inflation")); // consistent

        var stdBudget = doc.GetColumnStdDev("budget_balance_gdp");
        Assert.True(stdBudget >= 0.0);

        // stdDev^2 ≈ variance for same column
        var varCpi = doc.GetColumnVariance("cpi_inflation");
        Assert.True(Math.Abs(stdCpi * stdCpi - varCpi) < 0.1);

        // GetCoefficientOfVariation — relative variability
        var cvCurrentAccount = doc.GetCoefficientOfVariation("current_account_gdp");
        Assert.True(cvCurrentAccount >= 0.0);
        Assert.Equal(cvCurrentAccount, doc.GetCoefficientOfVariation("current_account_gdp")); // consistent

        var cvDebt = doc.GetCoefficientOfVariation("debt_gdp");
        Assert.True(cvDebt >= 0.0);

        // SaveToFile
        var out1 = TempFile("dogfood_macro_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(varGdp, loaded.GetColumnVariance("gdp_growth_pct"), precision: 4);
        Assert.Equal(stdCpi, loaded.GetColumnStdDev("cpi_inflation"), precision: 4);
        Assert.Equal(cvCurrentAccount, loaded.GetCoefficientOfVariation("current_account_gdp"), precision: 4);

        // AddRow — emerging market addition
        loaded.AddRow(new[] { "Brazil", "2.9", "7.8", "4.6", "-1.8", "88.5", "-6.2" });
        Assert.Equal(13, loaded.GetRowCount());

        // Variance should remain non-negative after row addition
        Assert.True(loaded.GetColumnVariance("gdp_growth_pct") >= 0.0);

        // Uniform column check
        var uniformDoc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, uniformDoc.GetColumnVariance("value"), precision: 6);
        Assert.Equal(0.0, uniformDoc.GetColumnStdDev("value"), precision: 6);

        // Final save
        var out2 = TempFile("dogfood_macro_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnVariance("debt_gdp") >= 0.0);
        Assert.True(loaded2.GetColumnStdDev("unemployment_pct") >= 0.0);
        Assert.True(loaded2.GetCoefficientOfVariation("cpi_inflation") >= 0.0);
    }
}
