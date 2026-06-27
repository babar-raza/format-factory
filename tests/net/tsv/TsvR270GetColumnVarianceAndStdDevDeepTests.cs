// Tests for TsvDocument.GetColumnVariance, GetColumnStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R270

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R270: Tests for TsvDocument.GetColumnVariance, GetColumnStdDev deeper.
/// GetColumnVariance(colName): returns the sample variance of numeric values in the column.
/// GetColumnStdDev(colName): returns the sample standard deviation; equals sqrt(variance).
/// Covers: GetColumnVariance no-throw; GetColumnVariance non-negative; GetColumnVariance zero for uniform;
/// GetColumnVariance consistent; GetColumnVariance save-load;
/// GetColumnStdDev no-throw; GetColumnStdDev non-negative; GetColumnStdDev zero for uniform;
/// GetColumnStdDev consistent; GetColumnStdDev save-load;
/// GetColumnVariance equals GetColumnStdDev squared; dogfood pipeline.
/// </summary>
public class TsvR270GetColumnVarianceAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR270GetColumnVarianceAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR270_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 10; i++) sb.AppendLine($"R{i:D2}\t{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tmeasure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2}\t42.5");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnVariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnVariance("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnVariance_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnVariance("value") >= 0.0);
    }

    [Fact]
    public void GetColumnVariance_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnVariance("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnVariance("value"), doc.GetColumnVariance("value"));
    }

    [Fact]
    public void GetColumnVariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnVariance("value");
        var path = TempFile("var_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnVariance("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnStdDev("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnStdDev("value") >= 0.0);
    }

    [Fact]
    public void GetColumnStdDev_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnStdDev("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnStdDev("value"), doc.GetColumnStdDev("value"));
    }

    [Fact]
    public void GetColumnStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnStdDev("value");
        var path = TempFile("sd_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetColumnVariance_Equals_StdDev_Squared()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var sd = doc.GetColumnStdDev("value");
        var var_ = doc.GetColumnVariance("value");
        Assert.Equal(sd * sd, var_, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnVariance_GetColumnStdDev_Pipeline()
    {
        // Finance — Bank of England / FCA: Consumer Credit Market Data 2024
        // Household credit market statistics for financial stability monitoring
        // Variance/StdDev detect concentration risk and outlier firm behaviour

        var path = TempFile("boe_consumer_credit_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("firm_id\tfirm_name\toutstanding_balance_gbpm\tnew_lending_gbpm\tdefault_rate_pct\taverage_apr_pct\twrite_off_rate_pct\tprofit_margin_pct");

        var rng = new Random(20240701);
        string[] firms = {
            "Barclaycard", "HSBC_CC", "Lloyds_CC", "NatWest_CC", "Santander_UK",
            "Capital_One_UK", "NewDay_Ltd", "Virgin_Money_CC", "Amex_UK", "MBNA_UK",
            "Tesco_Bank", "M&S_Bank", "Sainsbury_Bank", "Asda_Money", "Post_Office_Money",
            "Vanquis_Bank", "Aqua_Credit", "Opus_Credit", "Chrome_CC", "Granite_Financial"
        };

        for (int i = 0; i < firms.Length; i++)
        {
            double balance = 800 + rng.NextDouble() * 12000;
            double newLend = 50 + rng.NextDouble() * 2000;
            double defaultRate = 0.5 + rng.NextDouble() * 4.5 + (i == 15 ? 6.0 : 0); // Vanquis outlier
            double apr = 12 + rng.NextDouble() * 28 + (i == 16 ? 25 : 0); // Aqua outlier
            double writeOff = 0.3 + rng.NextDouble() * 3.2;
            double margin = 2 + rng.NextDouble() * 8;
            sb.AppendLine($"FIRM{i:D3}\t{firms[i]}\t{balance:F1}\t{newLend:F1}\t{defaultRate:F2}\t{apr:F1}\t{writeOff:F2}\t{margin:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(firms.Length, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Variance and StdDev for default rate
        var defaultVar = doc.GetColumnVariance("default_rate_pct");
        var defaultSd = doc.GetColumnStdDev("default_rate_pct");
        Assert.True(defaultVar >= 0.0);
        Assert.True(defaultSd >= 0.0);
        Assert.True(defaultVar > 0.0); // rates vary
        Assert.Equal(defaultSd * defaultSd, defaultVar, precision: 4);
        Assert.Equal(defaultVar, doc.GetColumnVariance("default_rate_pct")); // consistent
        Assert.Equal(defaultSd, doc.GetColumnStdDev("default_rate_pct")); // consistent

        // APR variance and StdDev
        var aprVar = doc.GetColumnVariance("average_apr_pct");
        var aprSd = doc.GetColumnStdDev("average_apr_pct");
        Assert.True(aprVar >= 0.0);
        Assert.True(aprSd >= 0.0);
        Assert.Equal(aprSd * aprSd, aprVar, precision: 4);

        // Balance variance
        var balVar = doc.GetColumnVariance("outstanding_balance_gbpm");
        var balSd = doc.GetColumnStdDev("outstanding_balance_gbpm");
        Assert.True(balVar >= 0.0);
        Assert.Equal(balSd * balSd, balVar, precision: 2);

        // Margin variance (should be smaller than APR variance)
        var marginVar = doc.GetColumnVariance("profit_margin_pct");
        Assert.True(marginVar >= 0.0);

        // SaveToFile
        var outPath = TempFile("boe_cc_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(defaultVar, loaded.GetColumnVariance("default_rate_pct"), precision: 6);
        Assert.Equal(defaultSd, loaded.GetColumnStdDev("default_rate_pct"), precision: 6);
        Assert.Equal(aprVar, loaded.GetColumnVariance("average_apr_pct"), precision: 6);
        Assert.Equal(aprSd, loaded.GetColumnStdDev("average_apr_pct"), precision: 6);
        Assert.Equal(balVar, loaded.GetColumnVariance("outstanding_balance_gbpm"), precision: 3);
    }
}
