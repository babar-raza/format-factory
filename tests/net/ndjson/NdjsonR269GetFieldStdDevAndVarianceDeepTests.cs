// Tests for NdjsonDocument.GetFieldStdDev, GetFieldVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R269

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R269: Tests for NdjsonDocument.GetFieldStdDev, GetFieldVariance deeper.
/// GetFieldStdDev(fieldName): returns the population standard deviation of numeric field values.
/// GetFieldVariance(fieldName): returns the population variance of numeric field values.
/// Covers: GetFieldStdDev no-throw; GetFieldStdDev non-negative; GetFieldStdDev consistent;
/// GetFieldStdDev zero for constant; GetFieldStdDev save-load;
/// GetFieldVariance no-throw; GetFieldVariance non-negative;
/// GetFieldVariance zero for constant; GetFieldVariance consistent;
/// GetFieldVariance equals StdDev squared; GetFieldStdDev save-load;
/// dogfood CreateDoc→GetFieldStdDev→GetFieldVariance pipeline.
/// </summary>
public class NdjsonR269GetFieldStdDevAndVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR269GetFieldStdDevAndVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR269_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240815);
        for (int i = 0; i < 100; i++)
        {
            int age = 18 + rng.Next(62);
            double salary = Math.Round(20000 + rng.NextDouble() * 80000, 2);
            int score = rng.Next(100);
            sb.AppendLine($"{{\"id\":{i},\"age\":{age},\"salary\":{salary},\"score\":{score}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateConstantNdjson()
    {
        var path = TempFile("constant.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":42}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldStdDev_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldStdDev("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldStdDev_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldStdDev("salary") >= 0.0);
    }

    [Fact]
    public void GetFieldStdDev_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldStdDev("age"), doc.GetFieldStdDev("age"));
    }

    [Fact]
    public void GetFieldStdDev_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetFieldStdDev_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldStdDev("salary");
        var path = TempFile("sd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldStdDev("salary"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldVariance_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldVariance("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldVariance_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldVariance("salary") >= 0.0);
    }

    [Fact]
    public void GetFieldVariance_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantNdjson());
        Assert.Equal(0.0, doc.GetFieldVariance("value"), precision: 6);
    }

    [Fact]
    public void GetFieldVariance_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldVariance("score"), doc.GetFieldVariance("score"));
    }

    [Fact]
    public void GetFieldVariance_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldVariance("age");
        var path = TempFile("var_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldVariance("age"), precision: 6);
    }

    [Fact]
    public void GetFieldVariance_Equals_StdDev_Squared()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sd = doc.GetFieldStdDev("salary");
        var variance = doc.GetFieldVariance("salary");
        Assert.Equal(sd * sd, variance, precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldStdDev_GetFieldVariance_Pipeline()
    {
        // Financial services — Bank of England Stress Testing: DFAST-equivalent
        // Internal Capital Adequacy Assessment Process (ICAAP) scenario data
        // StdDev/Variance analysis of capital ratios and stress losses across scenarios
        var path = TempFile("boe_stress_test.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] scenarios = { "Base", "Adverse", "Severely Adverse", "Exploratory" };
        string[] banks = { "HSBC", "Barclays", "Lloyds", "NatWest", "Standard Chartered",
                           "Santander UK", "TSB", "Metro Bank", "Handelsbanken", "Nationwide" };

        for (int i = 0; i < 200; i++)
        {
            string bank = banks[i % banks.Length];
            string scenario = scenarios[rng.Next(scenarios.Length)];
            double cet1Ratio = Math.Round(8.0 + rng.NextDouble() * 8.0, 2);
            double leverageRatio = Math.Round(3.5 + rng.NextDouble() * 3.5, 2);
            double stressLossBn = Math.Round(0.5 + rng.NextDouble() * 15.0, 2);
            double rwaDensityPct = Math.Round(25.0 + rng.NextDouble() * 40.0, 2);
            double nplRatioPct = Math.Round(0.5 + rng.NextDouble() * 6.0, 2);
            bool passed = cet1Ratio >= 10.0;
            sb.AppendLine($"{{\"record_id\":{i},\"bank\":\"{bank}\",\"scenario\":\"{scenario}\"," +
                          $"\"cet1_ratio\":{cet1Ratio},\"leverage_ratio\":{leverageRatio}," +
                          $"\"stress_loss_bn\":{stressLossBn},\"rwa_density_pct\":{rwaDensityPct}," +
                          $"\"npl_ratio_pct\":{nplRatioPct},\"passed\":{passed.ToString().ToLower()}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(200, doc.RecordCount);

        // GetFieldStdDev — CET1 ratio
        var sdCet1 = doc.GetFieldStdDev("cet1_ratio");
        Assert.True(sdCet1 >= 0);
        Assert.Equal(sdCet1, doc.GetFieldStdDev("cet1_ratio")); // consistent

        // GetFieldVariance — CET1 ratio
        var varCet1 = doc.GetFieldVariance("cet1_ratio");
        Assert.True(varCet1 >= 0);
        Assert.Equal(varCet1, doc.GetFieldVariance("cet1_ratio")); // consistent
        Assert.Equal(sdCet1 * sdCet1, varCet1, precision: 2);

        // Leverage ratio: narrower range → smaller variance than stress loss
        var sdLev = doc.GetFieldStdDev("leverage_ratio");
        var varLev = doc.GetFieldVariance("leverage_ratio");
        Assert.True(sdLev >= 0);
        Assert.True(varLev >= 0);
        Assert.Equal(sdLev * sdLev, varLev, precision: 2);

        // Stress loss: wide range 0.5-15.5bn → should have meaningful variance
        var sdLoss = doc.GetFieldStdDev("stress_loss_bn");
        var varLoss = doc.GetFieldVariance("stress_loss_bn");
        Assert.True(sdLoss >= 0);
        Assert.True(varLoss >= 0);
        Assert.Equal(sdLoss * sdLoss, varLoss, precision: 2);

        // RWA density: moderate spread
        var sdRwa = doc.GetFieldStdDev("rwa_density_pct");
        Assert.True(sdRwa >= 0);
        Assert.True(doc.GetFieldVariance("rwa_density_pct") >= 0);

        // NPL ratio
        var sdNpl = doc.GetFieldStdDev("npl_ratio_pct");
        Assert.True(sdNpl >= 0);
        Assert.Equal(sdNpl * sdNpl, doc.GetFieldVariance("npl_ratio_pct"), precision: 2);

        // Basic field stats
        Assert.True(doc.GetFieldMean("cet1_ratio") > 0);
        Assert.True(doc.GetFieldSum("stress_loss_bn") > 0);

        // SaveToFile
        var outPath = TempFile("boe_stress_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(sdCet1, loaded.GetFieldStdDev("cet1_ratio"), precision: 6);
        Assert.Equal(varCet1, loaded.GetFieldVariance("cet1_ratio"), precision: 4);

        // Constant variance sub-test
        var path2 = TempFile("constant_capital.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 50; i++)
            sb2.AppendLine($"{{\"id\":{i},\"cet1_ratio\":12.5}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(0.0, doc2.GetFieldStdDev("cet1_ratio"), precision: 6);
        Assert.Equal(0.0, doc2.GetFieldVariance("cet1_ratio"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldStdDev("leverage_ratio"));
        var ex2 = Record.Exception(() => loaded.GetFieldVariance("leverage_ratio"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
