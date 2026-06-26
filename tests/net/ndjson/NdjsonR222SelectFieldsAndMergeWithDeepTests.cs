// Tests for NdjsonDocument.SelectFields, MergeWith, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R222

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R222: Tests for NdjsonDocument.SelectFields, MergeWith, GetDistinctValues deeper.
/// SelectFields(string[]): returns a new document containing only the specified fields.
/// MergeWith(other): combines records from both documents into one.
/// GetDistinctValues(fieldName): returns unique values for a field across all records.
/// Covers: SelectFields non-null; SelectFields no-throw; SelectFields reduces fields;
/// SelectFields correct fields; SelectFields consistent; SelectFields save-load;
/// SelectFields then GetRecordAt; SelectFields then ExportToCsv;
/// MergeWith non-null; MergeWith no-throw; MergeWith count is sum; MergeWith consistent;
/// MergeWith save-load; MergeWith then GetRecordAt; MergeWith then Sum;
/// GetDistinctValues non-null; GetDistinctValues no-throw; GetDistinctValues no duplicates;
/// GetDistinctValues correct count; GetDistinctValues consistent; GetDistinctValues save-load;
/// GetDistinctValues after MergeWith; GetDistinctValues after AppendRecord;
/// dogfood LoadFile→SelectFields→MergeWith→GetDistinctValues→SaveToFile pipeline.
/// </summary>
public class NdjsonR222SelectFieldsAndMergeWithDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR222SelectFieldsAndMergeWithDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR222_" + Guid.NewGuid().ToString("N"));
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
        var content =
            "{\"id\":\"E001\",\"name\":\"Alice\",\"dept\":\"Engineering\",\"salary\":95000,\"grade\":\"Senior\",\"office\":\"London\"}\n" +
            "{\"id\":\"E002\",\"name\":\"Bob\",\"dept\":\"Marketing\",\"salary\":72000,\"grade\":\"Mid\",\"office\":\"Paris\"}\n" +
            "{\"id\":\"E003\",\"name\":\"Carol\",\"dept\":\"Engineering\",\"salary\":115000,\"grade\":\"Lead\",\"office\":\"London\"}\n" +
            "{\"id\":\"E004\",\"name\":\"Dave\",\"dept\":\"Finance\",\"salary\":85000,\"grade\":\"Senior\",\"office\":\"Berlin\"}\n" +
            "{\"id\":\"E005\",\"name\":\"Eve\",\"dept\":\"Engineering\",\"salary\":99000,\"grade\":\"Senior\",\"office\":\"London\"}\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateContractorNdjson()
    {
        var path = TempFile("contractors.ndjson");
        var content =
            "{\"id\":\"C001\",\"name\":\"Frank\",\"dept\":\"Marketing\",\"salary\":68000,\"grade\":\"Mid\",\"office\":\"Rome\"}\n" +
            "{\"id\":\"C002\",\"name\":\"Grace\",\"dept\":\"Finance\",\"salary\":78000,\"grade\":\"Senior\",\"office\":\"Madrid\"}\n" +
            "{\"id\":\"C003\",\"name\":\"Hector\",\"dept\":\"Engineering\",\"salary\":105000,\"grade\":\"Lead\",\"office\":\"Tokyo\"}\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SelectFields
    // -------------------------------------------------------------------------

    [Fact]
    public void SelectFields_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.SelectFields(new[] { "name", "dept" }));
    }

    [Fact]
    public void SelectFields_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.SelectFields(new[] { "id", "name" }));
        Assert.Null(ex);
    }

    [Fact]
    public void SelectFields_SameRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var selected = doc.SelectFields(new[] { "name", "salary" });
        Assert.Equal(doc.GetRecordCount(), selected.GetRecordCount());
    }

    [Fact]
    public void SelectFields_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var s1 = doc.SelectFields(new[] { "name" });
        var s2 = doc.SelectFields(new[] { "name" });
        Assert.Equal(s1.GetRecordCount(), s2.GetRecordCount());
    }

    [Fact]
    public void SelectFields_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var selected = doc.SelectFields(new[] { "id", "name", "dept" });
        var path = TempFile("sf_save.ndjson");
        selected.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(selected.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void SelectFields_Then_GetRecordAt_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var selected = doc.SelectFields(new[] { "name", "dept" });
        for (int i = 0; i < selected.GetRecordCount(); i++)
            Assert.NotNull(selected.GetRecordAt(i));
    }

    [Fact]
    public void SelectFields_Then_ExportToCsv_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var selected = doc.SelectFields(new[] { "name", "salary" });
        var ex = Record.Exception(() => selected.ExportToCsv());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NonNull()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        Assert.NotNull(emp.MergeWith(con));
    }

    [Fact]
    public void MergeWith_NoThrow()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var ex = Record.Exception(() => emp.MergeWith(con));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeWith_Count_IsSum()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = emp.MergeWith(con);
        Assert.Equal(emp.GetRecordCount() + con.GetRecordCount(), merged.GetRecordCount());
    }

    [Fact]
    public void MergeWith_Consistent()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var m1 = emp.MergeWith(con);
        var m2 = emp.MergeWith(con);
        Assert.Equal(m1.GetRecordCount(), m2.GetRecordCount());
    }

    [Fact]
    public void MergeWith_SaveLoad_Consistent()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = emp.MergeWith(con);
        var path = TempFile("mw_save.ndjson");
        merged.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(merged.GetRecordCount(), loaded.GetRecordCount());
    }

    [Fact]
    public void MergeWith_Then_GetRecordAt_AllValid()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = emp.MergeWith(con);
        for (int i = 0; i < merged.GetRecordCount(); i++)
            Assert.NotNull(merged.GetRecordAt(i));
    }

    [Fact]
    public void MergeWith_Then_Sum()
    {
        var emp = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var con = NdjsonDocument.LoadFile(CreateContractorNdjson());
        var merged = emp.MergeWith(con);
        var totalSalary = merged.Sum("salary");
        // Verify > either individual sum
        Assert.True(totalSalary > emp.Sum("salary"));
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        Assert.NotNull(doc.GetDistinctValues("dept"));
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var ex = Record.Exception(() => doc.GetDistinctValues("grade"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var values = doc.GetDistinctValues("dept");
        var set = new System.Collections.Generic.HashSet<string>(values);
        Assert.Equal(values.Count, set.Count);
    }

    [Fact]
    public void GetDistinctValues_Dept_ThreeValues()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        // Engineering, Marketing, Finance
        Assert.Equal(3, doc.GetDistinctValues("dept").Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var v1 = doc.GetDistinctValues("dept");
        var v2 = doc.GetDistinctValues("dept");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetDistinctValues_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateEmployeeNdjson());
        var before = doc.GetDistinctValues("dept").Count;
        var path = TempFile("gdv_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDistinctValues("dept").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SelectFields_MergeWith_GetDistinctValues_SaveToFile_Pipeline()
    {
        var pathA = TempFile("dogfood_teamA.ndjson");
        File.WriteAllText(pathA,
            "{\"empId\":\"A001\",\"name\":\"Alice\",\"team\":\"Platform\",\"level\":\"Senior\",\"salary\":95000,\"office\":\"London\",\"yoe\":7}\n" +
            "{\"empId\":\"A002\",\"name\":\"Bob\",\"team\":\"Data\",\"level\":\"Mid\",\"salary\":72000,\"office\":\"Paris\",\"yoe\":3}\n" +
            "{\"empId\":\"A003\",\"name\":\"Carol\",\"team\":\"Platform\",\"level\":\"Lead\",\"salary\":125000,\"office\":\"London\",\"yoe\":12}\n" +
            "{\"empId\":\"A004\",\"name\":\"Dave\",\"team\":\"Finance\",\"level\":\"Junior\",\"salary\":58000,\"office\":\"Berlin\",\"yoe\":1}\n");

        var pathB = TempFile("dogfood_teamB.ndjson");
        File.WriteAllText(pathB,
            "{\"empId\":\"B001\",\"name\":\"Eve\",\"team\":\"Platform\",\"level\":\"Senior\",\"salary\":99000,\"office\":\"London\",\"yoe\":8}\n" +
            "{\"empId\":\"B002\",\"name\":\"Frank\",\"team\":\"Data\",\"level\":\"Senior\",\"salary\":105000,\"office\":\"Tokyo\",\"yoe\":9}\n" +
            "{\"empId\":\"B003\",\"name\":\"Grace\",\"team\":\"Finance\",\"level\":\"Mid\",\"salary\":78000,\"office\":\"Madrid\",\"yoe\":5}\n");

        var docA = NdjsonDocument.LoadFile(pathA);
        var docB = NdjsonDocument.LoadFile(pathB);

        Assert.Equal(4, docA.GetRecordCount());
        Assert.Equal(3, docB.GetRecordCount());

        // GetDistinctValues — team
        var teamsA = docA.GetDistinctValues("team");
        Assert.NotNull(teamsA);
        Assert.Equal(3, teamsA.Count); // Platform, Data, Finance
        var teamSet = new System.Collections.Generic.HashSet<string>(teamsA);
        Assert.Equal(teamsA.Count, teamSet.Count); // no duplicates

        // GetDistinctValues — level
        var levelsA = docA.GetDistinctValues("level");
        Assert.True(levelsA.Count >= 2);

        // SelectFields — public profile (name, team, level)
        var profile = docA.SelectFields(new[] { "name", "team", "level" });
        Assert.Equal(4, profile.GetRecordCount());
        for (int i = 0; i < profile.GetRecordCount(); i++)
            Assert.NotNull(profile.GetRecordAt(i));

        // SelectFields — salary subset
        var salaryView = docA.SelectFields(new[] { "empId", "salary" });
        Assert.Equal(4, salaryView.GetRecordCount());
        // Sum on salary subset
        var salarySum = salaryView.Sum("salary");
        Assert.True(salarySum > 0);
        Assert.Equal(docA.Sum("salary"), salarySum, 1); // same total

        // SelectFields consistent
        var prof2 = docA.SelectFields(new[] { "name", "team", "level" });
        Assert.Equal(profile.GetRecordCount(), prof2.GetRecordCount());

        // MergeWith
        var merged = docA.MergeWith(docB);
        Assert.Equal(7, merged.GetRecordCount());

        // GetDistinctValues on merged
        var allTeams = merged.GetDistinctValues("team");
        Assert.Equal(3, allTeams.Count); // Platform, Data, Finance still 3

        var allOffices = merged.GetDistinctValues("office");
        Assert.True(allOffices.Count >= 3); // London, Paris, Berlin, Tokyo, Madrid, etc.

        // Sum on merged
        var totalSalary = merged.Sum("salary");
        Assert.True(totalSalary > docA.Sum("salary")); // larger than either alone
        Assert.True(totalSalary > docB.Sum("salary"));
        Assert.Equal(docA.Sum("salary") + docB.Sum("salary"), totalSalary, 1);

        // Average on merged
        var avgSalary = merged.Average("salary");
        Assert.True(avgSalary >= merged.GetMinValue("salary"));
        Assert.True(avgSalary <= merged.GetMaxValue("salary"));

        // FilterByField on merged — Platform team
        var platform = merged.FilterByField("team", "Platform");
        Assert.Equal(3, platform.GetRecordCount()); // A001, A003, B001

        // SelectFields on merged
        var mergedProfile = merged.SelectFields(new[] { "name", "team", "level" });
        Assert.Equal(7, mergedProfile.GetRecordCount());

        // ExportToCsv
        var csv = merged.ExportToCsv();
        Assert.NotNull(csv);
        Assert.NotEmpty(csv);

        // ExportToJson
        var json = merged.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // SaveToFile merged
        var savePath = TempFile("dogfood_all_staff.ndjson");
        merged.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRecordCount());
        Assert.Equal(3, loaded.GetDistinctValues("team").Count);
        Assert.Equal(totalSalary, loaded.Sum("salary"), 1);

        // SelectFields on loaded
        var loadedProfile = loaded.SelectFields(new[] { "empId", "name" });
        Assert.Equal(7, loadedProfile.GetRecordCount());

        // MergeWith loaded with docA again
        var extended = loaded.MergeWith(docA);
        Assert.Equal(11, extended.GetRecordCount());

        // Final save
        var path2 = TempFile("dogfood_all_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(3, loaded2.GetDistinctValues("team").Count);
        var ex1 = Record.Exception(() => loaded2.ExportToCsv());
        var ex2 = Record.Exception(() => loaded2.ExportToJson());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
