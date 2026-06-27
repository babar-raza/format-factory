// Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R274

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R274: Tests for CsvDocument.GetColumnSkewness, GetColumnKurtosis deeper.
/// GetColumnSkewness(colName): returns the skewness of the numeric distribution in the column.
/// GetColumnKurtosis(colName): returns the kurtosis of the numeric distribution in the column.
/// Covers: GetColumnSkewness no-throw; GetColumnSkewness finite; GetColumnSkewness zero for uniform;
/// GetColumnSkewness consistent; GetColumnSkewness save-load;
/// GetColumnKurtosis no-throw; GetColumnKurtosis finite;
/// GetColumnKurtosis consistent; GetColumnKurtosis save-load;
/// dogfood pipeline.
/// </summary>
public class CsvR274GetColumnSkewnessAndKurtosisDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR274GetColumnSkewnessAndKurtosisDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR274_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,value");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2},{i * 5.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformCsv()
    {
        var path = TempFile("uniform.csv");
        var sb = new StringBuilder();
        sb.AppendLine("id,measure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2},42.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnSkewness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnSkewness_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnSkewness("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnSkewness_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sk = doc.GetColumnSkewness("value");
        Assert.True(!double.IsNaN(sk) && !double.IsInfinity(sk));
    }

    [Fact]
    public void GetColumnSkewness_Zero_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreateUniformCsv());
        Assert.Equal(0.0, doc.GetColumnSkewness("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnSkewness_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnSkewness("value"), doc.GetColumnSkewness("value"));
    }

    [Fact]
    public void GetColumnSkewness_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnSkewness("value");
        var path = TempFile("sk_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnSkewness("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnKurtosis
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnKurtosis_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnKurtosis("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnKurtosis_Finite()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var kurt = doc.GetColumnKurtosis("value");
        Assert.True(!double.IsNaN(kurt) && !double.IsInfinity(kurt));
    }

    [Fact]
    public void GetColumnKurtosis_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnKurtosis("value"), doc.GetColumnKurtosis("value"));
    }

    [Fact]
    public void GetColumnKurtosis_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnKurtosis("value");
        var path = TempFile("kurt_save.csv");
        doc.SaveToFile(path);
        Assert.Equal(before, CsvDocument.LoadFile(path).GetColumnKurtosis("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnSkewness_GetColumnKurtosis_Pipeline()
    {
        // Health — MHRA / NICE: Medicine Adverse Event Reporting System
        // Reporting rates and severity scores for Yellow Card adverse drug reaction submissions
        // Skewness/kurtosis of severity and time-to-report distributions detect signal clusters

        var path = TempFile("mhra_yellowcard_2024.csv");
        var sb = new StringBuilder();
        sb.AppendLine("report_id,drug_class,reporter_type,days_to_report,severity_score,outcome_code,age_group,reports_per_100k_prescriptions");

        var rng = new Random(20240101);
        string[] drugClasses = {
            "Anticoagulants", "NSAIDs", "Statins", "ACE_Inhibitors", "Beta_Blockers",
            "Antidepressants", "Antibiotics", "Opioids", "Antipsychotics", "Antivirals",
            "Biologics", "Chemotherapy", "Immunosuppressants", "Anticonvulsants", "Hormones"
        };
        string[] reporters = { "GP", "Hospital_Consultant", "Pharmacist", "Nurse", "Patient" };
        string[] outcomes = { "Recovered", "Recovering", "Recovered_With_Sequelae", "Fatal", "Unknown" };
        string[] ageGroups = { "18-29", "30-44", "45-59", "60-74", "75+" };

        for (int i = 0; i < 400; i++)
        {
            string drug = drugClasses[rng.Next(drugClasses.Length)];
            string reporter = reporters[rng.Next(reporters.Length)];
            // Days to report: right-skewed (most < 30 days, some very late)
            double daysToReport = rng.NextDouble() < 0.1
                ? 90 + rng.NextDouble() * 180  // late reporters
                : 2 + rng.NextDouble() * 28;
            // Severity score: right-skewed (most mild 1-4, some severe)
            double severity = rng.NextDouble() < 0.05
                ? 8 + rng.NextDouble() * 2  // severe outliers
                : 1 + rng.NextDouble() * 5;
            string outcome = outcomes[rng.Next(outcomes.Length)];
            string age = ageGroups[rng.Next(ageGroups.Length)];
            // Reports per 100k: varies by drug class
            double reportRate = drug == "Opioids" ? 12 + rng.NextDouble() * 20
                              : drug == "Biologics" ? 8 + rng.NextDouble() * 15
                              : 0.5 + rng.NextDouble() * 5;
            sb.AppendLine($"YC{i:D6},{drug},{reporter},{daysToReport:F0},{severity:F1},{outcome},{age},{reportRate:F2}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(400, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Days to report skewness (right-skewed expected)
        var daysSkew = doc.GetColumnSkewness("days_to_report");
        var daysKurt = doc.GetColumnKurtosis("days_to_report");
        Assert.True(!double.IsNaN(daysSkew) && !double.IsInfinity(daysSkew));
        Assert.True(!double.IsNaN(daysKurt) && !double.IsInfinity(daysKurt));
        Assert.Equal(daysSkew, doc.GetColumnSkewness("days_to_report")); // consistent
        Assert.Equal(daysKurt, doc.GetColumnKurtosis("days_to_report")); // consistent

        // Severity score skewness
        var sevSkew = doc.GetColumnSkewness("severity_score");
        var sevKurt = doc.GetColumnKurtosis("severity_score");
        Assert.True(!double.IsNaN(sevSkew) && !double.IsInfinity(sevSkew));
        Assert.True(!double.IsNaN(sevKurt) && !double.IsInfinity(sevKurt));

        // Report rate skewness
        var rateSkew = doc.GetColumnSkewness("reports_per_100k_prescriptions");
        var rateKurt = doc.GetColumnKurtosis("reports_per_100k_prescriptions");
        Assert.True(!double.IsNaN(rateSkew) && !double.IsInfinity(rateSkew));
        Assert.True(!double.IsNaN(rateKurt) && !double.IsInfinity(rateKurt));

        // SaveToFile
        var outPath = TempFile("mhra_yc_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(daysSkew, loaded.GetColumnSkewness("days_to_report"), precision: 6);
        Assert.Equal(daysKurt, loaded.GetColumnKurtosis("days_to_report"), precision: 6);
        Assert.Equal(sevSkew, loaded.GetColumnSkewness("severity_score"), precision: 6);
        Assert.Equal(rateKurt, loaded.GetColumnKurtosis("reports_per_100k_prescriptions"), precision: 6);
    }
}
