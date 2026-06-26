// Tests for FodsSheetInfo, FodsParseResult.Sheets, FodsParser.MaxFileSizeBytes, and FodsParseException.
// Sprint: ff-sprint-s132-dotnet-deepening-20260627
// Ledger: PC-FODS-R145

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R145: Tests for FodsSheetInfo, FodsParseResult.Sheets, FodsParser.MaxFileSizeBytes,
/// and FodsParseException. FodsSheetInfo is a plain data class with Name, RowCount,
/// and CellCount properties. FodsParseResult.Sheets is a List&lt;FodsSheetInfo&gt; initialized
/// to an empty list. FodsParser.MaxFileSizeBytes is an init-only property defaulting to 50 MB.
/// FodsParseException is sealed and derives from System.Exception.
/// Covers: FodsSheetInfo Name default empty; RowCount default 0; CellCount default 0;
/// FodsSheetInfo assignable via object initializer; FodsParseResult.Sheets default empty;
/// FodsParseResult.Errors default empty; FodsParseResult.Warnings default empty;
/// FodsParser MaxFileSizeBytes default; FodsParseException Exception subclass; message;
/// dogfood FodsSheetInfo assembly composition pipeline.
/// </summary>
public class FodsR145ParseResultAndSheetInfoTests
{
    // -------------------------------------------------------------------------
    // FodsSheetInfo default values
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsSheetInfo_Name_DefaultIsEmpty()
    {
        var info = new FodsSheetInfo();
        Assert.Equal(string.Empty, info.Name);
    }

    [Fact]
    public void FodsSheetInfo_RowCount_DefaultIsZero()
    {
        var info = new FodsSheetInfo();
        Assert.Equal(0, info.RowCount);
    }

    [Fact]
    public void FodsSheetInfo_CellCount_DefaultIsZero()
    {
        var info = new FodsSheetInfo();
        Assert.Equal(0, info.CellCount);
    }

    [Fact]
    public void FodsSheetInfo_Assignable_ViaObjectInitializer()
    {
        var info = new FodsSheetInfo
        {
            Name = "Sheet1",
            RowCount = 10,
            CellCount = 30
        };
        Assert.Equal("Sheet1", info.Name);
        Assert.Equal(10, info.RowCount);
        Assert.Equal(30, info.CellCount);
    }

    // -------------------------------------------------------------------------
    // FodsParseResult collection defaults
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsParseResult_Sheets_DefaultIsEmpty()
    {
        var result = new FodsParseResult();
        Assert.NotNull(result.Sheets);
        Assert.Empty(result.Sheets);
    }

    [Fact]
    public void FodsParseResult_Errors_DefaultIsEmpty()
    {
        var result = new FodsParseResult();
        Assert.NotNull(result.Errors);
        Assert.Empty(result.Errors);
    }

    [Fact]
    public void FodsParseResult_Warnings_DefaultIsEmpty()
    {
        var result = new FodsParseResult();
        Assert.NotNull(result.Warnings);
        Assert.Empty(result.Warnings);
    }

    // -------------------------------------------------------------------------
    // FodsParser.MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsParser_MaxFileSizeBytes_DefaultIs50MB()
    {
        var parser = new FodsParser();
        const long expected = 50L * 1024 * 1024;
        Assert.Equal(expected, parser.MaxFileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // FodsParseException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsParseException_IsSubclassOfException()
    {
        var ex = new FodsParseException("parse failed");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: FodsSheetInfo assembly composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FodsParseResult_AddSheetInfo_VerifiesCollection()
    {
        var result = new FodsParseResult
        {
            MimeType = "application/vnd.oasis.opendocument.spreadsheet",
            OdfVersion = "1.3"
        };

        result.Sheets.Add(new FodsSheetInfo { Name = "Revenue", RowCount = 50, CellCount = 150 });
        result.Sheets.Add(new FodsSheetInfo { Name = "Costs", RowCount = 30, CellCount = 90 });

        Assert.Equal(2, result.Sheets.Count);
        Assert.Equal("Revenue", result.Sheets[0].Name);
        Assert.Equal(50, result.Sheets[0].RowCount);
        Assert.Equal(150, result.Sheets[0].CellCount);
        Assert.Equal("Costs", result.Sheets[1].Name);
        Assert.Equal("application/vnd.oasis.opendocument.spreadsheet", result.MimeType);
        Assert.Equal("1.3", result.OdfVersion);
    }
}
