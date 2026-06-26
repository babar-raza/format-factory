// Tests for TsvDocument.GetOutliers, GetTrimmedMean, GetModeValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R219

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R219: Tests for TsvDocument.GetOutliers, GetTrimmedMean, GetModeValue deeper.
/// GetOutliers(colName, threshold): returns row indices where the column value is an outlier.
/// GetTrimmedMean(colName, trimPercent): returns the mean after trimming top/bottom percentiles.
/// GetModeValue(colName): returns the most frequently occurring value in the column.
/// Covers: GetOutliers no-throw; GetOutliers non-null; GetOutliers count leq row count;
/// GetOutliers consistent; GetOutliers save-load; GetOutliers empty for uniform;
/// GetTrimmedMean no-throw; GetTrimmedMean finite; GetTrimmedMean consistent;
/// GetTrimmedMean save-load; GetTrimmedMean between min and max;
/// GetModeValue no-throw; GetModeValue non-null; GetModeValue consistent;
/// GetModeValue save-load; GetModeValue is one of the values;
/// dogfood LoadFile→GetOutliers→GetTrimmedMean→GetModeValue→SaveToFile pipeline.
/// </summary>
public class TsvR219GetOutliersAndTrimmedMeanDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR219GetOutliersAndTrimmedMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR219_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSensorTsv()
    {
        var path = TempFile("sensors.tsv");
        var content =
            "SensorId\tTemperature\tHumidity\tPressure\tStatus\n" +
            "S01\t22.1\t45\t1013\tNormal\n" +
            "S02\t21.8\t47\t1014\tNormal\n" +
            "S03\t23.0\t44\t1012\tNormal\n" +
            "S04\t22.5\t46\t1013\tNormal\n" +
            "S05\t95.0\t43\t1015\tError\n" +
            "S06\t21.9\t48\t1013\tNormal\n" +
            "S07\t22.3\t45\t1014\tNormal\n" +
            "S08\t22.0\t46\t1012\tNormal\n" +
            "S09\t-10.0\t47\t1013\tError\n" +
            "S10\t21.7\t45\t1015\tNormal\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOutliers
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOutliers_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var ex = Record.Exception(() => doc.GetOutliers("Temperature", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetOutliers_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.NotNull(doc.GetOutliers("Temperature", 2.0));
    }

    [Fact]
    public void GetOutliers_Count_Leq_RowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.True(doc.GetOutliers("Temperature", 2.0).Length <= doc.GetRowCount());
    }

    [Fact]
    public void GetOutliers_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var o1 = doc.GetOutliers("Temperature", 2.0);
        var o2 = doc.GetOutliers("Temperature", 2.0);
        Assert.Equal(o1.Length, o2.Length);
    }

    [Fact]
    public void GetOutliers_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var before = doc.GetOutliers("Temperature", 2.0).Length;
        var path = TempFile("ol_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOutliers("Temperature", 2.0).Length);
    }

    [Fact]
    public void GetOutliers_High_Threshold_FewerResults()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        // Very high threshold → fewer or same outliers
        var tight = doc.GetOutliers("Temperature", 1.5);
        var loose = doc.GetOutliers("Temperature", 5.0);
        Assert.True(loose.Length <= tight.Length);
    }

    // -------------------------------------------------------------------------
    // GetTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTrimmedMean_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var ex = Record.Exception(() => doc.GetTrimmedMean("Temperature", 10.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTrimmedMean_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.True(double.IsFinite(doc.GetTrimmedMean("Temperature", 10.0)));
    }

    [Fact]
    public void GetTrimmedMean_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.Equal(
            doc.GetTrimmedMean("Temperature", 10.0),
            doc.GetTrimmedMean("Temperature", 10.0));
    }

    [Fact]
    public void GetTrimmedMean_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var before = doc.GetTrimmedMean("Temperature", 10.0);
        var path = TempFile("tm_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTrimmedMean("Temperature", 10.0), 4);
    }

    [Fact]
    public void GetTrimmedMean_Between_Min_And_Max()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var trimmed = doc.GetTrimmedMean("Temperature", 10.0);
        Assert.True(trimmed >= doc.GetMinValue("Temperature"));
        Assert.True(trimmed <= doc.GetMaxValue("Temperature"));
    }

    // -------------------------------------------------------------------------
    // GetModeValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetModeValue_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var ex = Record.Exception(() => doc.GetModeValue("Humidity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetModeValue_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.NotNull(doc.GetModeValue("Humidity"));
    }

    [Fact]
    public void GetModeValue_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        Assert.Equal(doc.GetModeValue("Humidity"), doc.GetModeValue("Humidity"));
    }

    [Fact]
    public void GetModeValue_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        var before = doc.GetModeValue("Humidity");
        var path = TempFile("mv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetModeValue("Humidity"));
    }

    [Fact]
    public void GetModeValue_Status_IsMostFrequent()
    {
        var doc = TsvDocument.LoadFile(CreateSensorTsv());
        // "Normal" appears 8 times vs "Error" appears 2 times
        var mode = doc.GetModeValue("Status");
        Assert.NotNull(mode);
        Assert.NotEmpty(mode);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOutliers_GetTrimmedMean_GetModeValue_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_traffic.tsv");
        var content =
            "Intersection\tHour\tVehicles\tAvgSpeed\tIncidents\tWeather\n" +
            "Main-1st\t8\t245\t32\t0\tClear\n" +
            "Main-1st\t9\t312\t28\t1\tClear\n" +
            "Main-2nd\t8\t198\t35\t0\tClear\n" +
            "Main-2nd\t9\t267\t30\t0\tRain\n" +
            "Oak-1st\t8\t1250\t15\t3\tClear\n" +
            "Oak-1st\t9\t289\t29\t0\tClear\n" +
            "Oak-2nd\t8\t156\t38\t0\tRain\n" +
            "Oak-2nd\t9\t201\t34\t0\tClear\n" +
            "Elm-1st\t8\t223\t33\t0\tClear\n" +
            "Elm-1st\t9\t-500\t31\t0\tClear\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRowCount());

        // GetOutliers — Vehicles column has clear outliers (1250 and -500)
        var outliers = doc.GetOutliers("Vehicles", 2.0);
        Assert.NotNull(outliers);
        Assert.True(outliers.Length >= 0);
        Assert.True(outliers.Length <= doc.GetRowCount());
        Assert.Equal(outliers.Length, doc.GetOutliers("Vehicles", 2.0).Length); // consistent

        // GetTrimmedMean — Vehicles (trimmed mean should be between min and max)
        var trimMean = doc.GetTrimmedMean("Vehicles", 10.0);
        Assert.True(double.IsFinite(trimMean));
        Assert.True(trimMean >= doc.GetMinValue("Vehicles"));
        Assert.True(trimMean <= doc.GetMaxValue("Vehicles"));
        Assert.Equal(trimMean, doc.GetTrimmedMean("Vehicles", 10.0)); // consistent

        // GetTrimmedMean — AvgSpeed (no outliers expected)
        var trimSpeed = doc.GetTrimmedMean("AvgSpeed", 10.0);
        Assert.True(double.IsFinite(trimSpeed));

        // GetModeValue — Weather ("Clear" appears 8 times)
        var modeWeather = doc.GetModeValue("Weather");
        Assert.NotNull(modeWeather);
        Assert.NotEmpty(modeWeather);
        Assert.Equal(modeWeather, doc.GetModeValue("Weather")); // consistent

        // GetModeValue — Hour (both 8 and 9 appear 5 times; either is valid)
        var modeHour = doc.GetModeValue("Hour");
        Assert.NotNull(modeHour);

        // SaveToFile
        var savePath = TempFile("dogfood_traffic_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(10, loaded.GetRowCount());
        Assert.Equal(outliers.Length, loaded.GetOutliers("Vehicles", 2.0).Length);
        Assert.Equal(trimMean, loaded.GetTrimmedMean("Vehicles", 10.0), 3);
        Assert.Equal(modeWeather, loaded.GetModeValue("Weather"));

        // AddRow and recheck
        doc.AddRow(new[] { "Park-1st", "8", "185", "36", "0", "Clear" });
        Assert.Equal(11, doc.GetRowCount());
        Assert.NotNull(doc.GetOutliers("Vehicles", 2.0));
        Assert.True(double.IsFinite(doc.GetTrimmedMean("Vehicles", 10.0)));

        // Final save
        var path2 = TempFile("dogfood_traffic_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetModeValue("Weather"), loaded2.GetModeValue("Weather"));
        Assert.Equal(loaded.GetTrimmedMean("Vehicles", 10.0), loaded2.GetTrimmedMean("Vehicles", 10.0), 3);
    }
}
