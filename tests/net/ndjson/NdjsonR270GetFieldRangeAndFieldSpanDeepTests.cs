// Tests for NdjsonDocument.GetFieldRange, GetFieldSpan deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R270

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R270: Tests for NdjsonDocument.GetFieldRange, GetFieldSpan deeper.
/// GetFieldRange(fieldName): returns the tuple (min, max) of numeric field values.
/// GetFieldSpan(fieldName): returns max - min (the range width) of numeric field values.
/// Covers: GetFieldRange no-throw; GetFieldRange min le max; GetFieldRange consistent;
/// GetFieldRange zero range for constant; GetFieldRange save-load;
/// GetFieldSpan no-throw; GetFieldSpan non-negative;
/// GetFieldSpan zero for constant; GetFieldSpan consistent;
/// GetFieldSpan equals max minus min; GetFieldSpan save-load;
/// dogfood CreateDoc→GetFieldRange→GetFieldSpan pipeline.
/// </summary>
public class NdjsonR270GetFieldRangeAndFieldSpanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR270GetFieldRangeAndFieldSpanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR270_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            int age = 18 + rng.Next(62);
            double salary = Math.Round(20000 + rng.NextDouble() * 80000, 2);
            int score = rng.Next(100);
            sb.AppendLine($"{{\"id\":{i},\"age\":{age},\"salary\":{salary},\"score\":{score}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":42}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldRange("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldRange_Min_Le_Max()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r = doc.GetFieldRange("salary");
        Assert.True(r.Min <= r.Max);
    }

    [Fact]
    public void GetFieldRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r1 = doc.GetFieldRange("age");
        var r2 = doc.GetFieldRange("age");
        Assert.Equal(r1.Min, r2.Min);
        Assert.Equal(r1.Max, r2.Max);
    }

    [Fact]
    public void GetFieldRange_ZeroRange_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        var r = doc.GetFieldRange("value");
        Assert.Equal(r.Min, r.Max);
    }

    [Fact]
    public void GetFieldRange_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldRange("salary");
        var path = TempFile("range_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetFieldRange("salary");
        Assert.Equal(before.Min, after.Min, precision: 6);
        Assert.Equal(before.Max, after.Max, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldSpan
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSpan_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldSpan("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSpan_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldSpan("salary") >= 0.0);
    }

    [Fact]
    public void GetFieldSpan_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldSpan("value"), precision: 6);
    }

    [Fact]
    public void GetFieldSpan_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldSpan("score"), doc.GetFieldSpan("score"));
    }

    [Fact]
    public void GetFieldSpan_Equals_Max_Minus_Min()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var r = doc.GetFieldRange("salary");
        var span = doc.GetFieldSpan("salary");
        Assert.Equal(r.Max - r.Min, span, precision: 6);
    }

    [Fact]
    public void GetFieldSpan_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldSpan("age");
        var path = TempFile("span_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSpan("age"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldRange_GetFieldSpan_Pipeline()
    {
        // Infrastructure — National Grid ESO: Real-Time Electricity Demand and Supply
        // NDJSON stream of balancing mechanism settlement periods
        // Range/span analysis for demand forecasting and frequency response monitoring
        var path = TempFile("ng_eso_demand.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] settlementDates = {
            "2025-01-15", "2025-01-16", "2025-01-17", "2025-01-18", "2025-01-19"
        };
        string[] bmuTypes = { "CCGT", "Nuclear", "Wind", "Solar", "Hydro", "Interconnector", "Pumped Storage" };

        for (int i = 0; i < 200; i++)
        {
            string date = settlementDates[i % settlementDates.Length];
            int period = (i % 48) + 1; // 30-minute settlement periods
            string bmu = bmuTypes[rng.Next(bmuTypes.Length)];
            double demand = Math.Round(28000 + rng.NextDouble() * 8000, 1); // MW
            double generation = Math.Round(demand * (0.95 + rng.NextDouble() * 0.10), 1);
            double imbalance = Math.Round(generation - demand, 1);
            double frequency = Math.Round(49.8 + rng.NextDouble() * 0.4, 3); // Hz
            double systemPrice = Math.Round(40 + rng.NextDouble() * 120, 2); // £/MWh
            double carbonIntensity = Math.Round(80 + rng.NextDouble() * 200, 1); // gCO2/kWh
            sb.AppendLine($"{{\"settlement_id\":{i},\"date\":\"{date}\",\"period\":{period}," +
                          $"\"bmu_type\":\"{bmu}\",\"demand_mw\":{demand},\"generation_mw\":{generation}," +
                          $"\"imbalance_mw\":{imbalance},\"frequency_hz\":{frequency}," +
                          $"\"system_price\":{systemPrice},\"carbon_intensity\":{carbonIntensity}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldRange for demand_mw
        var rangeDemand = doc.GetFieldRange("demand_mw");
        Assert.True(rangeDemand.Min <= rangeDemand.Max);
        Assert.True(rangeDemand.Min >= 28000); // minimum set
        Assert.True(rangeDemand.Max <= 36001); // maximum possible
        var r2 = doc.GetFieldRange("demand_mw");
        Assert.Equal(rangeDemand.Min, r2.Min); // consistent
        Assert.Equal(rangeDemand.Max, r2.Max);

        // GetFieldSpan for demand_mw
        var spanDemand = doc.GetFieldSpan("demand_mw");
        Assert.True(spanDemand >= 0);
        Assert.Equal(rangeDemand.Max - rangeDemand.Min, spanDemand, precision: 4);
        Assert.Equal(spanDemand, doc.GetFieldSpan("demand_mw")); // consistent

        // Frequency range — narrow band around 50 Hz
        var rangeFreq = doc.GetFieldRange("frequency_hz");
        Assert.True(rangeFreq.Min >= 49.8);
        Assert.True(rangeFreq.Max <= 50.21);
        var spanFreq = doc.GetFieldSpan("frequency_hz");
        Assert.True(spanFreq >= 0);
        Assert.True(spanFreq <= 0.4); // max spread 0.4 Hz
        Assert.Equal(rangeFreq.Max - rangeFreq.Min, spanFreq, precision: 6);

        // System price range
        var rangePrice = doc.GetFieldRange("system_price");
        Assert.True(rangePrice.Min >= 40);
        Assert.True(rangePrice.Max <= 161);
        var spanPrice = doc.GetFieldSpan("system_price");
        Assert.Equal(rangePrice.Max - rangePrice.Min, spanPrice, precision: 4);

        // Carbon intensity range
        var rangeCarbon = doc.GetFieldRange("carbon_intensity");
        Assert.True(rangeCarbon.Min >= 80);
        Assert.True(rangeCarbon.Max <= 281);
        var spanCarbon = doc.GetFieldSpan("carbon_intensity");
        Assert.Equal(rangeCarbon.Max - rangeCarbon.Min, spanCarbon, precision: 4);

        // Imbalance: can be negative (generation below demand)
        var rangeImbalance = doc.GetFieldRange("imbalance_mw");
        Assert.True(rangeImbalance.Min <= rangeImbalance.Max);
        var spanImbalance = doc.GetFieldSpan("imbalance_mw");
        Assert.True(spanImbalance >= 0);
        Assert.Equal(rangeImbalance.Max - rangeImbalance.Min, spanImbalance, precision: 4);

        // Basic field stats
        Assert.True(doc.GetFieldMean("demand_mw") > 0);
        Assert.True(doc.GetFieldSum("generation_mw") > 0);

        // SaveToFile
        var outPath = TempFile("ng_eso_demand_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        var loadedRange = loaded.GetFieldRange("demand_mw");
        Assert.Equal(rangeDemand.Min, loadedRange.Min, precision: 6);
        Assert.Equal(rangeDemand.Max, loadedRange.Max, precision: 6);
        Assert.Equal(spanDemand, loaded.GetFieldSpan("demand_mw"), precision: 6);

        // Constant span sub-test
        var path2 = TempFile("constant_demand.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{{\"id\":{i},\"demand_mw\":32000.0}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        var rangeConst = doc2.GetFieldRange("demand_mw");
        Assert.Equal(rangeConst.Min, rangeConst.Max);
        Assert.Equal(0.0, doc2.GetFieldSpan("demand_mw"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldRange("frequency_hz"));
        var ex2 = Record.Exception(() => loaded.GetFieldSpan("carbon_intensity"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
