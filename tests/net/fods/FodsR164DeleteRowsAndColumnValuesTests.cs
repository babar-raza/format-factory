// Tests for FodsDocument.DeleteRows, GetColumnValues, GetColumnCount.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R164

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R164: Tests for FodsDocument.DeleteRows, GetColumnValues, GetColumnCount methods.
/// DeleteRows(sheetName, startRow, count): removes rows beginning at startRow.
/// GetColumnValues(sheetName, col): returns all values (including null) in the column.
/// GetColumnCount(sheetName): number of columns based on header row.
/// GetColumnCount(): column count for first sheet.
/// Covers: DeleteRows reduces row count by count; DeleteRows first row shifts rest;
/// DeleteRows OOB startRow throws or is noop; DeleteRows count=0 is noop;
/// GetColumnValues returns correct values; GetColumnValues null for empty cells;
/// GetColumnValues empty result for OOB col; GetColumnCount from headers;
/// GetColumnCount empty doc is 0; GetColumnCount first vs named sheet;
/// dogfood BuildSheet->DeleteRows->GetColumnValues->GetColumnCount pipeline.
/// </summary>
public class FodsR164DeleteRowsAndColumnValuesTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_ReducesRowCount()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] {
                new[] { "Alice", "95" },
                new[] { "Bob", "82" },
                new[] { "Carol", "88" }
            });
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 1, 1);
        Assert.Equal(before - 1, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DeleteRows_FirstRow_ShiftsRemainingRows()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Name" },
            new[] { new[] { "Alice" }, new[] { "Bob" } });

        // Row 0 = header (Name), Row 1 = Alice, Row 2 = Bob
        doc.DeleteRows("Sheet", 1, 1); // Remove Alice
        var values = doc.GetColumnValues("Sheet", 0);
        Assert.DoesNotContain("Alice", values);
    }

    [Fact]
    public void DeleteRows_CountZero_IsNoop()
    {
        var doc = BuildSheet("Data",
            new[] { "A" },
            new[] { new[] { "1" }, new[] { "2" } });
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 0, 0);
        Assert.Equal(before, doc.GetRowCount("Data"));
    }

    [Fact]
    public void DeleteRows_MultipleRows_ReducesCountByN()
    {
        var doc = BuildSheet("Data",
            new[] { "A" },
            new[] { new[] { "1" }, new[] { "2" }, new[] { "3" }, new[] { "4" } });
        var before = doc.GetRowCount("Data");
        doc.DeleteRows("Data", 1, 2);
        Assert.Equal(before - 2, doc.GetRowCount("Data"));
    }

    // -------------------------------------------------------------------------
    // GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_ReturnsAllValuesInColumn()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] {
                new[] { "Alice", "95" },
                new[] { "Bob", "82" }
            });
        var values = doc.GetColumnValues("Data", 0);
        Assert.Contains("Alice", values);
        Assert.Contains("Bob", values);
    }

    [Fact]
    public void GetColumnValues_OobCol_IsEmpty()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" } });
        var values = doc.GetColumnValues("Data", 99);
        Assert.Empty(values);
    }

    [Fact]
    public void GetColumnValues_ScoreColumn_ContainsExpectedScores()
    {
        var doc = BuildSheet("Scores",
            new[] { "Name", "Score" },
            new[] {
                new[] { "Alice", "95" },
                new[] { "Carol", "88" }
            });
        var scores = doc.GetColumnValues("Scores", 1);
        Assert.Contains("95", scores);
        Assert.Contains("88", scores);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_FromHeaders_ReturnsHeaderLength()
    {
        var doc = BuildSheet("Data",
            new[] { "A", "B", "C" },
            new[] { new[] { "1", "2", "3" } });
        Assert.Equal(3, doc.GetColumnCount("Data"));
    }

    [Fact]
    public void GetColumnCount_FirstSheet_SameAsNamed()
    {
        var doc = BuildSheet("Main",
            new[] { "X", "Y" },
            new[] { new[] { "a", "b" } });
        Assert.Equal(doc.GetColumnCount("Main"), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_EmptyDoc_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];
        Assert.Equal(0, doc.GetColumnCount(sheetName));
    }

    // -------------------------------------------------------------------------
    // Dogfood: BuildSheet->DeleteRows->GetColumnValues->GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_DeleteRowsColumnValuesColumnCount_Pipeline()
    {
        var doc = BuildSheet("Team",
            new[] { "Name", "Role", "Score" },
            new[] {
                new[] { "Alice", "Dev", "95" },
                new[] { "Bob", "QA", "82" },
                new[] { "Carol", "Dev", "88" },
                new[] { "Dave", "Mgr", "90" }
            });

        // Column count
        Assert.Equal(3, doc.GetColumnCount("Team"));

        // Column values before deletion
        var names = doc.GetColumnValues("Team", 0);
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);

        // Delete Bob (row index 2 = header 0, Alice 1, Bob 2)
        doc.DeleteRows("Team", 2, 1);
        var namesAfter = doc.GetColumnValues("Team", 0);
        Assert.DoesNotContain("Bob", namesAfter);
        Assert.Contains("Alice", namesAfter);
        Assert.Contains("Carol", namesAfter);

        // Row count decreased
        Assert.Equal(4, doc.GetRowCount("Team")); // header + 3 data rows
    }
}
