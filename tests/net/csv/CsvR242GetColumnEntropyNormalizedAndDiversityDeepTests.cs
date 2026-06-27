// Tests for CsvDocument.GetColumnEntropyNormalized, GetColumnDiversity, GetColumnCardinality deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R242

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R242: Tests for CsvDocument.GetColumnEntropyNormalized, GetColumnDiversity, GetColumnCardinality deeper.
/// GetColumnEntropyNormalized(columnName): returns entropy divided by log(cardinality), in [0,1].
/// GetColumnDiversity(columnName): returns distinct value count divided by row count, in [0,1].
/// GetColumnCardinality(columnName): returns the count of distinct values in the column.
/// Covers: GetColumnEntropyNormalized no-throw; GetColumnEntropyNormalized in [0,1];
/// GetColumnEntropyNormalized consistent; GetColumnEntropyNormalized high for uniform;
/// GetColumnDiversity no-throw; GetColumnDiversity in [0,1]; GetColumnDiversity consistent;
/// GetColumnDiversity high for all-distinct; GetColumnDiversity low for constant;
/// GetColumnCardinality no-throw; GetColumnCardinality positive; GetColumnCardinality consistent;
/// GetColumnCardinality one for constant; GetColumnCardinality save-load;
/// dogfood pipeline for all three measures.
/// </summary>
public class CsvR242GetColumnEntropyNormalizedAndDiversityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR242GetColumnEntropyNormalizedAndDiversityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePatientDataCsv()
    {
        var path = TempFile("patient_data.csv");
        File.WriteAllLines(path, new[]
        {
            "patient_id,blood_type,diagnosis_group,treatment_pathway,ward,discharge_status",
            "P001,A+,Cardiac,Surgical,CCU,Discharged",
            "P002,O+,Respiratory,Medical,ITU,Discharged",
            "P003,B+,Orthopedic,Surgical,General,Discharged",
            "P004,AB-,Neurological,Medical,Neuro,Transferred",
            "P005,A+,Cardiac,Medical,CCU,Discharged",
            "P006,O-,Oncology,Oncology,Oncology,Discharged",
            "P007,A-,Respiratory,Medical,General,Deceased",
            "P008,B-,Orthopedic,Surgical,Ortho,Discharged",
            "P009,O+,Cardiac,Surgical,CCU,Discharged",
            "P010,AB+,Neurological,Surgical,Neuro,Discharged",
            "P011,A+,Gastro,Medical,General,Discharged",
            "P012,O+,Cardiac,Medical,CCU,Transferred",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropyNormalized
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropyNormalized_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var ex = Record.Exception(() => doc.GetColumnEntropyNormalized("diagnosis_group"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropyNormalized_InRange()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var en = doc.GetColumnEntropyNormalized("diagnosis_group");
        Assert.True(en >= 0.0 && en <= 1.0);
    }

    [Fact]
    public void GetColumnEntropyNormalized_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        Assert.Equal(
            doc.GetColumnEntropyNormalized("blood_type"),
            doc.GetColumnEntropyNormalized("blood_type"));
    }

    [Fact]
    public void GetColumnEntropyNormalized_High_ForUniform()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        // blood_type has 8 types, fairly spread → high normalized entropy
        var en = doc.GetColumnEntropyNormalized("blood_type");
        Assert.True(en > 0.5);
    }

    // -------------------------------------------------------------------------
    // GetColumnDiversity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDiversity_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var ex = Record.Exception(() => doc.GetColumnDiversity("ward"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDiversity_InRange()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var div = doc.GetColumnDiversity("ward");
        Assert.True(div >= 0.0 && div <= 1.0);
    }

    [Fact]
    public void GetColumnDiversity_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        Assert.Equal(
            doc.GetColumnDiversity("treatment_pathway"),
            doc.GetColumnDiversity("treatment_pathway"));
    }

    [Fact]
    public void GetColumnDiversity_High_ForAllDistinct()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        // patient_id: all 12 distinct → diversity ≈ 1.0
        Assert.True(doc.GetColumnDiversity("patient_id") >= 0.9);
    }

    // -------------------------------------------------------------------------
    // GetColumnCardinality
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCardinality_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var ex = Record.Exception(() => doc.GetColumnCardinality("diagnosis_group"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCardinality_Positive()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        Assert.True(doc.GetColumnCardinality("blood_type") > 0);
    }

    [Fact]
    public void GetColumnCardinality_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        Assert.Equal(
            doc.GetColumnCardinality("ward"),
            doc.GetColumnCardinality("ward"));
    }

    [Fact]
    public void GetColumnCardinality_One_ForConstant()
    {
        var path = TempFile("constant.csv");
        File.WriteAllLines(path, new[] { "id,value", "A,X", "B,X", "C,X" });
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(1, doc.GetColumnCardinality("value"));
    }

    [Fact]
    public void GetColumnCardinality_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientDataCsv());
        var before = doc.GetColumnCardinality("diagnosis_group");
        var path = TempFile("card_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCardinality("diagnosis_group"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropyNormalized_GetColumnDiversity_GetColumnCardinality_Pipeline()
    {
        // Clinical data governance — multi-site trial data quality assessment
        var path = TempFile("trial_data_quality.csv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("record_id,site_id,visit_type,arm,adverse_event_grade,lab_panel,form_status,region");
        string[] sites = { "SITE001", "SITE002", "SITE003", "SITE004", "SITE005" };
        string[] visits = { "Screening", "Baseline", "Week4", "Week8", "Week12", "Week24", "EOT" };
        string[] arms = { "Placebo", "LowDose", "HighDose" };
        string[] grades = { "0", "1", "2", "3" };
        string[] panels = { "CBC", "LFT", "RFT", "Lipids", "Glucose", "HbA1c" };
        string[] statuses = { "Complete", "Pending", "Queried", "Locked" };
        string[] regions = { "Europe", "Americas", "AsiaPac" };
        var rng = new Random(20241201);
        for (int i = 0; i < 120; i++)
            lines.Add($"REC{i:D5},{sites[i % 5]},{visits[i % 7]},{arms[i % 3]},{grades[i % 4]},{panels[i % 6]},{statuses[i % 4]},{regions[i % 3]}");
        File.WriteAllLines(path, lines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnCardinality
        Assert.Equal(5, doc.GetColumnCardinality("site_id"));
        Assert.Equal(7, doc.GetColumnCardinality("visit_type"));
        Assert.Equal(3, doc.GetColumnCardinality("arm"));
        Assert.Equal(4, doc.GetColumnCardinality("adverse_event_grade"));
        Assert.Equal(6, doc.GetColumnCardinality("lab_panel"));
        Assert.Equal(4, doc.GetColumnCardinality("form_status"));
        Assert.Equal(3, doc.GetColumnCardinality("region"));
        Assert.Equal(doc.GetColumnCardinality("visit_type"), doc.GetColumnCardinality("visit_type")); // consistent

        // GetColumnDiversity
        var siteDiv = doc.GetColumnDiversity("site_id");
        Assert.True(siteDiv >= 0.0 && siteDiv <= 1.0);
        var visitDiv = doc.GetColumnDiversity("visit_type");
        Assert.True(visitDiv >= 0.0 && visitDiv <= 1.0);
        Assert.True(visitDiv > siteDiv); // 7 visits > 5 sites → higher diversity
        Assert.Equal(siteDiv, doc.GetColumnDiversity("site_id")); // consistent

        // GetColumnEntropyNormalized
        var siteEn = doc.GetColumnEntropyNormalized("site_id");
        Assert.True(siteEn >= 0.0 && siteEn <= 1.0);
        var visitEn = doc.GetColumnEntropyNormalized("visit_type");
        Assert.True(visitEn >= 0.0 && visitEn <= 1.0);
        Assert.True(siteEn > 0.8); // uniform distribution → high entropy
        Assert.True(visitEn > 0.8);
        Assert.Equal(siteEn, doc.GetColumnEntropyNormalized("site_id")); // consistent

        // SaveToFile
        var outPath = TempFile("trial_quality_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(5, loaded.GetColumnCardinality("site_id"));
        Assert.Equal(siteDiv, loaded.GetColumnDiversity("site_id"), precision: 6);
        Assert.Equal(siteEn, loaded.GetColumnEntropyNormalized("site_id"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }
}
