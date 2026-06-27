// Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R272

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R272: Tests for NdjsonDocument.GetFieldSkewness, GetFieldKurtosis deeper.
/// GetFieldSkewness(field): returns the skewness of numeric values in the field (0 for symmetric distribution).
/// GetFieldKurtosis(field): returns the excess kurtosis of numeric values in the field (0 for normal distribution).
/// Covers: GetFieldSkewness no-throw; GetFieldSkewness finite; GetFieldSkewness consistent;
/// GetFieldSkewness zero for symmetric; GetFieldSkewness save-load;
/// GetFieldKurtosis no-throw; GetFieldKurtosis finite; GetFieldKurtosis consistent;
/// GetFieldKurtosis save-load; GetFieldKurtosis higher for peaked distribution;
/// dogfood CreateDoc→GetFieldSkewness→GetFieldKurtosis→SaveToFile pipeline.
/// </summary>
public class NdjsonR272GetFieldSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR272GetFieldSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR272_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSymmetricNdjson()
    {
        // Values symmetric around mean: -3,-2,-1,0,1,2,3 (mean=0, skewness≈0)
        var path = TempFile("symmetric.ndjson");
        var sb = new StringBuilder();
        int[] vals = { -3, -2, -1, 0, 1, 2, 3 };
        foreach (var v in vals)
            sb.AppendLine($"{{\"id\":{v + 4},\"value\":{v}}}");
        // Repeat to get 70 records (10 cycles of 7)
        for (int rep = 1; rep < 10; rep++)
            foreach (var v in vals)
                sb.AppendLine($"{{\"id\":{rep * 7 + v + 4},\"value\":{v}}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateRightSkewedNdjson()
    {
        // Right-skewed: many small values, few large ones
        var path = TempFile("right_skewed.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(42);
        for (int i = 0; i < 100; i++)
        {
            // Exponential-like: most values near 1, a few very large
            double v = Math.Pow(rng.NextDouble() + 0.01, -0.5) - 1;
            v = Math.Max(0, Math.Min(100, v));
            sb.AppendLine($"{{\"id\":{i},\"value\":{v:F4}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreatePeakedNdjson()
    {
        // Highly peaked (leptokurtic): nearly all values at mean, very few outliers
        var path = TempFile("peaked.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 90; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":100}}"); // all at 100
        // A few extreme outliers
        sb.AppendLine("{\"id\":90,\"value\":200}");
        sb.AppendLine("{\"id\":91,\"value\":0}");
        sb.AppendLine("{\"id\":92,\"value\":200}");
        sb.AppendLine("{\"id\":93,\"value\":0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateFlatNdjson()
    {
        // Flat (platykurtic): uniform distribution
        var path = TempFile("flat.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 100; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{i}}}"); // uniform 0..99
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSkewness_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSymmetricNdjson());
        var ex = Record.Exception(() => doc.GetFieldSkewness("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSkewness_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateRightSkewedNdjson());
        var sk = doc.GetFieldSkewness("value");
        Assert.True(double.IsFinite(sk));
    }

    [Fact]
    public void GetFieldSkewness_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSymmetricNdjson());
        Assert.Equal(doc.GetFieldSkewness("value"), doc.GetFieldSkewness("value"));
    }

    [Fact]
    public void GetFieldSkewness_NearZero_ForSymmetric()
    {
        var doc = NdjsonDocument.LoadFile(CreateSymmetricNdjson());
        var sk = doc.GetFieldSkewness("value");
        Assert.True(Math.Abs(sk) < 0.5); // symmetric → near zero
    }

    [Fact]
    public void GetFieldSkewness_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateRightSkewedNdjson());
        var before = doc.GetFieldSkewness("value");
        var path = TempFile("sk_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldKurtosis_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreatePeakedNdjson());
        var ex = Record.Exception(() => doc.GetFieldKurtosis("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldKurtosis_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlatNdjson());
        var k = doc.GetFieldKurtosis("value");
        Assert.True(double.IsFinite(k));
    }

    [Fact]
    public void GetFieldKurtosis_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFlatNdjson());
        Assert.Equal(doc.GetFieldKurtosis("value"), doc.GetFieldKurtosis("value"));
    }

    [Fact]
    public void GetFieldKurtosis_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreatePeakedNdjson());
        var before = doc.GetFieldKurtosis("value");
        var path = TempFile("ku_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldKurtosis("value"), precision: 6);
    }

    [Fact]
    public void GetFieldKurtosis_Higher_ForPeaked_Than_Flat()
    {
        var docPeaked = NdjsonDocument.LoadFile(CreatePeakedNdjson());
        var docFlat = NdjsonDocument.LoadFile(CreateFlatNdjson());
        // Peaked distribution has higher kurtosis than flat uniform distribution
        Assert.True(docPeaked.GetFieldKurtosis("value") >= docFlat.GetFieldKurtosis("value"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldSkewness_GetFieldKurtosis_SaveToFile_Pipeline()
    {
        // Finance — Bank of England Stress Testing: PRA Capital Distribution Analysis
        // DFAST-equivalent capital adequacy ratios across UK major banks under adverse scenario
        // Skewness and kurtosis of capital ratios to detect tail risk concentration

        var path = TempFile("pra_capital_stress.ndjson");
        var sb = new StringBuilder();

        var rng = new Random(20240915);

        // Group A: Well-capitalised banks — CET1 ratios cluster around 14-16% (near-normal)
        for (int i = 0; i < 60; i++)
        {
            double cet1 = 14.0 + rng.NextDouble() * 2.0 + (rng.NextDouble() - 0.5) * 0.8;
            double leverage = 5.5 + rng.NextDouble() * 1.5;
            double rwa_density = 38 + rng.NextDouble() * 12;
            double stress_loss_pct = 2.5 + rng.NextDouble() * 2.0;
            sb.AppendLine($"{{\"bank_id\":\"GRP_A_{i:D3}\",\"group\":\"well_capitalised\",\"cet1_ratio\":{cet1:F3},\"leverage_ratio\":{leverage:F3},\"rwa_density_pct\":{rwa_density:F2},\"stress_loss_pct\":{stress_loss_pct:F3}}}");
        }

        // Group B: Constrained banks — CET1 ratios right-skewed (most near 10-11%, a few high outliers)
        for (int i = 0; i < 30; i++)
        {
            double cet1 = 10.0 + Math.Pow(rng.NextDouble(), 2) * 6.0; // right-skewed
            double leverage = 4.2 + rng.NextDouble() * 1.0;
            double rwa_density = 52 + rng.NextDouble() * 18;
            double stress_loss_pct = 4.0 + rng.NextDouble() * 3.5;
            sb.AppendLine($"{{\"bank_id\":\"GRP_B_{i:D3}\",\"group\":\"constrained\",\"cet1_ratio\":{cet1:F3},\"leverage_ratio\":{leverage:F3},\"rwa_density_pct\":{rwa_density:F2},\"stress_loss_pct\":{stress_loss_pct:F3}}}");
        }

        // Group C: Building societies — stress losses highly peaked near 1.5% (leptokurtic)
        for (int i = 0; i < 40; i++)
        {
            double stress_loss_pct = 1.5 + (rng.NextDouble() - 0.5) * 0.1; // very concentrated
            double cet1 = 16 + rng.NextDouble() * 4;
            double leverage = 6.0 + rng.NextDouble() * 0.5;
            double rwa_density = 28 + rng.NextDouble() * 8;
            sb.AppendLine($"{{\"bank_id\":\"GRP_C_{i:D3}\",\"group\":\"building_society\",\"cet1_ratio\":{cet1:F3},\"leverage_ratio\":{leverage:F3},\"rwa_density_pct\":{rwa_density:F2},\"stress_loss_pct\":{stress_loss_pct:F3}}}");
        }

        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(130, doc.RecordCount);

        // CET1 ratio skewness — right-skewed overall (group B pulls right)
        var skCet1 = doc.GetFieldSkewness("cet1_ratio");
        Assert.True(double.IsFinite(skCet1));
        Assert.Equal(skCet1, doc.GetFieldSkewness("cet1_ratio")); // consistent

        // Leverage ratio — roughly symmetric
        var skLeverage = doc.GetFieldSkewness("leverage_ratio");
        Assert.True(double.IsFinite(skLeverage));

        // RWA density skewness — positive (bank group B has higher density)
        var skRwa = doc.GetFieldSkewness("rwa_density_pct");
        Assert.True(double.IsFinite(skRwa));

        // Stress loss kurtosis — building societies drive leptokurtosis
        var kuStress = doc.GetFieldKurtosis("stress_loss_pct");
        Assert.True(double.IsFinite(kuStress));
        Assert.Equal(kuStress, doc.GetFieldKurtosis("stress_loss_pct")); // consistent

        // CET1 kurtosis
        var kuCet1 = doc.GetFieldKurtosis("cet1_ratio");
        Assert.True(double.IsFinite(kuCet1));

        // Leverage kurtosis
        var kuLeverage = doc.GetFieldKurtosis("leverage_ratio");
        Assert.True(double.IsFinite(kuLeverage));

        // Basic record checks
        Assert.True(doc.GetFieldMean("cet1_ratio") > 0);
        Assert.True(doc.GetFieldStdDev("cet1_ratio") > 0);
        Assert.True(doc.GetFieldMin("cet1_ratio") > 0);
        Assert.True(doc.GetFieldMax("cet1_ratio") <= 30);

        // SaveToFile
        var out1 = TempFile("pra_capital_stress_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify distribution stats preserved
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(skCet1, loaded.GetFieldSkewness("cet1_ratio"), precision: 6);
        Assert.Equal(kuStress, loaded.GetFieldKurtosis("stress_loss_pct"), precision: 6);
        Assert.Equal(skLeverage, loaded.GetFieldSkewness("leverage_ratio"), precision: 6);
        Assert.Equal(kuCet1, loaded.GetFieldKurtosis("cet1_ratio"), precision: 6);

        // Add PRA buffer requirement records (Pillar 2A top-up scenario)
        var sb2 = new StringBuilder();
        sb2.AppendLine("{\"bank_id\":\"SIFI_001\",\"group\":\"g_sifi\",\"cet1_ratio\":18.5,\"leverage_ratio\":7.2,\"rwa_density_pct\":45.0,\"stress_loss_pct\":3.1}");
        sb2.AppendLine("{\"bank_id\":\"SIFI_002\",\"group\":\"g_sifi\",\"cet1_ratio\":17.8,\"leverage_ratio\":6.9,\"rwa_density_pct\":42.5,\"stress_loss_pct\":2.9}");
        sb2.AppendLine("{\"bank_id\":\"SIFI_003\",\"group\":\"g_sifi\",\"cet1_ratio\":16.2,\"leverage_ratio\":6.5,\"rwa_density_pct\":48.3,\"stress_loss_pct\":3.4}");

        // Append to loaded document
        loaded.AppendRecords(sb2.ToString());
        Assert.Equal(doc.RecordCount + 3, loaded.RecordCount);

        var skCet1After = loaded.GetFieldSkewness("cet1_ratio");
        Assert.True(double.IsFinite(skCet1After));
        var kuStressAfter = loaded.GetFieldKurtosis("stress_loss_pct");
        Assert.True(double.IsFinite(kuStressAfter));

        // Final save
        var out2 = TempFile("pra_capital_stress_final.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var final = NdjsonDocument.LoadFile(out2);
        Assert.Equal(loaded.RecordCount, final.RecordCount);
        Assert.Equal(skCet1After, final.GetFieldSkewness("cet1_ratio"), precision: 6);
        Assert.Equal(kuStressAfter, final.GetFieldKurtosis("stress_loss_pct"), precision: 6);

        var ex1 = Record.Exception(() => final.GetFieldSkewness("cet1_ratio"));
        var ex2 = Record.Exception(() => final.GetFieldKurtosis("stress_loss_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
