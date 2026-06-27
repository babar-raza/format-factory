// Tests for CsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R270

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R270: Tests for CsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
/// GetColumnZScore(colName, value): returns the z-score of the given value within the column distribution.
/// GetColumnOutlierCount(colName, threshold): returns the count of values with |z-score| > threshold.
/// Covers: GetColumnZScore no-throw; GetColumnZScore near-zero for mean; GetColumnZScore consistent;
/// GetColumnZScore save-load; GetColumnOutlierCount no-throw; GetColumnOutlierCount non-negative;
/// GetColumnOutlierCount zero for very-high threshold; GetColumnOutlierCount le RowCount;
/// GetColumnOutlierCount consistent; GetColumnOutlierCount save-load; dogfood pipeline.
/// </summary>
public class CsvR270GetColumnZScoreAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR270GetColumnZScoreAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR270_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateNormalCsv()
    {
        var path = TempFile("normal.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,measure");
        var rng = new Random(99);
        for (int i = 0; i < 80; i++)
            sb.AppendLine($"R{i:D3},{100 + rng.NextDouble() * 20 - 10:F2}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateOutlierCsv()
    {
        var path = TempFile("outlier.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        for (int i = 0; i < 95; i++)
            sb.AppendLine($"R{i:D3},{50 + (i % 8) - 4}");
        sb.AppendLine("R095,500"); // extreme outlier
        sb.AppendLine("R096,-200"); // extreme outlier
        sb.AppendLine("R097,600"); // extreme outlier
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateNormalCsv());
        var mean = doc.GetColumnMean("measure");
        var ex = Record.Exception(() => doc.GetColumnZScore("measure", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_NearZero_ForMean()
    {
        var doc = CsvDocument.LoadFile(CreateNormalCsv());
        var mean = doc.GetColumnMean("measure");
        var z = doc.GetColumnZScore("measure", mean);
        Assert.True(Math.Abs(z) < 0.5);
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateNormalCsv());
        var mean = doc.GetColumnMean("measure");
        Assert.Equal(doc.GetColumnZScore("measure", mean), doc.GetColumnZScore("measure", mean));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateNormalCsv());
        var mean = doc.GetColumnMean("measure");
        var before = doc.GetColumnZScore("measure", mean);
        var path = TempFile("zs_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("measure", mean), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateOutlierCsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("value", 3.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateOutlierCsv());
        Assert.True(doc.GetColumnOutlierCount("value", 3.0) >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForVeryHighThreshold()
    {
        var doc = CsvDocument.LoadFile(CreateNormalCsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("measure", 100.0));
    }

    [Fact]
    public void GetColumnOutlierCount_LeRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateOutlierCsv());
        Assert.True(doc.GetColumnOutlierCount("value", 0.5) <= doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOutlierCsv());
        Assert.Equal(doc.GetColumnOutlierCount("value", 3.0), doc.GetColumnOutlierCount("value", 3.0));
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateOutlierCsv());
        var before = doc.GetColumnOutlierCount("value", 3.0);
        var path = TempFile("oc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("value", 3.0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnOutlierCount_Pipeline()
    {
        // Finance — Bank of England: Solvency II Insurance Stress Test Data 2024
        // Sector-wide insurer capital and solvency data for systemic risk monitoring
        // Z-score analysis flags insurers with extreme capital ratios needing supervisory review

        var path = TempFile("boe_solv2_stress_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("firm_id,firm_name,scr_ratio_pct,own_funds_gbp_m,loss_absorbing_capacity_pct,net_premium_written_gbp_m,combined_ratio_pct,solvency_ii_tier1_ratio_pct");

        var rng = new Random(20240615);
        string[] firmNames = {
            "Aviva", "Legal_General", "Prudential", "Standard_Life_Aberdeen", "RSA_Insurance",
            "Direct_Line", "Admiral", "Zurich_UK", "Allianz_UK", "AXA_UK",
            "Chubb_UK", "Liberty_Mutual_UK", "Hiscox", "Lloyd_s_of_London", "Brit_Insurance",
            "Beazley", "Markel_UK", "QBE_UK", "Tokio_Marine_UK", "MS_Amlin"
        };

        double[] scrRatios = new double[firmNames.Length];
        double[] ownFunds = new double[firmNames.Length];
        double[] lossCap = new double[firmNames.Length];
        double[] premiums = new double[firmNames.Length];
        double[] combinedRatios = new double[firmNames.Length];
        double[] tier1Ratios = new double[firmNames.Length];

        for (int i = 0; i < firmNames.Length; i++)
        {
            scrRatios[i] = 160 + rng.NextDouble() * 80 + (i == 7 ? 200 : 0); // Zurich outlier
            ownFunds[i] = 2000 + rng.NextDouble() * 8000;
            lossCap[i] = 30 + rng.NextDouble() * 20;
            premiums[i] = 500 + rng.NextDouble() * 3000;
            combinedRatios[i] = 90 + rng.NextDouble() * 20 + (i == 14 ? 40 : 0); // Brit outlier
            tier1Ratios[i] = 65 + rng.NextDouble() * 25;
            sb.AppendLine($"FIRM{i:D3},{firmNames[i]},{scrRatios[i]:F1},{ownFunds[i]:F0},{lossCap[i]:F1},{premiums[i]:F0},{combinedRatios[i]:F1},{tier1Ratios[i]:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(firmNames.Length, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Z-score of mean should be near zero
        var scrMean = doc.GetColumnMean("scr_ratio_pct");
        var zMean = doc.GetColumnZScore("scr_ratio_pct", scrMean);
        Assert.True(Math.Abs(zMean) < 0.5);

        // Zurich (index 7) SCR ratio is an outlier
        var zZurich = doc.GetColumnZScore("scr_ratio_pct", scrRatios[7]);
        Assert.True(zZurich > 1.5); // well above mean

        // Brit Insurance (index 14) combined ratio outlier
        var combinedMean = doc.GetColumnMean("combined_ratio_pct");
        var zBrit = doc.GetColumnZScore("combined_ratio_pct", combinedRatios[14]);
        Assert.True(zBrit > 1.5);

        // Outlier counts
        var outlierScr = doc.GetColumnOutlierCount("scr_ratio_pct", 2.0);
        Assert.True(outlierScr >= 0 && outlierScr <= doc.RowCount);

        var outlierCombined = doc.GetColumnOutlierCount("combined_ratio_pct", 2.0);
        Assert.True(outlierCombined >= 0 && outlierCombined <= doc.RowCount);

        // Very high threshold → no outliers
        Assert.Equal(0, doc.GetColumnOutlierCount("scr_ratio_pct", 100.0));

        // Consistency
        Assert.Equal(zZurich, doc.GetColumnZScore("scr_ratio_pct", scrRatios[7]));
        Assert.Equal(outlierScr, doc.GetColumnOutlierCount("scr_ratio_pct", 2.0));

        // SaveToFile
        var outPath = TempFile("boe_solv2_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zZurich, loaded.GetColumnZScore("scr_ratio_pct", scrRatios[7]), precision: 6);
        Assert.Equal(outlierScr, loaded.GetColumnOutlierCount("scr_ratio_pct", 2.0));
        Assert.Equal(zMean, loaded.GetColumnZScore("scr_ratio_pct", scrMean), precision: 6);
        Assert.Equal(zBrit, loaded.GetColumnZScore("combined_ratio_pct", combinedRatios[14]), precision: 6);
    }
}
