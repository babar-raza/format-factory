// Tests for NdjsonDocument.GetMissingFieldCount, FillMissingValues, GetFieldCoverage deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R235

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R235: Tests for NdjsonDocument.GetMissingFieldCount, FillMissingValues, GetFieldCoverage deeper.
/// GetMissingFieldCount(fieldName): returns the number of records missing the specified field.
/// FillMissingValues(fieldName, defaultValue): returns a new doc with missing field values filled.
/// GetFieldCoverage(fieldName): returns the fraction of records that contain the specified field.
/// Covers: GetMissingFieldCount no-throw; GetMissingFieldCount non-negative; GetMissingFieldCount consistent;
/// GetMissingFieldCount zero for universal field; GetMissingFieldCount save-load;
/// FillMissingValues no-throw; FillMissingValues non-null; FillMissingValues record count unchanged;
/// FillMissingValues consistent; FillMissingValues save-load;
/// GetFieldCoverage no-throw; GetFieldCoverage in [0,1]; GetFieldCoverage consistent;
/// GetFieldCoverage one for universal field; GetFieldCoverage save-load;
/// dogfood CreateDoc→GetMissingFieldCount→FillMissingValues→GetFieldCoverage→SaveToFile pipeline.
/// </summary>
public class NdjsonR235GetMissingFieldCountAndFillMissingDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR235GetMissingFieldCountAndFillMissingDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR235_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSparseNdjson()
    {
        var path = TempFile("sparse.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":1,\"name\":\"Alice\",\"email\":\"alice@example.com\",\"phone\":\"+44-20-1234-5678\",\"score\":92}",
            "{\"id\":2,\"name\":\"Bob\",\"email\":\"bob@example.com\",\"score\":78}",
            "{\"id\":3,\"name\":\"Carol\",\"email\":\"carol@example.com\",\"phone\":\"+44-20-2345-6789\",\"score\":85}",
            "{\"id\":4,\"name\":\"David\",\"score\":91}",
            "{\"id\":5,\"name\":\"Emma\",\"email\":\"emma@example.com\",\"phone\":\"+44-20-3456-7890\",\"score\":74}",
            "{\"id\":6,\"name\":\"Frank\",\"phone\":\"+44-20-4567-8901\",\"score\":88}",
            "{\"id\":7,\"name\":\"Grace\",\"email\":\"grace@example.com\",\"score\":95}",
            "{\"id\":8,\"name\":\"Henry\",\"email\":\"henry@example.com\",\"phone\":\"+44-20-5678-9012\",\"score\":67}",
        });
        return path;
    }

    private string CreateConsistentNdjson()
    {
        var path = TempFile("consistent.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":\"A1\",\"value\":10.5,\"label\":\"alpha\"}",
            "{\"id\":\"A2\",\"value\":20.1,\"label\":\"beta\"}",
            "{\"id\":\"A3\",\"value\":15.8,\"label\":\"gamma\"}",
            "{\"id\":\"A4\",\"value\":25.4,\"label\":\"delta\"}",
            "{\"id\":\"A5\",\"value\":18.9,\"label\":\"epsilon\"}",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMissingFieldCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMissingFieldCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var ex = Record.Exception(() => doc.GetMissingFieldCount("phone"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetMissingFieldCount_NonNegative()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        Assert.True(doc.GetMissingFieldCount("phone") >= 0);
    }

    [Fact]
    public void GetMissingFieldCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        Assert.Equal(doc.GetMissingFieldCount("email"), doc.GetMissingFieldCount("email"));
    }

    [Fact]
    public void GetMissingFieldCount_Zero_ForUniversalField()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        // All records have "id" and "name"
        Assert.Equal(0, doc.GetMissingFieldCount("id"));
        Assert.Equal(0, doc.GetMissingFieldCount("name"));
    }

    [Fact]
    public void GetMissingFieldCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var before = doc.GetMissingFieldCount("phone");
        var path = TempFile("mfc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMissingFieldCount("phone"));
    }

    // -------------------------------------------------------------------------
    // FillMissingValues
    // -------------------------------------------------------------------------

    [Fact]
    public void FillMissingValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var ex = Record.Exception(() => doc.FillMissingValues("phone", "N/A"));
        Assert.Null(ex);
    }

    [Fact]
    public void FillMissingValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        Assert.NotNull(doc.FillMissingValues("email", "unknown@example.com"));
    }

    [Fact]
    public void FillMissingValues_RecordCount_Unchanged()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var before = doc.GetRecordCount();
        var filled = doc.FillMissingValues("phone", "N/A");
        Assert.Equal(before, filled.GetRecordCount());
    }

    [Fact]
    public void FillMissingValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var f1 = doc.FillMissingValues("email", "default@example.com");
        var f2 = doc.FillMissingValues("email", "default@example.com");
        Assert.Equal(f1.GetRecordCount(), f2.GetRecordCount());
    }

    [Fact]
    public void FillMissingValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var filled = doc.FillMissingValues("phone", "N/A");
        var path = TempFile("fmv_save.ndjson");
        filled.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(filled.GetRecordCount(), loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GetFieldCoverage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCoverage_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var ex = Record.Exception(() => doc.GetFieldCoverage("phone"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCoverage_InRange()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var coverage = doc.GetFieldCoverage("phone");
        Assert.True(coverage >= 0.0 && coverage <= 1.0);
    }

    [Fact]
    public void GetFieldCoverage_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        Assert.Equal(doc.GetFieldCoverage("email"), doc.GetFieldCoverage("email"));
    }

    [Fact]
    public void GetFieldCoverage_One_ForUniversalField()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        Assert.Equal(1.0, doc.GetFieldCoverage("id"), precision: 6);
        Assert.Equal(1.0, doc.GetFieldCoverage("score"), precision: 6);
    }

    [Fact]
    public void GetFieldCoverage_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSparseNdjson());
        var before = doc.GetFieldCoverage("phone");
        var path = TempFile("gfc_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldCoverage("phone"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMissingFieldCount_FillMissingValues_GetFieldCoverage_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_survey.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"respondent_id\":\"R001\",\"age\":34,\"gender\":\"Female\",\"region\":\"London\",\"income_band\":\"40-60k\",\"satisfaction\":8,\"nps\":9,\"comments\":\"Excellent service overall\"}",
            "{\"respondent_id\":\"R002\",\"age\":52,\"gender\":\"Male\",\"region\":\"Manchester\",\"income_band\":\"60-80k\",\"satisfaction\":6,\"nps\":7}",
            "{\"respondent_id\":\"R003\",\"age\":28,\"gender\":\"Non-binary\",\"region\":\"Edinburgh\",\"satisfaction\":9,\"nps\":10,\"comments\":\"Very satisfied with recent changes\"}",
            "{\"respondent_id\":\"R004\",\"age\":41,\"gender\":\"Male\",\"region\":\"Birmingham\",\"income_band\":\"20-40k\",\"satisfaction\":4,\"nps\":5,\"comments\":\"Service could be improved\"}",
            "{\"respondent_id\":\"R005\",\"age\":67,\"region\":\"Bristol\",\"income_band\":\"40-60k\",\"satisfaction\":7,\"nps\":8}",
            "{\"respondent_id\":\"R006\",\"age\":23,\"gender\":\"Female\",\"region\":\"Leeds\",\"income_band\":\"<20k\",\"satisfaction\":8,\"nps\":9,\"comments\":\"Happy with the experience\"}",
            "{\"respondent_id\":\"R007\",\"age\":45,\"gender\":\"Male\",\"income_band\":\"80k+\",\"satisfaction\":5,\"nps\":6}",
            "{\"respondent_id\":\"R008\",\"age\":38,\"gender\":\"Female\",\"region\":\"Cardiff\",\"income_band\":\"40-60k\",\"satisfaction\":9,\"nps\":10,\"comments\":\"Outstanding support team\"}",
            "{\"respondent_id\":\"R009\",\"age\":55,\"gender\":\"Male\",\"region\":\"Glasgow\",\"satisfaction\":6,\"nps\":7}",
            "{\"respondent_id\":\"R010\",\"age\":31,\"gender\":\"Female\",\"region\":\"Liverpool\",\"income_band\":\"40-60k\",\"satisfaction\":8,\"nps\":9}",
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(10, doc.GetRecordCount());

        // GetMissingFieldCount — universal fields have zero missing
        Assert.Equal(0, doc.GetMissingFieldCount("respondent_id"));
        Assert.Equal(0, doc.GetMissingFieldCount("satisfaction"));
        Assert.Equal(0, doc.GetMissingFieldCount("nps"));

        // GetMissingFieldCount — optional fields have some missing
        var missingComments = doc.GetMissingFieldCount("comments");
        Assert.True(missingComments >= 0);
        var missingGender = doc.GetMissingFieldCount("gender");
        Assert.True(missingGender >= 0);
        var missingRegion = doc.GetMissingFieldCount("region");
        Assert.True(missingRegion >= 0);
        var missingIncome = doc.GetMissingFieldCount("income_band");
        Assert.True(missingIncome >= 0);

        // Consistent
        Assert.Equal(missingComments, doc.GetMissingFieldCount("comments"));

        // GetFieldCoverage — universal fields = 1.0
        Assert.Equal(1.0, doc.GetFieldCoverage("respondent_id"), precision: 6);
        Assert.Equal(1.0, doc.GetFieldCoverage("satisfaction"), precision: 6);

        // Optional field coverage in [0,1]
        var coverageComments = doc.GetFieldCoverage("comments");
        Assert.True(coverageComments >= 0.0 && coverageComments <= 1.0);

        var coverageIncome = doc.GetFieldCoverage("income_band");
        Assert.True(coverageIncome >= 0.0 && coverageIncome <= 1.0);

        // Consistent
        Assert.Equal(coverageComments, doc.GetFieldCoverage("comments"));

        // FillMissingValues — fill comments
        var filledComments = doc.FillMissingValues("comments", "No comment provided");
        Assert.NotNull(filledComments);
        Assert.Equal(doc.GetRecordCount(), filledComments.GetRecordCount());
        Assert.Equal(0, filledComments.GetMissingFieldCount("comments"));

        // FillMissingValues — fill income_band
        var filledIncome = doc.FillMissingValues("income_band", "Unknown");
        Assert.NotNull(filledIncome);
        Assert.Equal(doc.GetRecordCount(), filledIncome.GetRecordCount());

        // GetFieldCoverage after fill = 1.0
        Assert.Equal(1.0, filledComments.GetFieldCoverage("comments"), precision: 6);

        // SaveToFile
        var out1 = TempFile("dogfood_survey_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(10, loaded.GetRecordCount());
        Assert.Equal(missingComments, loaded.GetMissingFieldCount("comments"));
        Assert.Equal(coverageComments, loaded.GetFieldCoverage("comments"), precision: 6);

        // FillMissingValues on loaded
        var loadedFilled = loaded.FillMissingValues("gender", "Not Specified");
        Assert.Equal(loaded.GetRecordCount(), loadedFilled.GetRecordCount());

        // AddRecord — consistent schema
        loaded.AddRecord("{\"respondent_id\":\"R011\",\"age\":47,\"gender\":\"Male\",\"region\":\"Oxford\",\"income_band\":\"60-80k\",\"satisfaction\":7,\"nps\":8,\"comments\":\"Good but room for improvement\"}");
        Assert.Equal(11, loaded.GetRecordCount());
        Assert.Equal(0, loaded.GetMissingFieldCount("satisfaction"));

        // Final save
        var out2 = TempFile("dogfood_survey_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(11, loaded2.GetRecordCount());
        Assert.True(loaded2.GetMissingFieldCount("comments") >= 0);
        Assert.True(loaded2.GetFieldCoverage("respondent_id") == 1.0);
        var ex1 = Record.Exception(() => loaded2.FillMissingValues("comments", "N/A"));
        var ex2 = Record.Exception(() => loaded2.GetMissingFieldCount("income_band"));
        var ex3 = Record.Exception(() => loaded2.GetFieldCoverage("gender"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
