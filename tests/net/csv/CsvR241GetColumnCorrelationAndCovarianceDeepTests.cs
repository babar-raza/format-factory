// Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance, GetColumnMutualInformation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R241

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R241: Tests for CsvDocument.GetColumnCorrelation, GetColumnCovariance, GetColumnMutualInformation deeper.
/// GetColumnCorrelation(col1, col2): returns the Pearson correlation coefficient between two numeric columns.
/// GetColumnCovariance(col1, col2): returns the sample covariance between two numeric columns.
/// GetColumnMutualInformation(col1, col2): returns an information-theoretic measure of dependence.
/// Covers: GetColumnCorrelation no-throw; GetColumnCorrelation in [-1,1]; GetColumnCorrelation consistent;
/// GetColumnCorrelation one for identical columns; GetColumnCorrelation symmetric;
/// GetColumnCovariance no-throw; GetColumnCovariance consistent; GetColumnCovariance sign consistent;
/// GetColumnCovariance save-load;
/// GetColumnMutualInformation no-throw; GetColumnMutualInformation non-negative; GetColumnMutualInformation consistent;
/// dogfood GetColumnCorrelation→GetColumnCovariance→GetColumnMutualInformation pipeline.
/// </summary>
public class CsvR241GetColumnCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR241GetColumnCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR241_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMacroDataCsv()
    {
        var path = TempFile("macro.csv");
        File.WriteAllLines(path, new[]
        {
            "country,gdp_growth,unemployment,inflation,interest_rate,current_account",
            "UK,0.1,3.8,3.2,5.25,-2.8",
            "Germany,0.3,3.0,2.6,4.00,5.8",
            "France,0.9,7.3,2.3,4.00,-0.9",
            "Italy,-0.2,6.7,1.2,4.00,0.2",
            "Spain,2.1,11.9,2.8,4.00,3.5",
            "Netherlands,0.6,3.7,2.9,4.00,10.2",
            "Sweden,-0.8,8.5,1.8,3.75,5.9",
            "Poland,2.9,3.0,4.6,5.75,-2.1",
            "Czech,0.4,2.7,3.1,5.00,-0.8",
            "Denmark,1.7,4.8,1.9,3.60,9.4",
            "Norway,1.1,3.6,3.3,4.50,22.6",
            "Switzerland,1.4,2.2,1.3,1.75,10.8",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var ex = Record.Exception(() => doc.GetColumnCorrelation("gdp_growth", "unemployment"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var corr = doc.GetColumnCorrelation("gdp_growth", "inflation");
        Assert.True(corr >= -1.0 && corr <= 1.0);
    }

    [Fact]
    public void GetColumnCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        Assert.Equal(
            doc.GetColumnCorrelation("gdp_growth", "unemployment"),
            doc.GetColumnCorrelation("gdp_growth", "unemployment"));
    }

    [Fact]
    public void GetColumnCorrelation_One_ForIdenticalColumns()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var corr = doc.GetColumnCorrelation("inflation", "inflation");
        Assert.True(Math.Abs(corr - 1.0) < 1e-6);
    }

    [Fact]
    public void GetColumnCorrelation_Symmetric()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var c1 = doc.GetColumnCorrelation("gdp_growth", "inflation");
        var c2 = doc.GetColumnCorrelation("inflation", "gdp_growth");
        Assert.Equal(c1, c2, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCovariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var ex = Record.Exception(() => doc.GetColumnCovariance("gdp_growth", "inflation"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCovariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        Assert.Equal(
            doc.GetColumnCovariance("unemployment", "interest_rate"),
            doc.GetColumnCovariance("unemployment", "interest_rate"));
    }

    [Fact]
    public void GetColumnCovariance_Sign_Consistent_With_Correlation()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var corr = doc.GetColumnCorrelation("gdp_growth", "current_account");
        var cov = doc.GetColumnCovariance("gdp_growth", "current_account");
        Assert.True(Math.Sign(corr) == Math.Sign(cov) || Math.Abs(cov) < 1e-6);
    }

    [Fact]
    public void GetColumnCovariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var before = doc.GetColumnCovariance("gdp_growth", "unemployment");
        var path = TempFile("cov_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCovariance("gdp_growth", "unemployment"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnMutualInformation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMutualInformation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        var ex = Record.Exception(() => doc.GetColumnMutualInformation("gdp_growth", "unemployment"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMutualInformation_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        Assert.True(doc.GetColumnMutualInformation("inflation", "interest_rate") >= 0);
    }

    [Fact]
    public void GetColumnMutualInformation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateMacroDataCsv());
        Assert.Equal(
            doc.GetColumnMutualInformation("gdp_growth", "current_account"),
            doc.GetColumnMutualInformation("gdp_growth", "current_account"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCorrelation_GetColumnCovariance_GetColumnMutualInformation_Pipeline()
    {
        // Real estate economics — housing market indicator correlation study
        var path = TempFile("housing_market.csv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("month,avg_price_gbp,transactions,mortgage_rate,new_supply,affordability_ratio,rental_yield_pct");
        var rng = new Random(20240901);
        double price = 280000;
        double rate = 4.5;
        for (int i = 0; i < 60; i++) // 5 years monthly
        {
            price += (rng.NextDouble() - 0.42) * 4000; // slight upward drift
            rate += (rng.NextDouble() - 0.55) * 0.15; // slight downward drift
            rate = Math.Max(2.0, Math.Min(7.5, rate));
            int transactions = (int)(55000 - (rate - 3.0) * 8000 + (rng.NextDouble() - 0.5) * 10000);
            int supply = (int)(15000 + (rng.NextDouble() - 0.5) * 6000);
            double affordability = price / (30000 + rng.NextDouble() * 20000);
            double rentalYield = 4.5 - (price - 280000) / 100000 * 0.1 + rng.NextDouble() * 0.5;
            lines.Add($"2020-{(i % 12 + 1):D2},{price:F0},{Math.Max(10000, transactions)},{rate:F2},{supply},{affordability:F2},{rentalYield:F2}");
        }
        File.WriteAllLines(path, lines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(60, doc.RowCount);

        // GetColumnCorrelation — mortgage rate vs transactions (should be negative)
        var rateTransCorr = doc.GetColumnCorrelation("mortgage_rate", "transactions");
        Assert.True(rateTransCorr >= -1.0 && rateTransCorr <= 1.0);
        Assert.True(rateTransCorr < 0); // higher rates → fewer transactions

        // Self-correlation
        Assert.True(Math.Abs(doc.GetColumnCorrelation("avg_price_gbp", "avg_price_gbp") - 1.0) < 1e-6);

        // Consistent
        var c1 = doc.GetColumnCorrelation("avg_price_gbp", "rental_yield_pct");
        Assert.Equal(c1, doc.GetColumnCorrelation("avg_price_gbp", "rental_yield_pct"));

        // Symmetric
        var corrAB = doc.GetColumnCorrelation("avg_price_gbp", "mortgage_rate");
        var corrBA = doc.GetColumnCorrelation("mortgage_rate", "avg_price_gbp");
        Assert.Equal(corrAB, corrBA, precision: 6);

        // GetColumnCovariance
        var cov = doc.GetColumnCovariance("mortgage_rate", "transactions");
        Assert.True(Math.Sign(cov) == Math.Sign(rateTransCorr) || Math.Abs(cov) < 1e-6);
        Assert.Equal(cov, doc.GetColumnCovariance("mortgage_rate", "transactions")); // consistent

        // GetColumnMutualInformation
        var mi = doc.GetColumnMutualInformation("avg_price_gbp", "transactions");
        Assert.True(mi >= 0);
        Assert.Equal(mi, doc.GetColumnMutualInformation("avg_price_gbp", "transactions")); // consistent

        // All pairs in range
        string[] cols = { "avg_price_gbp", "transactions", "mortgage_rate", "new_supply" };
        for (int i = 0; i < cols.Length; i++)
            for (int j = i + 1; j < cols.Length; j++)
            {
                var c = doc.GetColumnCorrelation(cols[i], cols[j]);
                Assert.True(c >= -1.0 && c <= 1.0);
                Assert.True(doc.GetColumnMutualInformation(cols[i], cols[j]) >= 0);
            }

        // SaveToFile
        var outPath = TempFile("housing_market_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(rateTransCorr, loaded.GetColumnCorrelation("mortgage_rate", "transactions"), precision: 6);
        Assert.Equal(cov, loaded.GetColumnCovariance("mortgage_rate", "transactions"), precision: 6);
        Assert.Equal(mi, loaded.GetColumnMutualInformation("avg_price_gbp", "transactions"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }
}
