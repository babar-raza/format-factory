// Tests for NdjsonDocument.GetFieldUniqueValues, GetFieldValueFrequency, GetFieldModeValue deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R253

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R253: Tests for NdjsonDocument.GetFieldUniqueValues, GetFieldValueFrequency, GetFieldModeValue deeper.
/// GetFieldUniqueValues(fieldName): returns a list of distinct values found in the field.
/// GetFieldValueFrequency(fieldName, value): returns how many records have the given field value.
/// GetFieldModeValue(fieldName): returns the most frequently occurring value in the field.
/// Covers: GetFieldUniqueValues no-throw; GetFieldUniqueValues non-null; GetFieldUniqueValues consistent;
/// GetFieldUniqueValues count ≤ RecordCount;
/// GetFieldValueFrequency no-throw; GetFieldValueFrequency non-negative; GetFieldValueFrequency consistent;
/// GetFieldValueFrequency zero for absent value;
/// GetFieldModeValue no-throw; GetFieldModeValue non-null; GetFieldModeValue consistent;
/// GetFieldModeValue save-load;
/// dogfood CreateDoc→GetFieldUniqueValues→GetFieldValueFrequency→GetFieldModeValue pipeline.
/// </summary>
public class NdjsonR253GetFieldUniqueValuesAndValueFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR253GetFieldUniqueValuesAndValueFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR253_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductNdjson()
    {
        var path = TempFile("products.ndjson");
        var lines = new System.Collections.Generic.List<string>
        {
            "{\"sku\":\"P001\",\"category\":\"Electronics\",\"brand\":\"Alpha\",\"rating\":4,\"in_stock\":true}",
            "{\"sku\":\"P002\",\"category\":\"Clothing\",\"brand\":\"Beta\",\"rating\":5,\"in_stock\":true}",
            "{\"sku\":\"P003\",\"category\":\"Electronics\",\"brand\":\"Gamma\",\"rating\":3,\"in_stock\":false}",
            "{\"sku\":\"P004\",\"category\":\"Books\",\"brand\":\"Alpha\",\"rating\":5,\"in_stock\":true}",
            "{\"sku\":\"P005\",\"category\":\"Electronics\",\"brand\":\"Beta\",\"rating\":4,\"in_stock\":true}",
            "{\"sku\":\"P006\",\"category\":\"Clothing\",\"brand\":\"Alpha\",\"rating\":2,\"in_stock\":false}",
            "{\"sku\":\"P007\",\"category\":\"Books\",\"brand\":\"Gamma\",\"rating\":5,\"in_stock\":true}",
            "{\"sku\":\"P008\",\"category\":\"Electronics\",\"brand\":\"Alpha\",\"rating\":4,\"in_stock\":true}",
            "{\"sku\":\"P009\",\"category\":\"Books\",\"brand\":\"Beta\",\"rating\":3,\"in_stock\":true}",
            "{\"sku\":\"P010\",\"category\":\"Clothing\",\"brand\":\"Gamma\",\"rating\":4,\"in_stock\":false}",
            "{\"sku\":\"P011\",\"category\":\"Electronics\",\"brand\":\"Alpha\",\"rating\":5,\"in_stock\":true}",
            "{\"sku\":\"P012\",\"category\":\"Books\",\"brand\":\"Beta\",\"rating\":4,\"in_stock\":true}",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldUniqueValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldUniqueValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldUniqueValues("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldUniqueValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.GetFieldUniqueValues("category"));
    }

    [Fact]
    public void GetFieldUniqueValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.GetFieldUniqueValues("category").Count,
                     doc.GetFieldUniqueValues("category").Count);
    }

    [Fact]
    public void GetFieldUniqueValues_Count_LessOrEqual_RecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var unique = doc.GetFieldUniqueValues("category");
        Assert.True(unique.Count <= doc.RecordCount);
    }

    // -------------------------------------------------------------------------
    // GetFieldValueFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldValueFrequency_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldValueFrequency("category", "Electronics"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldValueFrequency_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(doc.GetFieldValueFrequency("category", "Electronics") >= 0);
    }

    [Fact]
    public void GetFieldValueFrequency_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(
            doc.GetFieldValueFrequency("brand", "Alpha"),
            doc.GetFieldValueFrequency("brand", "Alpha"));
    }

    [Fact]
    public void GetFieldValueFrequency_Zero_For_Absent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(0, doc.GetFieldValueFrequency("category", "Jewellery"));
    }

    // -------------------------------------------------------------------------
    // GetFieldModeValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldModeValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldModeValue("category"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldModeValue_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.NotNull(doc.GetFieldModeValue("category"));
    }

    [Fact]
    public void GetFieldModeValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.GetFieldModeValue("brand"), doc.GetFieldModeValue("brand"));
    }

    [Fact]
    public void GetFieldModeValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.GetFieldModeValue("category");
        var path = TempFile("mode_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldModeValue("category"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldUniqueValues_GetFieldValueFrequency_GetFieldModeValue_Pipeline()
    {
        // UK Higher Education — UCAS application data for course popularity analysis
        var path = TempFile("ucas_applications.ndjson");
        var lines = new System.Collections.Generic.List<string>();
        var rng = new Random(20240901);
        string[] subjects = { "Computer_Science", "Medicine", "Law", "Economics", "Engineering", "Psychology" };
        string[] universities = { "Oxford", "Cambridge", "Imperial", "UCL", "LSE", "Manchester" };
        string[] grades = { "AAA", "AAB", "ABB", "BBB", "BBC", "BCC" };
        for (int i = 0; i < 150; i++)
        {
            // Computer Science and Medicine are most popular
            string subject = i < 40 ? "Computer_Science" :
                             i < 70 ? "Medicine" :
                             subjects[rng.Next(2, 6)];
            string university = universities[rng.Next(6)];
            string grade = grades[rng.Next(6)];
            int year = 2021 + rng.Next(4);
            int offer = rng.NextDouble() < 0.65 ? 1 : 0;
            lines.Add($"{{\"application_id\":\"APP{i:D5}\",\"subject\":\"{subject}\",\"university\":\"{university}\",\"predicted_grades\":\"{grade}\",\"year\":{year},\"offer_made\":{offer.ToString().ToLower()}}}");
        }
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(150, doc.RecordCount);

        // GetFieldUniqueValues — subjects
        var uniqueSubjects = doc.GetFieldUniqueValues("subject");
        Assert.NotNull(uniqueSubjects);
        Assert.True(uniqueSubjects.Count > 0);
        Assert.True(uniqueSubjects.Count <= doc.RecordCount);
        Assert.Equal(uniqueSubjects.Count, doc.GetFieldUniqueValues("subject").Count); // consistent

        // GetFieldUniqueValues — universities
        var uniqueUnis = doc.GetFieldUniqueValues("university");
        Assert.NotNull(uniqueUnis);
        Assert.True(uniqueUnis.Count > 0);

        // GetFieldValueFrequency — Computer Science (should be highest)
        var csFreq = doc.GetFieldValueFrequency("subject", "Computer_Science");
        Assert.True(csFreq >= 0);
        Assert.Equal(csFreq, doc.GetFieldValueFrequency("subject", "Computer_Science")); // consistent

        // GetFieldValueFrequency — Medicine
        var medFreq = doc.GetFieldValueFrequency("subject", "Medicine");
        Assert.True(medFreq >= 0);

        // GetFieldValueFrequency — absent value
        Assert.Equal(0, doc.GetFieldValueFrequency("subject", "Astrophysics"));

        // GetFieldValueFrequency — all frequencies should sum to record count
        int totalFreq = 0;
        foreach (var s in uniqueSubjects)
            totalFreq += doc.GetFieldValueFrequency("subject", s.ToString());
        Assert.Equal(doc.RecordCount, totalFreq);

        // GetFieldModeValue — subject (expect Computer_Science or Medicine)
        var modeSubject = doc.GetFieldModeValue("subject");
        Assert.NotNull(modeSubject);
        Assert.Equal(modeSubject, doc.GetFieldModeValue("subject")); // consistent

        // GetFieldModeValue — university and predicted_grades
        var modeUni = doc.GetFieldModeValue("university");
        Assert.NotNull(modeUni);
        var modeGrade = doc.GetFieldModeValue("predicted_grades");
        Assert.NotNull(modeGrade);

        // SaveToFile
        var outPath = TempFile("ucas_applications_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(uniqueSubjects.Count, loaded.GetFieldUniqueValues("subject").Count);
        Assert.Equal(csFreq, loaded.GetFieldValueFrequency("subject", "Computer_Science"));
        Assert.Equal(modeSubject, loaded.GetFieldModeValue("subject"));
        Assert.Equal(doc.RecordCount, loaded.RecordCount);

        // Additional stats
        var meanYear = doc.GetFieldMean("year");
        Assert.True(meanYear >= 2021 && meanYear <= 2024);
        var uniqueYears = doc.GetFieldUniqueValues("year");
        Assert.True(uniqueYears.Count > 0 && uniqueYears.Count <= 4);
    }
}
