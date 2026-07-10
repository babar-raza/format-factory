// FormatFactory.Csv.Tests — AddRow / SetCell mutation round-trip tests.
// Skill: /add-roundtrip-test  format=csv  lang=dotnet  edit_operation=AddRow+SetCell
// Sprint: FOSS-CSV-DOTNET-ROUNDTRIP-001

using System;
using System.IO;
using FormatFactory.Csv;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// Round-trip tests: load → mutate (AddRow / SetCell) → save → reload → assert change visible.
/// </summary>
public class CsvAddRowRoundtripTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_csv_rt_{Guid.NewGuid():N}.csv");

    // ---- AddRow roundtrip ----

    [Fact]
    public void AddRow_Roundtrip_NewRowVisibleAfterReload()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\nBob,25\n", hasHeaders: true);
            doc.AddRow(new[] { "Carol", "35" });
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(3, reloaded.RowCount);
            Assert.Equal("Carol", reloaded.Rows[2][0]);
            Assert.Equal("35",    reloaded.Rows[2][1]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void AddRow_Roundtrip_RowCountIncreases()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\n", hasHeaders: true);
            Assert.Equal(1, doc.RowCount);
            doc.AddRow(new[] { "Bob", "25" });
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(2, reloaded.RowCount);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void AddRow_Roundtrip_HeadersPreserved()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\n", hasHeaders: true);
            doc.AddRow(new[] { "Bob", "25" });
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.NotNull(reloaded.Headers);
            Assert.Equal("Name", reloaded.Headers![0]);
            Assert.Equal("Age",  reloaded.Headers![1]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void AddRow_Roundtrip_ExistingRowsUntouched()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\nBob,25\n", hasHeaders: true);
            doc.AddRow(new[] { "Carol", "35" });
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal("Alice", reloaded.Rows[0][0]);
            Assert.Equal("30",    reloaded.Rows[0][1]);
            Assert.Equal("Bob",   reloaded.Rows[1][0]);
            Assert.Equal("25",    reloaded.Rows[1][1]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- SetCell roundtrip ----

    [Fact]
    public void SetCell_Roundtrip_EditedValueVisibleAfterReload()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\nBob,25\n", hasHeaders: true);
            doc.SetCell(0, 1, "99"); // change Alice's age to 99
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal("99", reloaded.Rows[0][1]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SetCell_Roundtrip_OtherCellsUntouched()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Age\nAlice,30\nBob,25\n", hasHeaders: true);
            doc.SetCell(1, 0, "Charlie"); // rename Bob to Charlie
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal("Charlie", reloaded.Rows[1][0]);
            Assert.Equal("25",      reloaded.Rows[1][1]); // age unchanged
            Assert.Equal("Alice",   reloaded.Rows[0][0]); // row 0 unchanged
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Combined AddRow + SetCell roundtrip ----

    [Fact]
    public void AddRowAndSetCell_Roundtrip_BothChangesVisible()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Score\nAlice,80\n", hasHeaders: true);
            doc.AddRow(new[] { "Bob", "70" });
            doc.SetCell(0, 1, "95"); // update Alice's score

            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(2,     reloaded.RowCount);
            Assert.Equal("95",  reloaded.Rows[0][1]); // Alice's updated score
            Assert.Equal("Bob", reloaded.Rows[1][0]); // new row preserved
            Assert.Equal("70",  reloaded.Rows[1][1]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void AddRowAndSetCell_Roundtrip_HeadersIntact()
    {
        var path = TempPath();
        try
        {
            var doc = CsvDocument.Load("Name,Score\nAlice,80\n", hasHeaders: true);
            doc.AddRow(new[] { "Bob", "70" });
            doc.SetCell(0, 0, "Alicia");
            doc.SaveToFile(path);

            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal("Name",  reloaded.Headers![0]);
            Assert.Equal("Score", reloaded.Headers![1]);
            Assert.Equal("Alicia", reloaded.Rows[0][0]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
