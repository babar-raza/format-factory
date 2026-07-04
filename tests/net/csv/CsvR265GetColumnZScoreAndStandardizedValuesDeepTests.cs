// Tests for CsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R265

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R265: Tests for CsvDocument.GetColumnZScore, GetColumnStandardizedValues deeper.
/// GetColumnZScore(colName, value): returns the z-score of the given value relative to the column.
/// GetColumnStandardizedValues(colName): returns the list of z-scores for all values in the column.
/// Covers: GetColumnZScore no-throw; GetColumnZScore zero for mean; GetColumnZScore consistent;
/// GetColumnZScore save-load; GetColumnStandardizedValues no-throw;
/// GetColumnStandardizedValues count equals RowCount; GetColumnStandardizedValues consistent;
/// GetColumnStandardizedValues mean near zero; GetColumnStandardizedValues save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnStandardizedValues pipeline.
/// </summary>
public class CsvR265GetColumnZScoreAndStandardizedValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR265GetColumnZScoreAndStandardizedValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR265_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id,return_pct,volatility_pct,sharpe_ratio");
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            double ret = Math.Round(-5 + rng.NextDouble() * 25, 3);
            double vol = Math.Round(5 + rng.NextDouble() * 25, 3);
            double sharpe = Math.Round(ret / vol, 4);
            sb.AppendLine($"{i},{ret},{vol},{sharpe}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        double mean = doc.GetColumnMean("return_pct");
        var ex = Record.Exception(() => doc.GetColumnZScore("return_pct", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Zero_ForMean()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        double mean = doc.GetColumnMean("return_pct");
        Assert.Equal(0.0, doc.GetColumnZScore("return_pct", mean), precision: 6);
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnZScore("volatility_pct", 15.0),
                     doc.GetColumnZScore("volatility_pct", 15.0));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnZScore("return_pct", 10.0);
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("return_pct", 10.0), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnStandardizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnStandardizedValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnStandardizedValues("return_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnStandardizedValues_Count_Equals_RowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.RowCount, doc.GetColumnStandardizedValues("return_pct").Length);
    }

    [Fact]
    public void GetColumnStandardizedValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnStandardizedValues("volatility_pct");
        var v2 = doc.GetColumnStandardizedValues("volatility_pct");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnStandardizedValues_Mean_Near_Zero()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetColumnStandardizedValues("return_pct");
        double sum = 0;
        foreach (var v in vals) sum += v;
        Assert.Equal(0.0, sum / vals.Length, precision: 4);
    }

    [Fact]
    public void GetColumnStandardizedValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnStandardizedValues("sharpe_ratio");
        var path = TempFile("sv_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var after = loaded.GetColumnStandardizedValues("sharpe_ratio");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnStandardizedValues_Pipeline()
    {
        // Property — HM Land Registry House Price Index: 2024 Regional Analysis
        // Z-score normalisation to identify affordability ratio outliers by local authority
        var path = TempFile("hmlr_regional_hpi.csv");
        var sb = new StringBuilder();
        sb.AppendLine("la_code,la_name,region,avg_price_gbp,price_growth_pct,affordability_ratio,transaction_volume,detached_pct,flat_pct");

        var rng = new Random(20240901);
        string[] regions = { "London", "South East", "East of England", "South West",
                             "West Midlands", "East Midlands", "Yorkshire", "North West",
                             "North East", "Wales" };
        double[] regionMeans = { 500000, 380000, 320000, 295000, 235000, 220000, 195000, 205000, 155000, 195000 };

        for (int i = 0; i < 200; i++)
        {
            int regIdx = i % regions.Length;
            string region = regions[regIdx];
            string la = $"E090{i % 90 + 10:D2}{i % 100 + 100}";
            string name = $"LA {i}";
            double basePrice = regionMeans[regIdx];
            double price = Math.Round(basePrice * (0.7 + rng.NextDouble() * 0.6), 0);
            double growth = Math.Round(-2 + rng.NextDouble() * 18, 2);
            double affordability = Math.Round(price / (30000 + rng.NextDouble() * 20000), 2);
            int volume = 200 + rng.Next(2800);
            double detached = Math.Round(15 + rng.NextDouble() * 50, 1);
            double flat = Math.Round(5 + rng.NextDouble() * 40, 1);
            sb.AppendLine($"{la},{name},{region},{price:F0},{growth},{affordability},{volume},{detached},{flat}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(200, doc.RowCount);
        Assert.Equal(9, doc.ColumnCount);

        // GetColumnZScore for avg_price_gbp
        double meanPrice = doc.GetColumnMean("avg_price_gbp");
        Assert.True(meanPrice > 0);
        Assert.Equal(0.0, doc.GetColumnZScore("avg_price_gbp", meanPrice), precision: 4);
        Assert.Equal(doc.GetColumnZScore("avg_price_gbp", 300000.0),
                     doc.GetColumnZScore("avg_price_gbp", 300000.0)); // consistent

        // Z-score for 1 SD above/below mean
        double sdPrice = doc.GetColumnStdDev("avg_price_gbp");
        Assert.True(sdPrice > 0);
        Assert.Equal(1.0, doc.GetColumnZScore("avg_price_gbp", meanPrice + sdPrice), precision: 4);
        Assert.Equal(-1.0, doc.GetColumnZScore("avg_price_gbp", meanPrice - sdPrice), precision: 4);

        // GetColumnZScore for affordability_ratio
        double meanAff = doc.GetColumnMean("affordability_ratio");
        Assert.Equal(0.0, doc.GetColumnZScore("affordability_ratio", meanAff), precision: 4);

        // GetColumnStandardizedValues for avg_price_gbp
        var stdPrice = doc.GetColumnStandardizedValues("avg_price_gbp");
        Assert.Equal(doc.RowCount, stdPrice.Length);
        double sumZ = 0; foreach (var v in stdPrice) sumZ += v;
        Assert.Equal(0.0, sumZ / stdPrice.Length, precision: 4);
        Assert.Equal(stdPrice, doc.GetColumnStandardizedValues("avg_price_gbp"));

        // GetColumnStandardizedValues for affordability_ratio
        var stdAff = doc.GetColumnStandardizedValues("affordability_ratio");
        Assert.Equal(doc.RowCount, stdAff.Length);

        // GetColumnStandardizedValues for price_growth_pct
        var stdGrowth = doc.GetColumnStandardizedValues("price_growth_pct");
        Assert.Equal(doc.RowCount, stdGrowth.Length);

        // SaveToFile
        var outPath = TempFile("hmlr_hpi_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(doc.GetColumnZScore("avg_price_gbp", 250000.0),
                     loaded.GetColumnZScore("avg_price_gbp", 250000.0), precision: 6);
        var loadedStd = loaded.GetColumnStandardizedValues("avg_price_gbp");
        Assert.Equal(stdPrice.Length, loadedStd.Length);
        for (int i = 0; i < stdPrice.Length; i++)
            Assert.Equal(stdPrice[i], loadedStd[i], precision: 6);
    }
}
