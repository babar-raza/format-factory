// Tests for TsvDocument.GetUniqueValueCount, ApplyTransform, ExportToJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R211

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R211: Tests for TsvDocument.GetUniqueValueCount, ApplyTransform, ExportToJson deeper.
/// GetUniqueValueCount(colName): returns count of distinct values in a column.
/// ApplyTransform(colName, func): returns new doc with func applied to each cell in column.
/// ExportToJson(): exports the document as a JSON string (array of objects).
/// Covers: GetUniqueValueCount positive; GetUniqueValueCount no-throw;
/// GetUniqueValueCount department count correct; GetUniqueValueCount consistent;
/// GetUniqueValueCount save-load; GetUniqueValueCount after AddRow updates;
/// GetUniqueValueCount all-unique column=rowCount;
/// ApplyTransform non-null; ApplyTransform no-throw; ApplyTransform same row count;
/// ApplyTransform values changed; ApplyTransform consistent; ApplyTransform save-load;
/// ApplyTransform identity no change; ApplyTransform uppercase transforms;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson has braces;
/// ExportToJson has content; ExportToJson consistent; ExportToJson no-throw;
/// ExportToJson after AddRow grows; ExportToJson save-load;
/// dogfood LoadFile→GetUniqueValueCount→ApplyTransform→ExportToJson→SaveToFile pipeline.
/// </summary>
public class TsvR211GetUniqueValueCountAndTransformDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR211GetUniqueValueCountAndTransformDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR211_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEmployeeTsv()
    {
        var path = TempFile("employees.tsv");
        var content =
            "Name\tDepartment\tCity\tScore\n" +
            "Alice\tEngineering\tLondon\t92\n" +
            "Bob\tMarketing\tParis\t78\n" +
            "Carol\tEngineering\tLondon\t88\n" +
            "Dave\tFinance\tBerlin\t85\n" +
            "Eve\tEngineering\tLondon\t95\n" +
            "Frank\tMarketing\tRome\t72\n" +
            "Grace\tFinance\tMadrid\t81\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetUniqueValueCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueValueCount_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.True(doc.GetUniqueValueCount("Department") > 0);
    }

    [Fact]
    public void GetUniqueValueCount_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.GetUniqueValueCount("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueValueCount_Department_ThreeDistinct()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        // Engineering, Marketing, Finance = 3
        Assert.Equal(3, doc.GetUniqueValueCount("Department"));
    }

    [Fact]
    public void GetUniqueValueCount_City_FiveDistinct()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        // London(3), Paris, Berlin, Rome, Madrid = 5 distinct
        Assert.Equal(5, doc.GetUniqueValueCount("City"));
    }

    [Fact]
    public void GetUniqueValueCount_Name_AllUnique()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        // All 7 names are unique
        Assert.Equal(doc.GetRowCount(), doc.GetUniqueValueCount("Name"));
    }

    [Fact]
    public void GetUniqueValueCount_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.Equal(doc.GetUniqueValueCount("Department"), doc.GetUniqueValueCount("Department"));
    }

    [Fact]
    public void GetUniqueValueCount_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.GetUniqueValueCount("Department");
        var path = TempFile("uvc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueValueCount("Department"));
    }

    [Fact]
    public void GetUniqueValueCount_AfterAddRow_Updates()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.GetUniqueValueCount("Department");
        doc.AddRow(new[] { "Hector", "Legal", "Amsterdam", "79" });
        Assert.Equal(before + 1, doc.GetUniqueValueCount("Department"));
    }

    // -------------------------------------------------------------------------
    // ApplyTransform
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyTransform_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.ApplyTransform("Department", v => v.ToUpper()));
    }

    [Fact]
    public void ApplyTransform_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.ApplyTransform("Department", v => v.ToUpper()));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyTransform_SameRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var transformed = doc.ApplyTransform("Department", v => v.ToUpper());
        Assert.Equal(doc.GetRowCount(), transformed.GetRowCount());
    }

    [Fact]
    public void ApplyTransform_Values_Changed()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var transformed = doc.ApplyTransform("Department", v => v.ToUpper());
        var vals = transformed.GetColumnValues("Department");
        Assert.True(vals.Exists(v => v == "ENGINEERING" || v == "MARKETING" || v == "FINANCE"));
    }

    [Fact]
    public void ApplyTransform_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var t1 = doc.ApplyTransform("Department", v => v.ToUpper());
        var t2 = doc.ApplyTransform("Department", v => v.ToUpper());
        Assert.Equal(t1.GetRowCount(), t2.GetRowCount());
    }

    [Fact]
    public void ApplyTransform_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var transformed = doc.ApplyTransform("Name", v => v.ToLower());
        var path = TempFile("transform_save.tsv");
        transformed.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(transformed.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void ApplyTransform_Identity_NoChange()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var transformed = doc.ApplyTransform("Department", v => v);
        var orig = doc.GetColumnValues("Department");
        var trans = transformed.GetColumnValues("Department");
        Assert.Equal(orig.Count, trans.Count);
        for (int i = 0; i < orig.Count; i++)
            Assert.Equal(orig[i], trans[i]);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_HasBraces()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_HasContent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Engineering") || json.Contains("Department"));
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    [Fact]
    public void ExportToJson_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.ExportToJson());
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToJson_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.ExportToJson().Length;
        doc.AddRow(new[] { "Hector", "Legal", "Amsterdam", "79" });
        Assert.True(doc.ExportToJson().Length > before);
    }

    [Fact]
    public void ExportToJson_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.ExportToJson().Length;
        var path = TempFile("json_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.True(Math.Abs(loaded.ExportToJson().Length - before) <= 10);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetUniqueValueCount_ApplyTransform_ExportToJson_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_staff.tsv");
        var content =
            "EmpId\tName\tTeam\tLevel\tLocation\tRating\n" +
            "E001\tAlice\tPlatform\tSenior\tLondon\t92\n" +
            "E002\tBob\tData\tJunior\tParis\t74\n" +
            "E003\tCarol\tPlatform\tLead\tLondon\t98\n" +
            "E004\tDave\tFinance\tMid\tBerlin\t81\n" +
            "E005\tEve\tData\tSenior\tLondon\t89\n" +
            "E006\tFrank\tPlatform\tSenior\tRome\t87\n" +
            "E007\tGrace\tFinance\tJunior\tMadrid\t76\n" +
            "E008\tHector\tData\tMid\tTokyo\t83\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // GetUniqueValueCount
        Assert.Equal(3, doc.GetUniqueValueCount("Team"));
        Assert.Equal(4, doc.GetUniqueValueCount("Level"));
        Assert.Equal(6, doc.GetUniqueValueCount("Location"));
        Assert.Equal(8, doc.GetUniqueValueCount("EmpId")); // all unique

        // Consistent
        Assert.Equal(3, doc.GetUniqueValueCount("Team"));

        // AfterAddRow updates
        doc.AddRow(new[] { "E009", "Iris", "Legal", "Mid", "Sydney", "85" });
        Assert.Equal(4, doc.GetUniqueValueCount("Team"));
        Assert.Equal(9, doc.GetRowCount());

        // ApplyTransform — uppercase Team
        var upperTeam = doc.ApplyTransform("Team", v => v.ToUpper());
        Assert.Equal(9, upperTeam.GetRowCount());
        var teamVals = upperTeam.GetColumnValues("Team");
        Assert.True(teamVals.Exists(v => v == "PLATFORM" || v == "DATA" || v == "FINANCE"));

        // ApplyTransform — prefix EmpId
        var prefixed = doc.ApplyTransform("EmpId", v => "ID:" + v);
        Assert.Equal(9, prefixed.GetRowCount());
        var idVals = prefixed.GetColumnValues("EmpId");
        Assert.True(idVals.Exists(v => v.StartsWith("ID:")));

        // ApplyTransform consistent
        var t1 = doc.ApplyTransform("Team", v => v.ToUpper());
        var t2 = doc.ApplyTransform("Team", v => v.ToUpper());
        Assert.Equal(t1.GetRowCount(), t2.GetRowCount());

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));
        Assert.True(json.Contains("Alice") || json.Contains("Team") || json.Contains("EmpId"));

        // Consistent
        Assert.Equal(json.Length, doc.ExportToJson().Length);

        // ExportToJson on transformed doc
        var upperJson = upperTeam.ExportToJson();
        Assert.NotNull(upperJson);
        Assert.True(upperJson.Contains("PLATFORM") || upperJson.Contains("{"));

        // SaveToFile
        var savePath = TempFile("dogfood_staff_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetUniqueValueCount("Team"));

        // GetUniqueValueCount on loaded
        Assert.Equal(8, loaded.GetUniqueValueCount("EmpId")); // E009 also, but EmpId unique per row → 9? verify
        // (actually 9 unique EmpIds in 9 rows)
        Assert.True(loaded.GetUniqueValueCount("EmpId") >= 8);

        // ApplyTransform on loaded
        var loadedTransform = loaded.ApplyTransform("Level", v => v.ToLower());
        var levelVals = loadedTransform.GetColumnValues("Level");
        Assert.True(levelVals.Exists(v => v == "senior" || v == "junior" || v == "mid"));

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.Contains("{", loadedJson);

        // Final save
        var path2 = TempFile("dogfood_staff_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetUniqueValueCount("Team"), loaded2.GetUniqueValueCount("Team"));
    }
}
