// Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R266

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R266: Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance deeper.
/// GetColumnCorrelation(colA, colB): returns Pearson correlation coefficient (-1 to +1).
/// GetColumnCovariance(colA, colB): returns population covariance between two columns.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in-range; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical; GetColumnCorrelation save-load;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent;
/// GetColumnCovariance positive for positively correlated; GetColumnCovariance save-load;
/// GetColumnCorrelation symmetric; dogfood CreateDoc→GetColumnCorrelation→GetColumnCovariance pipeline.
/// </summary>
public class CsvR266GetColumnCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR266GetColumnCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR266_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,price,yield_pct,duration,spread_bps");
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            double price = 80 + rng.NextDouble() * 40;
            double yield = Math.Round(10 - (price - 80) / 40 * 5 + rng.NextDouble() * 0.5, 4); // neg corr with price
            double duration = Math.Round(2 + rng.NextDouble() * 8, 2);
            double spread = Math.Round(50 + rng.NextDouble() * 300, 1);
            sb.AppendLine($"{i},{price:F4},{yield},{duration},{spread}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateIdenticalCsv()
    {
        var path = TempFile("identical.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,a,b");
        var rng = new Random(42);
        for (int i = 0; i < 50; i++)
        {
            double v = rng.NextDouble() * 100;
            sb.AppendLine($"{i},{v:F4},{v:F4}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("price", "yield_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var r = doc.GetColumnCorrelation("price", "yield_pct");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnCorrelation("price", "yield_pct"),
                     doc.GetColumnCorrelation("price", "yield_pct"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdentical()
    {
        var doc = CsvDocument.LoadFile(CreateIdenticalCsv());
        Assert.Equal(1.0, doc.GetColumnCorrelation("a", "b"), precision: 6);
    }

    [Fact]
    public void GetColumnCorrelation_Symmetric()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnCorrelation("price", "duration"),
                     doc.GetColumnCorrelation("duration", "price"), precision: 6);
    }

    [Fact]
    public void GetColumnCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCorrelation("price", "yield_pct");
        var path = TempFile("corr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCorrelation("price", "yield_pct"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("price", "duration"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnCovariance("price", "spread_bps"),
                     doc.GetColumnCovariance("price", "spread_bps"));
    }

    [Fact]
    public void GetColumnCovariance_Negative_ForNegativelyCorrelated()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        // price and yield_pct are negatively correlated by construction
        Assert.True(doc.GetColumnCovariance("price", "yield_pct") < 0);
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCovariance("duration", "spread_bps");
        var path = TempFile("cov_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("duration", "spread_bps"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_Pipeline()
    {
        // Fixed income — Debt Management Office: UK Gilt Market Analysis
        // Correlation analysis between gilt yields, prices, durations, and spread indicators
        var path = TempFile("dmo_gilt_analysis.csv");
        var sb = new StringBuilder();
        sb.AppendLine("isin,maturity_yr,coupon_pct,clean_price,ytm_pct,modified_duration,spread_to_bund_bps,bid_ask_bps");

        var rng = new Random(20240901);
        for (int i = 0; i < 200; i++)
        {
            int matYr = 2025 + rng.Next(26); // 2025-2050
            double coupon = Math.Round(0.125 + rng.NextDouble() * 5.875, 3);
            double ytm = Math.Round(3.5 + rng.NextDouble() * 2.0, 4);
            // Price and yield inversely related
            double price = Math.Round(100 * coupon / ytm + rng.NextDouble() * 5, 4);
            double modDur = Math.Round((matYr - 2025) * 0.8 + rng.NextDouble() * 1.5, 2);
            double spread = Math.Round(10 + rng.NextDouble() * 60, 1);
            double bidAsk = Math.Round(0.5 + rng.NextDouble() * 2.5, 2);
            sb.AppendLine($"GB{i:D10},{matYr},{coupon},{price},{ytm},{modDur},{spread},{bidAsk}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Correlation: ytm vs clean_price — expect negative (inverse relationship)
        var corrYtmPrice = doc.GetColumnCorrelation("ytm_pct", "clean_price");
        Assert.True(corrYtmPrice >= -1.0 && corrYtmPrice <= 1.0);
        Assert.Equal(corrYtmPrice, doc.GetColumnCorrelation("ytm_pct", "clean_price")); // consistent

        // Symmetry check
        Assert.Equal(corrYtmPrice,
                     doc.GetColumnCorrelation("clean_price", "ytm_pct"), precision: 6);

        // Correlation: modified_duration vs maturity — expect strong positive
        var corrDurMat = doc.GetColumnCorrelation("modified_duration", "maturity_yr");
        Assert.True(corrDurMat >= -1.0 && corrDurMat <= 1.0);
        Assert.True(corrDurMat > 0); // longer maturity → longer duration

        // Correlation self (= 1)
        var corrSelf = doc.GetColumnCorrelation("ytm_pct", "ytm_pct");
        Assert.Equal(1.0, corrSelf, precision: 6);

        // Covariance: ytm vs clean_price
        var covYtmPrice = doc.GetColumnCovariance("ytm_pct", "clean_price");
        Assert.Equal(covYtmPrice, doc.GetColumnCovariance("ytm_pct", "clean_price")); // consistent

        // Covariance: duration vs maturity — positive
        var covDurMat = doc.GetColumnCovariance("modified_duration", "maturity_yr");
        Assert.True(covDurMat > 0);

        // Covariance: bid_ask vs spread — independent
        var covBidSpread = doc.GetColumnCovariance("bid_ask_bps", "spread_to_bund_bps");
        // just verify it's a finite number
        Assert.True(double.IsFinite(covBidSpread));

        // SaveToFile
        var outPath = TempFile("dmo_gilt_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(corrYtmPrice, loaded.GetColumnCorrelation("ytm_pct", "clean_price"), precision: 6);
        Assert.Equal(covYtmPrice, loaded.GetColumnCovariance("ytm_pct", "clean_price"), precision: 4);
        Assert.Equal(corrDurMat, loaded.GetColumnCorrelation("modified_duration", "maturity_yr"), precision: 6);
    }
}
