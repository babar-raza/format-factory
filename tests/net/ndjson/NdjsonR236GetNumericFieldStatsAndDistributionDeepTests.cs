// Tests for NdjsonDocument.GetNumericFieldStats, GetFieldDistribution, GetCategoryBreakdown deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R236

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R236: Tests for NdjsonDocument.GetNumericFieldStats, GetFieldDistribution, GetCategoryBreakdown deeper.
/// GetNumericFieldStats(field): returns a stats object with Min, Max, Mean, StdDev for the field.
/// GetFieldDistribution(field): returns a dictionary mapping each distinct value to its count.
/// GetCategoryBreakdown(field): returns a dictionary mapping each distinct value to its percentage.
/// Covers: GetNumericFieldStats no-throw; GetNumericFieldStats min leq max; GetNumericFieldStats mean in range;
/// GetNumericFieldStats stddev non-negative; GetNumericFieldStats consistent; GetNumericFieldStats save-load;
/// GetFieldDistribution no-throw; GetFieldDistribution non-null; GetFieldDistribution consistent;
/// GetFieldDistribution counts sum to record count; GetFieldDistribution save-load;
/// GetCategoryBreakdown no-throw; GetCategoryBreakdown non-null; GetCategoryBreakdown percentages in range;
/// GetCategoryBreakdown sum near 100; GetCategoryBreakdown save-load;
/// dogfood CreateDoc→GetNumericFieldStats→GetFieldDistribution→GetCategoryBreakdown→SaveToFile pipeline.
/// </summary>
public class NdjsonR236GetNumericFieldStatsAndDistributionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR236GetNumericFieldStatsAndDistributionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR236_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeNdjson()
    {
        var path = TempFile("employees.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"emp_id\":\"E001\",\"department\":\"Engineering\",\"grade\":\"Senior\",\"salary\":85000,\"years_exp\":8,\"performance\":4.2}",
            "{\"emp_id\":\"E002\",\"department\":\"Marketing\",\"grade\":\"Junior\",\"salary\":42000,\"years_exp\":2,\"performance\":3.8}",
            "{\"emp_id\":\"E003\",\"department\":\"Engineering\",\"grade\":\"Lead\",\"salary\":110000,\"years_exp\":12,\"performance\":4.7}",
            "{\"emp_id\":\"E004\",\"department\":\"Finance\",\"grade\":\"Senior\",\"salary\":78000,\"years_exp\":6,\"performance\":4.0}",
            "{\"emp_id\":\"E005\",\"department\":\"Marketing\",\"grade\":\"Senior\",\"salary\":65000,\"years_exp\":5,\"performance\":3.9}",
            "{\"emp_id\":\"E006\",\"department\":\"Engineering\",\"grade\":\"Junior\",\"salary\":55000,\"years_exp\":3,\"performance\":3.6}",
            "{\"emp_id\":\"E007\",\"department\":\"HR\",\"grade\":\"Senior\",\"salary\":60000,\"years_exp\":7,\"performance\":4.1}",
            "{\"emp_id\":\"E008\",\"department\":\"Engineering\",\"grade\":\"Lead\",\"salary\":120000,\"years_exp\":15,\"performance\":4.9}",
            "{\"emp_id\":\"E009\",\"department\":\"Finance\",\"grade\":\"Junior\",\"salary\":38000,\"years_exp\":1,\"performance\":3.5}",
            "{\"emp_id\":\"E010\",\"department\":\"Marketing\",\"grade\":\"Lead\",\"salary\":95000,\"years_exp\":10,\"performance\":4.5}"
        });
        return path;
    }

    private string CreateUniformNdjson()
    {
        var path = TempFile("uniform.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":\"U1\",\"score\":50,\"category\":\"A\"}",
            "{\"id\":\"U2\",\"score\":50,\"category\":\"A\"}",
            "{\"id\":\"U3\",\"score\":50,\"category\":\"A\"}",
            "{\"id\":\"U4\",\"score\":50,\"category\":\"A\"}",
            "{\"id\":\"U5\",\"score\":50,\"category\":\"A\"}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNumericFieldStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericFieldStats_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetNumericFieldStats("salary"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetNumericFieldStats_MinLeqMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetNumericFieldStats("salary");
        Assert.True(stats.Min <= stats.Max);
    }

    [Fact]
    public void GetNumericFieldStats_MeanInRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetNumericFieldStats("salary");
        Assert.True(stats.Mean >= stats.Min);
        Assert.True(stats.Mean <= stats.Max);
    }

    [Fact]
    public void GetNumericFieldStats_StdDevNonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var stats = doc.GetNumericFieldStats("years_exp");
        Assert.True(stats.StdDev >= 0.0);
    }

    [Fact]
    public void GetNumericFieldStats_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var s1 = doc.GetNumericFieldStats("performance");
        var s2 = doc.GetNumericFieldStats("performance");
        Assert.Equal(s1.Min, s2.Min);
        Assert.Equal(s1.Max, s2.Max);
        Assert.Equal(s1.Mean, s2.Mean, precision: 6);
    }

    [Fact]
    public void GetNumericFieldStats_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetNumericFieldStats("salary");
        var path = TempFile("nfs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetNumericFieldStats("salary");
        Assert.Equal(before.Min, after.Min, precision: 6);
        Assert.Equal(before.Max, after.Max, precision: 6);
        Assert.Equal(before.Mean, after.Mean, precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldDistribution
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldDistribution_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetFieldDistribution("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldDistribution_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetFieldDistribution("department"));
    }

    [Fact]
    public void GetFieldDistribution_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var d1 = doc.GetFieldDistribution("grade");
        var d2 = doc.GetFieldDistribution("grade");
        Assert.Equal(d1.Count, d2.Count);
    }

    [Fact]
    public void GetFieldDistribution_CountsSumToRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var dist = doc.GetFieldDistribution("department");
        int total = 0;
        foreach (var kvp in dist) total += kvp.Value;
        Assert.Equal(doc.GetRecordCount(), total);
    }

    [Fact]
    public void GetFieldDistribution_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetFieldDistribution("department");
        var path = TempFile("fd_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetFieldDistribution("department");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // GetCategoryBreakdown
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCategoryBreakdown_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetCategoryBreakdown("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCategoryBreakdown_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetCategoryBreakdown("grade"));
    }

    [Fact]
    public void GetCategoryBreakdown_PercentagesInRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var breakdown = doc.GetCategoryBreakdown("department");
        foreach (var kvp in breakdown)
        {
            Assert.True(kvp.Value >= 0.0);
            Assert.True(kvp.Value <= 100.0);
        }
    }

    [Fact]
    public void GetCategoryBreakdown_SumNear100()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var breakdown = doc.GetCategoryBreakdown("grade");
        double total = 0.0;
        foreach (var kvp in breakdown) total += kvp.Value;
        Assert.True(Math.Abs(total - 100.0) < 1.0);
    }

    [Fact]
    public void GetCategoryBreakdown_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetCategoryBreakdown("department");
        var path = TempFile("cb_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        var after = loaded.GetCategoryBreakdown("department");
        Assert.Equal(before.Count, after.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNumericFieldStats_GetFieldDistribution_GetCategoryBreakdown_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_clinical_trials.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"trial_id\":\"CT001\",\"phase\":\"Phase2\",\"indication\":\"Oncology\",\"arm\":\"Treatment\",\"patients\":120,\"response_rate\":0.42,\"adverse_events\":18,\"dropout_rate\":0.08}",
            "{\"trial_id\":\"CT002\",\"phase\":\"Phase3\",\"indication\":\"Cardiology\",\"arm\":\"Control\",\"patients\":240,\"response_rate\":0.21,\"adverse_events\":12,\"dropout_rate\":0.05}",
            "{\"trial_id\":\"CT003\",\"phase\":\"Phase2\",\"indication\":\"Neurology\",\"arm\":\"Treatment\",\"patients\":90,\"response_rate\":0.38,\"adverse_events\":22,\"dropout_rate\":0.11}",
            "{\"trial_id\":\"CT004\",\"phase\":\"Phase3\",\"indication\":\"Oncology\",\"arm\":\"Treatment\",\"patients\":310,\"response_rate\":0.51,\"adverse_events\":35,\"dropout_rate\":0.09}",
            "{\"trial_id\":\"CT005\",\"phase\":\"Phase1\",\"indication\":\"Immunology\",\"arm\":\"Treatment\",\"patients\":45,\"response_rate\":0.29,\"adverse_events\":8,\"dropout_rate\":0.04}",
            "{\"trial_id\":\"CT006\",\"phase\":\"Phase2\",\"indication\":\"Cardiology\",\"arm\":\"Control\",\"patients\":110,\"response_rate\":0.18,\"adverse_events\":9,\"dropout_rate\":0.06}",
            "{\"trial_id\":\"CT007\",\"phase\":\"Phase3\",\"indication\":\"Neurology\",\"arm\":\"Treatment\",\"patients\":280,\"response_rate\":0.45,\"adverse_events\":28,\"dropout_rate\":0.10}",
            "{\"trial_id\":\"CT008\",\"phase\":\"Phase1\",\"indication\":\"Oncology\",\"arm\":\"Treatment\",\"patients\":30,\"response_rate\":0.33,\"adverse_events\":5,\"dropout_rate\":0.03}",
            "{\"trial_id\":\"CT009\",\"phase\":\"Phase2\",\"indication\":\"Immunology\",\"arm\":\"Control\",\"patients\":85,\"response_rate\":0.15,\"adverse_events\":7,\"dropout_rate\":0.05}",
            "{\"trial_id\":\"CT010\",\"phase\":\"Phase3\",\"indication\":\"Cardiology\",\"arm\":\"Treatment\",\"patients\":350,\"response_rate\":0.48,\"adverse_events\":42,\"dropout_rate\":0.12}",
            "{\"trial_id\":\"CT011\",\"phase\":\"Phase2\",\"indication\":\"Oncology\",\"arm\":\"Control\",\"patients\":115,\"response_rate\":0.22,\"adverse_events\":14,\"dropout_rate\":0.07}",
            "{\"trial_id\":\"CT012\",\"phase\":\"Phase1\",\"indication\":\"Neurology\",\"arm\":\"Treatment\",\"patients\":25,\"response_rate\":0.36,\"adverse_events\":4,\"dropout_rate\":0.04}"
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetNumericFieldStats — patients
        var patientsStats = doc.GetNumericFieldStats("patients");
        Assert.True(patientsStats.Min <= patientsStats.Max);
        Assert.True(patientsStats.Mean >= patientsStats.Min);
        Assert.True(patientsStats.Mean <= patientsStats.Max);
        Assert.True(patientsStats.StdDev >= 0.0);
        Assert.Equal(25.0, patientsStats.Min, precision: 1); // CT008 = 30, CT012=25

        // GetNumericFieldStats — response_rate
        var rrStats = doc.GetNumericFieldStats("response_rate");
        Assert.True(rrStats.Min >= 0.0);
        Assert.True(rrStats.Max <= 1.0);
        Assert.True(rrStats.StdDev >= 0.0);

        // GetNumericFieldStats — adverse_events
        var aeStats = doc.GetNumericFieldStats("adverse_events");
        Assert.True(aeStats.Min >= 0.0);
        Assert.True(aeStats.Mean >= aeStats.Min);
        Assert.True(aeStats.Mean <= aeStats.Max);

        // Consistent
        var stats2 = doc.GetNumericFieldStats("patients");
        Assert.Equal(patientsStats.Min, stats2.Min, precision: 6);

        // GetFieldDistribution — phase
        var phaseDist = doc.GetFieldDistribution("phase");
        Assert.NotNull(phaseDist);
        int phaseTotal = 0;
        foreach (var kvp in phaseDist) phaseTotal += kvp.Value;
        Assert.Equal(12, phaseTotal);
        Assert.True(phaseDist.ContainsKey("Phase1") || phaseDist.ContainsKey("Phase2") || phaseDist.ContainsKey("Phase3"));

        // GetFieldDistribution — indication
        var indDist = doc.GetFieldDistribution("indication");
        int indTotal = 0;
        foreach (var kvp in indDist) indTotal += kvp.Value;
        Assert.Equal(12, indTotal);

        // GetFieldDistribution — arm
        var armDist = doc.GetFieldDistribution("arm");
        int armTotal = 0;
        foreach (var kvp in armDist) armTotal += kvp.Value;
        Assert.Equal(12, armTotal);

        // GetCategoryBreakdown — phase
        var phaseBreakdown = doc.GetCategoryBreakdown("phase");
        Assert.NotNull(phaseBreakdown);
        double phaseSum = 0.0;
        foreach (var kvp in phaseBreakdown)
        {
            Assert.True(kvp.Value >= 0.0);
            Assert.True(kvp.Value <= 100.0);
            phaseSum += kvp.Value;
        }
        Assert.True(Math.Abs(phaseSum - 100.0) < 1.0);

        // GetCategoryBreakdown — arm (should sum to ~100%)
        var armBreakdown = doc.GetCategoryBreakdown("arm");
        double armSum = 0.0;
        foreach (var kvp in armBreakdown) armSum += kvp.Value;
        Assert.True(Math.Abs(armSum - 100.0) < 1.0);

        // Consistent
        Assert.Equal(doc.GetFieldDistribution("phase").Count, doc.GetFieldDistribution("phase").Count);

        // SaveToFile
        var out1 = TempFile("dogfood_clinical_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        var loadedStats = loaded.GetNumericFieldStats("patients");
        Assert.Equal(patientsStats.Min, loadedStats.Min, precision: 6);
        Assert.Equal(patientsStats.Max, loadedStats.Max, precision: 6);
        var loadedDist = loaded.GetFieldDistribution("phase");
        Assert.Equal(phaseDist.Count, loadedDist.Count);
        var loadedBreakdown = loaded.GetCategoryBreakdown("indication");
        Assert.NotNull(loadedBreakdown);

        // AddRecord on loaded
        loaded.AddRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["trial_id"] = "CT013",
            ["phase"] = "Phase2",
            ["indication"] = "Immunology",
            ["arm"] = "Treatment",
            ["patients"] = 75,
            ["response_rate"] = 0.40,
            ["adverse_events"] = 11,
            ["dropout_rate"] = 0.06
        });
        Assert.Equal(13, loaded.GetRecordCount());

        // Stats update after AddRecord
        var updatedStats = loaded.GetNumericFieldStats("patients");
        Assert.True(updatedStats.Min <= updatedStats.Max);

        // Final save
        var out2 = TempFile("dogfood_clinical_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.NotNull(loaded2.GetNumericFieldStats("patients"));
        Assert.NotNull(loaded2.GetFieldDistribution("phase"));
        Assert.NotNull(loaded2.GetCategoryBreakdown("arm"));
        var ex1 = Record.Exception(() => loaded2.GetNumericFieldStats("response_rate"));
        var ex2 = Record.Exception(() => loaded2.GetFieldDistribution("indication"));
        var ex3 = Record.Exception(() => loaded2.GetCategoryBreakdown("phase"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
