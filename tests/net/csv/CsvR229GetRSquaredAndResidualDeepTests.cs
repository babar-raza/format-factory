// Tests for CsvDocument.GetRSquared, GetResidualStdDev, GetMeanAbsoluteError deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R229

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R229: Tests for CsvDocument.GetRSquared, GetResidualStdDev, GetMeanAbsoluteError deeper.
/// GetRSquared(xCol, yCol): returns the coefficient of determination (R²) for the regression.
/// GetResidualStdDev(xCol, yCol): returns the standard deviation of regression residuals.
/// GetMeanAbsoluteError(xCol, yCol): returns the mean absolute error of the regression.
/// Covers: GetRSquared no-throw; GetRSquared in [0,1]; GetRSquared consistent;
/// GetRSquared perfect for linear data; GetRSquared save-load;
/// GetResidualStdDev no-throw; GetResidualStdDev non-negative; GetResidualStdDev consistent;
/// GetResidualStdDev zero for perfect fit; GetResidualStdDev save-load;
/// GetMeanAbsoluteError no-throw; GetMeanAbsoluteError non-negative; GetMeanAbsoluteError consistent;
/// GetMeanAbsoluteError save-load;
/// dogfood CreateDoc→GetRSquared→GetResidualStdDev→GetMeanAbsoluteError→SaveToFile pipeline.
/// </summary>
public class CsvR229GetRSquaredAndResidualDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR229GetRSquaredAndResidualDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR229_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHealthCsv()
    {
        var path = TempFile("health.csv");
        File.WriteAllText(path,
            "country,health_expenditure_pct_gdp,life_expectancy,infant_mortality_per_1k,obesity_rate_pct,physician_per_1k\n" +
            "USA,16.8,78.9,5.4,36.2,2.6\n" +
            "Germany,11.7,81.3,3.1,23.6,4.2\n" +
            "France,11.1,82.5,3.3,21.6,3.2\n" +
            "UK,9.9,81.4,3.7,27.8,3.0\n" +
            "Japan,10.9,84.3,1.9,4.3,2.5\n" +
            "Canada,10.8,82.2,4.5,26.8,2.7\n" +
            "Australia,9.9,83.4,3.1,29.0,3.8\n" +
            "Sweden,10.9,82.8,2.1,20.6,4.3\n" +
            "Switzerland,11.3,83.8,3.5,19.5,4.3\n" +
            "Netherlands,10.0,82.3,3.8,20.4,3.6\n" +
            "Spain,9.1,83.5,2.7,23.8,4.1\n" +
            "Italy,8.9,83.4,2.7,19.9,4.0\n");
        return path;
    }

    private string CreateLinearCsv()
    {
        // Perfect linear: y = 3*x + 1
        var path = TempFile("linear.csv");
        File.WriteAllText(path,
            "x,y\n" +
            "1,4\n" +
            "2,7\n" +
            "3,10\n" +
            "4,13\n" +
            "5,16\n" +
            "6,19\n" +
            "7,22\n" +
            "8,25\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRSquared
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRSquared_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var ex = Record.Exception(() => doc.GetRSquared("health_expenditure_pct_gdp", "life_expectancy"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRSquared_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var r2 = doc.GetRSquared("health_expenditure_pct_gdp", "life_expectancy");
        Assert.True(r2 >= 0.0 && r2 <= 1.0);
    }

    [Fact]
    public void GetRSquared_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        Assert.Equal(
            doc.GetRSquared("health_expenditure_pct_gdp", "infant_mortality_per_1k"),
            doc.GetRSquared("health_expenditure_pct_gdp", "infant_mortality_per_1k"));
    }

    [Fact]
    public void GetRSquared_PerfectFit_ForLinearData()
    {
        var doc = CsvDocument.LoadFile(CreateLinearCsv());
        var r2 = doc.GetRSquared("x", "y");
        Assert.True(r2 >= 0.999);
    }

    [Fact]
    public void GetRSquared_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var before = doc.GetRSquared("health_expenditure_pct_gdp", "life_expectancy");
        var path = TempFile("r2_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRSquared("health_expenditure_pct_gdp", "life_expectancy"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetResidualStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetResidualStdDev_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var ex = Record.Exception(() => doc.GetResidualStdDev("health_expenditure_pct_gdp", "life_expectancy"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetResidualStdDev_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        Assert.True(doc.GetResidualStdDev("health_expenditure_pct_gdp", "life_expectancy") >= 0.0);
    }

    [Fact]
    public void GetResidualStdDev_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        Assert.Equal(
            doc.GetResidualStdDev("physician_per_1k", "life_expectancy"),
            doc.GetResidualStdDev("physician_per_1k", "life_expectancy"));
    }

    [Fact]
    public void GetResidualStdDev_Zero_ForPerfectFit()
    {
        var doc = CsvDocument.LoadFile(CreateLinearCsv());
        var stdDev = doc.GetResidualStdDev("x", "y");
        Assert.True(stdDev < 1e-9 || stdDev == 0.0);
    }

    [Fact]
    public void GetResidualStdDev_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var before = doc.GetResidualStdDev("health_expenditure_pct_gdp", "life_expectancy");
        var path = TempFile("rsd_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetResidualStdDev("health_expenditure_pct_gdp", "life_expectancy"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetMeanAbsoluteError
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMeanAbsoluteError_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var ex = Record.Exception(() => doc.GetMeanAbsoluteError("health_expenditure_pct_gdp", "life_expectancy"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMeanAbsoluteError_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        Assert.True(doc.GetMeanAbsoluteError("health_expenditure_pct_gdp", "life_expectancy") >= 0.0);
    }

    [Fact]
    public void GetMeanAbsoluteError_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        Assert.Equal(
            doc.GetMeanAbsoluteError("physician_per_1k", "life_expectancy"),
            doc.GetMeanAbsoluteError("physician_per_1k", "life_expectancy"));
    }

    [Fact]
    public void GetMeanAbsoluteError_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateHealthCsv());
        var before = doc.GetMeanAbsoluteError("health_expenditure_pct_gdp", "infant_mortality_per_1k");
        var path = TempFile("mae_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMeanAbsoluteError("health_expenditure_pct_gdp", "infant_mortality_per_1k"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRSquared_GetResidualStdDev_GetMeanAbsoluteError_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_urbanisation.csv");
        File.WriteAllText(path,
            "city_region,urban_pop_pct,internet_penetration_pct,co2_per_capita,public_transport_share,green_space_pct,wellbeing_index\n" +
            "Greater London,88.4,94.2,4.8,44.3,18.2,72.4\n" +
            "Greater Paris,87.1,90.8,4.2,51.2,22.1,74.8\n" +
            "Greater Tokyo,91.2,96.4,4.1,56.8,19.4,78.2\n" +
            "Greater New York,85.6,93.1,6.2,39.4,15.8,69.3\n" +
            "Greater Seoul,92.1,98.2,3.8,62.4,16.7,71.6\n" +
            "Greater Amsterdam,89.3,95.7,3.4,49.1,27.3,80.1\n" +
            "Greater Vienna,82.4,92.3,4.6,41.2,30.4,82.6\n" +
            "Greater Stockholm,87.9,96.1,3.1,47.8,29.2,84.3\n" +
            "Greater Singapore,100.0,97.8,3.6,64.2,9.8,76.8\n" +
            "Greater Copenhagen,84.7,95.3,4.0,38.6,31.4,83.7\n" +
            "Greater Zurich,83.2,93.8,3.2,50.4,35.2,86.1\n" +
            "Greater Melbourne,86.4,89.7,5.8,28.3,24.6,75.4\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetRSquared — internet penetration vs wellbeing
        var r2Internet = doc.GetRSquared("internet_penetration_pct", "wellbeing_index");
        Assert.True(r2Internet >= 0.0 && r2Internet <= 1.0);

        // Green space vs wellbeing (expect positive correlation)
        var r2GreenWellbeing = doc.GetRSquared("green_space_pct", "wellbeing_index");
        Assert.True(r2GreenWellbeing >= 0.0 && r2GreenWellbeing <= 1.0);

        // CO2 vs wellbeing (expect negative correlation, lower R² for wellbeing)
        var r2Co2 = doc.GetRSquared("co2_per_capita", "wellbeing_index");
        Assert.True(r2Co2 >= 0.0 && r2Co2 <= 1.0);

        // Consistent
        Assert.Equal(r2Internet, doc.GetRSquared("internet_penetration_pct", "wellbeing_index"));

        // Perfect fit check
        var linearDoc = CsvDocument.LoadFile(CreateLinearCsv());
        Assert.True(linearDoc.GetRSquared("x", "y") >= 0.999);

        // GetResidualStdDev
        var rsdInternet = doc.GetResidualStdDev("internet_penetration_pct", "wellbeing_index");
        Assert.True(rsdInternet >= 0.0);

        var rsdGreenSpace = doc.GetResidualStdDev("green_space_pct", "wellbeing_index");
        Assert.True(rsdGreenSpace >= 0.0);

        // Consistent
        Assert.Equal(rsdInternet, doc.GetResidualStdDev("internet_penetration_pct", "wellbeing_index"));

        // Perfect fit residual zero
        Assert.True(linearDoc.GetResidualStdDev("x", "y") < 1e-9);

        // GetMeanAbsoluteError
        var maeInternet = doc.GetMeanAbsoluteError("internet_penetration_pct", "wellbeing_index");
        Assert.True(maeInternet >= 0.0);

        var maePublicTransport = doc.GetMeanAbsoluteError("public_transport_share", "wellbeing_index");
        Assert.True(maePublicTransport >= 0.0);

        // Consistent
        Assert.Equal(maeInternet, doc.GetMeanAbsoluteError("internet_penetration_pct", "wellbeing_index"));

        // SaveToFile
        var out1 = TempFile("dogfood_urbanisation_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(r2Internet, loaded.GetRSquared("internet_penetration_pct", "wellbeing_index"), precision: 6);
        Assert.Equal(rsdInternet, loaded.GetResidualStdDev("internet_penetration_pct", "wellbeing_index"), precision: 6);
        Assert.Equal(maeInternet, loaded.GetMeanAbsoluteError("internet_penetration_pct", "wellbeing_index"), precision: 6);

        // AddRow — Greater Dubai
        loaded.AddRow(new[] { "Greater Dubai", "91.8", "97.2", "6.8", "22.1", "12.4", "70.3" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(loaded.GetRSquared("green_space_pct", "wellbeing_index") >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_urbanisation_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetRSquared("internet_penetration_pct", "wellbeing_index") >= 0.0);
        Assert.True(loaded2.GetResidualStdDev("green_space_pct", "wellbeing_index") >= 0.0);
        Assert.True(loaded2.GetMeanAbsoluteError("public_transport_share", "wellbeing_index") >= 0.0);
    }
}
