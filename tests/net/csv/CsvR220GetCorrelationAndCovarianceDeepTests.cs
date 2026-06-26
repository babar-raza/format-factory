// Tests for CsvDocument.GetCorrelation, GetCovariance, GetZScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R220

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R220: Tests for CsvDocument.GetCorrelation, GetCovariance, GetZScore deeper.
/// GetCorrelation(col1, col2): returns the Pearson correlation coefficient.
/// GetCovariance(col1, col2): returns the covariance between two numeric columns.
/// GetZScore(colName, rowIndex): returns the z-score of a value within its column.
/// Covers: GetCorrelation no-throw; GetCorrelation in [-1,1]; GetCorrelation consistent;
/// GetCorrelation self is 1; GetCorrelation save-load;
/// GetCovariance no-throw; GetCovariance finite; GetCovariance consistent;
/// GetCovariance symmetric; GetCovariance save-load;
/// GetZScore no-throw; GetZScore finite; GetZScore consistent; GetZScore save-load;
/// GetZScore all rows finite;
/// dogfood LoadFile→GetCorrelation→GetCovariance→GetZScore→SaveToFile pipeline.
/// </summary>
public class CsvR220GetCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR220GetCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR220_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStockCsv()
    {
        var path = TempFile("stocks.csv");
        var content =
            "Ticker,Open,High,Low,Close,Volume\n" +
            "AAPL,182.50,185.20,181.80,184.60,52000000\n" +
            "GOOGL,138.20,140.50,137.60,139.80,22000000\n" +
            "MSFT,415.30,418.70,414.20,417.50,28000000\n" +
            "AMZN,185.60,187.90,184.10,186.70,35000000\n" +
            "NVDA,875.20,890.40,872.10,888.30,48000000\n" +
            "META,520.40,525.80,518.20,523.60,31000000\n" +
            "TSLA,245.80,250.20,243.40,248.10,75000000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetCorrelation("Open", "Close"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var r = doc.GetCorrelation("Open", "Close");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(doc.GetCorrelation("Open", "High"), doc.GetCorrelation("Open", "High"));
    }

    [Fact]
    public void GetCorrelation_Self_IsOne()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(1.0, doc.GetCorrelation("Close", "Close"), 4);
    }

    [Fact]
    public void GetCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetCorrelation("Open", "Close");
        var path = TempFile("corr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCorrelation("Open", "Close"), 3);
    }

    [Fact]
    public void GetCorrelation_Open_Close_Positive()
    {
        // Open and Close prices tend to be strongly positively correlated
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.True(doc.GetCorrelation("Open", "Close") > 0);
    }

    // -------------------------------------------------------------------------
    // GetCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCovariance_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetCovariance("Open", "Close"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCovariance_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var cov = doc.GetCovariance("Open", "Close");
        Assert.True(double.IsFinite(cov));
    }

    [Fact]
    public void GetCovariance_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(doc.GetCovariance("High", "Low"), doc.GetCovariance("High", "Low"));
    }

    [Fact]
    public void GetCovariance_Symmetric()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(
            doc.GetCovariance("Open", "Close"),
            doc.GetCovariance("Close", "Open"),
            3);
    }

    [Fact]
    public void GetCovariance_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetCovariance("High", "Volume");
        var path = TempFile("cov_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCovariance("High", "Volume"), 2);
    }

    // -------------------------------------------------------------------------
    // GetZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var ex = Record.Exception(() => doc.GetZScore("Close", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScore_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.True(double.IsFinite(doc.GetZScore("Close", 0)));
    }

    [Fact]
    public void GetZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        Assert.Equal(doc.GetZScore("Close", 3), doc.GetZScore("Close", 3));
    }

    [Fact]
    public void GetZScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        var before = doc.GetZScore("Close", 2);
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScore("Close", 2), 4);
    }

    [Fact]
    public void GetZScore_AllRows_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateStockCsv());
        for (int i = 0; i < doc.GetRowCount(); i++)
            Assert.True(double.IsFinite(doc.GetZScore("Close", i)));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCorrelation_GetCovariance_GetZScore_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_portfolio.csv");
        var content =
            "Fund,NAV,YTD_Return,StdDev,SharpeRatio,AUM\n" +
            "GrowthPlus,248.50,18.4,14.2,1.28,4200000000\n" +
            "ValueCore,182.30,12.1,9.8,1.15,3100000000\n" +
            "TechFocus,315.80,24.6,18.5,1.42,2800000000\n" +
            "IncomeBlend,142.60,8.9,7.2,1.08,5600000000\n" +
            "GlobalGrowth,205.40,15.7,12.9,1.22,3900000000\n" +
            "SmallCapValue,128.90,21.3,16.8,1.35,1200000000\n" +
            "BondMix,98.20,5.4,4.1,1.02,7800000000\n" +
            "DividendFocus,165.70,9.8,8.6,1.11,4500000000\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetCorrelation — NAV vs YTD_Return
        var corrNAV_YTD = doc.GetCorrelation("NAV", "YTD_Return");
        Assert.True(corrNAV_YTD >= -1.0 && corrNAV_YTD <= 1.0);
        Assert.Equal(corrNAV_YTD, doc.GetCorrelation("NAV", "YTD_Return")); // consistent

        // GetCorrelation — self
        Assert.Equal(1.0, doc.GetCorrelation("NAV", "NAV"), 4);

        // GetCorrelation — YTD_Return vs SharpeRatio (should be positive)
        var corrYTD_Sharpe = doc.GetCorrelation("YTD_Return", "SharpeRatio");
        Assert.True(corrYTD_Sharpe >= -1.0 && corrYTD_Sharpe <= 1.0);
        Assert.True(corrYTD_Sharpe > 0);

        // GetCovariance — NAV vs YTD_Return
        var covNAV_YTD = doc.GetCovariance("NAV", "YTD_Return");
        Assert.True(double.IsFinite(covNAV_YTD));
        Assert.Equal(covNAV_YTD, doc.GetCovariance("NAV", "YTD_Return")); // consistent

        // GetCovariance — symmetric
        Assert.Equal(
            doc.GetCovariance("StdDev", "YTD_Return"),
            doc.GetCovariance("YTD_Return", "StdDev"),
            3);

        // GetZScore — all rows for NAV
        for (int i = 0; i < doc.GetRowCount(); i++)
            Assert.True(double.IsFinite(doc.GetZScore("NAV", i)));

        // GetZScore — TechFocus has highest NAV (index 2) — positive z-score
        var zTech = doc.GetZScore("NAV", 2); // TechFocus NAV=315.80
        Assert.True(zTech > 0);

        // GetZScore — BondMix has lowest NAV (index 6) — negative z-score
        var zBond = doc.GetZScore("NAV", 6); // BondMix NAV=98.20
        Assert.True(zBond < 0);

        // AddRow and recheck
        doc.AddRow(new[] { "RealEstate", "195.20", "13.2", "11.4", "1.18", "2200000000" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(double.IsFinite(doc.GetCovariance("NAV", "YTD_Return")));
        Assert.True(doc.GetCorrelation("NAV", "NAV") >= 0.999);

        // SaveToFile
        var savePath = TempFile("dogfood_portfolio_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetCorrelation("NAV", "YTD_Return"), loaded.GetCorrelation("NAV", "YTD_Return"), 3);
        Assert.Equal(doc.GetCovariance("NAV", "YTD_Return"), loaded.GetCovariance("NAV", "YTD_Return"), 2);
        Assert.Equal(doc.GetZScore("NAV", 0), loaded.GetZScore("NAV", 0), 4);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("NAV", cols);
        Assert.Contains("SharpeRatio", cols);

        // Final save
        var path2 = TempFile("dogfood_portfolio_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetCorrelation("NAV", "YTD_Return"), loaded2.GetCorrelation("NAV", "YTD_Return"), 3);
        Assert.Equal(loaded.GetCovariance("NAV", "SharpeRatio"), loaded2.GetCovariance("NAV", "SharpeRatio"), 2);
    }
}
