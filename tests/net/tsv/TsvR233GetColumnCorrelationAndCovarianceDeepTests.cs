// Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance, GetLinearRegressionSlope deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R233

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R233: Tests for TsvDocument.GetColumnCorrelation, GetColumnCovariance, GetLinearRegressionSlope deeper.
/// GetColumnCorrelation(col1, col2): returns the Pearson correlation coefficient [-1,1].
/// GetColumnCovariance(col1, col2): returns the covariance of the two columns.
/// GetLinearRegressionSlope(xCol, yCol): returns the slope of the OLS regression of y on x.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in range; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical; GetColumnCorrelation save-load;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent; GetColumnCovariance save-load;
/// GetLinearRegressionSlope no-throw; GetLinearRegressionSlope consistent; GetLinearRegressionSlope save-load;
/// dogfood CreateDoc→GetColumnCorrelation→GetColumnCovariance→GetLinearRegressionSlope→SaveToFile pipeline.
/// </summary>
public class TsvR233GetColumnCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR233GetColumnCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR233_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEconomicTsv()
    {
        var path = TempFile("economic.tsv");
        File.WriteAllText(path,
            "year\tgdp_bn\tconsumption_bn\tinvestment_bn\texports_bn\tunemployment_pct\n" +
            "2014\t18500\t12850\t3250\t2850\t6.2\n" +
            "2015\t19200\t13280\t3380\t2960\t5.8\n" +
            "2016\t19800\t13620\t3480\t3040\t5.5\n" +
            "2017\t20500\t14100\t3620\t3180\t5.2\n" +
            "2018\t21200\t14520\t3780\t3250\t4.8\n" +
            "2019\t21900\t14980\t3920\t3380\t4.5\n" +
            "2020\t20100\t14250\t3100\t2980\t8.1\n" +
            "2021\t22500\t15480\t4120\t3580\t5.9\n" +
            "2022\t24100\t16450\t4580\t3820\t4.2\n" +
            "2023\t25200\t17120\t4820\t3950\t3.9\n" +
            "2024\t26400\t17850\t5080\t4120\t3.7\n" +
            "2025\t27200\t18350\t5280\t4280\t3.5\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("gdp_bn", "consumption_bn"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var corr = doc.GetColumnCorrelation("gdp_bn", "consumption_bn");
        Assert.True(corr >= -1.0);
        Assert.True(corr <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        Assert.Equal(
            doc.GetColumnCorrelation("gdp_bn", "investment_bn"),
            doc.GetColumnCorrelation("gdp_bn", "investment_bn"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdentical()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        Assert.Equal(1.0, doc.GetColumnCorrelation("gdp_bn", "gdp_bn"), precision: 6);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var before = doc.GetColumnCorrelation("gdp_bn", "exports_bn");
        var path = TempFile("corr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("gdp_bn", "exports_bn"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("gdp_bn", "consumption_bn"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        Assert.Equal(
            doc.GetColumnCovariance("investment_bn", "exports_bn"),
            doc.GetColumnCovariance("investment_bn", "exports_bn"));
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var before = doc.GetColumnCovariance("gdp_bn", "investment_bn");
        var path = TempFile("cov_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("gdp_bn", "investment_bn"), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetLinearRegressionSlope
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLinearRegressionSlope_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var ex = Record.Exception(() => doc.GetLinearRegressionSlope("gdp_bn", "consumption_bn"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetLinearRegressionSlope_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        Assert.Equal(
            doc.GetLinearRegressionSlope("gdp_bn", "consumption_bn"),
            doc.GetLinearRegressionSlope("gdp_bn", "consumption_bn"));
    }

    [Fact]
    public void GetLinearRegressionSlope_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicTsv());
        var before = doc.GetLinearRegressionSlope("year", "gdp_bn");
        var path = TempFile("slope_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetLinearRegressionSlope("year", "gdp_bn"), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_GetLinearRegressionSlope_SaveToFile_Pipeline()
    {
        // Real estate market panel — 12 quarters of housing market indicators
        var path = TempFile("dogfood_housing.tsv");
        File.WriteAllText(path,
            "quarter\tmedian_price_k\tmortgage_rate\thousing_starts_k\tpermit_volume_k\tsales_volume_k\taffordability_index\n" +
            "Q1-23\t385.2\t6.85\t142.5\t158.4\t428.5\t88.2\n" +
            "Q2-23\t398.5\t6.42\t156.8\t172.3\t452.8\t89.5\n" +
            "Q3-23\t412.8\t7.12\t148.2\t165.8\t438.2\t87.1\n" +
            "Q4-23\t425.4\t7.48\t138.5\t152.4\t418.5\t85.8\n" +
            "Q1-24\t432.1\t7.25\t145.8\t162.5\t425.8\t86.4\n" +
            "Q2-24\t448.6\t6.85\t158.4\t176.2\t458.2\t88.8\n" +
            "Q3-24\t462.3\t6.52\t165.8\t182.5\t472.5\t90.2\n" +
            "Q4-24\t478.5\t6.28\t172.4\t188.8\t485.8\t91.5\n" +
            "Q1-25\t485.2\t6.15\t168.5\t185.2\t478.4\t92.1\n" +
            "Q2-25\t498.8\t5.98\t175.8\t192.4\t492.5\t93.5\n" +
            "Q3-25\t512.4\t5.85\t182.5\t198.8\t505.8\t94.8\n" +
            "Q4-25\t528.5\t5.72\t188.2\t205.4\t518.2\t96.2\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetColumnCorrelation — price vs mortgage rate (should be negative)
        var corrPriceMortgage = doc.GetColumnCorrelation("median_price_k", "mortgage_rate");
        Assert.True(corrPriceMortgage >= -1.0);
        Assert.True(corrPriceMortgage <= 1.0);
        Assert.Equal(corrPriceMortgage, doc.GetColumnCorrelation("median_price_k", "mortgage_rate")); // consistent

        // Price vs sales volume (should be positive)
        var corrPriceSales = doc.GetColumnCorrelation("median_price_k", "sales_volume_k");
        Assert.True(corrPriceSales >= -1.0);
        Assert.True(corrPriceSales <= 1.0);

        // Self-correlation = 1.0
        Assert.Equal(1.0, doc.GetColumnCorrelation("median_price_k", "median_price_k"), precision: 6);

        // GetColumnCovariance
        var covPriceStarts = doc.GetColumnCovariance("median_price_k", "housing_starts_k");
        Assert.Equal(covPriceStarts, doc.GetColumnCovariance("median_price_k", "housing_starts_k")); // consistent

        var covStartsPermits = doc.GetColumnCovariance("housing_starts_k", "permit_volume_k");
        Assert.Equal(covStartsPermits, doc.GetColumnCovariance("housing_starts_k", "permit_volume_k"));

        // GetLinearRegressionSlope — affordability index trend
        var slopeAffordMortgage = doc.GetLinearRegressionSlope("mortgage_rate", "affordability_index");
        Assert.Equal(slopeAffordMortgage, doc.GetLinearRegressionSlope("mortgage_rate", "affordability_index")); // consistent

        var slopePriceStarts = doc.GetLinearRegressionSlope("housing_starts_k", "median_price_k");
        Assert.Equal(slopePriceStarts, doc.GetLinearRegressionSlope("housing_starts_k", "median_price_k"));

        // SaveToFile
        var out1 = TempFile("dogfood_housing_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(corrPriceMortgage, loaded.GetColumnCorrelation("median_price_k", "mortgage_rate"), precision: 6);
        Assert.Equal(covPriceStarts, loaded.GetColumnCovariance("median_price_k", "housing_starts_k"), precision: 2);
        Assert.Equal(slopeAffordMortgage, loaded.GetLinearRegressionSlope("mortgage_rate", "affordability_index"), precision: 4);

        // AddRow and verify metrics still valid
        loaded.AddRow(new[] { "Q1-26", "545.2", "5.65", "192.8", "210.5", "528.5", "97.4" });
        Assert.Equal(13, loaded.GetRowCount());
        var newCorr = loaded.GetColumnCorrelation("median_price_k", "mortgage_rate");
        Assert.True(newCorr >= -1.0);
        Assert.True(newCorr <= 1.0);

        // Final save
        var out2 = TempFile("dogfood_housing_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnCorrelation("housing_starts_k", "sales_volume_k") >= -1.0);
        Assert.True(loaded2.GetColumnCorrelation("housing_starts_k", "sales_volume_k") <= 1.0);
    }
}
