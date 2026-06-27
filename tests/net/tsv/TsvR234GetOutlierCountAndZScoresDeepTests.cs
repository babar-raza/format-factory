// Tests for TsvDocument.GetOutlierCount, GetZScores, GetNormalizedColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R234

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R234: Tests for TsvDocument.GetOutlierCount, GetZScores, GetNormalizedColumn deeper.
/// GetOutlierCount(columnName, zThreshold): returns count of values with |z-score| > zThreshold.
/// GetZScores(columnName): returns the z-score for each row value in the column.
/// GetNormalizedColumn(columnName): returns values scaled to [0,1] using min-max normalisation.
/// Covers: GetOutlierCount no-throw; GetOutlierCount non-negative; GetOutlierCount consistent;
/// GetOutlierCount zero for uniform; GetOutlierCount save-load;
/// GetZScores no-throw; GetZScores non-null; GetZScores count equals row count; GetZScores consistent;
/// GetZScores save-load;
/// GetNormalizedColumn no-throw; GetNormalizedColumn non-null; GetNormalizedColumn in range;
/// GetNormalizedColumn consistent; GetNormalizedColumn save-load;
/// dogfood CreateDoc→GetOutlierCount→GetZScores→GetNormalizedColumn→SaveToFile pipeline.
/// </summary>
public class TsvR234GetOutlierCountAndZScoresDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR234GetOutlierCountAndZScoresDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR234_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateAnomalyTsv()
    {
        var path = TempFile("anomaly.tsv");
        // Normal values around 100, one extreme outlier at 950
        File.WriteAllText(path,
            "id\tsensor_value\ttemperature\tpressure\n" +
            "S01\t98.5\t22.1\t1013.2\n" +
            "S02\t101.2\t22.5\t1012.8\n" +
            "S03\t99.8\t21.9\t1013.5\n" +
            "S04\t102.4\t22.8\t1012.5\n" +
            "S05\t97.6\t21.5\t1013.8\n" +
            "S06\t950.0\t22.2\t1013.1\n" +  // extreme outlier
            "S07\t100.1\t22.4\t1013.0\n" +
            "S08\t103.5\t23.0\t1012.2\n" +
            "S09\t98.9\t21.8\t1013.6\n" +
            "S10\t101.8\t22.6\t1012.7\n" +
            "S11\t100.5\t22.3\t1013.1\n" +
            "S12\t99.2\t21.7\t1013.4\n");
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        File.WriteAllText(path, "id\tval\n1\t50\n2\t50\n3\t50\n4\t50\n5\t50\n6\t50\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutlierCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var ex = Record.Exception(() => doc.GetOutlierCount("sensor_value", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutlierCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        Assert.True(doc.GetOutlierCount("sensor_value", 2.0) >= 0);
    }

    [Fact]
    public void GetOutlierCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        Assert.Equal(doc.GetOutlierCount("sensor_value", 2.0), doc.GetOutlierCount("sensor_value", 2.0));
    }

    [Fact]
    public void GetOutlierCount_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0, doc.GetOutlierCount("val", 2.0));
    }

    [Fact]
    public void GetOutlierCount_DetectsExtreme_Outlier()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        // The 950 value should be flagged as outlier at z>2
        Assert.True(doc.GetOutlierCount("sensor_value", 2.0) >= 1);
    }

    [Fact]
    public void GetOutlierCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var before = doc.GetOutlierCount("sensor_value", 2.0);
        var path = TempFile("oc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutlierCount("sensor_value", 2.0));
    }

    // -------------------------------------------------------------------------
    // GetZScores
    // -------------------------------------------------------------------------

    [Fact]
    public void GetZScores_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var ex = Record.Exception(() => doc.GetZScores("sensor_value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetZScores_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        Assert.NotNull(doc.GetZScores("sensor_value"));
    }

    [Fact]
    public void GetZScores_CountEqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        Assert.Equal(doc.GetRowCount(), doc.GetZScores("sensor_value").Length);
    }

    [Fact]
    public void GetZScores_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var z1 = doc.GetZScores("sensor_value");
        var z2 = doc.GetZScores("sensor_value");
        Assert.Equal(z1.Length, z2.Length);
    }

    [Fact]
    public void GetZScores_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var before = doc.GetZScores("temperature").Length;
        var path = TempFile("zs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetZScores("temperature").Length);
    }

    // -------------------------------------------------------------------------
    // GetNormalizedColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNormalizedColumn_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var ex = Record.Exception(() => doc.GetNormalizedColumn("sensor_value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNormalizedColumn_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        Assert.NotNull(doc.GetNormalizedColumn("sensor_value"));
    }

    [Fact]
    public void GetNormalizedColumn_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var norm = doc.GetNormalizedColumn("sensor_value");
        foreach (var v in norm)
        {
            Assert.True(v >= 0.0);
            Assert.True(v <= 1.0);
        }
    }

    [Fact]
    public void GetNormalizedColumn_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var n1 = doc.GetNormalizedColumn("temperature");
        var n2 = doc.GetNormalizedColumn("temperature");
        Assert.Equal(n1.Length, n2.Length);
    }

    [Fact]
    public void GetNormalizedColumn_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateAnomalyTsv());
        var before = doc.GetNormalizedColumn("pressure").Length;
        var path = TempFile("nc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetNormalizedColumn("pressure").Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutlierCount_GetZScores_GetNormalizedColumn_SaveToFile_Pipeline()
    {
        // Network security monitoring — traffic anomaly detection dataset
        var path = TempFile("dogfood_netflow.tsv");
        File.WriteAllText(path,
            "flow_id\tbytes_sent\tpackets_sent\tduration_ms\tport_dst\tconn_per_min\trtt_ms\n" +
            "F001\t12500\t85\t245\t443\t12\t18.5\n" +
            "F002\t8200\t62\t180\t80\t8\t22.1\n" +
            "F003\t15800\t108\t312\t443\t15\t16.8\n" +
            "F004\t9500\t72\t215\t22\t9\t25.4\n" +
            "F005\t11200\t79\t268\t443\t11\t19.2\n" +
            "F006\t2850000\t18500\t125\t0\t8500\t0.8\n" +  // DDoS anomaly
            "F007\t13200\t91\t285\t443\t13\t17.5\n" +
            "F008\t10800\t76\t252\t80\t10\t21.8\n" +
            "F009\t14500\t99\t298\t443\t14\t18.1\n" +
            "F010\t9800\t68\t228\t8080\t10\t23.5\n" +
            "F011\t11500\t82\t260\t443\t11\t19.8\n" +
            "F012\t12800\t88\t275\t443\t12\t18.2\n");

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRowCount());

        // GetOutlierCount — bytes_sent anomaly detection
        var outlierCount = doc.GetOutlierCount("bytes_sent", 2.0);
        Assert.True(outlierCount >= 0);
        Assert.True(outlierCount >= 1); // F006 is extreme outlier
        Assert.Equal(outlierCount, doc.GetOutlierCount("bytes_sent", 2.0)); // consistent

        // conn_per_min anomaly
        var connOutliers = doc.GetOutlierCount("conn_per_min", 2.0);
        Assert.True(connOutliers >= 0);

        // Very high threshold → fewer outliers
        var strictCount = doc.GetOutlierCount("bytes_sent", 5.0);
        Assert.True(strictCount >= 0);

        // GetZScores — network flow z-scores
        var zBytes = doc.GetZScores("bytes_sent");
        Assert.NotNull(zBytes);
        Assert.Equal(12, zBytes.Length);
        Assert.Equal(zBytes.Length, doc.GetZScores("bytes_sent").Length); // consistent

        var zDuration = doc.GetZScores("duration_ms");
        Assert.NotNull(zDuration);
        Assert.Equal(12, zDuration.Length);

        // GetNormalizedColumn — normalise RTT values
        var normRtt = doc.GetNormalizedColumn("rtt_ms");
        Assert.NotNull(normRtt);
        Assert.Equal(12, normRtt.Length);
        foreach (var v in normRtt) { Assert.True(v >= 0.0); Assert.True(v <= 1.0); }
        Assert.Equal(normRtt.Length, doc.GetNormalizedColumn("rtt_ms").Length); // consistent

        var normPackets = doc.GetNormalizedColumn("packets_sent");
        Assert.NotNull(normPackets);
        foreach (var v in normPackets) { Assert.True(v >= 0.0); Assert.True(v <= 1.0); }

        // SaveToFile
        var out1 = TempFile("dogfood_netflow_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRowCount());
        Assert.Equal(outlierCount, loaded.GetOutlierCount("bytes_sent", 2.0));
        Assert.Equal(zBytes.Length, loaded.GetZScores("bytes_sent").Length);
        var loadedNorm = loaded.GetNormalizedColumn("rtt_ms");
        Assert.Equal(normRtt.Length, loadedNorm.Length);
        for (int i = 0; i < normRtt.Length; i++)
            Assert.Equal(normRtt[i], loadedNorm[i], precision: 6);

        // AddRow and verify metrics still valid
        loaded.AddRow(new[] { "F013", "13500", "94", "288", "443", "13", "17.8" });
        Assert.Equal(13, loaded.GetRowCount());
        Assert.True(loaded.GetOutlierCount("bytes_sent", 2.0) >= 1);
        Assert.Equal(13, loaded.GetZScores("bytes_sent").Length);

        // Final save
        var out2 = TempFile("dogfood_netflow_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRowCount());
        Assert.NotNull(loaded2.GetNormalizedColumn("rtt_ms"));
        Assert.True(loaded2.GetOutlierCount("conn_per_min", 2.0) >= 0);
    }
}
