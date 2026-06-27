// Tests for NdjsonDocument.GetFieldNullPattern, GetFieldMissingRate, GetFieldPresentRate deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R256

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R256: Tests for NdjsonDocument.GetFieldNullPattern, GetFieldMissingRate, GetFieldPresentRate deeper.
/// GetFieldNullPattern(fieldName): returns the count of null/missing values for the field.
/// GetFieldMissingRate(fieldName): returns fraction of records where the field is null or absent.
/// GetFieldPresentRate(fieldName): returns fraction of records where the field has a non-null value.
/// Covers: GetFieldNullPattern no-throw; GetFieldNullPattern non-negative; GetFieldNullPattern consistent;
/// GetFieldNullPattern zero for fully-present field;
/// GetFieldMissingRate no-throw; GetFieldMissingRate in [0,1]; GetFieldMissingRate consistent;
/// GetFieldMissingRate zero for fully-present;
/// GetFieldPresentRate no-throw; GetFieldPresentRate in [0,1]; GetFieldPresentRate + MissingRate = 1;
/// GetFieldPresentRate save-load;
/// dogfood CreateDoc→GetFieldNullPattern→GetFieldMissingRate→GetFieldPresentRate pipeline.
/// </summary>
public class NdjsonR256GetFieldNullPatternAndMissingValueAnalysisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR256GetFieldNullPatternAndMissingValueAnalysisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR256_" + Guid.NewGuid().ToString("N"));
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
        var rng = new Random(55);
        for (int i = 0; i < 60; i++)
        {
            bool hasMeasure = rng.Next(5) != 0; // 80% present
            bool hasNote = rng.Next(3) == 0;    // 33% present
            if (hasMeasure)
                sb.AppendLine($"{{\"id\":{i},\"name\":\"item_{i}\",\"measure\":{rng.NextDouble() * 100.0:F2},\"note\":{(hasNote ? $"\"note_{i}\"" : "null")}}}");
            else
                sb.AppendLine($"{{\"id\":{i},\"name\":\"item_{i}\",\"note\":{(hasNote ? $"\"note_{i}\"" : "null")}}}");
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateFullyPresentNdjson()
    {
        var path = TempFile("full.ndjson");
        var sb = new StringBuilder();
        for (int i = 0; i < 30; i++)
            sb.AppendLine($"{{\"id\":{i},\"value\":{i * 3.14:F3},\"label\":\"L{i}\"}}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldNullPattern
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldNullPattern_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldNullPattern("measure"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldNullPattern_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldNullPattern("measure") >= 0);
    }

    [Fact]
    public void GetFieldNullPattern_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldNullPattern("note"), doc.GetFieldNullPattern("note"));
    }

    [Fact]
    public void GetFieldNullPattern_Zero_ForFullyPresent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyPresentNdjson());
        Assert.Equal(0, doc.GetFieldNullPattern("value"));
    }

    // -------------------------------------------------------------------------
    // GetFieldMissingRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMissingRate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldMissingRate("measure"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMissingRate_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var rate = doc.GetFieldMissingRate("measure");
        Assert.True(rate >= 0.0 && rate <= 1.0);
    }

    [Fact]
    public void GetFieldMissingRate_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldMissingRate("note"), doc.GetFieldMissingRate("note"));
    }

    [Fact]
    public void GetFieldMissingRate_Zero_ForFullyPresent()
    {
        var doc = NdjsonDocument.LoadFile(CreateFullyPresentNdjson());
        Assert.Equal(0.0, doc.GetFieldMissingRate("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldPresentRate
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldPresentRate_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldPresentRate("measure"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldPresentRate_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var rate = doc.GetFieldPresentRate("measure");
        Assert.True(rate >= 0.0 && rate <= 1.0);
    }

    [Fact]
    public void GetFieldPresentRate_PlusMissingRate_Equals_One()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var present = doc.GetFieldPresentRate("note");
        var missing = doc.GetFieldMissingRate("note");
        Assert.Equal(1.0, present + missing, precision: 6);
    }

    [Fact]
    public void GetFieldPresentRate_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldPresentRate("measure");
        var path = TempFile("pr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldPresentRate("measure"), precision: 8);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldNullPattern_GetFieldMissingRate_GetFieldPresentRate_Pipeline()
    {
        // Electronic health records — GP patient registry extract with real-world data quality issues
        var path = TempFile("gp_patient_registry.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241001);

        int totalRecords = 150;
        int bmiMissing = 0, smokingMissing = 0, imdMissing = 0;

        for (int i = 0; i < totalRecords; i++)
        {
            var parts = new System.Collections.Generic.List<string>
            {
                $"\"patient_id\":\"NHS{100000 + i}\"",
                $"\"age\":{30 + rng.Next(60)}",
                $"\"sex\":\"{(rng.Next(2) == 0 ? "M" : "F")}\""
            };

            // BMI — 85% recorded
            if (rng.Next(100) < 85)
                parts.Add($"\"bmi\":{(18.5 + rng.NextDouble() * 22.0):F1}");
            else
            {
                parts.Add("\"bmi\":null");
                bmiMissing++;
            }

            // Smoking status — 70% recorded
            string[] smokingCats = { "Never", "Ex-smoker", "Current_<10", "Current_10-20", "Current_>20" };
            if (rng.Next(100) < 70)
                parts.Add($"\"smoking_status\":\"{smokingCats[rng.Next(smokingCats.Length)]}\"");
            else
            {
                parts.Add("\"smoking_status\":null");
                smokingMissing++;
            }

            // SBP — 95% recorded
            if (rng.Next(100) < 95)
                parts.Add($"\"sbp_mmhg\":{(100 + rng.Next(80))}");
            else
                parts.Add("\"sbp_mmhg\":null");

            // IMD decile — 60% recorded
            if (rng.Next(100) < 60)
                parts.Add($"\"imd_decile\":{(1 + rng.Next(10))}");
            else
            {
                parts.Add("\"imd_decile\":null");
                imdMissing++;
            }

            // HbA1c — 40% recorded (only relevant for diabetes patients)
            if (rng.Next(100) < 40)
                parts.Add($"\"hba1c_mmol_mol\":{(31 + rng.Next(60))}");

            sb.AppendLine("{" + string.Join(",", parts) + "}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(totalRecords, doc.RecordCount);

        // GetFieldNullPattern
        var nullBmi = doc.GetFieldNullPattern("bmi");
        Assert.True(nullBmi >= 0);
        Assert.Equal(nullBmi, doc.GetFieldNullPattern("bmi")); // consistent

        var nullSmoking = doc.GetFieldNullPattern("smoking_status");
        Assert.True(nullSmoking >= 0);

        var nullImd = doc.GetFieldNullPattern("imd_decile");
        Assert.True(nullImd >= 0);

        var nullAge = doc.GetFieldNullPattern("age");
        Assert.Equal(0, nullAge); // age always present

        // GetFieldMissingRate
        var missingBmi = doc.GetFieldMissingRate("bmi");
        Assert.True(missingBmi >= 0.0 && missingBmi <= 1.0);
        Assert.Equal(missingBmi, doc.GetFieldMissingRate("bmi")); // consistent

        var missingSmoking = doc.GetFieldMissingRate("smoking_status");
        Assert.True(missingSmoking >= 0.0 && missingSmoking <= 1.0);

        // IMD has highest missing rate (~40%)
        var missingImd = doc.GetFieldMissingRate("imd_decile");
        Assert.True(missingImd >= missingBmi); // IMD should have more missing than BMI

        var missingAge = doc.GetFieldMissingRate("age");
        Assert.Equal(0.0, missingAge, precision: 6);

        // GetFieldPresentRate
        var presentBmi = doc.GetFieldPresentRate("bmi");
        Assert.True(presentBmi >= 0.0 && presentBmi <= 1.0);
        Assert.Equal(presentBmi, doc.GetFieldPresentRate("bmi")); // consistent

        // present + missing = 1.0 for all fields
        Assert.Equal(1.0, doc.GetFieldPresentRate("bmi") + doc.GetFieldMissingRate("bmi"), precision: 6);
        Assert.Equal(1.0, doc.GetFieldPresentRate("smoking_status") + doc.GetFieldMissingRate("smoking_status"), precision: 6);
        Assert.Equal(1.0, doc.GetFieldPresentRate("imd_decile") + doc.GetFieldMissingRate("imd_decile"), precision: 6);
        Assert.Equal(1.0, doc.GetFieldPresentRate("sbp_mmhg") + doc.GetFieldMissingRate("sbp_mmhg"), precision: 6);

        // Standard field stats
        var minAge = doc.GetFieldMin("age");
        var maxAge = doc.GetFieldMax("age");
        Assert.True(minAge <= maxAge);
        Assert.True(doc.GetFieldMean("age") > 0.0);

        // Unique values
        var sexValues = doc.GetFieldUniqueValues("sex");
        Assert.NotNull(sexValues);
        Assert.True(sexValues.Count >= 1);

        // SaveToFile
        var outPath = TempFile("gp_patient_registry_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(totalRecords, loaded.RecordCount);
        Assert.Equal(nullBmi, loaded.GetFieldNullPattern("bmi"));
        Assert.Equal(missingBmi, loaded.GetFieldMissingRate("bmi"), precision: 8);
        Assert.Equal(presentBmi, loaded.GetFieldPresentRate("bmi"), precision: 8);
        Assert.Equal(1.0, loaded.GetFieldPresentRate("bmi") + loaded.GetFieldMissingRate("bmi"), precision: 6);

        // Fully-present test
        var path2 = TempFile("complete_cases.ndjson");
        var sb2 = new StringBuilder();
        for (int i = 0; i < 40; i++)
            sb2.AppendLine($"{{\"id\":{i},\"hba1c\":{(42 + i * 0.5):F1},\"age\":{(40 + i)}}}");
        File.WriteAllText(path2, sb2.ToString());
        var doc2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(0, doc2.GetFieldNullPattern("hba1c"));
        Assert.Equal(0.0, doc2.GetFieldMissingRate("hba1c"), precision: 6);
        Assert.Equal(1.0, doc2.GetFieldPresentRate("hba1c"), precision: 6);
    }
}
