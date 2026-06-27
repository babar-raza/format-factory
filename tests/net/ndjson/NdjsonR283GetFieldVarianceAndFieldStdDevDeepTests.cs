// Tests for NdjsonDocument.GetFieldVariance, GetFieldStdDev deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R283

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R283: Tests for NdjsonDocument.GetFieldVariance, GetFieldStdDev deeper.
/// GetFieldVariance(field): returns the sample variance of numeric values in the named field.
/// GetFieldStdDev(field): returns the sample standard deviation; equals sqrt(variance).
/// Covers: GetFieldVariance no-throw; GetFieldVariance non-negative; GetFieldVariance zero for uniform;
/// GetFieldVariance consistent; GetFieldVariance save-load;
/// GetFieldStdDev no-throw; GetFieldStdDev non-negative; GetFieldStdDev zero for uniform;
/// GetFieldStdDev consistent; GetFieldStdDev save-load;
/// GetFieldVariance equals GetFieldStdDev squared; dogfood pipeline.
/// </summary>
public class NdjsonR283GetFieldVarianceAndFieldStdDevDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR283GetFieldVarianceAndFieldStdDevDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR283_" + Guid.NewGuid().ToString("N"));
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
        var lines = new StringBuilder();
        for (int i = 0; i < 10; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":{i * 10.0}}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":50.0}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldVariance
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldVariance_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldVariance("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldVariance_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldVariance("value") >= 0.0);
    }

    [Fact]
    public void GetFieldVariance_Zero_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(0.0, doc.GetFieldVariance("score"), precision: 6);
    }

    [Fact]
    public void GetFieldVariance_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldVariance("value"), doc.GetFieldVariance("value"));
    }

    [Fact]
    public void GetFieldVariance_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldVariance("value");
        var path = TempFile("var_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldVariance("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldStdDev
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldStdDev_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldStdDev("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldStdDev_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldStdDev("value") >= 0.0);
    }

    [Fact]
    public void GetFieldStdDev_Zero_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(0.0, doc.GetFieldStdDev("score"), precision: 6);
    }

    [Fact]
    public void GetFieldStdDev_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldStdDev("value"), doc.GetFieldStdDev("value"));
    }

    [Fact]
    public void GetFieldStdDev_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldStdDev("value");
        var path = TempFile("sd_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldStdDev("value"), precision: 6);
    }

    [Fact]
    public void GetFieldVariance_Equals_StdDev_Squared()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sd = doc.GetFieldStdDev("value");
        var var_ = doc.GetFieldVariance("value");
        Assert.Equal(sd * sd, var_, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldVariance_GetFieldStdDev_Pipeline()
    {
        // Climate — CEDA / Met Office Hadley Centre: UK Climate Projections (UKCP18) Ensemble Data
        // Regional temperature and precipitation variance from probabilistic climate model ensemble
        // Variance/StdDev quantify uncertainty spread across the climate ensemble members

        var path = TempFile("ukcp18_regional_ensemble_2070s.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241101);

        string[] regions = {
            "North_Scotland", "South_Scotland", "North_East_England", "North_West_England",
            "Yorkshire_Humber", "East_Midlands", "West_Midlands", "East_England",
            "London_South_East", "South_West_England", "Wales"
        };
        string[] seasons = { "DJF", "MAM", "JJA", "SON" };

        for (int r = 0; r < regions.Length; r++)
        {
            for (int s = 0; s < seasons.Length; s++)
            {
                // Temperature change (°C from 1981-2000 baseline) across 12 ensemble members
                // Central estimate higher for southern regions in summer
                double baseline_temp = 0.8 + rng.NextDouble() * 2.5 + (r >= 8 ? 0.8 : 0);
                double baseline_precip = -5 + rng.NextDouble() * 20;

                // Ensemble spread
                double temp_mean = baseline_temp;
                double temp_std = 0.5 + rng.NextDouble() * 1.5;
                double precip_mean = baseline_precip;
                double precip_std = 5 + rng.NextDouble() * 15;
                double temp_p10 = temp_mean - 1.28 * temp_std;
                double temp_p90 = temp_mean + 1.28 * temp_std;
                double precip_p10 = precip_mean - 1.28 * precip_std;
                double precip_p90 = precip_mean + 1.28 * precip_std;

                sb.AppendLine($"{{" +
                              $"\"region\":\"{regions[r]}\"," +
                              $"\"season\":\"{seasons[s]}\"," +
                              $"\"temp_change_mean_degc\":{temp_mean:F2}," +
                              $"\"temp_change_std_degc\":{temp_std:F2}," +
                              $"\"temp_change_p10_degc\":{temp_p10:F2}," +
                              $"\"temp_change_p90_degc\":{temp_p90:F2}," +
                              $"\"precip_change_mean_pct\":{precip_mean:F1}," +
                              $"\"precip_change_std_pct\":{precip_std:F1}," +
                              $"\"precip_change_p10_pct\":{precip_p10:F1}," +
                              $"\"precip_change_p90_pct\":{precip_p90:F1}," +
                              $"\"ensemble_size\":12" +
                              $"}}");
            }
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(regions.Length * seasons.Length, doc.RecordCount);

        // Temperature mean ensemble spread variance
        var tempStdVar = doc.GetFieldVariance("temp_change_std_degc");
        var tempStdSd = doc.GetFieldStdDev("temp_change_std_degc");
        Assert.True(tempStdVar >= 0.0);
        Assert.True(tempStdSd >= 0.0);
        Assert.Equal(tempStdSd * tempStdSd, tempStdVar, precision: 4);
        Assert.Equal(tempStdVar, doc.GetFieldVariance("temp_change_std_degc")); // consistent
        Assert.Equal(tempStdSd, doc.GetFieldStdDev("temp_change_std_degc")); // consistent

        // Temperature mean change variance
        var tempMeanVar = doc.GetFieldVariance("temp_change_mean_degc");
        var tempMeanSd = doc.GetFieldStdDev("temp_change_mean_degc");
        Assert.True(tempMeanVar >= 0.0);
        Assert.True(tempMeanSd >= 0.0);
        Assert.Equal(tempMeanSd * tempMeanSd, tempMeanVar, precision: 4);

        // Precipitation change variance
        var precipVar = doc.GetFieldVariance("precip_change_std_pct");
        var precipSd = doc.GetFieldStdDev("precip_change_std_pct");
        Assert.True(precipVar >= 0.0);
        Assert.True(precipSd >= 0.0);
        Assert.Equal(precipSd * precipSd, precipVar, precision: 2);

        // Zero variance for uniform field (ensemble_size is always 12)
        var ensVar = doc.GetFieldVariance("ensemble_size");
        var ensSd = doc.GetFieldStdDev("ensemble_size");
        Assert.Equal(0.0, ensVar, precision: 6);
        Assert.Equal(0.0, ensSd, precision: 6);

        // SaveToFile
        var outPath = TempFile("ukcp18_ensemble_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(tempStdVar, loaded.GetFieldVariance("temp_change_std_degc"), precision: 6);
        Assert.Equal(tempStdSd, loaded.GetFieldStdDev("temp_change_std_degc"), precision: 6);
        Assert.Equal(tempMeanVar, loaded.GetFieldVariance("temp_change_mean_degc"), precision: 6);
        Assert.Equal(precipSd, loaded.GetFieldStdDev("precip_change_std_pct"), precision: 6);
        Assert.Equal(0.0, loaded.GetFieldVariance("ensemble_size"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldVariance("temp_change_std_degc"));
        var ex2 = Record.Exception(() => loaded.GetFieldStdDev("precip_change_mean_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
