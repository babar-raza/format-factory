// Tests for TsvDocument.GetColumnMin, GetColumnMax, GetColumnRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R222: Tests for TsvDocument.GetColumnMin, GetColumnMax, GetColumnRange deeper.
/// GetColumnMin(colName): returns the minimum numeric value in the column.
/// GetColumnMax(colName): returns the maximum numeric value in the column.
/// GetColumnRange(colName): returns max - min for numeric column.
/// Covers: GetColumnMin no-throw; GetColumnMin leq mean; GetColumnMin consistent;
/// GetColumnMin save-load; GetColumnMin leq GetColumnMax;
/// GetColumnMax no-throw; GetColumnMax geq mean; GetColumnMax consistent;
/// GetColumnMax save-load; GetColumnMax geq GetColumnMin;
/// GetColumnRange no-throw; GetColumnRange non-negative; GetColumnRange consistent;
/// GetColumnRange save-load; GetColumnRange equals max-min;
/// dogfood LoadFile→GetColumnMin→GetColumnMax→GetColumnRange→SaveToFile pipeline.
/// </summary>
public class TsvR222GetColumnStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR222GetColumnStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR222_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEconTsv()
    {
        var path = TempFile("economy.tsv");
        var content =
            "Country\tGDP\tInflation\tUnemployment\tDebtRatio\n" +
            "Alpha\t2450.5\t3.2\t4.8\t62.1\n" +
            "Beta\t1820.3\t5.7\t7.2\t78.4\n" +
            "Gamma\t3100.8\t2.1\t3.5\t45.6\n" +
            "Delta\t980.6\t8.3\t9.1\t95.2\n" +
            "Epsilon\t4200.2\t1.8\t2.9\t38.7\n" +
            "Zeta\t1560.9\t4.5\t6.3\t71.0\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMin_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var ex = Record.Exception(() => doc.GetColumnMin("GDP"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMin_Leq_Mean()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.True(doc.GetColumnMin("GDP") <= doc.GetMean("GDP"));
    }

    [Fact]
    public void GetColumnMin_Leq_Max()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.True(doc.GetColumnMin("GDP") <= doc.GetColumnMax("GDP"));
    }

    [Fact]
    public void GetColumnMin_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.Equal(doc.GetColumnMin("Inflation"), doc.GetColumnMin("Inflation"));
    }

    [Fact]
    public void GetColumnMin_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var before = doc.GetColumnMin("GDP");
        var path = TempFile("min_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMin("GDP"), 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMax_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var ex = Record.Exception(() => doc.GetColumnMax("GDP"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMax_Geq_Mean()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.True(doc.GetColumnMax("GDP") >= doc.GetMean("GDP"));
    }

    [Fact]
    public void GetColumnMax_Geq_Min()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.True(doc.GetColumnMax("Unemployment") >= doc.GetColumnMin("Unemployment"));
    }

    [Fact]
    public void GetColumnMax_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.Equal(doc.GetColumnMax("DebtRatio"), doc.GetColumnMax("DebtRatio"));
    }

    [Fact]
    public void GetColumnMax_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var before = doc.GetColumnMax("Inflation");
        var path = TempFile("max_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMax("Inflation"), 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRange_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var ex = Record.Exception(() => doc.GetColumnRange("GDP"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRange_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.True(doc.GetColumnRange("GDP") >= 0.0);
    }

    [Fact]
    public void GetColumnRange_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        Assert.Equal(doc.GetColumnRange("DebtRatio"), doc.GetColumnRange("DebtRatio"));
    }

    [Fact]
    public void GetColumnRange_Equals_MaxMinuMin()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var range = doc.GetColumnRange("Inflation");
        var expected = doc.GetColumnMax("Inflation") - doc.GetColumnMin("Inflation");
        Assert.Equal(expected, range, 4);
    }

    [Fact]
    public void GetColumnRange_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEconTsv());
        var before = doc.GetColumnRange("Unemployment");
        var path = TempFile("range_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRange("Unemployment"), 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMin_GetColumnMax_GetColumnRange_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_climate.tsv");
        var content =
            "Station\tMaxTemp\tMinTemp\tRainfall\tHumidity\tWindSpeed\n" +
            "Station_A\t32.4\t18.2\t45.6\t72.0\t15.3\n" +
            "Station_B\t28.7\t15.9\t62.1\t68.5\t22.7\n" +
            "Station_C\t35.1\t20.4\t28.3\t65.2\t18.9\n" +
            "Station_D\t24.6\t12.8\t88.4\t81.3\t12.1\n" +
            "Station_E\t38.9\t22.7\t15.2\t58.7\t28.4\n" +
            "Station_F\t29.3\t16.5\t71.8\t75.1\t19.6\n" +
            "Station_G\t31.8\t19.1\t52.4\t69.8\t17.2\n" +
            "Station_H\t26.2\t14.3\t95.7\t83.6\t10.8\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetColumnMin — MaxTemp
        var minTemp = doc.GetColumnMin("MaxTemp");
        Assert.True(minTemp > 0);
        Assert.Equal(minTemp, doc.GetColumnMin("MaxTemp")); // consistent

        // GetColumnMax — MaxTemp
        var maxTemp = doc.GetColumnMax("MaxTemp");
        Assert.True(maxTemp >= minTemp);
        Assert.Equal(maxTemp, doc.GetColumnMax("MaxTemp")); // consistent

        // GetColumnRange — MaxTemp
        var rangeTemp = doc.GetColumnRange("MaxTemp");
        Assert.True(rangeTemp >= 0);
        Assert.Equal(maxTemp - minTemp, rangeTemp, 4);

        // GetColumnMin/Max — Rainfall
        var minRain = doc.GetColumnMin("Rainfall");
        var maxRain = doc.GetColumnMax("Rainfall");
        Assert.True(minRain >= 0);
        Assert.True(maxRain >= minRain);
        Assert.Equal(maxRain - minRain, doc.GetColumnRange("Rainfall"), 4);

        // GetColumnMin/Max — WindSpeed
        var minWind = doc.GetColumnMin("WindSpeed");
        var maxWind = doc.GetColumnMax("WindSpeed");
        Assert.True(minWind >= 0);
        Assert.True(maxWind >= minWind);

        // AddRow and recheck
        doc.AddRow(new[] { "Station_I", "33.5", "17.8", "41.2", "70.4", "21.0" });
        Assert.Equal(9, doc.GetRowCount());
        Assert.True(doc.GetColumnMin("MaxTemp") <= doc.GetColumnMax("MaxTemp"));
        Assert.True(doc.GetColumnRange("Humidity") >= 0);

        // SaveToFile
        var savePath = TempFile("dogfood_climate_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(doc.GetColumnMin("MaxTemp"), loaded.GetColumnMin("MaxTemp"), 4);
        Assert.Equal(doc.GetColumnMax("MaxTemp"), loaded.GetColumnMax("MaxTemp"), 4);
        Assert.Equal(doc.GetColumnRange("Rainfall"), loaded.GetColumnRange("Rainfall"), 4);

        // GetColumnNames cross-check
        var cols = loaded.GetColumnNames();
        Assert.Contains("MaxTemp", cols);
        Assert.Contains("Rainfall", cols);

        // Final save
        var path2 = TempFile("dogfood_climate_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetColumnMin("WindSpeed"), loaded2.GetColumnMin("WindSpeed"), 4);
        Assert.Equal(loaded.GetColumnMax("WindSpeed"), loaded2.GetColumnMax("WindSpeed"), 4);
        Assert.Equal(loaded.GetColumnRange("MinTemp"), loaded2.GetColumnRange("MinTemp"), 4);
    }
}
