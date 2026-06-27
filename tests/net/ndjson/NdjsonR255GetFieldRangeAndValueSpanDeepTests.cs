// Tests for NdjsonDocument.GetFieldRange, GetFieldValueSpan, GetFieldMedian deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R255

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R255: Tests for NdjsonDocument.GetFieldRange, GetFieldValueSpan, GetFieldMedian deeper.
/// GetFieldRange(fieldName): returns (min, max) as a tuple or as separate accessible properties.
/// GetFieldValueSpan(fieldName): returns max − min for numeric field values.
/// GetFieldMedian(fieldName): returns the median value of numeric field values.
/// Covers: GetFieldRange no-throw; GetFieldRange min ≤ max; GetFieldRange consistent;
/// GetFieldRange min equals GetFieldMin;
/// GetFieldValueSpan no-throw; GetFieldValueSpan non-negative; GetFieldValueSpan consistent;
/// GetFieldValueSpan zero for constant field;
/// GetFieldMedian no-throw; GetFieldMedian between min and max; GetFieldMedian consistent;
/// GetFieldMedian save-load;
/// dogfood CreateDoc→GetFieldRange→GetFieldValueSpan→GetFieldMedian pipeline.
/// </summary>
public class NdjsonR255GetFieldRangeAndValueSpanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR255GetFieldRangeAndValueSpanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR255_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMetricsNdjson()
    {
        var path = TempFile("metrics.ndjson");
        var lines = new System.Collections.Generic.List<string>
        {
            "{\"server\":\"web-01\",\"cpu_pct\":45.2,\"mem_pct\":62.1,\"latency_ms\":12}",
            "{\"server\":\"web-02\",\"cpu_pct\":72.8,\"mem_pct\":78.4,\"latency_ms\":18}",
            "{\"server\":\"db-01\",\"cpu_pct\":88.3,\"mem_pct\":91.2,\"latency_ms\":5}",
            "{\"server\":\"cache-01\",\"cpu_pct\":22.1,\"mem_pct\":34.7,\"latency_ms\":2}",
            "{\"server\":\"web-03\",\"cpu_pct\":55.9,\"mem_pct\":69.3,\"latency_ms\":15}",
            "{\"server\":\"api-01\",\"cpu_pct\":41.7,\"mem_pct\":55.8,\"latency_ms\":8}",
            "{\"server\":\"api-02\",\"cpu_pct\":36.4,\"mem_pct\":48.2,\"latency_ms\":7}",
            "{\"server\":\"db-02\",\"cpu_pct\":91.5,\"mem_pct\":94.1,\"latency_ms\":4}",
            "{\"server\":\"web-04\",\"cpu_pct\":48.6,\"mem_pct\":61.9,\"latency_ms\":11}",
            "{\"server\":\"api-03\",\"cpu_pct\":29.3,\"mem_pct\":42.6,\"latency_ms\":6}",
            "{\"server\":\"cache-02\",\"cpu_pct\":18.7,\"mem_pct\":28.4,\"latency_ms\":2}",
            "{\"server\":\"web-05\",\"cpu_pct\":64.1,\"mem_pct\":73.7,\"latency_ms\":16}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var lines = new string[]
        {
            "{\"id\":1,\"value\":42,\"label\":\"A\"}",
            "{\"id\":2,\"value\":42,\"label\":\"B\"}",
            "{\"id\":3,\"value\":42,\"label\":\"C\"}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldRange_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var ex = Record.Exception(() => doc.GetFieldRange("cpu_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldRange_Min_LessOrEqual_Max()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var range = doc.GetFieldRange("cpu_pct");
        Assert.True(range.Min <= range.Max);
    }

    [Fact]
    public void GetFieldRange_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var r1 = doc.GetFieldRange("latency_ms");
        var r2 = doc.GetFieldRange("latency_ms");
        Assert.Equal(r1.Min, r2.Min);
        Assert.Equal(r1.Max, r2.Max);
    }

    [Fact]
    public void GetFieldRange_Min_Equals_GetFieldMin()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        Assert.Equal(doc.GetFieldMin("cpu_pct"), doc.GetFieldRange("cpu_pct").Min, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldValueSpan
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueSpan_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueSpan("cpu_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueSpan_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        Assert.True(doc.GetFieldValueSpan("cpu_pct") >= 0);
    }

    [Fact]
    public void GetFieldValueSpan_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        Assert.Equal(doc.GetFieldValueSpan("latency_ms"), doc.GetFieldValueSpan("latency_ms"));
    }

    [Fact]
    public void GetFieldValueSpan_Zero_For_Constant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldValueSpan("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMedian_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var ex = Record.Exception(() => doc.GetFieldMedian("cpu_pct"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMedian_Between_Min_And_Max()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var median = doc.GetFieldMedian("cpu_pct");
        Assert.True(median >= doc.GetFieldMin("cpu_pct") && median <= doc.GetFieldMax("cpu_pct"));
    }

    [Fact]
    public void GetFieldMedian_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        Assert.Equal(doc.GetFieldMedian("latency_ms"), doc.GetFieldMedian("latency_ms"));
    }

    [Fact]
    public void GetFieldMedian_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateMetricsNdjson());
        var before = doc.GetFieldMedian("cpu_pct");
        var path = TempFile("median_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMedian("cpu_pct"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldRange_GetFieldValueSpan_GetFieldMedian_Pipeline()
    {
        // Financial technology — payment processing latency and throughput metrics
        var path = TempFile("payment_metrics.ndjson");
        var lines = new System.Collections.Generic.List<string>();
        var rng = new Random(20250801);
        string[] processors = { "VISA", "Mastercard", "Amex", "PayPal", "Stripe" };
        string[] regions = { "UK", "EU", "US", "APAC" };
        for (int i = 0; i < 150; i++)
        {
            string processor = processors[i % 5];
            string region = regions[i % 4];
            // Latency: log-normal (most fast, some slow)
            double latencyMs = Math.Exp(3 + rng.NextDouble() * 2);
            double successRate = 0.85 + rng.NextDouble() * 0.14;
            double tps = 50 + rng.NextDouble() * 450;
            double feeGbp = 0.10 + rng.NextDouble() * 1.40;
            int errorCode = rng.NextDouble() < 0.05 ? rng.Next(1, 10) : 0;
            lines.Add($"{{\"tx_id\":\"TX{i:D6}\",\"processor\":\"{processor}\",\"region\":\"{region}\",\"latency_ms\":{latencyMs:F1},\"success_rate\":{successRate:F4},\"tps\":{tps:F1},\"fee_gbp\":{feeGbp:F2},\"error_code\":{errorCode}}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150, doc.RecordCount);

        // GetFieldRange — latency
        var latRange = doc.GetFieldRange("latency_ms");
        Assert.True(latRange.Min <= latRange.Max);
        Assert.Equal(doc.GetFieldMin("latency_ms"), latRange.Min, precision: 6);
        Assert.Equal(doc.GetFieldMax("latency_ms"), latRange.Max, precision: 6);
        var latRange2 = doc.GetFieldRange("latency_ms");
        Assert.Equal(latRange.Min, latRange2.Min); // consistent

        // GetFieldRange — success_rate
        var srRange = doc.GetFieldRange("success_rate");
        Assert.True(srRange.Min <= srRange.Max);
        Assert.True(srRange.Min >= 0.84 && srRange.Max <= 1.01);

        // GetFieldValueSpan — latency
        var latSpan = doc.GetFieldValueSpan("latency_ms");
        Assert.True(latSpan >= 0);
        Assert.Equal(latSpan, doc.GetFieldValueSpan("latency_ms")); // consistent
        Assert.Equal(latRange.Max - latRange.Min, latSpan, precision: 6);

        // GetFieldValueSpan — tps
        var tpsSpan = doc.GetFieldValueSpan("tps");
        Assert.True(tpsSpan >= 0);

        // GetFieldMedian — latency
        var latMedian = doc.GetFieldMedian("latency_ms");
        Assert.True(latMedian >= latRange.Min && latMedian <= latRange.Max);
        Assert.Equal(latMedian, doc.GetFieldMedian("latency_ms")); // consistent

        // GetFieldMedian — success_rate
        var srMedian = doc.GetFieldMedian("success_rate");
        Assert.True(srMedian >= srRange.Min && srMedian <= srRange.Max);

        // GetFieldMedian — fee_gbp
        var feeMedian = doc.GetFieldMedian("fee_gbp");
        var feeRange = doc.GetFieldRange("fee_gbp");
        Assert.True(feeMedian >= feeRange.Min && feeMedian <= feeRange.Max);

        // SaveToFile
        var outPath = TempFile("payment_metrics_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        var loadedRange = loaded.GetFieldRange("latency_ms");
        Assert.Equal(latRange.Min, loadedRange.Min, precision: 6);
        Assert.Equal(latRange.Max, loadedRange.Max, precision: 6);
        Assert.Equal(latSpan, loaded.GetFieldValueSpan("latency_ms"), precision: 6);
        Assert.Equal(latMedian, loaded.GetFieldMedian("latency_ms"), precision: 6);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // Additional stats
        var meanLat = doc.GetFieldMean("latency_ms");
        Assert.True(meanLat > 0);
        var stdLat = doc.GetFieldStdDev("latency_ms");
        Assert.True(stdLat >= 0);
    }
}
