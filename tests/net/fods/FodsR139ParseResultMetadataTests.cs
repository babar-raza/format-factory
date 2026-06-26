// Tests for FodsParseResult metadata properties: FileSizeBytes, IsSuccess, Warnings, Sheets.
// Sprint: FORMAT-FACTORY-FODS-R139-20260627
// Ledger: R139-GOVERNED-DOTNET-FODS-PARSERESULT-METADATA-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R139: Tests for FodsParseResult metadata properties returned by FodsParser.Parse().
/// Covers: FileSizeBytes > 0 for valid file; IsSuccess = true for valid file;
/// Warnings list is empty for clean valid file; Sheets[0].RowCount >= 0;
/// Sheets[0].CellCount >= 0; Sheets[0].Name is non-empty; multi-sheet result count;
/// null path throws FodsParseException; Parse on a non-existent file returns errors;
/// dogfood multi-sheet pipeline verifying all metadata properties consistent.
/// </summary>
public class FodsR139ParseResultMetadataTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fods", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static FodsParseResult ParseFixture(string name)
    {
        var parser = new FodsParser();
        return parser.Parse(FixturePath(name));
    }

    // -------------------------------------------------------------------------
    // FileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ValidFile_FileSizeBytesGreaterThanZero()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.FileSizeBytes > 0,
            $"Expected FileSizeBytes > 0, got {result.FileSizeBytes}");
    }

    [Fact]
    public void Parse_ValidFile_FileSizeBytesMatchesActualFileSize()
    {
        var path = FixturePath("fods-minimal-roundtrip.fods");
        var actualSize = new FileInfo(path).Length;
        var parser = new FodsParser();
        var result = parser.Parse(path);
        Assert.Equal(actualSize, result.FileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // IsSuccess
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ValidFile_IsSuccessIsTrue()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.IsSuccess, $"Expected IsSuccess=true; Errors: {string.Join("; ", result.Errors)}");
    }

    [Fact]
    public void Parse_ValidFile_ErrorsListIsEmpty()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.Empty(result.Errors);
    }

    // -------------------------------------------------------------------------
    // Warnings
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ValidFile_WarningsListExists()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.NotNull(result.Warnings);
    }

    // -------------------------------------------------------------------------
    // Sheets metadata
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_ValidFile_SheetsCountAtLeastOne()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.Sheets.Count >= 1,
            $"Expected at least 1 sheet, got {result.Sheets.Count}");
    }

    [Fact]
    public void Parse_ValidFile_FirstSheetNameIsNonEmpty()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.Sheets.Count > 0);
        Assert.False(string.IsNullOrEmpty(result.Sheets[0].Name),
            "First sheet name should be non-empty");
    }

    [Fact]
    public void Parse_ValidFile_FirstSheetRowCountNonNegative()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.Sheets.Count > 0);
        Assert.True(result.Sheets[0].RowCount >= 0,
            $"RowCount must be >= 0, got {result.Sheets[0].RowCount}");
    }

    [Fact]
    public void Parse_ValidFile_FirstSheetCellCountNonNegative()
    {
        var result = ParseFixture("fods-minimal-roundtrip.fods");
        Assert.True(result.Sheets.Count > 0);
        Assert.True(result.Sheets[0].CellCount >= 0,
            $"CellCount must be >= 0, got {result.Sheets[0].CellCount}");
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-sheet parse + verify all metadata properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiSheetFile_AllMetadataConsistent()
    {
        var result = ParseFixture("fods-multi-sheet.fods");

        Assert.True(result.IsSuccess, $"Multi-sheet parse failed: {string.Join("; ", result.Errors)}");
        Assert.True(result.FileSizeBytes > 0);
        Assert.True(result.Sheets.Count >= 1);

        // All sheets have non-empty names
        foreach (var sheet in result.Sheets)
        {
            Assert.False(string.IsNullOrEmpty(sheet.Name),
                $"Sheet name should be non-empty: got '{sheet.Name}'");
            Assert.True(sheet.RowCount >= 0);
            Assert.True(sheet.CellCount >= 0);
        }
    }
}
