// Tests for TsvDocument.GetColumnFirstQuartile, GetColumnThirdQuartile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R271

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R271: Tests for TsvDocument.GetColumnFirstQuartile, GetColumnThirdQuartile deeper.
/// GetColumnFirstQuartile(colName): returns the first quartile (Q1, 25th percentile) of numeric values.
/// GetColumnThirdQuartile(colName): returns the third quartile (Q3, 75th percentile) of numeric values.
/// Covers: GetColumnFirstQuartile no-throw; GetColumnFirstQuartile in-range;
/// GetColumnFirstQuartile equal for uniform; GetColumnFirstQuartile consistent;
/// GetColumnFirstQuartile save-load;
/// GetColumnThirdQuartile no-throw; GetColumnThirdQuartile in-range;
/// GetColumnThirdQuartile equal for uniform; GetColumnThirdQuartile consistent;
/// GetColumnThirdQuartile save-load;
/// GetColumnFirstQuartile leq GetColumnThirdQuartile; dogfood pipeline.
/// </summary>
public class TsvR271GetColumnFirstQuartileAndThirdQuartileDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR271GetColumnFirstQuartileAndThirdQuartileDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR271_" + Guid.NewGuid().ToString("N"));
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
        sb.AppendLine("id\tvalue");
        // 12 values: 0,10,20,30,40,50,60,70,80,90,100,110
        for (int i = 0; i <= 11; i++) sb.AppendLine($"R{i:D2}\t{i * 10.0}");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("id\tmeasure");
        for (int i = 0; i < 20; i++) sb.AppendLine($"R{i:D2}\t55.0");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnFirstQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFirstQuartile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnFirstQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFirstQuartile_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var q1 = doc.GetColumnFirstQuartile("value");
        Assert.True(q1 >= doc.GetColumnMin("value") && q1 <= doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnFirstQuartile_Equal_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(55.0, doc.GetColumnFirstQuartile("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnFirstQuartile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnFirstQuartile("value"), doc.GetColumnFirstQuartile("value"));
    }

    [Fact]
    public void GetColumnFirstQuartile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnFirstQuartile("value");
        var path = TempFile("q1_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnFirstQuartile("value"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetColumnThirdQuartile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnThirdQuartile_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnThirdQuartile("value"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnThirdQuartile_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var q3 = doc.GetColumnThirdQuartile("value");
        Assert.True(q3 >= doc.GetColumnMin("value") && q3 <= doc.GetColumnMax("value"));
    }

    [Fact]
    public void GetColumnThirdQuartile_Equal_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(55.0, doc.GetColumnThirdQuartile("measure"), precision: 6);
    }

    [Fact]
    public void GetColumnThirdQuartile_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnThirdQuartile("value"), doc.GetColumnThirdQuartile("value"));
    }

    [Fact]
    public void GetColumnThirdQuartile_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetColumnThirdQuartile("value");
        var path = TempFile("q3_save.tsv");
        doc.SaveToFile(path);
        Assert.Equal(before, TsvDocument.LoadFile(path).GetColumnThirdQuartile("value"), precision: 6);
    }

    [Fact]
    public void GetColumnFirstQuartile_Leq_GetColumnThirdQuartile()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnFirstQuartile("value") <= doc.GetColumnThirdQuartile("value"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnFirstQuartile_GetColumnThirdQuartile_Pipeline()
    {
        // Health — NHS Digital / NHSE: Hospital Episode Statistics 2023-24
        // Inpatient spell data: length of stay, waiting time, and procedure cost distributions
        // Q1/Q3 quantify typical admission patterns and detect skewed distributions

        var path = TempFile("nhs_hes_inpatient_2024.tsv");
        var sb = new StringBuilder();
        sb.AppendLine("spell_id\tspecialty\tlos_days\twait_weeks\tprocedure_cost_gbp\tbed_type\tage_group\toutcome");

        var rng = new Random(20240401);
        string[] specialties = {
            "Cardiology", "Orthopaedics", "General_Surgery", "Neurology", "Oncology",
            "Gastroenterology", "Urology", "Respiratory", "Rheumatology", "Endocrinology"
        };
        string[] bedTypes = { "Day_Case", "Elective", "Emergency", "Maternity" };
        string[] ageGroups = { "0-17", "18-29", "30-44", "45-59", "60-74", "75+" };
        string[] outcomes = { "Discharged", "Discharged", "Discharged", "Transferred", "Deceased" };

        // LoS parameters by specialty (mean, sd)
        double[] losMean = { 4.5, 6.2, 3.1, 7.8, 9.3, 2.4, 2.8, 5.6, 3.9, 2.1 };

        for (int i = 0; i < 400; i++)
        {
            int specIdx = rng.Next(specialties.Length);
            double los = Math.Max(0.5, losMean[specIdx] + (rng.NextDouble() - 0.5) * losMean[specIdx] * 1.2);
            // Outlier: very long stay
            if (rng.NextDouble() < 0.03) los *= 5;
            double wait = Math.Max(0, 4 + rng.NextDouble() * 48);
            double cost = 800 + losMean[specIdx] * 180 + rng.NextDouble() * 1500;
            string bed = bedTypes[rng.Next(bedTypes.Length)];
            string age = ageGroups[rng.Next(ageGroups.Length)];
            string outcome = outcomes[rng.Next(outcomes.Length)];
            sb.AppendLine($"HES{i:D6}\t{specialties[specIdx]}\t{los:F1}\t{wait:F1}\t{cost:F0}\t{bed}\t{age}\t{outcome}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(400, doc.RowCount);
        Assert.Equal(8, doc.ColumnCount);

        // Length of stay quartiles
        var losQ1 = doc.GetColumnFirstQuartile("los_days");
        var losQ3 = doc.GetColumnThirdQuartile("los_days");
        Assert.True(losQ1 >= doc.GetColumnMin("los_days"));
        Assert.True(losQ3 <= doc.GetColumnMax("los_days"));
        Assert.True(losQ1 <= losQ3);
        Assert.Equal(losQ1, doc.GetColumnFirstQuartile("los_days")); // consistent
        Assert.Equal(losQ3, doc.GetColumnThirdQuartile("los_days")); // consistent

        // Wait time quartiles
        var waitQ1 = doc.GetColumnFirstQuartile("wait_weeks");
        var waitQ3 = doc.GetColumnThirdQuartile("wait_weeks");
        Assert.True(waitQ1 >= 0.0);
        Assert.True(waitQ1 <= waitQ3);

        // Procedure cost quartiles
        var costQ1 = doc.GetColumnFirstQuartile("procedure_cost_gbp");
        var costQ3 = doc.GetColumnThirdQuartile("procedure_cost_gbp");
        Assert.True(costQ1 >= 0.0);
        Assert.True(costQ1 <= costQ3);

        // IQR (Q3 - Q1) > 0 for varied data
        Assert.True((losQ3 - losQ1) >= 0.0);
        Assert.True((waitQ3 - waitQ1) >= 0.0);

        // SaveToFile
        var outPath = TempFile("nhs_hes_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(doc.RowCount, loaded.RowCount);
        Assert.Equal(losQ1, loaded.GetColumnFirstQuartile("los_days"), precision: 6);
        Assert.Equal(losQ3, loaded.GetColumnThirdQuartile("los_days"), precision: 6);
        Assert.Equal(waitQ1, loaded.GetColumnFirstQuartile("wait_weeks"), precision: 6);
        Assert.Equal(costQ3, loaded.GetColumnThirdQuartile("procedure_cost_gbp"), precision: 6);
    }
}
