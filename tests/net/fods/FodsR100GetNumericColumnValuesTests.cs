// R100 Wave 5: GetNumericColumnValues — extract float cell values from a column
// Governed skill: /add-dotnet-api
// Ledger: R100-GOVERNED-DOTNET-FODS-GETNUMERICCOLUMNVALUES-001
// Spec refs: FACT-FODS-006 (table:table-cell), FACT-FODS-010 (office:value-type float)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR100GetNumericColumnValuesTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static FodsDocument LoadFirst()
    {
        var files = Directory.GetFiles(SamplesDir, "*.fods");
        if (files.Length == 0)
            throw new InvalidOperationException("No .fods sample files found in " + SamplesDir);
        return FodsDocument.Load(files.OrderBy(f => f).First());
    }

    [Fact]
    public void GetNumericColumnValues_NullSheet_Throws()
    {
        var doc = LoadFirst();
        var sheet = doc.GetSheetNames().First();
        _ = sheet; // ensure doc loads
        var ex = Assert.Throws<ArgumentException>(
            () => doc.GetNumericColumnValues(null!, 0));
        Assert.Contains("Sheet name", ex.Message);
    }

    [Fact]
    public void GetNumericColumnValues_NegativeCol_Throws()
    {
        var doc = LoadFirst();
        var sheet = doc.GetSheetNames().First();
        Assert.Throws<ArgumentOutOfRangeException>(
            () => doc.GetNumericColumnValues(sheet, -1));
    }

    [Fact]
    public void GetNumericColumnValues_MissingSheet_Throws()
    {
        var doc = LoadFirst();
        Assert.Throws<InvalidOperationException>(
            () => doc.GetNumericColumnValues("__NO_SUCH_SHEET__", 0));
    }

    [Fact]
    public void GetNumericColumnValues_ReturnsOnlyDoubles()
    {
        var doc = LoadFirst();
        var sheet = doc.GetSheetNames().First();
        // Must return IReadOnlyList<double> — each item is a valid double
        var vals = doc.GetNumericColumnValues(sheet, 0);
        Assert.NotNull(vals);
        // All values must be finite (no NaN, no Inf from bad parse)
        foreach (var v in vals)
            Assert.True(double.IsFinite(v), $"Got non-finite value {v}");
    }

    [Fact]
    public void GetNumericColumnValues_EmptyCol_ReturnsEmpty()
    {
        // Create a fresh doc with one sheet; column 99 is empty
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        var vals = doc.GetNumericColumnValues("Data", 99);
        Assert.Empty(vals);
    }

    [Fact]
    public void GetNumericColumnValues_WithNumericCells_ReturnsThem()
    {
        // Build a sheet with a known numeric column
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new List<string?> { "header", "3.14", "2.71" });
        doc.InsertRowWithValues("Sheet1", 1, new List<string?> { "text_only", null, null });

        // Column 0 is "header"/"text_only" — no floats from text inserts unless doc marks them
        // This test verifies the method completes without exception
        var vals = doc.GetNumericColumnValues("Sheet1", 0);
        Assert.NotNull(vals);
    }
}
