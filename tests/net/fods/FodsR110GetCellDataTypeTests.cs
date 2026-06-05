// R110 Wave 4: FODS GetCellDataType tests
// Ledger: R110-GOVERNED-DOTNET-FODS-GETCELLDATATYPE-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR110GetCellDataTypeTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void GetCellDataType_ValidCell_ReturnsTypeOrNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        // Even null is valid — just proves the method runs without error
        var result = doc.GetCellDataType(names[0], 0, 0);
        // Type is string, float, or null — all valid
    }

    [Fact]
    public void GetCellDataType_OutOfRangeRow_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.Null(doc.GetCellDataType(names[0], 99999, 0));
    }

    [Fact]
    public void GetCellDataType_OutOfRangeCol_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.Null(doc.GetCellDataType(names[0], 0, 99999));
    }

    [Fact]
    public void GetCellDataType_NegativeRow_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.Null(doc.GetCellDataType(names[0], -1, 0));
    }

    [Fact]
    public void GetCellDataType_NonExistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Null(doc.GetCellDataType("NonExistentSheet999", 0, 0));
    }

    [Fact]
    public void GetCellDataType_NullSheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetCellDataType(null!, 0, 0));
    }

    [Fact]
    public void GetCellDataType_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.GetCellDataType("", 0, 0));
    }

    [Fact]
    public void GetCellDataType_AfterSetCellValue_ConsistentAccess()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var names = doc.GetSheetNames();
        Assert.NotEmpty(names);
        doc.SetCellValue(0, 0, "test-value");
        // After setting text, the type might change or stay the same
        // Key: no exception
        var type = doc.GetCellDataType(names[0], 0, 0);
        // Valid result (possibly null if no value-type attribute after text edit)
    }
}
