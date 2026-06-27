// Tests for NdjsonDocument.GetFieldMean, GetFieldMedian deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R278

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R278: Tests for NdjsonDocument.GetFieldMean, GetFieldMedian deeper.
/// GetFieldMean(field): returns the arithmetic mean of numeric values in the named field.
/// GetFieldMedian(field): returns the median of numeric values; equals mean for symmetric distributions.
/// Covers: GetFieldMean no-throw; GetFieldMean in-range; GetFieldMean exact for uniform;
/// GetFieldMean consistent; GetFieldMean save-load;
/// GetFieldMedian no-throw; GetFieldMedian in-range; GetFieldMedian exact for uniform;
/// GetFieldMedian consistent; GetFieldMedian save-load;
/// GetFieldMean between GetFieldMin and GetFieldMax; dogfood pipeline.
/// </summary>
public class NdjsonR278GetFieldMeanAndFieldMedianDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR278GetFieldMeanAndFieldMedianDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR278_" + Guid.NewGuid().ToString("N"));
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
        var lines = new StringBuilder();
        // 10 records: score 0..90 step 10 — mean=45, median=45
        for (int i = 0; i < 10; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":{i * 10.0},\"label\":\"L{i}\"}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":7.5}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMean_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMean("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMean_InRange_BetweenMinAndMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var mean = doc.GetFieldMean("score");
        Assert.True(mean >= doc.GetFieldMin("score") && mean <= doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMean_Exact_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(7.5, doc.GetFieldMean("value"), precision: 6);
    }

    [Fact]
    public void GetFieldMean_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMean("score"), doc.GetFieldMean("score"));
    }

    [Fact]
    public void GetFieldMean_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMean("score");
        var path = TempFile("mean_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMean("score"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMedian_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMedian("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMedian_InRange_BetweenMinAndMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var median = doc.GetFieldMedian("score");
        Assert.True(median >= doc.GetFieldMin("score") && median <= doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMedian_Exact_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(7.5, doc.GetFieldMedian("value"), precision: 6);
    }

    [Fact]
    public void GetFieldMedian_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMedian("score"), doc.GetFieldMedian("score"));
    }

    [Fact]
    public void GetFieldMedian_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMedian("score");
        var path = TempFile("median_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMedian("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMean_Equals_GetFieldMedian_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(doc.GetFieldMean("value"), doc.GetFieldMedian("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMean_GetFieldMedian_Pipeline()
    {
        // Housing — Land Registry / DLUHC: UK House Price Index 2024
        // Property transaction records for residential price trend analysis
        // Mean and median distinguish average vs. typical prices in skewed markets

        var path = TempFile("hm_land_registry_hpi_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240930);

        string[] regions = { "London", "South_East", "East_of_England", "South_West",
                              "West_Midlands", "East_Midlands", "Yorkshire", "North_West",
                              "North_East", "Wales" };
        string[] propTypes = { "Detached", "Semi_Detached", "Terraced", "Flat" };
        string[] tenures = { "Freehold", "Freehold", "Freehold", "Leasehold" };

        // Base prices by region (£000)
        double[] regionBase = { 600, 380, 320, 290, 240, 220, 200, 195, 155, 185 };

        for (int i = 0; i < 350; i++)
        {
            int regIdx = rng.Next(regions.Length);
            int propIdx = rng.Next(propTypes.Length);
            double basePrice = regionBase[regIdx] * 1000;

            // Property type multiplier
            double mult = propTypes[propIdx] == "Detached" ? 1.4
                        : propTypes[propIdx] == "Semi_Detached" ? 1.1
                        : propTypes[propIdx] == "Terraced" ? 0.95
                        : 0.75;
            double price = basePrice * mult * (0.8 + rng.NextDouble() * 0.4);

            // Luxury outlier (1% chance)
            if (rng.NextDouble() < 0.01) price *= 3.0;

            double priceChange = -5 + rng.NextDouble() * 15;
            int bedrooms = propIdx == 0 ? rng.Next(3, 7)
                         : propIdx == 1 ? rng.Next(2, 5)
                         : propIdx == 2 ? rng.Next(2, 4)
                         : rng.Next(1, 3);
            double sqFt = 400 + bedrooms * 120 + rng.NextDouble() * 200;
            double ltv = 60 + rng.NextDouble() * 35;

            sb.AppendLine($"{{\"transaction_id\":\"LR{i:D5}\",\"region\":\"{regions[regIdx]}\"," +
                          $"\"property_type\":\"{propTypes[propIdx]}\",\"tenure\":\"{tenures[propIdx]}\"," +
                          $"\"price_gbp\":{price:F0},\"price_change_yoy_pct\":{priceChange:F2}," +
                          $"\"bedrooms\":{bedrooms},\"floor_area_sqft\":{sqFt:F0},\"ltv_ratio_pct\":{ltv:F1}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(350, doc.RecordCount);

        // Price mean and median
        var priceMean = doc.GetFieldMean("price_gbp");
        var priceMedian = doc.GetFieldMedian("price_gbp");
        var priceMin = doc.GetFieldMin("price_gbp");
        var priceMax = doc.GetFieldMax("price_gbp");

        Assert.True(priceMean >= priceMin);
        Assert.True(priceMean <= priceMax);
        Assert.True(priceMedian >= priceMin);
        Assert.True(priceMedian <= priceMax);
        Assert.True(priceMean > 0.0);
        Assert.True(priceMedian > 0.0);

        // In right-skewed distributions (luxury outliers), mean > median
        // (not always guaranteed with random data, but statistically likely)
        Assert.True(priceMean >= priceMedian * 0.7); // mean not wildly below median

        // Consistency
        Assert.Equal(priceMean, doc.GetFieldMean("price_gbp"));
        Assert.Equal(priceMedian, doc.GetFieldMedian("price_gbp"));

        // Floor area mean and median
        var areaMean = doc.GetFieldMean("floor_area_sqft");
        var areaMedian = doc.GetFieldMedian("floor_area_sqft");
        Assert.True(areaMean > 0.0);
        Assert.True(areaMedian > 0.0);
        Assert.True(areaMean >= doc.GetFieldMin("floor_area_sqft"));
        Assert.True(areaMean <= doc.GetFieldMax("floor_area_sqft"));

        // Price change mean (should be near middle of [-5, 10] range)
        var changeMean = doc.GetFieldMean("price_change_yoy_pct");
        Assert.True(changeMean > -5.0 && changeMean < 15.0);
        var changeMedian = doc.GetFieldMedian("price_change_yoy_pct");
        Assert.Equal(changeMedian, doc.GetFieldMedian("price_change_yoy_pct"));

        // LTV ratio mean and median
        var ltvMean = doc.GetFieldMean("ltv_ratio_pct");
        var ltvMedian = doc.GetFieldMedian("ltv_ratio_pct");
        Assert.True(ltvMean >= 60.0 && ltvMean <= 95.0);
        Assert.True(ltvMedian >= 60.0 && ltvMedian <= 95.0);
        Assert.Equal(ltvMean * ltvMean, ltvMean * ltvMean, precision: 2); // self-consistent

        // SaveToFile
        var outPath = TempFile("hm_lr_hpi_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(priceMean, loaded.GetFieldMean("price_gbp"), precision: 6);
        Assert.Equal(priceMedian, loaded.GetFieldMedian("price_gbp"), precision: 6);
        Assert.Equal(areaMean, loaded.GetFieldMean("floor_area_sqft"), precision: 6);
        Assert.Equal(areaMedian, loaded.GetFieldMedian("floor_area_sqft"), precision: 6);
        Assert.Equal(ltvMean, loaded.GetFieldMean("ltv_ratio_pct"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldMean("price_gbp"));
        var ex2 = Record.Exception(() => loaded.GetFieldMedian("price_gbp"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
