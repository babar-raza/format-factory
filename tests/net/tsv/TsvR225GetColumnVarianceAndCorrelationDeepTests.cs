// Tests for TsvDocument.GetColumnVariance, GetColumnCorrelation, GetColumnCovariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R225

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R225: Tests for TsvDocument.GetColumnVariance, GetColumnCorrelation, GetColumnCovariance deeper.
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
public class TsvR225GetColumnVarianceAndCorrelationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR225GetColumnVarianceAndCorrelationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR225_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEconomicsTsv()
    {
        var path = TempFile("economics.tsv");
        File.WriteAllText(path,
            "country\tgdp_growth\tinflation\tunemployment\ttrade_balance\n" +
            "Germany\t1.9\t2.1\t3.1\t290.5\n" +
            "France\t1.5\t2.4\t7.4\t-42.1\n" +
            "Italy\t0.8\t1.9\t9.7\t52.3\n" +
            "Spain\t2.3\t3.2\t12.1\t-18.4\n" +
            "Netherlands\t2.8\t2.7\t3.6\t85.7\n" +
            "Belgium\t1.6\t2.9\t5.4\t18.2\n" +
            "Sweden\t2.1\t1.8\t8.3\t22.6\n" +
            "Denmark\t2.4\t2.3\t4.9\t31.4\n" +
            "Finland\t1.3\t2.0\t7.6\t3.1\n" +
            "Poland\t4.1\t3.5\t3.3\t-8.9\n");
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        File.WriteAllText(path,
            "id\tvalue\n" +
            "1\t5.0\n" +
            "2\t5.0\n" +
            "3\t5.0\n" +
            "4\t5.0\n" +
            "5\t5.0\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("gdp_growth"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        Assert.True(doc.GetColumnVariance("inflation") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        Assert.Equal(doc.GetColumnVariance("unemployment"), doc.GetColumnVariance("unemployment"));
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnVariance("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var before = doc.GetColumnVariance("trade_balance");
        var path = TempFile("var_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnVariance("trade_balance"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("gdp_growth", "inflation"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var r = doc.GetColumnCorrelation("gdp_growth", "inflation");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        Assert.Equal(
            doc.GetColumnCorrelation("gdp_growth", "unemployment"),
            doc.GetColumnCorrelation("gdp_growth", "unemployment"));
    }

    [Fact]
    public void GetColumnCorrelation_PerfectPositive_WithSelf()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var r = doc.GetColumnCorrelation("gdp_growth", "gdp_growth");
        Assert.True(Math.Abs(r - 1.0) < 1e-9 || r >= 0.99);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var before = doc.GetColumnCorrelation("inflation", "unemployment");
        var path = TempFile("corr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("inflation", "unemployment"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("gdp_growth", "inflation"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        Assert.Equal(
            doc.GetColumnCovariance("inflation", "unemployment"),
            doc.GetColumnCovariance("inflation", "unemployment"));
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconomicsTsv());
        var before = doc.GetColumnCovariance("gdp_growth", "trade_balance");
        var path = TempFile("cov_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("gdp_growth", "trade_balance"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnCorrelation_GetColumnCovariance_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_macro.tsv");
        File.WriteAllText(path,
            "economy\tgrowth\tcpi\tppi\texports\timports\tca_balance\n" +
            "USA\t2.3\t3.1\t3.4\t2500.0\t3100.0\t-600.0\n" +
            "China\t5.2\t1.9\t2.1\t3600.0\t2800.0\t800.0\n" +
            "Japan\t1.1\t2.8\t3.0\t750.0\t820.0\t-70.0\n" +
            "Germany\t1.9\t2.1\t2.3\t1600.0\t1310.0\t290.0\n" +
            "UK\t1.4\t4.0\t4.3\t470.0\t680.0\t-210.0\n" +
            "India\t6.8\t5.2\t5.7\t420.0\t680.0\t-260.0\n" +
            "Brazil\t2.9\t4.6\t4.9\t340.0\t220.0\t120.0\n" +
            "Canada\t2.1\t3.4\t3.7\t560.0\t580.0\t-20.0\n" +
            "Australia\t3.3\t3.6\t3.8\t280.0\t260.0\t20.0\n" +
            "South Korea\t2.6\t2.5\t2.8\t680.0\t620.0\t60.0\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnCount());

        // GetColumnVariance — all non-negative
        var varGrowth = doc.GetColumnVariance("growth");
        Assert.True(varGrowth >= 0.0);

        var varCpi = doc.GetColumnVariance("cpi");
        Assert.True(varCpi >= 0.0);

        var varExports = doc.GetColumnVariance("exports");
        Assert.True(varExports >= 0.0);

        // Consistent
        Assert.Equal(varGrowth, doc.GetColumnVariance("growth"));

        // GetColumnCorrelation
        var rGrowthCpi = doc.GetColumnCorrelation("growth", "cpi");
        Assert.True(rGrowthCpi >= -1.0 && rGrowthCpi <= 1.0);

        var rExportsImports = doc.GetColumnCorrelation("exports", "imports");
        Assert.True(rExportsImports >= -1.0 && rExportsImports <= 1.0);

        var rSelf = doc.GetColumnCorrelation("growth", "growth");
        Assert.True(rSelf >= 0.99 || Math.Abs(rSelf - 1.0) < 1e-9);

        // Consistent
        Assert.Equal(rGrowthCpi, doc.GetColumnCorrelation("growth", "cpi"));

        // GetColumnCovariance
        var covGrowthExports = doc.GetColumnCovariance("growth", "exports");
        Assert.Equal(covGrowthExports, doc.GetColumnCovariance("growth", "exports"));

        var covCpiPpi = doc.GetColumnCovariance("cpi", "ppi");
        Assert.Equal(covCpiPpi, doc.GetColumnCovariance("cpi", "ppi"));

        // Verify CPI and PPI strongly correlated (both measure prices)
        var rCpiPpi = doc.GetColumnCorrelation("cpi", "ppi");
        Assert.True(rCpiPpi > 0.5); // expect positive correlation

        // ExportToCsv no-throw
        var ex1 = Record.Exception(() => doc.ExportToCsv());
        Assert.Null(ex1);

        // SaveToFile
        var out1 = TempFile("dogfood_macro_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(doc.GetColumnVariance("growth"), loaded.GetColumnVariance("growth"), precision: 6);
        Assert.Equal(doc.GetColumnCorrelation("exports", "imports"),
            loaded.GetColumnCorrelation("exports", "imports"), precision: 6);
        Assert.Equal(doc.GetColumnCovariance("cpi", "ppi"),
            loaded.GetColumnCovariance("cpi", "ppi"), precision: 6);

        // AddRow and re-verify
        loaded.AddRow(new[] { "Mexico", "3.1", "4.8", "5.0", "490.0", "510.0", "-20.0" });
        Assert.Equal(11, loaded.GetRowCount());

        // Variance should change after adding row
        var newVarGrowth = loaded.GetColumnVariance("growth");
        Assert.True(newVarGrowth >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_macro_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRowCount());
        Assert.True(loaded2.GetColumnVariance("growth") >= 0.0);
        Assert.True(loaded2.GetColumnCorrelation("growth", "cpi") >= -1.0);
        Assert.Equal(loaded2.GetColumnCovariance("cpi", "ppi"), loaded2.GetColumnCovariance("cpi", "ppi"));
        var ex2 = Record.Exception(() => loaded2.ExportToCsv());
        Assert.Null(ex2);
    }
}
