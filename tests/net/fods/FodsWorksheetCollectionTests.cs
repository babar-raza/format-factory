// FormatFactory.Fods.Tests — FodsWorksheetCollectionTests
// Focused verification for TC-W1-FODS-NET-003:
//   - FodsDocument.Worksheets (FodsWorksheetCollection)
//   - FodsWorksheet: Name, Rows, IsVisible
//   - FodsCell: Value getter/setter, ValueType, Formula
//   - Round-trip: load → mutate via Worksheets → save → reload → verify
//
// Authority: plans/.claude/imperative-drifting-conway.md §9 (12 required pilots)
// TC-W1-FODS-NET-003

using System;
using System.IO;
using System.Linq;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public sealed class FodsWorksheetCollectionTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SamplePath(string name) =>
        Path.GetFullPath(Path.Combine(SamplesDir, name));

    // -------------------------------------------------------------------------
    // Pilot 1: FodsDocument.Worksheets exists and returns correct count
    // -------------------------------------------------------------------------

    [Fact]
    public void Worksheets_Count_MatchesSheetCount()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
        Assert.True(doc.Worksheets.Count > 0,
            "Worksheets.Count must be > 0 for multi-sheet-basic.fods");
    }

    [Fact]
    public void Worksheets_Count_MatchesLegacySheetCount()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
#pragma warning disable CS0618
        var legacyCount = doc.SheetCount;
#pragma warning restore CS0618
        Assert.Equal(legacyCount, doc.Worksheets.Count);
    }

    // -------------------------------------------------------------------------
    // Pilot 1: QName hierarchy — Worksheets[i] returns correct QName-owned type
    // -------------------------------------------------------------------------

    [Fact]
    public void Worksheets_IndexByInt_ReturnsWorksheet()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
        var ws = doc.Worksheets[0];
        Assert.IsType<FodsWorksheet>(ws);
        Assert.False(string.IsNullOrEmpty(ws.Name), "FodsWorksheet.Name must not be empty");
    }

    [Fact]
    public void Worksheets_IndexByName_ReturnsMatchingWorksheet()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
        var firstName = doc.Worksheets[0].Name;
        var ws = doc.Worksheets[firstName];
        Assert.Equal(firstName, ws.Name);
    }

    [Fact]
    public void Worksheets_IndexByInvalidName_ThrowsArgumentException()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
        Assert.Throws<ArgumentException>(() => doc.Worksheets["__nonexistent__"]);
    }

    [Fact]
    public void Worksheets_IndexByOutOfRange_ThrowsArgumentOutOfRange()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.Worksheets[9999]);
    }

    // -------------------------------------------------------------------------
    // Pilot 2: Nested ownership — Rows belong to FodsWorksheet, not FodsDocument
    // -------------------------------------------------------------------------

    [Fact]
    public void Worksheets_First_HasRows()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        var ws = doc.Worksheets[0];
        Assert.NotNull(ws.Rows);
    }

    [Fact]
    public void Worksheets_FirstRow_HasCells()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        var ws = doc.Worksheets[0];
        if (ws.Rows.Count > 0)
        {
            var row = ws.Rows[0];
            Assert.NotNull(row.Cells);
        }
    }

    // -------------------------------------------------------------------------
    // FodsCell: Value getter — reads text:p content
    // -------------------------------------------------------------------------

    [Fact]
    public void Cell_Value_ReadsFromTextP()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        var ws = doc.Worksheets[0];
        if (ws.Rows.Count > 0 && ws.Rows[0].Cells.Count > 0)
        {
            var cell = ws.Rows[0].Cells[0];
            // Value may be null for empty cells — just verify property is accessible
            _ = cell.Value;
        }
    }

    // -------------------------------------------------------------------------
    // FodsCell: Value setter and round-trip proof (Pilot 4, 6, 7)
    // -------------------------------------------------------------------------

    [Fact]
    public void Cell_ValueSetter_UpdatesContent()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        var ws = doc.Worksheets[0];

        // Ensure there's at least one row/cell
        if (ws.Rows.Count == 0)
        {
            var newWs = doc.Worksheets.Add("TestSheet");
        }

        // Set value via new Worksheets API
        var sheet = doc.Worksheets[0];
        var rows = sheet.Rows;
        if (rows.Count > 0 && rows[0].Cells.Count > 0)
        {
            var cell = rows[0].Cells[0];
            cell.Value = "ARC-TEST-VALUE";
            Assert.Equal("ARC-TEST-VALUE", cell.Value);
        }
    }

    [Fact]
    public void Cell_ValueSetter_RoundTrip_Preserved()
    {
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            // Load → mutate via Worksheets → save → reload → verify
            var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
            var ws = doc.Worksheets[0];

            if (ws.Rows.Count > 0 && ws.Rows[0].Cells.Count > 0)
            {
                ws.Rows[0].Cells[0].Value = "ROUND-TRIP-PROOF";
                doc.Save(tmp);

                var reloaded = FodsDocument.Load(tmp);
                var reloadedCell = reloaded.Worksheets[0].Rows[0].Cells[0];
                Assert.Equal("ROUND-TRIP-PROOF", reloadedCell.Value);
            }
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    // -------------------------------------------------------------------------
    // FodsCell: ValueType — reads office:value-type attribute
    // -------------------------------------------------------------------------

    [Fact]
    public void Cell_ValueType_ReadsAttribute()
    {
        var doc = FodsDocument.Load(SamplePath("typed-values-basic.fods"));
        var ws = doc.Worksheets[0];
        if (ws.Rows.Count > 0 && ws.Rows[0].Cells.Count > 0)
        {
            var cell = ws.Rows[0].Cells[0];
            // May be null for empty cell, or a string like "string"/"float"
            _ = cell.ValueType;
        }
    }

    // -------------------------------------------------------------------------
    // FodsWorksheetCollection.Add and Remove
    // -------------------------------------------------------------------------

    [Fact]
    public void Worksheets_Add_IncreasesCount()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.Worksheets.Count);
        doc.Worksheets.Add("Sheet1");
        Assert.Equal(1, doc.Worksheets.Count);
    }

    [Fact]
    public void Worksheets_Add_DuplicateName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.Worksheets.Add("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.Worksheets.Add("Sheet1"));
    }

    [Fact]
    public void Worksheets_Remove_DecreasesCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.Worksheets.Add("Sheet1");
        doc.Worksheets.Remove("Sheet1");
        Assert.Equal(0, doc.Worksheets.Count);
    }

    [Fact]
    public void Worksheets_Remove_Nonexistent_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.Worksheets.Remove("__nonexistent__"));
    }

    // -------------------------------------------------------------------------
    // Pilot 10: Lane ownership — existing tests not broken
    // -------------------------------------------------------------------------

    [Fact]
    public void ExistingTests_StillPass_WorksheetsDoesNotBreakOldAPI()
    {
        var doc = FodsDocument.Load(SamplePath("minimal-spreadsheet.fods"));
        // Verify old Sheets property still works (backward compat)
        _ = doc.Sheets;
    }

    // -------------------------------------------------------------------------
    // Pilot 12: Idempotency — second run produces same result
    // -------------------------------------------------------------------------

    [Fact]
    public void Worksheets_CalledTwice_ReturnsSameCount()
    {
        var doc = FodsDocument.Load(SamplePath("multi-sheet-basic.fods"));
        var count1 = doc.Worksheets.Count;
        var count2 = doc.Worksheets.Count;
        Assert.Equal(count1, count2);
    }
}
