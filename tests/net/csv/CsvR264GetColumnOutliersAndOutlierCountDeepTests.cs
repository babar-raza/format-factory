// Tests for CsvDocument.GetColumnOutliers, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R264

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R264: Tests for CsvDocument.GetColumnOutliers, GetColumnOutlierCount deeper.
/// GetColumnOutliers(colName): returns list of outlier values (IQR method: outside Q1-1.5*IQR or Q3+1.5*IQR).
/// GetColumnOutlierCount(colName): returns the count of outliers in the column.
/// Covers: GetColumnOutlierCount no-throw; GetColumnOutlierCount non-negative;
/// GetColumnOutlierCount consistent; GetColumnOutlierCount zero for uniform;
/// GetColumnOutlierCount save-load; GetColumnOutliers no-throw;
/// GetColumnOutliers count equals GetColumnOutlierCount; GetColumnOutliers consistent;
/// GetColumnOutliers save-load; GetColumnOutlierCount le RowCount;
/// dogfood CreateDoc→GetColumnOutliers→GetColumnOutlierCount pipeline.
/// </summary>
public class CsvR264GetColumnOutliersAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR264GetColumnOutliersAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR264_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("fund_id,nav,aum_gbpm,sharpe_ratio,max_drawdown_pct");
        var rng = new Random(20240815);
        for (int i = 0; i < 90; i++)
        {
            double nav = Math.Round(80 + rng.NextDouble() * 40, 2);
            double aum = Math.Round(100 + rng.NextDouble() * 900, 1);
            double sharpe = Math.Round(-0.5 + rng.NextDouble() * 3.0, 3);
            double dd = Math.Round(5 + rng.NextDouble() * 30, 2);
            sb.AppendLine($"F{i:D4},{nav},{aum},{sharpe},{dd}");
        }
        // Add outliers
        sb.AppendLine("F9000,250.00,15000.0,5.5,2.5");
        sb.AppendLine("F9001,10.00,8.5,-3.5,78.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,nav");
        for (int i = 0; i < 50; i++)
            sb.AppendLine($"{i},100");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("nav"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnOutlierCount("nav") >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnOutlierCount("nav"), doc.GetColumnOutlierCount("nav"));
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("nav"));
    }

    [Fact]
    public void GetColumnOutlierCount_Le_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnOutlierCount("nav") <= doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnOutlierCount("nav");
        var path = TempFile("oc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("nav"));
    }

    // -------------------------------------------------------------------------
    // GetColumnOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutliers_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnOutliers("nav"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutliers_Count_Equals_OutlierCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnOutlierCount("nav"), doc.GetColumnOutliers("nav").Count);
    }

    [Fact]
    public void GetColumnOutliers_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var o1 = doc.GetColumnOutliers("nav");
        var o2 = doc.GetColumnOutliers("nav");
        Assert.Equal(o1, o2);
    }

    [Fact]
    public void GetColumnOutliers_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnOutliers("aum_gbpm");
        var path = TempFile("outliers_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutliers("aum_gbpm"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnOutliers_GetColumnOutlierCount_Pipeline()
    {
        // Asset management — FCA Authorised Fund Manager Performance Review
        // Detecting outlier fund performance metrics for supervisory attention
        var path = TempFile("fca_fund_review.csv");
        var sb = new StringBuilder();
        sb.AppendLine("fund_id,fund_name,fund_type,aum_gbpm,ter_pct,ann_return_pct,volatility_pct,max_drawdown_pct,sharpe_ratio,info_ratio");

        var rng = new Random(20240901);
        string[] types = { "OEIC", "Unit Trust", "SICAV", "ETF", "Investment Trust" };

        for (int i = 0; i < 180; i++)
        {
            string ftype = types[i % types.Length];
            double aum = Math.Round(50 + rng.NextDouble() * 950, 1);
            double ter = Math.Round(0.15 + rng.NextDouble() * 1.5, 3);
            double ret = Math.Round(-5 + rng.NextDouble() * 20, 2);
            double vol = Math.Round(8 + rng.NextDouble() * 18, 2);
            double dd = Math.Round(5 + rng.NextDouble() * 30, 2);
            double sharpe = Math.Round(ret / vol, 3);
            double ir = Math.Round(-1 + rng.NextDouble() * 3, 3);
            sb.AppendLine($"F{i:D5},\"Fund {i} ({ftype})\",{ftype},{aum},{ter},{ret},{vol},{dd},{sharpe},{ir}");
        }
        // Outlier funds
        sb.AppendLine("F99001,\"High Fee Underperformer\",OEIC,45.0,3.25,-15.5,35.0,62.0,-0.443,-2.1");
        sb.AppendLine("F99002,\"Star Performer\",ETF,8500.0,0.05,35.0,12.0,4.5,2.917,3.5");
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(182, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // Outlier count for aum_gbpm
        var outlierCountAum = doc.GetColumnOutlierCount("aum_gbpm");
        Assert.True(outlierCountAum >= 0);
        Assert.True(outlierCountAum <= doc.RowCount);
        Assert.Equal(outlierCountAum, doc.GetColumnOutlierCount("aum_gbpm")); // consistent

        // Outlier values for aum_gbpm
        var outliersAum = doc.GetColumnOutliers("aum_gbpm");
        Assert.Equal(outlierCountAum, outliersAum.Count);
        Assert.Equal(outliersAum, doc.GetColumnOutliers("aum_gbpm")); // consistent

        // TER outliers (high fee outlier expected)
        var outlierCountTer = doc.GetColumnOutlierCount("ter_pct");
        Assert.True(outlierCountTer >= 0);
        var outliersTer = doc.GetColumnOutliers("ter_pct");
        Assert.Equal(outlierCountTer, outliersTer.Count);

        // Max drawdown outliers (high drawdown outlier expected)
        var outlierCountDd = doc.GetColumnOutlierCount("max_drawdown_pct");
        Assert.True(outlierCountDd >= 0);
        var outliersDd = doc.GetColumnOutliers("max_drawdown_pct");
        Assert.Equal(outlierCountDd, outliersDd.Count);

        // Annual return outliers
        var outlierCountRet = doc.GetColumnOutlierCount("ann_return_pct");
        Assert.True(outlierCountRet >= 0);
        var outliersRet = doc.GetColumnOutliers("ann_return_pct");
        Assert.Equal(outlierCountRet, outliersRet.Count);

        // Sharpe ratio outliers
        var outlierCountSharpe = doc.GetColumnOutlierCount("sharpe_ratio");
        Assert.True(outlierCountSharpe >= 0);
        var outliersSharpe = doc.GetColumnOutliers("sharpe_ratio");
        Assert.Equal(outlierCountSharpe, outliersSharpe.Count);

        // Basic column stats
        Assert.True(doc.GetColumnMean("aum_gbpm") > 0);
        Assert.True(doc.GetColumnStdDev("ann_return_pct") > 0);

        // SaveToFile
        var outPath = TempFile("fca_fund_review_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(outlierCountAum, loaded.GetColumnOutlierCount("aum_gbpm"));
        Assert.Equal(outliersAum, loaded.GetColumnOutliers("aum_gbpm"));

        // Uniform sub-test
        var path2 = TempFile("uniform_funds.csv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("fund_id,ter_pct");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"F{i:D4},0.75");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = CsvDocument.LoadFile(path2);
        Assert.Equal(0, doc2.GetColumnOutlierCount("ter_pct"));
        Assert.Empty(doc2.GetColumnOutliers("ter_pct"));
    }
}
