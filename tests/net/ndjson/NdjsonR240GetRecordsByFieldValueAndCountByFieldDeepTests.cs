// Tests for NdjsonDocument.GetRecordsByFieldValue, CountByFieldValue, GetDistinctFieldValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R240

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R240: Tests for NdjsonDocument.GetRecordsByFieldValue, CountByFieldValue, GetDistinctFieldValues deeper.
/// GetRecordsByFieldValue(fieldName, value): returns records where the field equals the value.
/// CountByFieldValue(fieldName, value): returns the count of records where the field equals the value.
/// GetDistinctFieldValues(fieldName): returns the list of unique values for the field.
/// Covers: GetRecordsByFieldValue no-throw; GetRecordsByFieldValue count leq total; GetRecordsByFieldValue consistent;
/// GetRecordsByFieldValue empty for non-existing value; GetRecordsByFieldValue save-load;
/// CountByFieldValue no-throw; CountByFieldValue non-negative; CountByFieldValue consistent;
/// CountByFieldValue zero for non-existing value; CountByFieldValue save-load;
/// GetDistinctFieldValues no-throw; GetDistinctFieldValues count leq record count; GetDistinctFieldValues consistent;
/// GetDistinctFieldValues save-load;
/// dogfood CreateDoc→GetRecordsByFieldValue→CountByFieldValue→GetDistinctFieldValues→SaveToFile pipeline.
/// </summary>
public class NdjsonR240GetRecordsByFieldValueAndCountByFieldDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR240GetRecordsByFieldValueAndCountByFieldDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR240_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHrNdjson()
    {
        var path = TempFile("hr.ndjson");
        File.WriteAllText(path,
            "{\"emp_id\":\"E001\",\"department\":\"Engineering\",\"grade\":\"L4\",\"salary\":95000,\"location\":\"NYC\"}\n" +
            "{\"emp_id\":\"E002\",\"department\":\"Marketing\",\"grade\":\"L3\",\"salary\":72000,\"location\":\"SF\"}\n" +
            "{\"emp_id\":\"E003\",\"department\":\"Engineering\",\"grade\":\"L5\",\"salary\":125000,\"location\":\"NYC\"}\n" +
            "{\"emp_id\":\"E004\",\"department\":\"Finance\",\"grade\":\"L4\",\"salary\":88000,\"location\":\"CHI\"}\n" +
            "{\"emp_id\":\"E005\",\"department\":\"Engineering\",\"grade\":\"L3\",\"salary\":78000,\"location\":\"SF\"}\n" +
            "{\"emp_id\":\"E006\",\"department\":\"Marketing\",\"grade\":\"L5\",\"salary\":105000,\"location\":\"NYC\"}\n" +
            "{\"emp_id\":\"E007\",\"department\":\"Finance\",\"grade\":\"L3\",\"salary\":65000,\"location\":\"CHI\"}\n" +
            "{\"emp_id\":\"E008\",\"department\":\"Engineering\",\"grade\":\"L6\",\"salary\":162000,\"location\":\"NYC\"}\n" +
            "{\"emp_id\":\"E009\",\"department\":\"HR\",\"grade\":\"L3\",\"salary\":68000,\"location\":\"SF\"}\n" +
            "{\"emp_id\":\"E010\",\"department\":\"Engineering\",\"grade\":\"L4\",\"salary\":98000,\"location\":\"CHI\"}\n" +
            "{\"emp_id\":\"E011\",\"department\":\"Marketing\",\"grade\":\"L4\",\"salary\":82000,\"location\":\"NYC\"}\n" +
            "{\"emp_id\":\"E012\",\"department\":\"HR\",\"grade\":\"L5\",\"salary\":92000,\"location\":\"SF\"}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetRecordsByFieldValue
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRecordsByFieldValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var ex = Record.Exception(() => doc.GetRecordsByFieldValue("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetRecordsByFieldValue_Count_LeqTotal()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.True(doc.GetRecordsByFieldValue("department", "Engineering").Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetRecordsByFieldValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var r1 = doc.GetRecordsByFieldValue("grade", "L4").Count;
        var r2 = doc.GetRecordsByFieldValue("grade", "L4").Count;
        Assert.Equal(r1, r2);
    }

    [Fact]
    public void GetRecordsByFieldValue_Empty_ForNonExistingValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.Equal(0, doc.GetRecordsByFieldValue("department", "LegalDept").Count);
    }

    [Fact]
    public void GetRecordsByFieldValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var before = doc.GetRecordsByFieldValue("location", "NYC").Count;
        var path = TempFile("rfv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordsByFieldValue("location", "NYC").Count);
    }

    // -------------------------------------------------------------------------
    // CountByFieldValue
    // -------------------------------------------------------------------------

    [Fact]
    public void CountByFieldValue_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var ex = Record.Exception(() => doc.CountByFieldValue("department", "Engineering"));
        Assert.Null(ex);
    }

    [Fact]
    public void CountByFieldValue_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.True(doc.CountByFieldValue("grade", "L3") >= 0);
    }

    [Fact]
    public void CountByFieldValue_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.Equal(doc.CountByFieldValue("location", "SF"), doc.CountByFieldValue("location", "SF"));
    }

    [Fact]
    public void CountByFieldValue_Zero_ForNonExistingValue()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.Equal(0, doc.CountByFieldValue("department", "Research"));
    }

    [Fact]
    public void CountByFieldValue_Matches_GetRecordsByFieldValue_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var count = doc.CountByFieldValue("department", "Finance");
        var records = doc.GetRecordsByFieldValue("department", "Finance");
        Assert.Equal(records.Count, count);
    }

    [Fact]
    public void CountByFieldValue_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var before = doc.CountByFieldValue("grade", "L4");
        var path = TempFile("cbf_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.CountByFieldValue("grade", "L4"));
    }

    // -------------------------------------------------------------------------
    // GetDistinctFieldValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctFieldValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var ex = Record.Exception(() => doc.GetDistinctFieldValues("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctFieldValues_Count_LeqRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.True(doc.GetDistinctFieldValues("department").Count <= doc.GetRecordCount());
    }

    [Fact]
    public void GetDistinctFieldValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        Assert.Equal(doc.GetDistinctFieldValues("grade").Count, doc.GetDistinctFieldValues("grade").Count);
    }

    [Fact]
    public void GetDistinctFieldValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateHrNdjson());
        var before = doc.GetDistinctFieldValues("location").Count;
        var path = TempFile("dfv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctFieldValues("location").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetRecordsByFieldValue_CountByFieldValue_GetDistinctFieldValues_SaveToFile_Pipeline()
    {
        // Academic research publication dataset — 12 papers across 4 journals
        var path = TempFile("dogfood_publications.ndjson");
        File.WriteAllText(path,
            "{\"paper_id\":\"P001\",\"journal\":\"Nature\",\"field\":\"Biology\",\"citations\":1842,\"year\":2022,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P002\",\"journal\":\"Science\",\"field\":\"Physics\",\"citations\":956,\"year\":2023,\"open_access\":\"no\"}\n" +
            "{\"paper_id\":\"P003\",\"journal\":\"Cell\",\"field\":\"Biology\",\"citations\":2145,\"year\":2021,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P004\",\"journal\":\"Nature\",\"field\":\"Chemistry\",\"citations\":784,\"year\":2023,\"open_access\":\"no\"}\n" +
            "{\"paper_id\":\"P005\",\"journal\":\"PNAS\",\"field\":\"Biology\",\"citations\":542,\"year\":2024,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P006\",\"journal\":\"Science\",\"field\":\"Biology\",\"citations\":1256,\"year\":2022,\"open_access\":\"no\"}\n" +
            "{\"paper_id\":\"P007\",\"journal\":\"Cell\",\"field\":\"Biochemistry\",\"citations\":3012,\"year\":2020,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P008\",\"journal\":\"Nature\",\"field\":\"Physics\",\"citations\":2890,\"year\":2021,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P009\",\"journal\":\"PNAS\",\"field\":\"Chemistry\",\"citations\":412,\"year\":2024,\"open_access\":\"no\"}\n" +
            "{\"paper_id\":\"P010\",\"journal\":\"Science\",\"field\":\"Biochemistry\",\"citations\":1645,\"year\":2022,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P011\",\"journal\":\"Nature\",\"field\":\"Biology\",\"citations\":895,\"year\":2023,\"open_access\":\"yes\"}\n" +
            "{\"paper_id\":\"P012\",\"journal\":\"PNAS\",\"field\":\"Physics\",\"citations\":328,\"year\":2024,\"open_access\":\"no\"}\n");

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetRecordsByFieldValue — by journal
        var naturePapers = doc.GetRecordsByFieldValue("journal", "Nature");
        Assert.Equal(4, naturePapers.Count);

        var sciencePapers = doc.GetRecordsByFieldValue("journal", "Science");
        Assert.Equal(3, sciencePapers.Count);

        var cellPapers = doc.GetRecordsByFieldValue("journal", "Cell");
        Assert.Equal(2, cellPapers.Count);

        // Non-existing value
        var lancetPapers = doc.GetRecordsByFieldValue("journal", "Lancet");
        Assert.Equal(0, lancetPapers.Count);

        // Consistent
        Assert.Equal(naturePapers.Count, doc.GetRecordsByFieldValue("journal", "Nature").Count);

        // GetRecordsByFieldValue — by field
        var bioPapers = doc.GetRecordsByFieldValue("field", "Biology");
        Assert.True(bioPapers.Count > 0);

        // GetRecordsByFieldValue — by open access
        var oaPapers = doc.GetRecordsByFieldValue("open_access", "yes");
        Assert.True(oaPapers.Count > 0);

        // CountByFieldValue — verify matches GetRecordsByFieldValue
        Assert.Equal(naturePapers.Count, doc.CountByFieldValue("journal", "Nature"));
        Assert.Equal(bioPapers.Count, doc.CountByFieldValue("field", "Biology"));
        Assert.Equal(oaPapers.Count, doc.CountByFieldValue("open_access", "yes"));

        // Non-existing count
        Assert.Equal(0, doc.CountByFieldValue("journal", "NEJM"));

        // Total counts across all journals should equal record count
        var countNature = doc.CountByFieldValue("journal", "Nature");
        var countScience = doc.CountByFieldValue("journal", "Science");
        var countCell = doc.CountByFieldValue("journal", "Cell");
        var countPnas = doc.CountByFieldValue("journal", "PNAS");
        Assert.Equal(12, countNature + countScience + countCell + countPnas);

        // GetDistinctFieldValues — journals
        var journals = doc.GetDistinctFieldValues("journal");
        Assert.Equal(4, journals.Count); // Nature, Science, Cell, PNAS
        Assert.True(journals.Count <= doc.GetRecordCount());

        // GetDistinctFieldValues — fields (Biology, Physics, Chemistry, Biochemistry)
        var fields = doc.GetDistinctFieldValues("field");
        Assert.Equal(4, fields.Count);

        // GetDistinctFieldValues — open_access (yes, no)
        var oaValues = doc.GetDistinctFieldValues("open_access");
        Assert.Equal(2, oaValues.Count);

        // Consistent
        Assert.Equal(journals.Count, doc.GetDistinctFieldValues("journal").Count);

        // SaveToFile
        var out1 = TempFile("dogfood_publications_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(naturePapers.Count, loaded.GetRecordsByFieldValue("journal", "Nature").Count);
        Assert.Equal(countNature, loaded.CountByFieldValue("journal", "Nature"));
        Assert.Equal(journals.Count, loaded.GetDistinctFieldValues("journal").Count);

        // AddRecord — new paper
        loaded.AddRecord("{\"paper_id\":\"P013\",\"journal\":\"Nature\",\"field\":\"Genomics\",\"citations\":142,\"year\":2025,\"open_access\":\"yes\"}");
        Assert.Equal(13, loaded.GetRecordCount());

        // Nature count increases
        Assert.Equal(countNature + 1, loaded.CountByFieldValue("journal", "Nature"));

        // Field count increases (Genomics is new)
        var newFields = loaded.GetDistinctFieldValues("field");
        Assert.Equal(5, newFields.Count); // +Genomics

        // Final save
        var out2 = TempFile("dogfood_publications_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.True(loaded2.GetDistinctFieldValues("journal").Count >= 4);
        Assert.True(loaded2.CountByFieldValue("open_access", "yes") > 0);
        var ex1 = Record.Exception(() => loaded2.GetRecordsByFieldValue("field", "Biology"));
        Assert.Null(ex1);
    }
}
