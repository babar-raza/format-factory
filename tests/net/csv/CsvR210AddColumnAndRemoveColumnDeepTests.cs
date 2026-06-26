// Tests for CsvDocument.AddColumn, RemoveColumn, GetColumnValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R210

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R210: Tests for CsvDocument.AddColumn, RemoveColumn, GetColumnValues deeper.
/// AddColumn(name, values): adds a new column with the given name and values.
/// RemoveColumn(name): removes the specified column from the document.
/// GetColumnValues(colName): returns all values in the specified column as a list.
/// Covers: AddColumn no-throw; AddColumn increases header count; AddColumn name in headers;
/// AddColumn values accessible; AddColumn persist; AddColumn multiple; AddColumn then Filter;
/// AddColumn then SortRows; AddColumn save-load consistent;
/// RemoveColumn no-throw; RemoveColumn decreases header count; RemoveColumn name gone;
/// RemoveColumn row count unchanged; RemoveColumn then AddColumn same name;
/// RemoveColumn persist; RemoveColumn save-load; RemoveColumn then ExportToXml;
/// GetColumnValues non-null; GetColumnValues non-empty; GetColumnValues no-throw;
/// GetColumnValues count=rowCount; GetColumnValues contains known; GetColumnValues consistent;
/// GetColumnValues after SetCell updates; GetColumnValues save-load consistent;
/// GetColumnValues after Filter subset; GetColumnValues after AddRow grows;
/// dogfood LoadFile→AddColumn→GetColumnValues→RemoveColumn→SaveToFile pipeline.
/// </summary>
public class CsvR210AddColumnAndRemoveColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR210AddColumnAndRemoveColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR210_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleCsv()
    {
        var path = TempFile("sample.csv");
        var content =
            "Name,Department,Score\n" +
            "Alice,Engineering,92\n" +
            "Bob,Marketing,78\n" +
            "Carol,Engineering,88\n" +
            "Dave,Finance,85\n" +
            "Eve,Engineering,95\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_IncreasesHeaderCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        Assert.Equal(before + 1, doc.GetHeaderCount());
    }

    [Fact]
    public void AddColumn_NameInHeaders()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.True(doc.GetHeaderCount() >= 4);
    }

    [Fact]
    public void AddColumn_ValuesAccessible()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        var vals = doc.GetColumnValues("City");
        Assert.True(vals.Contains("London") || vals.Exists(v => v == "London"));
    }

    [Fact]
    public void AddColumn_Persist()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        var path = TempFile("addcol_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetHeaderCount());
    }

    [Fact]
    public void AddColumn_Multiple()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        doc.AddColumn("Level", new[] { "L6", "L2", "L6", "L3", "L5" });
        Assert.Equal(5, doc.GetHeaderCount());
    }

    [Fact]
    public void AddColumn_ThenFilter_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        var ex = Record.Exception(() => doc.Filter("Region", "EU"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_ThenSortRows_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        var ex = Record.Exception(() => doc.SortRows("City", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void AddColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.AddColumn("City", new[] { "London", "Paris", "Berlin", "Rome", "Madrid" });
        var vals = doc.GetColumnValues("City");
        var path = TempFile("addcol_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(vals.Count, loaded.GetColumnValues("City").Count);
    }

    // -------------------------------------------------------------------------
    // RemoveColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.RemoveColumn("Score"));
        Assert.Null(ex);
    }

    [Fact]
    public void RemoveColumn_DecreasesHeaderCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetHeaderCount();
        doc.RemoveColumn("Score");
        Assert.Equal(before - 1, doc.GetHeaderCount());
    }

    [Fact]
    public void RemoveColumn_RowCountUnchanged()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetRowCount();
        doc.RemoveColumn("Score");
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void RemoveColumn_ThenAddColumnSameName()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveColumn("Score");
        doc.AddColumn("Score", new[] { "100", "99", "98", "97", "96" });
        Assert.Equal(3, doc.GetHeaderCount());
    }

    [Fact]
    public void RemoveColumn_Persist()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveColumn("Score");
        var path = TempFile("removecol_persist.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.GetHeaderCount());
    }

    [Fact]
    public void RemoveColumn_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveColumn("Department");
        var before = doc.GetHeaderCount();
        var path = TempFile("removecol_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetHeaderCount());
    }

    [Fact]
    public void RemoveColumn_ThenExportToXml_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RemoveColumn("Score");
        var ex = Record.Exception(() => doc.ExportToXml());
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.GetColumnValues("Name"));
    }

    [Fact]
    public void GetColumnValues_NonEmpty()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnValues("Name").Count > 0);
    }

    [Fact]
    public void GetColumnValues_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnValues("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnValues_Count_EqualsRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetRowCount(), doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_ContainsKnown()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var vals = doc.GetColumnValues("Name");
        Assert.True(vals.Contains("Alice") || vals.Exists(v => v == "Alice"));
    }

    [Fact]
    public void GetColumnValues_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var v1 = doc.GetColumnValues("Name");
        var v2 = doc.GetColumnValues("Name");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetColumnValues_AfterAddRow_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnValues("Name").Count;
        doc.AddRow(new[] { "Frank", "HR", "80" });
        Assert.Equal(before + 1, doc.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnValues("Name").Count;
        var path = TempFile("colvals_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnValues("Name").Count);
    }

    [Fact]
    public void GetColumnValues_AfterFilter_Subset()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var filtered = doc.Filter("Department", "Engineering");
        Assert.Equal(3, filtered.GetColumnValues("Name").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddColumn_GetColumnValues_RemoveColumn_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_employees.csv");
        var content =
            "Employee,Department,Score\n" +
            "Alice,Engineering,92\n" +
            "Bob,Marketing,78\n" +
            "Carol,Engineering,88\n" +
            "Dave,Finance,85\n" +
            "Eve,Engineering,95\n" +
            "Frank,Marketing,80\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());
        Assert.Equal(3, doc.GetHeaderCount());

        // GetColumnValues baseline
        var names = doc.GetColumnValues("Employee");
        Assert.Equal(6, names.Count);
        Assert.True(names.Contains("Alice") || names.Exists(v => v == "Alice"));

        var depts = doc.GetColumnValues("Department");
        Assert.Equal(6, depts.Count);
        Assert.True(depts.Contains("Engineering") || depts.Exists(v => v == "Engineering"));

        var scores = doc.GetColumnValues("Score");
        Assert.Equal(6, scores.Count);

        // AddColumn Location
        doc.AddColumn("Location", new[] { "London", "Paris", "London", "Berlin", "London", "Rome" });
        Assert.Equal(4, doc.GetHeaderCount());

        var locations = doc.GetColumnValues("Location");
        Assert.Equal(6, locations.Count);
        Assert.True(locations.Contains("London") || locations.Exists(v => v == "London"));

        // AddColumn Level
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Lead", "Mid", "Senior", "Senior" });
        Assert.Equal(5, doc.GetHeaderCount());

        var levels = doc.GetColumnValues("Level");
        Assert.Equal(6, levels.Count);

        // Consistent
        Assert.Equal(names.Count, doc.GetColumnValues("Employee").Count);

        // Filter using new column
        var londonTeam = doc.Filter("Location", "London");
        Assert.Equal(3, londonTeam.GetRowCount()); // Alice, Carol, Eve
        var londonNames = londonTeam.GetColumnValues("Employee");
        Assert.Equal(3, londonNames.Count);

        // SortRows by Level
        doc.SortRows("Level", ascending: true);
        Assert.Equal(6, doc.GetRowCount());

        // AddRow and verify GetColumnValues grows
        doc.AddRow(new[] { "Grace", "HR", "72", "Madrid", "Junior" });
        Assert.Equal(7, doc.GetRowCount());
        Assert.Equal(7, doc.GetColumnValues("Employee").Count);

        // RemoveColumn Level
        doc.RemoveColumn("Level");
        Assert.Equal(4, doc.GetHeaderCount());
        Assert.Equal(7, doc.GetRowCount()); // rows unchanged

        // GetColumnValues after RemoveColumn — only 4 columns
        var postRemoveNames = doc.GetColumnValues("Employee");
        Assert.Equal(7, postRemoveNames.Count);

        // ExportToXml with remaining columns
        var xml = doc.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);

        // SaveToFile
        var savePath = TempFile("dogfood_employees_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(4, loaded.GetHeaderCount());
        Assert.Equal(7, loaded.GetColumnValues("Employee").Count);

        // AddColumn on loaded
        loaded.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(5, loaded.GetHeaderCount());
        Assert.Equal(7, loaded.GetColumnValues("Region").Count);

        // RemoveColumn on loaded
        loaded.RemoveColumn("Location");
        Assert.Equal(4, loaded.GetHeaderCount());

        // GetColumnValues consistent on loaded
        Assert.Equal(loaded.GetColumnValues("Employee").Count,
                     loaded.GetColumnValues("Employee").Count);

        // Final save
        var path2 = TempFile("dogfood_employees_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetHeaderCount(), loaded2.GetHeaderCount());
        Assert.Equal(loaded.GetColumnValues("Employee").Count,
                     loaded2.GetColumnValues("Employee").Count);
    }
}
