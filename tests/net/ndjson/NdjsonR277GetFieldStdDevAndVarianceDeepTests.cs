// Tests for NdjsonDocument.GetFieldStdDev, GetFieldVariance deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R277

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R277: Tests for NdjsonDocument.GetFieldStdDev, GetFieldVariance deeper.
/// GetFieldStdDev(field): returns the sample standard deviation of numeric values in the field.
/// GetFieldVariance(field): returns the sample variance of numeric values in the field.
/// Covers: GetFieldStdDev no-throw; GetFieldStdDev non-negative; GetFieldStdDev zero for uniform;
/// GetFieldStdDev consistent; GetFieldStdDev save-load;
/// GetFieldVariance no-throw; GetFieldVariance non-negative; GetFieldVariance zero for uniform;
/// GetFieldVariance consistent; GetFieldVariance save-load;
/// GetFieldVariance equals GetFieldStdDev squared; dogfood pipeline.
/// </summary>
public class NdjsonR277GetFieldStdDevAndVarianceDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR277GetFieldStdDevAndVarianceDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR277_" + Guid.NewGuid().ToString("N"));
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
            lines.AppendLine($"{{\"id\":{i},\"score\":99.5}}");
        File.WriteAllText(path, lines.ToString());
        return path;
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
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldStdDev("value"), precision: 6);
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
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldVariance("value"), precision: 6);
    }

    [Fact]
    public void GetFieldVariance_Equals_StdDev_Squared()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sd = doc.GetFieldStdDev("value");
        var variance = doc.GetFieldVariance("value");
        Assert.Equal(sd * sd, variance, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldStdDev_GetFieldVariance_Pipeline()
    {
        // Education — Ofsted / DfE: GCSE Attainment 8 School Performance Data 2024
        // School-level GCSE attainment scores for league table and intervention analysis
        // StdDev/Variance quantify attainment spread within and across schools

        var path = TempFile("dfe_gcse_attainment8_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240815);

        string[] localAuthorities = { "Camden", "Islington", "Hackney", "Tower_Hamlets", "Newham",
                                       "Southwark", "Lewisham", "Lambeth", "Manchester", "Birmingham",
                                       "Leeds", "Sheffield", "Bristol", "Nottingham", "Liverpool" };
        string[] schoolTypes = { "Academy", "Academy", "Academy", "Community", "Community",
                                  "Free_School", "Voluntary_Aided", "Converter_Academy", "Foundation" };
        string[] ofstedRatings = { "Outstanding", "Good", "Good", "Good", "Requires_Improvement", "Inadequate" };

        for (int i = 0; i < 280; i++)
        {
            string urn = $"URN{100000 + i}";
            string la = localAuthorities[i % localAuthorities.Length];
            string schoolType = schoolTypes[rng.Next(schoolTypes.Length)];
            string ofsted = ofstedRatings[rng.Next(ofstedRatings.Length)];
            // Attainment 8 scores: national average ~46, range ~20-65, high-performing ~58+
            double att8 = 36 + rng.NextDouble() * 28;
            double progress8 = -1.5 + rng.NextDouble() * 3.0;
            int pupilCount = 50 + rng.Next(1000);
            double ebacc = 0.1 + rng.NextDouble() * 0.7;
            double absence_rate = 0.03 + rng.NextDouble() * 0.12;

            sb.AppendLine($"{{\"urn\":\"{urn}\",\"local_authority\":\"{la}\"," +
                          $"\"school_type\":\"{schoolType}\",\"ofsted_rating\":\"{ofsted}\"," +
                          $"\"attainment8\":{att8:F1}," +
                          $"\"progress8\":{progress8:F2}," +
                          $"\"pupil_count\":{pupilCount}," +
                          $"\"ebacc_entries\":{ebacc:F3}," +
                          $"\"absence_rate\":{absence_rate:F4}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(280, doc.RecordCount);

        // Attainment 8 std dev and variance
        var att8Sd = doc.GetFieldStdDev("attainment8");
        var att8Var = doc.GetFieldVariance("attainment8");
        Assert.True(att8Sd >= 0.0);
        Assert.True(att8Var >= 0.0);
        Assert.True(att8Sd > 0.0); // schools vary in attainment
        Assert.True(att8Var > 0.0);
        Assert.Equal(att8Sd * att8Sd, att8Var, precision: 3); // variance = sd²
        Assert.Equal(att8Sd, doc.GetFieldStdDev("attainment8")); // consistent
        Assert.Equal(att8Var, doc.GetFieldVariance("attainment8")); // consistent

        // Progress 8
        var p8Sd = doc.GetFieldStdDev("progress8");
        var p8Var = doc.GetFieldVariance("progress8");
        Assert.True(p8Sd >= 0.0);
        Assert.True(p8Var >= 0.0);
        Assert.Equal(p8Sd * p8Sd, p8Var, precision: 3);

        // EBacc entries
        var ebaccSd = doc.GetFieldStdDev("ebacc_entries");
        Assert.True(ebaccSd >= 0.0);
        Assert.Equal(ebaccSd * ebaccSd, doc.GetFieldVariance("ebacc_entries"), precision: 3);

        // Pupil count variance
        var pupilVar = doc.GetFieldVariance("pupil_count");
        Assert.True(pupilVar >= 0.0);
        Assert.Equal(Math.Sqrt(pupilVar), doc.GetFieldStdDev("pupil_count"), precision: 3);

        // Absence rate (small variance expected)
        var absenceSd = doc.GetFieldStdDev("absence_rate");
        Assert.True(absenceSd >= 0.0);

        // SaveToFile
        var outPath = TempFile("dfe_gcse_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(att8Sd, loaded.GetFieldStdDev("attainment8"), precision: 6);
        Assert.Equal(att8Var, loaded.GetFieldVariance("attainment8"), precision: 6);
        Assert.Equal(p8Sd, loaded.GetFieldStdDev("progress8"), precision: 6);
        Assert.Equal(p8Var, loaded.GetFieldVariance("progress8"), precision: 6);
        Assert.Equal(ebaccSd, loaded.GetFieldStdDev("ebacc_entries"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldStdDev("attainment8"));
        var ex2 = Record.Exception(() => loaded.GetFieldVariance("absence_rate"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
