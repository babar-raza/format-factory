// Tests for NdjsonDocument.GetFieldMean, GetFieldSum deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R268

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R268: Tests for NdjsonDocument.GetFieldMean, GetFieldSum deeper.
/// GetFieldMean(fieldName): returns the arithmetic mean of numeric values in the field.
/// GetFieldSum(fieldName): returns the sum of numeric values in the field.
/// Covers: GetFieldMean no-throw; GetFieldMean finite; GetFieldMean consistent;
/// GetFieldMean known value; GetFieldMean save-load;
/// GetFieldSum no-throw; GetFieldSum finite; GetFieldSum consistent;
/// GetFieldSum known value; GetFieldSum save-load;
/// GetFieldSum equals GetFieldMean * RecordCount (for non-null fields);
/// dogfood CreateDoc→GetFieldMean→GetFieldSum pipeline.
/// </summary>
public class NdjsonR268GetFieldMeanAndSumDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR268GetFieldMeanAndSumDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR268_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);
        for (int i = 0; i < 80; i++)
        {
            double revenue = 1000 + rng.NextDouble() * 99000;
            double cost = 500 + rng.NextDouble() * 50000;
            int units = rng.Next(500);
            sb.AppendLine($"{{\"id\":{i},\"revenue\":{revenue:F2},\"cost\":{cost:F2},\"units\":{units}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateKnownNdjson()
    {
        var path = TempFile("known.ndjson");
        var sb = new StringBuilder();
        sb.AppendLine("{\"id\":1,\"value\":10.0}");
        sb.AppendLine("{\"id\":2,\"value\":20.0}");
        sb.AppendLine("{\"id\":3,\"value\":30.0}");
        sb.AppendLine("{\"id\":4,\"value\":40.0}");
        // Mean = 25.0, Sum = 100.0
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMean_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMean("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMean_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMean("revenue")));
    }

    [Fact]
    public void GetFieldMean_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMean("cost"), doc.GetFieldMean("cost"));
    }

    [Fact]
    public void GetFieldMean_Known_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownNdjson());
        Assert.Equal(25.0, doc.GetFieldMean("value"), precision: 6);
    }

    [Fact]
    public void GetFieldMean_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMean("revenue");
        var path = TempFile("fm_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMean("revenue"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSum_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldSum("revenue"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSum_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldSum("revenue")));
    }

    [Fact]
    public void GetFieldSum_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldSum("units"), doc.GetFieldSum("units"));
    }

    [Fact]
    public void GetFieldSum_Known_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownNdjson());
        Assert.Equal(100.0, doc.GetFieldSum("value"), precision: 6);
    }

    [Fact]
    public void GetFieldSum_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldSum("cost");
        var path = TempFile("fs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSum("cost"), precision: 6);
    }

    [Fact]
    public void GetFieldSum_Equals_Mean_Times_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownNdjson());
        var mean = doc.GetFieldMean("value");
        var sum = doc.GetFieldSum("value");
        Assert.Equal(sum, mean * doc.RecordCount, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMean_GetFieldSum_Pipeline()
    {
        // Finance — UK Companies House filing data extract
        // Annual report financial metrics for FTSE 350 constituent companies
        var path = TempFile("ch_annual_reports.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241101);

        string[] sectors = { "Financials", "Consumer Discretionary", "Industrials",
                              "Technology", "Healthcare", "Energy", "Materials",
                              "Real Estate", "Utilities", "Consumer Staples" };

        double totalRevenue = 0;
        double totalEbitda = 0;
        double totalAssets = 0;
        int recordCount = 200;

        for (int i = 0; i < recordCount; i++)
        {
            string crn = $"{i + 1000000:D8}";
            string sector = sectors[i % sectors.Length];
            int year = 2022 + (i % 3);
            // Revenue: £50m to £50bn (log-normal-ish distribution)
            double revenue = Math.Exp(rng.NextDouble() * 8 + 3) * 1e6; // £20m-£8bn
            double ebitdaMargin = 0.05 + rng.NextDouble() * 0.35;
            double ebitda = revenue * ebitdaMargin;
            double assetsToRevenue = 0.8 + rng.NextDouble() * 3.0;
            double totalAsset = revenue * assetsToRevenue;
            double netDebt = rng.NextDouble() < 0.3 ? 0 : ebitda * (rng.NextDouble() * 4);
            int employees = (int)(revenue / (25000 + rng.NextDouble() * 75000));

            totalRevenue += revenue;
            totalEbitda += ebitda;
            totalAssets += totalAsset;

            sb.AppendLine($"{{\"crn\":\"{crn}\",\"sector\":\"{sector}\",\"year\":{year},\"revenue_gbp\":{revenue:F0},\"ebitda_gbp\":{ebitda:F0},\"total_assets_gbp\":{totalAsset:F0},\"net_debt_gbp\":{netDebt:F0},\"employees\":{employees}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(recordCount, doc.RecordCount);

        // GetFieldMean — revenue
        var meanRevenue = doc.GetFieldMean("revenue_gbp");
        Assert.True(double.IsFinite(meanRevenue));
        Assert.True(meanRevenue > 0);
        Assert.Equal(meanRevenue, doc.GetFieldMean("revenue_gbp")); // consistent

        // GetFieldSum — revenue
        var sumRevenue = doc.GetFieldSum("revenue_gbp");
        Assert.True(double.IsFinite(sumRevenue));
        Assert.True(sumRevenue > 0);
        Assert.Equal(sumRevenue, doc.GetFieldSum("revenue_gbp")); // consistent

        // Mean * count ≈ sum
        Assert.Equal(sumRevenue, meanRevenue * recordCount, precision: 0);

        // GetFieldMean — ebitda
        var meanEbitda = doc.GetFieldMean("ebitda_gbp");
        Assert.True(double.IsFinite(meanEbitda));
        Assert.True(meanEbitda > 0);

        // GetFieldSum — ebitda
        var sumEbitda = doc.GetFieldSum("ebitda_gbp");
        Assert.True(sumEbitda > 0);
        Assert.Equal(sumEbitda, meanEbitda * recordCount, precision: 0);

        // Revenue > EBITDA (EBITDA is a portion of revenue)
        Assert.True(sumRevenue > sumEbitda);
        Assert.True(meanRevenue > meanEbitda);

        // GetFieldMean — total_assets
        var meanAssets = doc.GetFieldMean("total_assets_gbp");
        Assert.True(double.IsFinite(meanAssets));
        Assert.True(meanAssets > 0);

        // GetFieldSum — total_assets
        var sumAssets = doc.GetFieldSum("total_assets_gbp");
        Assert.True(sumAssets > 0);
        Assert.Equal(sumAssets, meanAssets * recordCount, precision: 0);

        // SaveToFile
        var outPath = TempFile("ch_annual_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(meanRevenue, loaded.GetFieldMean("revenue_gbp"), precision: 4);
        Assert.Equal(sumRevenue, loaded.GetFieldSum("revenue_gbp"), precision: 4);
        Assert.Equal(meanEbitda, loaded.GetFieldMean("ebitda_gbp"), precision: 4);
        Assert.Equal(sumEbitda, loaded.GetFieldSum("ebitda_gbp"), precision: 4);

        // Known values test
        var knownPath = TempFile("known_revenues.ndjson");
        var sb2 = new StringBuilder();
        sb2.AppendLine("{\"company\":\"Alpha\",\"revenue\":1000000}");
        sb2.AppendLine("{\"company\":\"Beta\",\"revenue\":2000000}");
        sb2.AppendLine("{\"company\":\"Gamma\",\"revenue\":3000000}");
        sb2.AppendLine("{\"company\":\"Delta\",\"revenue\":4000000}");
        File.WriteAllText(knownPath, sb2.ToString());
        var known = NdjsonDocument.LoadFile(knownPath);
        Assert.Equal(2500000.0, known.GetFieldMean("revenue"), precision: 2);
        Assert.Equal(10000000.0, known.GetFieldSum("revenue"), precision: 2);
    }
}
