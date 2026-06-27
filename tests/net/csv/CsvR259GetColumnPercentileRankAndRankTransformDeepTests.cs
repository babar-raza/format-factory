// Tests for CsvDocument.GetColumnPercentileRank, GetColumnRankTransform deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R259

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R259: Tests for CsvDocument.GetColumnPercentileRank, GetColumnRankTransform deeper.
/// GetColumnPercentileRank(colName, value): returns the percentile rank (0-100) of the given value.
/// GetColumnRankTransform(colName): returns an array of per-row rank values (1-based).
/// Covers: GetColumnPercentileRank no-throw; GetColumnPercentileRank in [0,100];
/// GetColumnPercentileRank consistent; GetColumnPercentileRank save-load;
/// GetColumnRankTransform no-throw; GetColumnRankTransform non-null;
/// GetColumnRankTransform length equals RowCount; GetColumnRankTransform contains 1;
/// GetColumnRankTransform consistent; GetColumnRankTransform save-load;
/// dogfood CreateDoc→GetColumnPercentileRank→GetColumnRankTransform pipeline.
/// </summary>
public class CsvR259GetColumnPercentileRankAndRankTransformDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR259GetColumnPercentileRankAndRankTransformDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR259_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("fund_id,return_pct,sharpe_ratio,volatility_pct,max_drawdown_pct,aum_gbm");
        var rng = new Random(20240901);
        for (int i = 0; i < 150; i++)
        {
            double ret = -5 + rng.NextDouble() * 30;
            double sharpe = -0.5 + rng.NextDouble() * 3.0;
            double vol = 5 + rng.NextDouble() * 25;
            double mdd = -40 + rng.NextDouble() * 35;
            double aum = 50 + rng.NextDouble() * 5000;
            sb.AppendLine($"F{i:D5},{ret:F2},{sharpe:F3},{vol:F2},{mdd:F2},{aum:F0}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnPercentileRank
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPercentileRank_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnPercentileRank("return_pct", 10.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPercentileRank_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var pr = doc.GetColumnPercentileRank("return_pct", doc.GetColumnMedian("return_pct"));
        Assert.True(pr >= 0.0 && pr <= 100.0);
    }

    [Fact]
    public void GetColumnPercentileRank_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        double val = doc.GetColumnMean("sharpe_ratio");
        Assert.Equal(doc.GetColumnPercentileRank("sharpe_ratio", val),
                     doc.GetColumnPercentileRank("sharpe_ratio", val));
    }

    [Fact]
    public void GetColumnPercentileRank_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        double val = doc.GetColumnMean("volatility_pct");
        var before = doc.GetColumnPercentileRank("volatility_pct", val);
        var path = TempFile("pr_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPercentileRank("volatility_pct", val), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRankTransform
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRankTransform_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnRankTransform("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRankTransform_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnRankTransform("return_pct"));
    }

    [Fact]
    public void GetColumnRankTransform_LengthEqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRankTransform("return_pct").Length);
    }

    [Fact]
    public void GetColumnRankTransform_ContainsOne()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ranks = doc.GetColumnRankTransform("sharpe_ratio");
        bool hasOne = false;
        foreach (var r in ranks) if (r == 1) { hasOne = true; break; }
        Assert.True(hasOne);
    }

    [Fact]
    public void GetColumnRankTransform_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var r1 = doc.GetColumnRankTransform("return_pct");
        var r2 = doc.GetColumnRankTransform("return_pct");
        Assert.Equal(r1.Length, r2.Length);
        for (int i = 0; i < r1.Length; i++)
            Assert.Equal(r1[i], r2[i]);
    }

    [Fact]
    public void GetColumnRankTransform_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnRankTransform("return_pct");
        var path = TempFile("rt_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnRankTransform("return_pct");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnPercentileRank_GetColumnRankTransform_Pipeline()
    {
        // Financial regulation — FCA Asset Management Market Study
        // Fund performance ranking for retail investment product comparison
        var path = TempFile("fca_fund_ranking.csv");
        var sb = new StringBuilder();
        sb.AppendLine("fund_id,isin,fund_type,ann_return_3yr,ann_vol_3yr,sharpe_3yr,max_drawdown,ocf_pct,fund_size_gbm,esg_score,sustainability_label");

        var rng = new Random(20240901);
        string[] fundTypes = { "UK Equity", "Global Equity", "Fixed Income", "Multi-Asset", "Property", "Absolute Return" };
        string[] labels = { "Sustainable", "Responsible", "Impact", "ESG Focus", "None" };
        string[] isins = {};

        for (int i = 0; i < 200; i++)
        {
            string fundId = $"GB{1000000 + i:D7}A";
            string isin = $"GB{rng.Next(10000000):D8}";
            string fundType = fundTypes[rng.Next(fundTypes.Length)];
            double ret3y = fundType == "Fixed Income" ? (-2 + rng.NextDouble() * 10) :
                           fundType == "Property" ? (-5 + rng.NextDouble() * 15) :
                           (-8 + rng.NextDouble() * 30);
            double vol3y = fundType == "Fixed Income" ? (2 + rng.NextDouble() * 6) :
                           fundType == "Absolute Return" ? (3 + rng.NextDouble() * 8) :
                           (8 + rng.NextDouble() * 22);
            double sharpe = ret3y / Math.Max(vol3y, 1.0);
            double mdd = -ret3y * 2 - rng.NextDouble() * 15;
            double ocf = 0.1 + rng.NextDouble() * 2.4;
            double size = 10 + rng.NextDouble() * 4990;
            double esg = 20 + rng.NextDouble() * 80;
            string label = rng.NextDouble() < 0.35 ? labels[rng.Next(4)] : "None";
            sb.AppendLine($"{fundId},{isin},{fundType},{ret3y:F2},{vol3y:F2},{sharpe:F4},{mdd:F2},{ocf:F2},{size:F0},{esg:F1},{label}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(11, doc.ColumnCount);

        // GetColumnPercentileRank — return ranking
        var prReturn50 = doc.GetColumnPercentileRank("ann_return_3yr", doc.GetColumnMedian("ann_return_3yr"));
        Assert.True(prReturn50 >= 0.0 && prReturn50 <= 100.0);
        Assert.True(prReturn50 >= 30.0 && prReturn50 <= 70.0); // near 50th percentile

        var prReturnTop = doc.GetColumnPercentileRank("ann_return_3yr", doc.GetColumnMax("ann_return_3yr"));
        Assert.True(prReturnTop >= 90.0 && prReturnTop <= 100.0);

        var prSharpe50 = doc.GetColumnPercentileRank("sharpe_3yr", doc.GetColumnMean("sharpe_3yr"));
        Assert.True(prSharpe50 >= 0.0 && prSharpe50 <= 100.0);

        // Consistent
        Assert.Equal(prReturn50, doc.GetColumnPercentileRank("ann_return_3yr",
                     doc.GetColumnMedian("ann_return_3yr")));

        // OCF: lower is better — check percentile
        var prOcfLow = doc.GetColumnPercentileRank("ocf_pct", doc.GetColumnMin("ocf_pct"));
        Assert.True(prOcfLow >= 0.0 && prOcfLow <= 10.0); // minimum should be at very low percentile

        // GetColumnRankTransform — fund rankings
        var ranksReturn = doc.GetColumnRankTransform("ann_return_3yr");
        Assert.NotNull(ranksReturn);
        Assert.Equal(200, ranksReturn.Length);

        bool hasOne = false;
        foreach (var r in ranksReturn) if (r == 1) { hasOne = true; break; }
        Assert.True(hasOne);

        foreach (var r in ranksReturn)
            Assert.True(r >= 1);

        // Consistent
        var ranksReturn2 = doc.GetColumnRankTransform("ann_return_3yr");
        for (int i = 0; i < ranksReturn.Length; i++)
            Assert.Equal(ranksReturn[i], ranksReturn2[i]);

        // Sharpe ranks
        var ranksSharpe = doc.GetColumnRankTransform("sharpe_3yr");
        Assert.Equal(200, ranksSharpe.Length);

        // ESG ranks
        var ranksEsg = doc.GetColumnRankTransform("esg_score");
        Assert.Equal(200, ranksEsg.Length);

        // Basic stats
        Assert.True(doc.GetColumnMean("ann_return_3yr") >= -10.0); // returns roughly reasonable
        Assert.True(doc.GetColumnMin("ocf_pct") <= doc.GetColumnMax("ocf_pct"));

        // SaveToFile
        var outPath = TempFile("fca_fund_ranking_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(200, loaded.RowCount);
        Assert.Equal(prReturn50, loaded.GetColumnPercentileRank("ann_return_3yr",
                     doc.GetColumnMedian("ann_return_3yr")), precision: 4);
        var loadedRanks = loaded.GetColumnRankTransform("ann_return_3yr");
        Assert.Equal(ranksReturn.Length, loadedRanks.Length);
        for (int i = 0; i < ranksReturn.Length; i++)
            Assert.Equal(ranksReturn[i], loadedRanks[i]);
    }
}
