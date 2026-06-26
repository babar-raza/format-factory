// Tests for TsvDocument.Merge, GetCell deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R182

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R182: Tests for TsvDocument.Merge, GetCell deeper coverage.
/// Merge(other): returns a new document combining rows from both documents.
/// GetCell(rowIndex, colIndex): returns the cell value at the given row/col.
/// GetCell(rowIndex, colName): returns the cell value at the given row by column name.
/// Covers: Merge non-null; Merge count equals sum of both; Merge contains rows from both;
/// Merge GetColumnValues has all; Merge after Filter; Merge headers from first doc;
/// GetCell by index non-null; GetCell by index correct value; GetCell first row;
/// GetCell last row; GetCell middle row; GetCell after SetCellValue reflects change;
/// GetCell by name non-null; GetCell by name correct value;
/// dogfood LoadContent->Merge->GetCell->GetColumnValues->Verify pipeline.
/// </summary>
public class TsvR182MergeAndGetCellDeepTests
{
    private const string Doc1Content = "Name\tDept\tScore\nAlice\tEng\t92\nBob\tFinance\t85\nCarol\tEng\t78";
    private const string Doc2Content = "Name\tDept\tScore\nDave\tHR\t91\nEve\tFinance\t88\nFrank\tEng\t79";

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_NonNull()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        Assert.NotNull(doc1.Merge(doc2));
    }

    [Fact]
    public void Merge_CountEqualsSumOfBoth()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        Assert.Equal(doc1.RowCount + doc2.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_ContainsRowsFromBoth()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Merge_GetColumnValues_HasAllValues()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Equal(6, names.Count);
    }

    [Fact]
    public void Merge_HeadersFromFirstDoc()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        Assert.Contains("Name", merged.Headers);
        Assert.Contains("Dept", merged.Headers);
        Assert.Contains("Score", merged.Headers);
    }

    [Fact]
    public void Merge_AfterFilter_CorrectCount()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);
        var engOnly1 = doc1.Filter(r => r.GetCellValue("Dept") == "Eng");
        var engOnly2 = doc2.Filter(r => r.GetCellValue("Dept") == "Eng");
        var mergedEng = engOnly1.Merge(engOnly2);
        Assert.Equal(3, mergedEng.RowCount); // Alice, Carol, Frank
    }

    [Fact]
    public void Merge_WithEmptyDoc_SameAsOriginal()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var emptyContent = "Name\tDept\tScore";
        var empty = TsvDocument.LoadContent(emptyContent);
        var merged = doc1.Merge(empty);
        Assert.Equal(doc1.RowCount, merged.RowCount);
    }

    // -------------------------------------------------------------------------
    // GetCell by index
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_ByIndex_NonNull()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.NotNull(doc.GetCell(0, 0));
    }

    [Fact]
    public void GetCell_ByIndex_FirstRow_Correct()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal("Alice", doc.GetCell(0, 0));
        Assert.Equal("Eng", doc.GetCell(0, 1));
        Assert.Equal("92", doc.GetCell(0, 2));
    }

    [Fact]
    public void GetCell_ByIndex_LastRow_Correct()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal("Carol", doc.GetCell(2, 0));
    }

    [Fact]
    public void GetCell_ByIndex_MiddleRow_Correct()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal("Bob", doc.GetCell(1, 0));
        Assert.Equal("Finance", doc.GetCell(1, 1));
    }

    [Fact]
    public void GetCell_AfterSetCellValue_ReflectsChange()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        doc.SetCellValue(0, 0, "ALICE_UPDATED");
        Assert.Equal("ALICE_UPDATED", doc.GetCell(0, 0));
    }

    // -------------------------------------------------------------------------
    // GetCell by column name
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCell_ByName_NonNull()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.NotNull(doc.GetCell(0, "Name"));
    }

    [Fact]
    public void GetCell_ByName_CorrectValue()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        Assert.Equal("Alice", doc.GetCell(0, "Name"));
        Assert.Equal("Eng", doc.GetCell(0, "Dept"));
        Assert.Equal("92", doc.GetCell(0, "Score"));
    }

    [Fact]
    public void GetCell_ByName_AllRows_Accessible()
    {
        var doc = TsvDocument.LoadContent(Doc1Content);
        for (var i = 0; i < doc.RowCount; i++)
        {
            Assert.NotNull(doc.GetCell(i, "Name"));
            Assert.NotNull(doc.GetCell(i, "Dept"));
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_Merge_GetCell_GetColumnValues_Verify_Pipeline()
    {
        var doc1 = TsvDocument.LoadContent(Doc1Content);
        var doc2 = TsvDocument.LoadContent(Doc2Content);

        Assert.Equal(3, doc1.RowCount);
        Assert.Equal(3, doc2.RowCount);

        // GetCell on doc1
        Assert.Equal("Alice", doc1.GetCell(0, "Name"));
        Assert.Equal("Carol", doc1.GetCell(2, 0));

        // Merge
        var merged = doc1.Merge(doc2);
        Assert.Equal(6, merged.RowCount);

        // GetCell on merged
        Assert.Equal("Alice", merged.GetCell(0, "Name"));
        Assert.Equal("Dave", merged.GetCell(3, "Name")); // Dave from doc2

        // GetColumnValues on merged
        var allNames = merged.GetColumnValues("Name");
        Assert.Equal(6, allNames.Count);
        Assert.Contains("Alice", allNames);
        Assert.Contains("Frank", allNames);

        // Filter merged then merge result
        var engAll = merged.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, engAll.RowCount);

        var engNames = engAll.GetColumnValues("Name");
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
        Assert.Contains("Frank", engNames);
        Assert.DoesNotContain("Dave", engNames);

        // GetCell after filter
        Assert.Equal("Alice", engAll.GetCell(0, "Name"));
    }
}
