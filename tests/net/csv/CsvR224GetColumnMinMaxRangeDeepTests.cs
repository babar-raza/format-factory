// Tests for CsvDocument.GetColumnMin, GetColumnMax, GetColumnRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R224

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R224: Tests for CsvDocument.GetColumnMin, GetColumnMax, GetColumnRange deeper.
/// GetColumnMin(colName): returns the minimum numeric value in the column.
/// GetColumnMax(colName): returns the maximum numeric value in the column.
/// GetColumnRange(colName): returns max - min for the numeric column.
/// Covers: GetColumnMin no-throw; GetColumnMin leq mean; GetColumnMin leq max;
/// GetColumnMin consistent; GetColumnMin save-load;
/// GetColumnMax no-throw; GetColumnMax geq mean; GetColumnMax geq min;
/// GetColumnMax consistent; GetColumnMax save-load;
/// GetColumnRange no-throw; GetColumnRange non-negative; GetColumnRange equals max-min;
/// GetColumnRange consistent; GetColumnRange save-load;
/// dogfood LoadFile→GetColumnMin→GetColumnMax→GetColumnRange→SaveToFile pipeline.
/// </summary>
public class CsvR224GetColumnMinMaxRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR224GetColumnMinMaxRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR224_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSensorCsv()
    {
        var path = TempFile("sensors.csv");
        var content =
            "SensorId,Temperature,Pressure,Humidity,CO2,Voltage\n" +
            "S001,22.4,1013.5,48.2,412,3.28\n" +
            "S002,25.1,1010.2,52.7,438,3.31\n" +
            "S003,19.8,1016.8,44.5,398,3.25\n" +
            "S004,28.6,1008.4,61.3,465,3.35\n" +
            "S005,17.2,1018.9,41.8,385,3.22\n" +
            "S006,31.4,1005.7,67.9,492,3.38\n" +
            "S007,23.9,1012.1,50.4,425,3.29\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMin_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var ex = Record.Exception(() => doc.GetColumnMin("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMin_Leq_Mean()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.True(doc.GetColumnMin("Temperature") <= doc.GetMean("Temperature"));
    }

    [Fact]
    public void GetColumnMin_Leq_Max()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.True(doc.GetColumnMin("Pressure") <= doc.GetColumnMax("Pressure"));
    }

    [Fact]
    public void GetColumnMin_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.Equal(doc.GetColumnMin("CO2"), doc.GetColumnMin("CO2"));
    }

    [Fact]
    public void GetColumnMin_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var before = doc.GetColumnMin("Temperature");
        var path = TempFile("min_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMin("Temperature"), 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMax_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var ex = Record.Exception(() => doc.GetColumnMax("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMax_Geq_Mean()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.True(doc.GetColumnMax("Humidity") >= doc.GetMean("Humidity"));
    }

    [Fact]
    public void GetColumnMax_Geq_Min()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.True(doc.GetColumnMax("Voltage") >= doc.GetColumnMin("Voltage"));
    }

    [Fact]
    public void GetColumnMax_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.Equal(doc.GetColumnMax("CO2"), doc.GetColumnMax("CO2"));
    }

    [Fact]
    public void GetColumnMax_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var before = doc.GetColumnMax("Pressure");
        var path = TempFile("max_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMax("Pressure"), 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRange_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var ex = Record.Exception(() => doc.GetColumnRange("Temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRange_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.True(doc.GetColumnRange("Humidity") >= 0.0);
    }

    [Fact]
    public void GetColumnRange_Equals_MaxMinusMin()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var range = doc.GetColumnRange("CO2");
        var expected = doc.GetColumnMax("CO2") - doc.GetColumnMin("CO2");
        Assert.Equal(expected, range, 4);
    }

    [Fact]
    public void GetColumnRange_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        Assert.Equal(doc.GetColumnRange("Voltage"), doc.GetColumnRange("Voltage"));
    }

    [Fact]
    public void GetColumnRange_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSensorCsv());
        var before = doc.GetColumnRange("Temperature");
        var path = TempFile("range_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRange("Temperature"), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMin_GetColumnMax_GetColumnRange_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_properties.csv");
        var content =
            "PropertyId,ListPrice,SqFt,Bedrooms,Bathrooms,YearBuilt,DaysOnMarket\n" +
            "P001,425000,1850,3,2,1998,14\n" +
            "P002,685000,2400,4,3,2005,7\n" +
            "P003,310000,1250,2,1,1985,28\n" +
            "P004,920000,3200,5,4,2018,3\n" +
            "P005,275000,1100,2,1,1978,45\n" +
            "P006,540000,2050,3,2,2010,11\n" +
            "P007,780000,2750,4,3,2015,5\n" +
            "P008,380000,1550,3,2,1995,19\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetColumnMin — ListPrice
        var minPrice = doc.GetColumnMin("ListPrice");
        Assert.True(minPrice > 0);
        Assert.Equal(minPrice, doc.GetColumnMin("ListPrice")); // consistent

        // GetColumnMax — ListPrice
        var maxPrice = doc.GetColumnMax("ListPrice");
        Assert.True(maxPrice >= minPrice);

        // GetColumnRange — ListPrice
        var rangePrice = doc.GetColumnRange("ListPrice");
        Assert.True(rangePrice >= 0);
        Assert.Equal(maxPrice - minPrice, rangePrice, 2);

        // GetColumnMin/Max — SqFt
        var minSqFt = doc.GetColumnMin("SqFt");
        var maxSqFt = doc.GetColumnMax("SqFt");
        Assert.True(minSqFt > 0);
        Assert.True(maxSqFt >= minSqFt);
        Assert.Equal(maxSqFt - minSqFt, doc.GetColumnRange("SqFt"), 2);

        // GetColumnMin/Max — YearBuilt
        var minYear = doc.GetColumnMin("YearBuilt");
        var maxYear = doc.GetColumnMax("YearBuilt");
        Assert.True(minYear > 1900);
        Assert.True(maxYear >= minYear);

        // GetColumnRange — DaysOnMarket
        var rangeDays = doc.GetColumnRange("DaysOnMarket");
        Assert.True(rangeDays >= 0);
        Assert.Equal(doc.GetColumnMax("DaysOnMarket") - doc.GetColumnMin("DaysOnMarket"), rangeDays, 2);

        // AddRow and recheck
        doc.AddRow(new[] { "P009", "615000", "2200", "4", "3", "2012", "9" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.GetColumnMin("ListPrice") <= doc.GetColumnMax("ListPrice"));
        Assert.True(doc.GetColumnRange("Bedrooms") >= 0);

        // SaveToFile
        var savePath = TempFile("dogfood_properties_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetColumnMin("ListPrice"), loaded.GetColumnMin("ListPrice"), 2);
        Assert.Equal(doc.GetColumnMax("SqFt"), loaded.GetColumnMax("SqFt"), 2);
        Assert.Equal(doc.GetColumnRange("YearBuilt"), loaded.GetColumnRange("YearBuilt"), 2);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("ListPrice", cols);
        Assert.Contains("DaysOnMarket", cols);

        // Final save
        var path2 = TempFile("dogfood_properties_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetColumnMin("ListPrice"), loaded2.GetColumnMin("ListPrice"), 2);
        Assert.Equal(loaded.GetColumnMax("SqFt"), loaded2.GetColumnMax("SqFt"), 2);
        Assert.Equal(loaded.GetColumnRange("DaysOnMarket"), loaded2.GetColumnRange("DaysOnMarket"), 2);
    }
}
