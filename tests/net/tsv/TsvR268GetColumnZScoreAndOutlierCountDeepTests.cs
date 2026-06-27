// Tests for TsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R268

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R268: Tests for TsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
/// GetColumnZScore(colName, value): returns the z-score of the given value within the column distribution.
/// GetColumnOutlierCount(colName, threshold): returns the count of values with |z-score| > threshold.
/// Covers: GetColumnZScore no-throw; GetColumnZScore near-zero for mean; GetColumnZScore consistent;
/// GetColumnZScore save-load; GetColumnOutlierCount no-throw; GetColumnOutlierCount non-negative;
/// GetColumnOutlierCount zero when threshold is very high; GetColumnOutlierCount le RowCount;
/// GetColumnOutlierCount consistent; GetColumnOutlierCount save-load;
/// dogfood OFWAT water sector performance data pipeline.
/// </summary>
public class TsvR268GetColumnZScoreAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR268GetColumnZScoreAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR268_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateNormalTsv()
    {
        var path = TempFile("normal.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        var rng = new Random(42);
        double sum = 0;
        var vals = new double[100];
        for (int i = 0; i < 100; i++) { vals[i] = 50 + rng.NextDouble() * 10 - 5; sum += vals[i]; }
        double mean = sum / 100;
        foreach (var v in vals) sb.AppendLine($"{v:F3}\t{v:F3}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateOutlierTsv()
    {
        var path = TempFile("outlier.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tscore");
        // 97 normal values around 50, 3 extreme outliers
        for (int i = 0; i < 97; i++) sb.AppendLine($"R{i:D3}\t{50 + (i % 10) - 5}");
        sb.AppendLine("R097\t200"); // extreme outlier
        sb.AppendLine("R098\t-100"); // extreme outlier
        sb.AppendLine("R099\t300"); // extreme outlier
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateNormalTsv());
        var mean = doc.GetColumnMean("value");
        var ex = Record.Exception(() => doc.GetColumnZScore("value", mean));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_NearZero_ForMean()
    {
        var doc = TsvDocument.LoadFile(CreateNormalTsv());
        var mean = doc.GetColumnMean("value");
        var z = doc.GetColumnZScore("value", mean);
        Assert.True(Math.Abs(z) < 0.5); // z-score of mean should be near 0
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateNormalTsv());
        var mean = doc.GetColumnMean("value");
        Assert.Equal(doc.GetColumnZScore("value", mean), doc.GetColumnZScore("value", mean));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateNormalTsv());
        var mean = doc.GetColumnMean("value");
        var before = doc.GetColumnZScore("value", mean);
        var path = TempFile("zs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("value", mean), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateOutlierTsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("score", 3.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateOutlierTsv());
        Assert.True(doc.GetColumnOutlierCount("score", 3.0) >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForVeryHighThreshold()
    {
        var doc = TsvDocument.LoadFile(CreateNormalTsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("value", 100.0)); // threshold of 100 sigma
    }

    [Fact]
    public void GetColumnOutlierCount_LeRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateOutlierTsv());
        var count = doc.GetColumnOutlierCount("score", 0.5);
        Assert.True(count <= doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateOutlierTsv());
        Assert.Equal(doc.GetColumnOutlierCount("score", 3.0), doc.GetColumnOutlierCount("score", 3.0));
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateOutlierTsv());
        var before = doc.GetColumnOutlierCount("score", 3.0);
        var path = TempFile("oc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("score", 3.0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnOutlierCount_Pipeline()
    {
        // Water Sector — OFWAT: PR24 Company Performance Commitments 2024-25
        // Water company key performance indicator (KPI) data
        // Z-score detection identifies underperforming companies needing regulatory intervention

        var path = TempFile("ofwat_pr24_kpis.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("company\tleakage_ml_day\tcustomer_contacts_per_1000\tpipe_bursts_per_1000km\twater_quality_score\tsupply_interruptions_mins\tco2_kg_per_ml");

        var rng = new Random(20240401);
        // 17 water companies with realistic PR24 KPI ranges
        string[] companies = {
            "Anglian", "Affinity", "Bristol", "Cambridge", "Dee_Valley",
            "Essex_Suffolk", "Hartlepool", "Northumbrian", "Portsmouth",
            "South_East", "Southern", "South_Staffs", "South_West",
            "Sutton_East_Surrey", "Thames", "United_Utilities", "Wessex", "Yorkshire"
        };

        double[] leakages = new double[companies.Length];
        double[] contacts = new double[companies.Length];
        double[] bursts = new double[companies.Length];
        double[] quality = new double[companies.Length];
        double[] interruptions = new double[companies.Length];
        double[] emissions = new double[companies.Length];

        for (int i = 0; i < companies.Length; i++)
        {
            // Normal performance range with 1-2 companies as outliers
            leakages[i] = 120 + rng.NextDouble() * 80 + (i == 14 ? 300 : 0); // Thames outlier
            contacts[i] = 25 + rng.NextDouble() * 15 + (i == 16 ? 80 : 0);   // Wessex outlier
            bursts[i] = 15 + rng.NextDouble() * 10;
            quality[i] = 99.0 + rng.NextDouble() * 0.9;
            interruptions[i] = 5 + rng.NextDouble() * 20 + (i == 14 ? 120 : 0); // Thames outlier
            emissions[i] = 0.8 + rng.NextDouble() * 0.4;
            sb.AppendLine($"{companies[i]}\t{leakages[i]:F1}\t{contacts[i]:F1}\t{bursts[i]:F1}\t{quality[i]:F3}\t{interruptions[i]:F1}\t{emissions[i]:F3}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(companies.Length, doc.RowCount);
        Assert.Equal(7, doc.ColumnCount);

        // Z-score of mean should be near zero
        var leakMean = doc.GetColumnMean("leakage_ml_day");
        var zMean = doc.GetColumnZScore("leakage_ml_day", leakMean);
        Assert.True(Math.Abs(zMean) < 0.5);

        // Thames water (index 14) leakage is an outlier → high z-score
        var zThames = doc.GetColumnZScore("leakage_ml_day", leakages[14]);
        Assert.True(zThames > 2.0); // far above mean

        // Outlier count at threshold 2.0
        var outlierLeakage = doc.GetColumnOutlierCount("leakage_ml_day", 2.0);
        Assert.True(outlierLeakage >= 0);
        Assert.True(outlierLeakage <= doc.RowCount);

        // Outlier count at very high threshold = 0
        Assert.Equal(0, doc.GetColumnOutlierCount("leakage_ml_day", 100.0));

        // Customer contacts — Wessex outlier
        var contactsMean = doc.GetColumnMean("customer_contacts_per_1000");
        var zContactsMean = doc.GetColumnZScore("customer_contacts_per_1000", contactsMean);
        Assert.True(Math.Abs(zContactsMean) < 0.5);
        var outlierContacts = doc.GetColumnOutlierCount("customer_contacts_per_1000", 2.0);
        Assert.True(outlierContacts >= 0 && outlierContacts <= doc.RowCount);

        // Quality score — near-uniform → few outliers at 2.0 sigma
        var qualityOutliers = doc.GetColumnOutlierCount("water_quality_score", 2.0);
        Assert.True(qualityOutliers <= doc.RowCount);

        // Consistency
        Assert.Equal(zThames, doc.GetColumnZScore("leakage_ml_day", leakages[14]));
        Assert.Equal(outlierLeakage, doc.GetColumnOutlierCount("leakage_ml_day", 2.0));

        // SaveToFile
        var outPath = TempFile("ofwat_pr24_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zThames, loaded.GetColumnZScore("leakage_ml_day", leakages[14]), precision: 6);
        Assert.Equal(outlierLeakage, loaded.GetColumnOutlierCount("leakage_ml_day", 2.0));
        Assert.Equal(zMean, loaded.GetColumnZScore("leakage_ml_day", leakMean), precision: 6);
    }
}
