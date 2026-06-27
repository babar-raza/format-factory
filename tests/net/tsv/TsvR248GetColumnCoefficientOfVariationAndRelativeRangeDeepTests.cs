// Tests for TsvDocument.GetColumnCoefficientOfVariation, GetColumnRelativeRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R248

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R248: Tests for TsvDocument.GetColumnCoefficientOfVariation, GetColumnRelativeRange deeper.
/// GetColumnCoefficientOfVariation(colName): returns std/mean for a numeric column (CV = sigma/mu).
/// GetColumnRelativeRange(colName): returns (max-min)/mean for a numeric column.
/// Covers: GetColumnCoefficientOfVariation no-throw; GetColumnCoefficientOfVariation non-negative;
/// GetColumnCoefficientOfVariation zero for constant; GetColumnCoefficientOfVariation consistent;
/// GetColumnCoefficientOfVariation save-load;
/// GetColumnRelativeRange no-throw; GetColumnRelativeRange non-negative;
/// GetColumnRelativeRange zero for constant; GetColumnRelativeRange consistent;
/// GetColumnRelativeRange save-load;
/// dogfood CreateDoc→GetColumnCoefficientOfVariation→GetColumnRelativeRange pipeline.
/// </summary>
public class TsvR248GetColumnCoefficientOfVariationAndRelativeRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR248GetColumnCoefficientOfVariationAndRelativeRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR248_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("station_id\ttemperature\thumidity\twind_speed");
        var rng = new Random(42);
        for (int i = 0; i < 60; i++)
            sb.AppendLine($"STN{i:D3}\t{(10.0 + rng.NextDouble() * 20.0):F2}\t{(40.0 + rng.NextDouble() * 50.0):F1}\t{(0.5 + rng.NextDouble() * 15.0):F2}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue\tcategory");
        for (int i = 0; i < 20; i++)
            sb.AppendLine($"{i}\t50\tA");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnCoefficientOfVariation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCoefficientOfVariation_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnCoefficientOfVariation("temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnCoefficientOfVariation("temperature") >= 0.0);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnCoefficientOfVariation("value"), precision: 6);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnCoefficientOfVariation("humidity");
        var v2 = doc.GetColumnCoefficientOfVariation("humidity");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnCoefficientOfVariation_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnCoefficientOfVariation("wind_speed");
        var path = TempFile("cv_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCoefficientOfVariation("wind_speed"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnRelativeRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnRelativeRange_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnRelativeRange("temperature"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnRelativeRange_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnRelativeRange("temperature") >= 0.0);
    }

    [Fact]
    public void GetColumnRelativeRange_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0.0, doc.GetColumnRelativeRange("value"), precision: 6);
    }

    [Fact]
    public void GetColumnRelativeRange_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnRelativeRange("humidity");
        var v2 = doc.GetColumnRelativeRange("humidity");
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnRelativeRange_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnRelativeRange("wind_speed");
        var path = TempFile("rr_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnRelativeRange("wind_speed"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnCoefficientOfVariation_GetColumnRelativeRange_Pipeline()
    {
        // Environmental monitoring — NO2 and PM10 continuous monitoring data across UK urban stations
        var path = TempFile("air_quality_no2_pm10.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("site_code\tsite_type\tno2_ug_m3\tpm10_ug_m3\to3_ug_m3\ttemperature_c\twind_speed_ms\twind_direction_deg");
        var rng = new Random(20240701);
        string[] siteTypes = { "Urban_Background", "Urban_Traffic", "Suburban", "Rural", "Industrial" };
        for (int i = 0; i < 150; i++)
        {
            var type = siteTypes[i % siteTypes.Length];
            double no2 = type == "Urban_Traffic" ? 35 + rng.NextDouble() * 50 : 10 + rng.NextDouble() * 30;
            double pm10 = 15 + rng.NextDouble() * 35;
            double o3 = 40 + rng.NextDouble() * 60;
            double temp = 8 + rng.NextDouble() * 18;
            double ws = 0.5 + rng.NextDouble() * 10;
            double wd = rng.NextDouble() * 360;
            sb.AppendLine($"UK{i:D4}\t{type}\t{no2:F1}\t{pm10:F1}\t{o3:F1}\t{temp:F1}\t{ws:F2}\t{wd:F0}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(150, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // GetColumnCoefficientOfVariation
        var cvNo2 = doc.GetColumnCoefficientOfVariation("no2_ug_m3");
        Assert.True(cvNo2 >= 0.0);
        Assert.Equal(cvNo2, doc.GetColumnCoefficientOfVariation("no2_ug_m3")); // consistent

        var cvPm10 = doc.GetColumnCoefficientOfVariation("pm10_ug_m3");
        Assert.True(cvPm10 >= 0.0);

        var cvO3 = doc.GetColumnCoefficientOfVariation("o3_ug_m3");
        Assert.True(cvO3 >= 0.0);

        var cvTemp = doc.GetColumnCoefficientOfVariation("temperature_c");
        Assert.True(cvTemp >= 0.0);

        // GetColumnRelativeRange
        var rrNo2 = doc.GetColumnRelativeRange("no2_ug_m3");
        Assert.True(rrNo2 >= 0.0);
        Assert.Equal(rrNo2, doc.GetColumnRelativeRange("no2_ug_m3")); // consistent

        var rrPm10 = doc.GetColumnRelativeRange("pm10_ug_m3");
        Assert.True(rrPm10 >= 0.0);

        var rrWs = doc.GetColumnRelativeRange("wind_speed_ms");
        Assert.True(rrWs >= 0.0);

        // Basic stats
        Assert.True(doc.GetColumnMin("no2_ug_m3") <= doc.GetColumnMax("no2_ug_m3"));
        Assert.True(doc.GetColumnMean("temperature_c") > 0.0);
        Assert.True(doc.GetColumnStdDev("pm10_ug_m3") >= 0.0);

        // Quantile
        var q25 = doc.GetColumnQuantile("no2_ug_m3", 0.25);
        var q75 = doc.GetColumnQuantile("no2_ug_m3", 0.75);
        Assert.True(q25 <= q75);

        // SaveToFile
        var outPath = TempFile("air_quality_no2_pm10_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(cvNo2, loaded.GetColumnCoefficientOfVariation("no2_ug_m3"), precision: 8);
        Assert.Equal(rrNo2, loaded.GetColumnRelativeRange("no2_ug_m3"), precision: 8);
        Assert.Equal(cvPm10, loaded.GetColumnCoefficientOfVariation("pm10_ug_m10"), precision: 8);

        // Constant column test
        var path2 = TempFile("constant_no2.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("site\tno2_fixed\tpm10");
        for (int i = 0; i < 30; i++)
            sb2.AppendLine($"S{i:D2}\t40\t{(15 + i * 0.5):F1}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetColumnCoefficientOfVariation("no2_fixed"), precision: 6);
        Assert.Equal(0.0, doc2.GetColumnRelativeRange("no2_fixed"), precision: 6);
        Assert.True(doc2.GetColumnCoefficientOfVariation("pm10") > 0.0);
    }
}
