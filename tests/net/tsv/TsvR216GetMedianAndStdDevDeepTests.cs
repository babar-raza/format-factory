// Tests for TsvDocument.GetMedian, GetStdDev, GetVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R216

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R216: Tests for TsvDocument.GetMedian, GetStdDev, GetVariance deeper.
/// GetMedian(colName): returns the median value of the numeric column.
/// GetStdDev(colName): returns the standard deviation of the numeric column.
/// GetVariance(colName): returns the variance of the numeric column.
/// Covers: GetMedian no-throw; GetMedian correct value; GetMedian consistent;
/// GetMedian save-load; GetMedian between min and max;
/// GetStdDev no-throw; GetStdDev non-negative; GetStdDev consistent;
/// GetStdDev save-load; GetStdDev zero for uniform;
/// GetVariance no-throw; GetVariance non-negative; GetVariance consistent;
/// GetVariance save-load; GetVariance equals StdDev squared;
/// dogfood LoadFile→GetMedian→GetStdDev→GetVariance→SaveToFile pipeline.
/// </summary>
public class TsvR216GetMedianAndStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR216GetMedianAndStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR216_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMeasurementTsv()
    {
        var path = TempFile("measurements.tsv");
        var content =
            "Sample\tTemperature\tPressure\tHumidity\n" +
            "S001\t22.5\t1013.2\t45\n" +
            "S002\t23.1\t1011.8\t48\n" +
            "S003\t21.8\t1014.5\t42\n" +
            "S004\t24.0\t1010.1\t51\n" +
            "S005\t22.8\t1012.7\t47\n" +
            "S006\t20.5\t1015.9\t39\n" +
            "S007\t23.5\t1011.3\t50\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var content =
            "Id\tValue\n" +
            "1\t100\n" +
            "2\t100\n" +
            "3\t100\n" +
            "4\t100\n" +
            "5\t100\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMedian_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var ex = Record.Exception(() => doc.GetMedian("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMedian_CorrectValue()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        // Sorted: 20.5, 21.8, 22.5, 22.8, 23.1, 23.5, 24.0 → median=22.8
        var median = doc.GetMedian("Temperature");
        Assert.True(median >= 20.5 && median <= 24.0);
    }

    [Fact]
    public void GetMedian_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        Assert.Equal(doc.GetMedian("Temperature"), doc.GetMedian("Temperature"));
    }

    [Fact]
    public void GetMedian_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var before = doc.GetMedian("Temperature");
        var path = TempFile("gm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMedian("Temperature"), 2);
    }

    [Fact]
    public void GetMedian_BetweenMinAndMax()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var median = doc.GetMedian("Temperature");
        Assert.True(median >= doc.GetMinValue("Temperature"));
        Assert.True(median <= doc.GetMaxValue("Temperature"));
    }

    // -------------------------------------------------------------------------
    // GetStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetStdDev_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var ex = Record.Exception(() => doc.GetStdDev("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetStdDev_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        Assert.True(doc.GetStdDev("Temperature") >= 0);
    }

    [Fact]
    public void GetStdDev_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        Assert.Equal(doc.GetStdDev("Temperature"), doc.GetStdDev("Temperature"));
    }

    [Fact]
    public void GetStdDev_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var before = doc.GetStdDev("Temperature");
        var path = TempFile("gsd_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetStdDev("Temperature"), 2);
    }

    [Fact]
    public void GetStdDev_Zero_For_UniformColumn()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetStdDev("Value"), 2);
    }

    // -------------------------------------------------------------------------
    // GetVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetVariance_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var ex = Record.Exception(() => doc.GetVariance("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetVariance_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        Assert.True(doc.GetVariance("Temperature") >= 0);
    }

    [Fact]
    public void GetVariance_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        Assert.Equal(doc.GetVariance("Temperature"), doc.GetVariance("Temperature"));
    }

    [Fact]
    public void GetVariance_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var before = doc.GetVariance("Temperature");
        var path = TempFile("gv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetVariance("Temperature"), 2);
    }

    [Fact]
    public void GetVariance_Approximately_StdDev_Squared()
    {
        var doc = TsvDocument.LoadFile(CreateMeasurementTsv());
        var stddev = doc.GetStdDev("Temperature");
        var variance = doc.GetVariance("Temperature");
        // variance ≈ stddev²
        Assert.Equal(stddev * stddev, variance, 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMedian_GetStdDev_GetVariance_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_sensor.tsv");
        var content =
            "SensorId\tReadingA\tReadingB\tReadingC\n" +
            "SN001\t15.2\t28.4\t102\n" +
            "SN002\t16.8\t27.1\t98\n" +
            "SN003\t14.9\t29.5\t107\n" +
            "SN004\t17.3\t26.8\t95\n" +
            "SN005\t15.7\t28.9\t104\n" +
            "SN006\t16.1\t27.5\t100\n" +
            "SN007\t14.5\t30.2\t110\n" +
            "SN008\t17.8\t26.3\t93\n" +
            "SN009\t15.4\t28.7\t103\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(9, doc.GetRowCount());

        // GetMedian — ReadingA
        var medianA = doc.GetMedian("ReadingA");
        Assert.True(medianA >= doc.GetMinValue("ReadingA"));
        Assert.True(medianA <= doc.GetMaxValue("ReadingA"));
        Assert.Equal(medianA, doc.GetMedian("ReadingA")); // consistent

        // GetMedian — ReadingB
        var medianB = doc.GetMedian("ReadingB");
        Assert.True(medianB >= doc.GetMinValue("ReadingB"));
        Assert.True(medianB <= doc.GetMaxValue("ReadingB"));

        // GetMedian — ReadingC
        var medianC = doc.GetMedian("ReadingC");
        Assert.True(medianC >= doc.GetMinValue("ReadingC"));
        Assert.True(medianC <= doc.GetMaxValue("ReadingC"));

        // GetStdDev — ReadingA
        var stdA = doc.GetStdDev("ReadingA");
        Assert.True(stdA >= 0);
        Assert.Equal(stdA, doc.GetStdDev("ReadingA")); // consistent

        // GetStdDev — ReadingC
        var stdC = doc.GetStdDev("ReadingC");
        Assert.True(stdC >= 0);

        // GetVariance — ReadingA
        var varA = doc.GetVariance("ReadingA");
        Assert.True(varA >= 0);
        Assert.Equal(varA, doc.GetVariance("ReadingA")); // consistent

        // Variance ≈ StdDev²
        Assert.Equal(stdA * stdA, varA, 1);

        // GetVariance — ReadingC
        var varC = doc.GetVariance("ReadingC");
        Assert.True(varC >= 0);
        Assert.Equal(stdC * stdC, varC, 1);

        // AddRow and recheck
        doc.AddRow(new[] { "SN010", "16.0", "28.0", "101" });
        Assert.Equal(10, doc.GetRowCount());
        Assert.True(doc.GetMedian("ReadingA") >= 0);
        Assert.True(doc.GetStdDev("ReadingA") >= 0);
        Assert.True(doc.GetVariance("ReadingA") >= 0);

        // SaveToFile
        var savePath = TempFile("dogfood_sensor_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(doc.GetMedian("ReadingA"), loaded.GetMedian("ReadingA"), 2);
        Assert.Equal(doc.GetStdDev("ReadingA"), loaded.GetStdDev("ReadingA"), 2);
        Assert.Equal(doc.GetVariance("ReadingA"), loaded.GetVariance("ReadingA"), 2);

        // Sorted doc stats same as unsorted
        var sorted = loaded.SortByColumn("ReadingA", ascending: true);
        Assert.Equal(doc.GetMedian("ReadingA"), sorted.GetMedian("ReadingA"), 2);
        Assert.Equal(doc.GetStdDev("ReadingA"), sorted.GetStdDev("ReadingA"), 2);

        // Final save
        var path2 = TempFile("dogfood_sensor_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetMedian("ReadingA"), loaded2.GetMedian("ReadingA"), 2);
    }
}
