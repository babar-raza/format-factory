// Tests for CsvDocument.SortByColumn, RenameColumn, GetColumnCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R211

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R211: Tests for CsvDocument.SortByColumn, RenameColumn, GetColumnCount deeper.
/// SortByColumn(colName, ascending): returns new CsvDocument sorted by column.
/// RenameColumn(oldName, newName): renames a header column.
/// GetColumnCount(): returns the number of columns.
/// Covers: SortByColumn non-null; SortByColumn no-throw; SortByColumn same row count;
/// SortByColumn ascending correct; SortByColumn descending correct;
/// SortByColumn consistent; SortByColumn save-load; SortByColumn numeric order;
/// RenameColumn no-throw; RenameColumn new name accessible; RenameColumn old name gone;
/// RenameColumn value preserved; RenameColumn consistent; RenameColumn save-load;
/// RenameColumn then SortByColumn works; RenameColumn then Filter works;
/// GetColumnCount non-zero; GetColumnCount correct; GetColumnCount no-throw;
/// GetColumnCount consistent; GetColumnCount after AddColumn grows;
/// GetColumnCount after RemoveColumn shrinks; GetColumnCount save-load;
/// dogfood LoadFile→SortByColumn→RenameColumn→GetColumnCount→SaveToFile pipeline.
/// </summary>
public class CsvR211SortByColumnAndRenameColumnDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR211SortByColumnAndRenameColumnDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR211_" + Guid.NewGuid().ToString("N"));
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
            "Name,Department,Score,Salary\n" +
            "Alice,Engineering,92,95000\n" +
            "Bob,Marketing,78,55000\n" +
            "Carol,Engineering,88,115000\n" +
            "Dave,Finance,85,72000\n" +
            "Eve,Engineering,95,98000\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // SortByColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void SortByColumn_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.NotNull(doc.SortByColumn("Score", ascending: true));
    }

    [Fact]
    public void SortByColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.SortByColumn("Score", ascending: true));
        Assert.Null(ex);
    }

    [Fact]
    public void SortByColumn_SameRowCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        Assert.Equal(doc.GetRowCount(), sorted.GetRowCount());
    }

    [Fact]
    public void SortByColumn_Ascending_FirstLowest()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        var values = sorted.GetNumericColumn("Score");
        Assert.True(values[0] <= values[values.Count - 1]);
    }

    [Fact]
    public void SortByColumn_Descending_FirstHighest()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sorted = doc.SortByColumn("Score", ascending: false);
        var values = sorted.GetNumericColumn("Score");
        Assert.True(values[0] >= values[values.Count - 1]);
    }

    [Fact]
    public void SortByColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var s1 = doc.SortByColumn("Score", ascending: true);
        var s2 = doc.SortByColumn("Score", ascending: true);
        Assert.Equal(s1.GetRowCount(), s2.GetRowCount());
    }

    [Fact]
    public void SortByColumn_SaveLoad_SameCount()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sorted = doc.SortByColumn("Salary", ascending: true);
        var path = TempFile("sorted_save.csv");
        sorted.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(sorted.GetRowCount(), loaded.GetRowCount());
    }

    [Fact]
    public void SortByColumn_Numeric_Ascending_InOrder()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var sorted = doc.SortByColumn("Score", ascending: true);
        var values = sorted.GetNumericColumn("Score");
        for (int i = 0; i < values.Count - 1; i++)
            Assert.True(values[i] <= values[i + 1]);
    }

    // -------------------------------------------------------------------------
    // RenameColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void RenameColumn_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.RenameColumn("Score", "Points"));
        Assert.Null(ex);
    }

    [Fact]
    public void RenameColumn_NewName_Accessible()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RenameColumn("Score", "Points");
        var headers = doc.GetHeaders();
        Assert.Contains("Points", headers);
    }

    [Fact]
    public void RenameColumn_OldName_Gone()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RenameColumn("Score", "Points");
        var headers = doc.GetHeaders();
        Assert.DoesNotContain("Score", headers);
    }

    [Fact]
    public void RenameColumn_Values_Preserved()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnValues("Score");
        doc.RenameColumn("Score", "Points");
        var after = doc.GetColumnValues("Points");
        Assert.Equal(before.Count, after.Count);
        Assert.Equal(before[0], after[0]);
    }

    [Fact]
    public void RenameColumn_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RenameColumn("Score", "Rating");
        var headers = doc.GetHeaders();
        Assert.Contains("Rating", headers);
    }

    [Fact]
    public void RenameColumn_SaveLoad_Persists()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RenameColumn("Department", "Division");
        var path = TempFile("rename_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Contains("Division", loaded.GetHeaders());
        Assert.DoesNotContain("Department", loaded.GetHeaders());
    }

    [Fact]
    public void RenameColumn_Then_SortByColumn_Works()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        doc.RenameColumn("Score", "Pts");
        var ex = Record.Exception(() => doc.SortByColumn("Pts", ascending: true));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NonZero()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.True(doc.GetColumnCount() > 0);
    }

    [Fact]
    public void GetColumnCount_Correct()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        // Name, Department, Score, Salary = 4 columns
        Assert.Equal(4, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var ex = Record.Exception(() => doc.GetColumnCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCount_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_After_AddColumn_Grows()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCount();
        doc.AddColumn("Bonus", new[] { "5000", "3000", "7000", "4000", "6000" });
        Assert.Equal(before + 1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_After_RemoveColumn_Shrinks()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCount();
        doc.RemoveColumn("Salary");
        Assert.Equal(before - 1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateSampleCsv());
        var before = doc.GetColumnCount();
        var path = TempFile("cc_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SortByColumn_RenameColumn_GetColumnCount_SaveToFile_Pipeline()
    {
        // Build comprehensive CSV
        var path = TempFile("dogfood_products.csv");
        var content =
            "Product,Category,UnitPrice,StockQty,Rating\n" +
            "Widget-A,Electronics,29.99,500,4.2\n" +
            "Gadget-B,Electronics,79.99,200,4.7\n" +
            "Tool-C,Hardware,14.99,800,3.9\n" +
            "Device-D,Electronics,149.99,100,4.5\n" +
            "Part-E,Hardware,9.99,1200,4.0\n" +
            "Module-F,Software,199.99,50,4.8\n" +
            "Cable-G,Hardware,4.99,2000,3.7\n";
        File.WriteAllText(path, content);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(7, doc.GetRowCount());

        // GetColumnCount
        Assert.Equal(5, doc.GetColumnCount());

        // SortByColumn — ascending UnitPrice
        var sortedAsc = doc.SortByColumn("UnitPrice", ascending: true);
        Assert.Equal(7, sortedAsc.GetRowCount());
        var prices = sortedAsc.GetNumericColumn("UnitPrice");
        for (int i = 0; i < prices.Count - 1; i++)
            Assert.True(prices[i] <= prices[i + 1]);

        // SortByColumn — descending Rating
        var sortedDesc = doc.SortByColumn("Rating", ascending: false);
        var ratings = sortedDesc.GetNumericColumn("Rating");
        Assert.True(ratings[0] >= ratings[ratings.Count - 1]);

        // SortByColumn consistent
        Assert.Equal(sortedAsc.GetRowCount(), doc.SortByColumn("UnitPrice", ascending: true).GetRowCount());

        // RenameColumn — UnitPrice → Price
        doc.RenameColumn("UnitPrice", "Price");
        var headers = doc.GetHeaders();
        Assert.Contains("Price", headers);
        Assert.DoesNotContain("UnitPrice", headers);
        Assert.Equal(5, doc.GetColumnCount()); // count unchanged

        // Values preserved after rename
        var priceValues = doc.GetColumnValues("Price");
        Assert.Equal(7, priceValues.Count);

        // RenameColumn — StockQty → Quantity
        doc.RenameColumn("StockQty", "Quantity");
        Assert.Contains("Quantity", doc.GetHeaders());
        Assert.Equal(5, doc.GetColumnCount());

        // SortByColumn after rename works
        var sortedByPrice = doc.SortByColumn("Price", ascending: true);
        Assert.Equal(7, sortedByPrice.GetRowCount());

        // AddColumn — TotalValue
        doc.AddColumn("TotalValue", new[] { "14995", "15998", "11992", "14999", "11988", "9999.5", "9980" });
        Assert.Equal(6, doc.GetColumnCount());

        // RemoveColumn — TotalValue
        doc.RemoveColumn("TotalValue");
        Assert.Equal(5, doc.GetColumnCount());

        // SaveToFile
        var savePath = TempFile("dogfood_products_out.csv");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(savePath);
        Assert.Equal(7, loaded.GetRowCount());
        Assert.Equal(5, loaded.GetColumnCount());
        Assert.Contains("Price", loaded.GetHeaders());
        Assert.Contains("Quantity", loaded.GetHeaders());

        // SortByColumn on loaded
        var loadedSorted = loaded.SortByColumn("Price", ascending: false);
        var loadedPrices = loadedSorted.GetNumericColumn("Price");
        Assert.True(loadedPrices[0] >= loadedPrices[loadedPrices.Count - 1]);

        // RenameColumn on loaded
        loaded.RenameColumn("Category", "Type");
        Assert.Contains("Type", loaded.GetHeaders());
        Assert.Equal(5, loaded.GetColumnCount());

        // GetGroupCounts equivalent via Filter
        var electronics = loaded.Filter("Type", "Electronics");
        Assert.Equal(3, electronics.GetRowCount());

        // Final save
        var path2 = TempFile("dogfood_products_v2.csv");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = CsvDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRowCount(), loaded2.GetRowCount());
        Assert.Equal(loaded.GetColumnCount(), loaded2.GetColumnCount());
        Assert.Contains("Type", loaded2.GetHeaders());
    }
}
