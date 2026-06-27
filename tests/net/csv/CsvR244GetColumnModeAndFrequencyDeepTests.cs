// Tests for CsvDocument.GetColumnMode, GetColumnFrequency, GetColumnUniqueRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R244

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R244: Tests for CsvDocument.GetColumnMode, GetColumnFrequency, GetColumnUniqueRatio deeper.
/// GetColumnMode(columnName): returns the most frequently occurring value in the column.
/// GetColumnFrequency(columnName, value): returns how many times the given value appears.
/// GetColumnUniqueRatio(columnName): returns the ratio of unique values to total values (0–1).
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnFrequency no-throw; GetColumnFrequency non-negative; GetColumnFrequency consistent;
/// GetColumnFrequency zero for absent value;
/// GetColumnUniqueRatio no-throw; GetColumnUniqueRatio in [0,1]; GetColumnUniqueRatio consistent;
/// GetColumnUniqueRatio one for all-unique column; GetColumnUniqueRatio save-load;
/// dogfood CreateDoc→GetColumnMode→GetColumnFrequency→GetColumnUniqueRatio pipeline.
/// </summary>
public class CsvR244GetColumnModeAndFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR244GetColumnModeAndFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR244_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePatientCsv()
    {
        var path = TempFile("patients.csv");
        var lines = new System.Collections.Generic.List<string>
        {
            "patient_id,blood_group,ward,admission_type,los_category",
            "P001,A+,Cardiology,Emergency,Short",
            "P002,O+,Orthopaedics,Elective,Medium",
            "P003,A+,Cardiology,Emergency,Short",
            "P004,B+,Oncology,Elective,Long",
            "P005,O+,Cardiology,Emergency,Short",
            "P006,AB+,Neurology,Elective,Medium",
            "P007,A+,Cardiology,Day_Case,Short",
            "P008,O+,Orthopaedics,Elective,Medium",
            "P009,A-,Oncology,Emergency,Long",
            "P010,O+,Cardiology,Elective,Short",
            "P011,A+,Neurology,Emergency,Medium",
            "P012,B-,Orthopaedics,Elective,Short",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateUniqueRefCsv()
    {
        var path = TempFile("unique_refs.csv");
        var lines = new string[]
        {
            "ref_code,amount,type",
            "REF-A001,100,X",
            "REF-B002,200,Y",
            "REF-C003,300,X",
            "REF-D004,400,Z",
            "REF-E005,500,Y",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        var ex = Record.Exception(() => doc.GetColumnMode("ward"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.NotNull(doc.GetColumnMode("blood_group"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.Equal(doc.GetColumnMode("ward"), doc.GetColumnMode("ward"));
    }

    // -------------------------------------------------------------------------
    // GetColumnFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFrequency_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        var ex = Record.Exception(() => doc.GetColumnFrequency("blood_group", "O+"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFrequency_NonNegative()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.True(doc.GetColumnFrequency("ward", "Cardiology") >= 0);
    }

    [Fact]
    public void GetColumnFrequency_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.Equal(
            doc.GetColumnFrequency("admission_type", "Emergency"),
            doc.GetColumnFrequency("admission_type", "Emergency"));
    }

    [Fact]
    public void GetColumnFrequency_Zero_ForAbsent_Value()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.Equal(0, doc.GetColumnFrequency("ward", "NonExistentWard_XYZ"));
    }

    // -------------------------------------------------------------------------
    // GetColumnUniqueRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniqueRatio_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        var ex = Record.Exception(() => doc.GetColumnUniqueRatio("blood_group"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniqueRatio_InRange()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        var ratio = doc.GetColumnUniqueRatio("ward");
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
    }

    [Fact]
    public void GetColumnUniqueRatio_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        Assert.Equal(doc.GetColumnUniqueRatio("admission_type"), doc.GetColumnUniqueRatio("admission_type"));
    }

    [Fact]
    public void GetColumnUniqueRatio_One_ForAllUnique()
    {
        var doc = CsvDocument.LoadFile(CreateUniqueRefCsv());
        Assert.Equal(1.0, doc.GetColumnUniqueRatio("ref_code"), precision: 6);
    }

    [Fact]
    public void GetColumnUniqueRatio_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreatePatientCsv());
        var before = doc.GetColumnUniqueRatio("blood_group");
        var path = TempFile("ur_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnUniqueRatio("blood_group"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnFrequency_GetColumnUniqueRatio_Pipeline()
    {
        // UK planning authority — development application classification and decision data
        var path = TempFile("planning_applications.csv");
        var csvLines = new System.Collections.Generic.List<string>();
        csvLines.Add("app_ref,lpa_code,app_type,decision,decision_date,floor_area_sqm,housing_units,officer_grade");
        var rng = new Random(20240901);
        string[] lpas = { "LPA_001", "LPA_002", "LPA_003", "LPA_004", "LPA_005" };
        string[] types = { "Full_PP", "Outline_PP", "LDC", "PriorApproval", "Advertisement" };
        string[] decisions = { "Granted", "Refused", "Withdrawn", "Appeal_Allowed", "Appeal_Dismissed" };
        string[] grades = { "Principal_Officer", "Senior_Officer", "Development_Manager" };
        for (int i = 0; i < 120; i++)
        {
            var lpa = lpas[i % 5];
            var tp = types[i % 5];
            // Full_PP most common; Granted most common decision
            var dec = (rng.NextDouble() < 0.55) ? "Granted" :
                      (rng.NextDouble() < 0.25) ? "Refused" : decisions[i % 5];
            var grade = grades[i % 3];
            double area = 50 + rng.NextDouble() * 500;
            int units = (tp == "Full_PP") ? rng.Next(1, 20) : 0;
            csvLines.Add($"APP{i:D5}/{(2024 + i % 2)},{lpa},{tp},{dec},2024-{(i % 12 + 1):D2}-15,{area:F0},{units},{grade}");
        }
        File.WriteAllLines(path, csvLines);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnMode — most common app type and decision
        var modeType = doc.GetColumnMode("app_type");
        Assert.NotNull(modeType);
        Assert.Equal(modeType, doc.GetColumnMode("app_type")); // consistent

        var modeDec = doc.GetColumnMode("decision");
        Assert.NotNull(modeDec);

        // GetColumnFrequency
        var grantedCount = doc.GetColumnFrequency("decision", "Granted");
        Assert.True(grantedCount >= 0);
        Assert.Equal(grantedCount, doc.GetColumnFrequency("decision", "Granted")); // consistent

        var lpa1Count = doc.GetColumnFrequency("lpa_code", "LPA_001");
        Assert.True(lpa1Count >= 0);

        var absentCount = doc.GetColumnFrequency("decision", "Decision_Does_Not_Exist");
        Assert.Equal(0, absentCount);

        // GetColumnUniqueRatio — app_ref should be unique; lpa_code should be ~5/120
        var refRatio = doc.GetColumnUniqueRatio("app_ref");
        Assert.Equal(1.0, refRatio, precision: 6);

        var lpaRatio = doc.GetColumnUniqueRatio("lpa_code");
        Assert.True(lpaRatio > 0 && lpaRatio <= 1.0);
        Assert.Equal(lpaRatio, doc.GetColumnUniqueRatio("lpa_code")); // consistent

        // All categorical columns
        foreach (var col in new[] { "app_type", "decision", "lpa_code", "officer_grade" })
        {
            Assert.NotNull(doc.GetColumnMode(col));
            Assert.Equal(0, doc.GetColumnFrequency(col, "NONEXISTENT"));
            var ratio = doc.GetColumnUniqueRatio(col);
            Assert.True(ratio >= 0 && ratio <= 1.0);
        }

        // SaveToFile
        var outPath = TempFile("planning_apps_out.csv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(outPath);
        Assert.Equal(modeType, loaded.GetColumnMode("app_type"));
        Assert.Equal(grantedCount, loaded.GetColumnFrequency("decision", "Granted"));
        Assert.Equal(refRatio, loaded.GetColumnUniqueRatio("app_ref"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean for numeric column
        var meanArea = doc.GetColumnMean("floor_area_sqm");
        Assert.True(meanArea >= 0);
    }
}
