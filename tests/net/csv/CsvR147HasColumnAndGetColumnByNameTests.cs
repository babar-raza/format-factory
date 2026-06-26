// Tests for CsvDocument.HasColumn, GetColumn(string), GetColumn(int), ColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R147

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R147: Tests for CsvDocument.HasColumn, GetColumn(string), GetColumn(int), ColumnCount.
/// HasColumn(name): true if the named column exists in Headers.
/// GetColumn(string name): returns column values by header name.
/// GetColumn(int index): returns column values by zero-based index.
/// ColumnCount: total number of columns.
/// Covers: HasColumn true for existing column; HasColumn false for missing column;
/// HasColumn case-sensitive check; GetColumn(string) returns correct values;
/// GetColumn(string) count equals RowCount; GetColumn(int) for first column;
/// GetColumn(int) for last column; GetColumn(int) OOB returns empty;
/// ColumnCount equals 3 for 3-column CSV; ColumnCount with hasHeaders=false;
/// GetColumn after Filter returns subset; HasColumn with no headers is false;
/// dogfood Load->HasColumn->GetColumn->Filter pipeline.
/// </summary>
public class CsvR147HasColumnAndGetColumnByNameTests
{
    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    // -------------------------------------------------------------------------
    // HasColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingColumn_IsTrue()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_MissingColumn_IsFalse()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        Assert.False(doc.HasColumn("Missing"));
        Assert.False(doc.HasColumn("Department"));
    }

    [Fact]
    public void HasColumn_CaseSensitive_MismatchIsFalse()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        // "name" (lowercase) vs "Name" (title case)
        Assert.False(doc.HasColumn("name"));
    }

    [Fact]
    public void HasColumn_NoHeaders_IsFalse()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: false);
        Assert.False(doc.HasColumn("Name"));
    }

    // -------------------------------------------------------------------------
    // GetColumn(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByName_ReturnsCorrectValues()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var names = doc.GetColumn("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void GetColumnByName_CountEqualsRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var depts = doc.GetColumn("Dept");
        Assert.Equal(doc.RowCount, depts.Count);
    }

    [Fact]
    public void GetColumnByName_DeptColumn_ContainsExpectedValues()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var depts = doc.GetColumn("Dept");
        Assert.Contains("Eng", depts);
        Assert.Contains("Finance", depts);
    }

    [Fact]
    public void GetColumnByName_ScoreColumn_ContainsNumericStrings()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var scores = doc.GetColumn("Score");
        Assert.Contains("95", scores);
        Assert.Contains("82", scores);
    }

    // -------------------------------------------------------------------------
    // GetColumn(int)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnByIndex_FirstColumn_ContainsNames()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var col0 = doc.GetColumn(0);
        Assert.Contains("Alice", col0);
        Assert.Contains("Bob", col0);
    }

    [Fact]
    public void GetColumnByIndex_LastColumn_ContainsScores()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var col2 = doc.GetColumn(2);
        Assert.Contains("95", col2);
        Assert.Contains("82", col2);
    }

    [Fact]
    public void GetColumnByIndex_OobIndex_ReturnsEmpty()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var oob = doc.GetColumn(999);
        Assert.Empty(oob);
    }

    // -------------------------------------------------------------------------
    // ColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void ColumnCount_ThreeColumnCsv_IsThree()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_FromFirstRow()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: false);
        // ColumnCount comes from first row (3 values)
        Assert.Equal(3, doc.ColumnCount);
    }

    // -------------------------------------------------------------------------
    // GetColumn after Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnAfterFilter_ReturnsSubset()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        var engNames = eng.GetColumn(0);
        Assert.Equal(2, engNames.Count);
        Assert.Contains("Alice", engNames);
        Assert.Contains("Carol", engNames);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->HasColumn->GetColumn->Filter pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_HasColumnGetColumnFilterPipeline()
    {
        var doc = CsvDocument.Load(FourRowCsv, hasHeaders: true);

        // Verify columns exist
        Assert.True(doc.HasColumn("Name"));
        Assert.True(doc.HasColumn("Dept"));
        Assert.True(doc.HasColumn("Score"));
        Assert.False(doc.HasColumn("Salary"));

        // Get all departments
        var depts = doc.GetColumn("Dept");
        Assert.Equal(4, depts.Count);
        Assert.Contains("Eng", depts);

        // Filter and verify column values
        var finance = doc.Filter(row => row.Length > 1 && row[1] == "Finance");
        Assert.Equal(2, finance.RowCount);

        var financeNames = finance.GetColumn(0);
        Assert.Contains("Bob", financeNames);
        Assert.Contains("Dave", financeNames);
        Assert.DoesNotContain("Alice", financeNames);
    }
}
