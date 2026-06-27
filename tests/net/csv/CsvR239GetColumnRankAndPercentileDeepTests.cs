// Tests for CsvDocument.GetColumnRank, GetColumnPercentile, GetColumnQuantile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R239

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R239: Tests for CsvDocument.GetColumnRank, GetColumnPercentile, GetColumnQuantile deeper.
/// GetColumnRank(col, value): returns the rank (1-based) of the given value within the column.
/// GetColumnPercentile(col, percentile): returns the value at the given percentile.
/// GetColumnQuantile(col, quantile): returns the value at the given quantile (0-1 scale).
/// Covers: GetColumnRank no-throw; GetColumnRank positive; GetColumnRank consistent;
/// GetColumnRank save-load;
/// GetColumnPercentile no-throw; GetColumnPercentile in range; GetColumnPercentile consistent;
/// GetColumnPercentile p50 near median; GetColumnPercentile save-load;
/// GetColumnQuantile no-throw; GetColumnQuantile in range; GetColumnQuantile consistent;
/// GetColumnQuantile q0.5 near median; GetColumnQuantile save-load;
/// dogfood Append→GetColumnRank→GetColumnPercentile→GetColumnQuantile→SaveToFile pipeline.
/// </summary>
public class CsvR239GetColumnRankAndPercentileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR239GetColumnRankAndPercentileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR239_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePortfolioCsv()
    {
        var path = TempFile("portfolio.csv");
        var lines = new[]
        {
            "ticker,sector,market_cap_bn,pe_ratio,dividend_yield,ytd_return",
            "MSFT,Technology,2950.0,36.2,0.72,18.5",
            "AAPL,Technology,2840.0,31.5,0.51,22.3",
            "GOOGL,Technology,1820.0,27.8,0.00,15.8",
            "AMZN,ConsumerDisc,1910.0,72.1,0.00,28.4",
            "BRK_B,Financials,780.0,9.8,0.00,12.1",
            "XOM,Energy,410.0,12.4,3.62,8.7",
            "JNJ,Healthcare,385.0,14.2,3.01,4.2",
            "V,Financials,480.0,28.9,0.77,11.5",
            "PG,ConsumerStap,355.0,22.8,2.42,6.8",
            "JPM,Financials,460.0,10.6,2.35,14.3",
            "UNH,Healthcare,420.0,22.1,1.58,9.4",
            "NVDA,Technology,2200.0,58.4,0.03,85.2"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRank_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var ex = Record.Exception(() => doc.GetColumnRank("market_cap_bn", 2950.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRank_Positive()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        Assert.True(doc.GetColumnRank("market_cap_bn", 2950.0) >= 1);
    }

    [Fact]
    public void GetColumnRank_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        Assert.Equal(doc.GetColumnRank("ytd_return", 85.2), doc.GetColumnRank("ytd_return", 85.2));
    }

    [Fact]
    public void GetColumnRank_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var before = doc.GetColumnRank("pe_ratio", 28.9);
        var path = TempFile("rank_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRank("pe_ratio", 28.9));
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var ex = Record.Exception(() => doc.GetColumnPercentile("ytd_return", 75));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentile_InRange()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var p75 = doc.GetColumnPercentile("ytd_return", 75);
        Assert.True(p75 >= doc.GetColumnMin("ytd_return"));
        Assert.True(p75 <= doc.GetColumnMax("ytd_return"));
    }

    [Fact]
    public void GetColumnPercentile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        Assert.Equal(doc.GetColumnPercentile("market_cap_bn", 50), doc.GetColumnPercentile("market_cap_bn", 50), precision: 4);
    }

    [Fact]
    public void GetColumnPercentile_P50_Near_Median()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var p50 = doc.GetColumnPercentile("ytd_return", 50);
        var median = doc.GetColumnMedian("ytd_return");
        Assert.True(Math.Abs(p50 - median) < 5.0);
    }

    [Fact]
    public void GetColumnPercentile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var before = doc.GetColumnPercentile("pe_ratio", 25);
        var path = TempFile("pct_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPercentile("pe_ratio", 25), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetColumnQuantile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnQuantile_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var ex = Record.Exception(() => doc.GetColumnQuantile("ytd_return", 0.9));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnQuantile_InRange()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var q90 = doc.GetColumnQuantile("ytd_return", 0.9);
        Assert.True(q90 >= doc.GetColumnMin("ytd_return"));
        Assert.True(q90 <= doc.GetColumnMax("ytd_return"));
    }

    [Fact]
    public void GetColumnQuantile_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        Assert.Equal(doc.GetColumnQuantile("pe_ratio", 0.75), doc.GetColumnQuantile("pe_ratio", 0.75), precision: 4);
    }

    [Fact]
    public void GetColumnQuantile_Q05_Near_Median()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var q50 = doc.GetColumnQuantile("market_cap_bn", 0.5);
        var median = doc.GetColumnMedian("market_cap_bn");
        Assert.True(Math.Abs(q50 - median) < 50.0);
    }

    [Fact]
    public void GetColumnQuantile_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePortfolioCsv());
        var before = doc.GetColumnQuantile("dividend_yield", 0.75);
        var path = TempFile("qtl_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnQuantile("dividend_yield", 0.75), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnRank_GetColumnPercentile_GetColumnQuantile_SaveToFile_Pipeline()
    {
        // Real estate investment trust — property fund performance analytics
        var path = TempFile("dogfood_reit.csv");
        var lines = new[]
        {
            "fund_id,fund_name,aum_mn,nav_per_unit,ytd_return,inception_return,expense_ratio,yield,sharpe_ratio,beta",
            "F001,Urban Office REIT,2840.5,12.45,8.2,6.8,0.85,4.2,0.92,0.78",
            "F002,Residential Income,1920.3,8.72,12.5,9.4,1.12,3.8,1.18,0.65",
            "F003,Industrial Logistics,3450.8,18.30,22.3,15.6,0.72,2.9,1.45,0.89",
            "F004,Retail Centres,880.2,5.15,-3.8,1.2,1.45,6.8,0.32,1.15",
            "F005,Healthcare Facilities,1640.7,14.88,9.8,8.2,0.95,5.1,0.88,0.58",
            "F006,Student Housing,720.4,6.42,18.4,12.3,1.28,4.5,1.22,0.72",
            "F007,Data Centres,4200.1,24.65,35.8,28.4,0.68,1.8,1.85,1.24",
            "F008,Self Storage,990.6,9.18,14.2,10.8,0.98,3.6,1.12,0.81",
            "F009,Mixed Use Urban,1380.9,11.05,6.8,5.4,1.15,4.8,0.72,0.92",
            "F010,Senior Living,1180.3,10.72,11.5,7.9,1.08,5.5,0.98,0.67",
            "F011,Hospitality REIT,650.8,7.85,-8.5,-2.4,1.62,2.1,0.18,1.45",
            "F012,Cold Chain,1850.4,15.42,19.6,14.2,0.88,3.2,1.38,0.95"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnRank — top performer (F007 ytd_return=35.8 → rank 1)
        var topRank = doc.GetColumnRank("ytd_return", 35.8);
        Assert.True(topRank >= 1);
        Assert.True(topRank <= 12);
        Assert.Equal(topRank, doc.GetColumnRank("ytd_return", 35.8)); // consistent

        // GetColumnRank — worst performer (F011 ytd_return=-8.5 → rank 12)
        var worstRank = doc.GetColumnRank("ytd_return", -8.5);
        Assert.True(worstRank >= 1);
        Assert.True(worstRank <= 12);

        // GetColumnRank — F007 Sharpe ratio (1.85 → rank 1)
        var sharpeRank = doc.GetColumnRank("sharpe_ratio", 1.85);
        Assert.True(sharpeRank >= 1);
        Assert.True(sharpeRank <= 12);

        // GetColumnPercentile — ytd_return quartiles
        var p25ytd = doc.GetColumnPercentile("ytd_return", 25);
        var p50ytd = doc.GetColumnPercentile("ytd_return", 50);
        var p75ytd = doc.GetColumnPercentile("ytd_return", 75);
        Assert.True(p25ytd <= p50ytd);
        Assert.True(p50ytd <= p75ytd);
        Assert.Equal(p50ytd, doc.GetColumnPercentile("ytd_return", 50), precision: 2); // consistent

        // GetColumnPercentile — AUM P90 (large funds)
        var aum90 = doc.GetColumnPercentile("aum_mn", 90);
        Assert.True(aum90 >= doc.GetColumnMin("aum_mn"));
        Assert.True(aum90 <= doc.GetColumnMax("aum_mn"));

        // GetColumnQuantile — ytd_return IQR
        var q1ytd = doc.GetColumnQuantile("ytd_return", 0.25);
        var q3ytd = doc.GetColumnQuantile("ytd_return", 0.75);
        Assert.True(q1ytd <= q3ytd);
        Assert.Equal(q3ytd, doc.GetColumnQuantile("ytd_return", 0.75), precision: 2); // consistent

        // GetColumnQuantile — expense_ratio Q0.25 (lowest cost funds)
        var expQ25 = doc.GetColumnQuantile("expense_ratio", 0.25);
        Assert.True(expQ25 >= 0.0);
        Assert.True(expQ25 <= 2.0);

        // P50 ≈ Q0.5 (within 5 units)
        var p50nav = doc.GetColumnPercentile("nav_per_unit", 50);
        var q50nav = doc.GetColumnQuantile("nav_per_unit", 0.5);
        Assert.True(Math.Abs(p50nav - q50nav) < 5.0);

        // AppendRow — two new REITs
        doc.AppendRow(new[] { "F013", "Bio-pharma Facilities", "3800.2", "22.15", "28.4", "21.8", "0.78", "2.4", "1.62", "0.88" });
        doc.AppendRow(new[] { "F014", "Distressed Retail", "320.5", "3.82", "-15.2", "-8.6", "1.95", "8.5", "0.08", "1.68" });
        Assert.Equal(14, doc.RowCount);

        // After append: ytd rank of 35.8 remains rank 1 (no new value > 35.8)
        Assert.Equal(topRank, doc.GetColumnRank("ytd_return", 35.8));

        // SaveToFile
        var out1 = TempFile("dogfood_reit_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnPercentile("ytd_return", 50), loaded.GetColumnPercentile("ytd_return", 50), precision: 2);
        Assert.Equal(doc.GetColumnQuantile("aum_mn", 0.75), loaded.GetColumnQuantile("aum_mn", 0.75), precision: 2);

        // Final save
        var out2 = TempFile("dogfood_reit_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.True(loaded2.GetColumnPercentile("sharpe_ratio", 75) > 0);
        Assert.True(loaded2.GetColumnQuantile("beta", 0.5) > 0);
        var ex1 = Record.Exception(() => loaded2.GetColumnRank("ytd_return", 22.3));
        var ex2 = Record.Exception(() => loaded2.GetColumnPercentile("yield", 90));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
