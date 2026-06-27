// Tests for NdjsonDocument.GetFieldCorrelation, GetFieldCovariance, GetFieldPearsonR deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R252

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R252: Tests for NdjsonDocument.GetFieldCorrelation, GetFieldCovariance, GetFieldPearsonR deeper.
/// GetFieldCorrelation(field1, field2): returns Pearson correlation coefficient in [-1,1].
/// GetFieldCovariance(field1, field2): returns sample covariance between two numeric fields.
/// GetFieldPearsonR(field1, field2): alias or variant returning Pearson R statistic.
/// Covers: GetFieldCorrelation no-throw; GetFieldCorrelation in [-1,1]; GetFieldCorrelation consistent;
/// GetFieldCorrelation self-correlation = 1.0;
/// GetFieldCovariance no-throw; GetFieldCovariance finite; GetFieldCovariance consistent;
/// GetFieldCovariance zero for constant field;
/// GetFieldPearsonR no-throw; GetFieldPearsonR in [-1,1]; GetFieldPearsonR consistent;
/// GetFieldPearsonR save-load;
/// dogfood CreateDoc→GetFieldCorrelation→GetFieldCovariance→GetFieldPearsonR pipeline.
/// </summary>
public class NdjsonR252GetFieldCorrelationAndCovarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR252GetFieldCorrelationAndCovarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR252_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSensorNdjson()
    {
        var path = TempFile("sensors.ndjson");
        var lines = new System.Collections.Generic.List<string>
        {
            "{\"sensor_id\":\"S01\",\"temperature\":22.1,\"humidity\":55,\"pressure\":1013}",
            "{\"sensor_id\":\"S02\",\"temperature\":23.5,\"humidity\":52,\"pressure\":1011}",
            "{\"sensor_id\":\"S03\",\"temperature\":24.8,\"humidity\":48,\"pressure\":1009}",
            "{\"sensor_id\":\"S04\",\"temperature\":26.2,\"humidity\":44,\"pressure\":1007}",
            "{\"sensor_id\":\"S05\",\"temperature\":27.1,\"humidity\":41,\"pressure\":1006}",
            "{\"sensor_id\":\"S06\",\"temperature\":28.4,\"humidity\":38,\"pressure\":1004}",
            "{\"sensor_id\":\"S07\",\"temperature\":29.0,\"humidity\":35,\"pressure\":1003}",
            "{\"sensor_id\":\"S08\",\"temperature\":30.2,\"humidity\":32,\"pressure\":1001}",
            "{\"sensor_id\":\"S09\",\"temperature\":31.5,\"humidity\":30,\"pressure\":999}",
            "{\"sensor_id\":\"S10\",\"temperature\":32.8,\"humidity\":27,\"pressure\":997}",
            "{\"sensor_id\":\"S11\",\"temperature\":33.1,\"humidity\":25,\"pressure\":996}",
            "{\"sensor_id\":\"S12\",\"temperature\":34.4,\"humidity\":22,\"pressure\":994}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var lines = new string[]
        {
            "{\"id\":1,\"score\":50,\"constant\":100}",
            "{\"id\":2,\"score\":60,\"constant\":100}",
            "{\"id\":3,\"score\":55,\"constant\":100}",
            "{\"id\":4,\"score\":70,\"constant\":100}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldCorrelation
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCorrelation_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetFieldCorrelation("temperature", "humidity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCorrelation_In_Range()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var corr = doc.GetFieldCorrelation("temperature", "humidity");
        Assert.True(corr >= -1.0 && corr <= 1.0);
    }

    [Fact]
    public void GetFieldCorrelation_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.Equal(
            doc.GetFieldCorrelation("temperature", "humidity"),
            doc.GetFieldCorrelation("temperature", "humidity"));
    }

    [Fact]
    public void GetFieldCorrelation_Self_Equals_One()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.Equal(1.0, doc.GetFieldCorrelation("temperature", "temperature"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldCovariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCovariance_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetFieldCovariance("temperature", "pressure"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCovariance_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var cov = doc.GetFieldCovariance("temperature", "pressure");
        Assert.True(double.IsFinite(cov));
    }

    [Fact]
    public void GetFieldCovariance_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.Equal(
            doc.GetFieldCovariance("temperature", "humidity"),
            doc.GetFieldCovariance("temperature", "humidity"));
    }

    [Fact]
    public void GetFieldCovariance_Zero_For_Constant_Field()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        var cov = doc.GetFieldCovariance("score", "constant");
        Assert.Equal(0.0, cov, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldPearsonR
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldPearsonR_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var ex = Record.Exception(() => doc.GetFieldPearsonR("temperature", "humidity"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldPearsonR_In_Range()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var r = doc.GetFieldPearsonR("temperature", "humidity");
        Assert.True(r >= -1.0 && r <= 1.0);
    }

    [Fact]
    public void GetFieldPearsonR_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        Assert.Equal(
            doc.GetFieldPearsonR("temperature", "pressure"),
            doc.GetFieldPearsonR("temperature", "pressure"));
    }

    [Fact]
    public void GetFieldPearsonR_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSensorNdjson());
        var before = doc.GetFieldPearsonR("temperature", "humidity");
        var path = TempFile("pr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldPearsonR("temperature", "humidity"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldCorrelation_GetFieldCovariance_GetFieldPearsonR_Pipeline()
    {
        // UK biobank-style health data — BMI, blood pressure, cholesterol, lifestyle factors
        var path = TempFile("biobank.ndjson");
        var lines = new System.Collections.Generic.List<string>();
        var rng = new Random(20240301);
        for (int i = 0; i < 150; i++)
        {
            // BMI correlated with systolic BP (positive) and fitness score (negative)
            double bmi = 18.5 + rng.NextDouble() * 22.0; // 18.5–40.5
            double sbp = 100 + (bmi - 18.5) * 2.2 + rng.NextDouble() * 15; // correlated with BMI
            double fitness = 100 - (bmi - 18.5) * 2.5 + rng.NextDouble() * 20; // negatively correlated
            double chol = 3.5 + rng.NextDouble() * 3.5;
            int smoker = rng.NextDouble() < 0.25 ? 1 : 0;
            lines.Add($"{{\"participant_id\":\"UK{i:D5}\",\"bmi\":{bmi:F1},\"systolic_bp\":{sbp:F0},\"fitness_score\":{fitness:F0},\"cholesterol\":{chol:F2},\"smoker\":{smoker}}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150, doc.RecordCount);

        // GetFieldCorrelation — BMI vs BP (expect positive)
        var bmiSbpCorr = doc.GetFieldCorrelation("bmi", "systolic_bp");
        Assert.True(bmiSbpCorr >= -1.0 && bmiSbpCorr <= 1.0);
        Assert.Equal(bmiSbpCorr, doc.GetFieldCorrelation("bmi", "systolic_bp")); // consistent

        // Self-correlation
        Assert.Equal(1.0, doc.GetFieldCorrelation("bmi", "bmi"), precision: 6);

        // GetFieldCorrelation — BMI vs fitness (expect negative)
        var bmiFitCorr = doc.GetFieldCorrelation("bmi", "fitness_score");
        Assert.True(bmiFitCorr >= -1.0 && bmiFitCorr <= 1.0);

        // GetFieldCovariance — BMI vs BP
        var bmiSbpCov = doc.GetFieldCovariance("bmi", "systolic_bp");
        Assert.True(double.IsFinite(bmiSbpCov));
        Assert.Equal(bmiSbpCov, doc.GetFieldCovariance("bmi", "systolic_bp")); // consistent

        // GetFieldCovariance — BP vs fitness
        var sbpFitCov = doc.GetFieldCovariance("systolic_bp", "fitness_score");
        Assert.True(double.IsFinite(sbpFitCov));

        // GetFieldPearsonR — BMI vs systolic_bp
        var pearsonR = doc.GetFieldPearsonR("bmi", "systolic_bp");
        Assert.True(pearsonR >= -1.0 && pearsonR <= 1.0);
        Assert.Equal(pearsonR, doc.GetFieldPearsonR("bmi", "systolic_bp")); // consistent

        // GetFieldPearsonR — cholesterol vs smoker
        var cholSmkR = doc.GetFieldPearsonR("cholesterol", "smoker");
        Assert.True(cholSmkR >= -1.0 && cholSmkR <= 1.0);

        // All pairs should return finite values
        var fields = new[] { "bmi", "systolic_bp", "fitness_score", "cholesterol" };
        foreach (var f1 in fields)
            foreach (var f2 in fields)
            {
                Assert.True(double.IsFinite(doc.GetFieldCorrelation(f1, f2)));
                Assert.True(double.IsFinite(doc.GetFieldCovariance(f1, f2)));
                Assert.True(double.IsFinite(doc.GetFieldPearsonR(f1, f2)));
            }

        // SaveToFile
        var outPath = TempFile("biobank_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(bmiSbpCorr, loaded.GetFieldCorrelation("bmi", "systolic_bp"), precision: 6);
        Assert.Equal(bmiSbpCov, loaded.GetFieldCovariance("bmi", "systolic_bp"), precision: 6);
        Assert.Equal(pearsonR, loaded.GetFieldPearsonR("bmi", "systolic_bp"), precision: 6);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // Additional stats
        var meanBmi = doc.GetFieldMean("bmi");
        Assert.True(meanBmi > 18.0 && meanBmi < 42.0);
        var stdBmi = doc.GetFieldStdDev("bmi");
        Assert.True(stdBmi >= 0);
    }
}
