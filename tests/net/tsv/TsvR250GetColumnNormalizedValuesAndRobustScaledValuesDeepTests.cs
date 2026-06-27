// Tests for TsvDocument.GetColumnNormalizedValues, GetColumnRobustScaledValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R250

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R250: Tests for TsvDocument.GetColumnNormalizedValues, GetColumnRobustScaledValues deeper.
/// GetColumnNormalizedValues(colName): returns (value - min) / (max - min) for each row (min-max scaling).
/// GetColumnRobustScaledValues(colName): returns (value - median) / IQR for each row (robust scaling).
/// Covers: GetColumnNormalizedValues no-throw; GetColumnNormalizedValues non-null;
/// GetColumnNormalizedValues count equals row count; GetColumnNormalizedValues all in [0,1];
/// GetColumnNormalizedValues save-load;
/// GetColumnRobustScaledValues no-throw; GetColumnRobustScaledValues non-null;
/// GetColumnRobustScaledValues count equals row count; GetColumnRobustScaledValues median near zero;
/// GetColumnRobustScaledValues save-load;
/// dogfood CreateDoc→GetColumnNormalizedValues→GetColumnRobustScaledValues pipeline.
/// </summary>
public class TsvR250GetColumnNormalizedValuesAndRobustScaledValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR250GetColumnNormalizedValuesAndRobustScaledValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR250_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("sensor_id\tvoltage\tcurrent\ttemperature\tpower");
        var rng = new Random(7777);
        for (int i = 0; i < 60; i++)
        {
            double v = 3.0 + rng.NextDouble() * 2.0;
            double a = 0.1 + rng.NextDouble() * 1.9;
            double t = 25 + rng.NextDouble() * 50;
            double p = v * a;
            sb.AppendLine($"SEN{i:D3}\t{v:F3}\t{a:F4}\t{t:F2}\t{p:F4}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnNormalizedValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnNormalizedValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnNormalizedValues("voltage"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnNormalizedValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnNormalizedValues("voltage"));
    }

    [Fact]
    public void GetColumnNormalizedValues_Count_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnNormalizedValues("voltage").Length);
    }

    [Fact]
    public void GetColumnNormalizedValues_All_In_01()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        foreach (var v in doc.GetColumnNormalizedValues("voltage"))
            Assert.True(v >= 0.0 && v <= 1.0);
    }

    [Fact]
    public void GetColumnNormalizedValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnNormalizedValues("temperature");
        var path = TempFile("nv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnNormalizedValues("temperature");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnRobustScaledValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRobustScaledValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnRobustScaledValues("current"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRobustScaledValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetColumnRobustScaledValues("current"));
    }

    [Fact]
    public void GetColumnRobustScaledValues_Count_Equals_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.RowCount, doc.GetColumnRobustScaledValues("current").Length);
    }

    [Fact]
    public void GetColumnRobustScaledValues_Median_Near_Zero()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var vals = doc.GetColumnRobustScaledValues("voltage");
        // Sorted — median element should be near 0
        var sorted = (double[])vals.Clone();
        Array.Sort(sorted);
        double median = sorted.Length % 2 == 0
            ? (sorted[sorted.Length / 2 - 1] + sorted[sorted.Length / 2]) / 2.0
            : sorted[sorted.Length / 2];
        Assert.Equal(0.0, median, precision: 3);
    }

    [Fact]
    public void GetColumnRobustScaledValues_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnRobustScaledValues("temperature");
        var path = TempFile("rsv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var after = loaded.GetColumnRobustScaledValues("temperature");
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i], precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnNormalizedValues_GetColumnRobustScaledValues_Pipeline()
    {
        // Structural engineering — bridge condition monitoring sensor data (SHM system)
        var path = TempFile("bridge_shm_sensors.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("sensor_id\tlocation\tstrain_microstrain\tacceleration_g\tdisplacement_mm\ttemperature_c\tcorrosion_index\tcable_tension_kn");
        var rng = new Random(20250501);
        string[] locations = { "Deck_North", "Deck_South", "Tower_Base_E", "Tower_Base_W", "Midspan", "Approach_E", "Approach_W" };
        for (int i = 0; i < 150; i++)
        {
            var loc = locations[i % locations.Length];
            double strain = 50 + rng.NextDouble() * 300;
            // Add 5 outliers with extreme strain
            if (rng.Next(30) == 0) strain = 800 + rng.NextDouble() * 400;
            double accel = 0.001 + rng.NextDouble() * 0.05;
            double disp = 1.0 + rng.NextDouble() * 15.0;
            double temp = -5 + rng.NextDouble() * 45;
            double corr = rng.NextDouble() * 0.3;
            double tension = 800 + rng.NextDouble() * 400;
            sb.AppendLine($"SHM{i:D4}\t{loc}\t{strain:F2}\t{accel:F5}\t{disp:F3}\t{temp:F1}\t{corr:F4}\t{tension:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnNormalizedValues
        var normStrain = doc.GetColumnNormalizedValues("strain_microstrain");
        Assert.NotNull(normStrain);
        Assert.Equal(150, normStrain.Length);
        foreach (var v in normStrain)
            Assert.True(v >= 0.0 && v <= 1.0);

        var normAccel = doc.GetColumnNormalizedValues("acceleration_g");
        Assert.Equal(150, normAccel.Length);
        foreach (var v in normAccel)
            Assert.True(v >= 0.0 && v <= 1.0);

        var normTemp = doc.GetColumnNormalizedValues("temperature_c");
        Assert.Equal(150, normTemp.Length);
        foreach (var v in normTemp)
            Assert.True(v >= 0.0 && v <= 1.0);

        // GetColumnRobustScaledValues
        var robStrain = doc.GetColumnRobustScaledValues("strain_microstrain");
        Assert.NotNull(robStrain);
        Assert.Equal(150, robStrain.Length);

        // Robust scaling should handle outliers better — median at 0
        var sortedRob = (double[])robStrain.Clone();
        Array.Sort(sortedRob);
        double medianRob = sortedRob.Length % 2 == 0
            ? (sortedRob[sortedRob.Length / 2 - 1] + sortedRob[sortedRob.Length / 2]) / 2.0
            : sortedRob[sortedRob.Length / 2];
        Assert.Equal(0.0, medianRob, precision: 2);

        var robDisp = doc.GetColumnRobustScaledValues("displacement_mm");
        Assert.Equal(150, robDisp.Length);

        var robCorr = doc.GetColumnRobustScaledValues("corrosion_index");
        Assert.Equal(150, robCorr.Length);

        // Consistent
        var norm2 = doc.GetColumnNormalizedValues("strain_microstrain");
        for (int i = 0; i < 5; i++)
            Assert.Equal(normStrain[i], norm2[i]);

        var rob2 = doc.GetColumnRobustScaledValues("strain_microstrain");
        for (int i = 0; i < 5; i++)
            Assert.Equal(robStrain[i], rob2[i]);

        // Basic stats
        Assert.True(doc.GetColumnMean("strain_microstrain") > 0.0);
        Assert.True(doc.GetColumnMin("temperature_c") < doc.GetColumnMax("temperature_c"));

        // SaveToFile
        var outPath = TempFile("bridge_shm_sensors_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        var loadedNorm = loaded.GetColumnNormalizedValues("strain_microstrain");
        Assert.Equal(normStrain.Length, loadedNorm.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(normStrain[i], loadedNorm[i], precision: 8);
        var loadedRob = loaded.GetColumnRobustScaledValues("strain_microstrain");
        Assert.Equal(robStrain.Length, loadedRob.Length);
        for (int i = 0; i < 5; i++)
            Assert.Equal(robStrain[i], loadedRob[i], precision: 8);
    }
}
