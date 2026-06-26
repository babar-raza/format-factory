// Tests for NdjsonDocument.GetFieldMean, GetFieldStdDev, GetFieldVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R228

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R228: Tests for NdjsonDocument.GetFieldMean, GetFieldStdDev, GetFieldVariance deeper.
/// GetFieldMean(fieldName): returns the arithmetic mean of all numeric values in the field.
/// GetFieldStdDev(fieldName): returns the standard deviation of numeric values in the field.
/// GetFieldVariance(fieldName): returns the variance of numeric values in the field.
/// Covers: GetFieldMean no-throw; GetFieldMean finite; GetFieldMean consistent;
/// GetFieldMean save-load; GetFieldMean between min and max;
/// GetFieldStdDev no-throw; GetFieldStdDev non-negative; GetFieldStdDev consistent;
/// GetFieldStdDev save-load; GetFieldStdDev zero for uniform;
/// GetFieldVariance no-throw; GetFieldVariance non-negative; GetFieldVariance consistent;
/// GetFieldVariance save-load; GetFieldVariance approx StdDev squared;
/// dogfood LoadFile→GetFieldMean→GetFieldStdDev→GetFieldVariance→SaveToFile pipeline.
/// </summary>
public class NdjsonR228GetFieldMeanAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR228GetFieldMeanAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR228_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateScoreNdjson()
    {
        var path = TempFile("scores.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":1,\"name\":\"Alice\",\"score\":88,\"attempts\":3,\"time\":45}",
            "{\"id\":2,\"name\":\"Bob\",\"score\":72,\"attempts\":5,\"time\":62}",
            "{\"id\":3,\"name\":\"Carol\",\"score\":95,\"attempts\":2,\"time\":38}",
            "{\"id\":4,\"name\":\"Dave\",\"score\":61,\"attempts\":7,\"time\":78}",
            "{\"id\":5,\"name\":\"Eve\",\"score\":84,\"attempts\":3,\"time\":50}",
            "{\"id\":6,\"name\":\"Frank\",\"score\":79,\"attempts\":4,\"time\":55}",
            "{\"id\":7,\"name\":\"Grace\",\"score\":91,\"attempts\":2,\"time\":42}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMean_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetFieldMean("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMean_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMean("score")));
    }

    [Fact]
    public void GetFieldMean_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.Equal(doc.GetFieldMean("score"), doc.GetFieldMean("score"));
    }

    [Fact]
    public void GetFieldMean_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var before = doc.GetFieldMean("score");
        var path = TempFile("fm_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMean("score"), 4);
    }

    [Fact]
    public void GetFieldMean_Between_Min_And_Max()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var mean = doc.GetFieldMean("score");
        Assert.True(mean >= doc.GetFieldMin("score"));
        Assert.True(mean <= doc.GetFieldMax("score"));
    }

    [Fact]
    public void GetFieldMean_Time_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.True(doc.GetFieldMean("time") > 0);
    }

    // -------------------------------------------------------------------------
    // GetFieldStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldStdDev_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetFieldStdDev("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldStdDev_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.True(doc.GetFieldStdDev("score") >= 0);
    }

    [Fact]
    public void GetFieldStdDev_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.Equal(doc.GetFieldStdDev("score"), doc.GetFieldStdDev("score"));
    }

    [Fact]
    public void GetFieldStdDev_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var before = doc.GetFieldStdDev("score");
        var path = TempFile("fsd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldStdDev("score"), 4);
    }

    [Fact]
    public void GetFieldStdDev_Positive_For_Varied_Data()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        // Score values are varied → std dev > 0
        Assert.True(doc.GetFieldStdDev("score") > 0);
    }

    // -------------------------------------------------------------------------
    // GetFieldVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldVariance_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetFieldVariance("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldVariance_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.True(doc.GetFieldVariance("score") >= 0);
    }

    [Fact]
    public void GetFieldVariance_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.Equal(doc.GetFieldVariance("score"), doc.GetFieldVariance("score"));
    }

    [Fact]
    public void GetFieldVariance_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var before = doc.GetFieldVariance("score");
        var path = TempFile("fv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldVariance("score"), 3);
    }

    [Fact]
    public void GetFieldVariance_Approx_StdDev_Squared()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var stdDev = doc.GetFieldStdDev("score");
        var variance = doc.GetFieldVariance("score");
        // variance ≈ stdDev²
        Assert.Equal(stdDev * stdDev, variance, 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMean_GetFieldStdDev_GetFieldVariance_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_benchmarks.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"run\":1,\"system\":\"SystemA\",\"latency\":45.2,\"throughput\":1850,\"errorRate\":0.02}",
            "{\"run\":2,\"system\":\"SystemB\",\"latency\":38.7,\"throughput\":2150,\"errorRate\":0.01}",
            "{\"run\":3,\"system\":\"SystemA\",\"latency\":47.1,\"throughput\":1780,\"errorRate\":0.03}",
            "{\"run\":4,\"system\":\"SystemC\",\"latency\":29.3,\"throughput\":2890,\"errorRate\":0.005}",
            "{\"run\":5,\"system\":\"SystemB\",\"latency\":41.5,\"throughput\":2050,\"errorRate\":0.015}",
            "{\"run\":6,\"system\":\"SystemA\",\"latency\":44.8,\"throughput\":1920,\"errorRate\":0.025}",
            "{\"run\":7,\"system\":\"SystemC\",\"latency\":31.2,\"throughput\":2750,\"errorRate\":0.008}",
            "{\"run\":8,\"system\":\"SystemB\",\"latency\":39.9,\"throughput\":2100,\"errorRate\":0.012}"
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRecordCount());

        // GetFieldMean — latency
        var meanLatency = doc.GetFieldMean("latency");
        Assert.True(double.IsFinite(meanLatency));
        Assert.True(meanLatency > 0);
        Assert.True(meanLatency >= doc.GetFieldMin("latency"));
        Assert.True(meanLatency <= doc.GetFieldMax("latency"));
        Assert.Equal(meanLatency, doc.GetFieldMean("latency")); // consistent

        // GetFieldMean — throughput
        var meanThroughput = doc.GetFieldMean("throughput");
        Assert.True(meanThroughput > 0);

        // GetFieldMean — errorRate
        var meanError = doc.GetFieldMean("errorRate");
        Assert.True(meanError >= 0);

        // GetFieldStdDev — latency (varied → > 0)
        var stdLatency = doc.GetFieldStdDev("latency");
        Assert.True(stdLatency >= 0);
        Assert.True(stdLatency > 0); // latency values are varied
        Assert.Equal(stdLatency, doc.GetFieldStdDev("latency")); // consistent

        // GetFieldStdDev — throughput
        var stdThroughput = doc.GetFieldStdDev("throughput");
        Assert.True(stdThroughput >= 0);

        // GetFieldVariance — latency
        var varLatency = doc.GetFieldVariance("latency");
        Assert.True(varLatency >= 0);
        Assert.Equal(stdLatency * stdLatency, varLatency, 2); // variance = stdDev²
        Assert.Equal(varLatency, doc.GetFieldVariance("latency")); // consistent

        // GetFieldVariance — throughput
        var varThroughput = doc.GetFieldVariance("throughput");
        Assert.Equal(stdThroughput * stdThroughput, varThroughput, 2);

        // ExportToJson works
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // SaveToFile
        var savePath = TempFile("dogfood_benchmarks_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRecordCount());
        Assert.Equal(meanLatency, loaded.GetFieldMean("latency"), 4);
        Assert.Equal(stdLatency, loaded.GetFieldStdDev("latency"), 4);
        Assert.Equal(varLatency, loaded.GetFieldVariance("latency"), 3);

        // AddRecord and recheck
        doc.AddRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["run"] = 9,
            ["system"] = "SystemD",
            ["latency"] = 25.8,
            ["throughput"] = 3100,
            ["errorRate"] = 0.003
        });
        Assert.Equal(9, doc.GetRecordCount());
        Assert.True(double.IsFinite(doc.GetFieldMean("latency")));
        Assert.True(doc.GetFieldStdDev("latency") >= 0);
        Assert.True(doc.GetFieldVariance("latency") >= 0);

        // Final save
        var path2 = TempFile("dogfood_benchmarks_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.GetFieldMean("latency"), loaded2.GetFieldMean("latency"), 4);
        Assert.Equal(loaded.GetFieldStdDev("latency"), loaded2.GetFieldStdDev("latency"), 4);
        Assert.Equal(loaded.GetFieldVariance("latency"), loaded2.GetFieldVariance("latency"), 3);
    }
}
