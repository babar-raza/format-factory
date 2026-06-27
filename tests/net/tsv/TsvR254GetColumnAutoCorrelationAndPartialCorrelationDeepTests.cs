// Tests for TsvDocument.GetColumnAutoCorrelation, GetColumnPartialCorrelation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R254

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R254: Tests for TsvDocument.GetColumnAutoCorrelation, GetColumnPartialCorrelation deeper.
/// GetColumnAutoCorrelation(colName, lag): returns autocorrelation at the given lag.
/// GetColumnPartialCorrelation(colName1, colName2, controlCol): returns partial correlation
///   between col1 and col2 controlling for controlCol.
/// Covers: GetColumnAutoCorrelation no-throw; GetColumnAutoCorrelation in [-1,1];
/// GetColumnAutoCorrelation lag0 equals 1.0; GetColumnAutoCorrelation consistent;
/// GetColumnAutoCorrelation save-load;
/// GetColumnPartialCorrelation no-throw; GetColumnPartialCorrelation in [-1,1];
/// GetColumnPartialCorrelation consistent; GetColumnPartialCorrelation save-load;
/// dogfood CreateDoc→GetColumnAutoCorrelation→GetColumnPartialCorrelation pipeline.
/// </summary>
public class TsvR254GetColumnAutoCorrelationAndPartialCorrelationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR254GetColumnAutoCorrelationAndPartialCorrelationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR254_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTimeSeriesTsv()
    {
        var path = TempFile("time_series.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("t\tvalue\ttrend\tnoise");
        var rng = new Random(20240101);
        double v = 100;
        for (int i = 0; i < 100; i++)
        {
            double trend = i * 0.5;
            double noise = (rng.NextDouble() - 0.5) * 10;
            v = 0.8 * v + 0.2 * (trend + noise) + 20;
            sb.AppendLine($"{i}\t{v:F4}\t{trend:F4}\t{noise:F4}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnAutoCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAutoCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var ex = Record.Exception(() => doc.GetColumnAutoCorrelation("value", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnAutoCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var ac = doc.GetColumnAutoCorrelation("value", 1);
        Assert.True(ac >= -1.0 && ac <= 1.0);
    }

    [Fact]
    public void GetColumnAutoCorrelation_Lag0_Equals_One()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("value", 0), precision: 6);
    }

    [Fact]
    public void GetColumnAutoCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        Assert.Equal(doc.GetColumnAutoCorrelation("value", 2), doc.GetColumnAutoCorrelation("value", 2));
    }

    [Fact]
    public void GetColumnAutoCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var before = doc.GetColumnAutoCorrelation("value", 1);
        var path = TempFile("ac_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnAutoCorrelation("value", 1), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnPartialCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPartialCorrelation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var ex = Record.Exception(() => doc.GetColumnPartialCorrelation("value", "trend", "noise"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPartialCorrelation_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var pc = doc.GetColumnPartialCorrelation("value", "trend", "noise");
        Assert.True(pc >= -1.0 && pc <= 1.0);
    }

    [Fact]
    public void GetColumnPartialCorrelation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        Assert.Equal(
            doc.GetColumnPartialCorrelation("value", "trend", "noise"),
            doc.GetColumnPartialCorrelation("value", "trend", "noise"));
    }

    [Fact]
    public void GetColumnPartialCorrelation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTimeSeriesTsv());
        var before = doc.GetColumnPartialCorrelation("value", "noise", "trend");
        var path = TempFile("pc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPartialCorrelation("value", "noise", "trend"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnAutoCorrelation_GetColumnPartialCorrelation_Pipeline()
    {
        // Time series econometrics — Bank of England MPC quarterly Inflation Report data
        // Autocorrelation and partial correlation for CPI, unemployment, and Bank Rate time series
        var path = TempFile("boe_macro_quarterly.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("quarter\tcpi_yoy_pct\tunemployment_pct\tbank_rate_pct\tgdp_growth_pct\tfx_twi_index\tbrent_usd");
        var rng = new Random(20240115);
        // Simulate 100 quarterly observations (AR(1) processes with cross-correlations)
        double cpi = 2.0, unemp = 4.5, bankRate = 0.25, gdp = 2.0, twi = 100.0, brent = 60.0;
        for (int q = 0; q < 100; q++)
        {
            // AR(1) dynamics with noise
            cpi = 0.85 * cpi + 0.15 * 2.5 + (rng.NextDouble() - 0.5) * 0.8;
            unemp = 0.90 * unemp + 0.10 * 4.5 + (rng.NextDouble() - 0.5) * 0.4;
            // Bank rate responds to CPI
            bankRate = 0.95 * bankRate + 0.05 * (cpi > 2.5 ? 1.0 : 0.5) * cpi + (rng.NextDouble() - 0.5) * 0.1;
            bankRate = Math.Max(0.1, bankRate);
            gdp = 0.7 * gdp + 0.3 * (2.5 - 0.5 * unemp) + (rng.NextDouble() - 0.5) * 0.5;
            twi = 0.92 * twi + 0.08 * 98 + (rng.NextDouble() - 0.5) * 2;
            brent = 0.88 * brent + 0.12 * 65 + (rng.NextDouble() - 0.5) * 5;
            int year = 2000 + q / 4;
            int quarter_num = q % 4 + 1;
            sb.AppendLine($"Q{quarter_num}_{year}\t{cpi:F2}\t{unemp:F2}\t{bankRate:F2}\t{gdp:F2}\t{twi:F1}\t{brent:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(100, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // GetColumnAutoCorrelation — CPI should have high autocorrelation (persistent inflation)
        var ac1Cpi = doc.GetColumnAutoCorrelation("cpi_yoy_pct", 1);
        Assert.True(ac1Cpi >= -1.0 && ac1Cpi <= 1.0);
        Assert.Equal(ac1Cpi, doc.GetColumnAutoCorrelation("cpi_yoy_pct", 1)); // consistent

        var ac1Unemp = doc.GetColumnAutoCorrelation("unemployment_pct", 1);
        Assert.True(ac1Unemp >= -1.0 && ac1Unemp <= 1.0);

        var ac1BankRate = doc.GetColumnAutoCorrelation("bank_rate_pct", 1);
        Assert.True(ac1BankRate >= -1.0 && ac1BankRate <= 1.0);

        // Lag 0 = 1.0 by definition
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("cpi_yoy_pct", 0), precision: 6);
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("gdp_growth_pct", 0), precision: 6);

        // Lag 4 (annual)
        var ac4Cpi = doc.GetColumnAutoCorrelation("cpi_yoy_pct", 4);
        Assert.True(ac4Cpi >= -1.0 && ac4Cpi <= 1.0);

        // GetColumnPartialCorrelation — controlling for bank rate when correlating CPI and unemployment
        var pcCpiUnemp = doc.GetColumnPartialCorrelation("cpi_yoy_pct", "unemployment_pct", "bank_rate_pct");
        Assert.True(pcCpiUnemp >= -1.0 && pcCpiUnemp <= 1.0);
        Assert.Equal(pcCpiUnemp, doc.GetColumnPartialCorrelation("cpi_yoy_pct", "unemployment_pct", "bank_rate_pct")); // consistent

        var pcGdpCpi = doc.GetColumnPartialCorrelation("gdp_growth_pct", "cpi_yoy_pct", "unemployment_pct");
        Assert.True(pcGdpCpi >= -1.0 && pcGdpCpi <= 1.0);

        var pcBrentCpi = doc.GetColumnPartialCorrelation("brent_usd", "cpi_yoy_pct", "fx_twi_index");
        Assert.True(pcBrentCpi >= -1.0 && pcBrentCpi <= 1.0);

        // Basic stats
        Assert.True(doc.GetColumnMean("cpi_yoy_pct") > 0.0);
        Assert.True(doc.GetColumnStdDev("bank_rate_pct") >= 0.0);

        // SaveToFile
        var outPath = TempFile("boe_macro_quarterly_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(ac1Cpi, loaded.GetColumnAutoCorrelation("cpi_yoy_pct", 1), precision: 8);
        Assert.Equal(ac4Cpi, loaded.GetColumnAutoCorrelation("cpi_yoy_pct", 4), precision: 8);
        Assert.Equal(pcCpiUnemp, loaded.GetColumnPartialCorrelation("cpi_yoy_pct", "unemployment_pct", "bank_rate_pct"), precision: 8);
    }
}
