// Tests for NdjsonDocument.GetFieldMin, GetFieldMax deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R276

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R276: Tests for NdjsonDocument.GetFieldMin, GetFieldMax deeper.
/// GetFieldMin(field): returns the minimum numeric value across all records for the given field.
/// GetFieldMax(field): returns the maximum numeric value across all records for the given field.
/// Covers: GetFieldMin no-throw; GetFieldMin le GetFieldMean; GetFieldMin consistent;
/// GetFieldMin save-load; GetFieldMax no-throw; GetFieldMax ge GetFieldMean;
/// GetFieldMax ge GetFieldMin; GetFieldMax consistent; GetFieldMax save-load;
/// GetFieldMin/GetFieldMax equal for uniform; dogfood pipeline.
/// </summary>
public class NdjsonR276GetFieldMinAndFieldMaxDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR276GetFieldMinAndFieldMaxDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR276_" + Guid.NewGuid().ToString("N"));
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
        lines.AppendLine("{\"id\":1,\"score\":10.0,\"age\":22}");
        lines.AppendLine("{\"id\":2,\"score\":55.5,\"age\":34}");
        lines.AppendLine("{\"id\":3,\"score\":80.0,\"age\":45}");
        lines.AppendLine("{\"id\":4,\"score\":33.3,\"age\":28}");
        lines.AppendLine("{\"id\":5,\"score\":99.9,\"age\":61}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine("{\"id\":" + i + ",\"value\":42.0}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMin_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMin("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMin_Le_GetFieldMean()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMin("score") <= doc.GetFieldMean("score"));
    }

    [Fact]
    public void GetFieldMin_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMin("score"), doc.GetFieldMin("score"));
    }

    [Fact]
    public void GetFieldMin_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMin("score");
        var path = TempFile("min_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMin("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMin_Equal_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(42.0, doc.GetFieldMin("value"), precision: 3);
    }

    // -------------------------------------------------------------------------
    // GetFieldMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMax_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMax("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMax_Ge_GetFieldMean()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMax("score") >= doc.GetFieldMean("score"));
    }

    [Fact]
    public void GetFieldMax_Ge_GetFieldMin()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMax("score") >= doc.GetFieldMin("score"));
    }

    [Fact]
    public void GetFieldMax_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMax("score"), doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMax_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMax("score");
        var path = TempFile("max_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMax("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMax_Equal_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(42.0, doc.GetFieldMax("value"), precision: 3);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMin_GetFieldMax_Pipeline()
    {
        // Energy — National Grid ESO: Balancing Mechanism Report 2024-25
        // System balancing event stream — bid/offer prices and accepted MWh volumes
        // Min/Max field analysis for market surveillance and price cap monitoring

        var path = TempFile("ngeso_balancing_mechanism.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240801);

        string[] acceptTypes = { "BID", "BID", "OFFER", "OFFER", "OFFER" };
        string[] fuels = { "CCGT", "CCGT", "WIND", "NUCLEAR", "HYDRO", "BIOMASS", "COAL", "INTERCONNECTOR" };
        string[] participants = { "DRAX", "SSE_THERMAL", "ORSTED_UK", "EDF_NUCLEAR",
                                   "STATKRAFT_UK", "LYNEMOUTH", "RWE_RETAIL", "NEMO_LINK" };

        for (int i = 0; i < 300; i++)
        {
            string acceptType = acceptTypes[rng.Next(acceptTypes.Length)];
            string fuel = fuels[rng.Next(fuels.Length)];
            string participant = participants[rng.Next(participants.Length)];
            double price = acceptType == "BID"
                ? -(rng.NextDouble() * 40 + 5)  // negative prices for bids (-5 to -45)
                : rng.NextDouble() * 120 + 10;   // positive prices for offers (10 to 130)
            double volumeMwh = rng.NextDouble() * 200 + 10; // 10-210 MWh
            double settlementPeriod = rng.Next(1, 49);
            sb.AppendLine($"{{\"record_id\":\"BM{i:D6}\",\"accept_type\":\"{acceptType}\"," +
                          $"\"fuel_type\":\"{fuel}\",\"participant\":\"{participant}\"," +
                          $"\"price_per_mwh\":{price:F2}," +
                          $"\"volume_mwh\":{volumeMwh:F1}," +
                          $"\"settlement_period\":{settlementPeriod}," +
                          $"\"dispatch_date\":\"2024-{(i / 50 + 4):D2}-{(i % 28 + 1):D2}\"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(300, doc.RecordCount);

        // Price field min/max
        var priceMin = doc.GetFieldMin("price_per_mwh");
        var priceMax = doc.GetFieldMax("price_per_mwh");
        var priceMean = doc.GetFieldMean("price_per_mwh");
        Assert.True(priceMin <= priceMean);
        Assert.True(priceMax >= priceMean);
        Assert.True(priceMax >= priceMin);
        Assert.True(priceMin < 0); // bids have negative prices
        Assert.True(priceMax > 0); // offers have positive prices
        Assert.Equal(priceMin, doc.GetFieldMin("price_per_mwh")); // consistent
        Assert.Equal(priceMax, doc.GetFieldMax("price_per_mwh")); // consistent

        // Volume field min/max
        var volMin = doc.GetFieldMin("volume_mwh");
        var volMax = doc.GetFieldMax("volume_mwh");
        var volMean = doc.GetFieldMean("volume_mwh");
        Assert.True(volMin >= 0); // volume always non-negative
        Assert.True(volMax >= volMean);
        Assert.True(volMin <= volMean);
        Assert.True(volMax >= volMin);
        Assert.Equal(volMin, doc.GetFieldMin("volume_mwh")); // consistent

        // Settlement period: integer 1-48
        var spMin = doc.GetFieldMin("settlement_period");
        var spMax = doc.GetFieldMax("settlement_period");
        Assert.True(spMin >= 1);
        Assert.True(spMax <= 48);
        Assert.True(spMax >= spMin);

        // SaveToFile
        var outPath = TempFile("ngeso_bm_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(priceMin, loaded.GetFieldMin("price_per_mwh"), precision: 6);
        Assert.Equal(priceMax, loaded.GetFieldMax("price_per_mwh"), precision: 6);
        Assert.Equal(volMin, loaded.GetFieldMin("volume_mwh"), precision: 6);
        Assert.Equal(volMax, loaded.GetFieldMax("volume_mwh"), precision: 6);
        Assert.Equal(spMin, loaded.GetFieldMin("settlement_period"), precision: 6);
        Assert.Equal(spMax, loaded.GetFieldMax("settlement_period"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldMin("price_per_mwh"));
        var ex2 = Record.Exception(() => loaded.GetFieldMax("volume_mwh"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
