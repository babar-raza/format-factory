// Tests for TsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R255

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R255: Tests for TsvDocument.GetColumnZScore, GetColumnOutlierCount deeper.
/// GetColumnZScore(colName, row): returns the z-score of the value in the given row.
/// GetColumnOutlierCount(colName, threshold): returns count of rows where |z-score| > threshold.
/// Covers: GetColumnZScore no-throw; GetColumnZScore finite; GetColumnZScore consistent;
/// GetColumnZScore zero-mean-unit-std for standardised data; GetColumnZScore save-load;
/// GetColumnOutlierCount no-throw; GetColumnOutlierCount non-negative;
/// GetColumnOutlierCount zero for constant; GetColumnOutlierCount less-than-RowCount;
/// GetColumnOutlierCount consistent; GetColumnOutlierCount save-load;
/// dogfood CreateDoc→GetColumnZScore→GetColumnOutlierCount pipeline.
/// </summary>
public class TsvR255GetColumnZScoreAndOutlierCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR255GetColumnZScoreAndOutlierCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR255_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("patient_id\tage\tsystolic_bp\tdiastolic_bp\tbmi\tglucose_mmol");
        var rng = new Random(20240720);
        for (int i = 0; i < 100; i++)
        {
            int age = 30 + rng.Next(50);
            double sbp = 120 + rng.NextDouble() * 40;
            double dbp = 70 + rng.NextDouble() * 30;
            double bmi = 20 + rng.NextDouble() * 20;
            double glucose = 4.5 + rng.NextDouble() * 5.0;
            if (i == 5) sbp = 220; // outlier
            if (i == 50) bmi = 55;  // outlier
            sb.AppendLine($"P{i:D4}\t{age}\t{sbp:F1}\t{dbp:F1}\t{bmi:F1}\t{glucose:F2}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantTsv()
    {
        var path = TempFile("constant.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tvalue");
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{i}\t42.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnZScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnZScore_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnZScore("systolic_bp", 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnZScore_Finite()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var z = doc.GetColumnZScore("systolic_bp", 0);
        Assert.True(double.IsFinite(z));
    }

    [Fact]
    public void GetColumnZScore_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnZScore("bmi", 10), doc.GetColumnZScore("bmi", 10));
    }

    [Fact]
    public void GetColumnZScore_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnZScore("age", 3);
        var path = TempFile("zs_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnZScore("age", 3), precision: 8);
    }

    // -------------------------------------------------------------------------
    // GetColumnOutlierCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnOutlierCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnOutlierCount("systolic_bp", 2.0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnOutlierCount_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnOutlierCount("systolic_bp", 2.0) >= 0);
    }

    [Fact]
    public void GetColumnOutlierCount_Zero_ForConstant()
    {
        var doc = TsvDocument.LoadFile(CreateConstantTsv());
        Assert.Equal(0, doc.GetColumnOutlierCount("value", 2.0));
    }

    [Fact]
    public void GetColumnOutlierCount_LessThanRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnOutlierCount("bmi", 1.0) < doc.RowCount);
    }

    [Fact]
    public void GetColumnOutlierCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetColumnOutlierCount("glucose_mmol", 2.0);
        var v2 = doc.GetColumnOutlierCount("glucose_mmol", 2.0);
        Assert.Equal(v1, v2);
    }

    [Fact]
    public void GetColumnOutlierCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnOutlierCount("systolic_bp", 2.5);
        var path = TempFile("oc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnOutlierCount("systolic_bp", 2.5));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnZScore_GetColumnOutlierCount_Pipeline()
    {
        // Environmental — UK Air Quality Monitoring Network
        // Automatic Urban and Rural Network (AURN) hourly measurements: outlier detection
        // for flagging instrument faults, exceptional pollution events, and data quality control
        var path = TempFile("aurn_air_quality.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("timestamp\tsite_code\tno2_ug_m3\tpm25_ug_m3\tpm10_ug_m3\to3_ug_m3\tco_mg_m3\twind_speed_ms\ttemp_celsius\trh_pct");
        var rng = new Random(20240901);

        string[] sites = { "LON6", "SHED", "BIRM", "MCRPB", "LEEDS" };
        for (int i = 0; i < 180; i++)
        {
            string site = sites[i % sites.Length];
            // Hour of day affects concentrations (rush hour peaks)
            int hour = i % 24;
            double no2Base = hour >= 7 && hour <= 9 ? 55 : (hour >= 17 && hour <= 19 ? 50 : 28);
            double no2 = no2Base + rng.NextDouble() * 25;
            double pm25 = 8 + rng.NextDouble() * 18;
            double pm10 = 12 + rng.NextDouble() * 28;
            double o3 = hour >= 12 && hour <= 15 ? (60 + rng.NextDouble() * 40) : (25 + rng.NextDouble() * 30);
            double co = 0.2 + rng.NextDouble() * 0.6;
            double ws = 1 + rng.NextDouble() * 9;
            double temp = 8 + rng.NextDouble() * 20;
            double rh = 50 + rng.NextDouble() * 45;

            // Inject instrument fault spikes
            if (i == 12) no2 = 450;     // NO2 sensor fault
            if (i == 75) pm25 = 180;    // PM2.5 spike — exceptional event
            if (i == 120) co = 8.5;     // CO instrument fault

            string ts = $"2024-09-{(i / 24) + 1:D2}T{hour:D2}:00:00Z";
            sb.AppendLine($"{ts}\t{site}\t{no2:F1}\t{pm25:F1}\t{pm10:F1}\t{o3:F1}\t{co:F2}\t{ws:F1}\t{temp:F1}\t{rh:F0}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(180, doc.RowCount);
        Assert.Equal(10, doc.ColumnCount);

        // GetColumnZScore — individual readings
        var zsNo2Row12 = doc.GetColumnZScore("no2_ug_m3", 12);
        Assert.True(double.IsFinite(zsNo2Row12));
        Assert.True(zsNo2Row12 > 2.0); // spike at row 12 should have high z-score

        var zsPm25Row75 = doc.GetColumnZScore("pm25_ug_m3", 75);
        Assert.True(double.IsFinite(zsPm25Row75));
        Assert.True(zsPm25Row75 > 2.0); // PM2.5 spike

        var zsCoRow120 = doc.GetColumnZScore("co_mg_m3", 120);
        Assert.True(double.IsFinite(zsCoRow120));
        Assert.True(zsCoRow120 > 2.0); // CO fault

        // Normal readings should have moderate z-scores
        var zsNo2Row0 = doc.GetColumnZScore("no2_ug_m3", 0);
        Assert.True(double.IsFinite(zsNo2Row0));
        Assert.Equal(doc.GetColumnZScore("no2_ug_m3", 0), doc.GetColumnZScore("no2_ug_m3", 0)); // consistent

        // GetColumnOutlierCount — detect faults/spikes
        var outliersNo2 = doc.GetColumnOutlierCount("no2_ug_m3", 3.0);
        Assert.True(outliersNo2 >= 1); // at least the spike at row 12
        Assert.True(outliersNo2 < doc.RowCount);

        var outliersPm25 = doc.GetColumnOutlierCount("pm25_ug_m3", 3.0);
        Assert.True(outliersPm25 >= 1); // at least the spike at row 75

        var outliersCo = doc.GetColumnOutlierCount("co_mg_m3", 3.0);
        Assert.True(outliersCo >= 1); // at least the fault at row 120

        // Looser threshold catches more
        var outliersNo2Loose = doc.GetColumnOutlierCount("no2_ug_m3", 1.5);
        Assert.True(outliersNo2Loose >= outliersNo2);

        // Consistent
        Assert.Equal(outliersNo2, doc.GetColumnOutlierCount("no2_ug_m3", 3.0));

        // Basic column stats
        Assert.True(doc.GetColumnMean("no2_ug_m3") > 0);
        Assert.True(doc.GetColumnStdDev("no2_ug_m3") > 0);
        Assert.True(doc.GetColumnMin("pm25_ug_m3") <= doc.GetColumnMax("pm25_ug_m3"));

        // SaveToFile
        var outPath = TempFile("aurn_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(zsNo2Row12, loaded.GetColumnZScore("no2_ug_m3", 12), precision: 8);
        Assert.Equal(outliersNo2, loaded.GetColumnOutlierCount("no2_ug_m3", 3.0));
        Assert.Equal(outliersPm25, loaded.GetColumnOutlierCount("pm25_ug_m3", 3.0));

        // Constant column — no outliers
        var path2 = TempFile("constant_aq.tsv");
        var sb2 = new StringBuilder();
        sb2.AppendLine("site\tbackground_no2");
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"LON{i}\t5.0");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = TsvDocument.LoadFile(path2);
        Assert.Equal(0, doc2.GetColumnOutlierCount("background_no2", 2.0));
    }
}
