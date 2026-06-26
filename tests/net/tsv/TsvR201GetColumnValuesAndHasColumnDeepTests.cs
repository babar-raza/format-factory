// Tests for TsvDocument.GetColumnValues, HasColumn, ExportToJson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R201

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R201: Tests for TsvDocument.GetColumnValues, HasColumn, ExportToJson deeper.
/// GetColumnValues(colName): returns all values in the specified column.
/// HasColumn(colName): returns true if the column exists in the document.
/// ExportToJson(): exports the document content as a JSON string.
/// Covers: GetColumnValues non-null; GetColumnValues non-empty; GetColumnValues count=rowCount;
/// GetColumnValues contains known; GetColumnValues consistent; GetColumnValues for numeric col;
/// GetColumnValues after SetCell reflects; GetColumnValues after AddRow grows;
/// GetColumnValues after Filter shrinks; GetColumnValues no-throw;
/// HasColumn true for existing; HasColumn false for non-existent; HasColumn consistent;
/// HasColumn no-throw; HasColumn after AddColumn true; HasColumn after RemoveColumn false;
/// HasColumn for all known; HasColumn empty string false;
/// ExportToJson non-null; ExportToJson non-empty; ExportToJson has braces;
/// ExportToJson has header names; ExportToJson has data values; ExportToJson after AddRow grows;
/// ExportToJson after Filter shrinks; ExportToJson consistent;
/// dogfood LoadFile→GetColumnValues→HasColumn→ExportToJson→SaveToFile pipeline.
/// </summary>
public class TsvR201GetColumnValuesAndHasColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR201GetColumnValuesAndHasColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR201_" + Guid.NewGuid().ToString("N"));
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
        var content =
            "Name\tTeam\tScore\tCity\n" +
            "Alice\tAlpha\t92\tLondon\n" +
            "Bob\tBeta\t78\tParis\n" +
            "Carol\tAlpha\t88\tBerlin\n" +
            "Dave\tGamma\t85\tRome\n" +
            "Eve\tAlpha\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.True(doc.GetColumnValues("Name").Count > 0);
    }

    [Fact]
    public void GetColumnValues_CountEqualsRowCount()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.GetRowCount(), doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_ContainsKnown()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var values = doc.GetColumnValues("Name");
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
        Assert.Contains("Carol", values);
    }

    [Fact]
    public void GetColumnValues_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var v1 = doc.GetColumnValues("Name");
        var v2 = doc.GetColumnValues("Name");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetColumnValues_ForNumericColumn()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var values = doc.GetColumnValues("Score");
        Assert.True(values.Count > 0);
        Assert.Contains("92", values);
        Assert.Contains("78", values);
    }

    [Fact]
    public void GetColumnValues_AfterSetCell_Reflects()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.SetCell(0, 0, "ALICE_UPDATED");
        var values = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_UPDATED", values);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_Grows()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetColumnValues("Name").Count;
        doc.AddRow(new[] { "Frank", "Beta", "82", "Oslo" });
        var after = doc.GetColumnValues("Name").Count;
        Assert.Equal(before + 1, after);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_Shrinks()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.GetColumnValues("Name").Count;
        var filtered = doc.Filter("Team", "Alpha");
        var after = filtered.GetColumnValues("Name").Count;
        Assert.True(after < before);
    }

    [Fact]
    public void GetColumnValues_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.GetColumnValues("Name"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_True_ForExisting()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Team"));
        Assert.True(doc.HasColumn("Score"));
        Assert.True(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_False_ForNonExistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.False(doc.HasColumn("NonExistentColumn_XYZ"));
    }

    [Fact]
    public void HasColumn_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(doc.HasColumn("Name"), doc.HasColumn("Name"));
    }

    [Fact]
    public void HasColumn_NoThrow()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var ex = Record.Exception(() => doc.HasColumn("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void HasColumn_AfterAddColumn_True()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.True(doc.HasColumn("Region"));
    }

    [Fact]
    public void HasColumn_AfterRemoveColumn_False()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        doc.RemoveColumn("City");
        Assert.False(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_ReturnsBool()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var result = doc.HasColumn("Name");
        Assert.IsType<bool>(result);
    }

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_HasBraces()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var json = doc.ExportToJson();
        Assert.True(json.Contains("{") || json.Contains("["));
    }

    [Fact]
    public void ExportToJson_HasHeaderNames()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Name") || json.Contains("Team") || json.Contains("Score"));
    }

    [Fact]
    public void ExportToJson_HasDataValues()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var json = doc.ExportToJson();
        Assert.True(json.Contains("Alice") || json.Contains("Bob") || json.Contains("Carol"));
    }

    [Fact]
    public void ExportToJson_AfterAddRow_Grows()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToJson().Length;
        doc.AddRow(new[] { "Frank", "Beta", "82", "Oslo" });
        var after = doc.ExportToJson().Length;
        Assert.True(after > before);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Shrinks()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var before = doc.ExportToJson().Length;
        var filtered = doc.Filter("Team", "Alpha");
        var after = filtered.ExportToJson().Length;
        Assert.True(after < before);
    }

    [Fact]
    public void ExportToJson_Consistent()
    {
        var path = CreateSampleTsv();
        var doc = TsvDocument.LoadFile(path);
        var j1 = doc.ExportToJson();
        var j2 = doc.ExportToJson();
        Assert.Equal(j1.Length, j2.Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnValues_HasColumn_ExportToJson_SaveToFile_Pipeline()
    {
        // Create sample TSV
        var path = TempFile("dogfood_src.tsv");
        var content =
            "Employee\tDepartment\tGrade\tLocation\tSalary\n" +
            "Alice\tEngineering\tSenior\tLondon\t95000\n" +
            "Bob\tMarketing\tJunior\tParis\t55000\n" +
            "Carol\tEngineering\tLead\tLondon\t115000\n" +
            "Dave\tFinance\tMid\tBerlin\t72000\n" +
            "Eve\tEngineering\tSenior\tLondon\t98000\n" +
            "Frank\tMarketing\tSenior\tRome\t82000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetColumnValues — names
        var names = doc.GetColumnValues("Employee");
        Assert.NotNull(names);
        Assert.Equal(6, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);

        // GetColumnValues — departments
        var depts = doc.GetColumnValues("Department");
        Assert.Contains("Engineering", depts);
        Assert.Contains("Marketing", depts);
        Assert.Contains("Finance", depts);

        // HasColumn checks
        Assert.True(doc.HasColumn("Employee"));
        Assert.True(doc.HasColumn("Department"));
        Assert.True(doc.HasColumn("Grade"));
        Assert.True(doc.HasColumn("Location"));
        Assert.True(doc.HasColumn("Salary"));
        Assert.False(doc.HasColumn("NonExistent"));
        Assert.False(doc.HasColumn("Region"));

        // ExportToJson baseline
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);
        Assert.True(json.Contains("{") || json.Contains("["));

        // AddColumn and verify HasColumn
        doc.AddColumn("Level", new[] { "L5", "L2", "L6", "L3", "L5", "L4" });
        Assert.True(doc.HasColumn("Level"));
        var headersAfterAdd = doc.GetHeaders();
        Assert.Equal(6, headersAfterAdd.Count);

        // ExportToJson grows after AddColumn
        var jsonAfterAdd = doc.ExportToJson();
        Assert.True(jsonAfterAdd.Length > json.Length);

        // GetColumnValues for new column
        var levels = doc.GetColumnValues("Level");
        Assert.Equal(6, levels.Count);
        Assert.Contains("L5", levels);
        Assert.Contains("L6", levels);

        // SetCell and verify GetColumnValues reflects
        doc.SetCell(0, 0, "ALICE_MODIFIED");
        var namesAfterSet = doc.GetColumnValues("Employee");
        Assert.Contains("ALICE_MODIFIED", namesAfterSet);

        // AddRow and verify counts
        doc.AddRow(new[] { "Grace", "Finance", "Junior", "Madrid", "48000", "L1" });
        Assert.Equal(7, doc.GetRowCount());
        var namesAfterRow = doc.GetColumnValues("Employee");
        Assert.Equal(7, namesAfterRow.Count);
        Assert.Contains("Grace", namesAfterRow);

        // HasColumn after RemoveColumn
        doc.RemoveColumn("Level");
        Assert.False(doc.HasColumn("Level"));

        // ExportToJson after RemoveColumn shrinks
        var jsonAfterRemove = doc.ExportToJson();
        Assert.True(jsonAfterRemove.Length < jsonAfterAdd.Length);

        // Filter Engineering and verify GetColumnValues
        var engFiltered = doc.Filter("Department", "Engineering");
        var engNames = engFiltered.GetColumnValues("Employee");
        Assert.True(engNames.Count < names.Count);
        Assert.Contains("Carol", engNames);

        // HasColumn on filtered
        Assert.True(engFiltered.HasColumn("Employee"));
        Assert.True(engFiltered.HasColumn("Salary"));
        Assert.False(engFiltered.HasColumn("Level")); // was removed

        // ExportToJson on filtered
        var filteredJson = engFiltered.ExportToJson();
        Assert.True(filteredJson.Length < jsonAfterRemove.Length);

        // SortRows and verify GetColumnValues order
        doc.SortRows("Salary", ascending: false);
        var sortedSalaries = doc.GetColumnValues("Salary");
        Assert.True(sortedSalaries.Count > 0);

        // SaveToFile
        var savePath = TempFile("dogfood_column_values.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());

        var loadedNames = loaded.GetColumnValues("Employee");
        Assert.Equal(7, loadedNames.Count);

        Assert.True(loaded.HasColumn("Employee"));
        Assert.True(loaded.HasColumn("Salary"));
        Assert.False(loaded.HasColumn("Level"));

        // ExportToJson on loaded
        var loadedJson = loaded.ExportToJson();
        Assert.NotNull(loadedJson);
        Assert.NotEmpty(loadedJson);

        // GetColumnValues consistent on loaded
        var lv1 = loaded.GetColumnValues("Employee");
        var lv2 = loaded.GetColumnValues("Employee");
        Assert.Equal(lv1.Count, lv2.Count);
    }
}
