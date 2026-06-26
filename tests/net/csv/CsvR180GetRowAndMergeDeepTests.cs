// Tests for CsvDocument.GetRow, Merge, GetColumnValues deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R180

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R180: Tests for CsvDocument.GetRow, Merge, GetColumnValues deeper coverage.
/// GetRow(index): returns the list of cell values at the given row index.
/// Merge(other): returns a new document combining records from both documents.
/// GetColumnValues(colName): returns all values in the named column.
/// Covers: GetRow non-null; GetRow count equals ColumnCount; GetRow first row correct;
/// GetRow last row correct; GetRow middle row correct; Merge non-null;
/// Merge count equals sum of both; Merge contains rows from both;
/// Merge GetColumnValues has all values; Merge after Filter;
/// GetColumnValues all present; GetColumnValues count correct;
/// dogfood LoadContent->GetRow->Filter->Merge->GetColumnValues->Verify pipeline.
/// </summary>
public class CsvR180GetRowAndMergeDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string Doc1Content = "Name,Dept\nAlice,Eng\nBob,Finance\nCarol,Eng";
    private const string Doc2Content = "Name,Dept\nDave,HR\nEve,Finance\nFrank,Eng";

    public CsvR180GetRowAndMergeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR180_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // GetRow
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRow_NonNull()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        Assert.NotNull(doc.GetRow(0));
    }

    [Fact]
    public void GetRow_CountEqualsColumnCount()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        Assert.Equal(doc.ColumnCount, doc.GetRow(0).Count);
    }

    [Fact]
    public void GetRow_FirstRow_ContainsExpectedValues()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        var row = doc.GetRow(0);
        Assert.Contains("Alice", row);
    }

    [Fact]
    public void GetRow_LastRow_ContainsExpectedValues()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        var row = doc.GetRow(2);
        Assert.Contains("Carol", row);
    }

    [Fact]
    public void GetRow_MiddleRow_ContainsExpectedValues()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        var row = doc.GetRow(1);
        Assert.Contains("Bob", row);
    }

    [Fact]
    public void GetRow_EachRow_HasTwoValues()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        for (var i = 0; i < doc.RowCount; i++)
            Assert.Equal(2, doc.GetRow(i).Count);
    }

    // -------------------------------------------------------------------------
    // Merge
    // -------------------------------------------------------------------------

    [Fact]
    public void Merge_NonNull()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        Assert.NotNull(doc1.Merge(doc2));
    }

    [Fact]
    public void Merge_CountEqualsSumOfBoth()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        Assert.Equal(doc1.RowCount + doc2.RowCount, merged.RowCount);
    }

    [Fact]
    public void Merge_ContainsRowsFromBoth()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
        Assert.Contains("Frank", names);
    }

    [Fact]
    public void Merge_GetColumnValues_HasAllValues()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        var depts = merged.GetDistinctValues("Dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
        Assert.Contains("HR", depts);
    }

    [Fact]
    public void Merge_AfterFilter()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        var engOnly1 = doc1.Filter(r => r.GetCellValue("Dept") == "Eng");
        var engOnly2 = doc2.Filter(r => r.GetCellValue("Dept") == "Eng");
        var mergedEng = engOnly1.Merge(engOnly2);
        Assert.Equal(3, mergedEng.RowCount); // Alice, Carol, Frank
        var names = mergedEng.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_AllPresent()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        var names = doc.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void GetColumnValues_CountCorrect()
    {
        var doc = CsvDocument.LoadContent(Doc1Content);
        var names = doc.GetColumnValues("Name");
        Assert.Equal(3, names.Count);
    }

    [Fact]
    public void GetColumnValues_AfterMerge_IncludesAll()
    {
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        var merged = doc1.Merge(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Equal(6, names.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_GetRow_Filter_Merge_GetColumnValues_Verify_Pipeline()
    {
        // Load both docs
        var doc1 = CsvDocument.LoadContent(Doc1Content);
        var doc2 = CsvDocument.LoadContent(Doc2Content);
        Assert.Equal(3, doc1.RowCount);
        Assert.Equal(3, doc2.RowCount);

        // GetRow on first doc
        var r0 = doc1.GetRow(0);
        Assert.NotNull(r0);
        Assert.Contains("Alice", r0);
        var r2 = doc1.GetRow(2);
        Assert.Contains("Carol", r2);

        // Merge
        var merged = doc1.Merge(doc2);
        Assert.Equal(6, merged.RowCount);

        // GetColumnValues on merged
        var allNames = merged.GetColumnValues("Name");
        Assert.Equal(6, allNames.Count);
        Assert.Contains("Alice", allNames);
        Assert.Contains("Dave", allNames);

        // Filter merged
        var engAll = merged.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(3, engAll.RowCount); // Alice, Carol, Frank

        // GetRow on filtered
        var engRow0 = engAll.GetRow(0);
        Assert.NotNull(engRow0);

        // GetColumnValues on filtered
        var engNames = engAll.GetColumnValues("Name");
        Assert.Equal(3, engNames.Count);
        Assert.DoesNotContain("Dave", engNames);
        Assert.DoesNotContain("Eve", engNames);

        // Filter then merge
        var hrMerged = doc2.Filter(r => r.GetCellValue("Dept") == "HR");
        var finalMerge = engAll.Merge(hrMerged);
        Assert.Equal(4, finalMerge.RowCount);
    }
}
