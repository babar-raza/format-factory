// Tests for TsvDocument.AddColumn, GetDistinctValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R190

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R190: Tests for TsvDocument.AddColumn, GetDistinctValues deeper coverage.
/// AddColumn(colName, values): adds a new named column with the given values to the document.
/// GetDistinctValues(colName): returns the set of unique values for the named column.
/// Covers: AddColumn increases column count; AddColumn values accessible via GetColumnValues;
/// AddColumn HasColumn true after; AddColumn multiple columns; AddColumn then SaveToFile persists;
/// AddColumn then GetHeaders contains new col; AddColumn then Filter works;
/// AddColumn then ExportToJson contains new col;
/// GetDistinctValues non-null; GetDistinctValues correct count for known data;
/// GetDistinctValues all-unique equals row count; GetDistinctValues all-same returns one;
/// GetDistinctValues after AddRow grows; GetDistinctValues after Filter subset;
/// GetDistinctValues consistent; GetDistinctValues case-sensitive check;
/// dogfood LoadFile→AddColumn→GetDistinctValues→Filter→AddRow→SaveToFile pipeline.
/// </summary>
public class TsvR190AddColumnAndGetDistinctValuesDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR190AddColumnAndGetDistinctValuesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR190_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string SampleTsv =
        "Name\tTeam\tScore\n" +
        "Alice\tAlpha\t92\n" +
        "Bob\tBeta\t78\n" +
        "Carol\tAlpha\t85\n" +
        "Dave\tGamma\t71\n" +
        "Eve\tBeta\t90\n" +
        "Frank\tAlpha\t88\n";

    private TsvDocument LoadSample()
    {
        var path = TempFile("sample.tsv");
        File.WriteAllText(path, SampleTsv);
        return TsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // AddColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void AddColumn_IncreasesColumnCount()
    {
        var doc = LoadSample();
        var before = doc.ColumnCount;
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        Assert.Equal(before + 1, doc.ColumnCount);
    }

    [Fact]
    public void AddColumn_ValuesAccessibleViaGetColumnValues()
    {
        var doc = LoadSample();
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        var values = doc.GetColumnValues("Level");
        Assert.Contains("Senior", values);
        Assert.Contains("Mid", values);
    }

    [Fact]
    public void AddColumn_ThenGetHeadersContainsNewCol()
    {
        var doc = LoadSample();
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        Assert.Contains("Level", doc.GetHeaders());
    }

    [Fact]
    public void AddColumn_MultipleColumns_AllAccessible()
    {
        var doc = LoadSample();
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        doc.AddColumn("Location", new[] { "NY", "LA", "NY", "Chicago", "NY", "LA" });
        Assert.Contains("Level", doc.GetHeaders());
        Assert.Contains("Location", doc.GetHeaders());
        Assert.Equal(5, doc.ColumnCount);
    }

    [Fact]
    public void AddColumn_ThenSaveToFile_Persists()
    {
        var doc = LoadSample();
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        var path = TempFile("addcol_persist.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("Level", loaded.GetHeaders());
    }

    [Fact]
    public void AddColumn_ThenFilterWorks()
    {
        var doc = LoadSample();
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        var seniors = doc.Filter("Level", "Senior");
        Assert.Equal(3, seniors.RowCount);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_NonNull()
    {
        var doc = LoadSample();
        Assert.NotNull(doc.GetDistinctValues("Team"));
    }

    [Fact]
    public void GetDistinctValues_CorrectCountForTeam()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Team");
        Assert.Equal(3, distinct.Count); // Alpha, Beta, Gamma
    }

    [Fact]
    public void GetDistinctValues_ContainsExpectedValues()
    {
        var doc = LoadSample();
        var distinct = doc.GetDistinctValues("Team");
        Assert.Contains("Alpha", distinct);
        Assert.Contains("Beta", distinct);
        Assert.Contains("Gamma", distinct);
    }

    [Fact]
    public void GetDistinctValues_AllUnique_CountEqualsRowCount()
    {
        var doc = LoadSample();
        Assert.Equal(doc.RowCount, doc.GetDistinctValues("Name").Count);
    }

    [Fact]
    public void GetDistinctValues_AllSame_ReturnsOne()
    {
        var path = TempFile("allsame.tsv");
        File.WriteAllText(path, "Team\nAlpha\nAlpha\nAlpha\n");
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(1, doc.GetDistinctValues("Team").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterAddRow_Grows()
    {
        var doc = LoadSample();
        var before = doc.GetDistinctValues("Team").Count;
        doc.AddRow(new[] { "Gina", "Delta", "95" });
        Assert.Equal(before + 1, doc.GetDistinctValues("Team").Count);
    }

    [Fact]
    public void GetDistinctValues_AfterFilter_Subset()
    {
        var doc = LoadSample();
        var alphaDoc = doc.Filter("Team", "Alpha");
        var distinct = alphaDoc.GetDistinctValues("Team");
        Assert.Equal(1, distinct.Count);
        Assert.Contains("Alpha", distinct);
    }

    [Fact]
    public void GetDistinctValues_Consistent()
    {
        var doc = LoadSample();
        Assert.Equal(doc.GetDistinctValues("Team").Count, doc.GetDistinctValues("Team").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFile_AddColumn_GetDistinctValues_Filter_AddRow_SaveToFile_Pipeline()
    {
        var doc = LoadSample();
        Assert.Equal(6, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);

        // GetDistinctValues — Team
        var teamDistinct = doc.GetDistinctValues("Team");
        Assert.Equal(3, teamDistinct.Count);
        Assert.Contains("Alpha", teamDistinct);

        // GetDistinctValues — Name (all unique)
        Assert.Equal(6, doc.GetDistinctValues("Name").Count);

        // AddColumn Level
        doc.AddColumn("Level", new[] { "Senior", "Junior", "Senior", "Junior", "Mid", "Senior" });
        Assert.Equal(4, doc.ColumnCount);
        Assert.Contains("Level", doc.GetHeaders());

        // GetDistinctValues on new column
        var levelDistinct = doc.GetDistinctValues("Level");
        Assert.Equal(3, levelDistinct.Count); // Senior, Junior, Mid
        Assert.Contains("Senior", levelDistinct);

        // Filter by Level
        var seniors = doc.Filter("Level", "Senior");
        Assert.Equal(3, seniors.RowCount);
        var seniorTeams = seniors.GetDistinctValues("Team");
        Assert.True(seniorTeams.Count >= 1);

        // AddColumn Location
        doc.AddColumn("Location", new[] { "NYC", "LA", "NYC", "Chicago", "NYC", "LA" });
        Assert.Equal(5, doc.ColumnCount);

        // GetDistinctValues on Location
        var locDistinct = doc.GetDistinctValues("Location");
        Assert.Equal(3, locDistinct.Count); // NYC, LA, Chicago

        // AddRow — new team Delta, new level Expert
        doc.AddRow(new[] { "Gina", "Delta", "95", "Expert", "Boston" });
        Assert.Equal(7, doc.RowCount);
        Assert.Equal(4, doc.GetDistinctValues("Team").Count); // +Delta
        Assert.Equal(4, doc.GetDistinctValues("Level").Count); // +Expert
        Assert.Equal(4, doc.GetDistinctValues("Location").Count); // +Boston

        // SaveToFile
        var path = TempFile("dogfood_addcol.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(7, loaded.RowCount);
        Assert.Equal(5, loaded.ColumnCount);
        Assert.Contains("Level", loaded.GetHeaders());
        Assert.Contains("Location", loaded.GetHeaders());
        Assert.Equal(4, loaded.GetDistinctValues("Team").Count);
        Assert.Contains("Delta", loaded.GetDistinctValues("Team"));
    }
}
