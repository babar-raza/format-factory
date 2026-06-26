// Tests for CsvDocument.GetLinearRegressionSlope, GetLinearRegressionIntercept, GetPredictedValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R228

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R228: Tests for CsvDocument.GetLinearRegressionSlope, GetLinearRegressionIntercept, GetPredictedValue deeper.
/// GetLinearRegressionSlope(xCol, yCol): returns the slope of the OLS regression line.
/// GetLinearRegressionIntercept(xCol, yCol): returns the intercept of the OLS regression line.
/// GetPredictedValue(xCol, yCol, xValue): returns the predicted y for a given x value.
/// Covers: GetLinearRegressionSlope no-throw; GetLinearRegressionSlope finite; GetLinearRegressionSlope consistent;
/// GetLinearRegressionSlope save-load; GetLinearRegressionSlope positive for positively correlated;
/// GetLinearRegressionIntercept no-throw; GetLinearRegressionIntercept finite; GetLinearRegressionIntercept consistent;
/// GetLinearRegressionIntercept save-load;
/// GetPredictedValue no-throw; GetPredictedValue finite; GetPredictedValue consistent;
/// GetPredictedValue save-load;
/// dogfood CreateDoc→GetLinearRegressionSlope→GetLinearRegressionIntercept→GetPredictedValue pipeline.
/// </summary>
public class CsvR228GetLinearRegressionAndPredictionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR228GetLinearRegressionAndPredictionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR228_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateInfrastructureCsv()
    {
        var path = TempFile("infrastructure.csv");
        File.WriteAllText(path,
            "country,infrastructure_index,gdp_per_capita_usd,logistics_perf_index,trade_cost_usd_per_container\n" +
            "Singapore,96.4,65200,4.3,335\n" +
            "Hong Kong,93.8,51800,4.1,370\n" +
            "Denmark,87.6,68100,3.9,420\n" +
            "Germany,85.2,55400,4.2,410\n" +
            "Netherlands,83.4,58700,4.0,430\n" +
            "Japan,81.1,42700,4.1,450\n" +
            "Sweden,79.5,62100,3.8,480\n" +
            "Austria,76.8,53400,3.7,510\n" +
            "France,74.3,47800,3.6,525\n" +
            "UK,72.1,48500,3.7,530\n" +
            "Canada,69.4,56800,3.7,545\n" +
            "Australia,67.9,60200,3.6,560\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionSlope
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionSlope_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionSlope("infrastructure_index", "gdp_per_capita_usd"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionSlope_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var slope = doc.GetLinearRegressionSlope("infrastructure_index", "gdp_per_capita_usd");
        Assert.True(double.IsFinite(slope));
    }

    [Fact]
    public void GetLinearRegressionSlope_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        Assert.Equal(
            doc.GetLinearRegressionSlope("infrastructure_index", "logistics_perf_index"),
            doc.GetLinearRegressionSlope("infrastructure_index", "logistics_perf_index"));
    }

    [Fact]
    public void GetLinearRegressionSlope_Positive_ForPositivelyCorrelated()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        // Higher infrastructure index → higher GDP per capita
        var slope = doc.GetLinearRegressionSlope("infrastructure_index", "gdp_per_capita_usd");
        Assert.True(slope > 0.0);
    }

    [Fact]
    public void GetLinearRegressionSlope_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var before = doc.GetLinearRegressionSlope("infrastructure_index", "gdp_per_capita_usd");
        var path = TempFile("slope_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionSlope("infrastructure_index", "gdp_per_capita_usd"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionIntercept
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionIntercept_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionIntercept("infrastructure_index", "gdp_per_capita_usd"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionIntercept_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var intercept = doc.GetLinearRegressionIntercept("infrastructure_index", "gdp_per_capita_usd");
        Assert.True(double.IsFinite(intercept));
    }

    [Fact]
    public void GetLinearRegressionIntercept_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        Assert.Equal(
            doc.GetLinearRegressionIntercept("infrastructure_index", "logistics_perf_index"),
            doc.GetLinearRegressionIntercept("infrastructure_index", "logistics_perf_index"));
    }

    [Fact]
    public void GetLinearRegressionIntercept_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var before = doc.GetLinearRegressionIntercept("infrastructure_index", "trade_cost_usd_per_container");
        var path = TempFile("intercept_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionIntercept("infrastructure_index", "trade_cost_usd_per_container"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetPredictedValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPredictedValue_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var ex = Record.Exception(() => doc.GetPredictedValue("infrastructure_index", "gdp_per_capita_usd", 80.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetPredictedValue_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var pred = doc.GetPredictedValue("infrastructure_index", "gdp_per_capita_usd", 80.0);
        Assert.True(double.IsFinite(pred));
    }

    [Fact]
    public void GetPredictedValue_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        Assert.Equal(
            doc.GetPredictedValue("infrastructure_index", "gdp_per_capita_usd", 90.0),
            doc.GetPredictedValue("infrastructure_index", "gdp_per_capita_usd", 90.0));
    }

    [Fact]
    public void GetPredictedValue_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateInfrastructureCsv());
        var before = doc.GetPredictedValue("infrastructure_index", "logistics_perf_index", 85.0);
        var path = TempFile("pred_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetPredictedValue("infrastructure_index", "logistics_perf_index", 85.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetLinearRegressionSlope_GetIntercept_GetPredictedValue_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_education.csv");
        File.WriteAllText(path,
            "country,education_spending_pct_gdp,pisa_math_score,pisa_reading_score,tertiary_enrollment_pct,youth_unemployment_pct,graduate_employment_rate\n" +
            "Finland,5.9,507,524,90.1,17.8,88.4\n" +
            "South Korea,4.5,527,514,94.2,7.3,76.3\n" +
            "Estonia,5.2,523,523,76.3,11.4,83.1\n" +
            "Japan,3.6,527,504,63.4,4.2,91.2\n" +
            "Canada,5.3,512,520,58.5,11.2,83.7\n" +
            "Germany,4.8,500,498,69.4,5.6,88.9\n" +
            "Netherlands,5.4,519,524,83.2,8.4,87.3\n" +
            "Australia,4.9,491,503,83.0,11.7,82.4\n" +
            "UK,5.5,502,504,60.5,12.4,81.6\n" +
            "Sweden,6.8,502,506,76.8,20.1,84.2\n" +
            "Norway,6.5,501,506,80.3,11.1,88.7\n" +
            "Denmark,6.9,509,514,82.4,10.9,85.3\n");

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetLinearRegressionSlope — education spending vs PISA math
        var slopeSpendMath = doc.GetLinearRegressionSlope("education_spending_pct_gdp", "pisa_math_score");
        Assert.True(double.IsFinite(slopeSpendMath));

        // Higher tertiary enrollment → higher graduate employment (expect positive)
        var slopeTertiaryEmp = doc.GetLinearRegressionSlope("tertiary_enrollment_pct", "graduate_employment_rate");
        Assert.True(double.IsFinite(slopeTertiaryEmp));

        // Consistent
        Assert.Equal(slopeSpendMath, doc.GetLinearRegressionSlope("education_spending_pct_gdp", "pisa_math_score"));

        // GetLinearRegressionIntercept
        var interceptSpendMath = doc.GetLinearRegressionIntercept("education_spending_pct_gdp", "pisa_math_score");
        Assert.True(double.IsFinite(interceptSpendMath));

        var interceptSpendRead = doc.GetLinearRegressionIntercept("education_spending_pct_gdp", "pisa_reading_score");
        Assert.True(double.IsFinite(interceptSpendRead));

        // Consistent
        Assert.Equal(interceptSpendMath, doc.GetLinearRegressionIntercept("education_spending_pct_gdp", "pisa_math_score"));

        // GetPredictedValue — predict PISA math for 5.0% GDP spending
        var pred50 = doc.GetPredictedValue("education_spending_pct_gdp", "pisa_math_score", 5.0);
        Assert.True(double.IsFinite(pred50));

        var pred70 = doc.GetPredictedValue("education_spending_pct_gdp", "pisa_math_score", 7.0);
        Assert.True(double.IsFinite(pred70));

        // Consistent
        Assert.Equal(pred50, doc.GetPredictedValue("education_spending_pct_gdp", "pisa_math_score", 5.0));

        // SaveToFile
        var out1 = TempFile("dogfood_education_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(slopeSpendMath, loaded.GetLinearRegressionSlope("education_spending_pct_gdp", "pisa_math_score"), precision: 6);
        Assert.Equal(interceptSpendMath, loaded.GetLinearRegressionIntercept("education_spending_pct_gdp", "pisa_math_score"), precision: 6);
        Assert.Equal(pred50, loaded.GetPredictedValue("education_spending_pct_gdp", "pisa_math_score", 5.0), precision: 6);

        // AddRow — New Zealand
        loaded.AddRow(new[] { "New Zealand", "7.2", "494", "501", "80.6", "12.8", "82.9" });
        Assert.Equal(13, loaded.GetRowCount());
        var newSlope = loaded.GetLinearRegressionSlope("education_spending_pct_gdp", "pisa_math_score");
        Assert.True(double.IsFinite(newSlope));

        // Final save
        var out2 = TempFile("dogfood_education_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(double.IsFinite(loaded2.GetLinearRegressionSlope("education_spending_pct_gdp", "pisa_math_score")));
        Assert.True(double.IsFinite(loaded2.GetLinearRegressionIntercept("education_spending_pct_gdp", "pisa_reading_score")));
        Assert.True(double.IsFinite(loaded2.GetPredictedValue("tertiary_enrollment_pct", "graduate_employment_rate", 75.0)));
    }
}
