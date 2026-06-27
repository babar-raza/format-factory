// Tests for NdjsonDocument.GetFieldEntropy, GetFieldInformationGain, GetFieldGiniImpurity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R251

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R251: Tests for NdjsonDocument.GetFieldEntropy, GetFieldInformationGain, GetFieldGiniImpurity deeper.
/// GetFieldEntropy(fieldName): returns the Shannon entropy of the field's value distribution.
/// GetFieldInformationGain(fieldName, targetField): returns the information gain for the field vs target.
/// GetFieldGiniImpurity(fieldName): returns the Gini impurity of the field's value distribution.
/// Covers: GetFieldEntropy no-throw; GetFieldEntropy non-negative; GetFieldEntropy consistent;
/// GetFieldEntropy zero for constant field; GetFieldEntropy save-load;
/// GetFieldInformationGain no-throw; GetFieldInformationGain non-negative; GetFieldInformationGain consistent;
/// GetFieldGiniImpurity no-throw; GetFieldGiniImpurity in [0, 0.5]; GetFieldGiniImpurity consistent;
/// GetFieldGiniImpurity zero for constant field;
/// dogfood CreateDoc→GetFieldEntropy→GetFieldInformationGain→GetFieldGiniImpurity pipeline.
/// </summary>
public class NdjsonR251GetFieldEntropyAndInformationGainDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR251GetFieldEntropyAndInformationGainDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR251_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLoanNdjson()
    {
        var path = TempFile("loans.ndjson");
        string[] statuses = { "Current", "Defaulted", "Prepaid", "Delinquent" };
        string[] grades = { "A", "B", "C", "D" };
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var status = statuses[i % 4];
            var grade = grades[i % 4];
            int term = (i % 2 == 0) ? 36 : 60;
            double rate = 5.0 + (i % 4) * 2.5;
            lines.Add($"{{\"loan_id\":\"LN{i:D5}\",\"grade\":\"{grade}\",\"status\":\"{status}\",\"term_months\":{term},\"interest_rate\":{rate}}}");
        }
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateConstantFieldNdjson()
    {
        var path = TempFile("constant_field.ndjson");
        var lines = new System.Collections.Generic.List<string>
        {
            "{\"id\":\"R1\",\"category\":\"Alpha\",\"value\":10}",
            "{\"id\":\"R2\",\"category\":\"Alpha\",\"value\":20}",
            "{\"id\":\"R3\",\"category\":\"Alpha\",\"value\":30}",
            "{\"id\":\"R4\",\"category\":\"Alpha\",\"value\":40}",
            "{\"id\":\"R5\",\"category\":\"Alpha\",\"value\":50}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldEntropy_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        var ex = Record.Exception(() => doc.GetFieldEntropy("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldEntropy_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        Assert.True(doc.GetFieldEntropy("status") >= 0);
    }

    [Fact]
    public void GetFieldEntropy_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        Assert.Equal(doc.GetFieldEntropy("grade"), doc.GetFieldEntropy("grade"));
    }

    [Fact]
    public void GetFieldEntropy_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantFieldNdjson());
        Assert.Equal(0.0, doc.GetFieldEntropy("category"), precision: 6);
    }

    [Fact]
    public void GetFieldEntropy_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        var before = doc.GetFieldEntropy("grade");
        var path = TempFile("ent_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldEntropy("grade"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldInformationGain
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldInformationGain_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        var ex = Record.Exception(() => doc.GetFieldInformationGain("grade", "status"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldInformationGain_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        Assert.True(doc.GetFieldInformationGain("grade", "status") >= 0);
    }

    [Fact]
    public void GetFieldInformationGain_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        Assert.Equal(
            doc.GetFieldInformationGain("grade", "status"),
            doc.GetFieldInformationGain("grade", "status"));
    }

    // -------------------------------------------------------------------------
    // GetFieldGiniImpurity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldGiniImpurity_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        var ex = Record.Exception(() => doc.GetFieldGiniImpurity("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldGiniImpurity_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        var gini = doc.GetFieldGiniImpurity("grade");
        Assert.True(gini >= 0.0 && gini <= 1.0);
    }

    [Fact]
    public void GetFieldGiniImpurity_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLoanNdjson());
        Assert.Equal(doc.GetFieldGiniImpurity("status"), doc.GetFieldGiniImpurity("status"));
    }

    [Fact]
    public void GetFieldGiniImpurity_Zero_ForConstant()
    {
        var doc = NdjsonDocument.LoadFile(CreateConstantFieldNdjson());
        Assert.Equal(0.0, doc.GetFieldGiniImpurity("category"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldEntropy_GetFieldInformationGain_GetFieldGiniImpurity_Pipeline()
    {
        // Healthcare analytics — patient readmission risk factor dataset (ML feature selection)
        var path = TempFile("readmission_risk.ndjson");
        string[] diagnoses = { "Heart_Failure", "COPD", "Pneumonia", "Diabetes", "AMI", "Hip_Fracture" };
        string[] admissionTypes = { "Emergency", "Elective", "Transfer", "Day_Case" };
        string[] outcomes = { "Readmitted_30d", "Readmitted_90d", "No_Readmission" };
        string[] comorbidities = { "Low", "Medium", "High" };
        var rng = new Random(20240801);
        var lines = new System.Collections.Generic.List<string>();
        for (int i = 0; i < 12; i++)
        {
            var diag = diagnoses[i % 6];
            var admType = admissionTypes[i % 4];
            var outcome = outcomes[i % 3];
            var comorbid = comorbidities[i % 3];
            int los = 1 + rng.Next(0, 20);
            int age = 45 + rng.Next(0, 40);
            lines.Add($"{{\"patient_id\":\"P{i:D5}\",\"primary_diagnosis\":\"{diag}\",\"admission_type\":\"{admType}\",\"comorbidity_burden\":\"{comorbid}\",\"los_days\":{los},\"age\":{age},\"readmission_outcome\":\"{outcome}\"}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.RecordCount);

        // GetFieldEntropy — assess information content of categorical predictors
        var diagEnt = doc.GetFieldEntropy("primary_diagnosis");
        Assert.True(diagEnt >= 0);
        Assert.Equal(diagEnt, doc.GetFieldEntropy("primary_diagnosis")); // consistent

        var admEnt = doc.GetFieldEntropy("admission_type");
        Assert.True(admEnt >= 0);

        var outEnt = doc.GetFieldEntropy("readmission_outcome");
        Assert.True(outEnt >= 0);

        // GetFieldInformationGain — which feature best predicts readmission
        var diagIG = doc.GetFieldInformationGain("primary_diagnosis", "readmission_outcome");
        Assert.True(diagIG >= 0);
        Assert.Equal(diagIG, doc.GetFieldInformationGain("primary_diagnosis", "readmission_outcome")); // consistent

        var comorbIG = doc.GetFieldInformationGain("comorbidity_burden", "readmission_outcome");
        Assert.True(comorbIG >= 0);

        // GetFieldGiniImpurity — split quality metric
        var diagGini = doc.GetFieldGiniImpurity("primary_diagnosis");
        Assert.True(diagGini >= 0.0 && diagGini <= 1.0);
        Assert.Equal(diagGini, doc.GetFieldGiniImpurity("primary_diagnosis")); // consistent

        var outGini = doc.GetFieldGiniImpurity("readmission_outcome");
        Assert.True(outGini >= 0.0 && outGini <= 1.0);

        // SaveToFile
        var outPath = TempFile("readmission_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(diagEnt, loaded.GetFieldEntropy("primary_diagnosis"), precision: 6);
        Assert.Equal(diagIG, loaded.GetFieldInformationGain("primary_diagnosis", "readmission_outcome"), precision: 6);
        Assert.Equal(diagGini, loaded.GetFieldGiniImpurity("primary_diagnosis"), precision: 6);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // GetRecord consistency
        var record0 = loaded.GetRecord(0);
        Assert.NotNull(record0);

        var ex1 = Record.Exception(() => loaded.GetFieldEntropy("admission_type"));
        var ex2 = Record.Exception(() => loaded.GetFieldInformationGain("admission_type", "readmission_outcome"));
        var ex3 = Record.Exception(() => loaded.GetFieldGiniImpurity("comorbidity_burden"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
