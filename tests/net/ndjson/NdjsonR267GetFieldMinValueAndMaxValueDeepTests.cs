// Tests for NdjsonDocument.GetFieldMinValue, GetFieldMaxValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R267

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R267: Tests for NdjsonDocument.GetFieldMinValue, GetFieldMaxValue deeper.
/// GetFieldMinValue(fieldName): returns the minimum numeric value of the specified field.
/// GetFieldMaxValue(fieldName): returns the maximum numeric value of the specified field.
/// Covers: GetFieldMinValue no-throw; GetFieldMinValue finite; GetFieldMinValue consistent;
/// GetFieldMinValue save-load; GetFieldMaxValue no-throw; GetFieldMaxValue finite;
/// GetFieldMaxValue consistent; GetFieldMaxValue save-load;
/// GetFieldMaxValue >= GetFieldMinValue; GetFieldMinValue known for injected data;
/// GetFieldMaxValue known for injected data;
/// dogfood CreateDoc→GetFieldMinValue→GetFieldMaxValue pipeline.
/// </summary>
public class NdjsonR267GetFieldMinValueAndMaxValueDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR267GetFieldMinValueAndMaxValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR267_" + Guid.NewGuid().ToString("N"));
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
            double temp = -5.0 + rng.NextDouble() * 35.0;
            int count = rng.Next(500);
            double ratio = rng.NextDouble();
            sb.AppendLine($"{{\"id\":{i},\"temperature\":{temp:F2},\"count\":{count},\"ratio\":{ratio:F4}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateKnownNdjson()
    {
        var path = TempFile("known.ndjson");
        var sb = new StringBuilder();
        sb.AppendLine("{\"id\":1,\"score\":42.5,\"rank\":3}");
        sb.AppendLine("{\"id\":2,\"score\":97.1,\"rank\":1}");
        sb.AppendLine("{\"id\":3,\"score\":15.0,\"rank\":5}");
        sb.AppendLine("{\"id\":4,\"score\":63.8,\"rank\":2}");
        sb.AppendLine("{\"id\":5,\"score\":29.9,\"rank\":4}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldMinValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMinValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMinValue("temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMinValue_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMinValue("temperature")));
    }

    [Fact]
    public void GetFieldMinValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMinValue("count"), doc.GetFieldMinValue("count"));
    }

    [Fact]
    public void GetFieldMinValue_Known_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownNdjson());
        Assert.Equal(15.0, doc.GetFieldMinValue("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMinValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMinValue("temperature");
        var path = TempFile("fmin_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMinValue("temperature"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldMaxValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMaxValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMaxValue("temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMaxValue_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMaxValue("temperature")));
    }

    [Fact]
    public void GetFieldMaxValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMaxValue("count"), doc.GetFieldMaxValue("count"));
    }

    [Fact]
    public void GetFieldMaxValue_Known_Value()
    {
        var doc = NdjsonDocument.LoadFile(CreateKnownNdjson());
        Assert.Equal(97.1, doc.GetFieldMaxValue("score"), precision: 6);
    }

    [Fact]
    public void GetFieldMaxValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldMaxValue("ratio");
        var path = TempFile("fmax_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMaxValue("ratio"), precision: 6);
    }

    [Fact]
    public void GetFieldMaxValue_GreaterOrEqual_GetFieldMinValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldMaxValue("temperature") >= doc.GetFieldMinValue("temperature"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldMinValue_GetFieldMaxValue_Pipeline()
    {
        // Environmental — UK Centre for Ecology & Hydrology (CEH) River Flow Network
        // Gauging station telemetry: daily mean flow and water level monitoring
        var path = TempFile("ceh_river_flow.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241101);

        string[] stations = { "45001", "27041", "33013", "54057", "76021", "39001", "52010" };
        string[] rivers = { "Thames at Kingston", "Trent at Colwick", "Great Ouse at Bedford",
                            "Severn at Bewdley", "Eden at Sheepmount",
                            "Lee at Feildes Weir", "Exe at Thorverton" };
        // Flow in m³/s — Thames range 30-600, Eden 5-400, Exe 2-150
        double[] minFlows = { 30, 20, 10, 40, 5, 3, 2 };
        double[] maxFlows = { 600, 350, 180, 450, 400, 200, 150 };

        double absoluteMin = double.MaxValue;
        double absoluteMax = double.MinValue;

        for (int i = 0; i < 200; i++)
        {
            int stationIdx = i % stations.Length;
            string stationId = stations[stationIdx];
            string river = rivers[stationIdx];
            string date = $"2024-{(i % 12) + 1:D2}-{(i % 28) + 1:D2}";
            double flow = minFlows[stationIdx] + rng.NextDouble() * (maxFlows[stationIdx] - minFlows[stationIdx]);
            double level = 0.5 + rng.NextDouble() * 3.5;
            double velocity = 0.1 + rng.NextDouble() * 2.5;
            double waterTemp = 4.0 + rng.NextDouble() * 16.0;
            bool flagged = flow > maxFlows[stationIdx] * 0.9;

            if (flow < absoluteMin) absoluteMin = flow;
            if (flow > absoluteMax) absoluteMax = flow;

            sb.AppendLine($"{{\"station_id\":\"{stationId}\",\"river\":\"{river}\",\"date\":\"{date}\",\"mean_flow_m3s\":{flow:F3},\"water_level_m\":{level:F3},\"velocity_ms\":{velocity:F3},\"water_temp_c\":{waterTemp:F1},\"flood_alert\":{flagged.ToString().ToLower()}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldMinValue — mean_flow_m3s
        var minFlow = doc.GetFieldMinValue("mean_flow_m3s");
        Assert.True(double.IsFinite(minFlow));
        Assert.True(minFlow > 0); // flow is always positive
        Assert.Equal(minFlow, doc.GetFieldMinValue("mean_flow_m3s")); // consistent

        // GetFieldMaxValue — mean_flow_m3s
        var maxFlow = doc.GetFieldMaxValue("mean_flow_m3s");
        Assert.True(double.IsFinite(maxFlow));
        Assert.True(maxFlow > minFlow);
        Assert.Equal(maxFlow, doc.GetFieldMaxValue("mean_flow_m3s")); // consistent

        // GetFieldMinValue — water_level_m
        var minLevel = doc.GetFieldMinValue("water_level_m");
        Assert.True(double.IsFinite(minLevel));
        Assert.True(minLevel >= 0.5); // minimum water level ≈ 0.5

        // GetFieldMaxValue — water_level_m
        var maxLevel = doc.GetFieldMaxValue("water_level_m");
        Assert.True(maxLevel >= minLevel);

        // GetFieldMinValue — water_temp_c
        var minTemp = doc.GetFieldMinValue("water_temp_c");
        Assert.True(double.IsFinite(minTemp));
        Assert.True(minTemp >= 4.0); // minimum simulated temp

        // GetFieldMaxValue — water_temp_c
        var maxTemp = doc.GetFieldMaxValue("water_temp_c");
        Assert.True(maxTemp >= minTemp);
        Assert.True(maxTemp <= 20.1); // maximum simulated temp

        // SaveToFile
        var outPath = TempFile("ceh_river_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(minFlow, loaded.GetFieldMinValue("mean_flow_m3s"), precision: 6);
        Assert.Equal(maxFlow, loaded.GetFieldMaxValue("mean_flow_m3s"), precision: 6);
        Assert.Equal(minLevel, loaded.GetFieldMinValue("water_level_m"), precision: 6);
        Assert.Equal(maxLevel, loaded.GetFieldMaxValue("water_level_m"), precision: 6);

        // Known values test
        var knownPath = TempFile("known_flow.ndjson");
        var sb2 = new StringBuilder();
        sb2.AppendLine("{\"station\":\"45001\",\"flow\":45.5}");
        sb2.AppendLine("{\"station\":\"27041\",\"flow\":120.0}");
        sb2.AppendLine("{\"station\":\"33013\",\"flow\":8.2}");
        sb2.AppendLine("{\"station\":\"54057\",\"flow\":300.7}");
        File.WriteAllText(knownPath, sb2.ToString());
        var known = NdjsonDocument.LoadFile(knownPath);
        Assert.Equal(8.2, known.GetFieldMinValue("flow"), precision: 6);
        Assert.Equal(300.7, known.GetFieldMaxValue("flow"), precision: 6);
        Assert.True(known.GetFieldMaxValue("flow") >= known.GetFieldMinValue("flow"));
    }
}
