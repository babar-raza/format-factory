// Tests for NdjsonDocument.GetFieldFirstQuartile, GetFieldThirdQuartile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R284

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R284: Tests for NdjsonDocument.GetFieldFirstQuartile, GetFieldThirdQuartile deeper.
/// GetFieldFirstQuartile(field): returns the 25th percentile of numeric values in the named field.
/// GetFieldThirdQuartile(field): returns the 75th percentile; always ≥ GetFieldFirstQuartile.
/// Covers: GetFieldFirstQuartile no-throw; GetFieldFirstQuartile in-range;
/// GetFieldFirstQuartile equal to mean for uniform; GetFieldFirstQuartile consistent;
/// GetFieldFirstQuartile save-load;
/// GetFieldThirdQuartile no-throw; GetFieldThirdQuartile in-range;
/// GetFieldThirdQuartile geq GetFieldFirstQuartile;
/// GetFieldThirdQuartile consistent; GetFieldThirdQuartile save-load; dogfood pipeline.
/// </summary>
public class NdjsonR284GetFieldFirstQuartileAndThirdQuartileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR284GetFieldFirstQuartileAndThirdQuartileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR284_" + Guid.NewGuid().ToString("N"));
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
        // values 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 → Q1~27.5, Q3~72.5
        for (int i = 1; i <= 10; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":{i * 10.0}}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 20; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":42.0}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldFirstQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldFirstQuartile_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldFirstQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldFirstQuartile_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var q1 = doc.GetFieldFirstQuartile("value");
        Assert.True(q1 >= doc.GetFieldMin("value") && q1 <= doc.GetFieldMax("value"));
    }

    [Fact]
    public void GetFieldFirstQuartile_Equal_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(42.0, doc.GetFieldFirstQuartile("score"), precision: 6);
    }

    [Fact]
    public void GetFieldFirstQuartile_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldFirstQuartile("value"), doc.GetFieldFirstQuartile("value"));
    }

    [Fact]
    public void GetFieldFirstQuartile_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldFirstQuartile("value");
        var path = TempFile("q1_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldFirstQuartile("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldThirdQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldThirdQuartile_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldThirdQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldThirdQuartile_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var q3 = doc.GetFieldThirdQuartile("value");
        Assert.True(q3 >= doc.GetFieldMin("value") && q3 <= doc.GetFieldMax("value"));
    }

    [Fact]
    public void GetFieldThirdQuartile_Geq_FirstQuartile()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldThirdQuartile("value") >= doc.GetFieldFirstQuartile("value"));
    }

    [Fact]
    public void GetFieldThirdQuartile_Equal_ForUniform()
    {
        var doc = NdjsonDocument.LoadFile(CreateUniformNdjson());
        Assert.Equal(42.0, doc.GetFieldThirdQuartile("score"), precision: 6);
    }

    [Fact]
    public void GetFieldThirdQuartile_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldThirdQuartile("value"), doc.GetFieldThirdQuartile("value"));
    }

    [Fact]
    public void GetFieldThirdQuartile_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldThirdQuartile("value");
        var path = TempFile("q3_save.ndjson");
        doc.SaveToFile(path);
        Assert.Equal(before, NdjsonDocument.LoadFile(path).GetFieldThirdQuartile("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldFirstQuartile_GetFieldThirdQuartile_Pipeline()
    {
        // Education — DfE / Ofsted: School Performance and Inspection Outcomes 2023/24
        // School-level attainment and progress data with quartile analysis for floor standard checks
        // Q1 identifies schools in the bottom quartile needing support; Q3 identifies outstanding performers

        var path = TempFile("dfe_school_performance_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20240901);

        string[] phases = { "Primary", "Secondary", "All_Through", "Special" };
        string[] localAuthorities = {
            "Barking_and_Dagenham", "Birmingham", "Bristol", "Cornwall", "Coventry",
            "Devon", "Hackney", "Hampshire", "Leeds", "Leicester",
            "Liverpool", "Manchester", "Newcastle", "Newham", "Nottingham",
            "Oldham", "Rochdale", "Salford", "Sheffield", "Southwark",
            "Tower_Hamlets", "Trafford", "Wakefield", "Wigan", "Wolverhampton"
        };
        string[] ofstedGrades = { "Outstanding", "Good", "Good", "Requires_Improvement", "Inadequate" };

        for (int i = 0; i < 400; i++)
        {
            string phase = phases[rng.Next(phases.Length)];
            string la = localAuthorities[rng.Next(localAuthorities.Length)];
            string grade = ofstedGrades[rng.Next(ofstedGrades.Length)];

            // KS2/KS4 attainment (higher = better)
            double attainment8 = phase == "Secondary" ? 35 + rng.NextDouble() * 35 : 0;
            double progress8 = phase == "Secondary" ? -3 + rng.NextDouble() * 6 : 0;
            double ks2ReadingPct = phase == "Primary" ? 50 + rng.NextDouble() * 40 : 0;
            double ks2MathsPct = phase == "Primary" ? 48 + rng.NextDouble() * 42 : 0;
            double pupilPremiumGapMonths = -3 + rng.NextDouble() * 10; // negative = disadvantaged ahead
            double absenceRatePct = 3 + rng.NextDouble() * 12;
            double persistentAbsencePct = 8 + rng.NextDouble() * 25;
            int rollSize = 100 + rng.Next(1800);
            double fsm6Pct = 5 + rng.NextDouble() * 50; // free school meals
            double senPct = 8 + rng.NextDouble() * 25; // special educational needs

            sb.AppendLine($"{{" +
                          $"\"urn\":{100000 + i}," +
                          $"\"phase\":\"{phase}\"," +
                          $"\"local_authority\":\"{la}\"," +
                          $"\"ofsted_grade\":\"{grade}\"," +
                          $"\"attainment8_score\":{attainment8:F1}," +
                          $"\"progress8_score\":{progress8:F2}," +
                          $"\"ks2_reading_pct\":{ks2ReadingPct:F1}," +
                          $"\"ks2_maths_pct\":{ks2MathsPct:F1}," +
                          $"\"disadvantage_gap_months\":{pupilPremiumGapMonths:F1}," +
                          $"\"absence_rate_pct\":{absenceRatePct:F1}," +
                          $"\"persistent_absence_pct\":{persistentAbsencePct:F1}," +
                          $"\"roll_size\":{rollSize}," +
                          $"\"fsm6_pct\":{fsm6Pct:F1}," +
                          $"\"sen_pct\":{senPct:F1}" +
                          $"}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(400, doc.RecordCount);

        // Absence rate quartiles (all schools)
        var absQ1 = doc.GetFieldFirstQuartile("absence_rate_pct");
        var absQ3 = doc.GetFieldThirdQuartile("absence_rate_pct");
        Assert.True(absQ1 >= doc.GetFieldMin("absence_rate_pct"));
        Assert.True(absQ3 <= doc.GetFieldMax("absence_rate_pct"));
        Assert.True(absQ1 <= absQ3);
        Assert.Equal(absQ1, doc.GetFieldFirstQuartile("absence_rate_pct")); // consistent
        Assert.Equal(absQ3, doc.GetFieldThirdQuartile("absence_rate_pct")); // consistent

        // Persistent absence quartiles
        var persQ1 = doc.GetFieldFirstQuartile("persistent_absence_pct");
        var persQ3 = doc.GetFieldThirdQuartile("persistent_absence_pct");
        Assert.True(persQ1 <= persQ3);
        Assert.True(persQ1 >= 0.0);

        // FSM percentage quartiles
        var fsmQ1 = doc.GetFieldFirstQuartile("fsm6_pct");
        var fsmQ3 = doc.GetFieldThirdQuartile("fsm6_pct");
        Assert.True(fsmQ1 <= fsmQ3);
        Assert.True(fsmQ1 >= 0.0);
        Assert.True(fsmQ3 <= 100.0);

        // Roll size quartiles
        var rollQ1 = doc.GetFieldFirstQuartile("roll_size");
        var rollQ3 = doc.GetFieldThirdQuartile("roll_size");
        Assert.True(rollQ1 <= rollQ3);
        Assert.True(rollQ1 >= 0.0);

        // Interquartile range (IQR) is non-negative
        double absIqr = absQ3 - absQ1;
        double persIqr = persQ3 - persQ1;
        Assert.True(absIqr >= 0.0);
        Assert.True(persIqr >= 0.0);

        // Uniform field (all same disadvantage gap doesn't hold — check Q1<=Q3)
        Assert.True(doc.GetFieldFirstQuartile("sen_pct") <= doc.GetFieldThirdQuartile("sen_pct"));

        // SaveToFile
        var outPath = TempFile("dfe_school_performance_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(absQ1, loaded.GetFieldFirstQuartile("absence_rate_pct"), precision: 6);
        Assert.Equal(absQ3, loaded.GetFieldThirdQuartile("absence_rate_pct"), precision: 6);
        Assert.Equal(persQ1, loaded.GetFieldFirstQuartile("persistent_absence_pct"), precision: 6);
        Assert.Equal(fsmQ3, loaded.GetFieldThirdQuartile("fsm6_pct"), precision: 6);
        Assert.Equal(rollQ1, loaded.GetFieldFirstQuartile("roll_size"), precision: 6);

        var ex1 = Record.Exception(() => loaded.GetFieldFirstQuartile("absence_rate_pct"));
        var ex2 = Record.Exception(() => loaded.GetFieldThirdQuartile("persistent_absence_pct"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
