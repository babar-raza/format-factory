// Tests for TsvDocument.SortByColumn, GroupBy, GetGroupCounts deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R209

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R209: Tests for TsvDocument.SortByColumn, GroupBy, GetGroupCounts deeper.
/// SortByColumn(colName, ascending): returns new TsvDocument sorted by column.
/// GroupBy(colName): returns dictionary of group key → list of row indices.
/// GetGroupCounts(colName): returns dictionary of group key → count.
/// Covers: SortByColumn non-null; SortByColumn no-throw; SortByColumn same row count;
/// SortByColumn ascending correct; SortByColumn descending correct;
/// SortByColumn consistent; SortByColumn save-load; SortByColumn numeric correct;
/// GroupBy non-null; GroupBy no-throw; GroupBy Engineering count correct;
/// GroupBy Finance count correct; GroupBy consistent; GroupBy total rows match;
/// GroupBy save-load; GroupBy all keys present;
/// GetGroupCounts non-null; GetGroupCounts no-throw; GetGroupCounts values correct;
/// GetGroupCounts consistent; GetGroupCounts save-load; GetGroupCounts sum=rowCount;
/// dogfood LoadFile→SortByColumn→GroupBy→GetGroupCounts→SaveToFile pipeline.
/// </summary>
public class TsvR209SortByColumnAndGroupByDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR209SortByColumnAndGroupByDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR209_" + Guid.NewGuid().ToString("N"));
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
            "Name\tDepartment\tScore\tCity\n" +
            "Alice\tEngineering\t92\tLondon\n" +
            "Bob\tMarketing\t78\tParis\n" +
            "Carol\tEngineering\t88\tLondon\n" +
            "Dave\tFinance\t85\tBerlin\n" +
            "Eve\tEngineering\t95\tLondon\n" +
            "Frank\tMarketing\t72\tRome\n" +
            "Grace\tFinance\t81\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortByColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void SortByColumn_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.SortByColumn("Score", ascending: true));
    }

    [Fact]
    public void SortByColumn_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.SortByColumn("Score", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortByColumn_SameRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        Assert.Equal(doc.GetRowCount(), sorted.GetRowCount());
    }

    [Fact]
    public void SortByColumn_Ascending_FirstHasLowest()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        var values = sorted.GetNumericColumn("Score");
        // First value should be <= last
        Assert.True(values[0] <= values[values.Count - 1]);
    }

    [Fact]
    public void SortByColumn_Descending_FirstHasHighest()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sorted = doc.SortByColumn("Score", ascending: false);
        var values = sorted.GetNumericColumn("Score");
        Assert.True(values[0] >= values[values.Count - 1]);
    }

    [Fact]
    public void SortByColumn_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var s1 = doc.SortByColumn("Name", ascending: true);
        var s2 = doc.SortByColumn("Name", ascending: true);
        Assert.Equal(s1.GetRowCount(), s2.GetRowCount());
    }

    [Fact]
    public void SortByColumn_SaveLoad_SameCount()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        var path = TempFile("sorted_save.tsv");
        sorted.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(sorted.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void SortByColumn_Numeric_Ascending_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        var values = sorted.GetNumericColumn("Score");
        for (int i = 0; i < values.Count - 1; i++)
            Assert.True(values[i] <= values[i + 1]);
    }

    // -------------------------------------------------------------------------
    // GroupBy
    // -------------------------------------------------------------------------

    [Fact]
    public void GroupBy_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.GroupBy("Department"));
    }

    [Fact]
    public void GroupBy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.GroupBy("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GroupBy_Engineering_ThreeRows()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var groups = doc.GroupBy("Department");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.Equal(3, groups["Engineering"].Count);
    }

    [Fact]
    public void GroupBy_Finance_TwoRows()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var groups = doc.GroupBy("Department");
        Assert.True(groups.ContainsKey("Finance"));
        Assert.Equal(2, groups["Finance"].Count);
    }

    [Fact]
    public void GroupBy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var g1 = doc.GroupBy("Department");
        var g2 = doc.GroupBy("Department");
        Assert.Equal(g1.Count, g2.Count);
    }

    [Fact]
    public void GroupBy_TotalRows_Match()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var groups = doc.GroupBy("Department");
        int total = 0;
        foreach (var kvp in groups)
            total += kvp.Value.Count;
        Assert.Equal(doc.GetRowCount(), total);
    }

    [Fact]
    public void GroupBy_AllKeys_Present()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var groups = doc.GroupBy("Department");
        Assert.True(groups.ContainsKey("Engineering"));
        Assert.True(groups.ContainsKey("Marketing"));
        Assert.True(groups.ContainsKey("Finance"));
    }

    // -------------------------------------------------------------------------
    // GetGroupCounts
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGroupCounts_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        Assert.NotNull(doc.GetGroupCounts("Department"));
    }

    [Fact]
    public void GetGroupCounts_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var ex = Record.Exception(() => doc.GetGroupCounts("Department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetGroupCounts_Engineering_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var counts = doc.GetGroupCounts("Department");
        Assert.Equal(3, counts["Engineering"]);
    }

    [Fact]
    public void GetGroupCounts_Marketing_Correct()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var counts = doc.GetGroupCounts("Department");
        Assert.Equal(2, counts["Marketing"]);
    }

    [Fact]
    public void GetGroupCounts_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var c1 = doc.GetGroupCounts("Department");
        var c2 = doc.GetGroupCounts("Department");
        Assert.Equal(c1["Engineering"], c2["Engineering"]);
    }

    [Fact]
    public void GetGroupCounts_Sum_EqualsRowCount()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var counts = doc.GetGroupCounts("Department");
        int total = 0;
        foreach (var kvp in counts)
            total += kvp.Value;
        Assert.Equal(doc.GetRowCount(), total);
    }

    [Fact]
    public void GetGroupCounts_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateEmployeeTsv());
        var before = doc.GetGroupCounts("Department")["Engineering"];
        var path = TempFile("gc_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetGroupCounts("Department")["Engineering"]);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortByColumn_GroupBy_GetGroupCounts_SaveToFile_Pipeline()
    {
        // Build comprehensive TSV
        var path = TempFile("dogfood_staff.tsv");
        var content =
            "Employee\tTeam\tLevel\tLocation\tRating\n" +
            "Alice\tPlatform\tSenior\tLondon\t92\n" +
            "Bob\tData\tJunior\tParis\t74\n" +
            "Carol\tPlatform\tLead\tLondon\t98\n" +
            "Dave\tFinance\tMid\tBerlin\t81\n" +
            "Eve\tData\tSenior\tLondon\t89\n" +
            "Frank\tPlatform\tSenior\tRome\t87\n" +
            "Grace\tFinance\tJunior\tMadrid\t76\n" +
            "Hector\tData\tMid\tTokyo\t83\n";
        File.WriteAllText(path, content);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRowCount());

        // SortByColumn — ascending Rating
        var sorted = doc.SortByColumn("Rating", ascending: true);
        Assert.Equal(8, sorted.GetRowCount());
        var sortedRatings = sorted.GetNumericColumn("Rating");
        for (int i = 0; i < sortedRatings.Count - 1; i++)
            Assert.True(sortedRatings[i] <= sortedRatings[i + 1]);

        // SortByColumn — descending Rating
        var sortedDesc = doc.SortByColumn("Rating", ascending: false);
        var ratingsDesc = sortedDesc.GetNumericColumn("Rating");
        Assert.True(ratingsDesc[0] >= ratingsDesc[ratingsDesc.Count - 1]);

        // SortByColumn consistent
        Assert.Equal(sorted.GetRowCount(), doc.SortByColumn("Rating", ascending: true).GetRowCount());

        // GroupBy Team
        var teamGroups = doc.GroupBy("Team");
        Assert.NotNull(teamGroups);
        Assert.True(teamGroups.ContainsKey("Platform"));
        Assert.True(teamGroups.ContainsKey("Data"));
        Assert.True(teamGroups.ContainsKey("Finance"));
        Assert.Equal(3, teamGroups["Platform"].Count);
        Assert.Equal(3, teamGroups["Data"].Count);
        Assert.Equal(2, teamGroups["Finance"].Count);

        // Total rows match
        int total = 0;
        foreach (var kvp in teamGroups) total += kvp.Value.Count;
        Assert.Equal(8, total);

        // GroupBy Level
        var levelGroups = doc.GroupBy("Level");
        Assert.True(levelGroups.ContainsKey("Senior"));
        Assert.Equal(3, levelGroups["Senior"].Count);

        // GetGroupCounts Team
        var teamCounts = doc.GetGroupCounts("Team");
        Assert.Equal(3, teamCounts["Platform"]);
        Assert.Equal(3, teamCounts["Data"]);
        Assert.Equal(2, teamCounts["Finance"]);

        // Sum = 8
        int countTotal = 0;
        foreach (var kvp in teamCounts) countTotal += kvp.Value;
        Assert.Equal(8, countTotal);

        // GetGroupCounts Location
        var locationCounts = doc.GetGroupCounts("Location");
        Assert.True(locationCounts.ContainsKey("London"));
        Assert.Equal(3, locationCounts["London"]); // Alice, Carol, Eve

        // Consistent
        Assert.Equal(teamCounts["Platform"], doc.GetGroupCounts("Team")["Platform"]);

        // AddRow and verify group counts update
        doc.AddRow(new[] { "Iris", "Platform", "Mid", "Sydney", "86" });
        Assert.Equal(9, doc.GetRowCount());
        var updatedCounts = doc.GetGroupCounts("Team");
        Assert.Equal(4, updatedCounts["Platform"]);

        // SaveToFile
        var savePath = TempFile("dogfood_staff_out.tsv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(savePath);
        Assert.Equal(9, loaded.GetRowCount());

        // GetGroupCounts on loaded
        var loadedCounts = loaded.GetGroupCounts("Team");
        Assert.Equal(4, loadedCounts["Platform"]);
        Assert.Equal(3, loadedCounts["Data"]);

        // SortByColumn on loaded
        var loadedSorted = loaded.SortByColumn("Rating", ascending: true);
        Assert.Equal(9, loadedSorted.GetRowCount());

        // GroupBy on loaded
        var loadedGroups = loaded.GroupBy("Level");
        Assert.True(loadedGroups.ContainsKey("Senior"));

        // Final save
        var path2 = TempFile("dogfood_staff_v2.tsv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = TsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetGroupCounts("Team")["Platform"], loaded2.GetGroupCounts("Team")["Platform"]);
    }
}
