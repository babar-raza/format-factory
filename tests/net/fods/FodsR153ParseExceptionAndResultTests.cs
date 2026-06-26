// Tests for FodsParseException hierarchy and FodsParseResult behavior.
// Sprint: ff-sprint-s145-dotnet-deepening-20260628
// Ledger: PC-FODS-R153

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R153: Tests for FodsParseException and FodsParseResult from FodsParser.
/// FodsParseException is thrown by GetSheetNames when parsing fails.
/// FodsParseResult.IsSuccess is false when Errors list is non-empty.
/// FodsParser.Parse returns a result (does not throw); errors go in result.Errors.
/// Covers: FodsParseException message stored; FodsParseException is Exception subclass;
/// FodsParseException with inner stores inner; FodsParseException with inner stores message;
/// FodsParseException can be thrown and caught; FodsParseResult nonexistent file IsSuccess=false;
/// FodsParseResult nonexistent file Errors non-empty; FodsParseResult empty path IsSuccess=false;
/// GetSheetNames nonexistent file throws FodsParseException;
/// dogfood FodsParseException message from GetSheetNames is non-empty.
/// </summary>
public class FodsR153ParseExceptionAndResultTests
{
    // -------------------------------------------------------------------------
    // FodsParseException constructor tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsParseException_MessageOnly_StoresMessage()
    {
        var ex = new FodsParseException("bad FODS input");
        Assert.Equal("bad FODS input", ex.Message);
    }

    [Fact]
    public void FodsParseException_IsExceptionSubclass()
    {
        var ex = new FodsParseException("test");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void FodsParseException_WithInnerException_InnerStored()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new FodsParseException("outer", inner);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void FodsParseException_WithInnerException_MessageStored()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new FodsParseException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
    }

    [Fact]
    public void FodsParseException_CanBeThrownAndCaught()
    {
        var threwCorrect = false;
        try { throw new FodsParseException("test throw"); }
        catch (FodsParseException) { threwCorrect = true; }
        Assert.True(threwCorrect);
    }

    // -------------------------------------------------------------------------
    // FodsParser.Parse result tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsParser_Parse_NonexistentFile_IsSuccessFalse()
    {
        var parser = new FodsParser();
        var result = parser.Parse(Path.Combine(Path.GetTempPath(), "nonexistent-xyz.fods"));
        Assert.False(result.IsSuccess);
    }

    [Fact]
    public void FodsParser_Parse_NonexistentFile_ErrorsNonEmpty()
    {
        var parser = new FodsParser();
        var result = parser.Parse(Path.Combine(Path.GetTempPath(), "nonexistent-xyz.fods"));
        Assert.NotEmpty(result.Errors);
    }

    [Fact]
    public void FodsParser_Parse_EmptyPath_IsSuccessFalse()
    {
        var parser = new FodsParser();
        var result = parser.Parse(string.Empty);
        Assert.False(result.IsSuccess);
    }

    // -------------------------------------------------------------------------
    // GetSheetNames exception tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_NonexistentFile_ThrowsFodsParseException()
    {
        var parser = new FodsParser();
        Assert.Throws<FodsParseException>(() =>
            parser.GetSheetNames(Path.Combine(Path.GetTempPath(), "no-such-file.fods")));
    }

    // -------------------------------------------------------------------------
    // Dogfood: FodsParseException message is informative
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_GetSheetNames_NonexistentFile_ExceptionMessageNonEmpty()
    {
        var parser = new FodsParser();
        var ex = Assert.Throws<FodsParseException>(() =>
            parser.GetSheetNames(Path.Combine(Path.GetTempPath(), "missing.fods")));
        Assert.False(string.IsNullOrEmpty(ex.Message));
    }
}
