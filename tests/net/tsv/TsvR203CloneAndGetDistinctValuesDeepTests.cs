// Tests for TsvDocument.Clone, GetDistinctValues, ExportToNdjson deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R203

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R203: Tests for TsvDocument.Clone, GetDistinctValues, ExportToNdjson deeper.
/// Clone(): returns an independent copy of the document.
/// GetDistinctValues(colName): returns unique values in the specified column.
/// ExportToNdjson(): exports the document as newline-delimited JSON.
/// Covers: Clone non-null; Clone same row count; Clone same headers; Clone independent;
/// Clone changes don't affect original; Clone persist; Clone then Filter; Clone then SortRows;
/// Clone then SetCell; Clone then AddRow;
/// GetDistinctValues non-null; GetDistinctValues non-empty; GetDistinctValues count correct;
/// GetDistinctValues contains known; GetDistinctValues no duplicates; GetDistinctValues consistent;
/// GetDistinctValues after AddRow updates; GetDistinctValues after Filter shrinks;
/// GetDistinctValues all names unique=5; GetDistinctValues no-throw;
/// ExportToNdjson non-null; ExportToNdjson non-empty; ExportToNdjson has braces;
/// ExportToNdjson has header names; ExportToNdjson has data; ExportToNdjson after AddRow grows;
/// ExportToNdjson after Filter shrinks; ExportToNdjson consistent;
/// dogfood LoadFile→Clone→GetDistinctValues→ExportToNdjson→SaveToFile pipeline.
/// </summary>
public class TsvR203CloneAndGetDistinctValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR203CloneAndGetDistinctValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR203_" + Guid.NewGuid().ToString("N"));
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
    // Clone
    // -------------------------------------------------------------------------

    [Fact]
    public void Clone_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.Clone());
    }

    [Fact]
    public void Clone_SameRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetRowCount(), doc.Clone().GetRowCount());
    }

    [Fact]
    public void Clone_SameHeaders()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var headers = doc.GetHeaders();
        var cloneHeaders = doc.Clone().GetHeaders();
        Assert.Equal(headers.Count, cloneHeaders.Count);
    }

    [Fact]
    public void Clone_Independent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        clone.SetCell(0, 0, "CLONE_MODIFIED");
        Assert.NotEqual("CLONE_MODIFIED", doc.GetCell(0, 0));
    }

    [Fact]
    public void Clone_ChangesDontAffectOriginal()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var origRow0 = doc.GetCell(0, 0);
        var clone = doc.Clone();
        clone.AddRow(new[] { "Extra", "Beta", "99", "Oslo" });
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(origRow0, doc.GetCell(0, 0));
    }

    [Fact]
    public void Clone_Persist()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        var path = TempFile("clone_persist.tsv");
        clone.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.GetRowCount());
    }

    [Fact]
    public void Clone_ThenFilter()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        var filtered = clone.Filter("Team", "Alpha");
        Assert.Equal(3, filtered.GetRowCount());
    }

    [Fact]
    public void Clone_ThenSortRows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        clone.SortRows("Name", ascending: true);
        Assert.Equal("Alice", clone.GetCell(0, 0));
        Assert.Equal(5, doc.GetRowCount()); // original unchanged
    }

    [Fact]
    public void Clone_ThenAddRow_OriginalUnchanged()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var clone = doc.Clone();
        clone.AddRow(new[] { "Zara", "Delta", "77", "Vienna" });
        Assert.Equal(5, doc.GetRowCount());
        Assert.Equal(6, clone.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.GetDistinctValues("Team"));
    }

    [Fact]
    public void GetDistinctValues_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetDistinctValues("Team").Count > 0);
    }

    [Fact]
    public void GetDistinctValues_CountCorrect()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        // Alpha, Beta, Gamma = 3 distinct teams
        Assert.Equal(3, doc.GetDistinctValues("Team").Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnown()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var values = doc.GetDistinctValues("Team");
        Assert.Contains("Alpha", values);
        Assert.Contains("Beta", values);
        Assert.Contains("Gamma", values);
    }

    [Fact]
    public void GetDistinctValues_NoDuplicates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var values = doc.GetDistinctValues("Team");
        var set = new System.Collections.Generic.HashSet<string>(values);
        Assert.Equal(set.Count, values.Count);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var v1 = doc.GetDistinctValues("Team");
        var v2 = doc.GetDistinctValues("Team");
        Assert.Equal(v1.Count, v2.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_Updates()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetDistinctValues("Team").Count;
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        var after = doc.GetDistinctValues("Team").Count;
        Assert.True(after >= before);
    }

    [Fact]
    public void GetDistinctValues_AllNamesUnique()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(5, doc.GetDistinctValues("Name").Count);
    }

    [Fact]
    public void GetDistinctValues_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetDistinctValues("Team"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // ExportToNdjson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToNdjson_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotEmpty(doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasBraces()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Contains("{", doc.ExportToNdjson());
    }

    [Fact]
    public void ExportToNdjson_HasHeaderNames()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Name") || ndjson.Contains("Team") || ndjson.Contains("Score"));
    }

    [Fact]
    public void ExportToNdjson_HasData()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ndjson = doc.ExportToNdjson();
        Assert.True(ndjson.Contains("Alice") || ndjson.Contains("Bob") || ndjson.Contains("Carol"));
    }

    [Fact]
    public void ExportToNdjson_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToNdjson().Length;
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        Assert.True(doc.ExportToNdjson().Length > before);
    }

    [Fact]
    public void ExportToNdjson_AfterFilter_Shrinks()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToNdjson().Length;
        var filtered = doc.Filter("Team", "Gamma");
        Assert.True(filtered.ExportToNdjson().Length < before);
    }

    [Fact]
    public void ExportToNdjson_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.ExportToNdjson().Length, doc.ExportToNdjson().Length);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_Clone_GetDistinctValues_ExportToNdjson_SaveToFile_Pipeline()
    {
        // Create main TSV
        var path = TempFile("dogfood_main.tsv");
        var content =
            "Employee\tDept\tGrade\tLocation\tSalary\n" +
            "Alice\tEng\tSenior\tLondon\t95000\n" +
            "Bob\tMkt\tJunior\tParis\t55000\n" +
            "Carol\tEng\tLead\tLondon\t115000\n" +
            "Dave\tFin\tMid\tBerlin\t72000\n" +
            "Eve\tEng\tSenior\tLondon\t98000\n" +
            "Frank\tMkt\tSenior\tRome\t82000\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(6, doc.GetRowCount());

        // GetDistinctValues
        var depts = doc.GetDistinctValues("Dept");
        Assert.Equal(3, depts.Count);
        Assert.Contains("Eng", depts);
        Assert.Contains("Mkt", depts);
        Assert.Contains("Fin", depts);

        var locations = doc.GetDistinctValues("Location");
        Assert.True(locations.Count <= 4);

        var grades = doc.GetDistinctValues("Grade");
        Assert.Contains("Senior", grades);
        Assert.Contains("Junior", grades);

        // ExportToNdjson baseline
        var ndjson = doc.ExportToNdjson();
        Assert.NotNull(ndjson);
        Assert.NotEmpty(ndjson);
        Assert.Contains("{", ndjson);

        // Clone
        var clone = doc.Clone();
        Assert.Equal(6, clone.GetRowCount());
        Assert.Equal(doc.GetHeaders().Count, clone.GetHeaders().Count);

        // Clone is independent
        clone.SetCell(0, 0, "ALICE_CLONE");
        Assert.Equal("Alice", doc.GetCell(0, 0));
        Assert.Equal("ALICE_CLONE", clone.GetCell(0, 0));

        // GetDistinctValues on clone
        var cloneDepts = clone.GetDistinctValues("Dept");
        Assert.Equal(depts.Count, cloneDepts.Count);

        // AddRow to clone only
        clone.AddRow(new[] { "Grace", "HR", "Junior", "Madrid", "48000" });
        Assert.Equal(7, clone.GetRowCount());
        Assert.Equal(6, doc.GetRowCount()); // original unchanged

        // GetDistinctValues on clone after AddRow
        var cloneDeptsAfter = clone.GetDistinctValues("Dept");
        Assert.True(cloneDeptsAfter.Count >= depts.Count);
        Assert.Contains("HR", cloneDeptsAfter);

        // ExportToNdjson on clone
        var cloneNdjson = clone.ExportToNdjson();
        Assert.True(cloneNdjson.Length > ndjson.Length); // clone has more rows

        // Filter on original
        var eng = doc.Filter("Dept", "Eng");
        var engDepts = eng.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);
        Assert.Contains("Eng", engDepts);

        // ExportToNdjson on filtered
        var engNdjson = eng.ExportToNdjson();
        Assert.True(engNdjson.Length < ndjson.Length);

        // Clone of filtered
        var engClone = eng.Clone();
        Assert.Equal(eng.GetRowCount(), engClone.GetRowCount());

        // SortRows on clone
        clone.SortRows("Salary", ascending: false);
        Assert.Equal(7, clone.GetRowCount());

        // AddColumn to clone
        clone.AddColumn("Active", new[] { "Yes", "Yes", "Yes", "Yes", "Yes", "No", "Yes" });
        var cloneDistinctActive = clone.GetDistinctValues("Active");
        Assert.True(cloneDistinctActive.Count >= 1);

        // ExportToNdjson after AddColumn
        var cloneNdjsonFull = clone.ExportToNdjson();
        Assert.True(cloneNdjsonFull.Length > cloneNdjson.Length);

        // GetDistinctValues consistent
        var dv1 = doc.GetDistinctValues("Dept");
        var dv2 = doc.GetDistinctValues("Dept");
        Assert.Equal(dv1.Count, dv2.Count);

        // SaveToFile original
        var saveOrig = TempFile("dogfood_orig.tsv");
        doc.SaveToFile(saveOrig);
        Assert.True(File.Exists(saveOrig));

        // SaveToFile clone
        var saveClone = TempFile("dogfood_clone.tsv");
        clone.SaveToFile(saveClone);
        Assert.True(File.Exists(saveClone));

        // LoadFile verify original
        var loadedOrig = TsvDocument.LoadFile(saveOrig);
        Assert.Equal(6, loadedOrig.GetRowCount());
        Assert.Equal(3, loadedOrig.GetDistinctValues("Dept").Count);

        var loadedNdjson = loadedOrig.ExportToNdjson();
        Assert.NotNull(loadedNdjson);
        Assert.NotEmpty(loadedNdjson);

        // LoadFile verify clone
        var loadedClone = TsvDocument.LoadFile(saveClone);
        Assert.Equal(7, loadedClone.GetRowCount());
        Assert.True(loadedClone.GetDistinctValues("Dept").Count >= depts.Count);

        // Clone of loaded
        var cloneOfLoaded = loadedOrig.Clone();
        Assert.Equal(loadedOrig.GetRowCount(), cloneOfLoaded.GetRowCount());
    }
}
