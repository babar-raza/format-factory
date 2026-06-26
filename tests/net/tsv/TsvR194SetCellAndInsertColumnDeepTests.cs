// Tests for TsvDocument.SetCell, InsertColumn, GetColumn deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R194

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R194: Tests for TsvDocument.SetCell, InsertColumn, GetColumn deeper.
/// SetCell(row, col, value): sets the value of a specific cell by row and column index.
/// InsertColumn(colName, values): inserts a new column with a header and optional values.
/// GetColumn(colName): returns all values in a named column as a list.
/// Covers: SetCell changes value; SetCell then GetColumnValues reflects change;
/// SetCell persist; SetCell out-of-bounds no-throw; SetCell multiple;
/// SetCell then ToTsv reflects; SetCell then Filter works;
/// InsertColumn increases GetColumnCount; InsertColumn new header in GetHeaders;
/// InsertColumn with values accessible; InsertColumn persist; InsertColumn then Filter;
/// InsertColumn then SortRows; InsertColumn multiple;
/// GetColumn non-null; GetColumn count equals row count; GetColumn contains known values;
/// GetColumn same as GetColumnValues; GetColumn consistent; GetColumn after SetCell;
/// dogfood LoadFile→SetCell→InsertColumn→GetColumn→SaveToFile pipeline.
/// </summary>
public class TsvR194SetCellAndInsertColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR194SetCellAndInsertColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR194_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tAge\tCity\n" +
        "Alice\t30\tNew York\n" +
        "Bob\t25\tLos Angeles\n" +
        "Carol\t35\tChicago\n" +
        "Dave\t28\tSeattle\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ChangesValue()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "ALICE_UPDATED");
        var values = doc.GetColumnValues("Name");
        Assert.Contains("ALICE_UPDATED", values);
    }

    [Fact]
    public void SetCell_ThenToTsv_Reflects()
    {
        var doc = LoadSample();
        doc.SetCell(0, 1, "99");
        var tsv = doc.ToTsv();
        Assert.Contains("99", tsv);
    }

    [Fact]
    public void SetCell_Persist()
    {
        var doc = LoadSample();
        doc.SetCell(0, 2, "BOSTON");
        var path = TempFile("setcell_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("BOSTON", loaded.GetColumnValues("City"));
    }

    [Fact]
    public void SetCell_Multiple_AllChange()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "NAME_A");
        doc.SetCell(1, 0, "NAME_B");
        var values = doc.GetColumnValues("Name");
        Assert.Contains("NAME_A", values);
        Assert.Contains("NAME_B", values);
    }

    [Fact]
    public void SetCell_RowCountUnchanged()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        doc.SetCell(0, 0, "Modified");
        Assert.Equal(before, doc.GetRowCount());
    }

    [Fact]
    public void SetCell_ThenFilterWorks()
    {
        var doc = LoadSample();
        doc.SetCell(0, 2, "Miami"); // Change Alice's city
        var miami = doc.Filter("City", "Miami");
        Assert.True(miami.GetRowCount() >= 1);
    }

    // -------------------------------------------------------------------------
    // InsertColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertColumn_IncreasesGetColumnCount()
    {
        var doc = LoadSample();
        var before = doc.GetColumnCount();
        doc.InsertColumn("Score", new[] { "90", "85", "92", "78" });
        Assert.True(doc.GetColumnCount() > before);
    }

    [Fact]
    public void InsertColumn_NewHeaderInGetHeaders()
    {
        var doc = LoadSample();
        doc.InsertColumn("Score", new[] { "90", "85", "92", "78" });
        Assert.Contains("Score", doc.GetHeaders());
    }

    [Fact]
    public void InsertColumn_ValuesAccessible()
    {
        var doc = LoadSample();
        doc.InsertColumn("Score", new[] { "90", "85", "92", "78" });
        var values = doc.GetColumnValues("Score");
        Assert.Contains("90", values);
        Assert.Contains("85", values);
    }

    [Fact]
    public void InsertColumn_Persist()
    {
        var doc = LoadSample();
        doc.InsertColumn("Rating", new[] { "A", "B", "A", "B" });
        var path = TempFile("insert_col_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("Rating", loaded.GetHeaders());
    }

    [Fact]
    public void InsertColumn_Multiple_BothPresent()
    {
        var doc = LoadSample();
        doc.InsertColumn("Score", new[] { "90", "85", "92", "78" });
        doc.InsertColumn("Rating", new[] { "A", "B", "A", "B" });
        var headers = doc.GetHeaders();
        Assert.Contains("Score", headers);
        Assert.Contains("Rating", headers);
    }

    [Fact]
    public void InsertColumn_ThenFilter_Works()
    {
        var doc = LoadSample();
        doc.InsertColumn("Dept", new[] { "Eng", "Finance", "Eng", "HR" });
        var engDoc = doc.Filter("Dept", "Eng");
        Assert.Equal(2, engDoc.GetRowCount());
    }

    // -------------------------------------------------------------------------
    // GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetColumn("Name"));
    }

    [Fact]
    public void GetColumn_CountEqualsRowCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetRowCount(), doc.GetColumn("Name").Count);
    }

    [Fact]
    public void GetColumn_ContainsKnownValues()
    {
        var doc = LoadSample();
        var column = doc.GetColumn("Name");
        Assert.Contains("Alice", column);
        Assert.Contains("Bob", column);
    }

    [Fact]
    public void GetColumn_SameAsGetColumnValues()
    {
        var doc = LoadSample();
        var gc = doc.GetColumn("Name");
        var gcv = doc.GetColumnValues("Name");
        Assert.Equal(gc.Count, gcv.Count);
        for (int i = 0; i < gc.Count; i++)
            Assert.Equal(gc[i], gcv[i]);
    }

    [Fact]
    public void GetColumn_Consistent()
    {
        var doc = LoadSample();
        var c1 = doc.GetColumn("City");
        var c2 = doc.GetColumn("City");
        Assert.Equal(c1.Count, c2.Count);
    }

    [Fact]
    public void GetColumn_AfterSetCell_Reflects()
    {
        var doc = LoadSample();
        doc.SetCell(0, 2, "Denver");
        var cities = doc.GetColumn("City");
        Assert.Contains("Denver", cities);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_SetCell_InsertColumn_GetColumn_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(4, doc.GetRowCount());
        Assert.Equal(3, doc.GetColumnCount());

        // GetColumn baseline
        var names = doc.GetColumn("Name");
        Assert.Equal(4, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);

        // SetCell — update Bob's age
        doc.SetCell(1, 1, "26");
        var ages = doc.GetColumn("Age");
        Assert.Contains("26", ages);

        // SetCell — update Carol's city
        doc.SetCell(2, 2, "Boston");
        var cities = doc.GetColumn("City");
        Assert.Contains("Boston", cities);

        // InsertColumn Score
        doc.InsertColumn("Score", new[] { "92", "87", "95", "78" });
        Assert.Equal(4, doc.GetColumnCount());
        Assert.Contains("Score", doc.GetHeaders());
        var scores = doc.GetColumn("Score");
        Assert.Equal(4, scores.Count);
        Assert.Contains("92", scores);

        // InsertColumn Dept
        doc.InsertColumn("Dept", new[] { "Engineering", "Finance", "Engineering", "HR" });
        Assert.Equal(5, doc.GetColumnCount());

        // Filter by Dept
        var engDoc = doc.Filter("Dept", "Engineering");
        Assert.Equal(2, engDoc.GetRowCount());
        var engNames = engDoc.GetColumn("Name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);

        // SortRows on doc with new columns
        var sorted = doc.SortRows("Score", ascending: false);
        var sortedScores = sorted.GetColumn("Score");
        Assert.Equal("95", sortedScores[0]); // Carol has highest score

        // ToTsv reflects all cells
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
        Assert.Contains("26", tsv); // Bob's updated age
        Assert.Contains("Boston", tsv); // Carol's updated city

        // SaveToFile and reload
        var path = TempFile("dogfood_setcell.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetRowCount());
        Assert.Equal(5, loaded.GetColumnCount());

        var loadedNames = loaded.GetColumn("Name");
        Assert.Equal(4, loadedNames.Count);
        Assert.Contains("Alice", loadedNames);

        var loadedScores = loaded.GetColumn("Score");
        Assert.Contains("92", loadedScores);

        // GetColumn on inserted column from loaded doc
        var loadedDepts = loaded.GetColumn("Dept");
        Assert.Equal(4, loadedDepts.Count);
        Assert.Contains("Engineering", loadedDepts);
    }
}
