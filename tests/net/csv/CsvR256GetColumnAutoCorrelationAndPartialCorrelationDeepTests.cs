// Tests for CsvDocument.GetColumnAutoCorrelation, GetColumnPartialCorrelation deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R256

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R256: Tests for CsvDocument.GetColumnAutoCorrelation, GetColumnPartialCorrelation deeper.
/// GetColumnAutoCorrelation(colName, lag): returns autocorrelation at the given lag.
/// GetColumnPartialCorrelation(colName1, colName2, controlCol): returns partial correlation.
/// Covers: GetColumnAutoCorrelation no-throw; GetColumnAutoCorrelation in [-1,1];
/// GetColumnAutoCorrelation lag0 equals 1.0; GetColumnAutoCorrelation consistent;
/// GetColumnAutoCorrelation save-load;
/// GetColumnPartialCorrelation no-throw; GetColumnPartialCorrelation in [-1,1];
/// GetColumnPartialCorrelation consistent; GetColumnPartialCorrelation save-load;
/// dogfood CreateDoc→GetColumnAutoCorrelation→GetColumnPartialCorrelation pipeline.
/// </summary>
public class CsvR256GetColumnAutoCorrelationAndPartialCorrelationDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR256GetColumnAutoCorrelationAndPartialCorrelationDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR256_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTimeSeriesCsv()
    {
        var path = TempFile("time_series.csv");
        var sb = new StringBuilder();
        sb.AppendLine("t,signal,baseline,noise");
        var rng = new Random(20240201);
        double s = 50;
        for (int i = 0; i < 100; i++)
        {
            double baseline = 50 + 5 * Math.Sin(2 * Math.PI * i / 12.0); // seasonal
            double noise = (rng.NextDouble() - 0.5) * 8;
            s = 0.75 * s + 0.25 * (baseline + noise);
            sb.AppendLine($"{i},{s:F4},{baseline:F4},{noise:F4}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnAutoCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAutoCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var ex = Record.Exception(() => doc.GetColumnAutoCorrelation("signal", 1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnAutoCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var ac = doc.GetColumnAutoCorrelation("signal", 1);
        Assert.True(ac >= -1.0 && ac <= 1.0);
    }

    [Fact]
    public void GetColumnAutoCorrelation_Lag0_Equals_One()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("signal", 0), precision: 6);
    }

    [Fact]
    public void GetColumnAutoCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        Assert.Equal(doc.GetColumnAutoCorrelation("signal", 3), doc.GetColumnAutoCorrelation("signal", 3));
    }

    [Fact]
    public void GetColumnAutoCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var before = doc.GetColumnAutoCorrelation("signal", 2);
        var path = TempFile("ac_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnAutoCorrelation("signal", 2), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnPartialCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnPartialCorrelation_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var ex = Record.Exception(() => doc.GetColumnPartialCorrelation("signal", "baseline", "noise"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnPartialCorrelation_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var pc = doc.GetColumnPartialCorrelation("signal", "baseline", "noise");
        Assert.True(pc >= -1.0 && pc <= 1.0);
    }

    [Fact]
    public void GetColumnPartialCorrelation_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        Assert.Equal(
            doc.GetColumnPartialCorrelation("signal", "noise", "baseline"),
            doc.GetColumnPartialCorrelation("signal", "noise", "baseline"));
    }

    [Fact]
    public void GetColumnPartialCorrelation_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateTimeSeriesCsv());
        var before = doc.GetColumnPartialCorrelation("signal", "baseline", "noise");
        var path = TempFile("pc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnPartialCorrelation("signal", "baseline", "noise"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnAutoCorrelation_GetColumnPartialCorrelation_Pipeline()
    {
        // Environmental monitoring — Defra UK Air Quality Archive daily measurements
        // Time series analysis for NO2, PM2.5, PM10 — autocorrelation structure for ARIMA model selection
        var path = TempFile("defra_air_quality_daily.csv");
        var sb = new StringBuilder();
        sb.AppendLine("date,no2_ug_m3,pm25_ug_m3,pm10_ug_m3,o3_ug_m3,temperature_c,wind_speed_ms,relative_humidity_pct");
        var rng = new Random(20240201);

        double no2 = 25, pm25 = 12, pm10 = 20, o3 = 50, temp = 12, ws = 4.5, rh = 75;
        for (int d = 0; d < 150; d++)
        {
            // Day of year seasonality
            double dayFrac = d / 365.0 * 2 * Math.PI;
            double no2Seasonal = 30 - 10 * Math.Sin(dayFrac); // higher in winter
            double o3Seasonal = 50 + 20 * Math.Sin(dayFrac);  // higher in summer
            double tempSeasonal = 12 + 8 * Math.Sin(dayFrac - Math.PI / 2);

            no2 = 0.80 * no2 + 0.20 * no2Seasonal + (rng.NextDouble() - 0.5) * 6;
            no2 = Math.Max(2, no2);
            pm25 = 0.75 * pm25 + 0.25 * 13 + (rng.NextDouble() - 0.5) * 4;
            pm25 = Math.Max(1, pm25);
            pm10 = 0.78 * pm10 + 0.22 * 20 + 0.4 * pm25 + (rng.NextDouble() - 0.5) * 4;
            pm10 = Math.Max(pm25, pm10);
            o3 = 0.85 * o3 + 0.15 * o3Seasonal + (rng.NextDouble() - 0.5) * 8;
            o3 = Math.Max(5, o3);
            temp = 0.88 * temp + 0.12 * tempSeasonal + (rng.NextDouble() - 0.5) * 1.5;
            ws = 0.70 * ws + 0.30 * 4.5 + (rng.NextDouble() - 0.5) * 1.5;
            ws = Math.Max(0.1, ws);
            rh = 0.82 * rh + 0.18 * 75 + (rng.NextDouble() - 0.5) * 5;
            rh = Math.Clamp(rh, 20, 100);

            int year = 2024 + d / 365;
            int dayOfYear = d % 365 + 1;
            sb.AppendLine($"2024-{(dayOfYear / 31 + 1):D2}-{(dayOfYear % 28 + 1):D2},{no2:F1},{pm25:F1},{pm10:F1},{o3:F1},{temp:F1},{ws:F2},{rh:F1}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnAutoCorrelation — NO2 has strong daily autocorrelation
        var ac1No2 = doc.GetColumnAutoCorrelation("no2_ug_m3", 1);
        Assert.True(ac1No2 >= -1.0 && ac1No2 <= 1.0);
        Assert.Equal(ac1No2, doc.GetColumnAutoCorrelation("no2_ug_m3", 1)); // consistent

        var ac1Pm25 = doc.GetColumnAutoCorrelation("pm25_ug_m3", 1);
        Assert.True(ac1Pm25 >= -1.0 && ac1Pm25 <= 1.0);

        var ac7No2 = doc.GetColumnAutoCorrelation("no2_ug_m3", 7); // weekly
        Assert.True(ac7No2 >= -1.0 && ac7No2 <= 1.0);

        // Lag 0 = 1.0
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("no2_ug_m3", 0), precision: 6);
        Assert.Equal(1.0, doc.GetColumnAutoCorrelation("o3_ug_m3", 0), precision: 6);

        // GetColumnPartialCorrelation
        // NO2 and PM10 correlation controlling for wind speed
        var pcNo2Pm10 = doc.GetColumnPartialCorrelation("no2_ug_m3", "pm10_ug_m3", "wind_speed_ms");
        Assert.True(pcNo2Pm10 >= -1.0 && pcNo2Pm10 <= 1.0);
        Assert.Equal(pcNo2Pm10, doc.GetColumnPartialCorrelation("no2_ug_m3", "pm10_ug_m3", "wind_speed_ms")); // consistent

        // O3 and NO2 — anti-correlated (NOx titration) controlling for temperature
        var pcO3No2 = doc.GetColumnPartialCorrelation("o3_ug_m3", "no2_ug_m3", "temperature_c");
        Assert.True(pcO3No2 >= -1.0 && pcO3No2 <= 1.0);

        var pcTempNo2 = doc.GetColumnPartialCorrelation("temperature_c", "no2_ug_m3", "relative_humidity_pct");
        Assert.True(pcTempNo2 >= -1.0 && pcTempNo2 <= 1.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("no2_ug_m3") <= doc.GetColumnMax("no2_ug_m3"));
        Assert.True(doc.GetColumnMean("no2_ug_m3") > 0.0);
        Assert.True(doc.GetColumnStdDev("pm25_ug_m3") >= 0.0);

        // SaveToFile
        var outPath = TempFile("defra_air_quality_daily_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(ac1No2, loaded.GetColumnAutoCorrelation("no2_ug_m3", 1), precision: 8);
        Assert.Equal(ac7No2, loaded.GetColumnAutoCorrelation("no2_ug_m3", 7), precision: 8);
        Assert.Equal(pcNo2Pm10, loaded.GetColumnPartialCorrelation("no2_ug_m3", "pm10_ug_m3", "wind_speed_ms"), precision: 8);
    }
}
