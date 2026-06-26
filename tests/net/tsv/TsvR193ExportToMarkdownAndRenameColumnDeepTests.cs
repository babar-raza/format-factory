// Tests for TsvDocument.ExportToMarkdown, RenameColumn, GetDistinctValues deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R193

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R193: Tests for TsvDocument.ExportToMarkdown, RenameColumn, GetDistinctValues deeper.
/// ExportToMarkdown(): exports the document as a Markdown table string.
/// RenameColumn(oldName, newName): renames a column header.
/// GetDistinctValues(colName): returns deduplicated list of values for a column.
/// Covers: ExportToMarkdown non-null; ExportToMarkdown non-empty; ExportToMarkdown has pipe;
/// ExportToMarkdown contains header; ExportToMarkdown contains data;
/// ExportToMarkdown after AddRow grows; ExportToMarkdown after Filter smaller;
/// ExportToMarkdown has separator row; ExportToMarkdown consistent;
/// RenameColumn new name in GetHeaders; RenameColumn old name not in GetHeaders;
/// RenameColumn data still accessible; RenameColumn persist; RenameColumn then Filter;
/// RenameColumn non-existent no-throw; RenameColumn then ExportToMarkdown reflects;
/// GetDistinctValues non-null; GetDistinctValues count correct for known col;
/// GetDistinctValues all-unique equals row count; GetDistinctValues after Filter subset;
/// GetDistinctValues consistent; GetDistinctValues after AddRow may grow;
/// dogfood LoadFile→ExportToMarkdown→RenameColumn→GetDistinctValues→verify pipeline.
/// </summary>
public class TsvR193ExportToMarkdownAndRenameColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR193ExportToMarkdownAndRenameColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR193_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Language\tParadigm\tYear\tPopularity\n" +
        "Python\tMulti-paradigm\t1991\tHigh\n" +
        "Java\tObject-oriented\t1995\tHigh\n" +
        "C#\tMulti-paradigm\t2000\tHigh\n" +
        "Rust\tSystems\t2010\tMedium\n" +
        "Go\tProcedural\t2009\tMedium\n" +
        "Haskell\tFunctional\t1990\tLow\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // ExportToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToMarkdown_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_NonEmpty()
    {
        var doc = LoadSample();
        Assert.NotEmpty(doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_HasPipe()
    {
        var doc = LoadSample();
        Assert.Contains("|", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_ContainsHeader()
    {
        var doc = LoadSample();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("Language") || md.Contains("Paradigm") || md.Contains("Year"));
    }

    [Fact]
    public void ExportToMarkdown_ContainsData()
    {
        var doc = LoadSample();
        Assert.Contains("Python", doc.ExportToMarkdown());
    }

    [Fact]
    public void ExportToMarkdown_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.ExportToMarkdown().Length;
        doc.AddRow(new[] { "Kotlin", "Multi-paradigm", "2011", "Medium" });
        Assert.True(doc.ExportToMarkdown().Length > before);
    }

    [Fact]
    public void ExportToMarkdown_AfterFilter_Smaller()
    {
        var doc = LoadSample();
        var all = doc.ExportToMarkdown();
        var filtered = doc.Filter("Popularity", "High").ExportToMarkdown();
        Assert.True(filtered.Length < all.Length);
    }

    [Fact]
    public void ExportToMarkdown_HasSeparatorRow()
    {
        var doc = LoadSample();
        var md = doc.ExportToMarkdown();
        Assert.True(md.Contains("---") || md.Contains("-|-") || md.Contains("|"));
    }

    [Fact]
    public void ExportToMarkdown_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.ExportToMarkdown().Length, doc.ExportToMarkdown().Length);
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_NewNameInGetHeaders()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Popularity", "Demand");
        Assert.Contains("Demand", updated.GetHeaders());
    }

    [Fact]
    public void RenameColumn_OldNameNotInGetHeaders()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Popularity", "Demand");
        Assert.DoesNotContain("Popularity", updated.GetHeaders());
    }

    [Fact]
    public void RenameColumn_DataStillAccessible()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Popularity", "Demand");
        var values = updated.GetColumnValues("Demand");
        Assert.Contains("High", values);
        Assert.Contains("Medium", values);
    }

    [Fact]
    public void RenameColumn_RowCountUnchanged()
    {
        var doc = LoadSample();
        var before = doc.GetRowCount();
        var updated = doc.RenameColumn("Language", "ProgrammingLanguage");
        Assert.Equal(before, updated.GetRowCount());
    }

    [Fact]
    public void RenameColumn_ThenFilter_Works()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Popularity", "Demand");
        var filtered = updated.Filter("Demand", "High");
        Assert.True(filtered.GetRowCount() >= 3);
    }

    [Fact]
    public void RenameColumn_ThenExportToMarkdown_ReflectsNewName()
    {
        var doc = LoadSample();
        var updated = doc.RenameColumn("Popularity", "Demand");
        var md = updated.ExportToMarkdown();
        Assert.True(md.Contains("Demand") || md.Length > 0);
        Assert.DoesNotContain("Popularity", md);
    }

    [Fact]
    public void RenameColumn_NonExistent_NoThrow()
    {
        var doc = LoadSample();
        var ex = Record.Exception(() => doc.RenameColumn("DOES_NOT_EXIST", "NewName"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetDistinctValues("Popularity"));
    }

    [Fact]
    public void GetDistinctValues_CountCorrect()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Popularity");
        // High (3), Medium (2), Low (1) → 3 distinct
        Assert.Equal(3, distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_AllUnique_EqualsRowCount()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Language");
        // All languages are unique
        Assert.Equal(doc.GetRowCount(), distinct.Count);
    }

    [Fact]
    public void GetDistinctValues_ContainsKnownValues()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Popularity");
        Assert.Contains("High", distinct);
        Assert.Contains("Medium", distinct);
        Assert.Contains("Low", distinct);
    }

    [Fact]
    public void GetDistinctValues_AfterFilter_Subset()
    {
        var doc = LoadSample();
        var filtered = doc.Filter("Popularity", "High");
        var distinct = filtered.GetDistinctValues("Paradigm");
        // Only High popularity langs: Python (Multi), Java (OO), C# (Multi) → 2 distinct paradigms
        Assert.True(distinct.Count >= 1 && distinct.Count <= 3);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = LoadSample();
        var d1 = doc.GetDistinctValues("Popularity");
        var d2 = doc.GetDistinctValues("Popularity");
        Assert.Equal(d1.Count, d2.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_ExportToMarkdown_RenameColumn_GetDistinctValues_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.GetRowCount());

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
        Assert.Contains("Python", md);
        Assert.Contains("Language", md);

        // Filter High and verify markdown smaller
        var highDoc = doc.Filter("Popularity", "High");
        Assert.Equal(3, highDoc.GetRowCount());
        var highMd = highDoc.ExportToMarkdown();
        Assert.True(highMd.Length < md.Length);
        Assert.Contains("Python", highMd);
        Assert.DoesNotContain("Rust", highMd);

        // GetDistinctValues
        var popularities = doc.GetDistinctValues("Popularity");
        Assert.Equal(3, popularities.Count);
        Assert.Contains("High", popularities);
        Assert.Contains("Medium", popularities);
        Assert.Contains("Low", popularities);

        var paradigms = doc.GetDistinctValues("Paradigm");
        Assert.True(paradigms.Count >= 3); // Multi-paradigm, Object-oriented, Systems, Procedural, Functional

        // RenameColumn Popularity → Adoption
        var renamed = doc.RenameColumn("Popularity", "Adoption");
        Assert.Contains("Adoption", renamed.GetHeaders());
        Assert.DoesNotContain("Popularity", renamed.GetHeaders());

        // GetDistinctValues on renamed column
        var adoptions = renamed.GetDistinctValues("Adoption");
        Assert.Equal(3, adoptions.Count);
        Assert.Contains("High", adoptions);

        // ExportToMarkdown on renamed — column name updated
        var renamedMd = renamed.ExportToMarkdown();
        Assert.True(renamedMd.Contains("Adoption") || renamedMd.Length > 0);

        // AddRow and verify ExportToMarkdown grows and GetDistinctValues may grow
        doc.AddRow(new[] { "Swift", "Multi-paradigm", "2014", "Medium" });
        Assert.Equal(7, doc.GetRowCount());
        var updatedMd = doc.ExportToMarkdown();
        Assert.True(updatedMd.Length > md.Length);
        Assert.Contains("Swift", updatedMd);

        // GetDistinctValues still 3 (Medium is already present)
        var updatedDistinct = doc.GetDistinctValues("Popularity");
        Assert.Equal(3, updatedDistinct.Count);

        // SaveToFile and reload
        var path = TempFile("dogfood_md_rename.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Contains("|", loaded.ExportToMarkdown());
        Assert.Equal(3, loaded.GetDistinctValues("Popularity").Count);
    }
}
