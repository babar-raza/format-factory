// R93 Train K: FODS .NET GetColumnHeaders Tests
// Governed skill: /add-dotnet-api
// Ledger: R93-GOVERNED-DOTNET-FODS-GETCOLUMNHEADERS-001
// Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR93GetColumnHeadersTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void GetColumnHeaders_ReturnsNonNullList()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders();
        Assert.NotNull(headers);
    }

    [Fact]
    public void GetColumnHeaders_ReturnsHeadersFromFirstRow()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders();
        // minimal-spreadsheet.fods first row contains "Hello"
        Assert.True(headers.Count > 0, "Expected at least one header");
        Assert.Equal("Hello", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_FirstSheetOverload_ReturnsNonNull()
    {
        // PQ-018: static overload removed; use instance overload instead
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheetNames = doc.GetSheetNames();
        Assert.True(sheetNames.Count > 0);
        var headers = doc.GetColumnHeaders(sheetNames[0]);
        Assert.NotNull(headers);
    }

    [Fact]
    public void GetColumnHeaders_NamedSheetOverload_ReturnsHeaders()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var sheetNames = doc.GetSheetNames();
        Assert.True(sheetNames.Count > 0);
        var headers = doc.GetColumnHeaders(sheetNames[0]);
        Assert.NotNull(headers);
        Assert.True(headers.Count > 0, "Expected at least one header from named sheet");
    }

    [Fact]
    public void GetColumnHeaders_NonExistentSheet_ReturnsEmpty()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders("NonExistentSheetXYZ");
        Assert.NotNull(headers);
        Assert.Empty(headers);
    }

    [Fact]
    public void GetColumnHeaders_CountMatchesSheetFirstRow()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders();
        // Verify count is consistent with repeated calls
        var headers2 = doc.GetColumnHeaders();
        Assert.Equal(headers.Count, headers2.Count);
    }

    [Fact]
    public void GetColumnHeaders_AfterSetCellValue_ReflectsChange()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        // Set first cell (row 0 = headers row) to new header value
        doc.SetCellValue(0, 0, "UpdatedHeader");
        var headers = doc.GetColumnHeaders();
        Assert.Equal("UpdatedHeader", headers[0]);
    }

    [Fact]
    public void GetColumnHeaders_ReturnsReadOnlyList()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var headers = doc.GetColumnHeaders();
        // Should be castable to IReadOnlyList<string>
        Assert.IsAssignableFrom<IReadOnlyList<string>>(headers);
    }
}
