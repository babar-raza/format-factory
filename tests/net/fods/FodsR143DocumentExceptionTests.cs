// Tests for FodsDocumentException exception hierarchy and throwing scenarios.
// Sprint: ff-sprint-s129-dotnet-deepening-20260627
// Ledger: PC-FODS-R143

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R143: Tests for FodsDocumentException — the dedicated exception type for FODS
/// document load and parse failures. FodsDocumentException is sealed and derives
/// from System.Exception.
/// Covers: Exception subclass; message constructor preserves message; inner-exception
/// constructor preserves both; message non-null; Load null/empty/nonexistent path throws
/// FodsDocumentException; exception caught as base Exception type; CreateNew does not
/// throw; dogfood try/catch on null-path load verifies exception properties.
/// </summary>
public class FodsR143DocumentExceptionTests
{
    // -------------------------------------------------------------------------
    // Exception hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsDocumentException_IsSubclassOfException()
    {
        var ex = new FodsDocumentException("test message");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void FodsDocumentException_MessageConstructor_PreservesMessage()
    {
        const string msg = "FODS load failure";
        var ex = new FodsDocumentException(msg);
        Assert.Equal(msg, ex.Message);
    }

    [Fact]
    public void FodsDocumentException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new InvalidOperationException("inner cause");
        var ex = new FodsDocumentException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void FodsDocumentException_Message_IsNonNull()
    {
        var ex = new FodsDocumentException("anything");
        Assert.NotNull(ex.Message);
    }

    // -------------------------------------------------------------------------
    // FodsDocument.Load throwing scenarios
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsDocument_Load_NullPath_ThrowsFodsDocumentException()
    {
        Assert.Throws<FodsDocumentException>(() => FodsDocument.Load(null!));
    }

    [Fact]
    public void FodsDocument_Load_EmptyPath_ThrowsFodsDocumentException()
    {
        Assert.Throws<FodsDocumentException>(() => FodsDocument.Load(string.Empty));
    }

    [Fact]
    public void FodsDocument_Load_NonexistentPath_ThrowsFodsDocumentException()
    {
        Assert.Throws<FodsDocumentException>(() =>
            FodsDocument.Load("/tmp/this_file_does_not_exist_r143.fods"));
    }

    // -------------------------------------------------------------------------
    // Exception caught as base type
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsDocument_Load_NullPath_ExceptionCaughtAsBaseException()
    {
        Exception? caught = null;
        try
        {
            FodsDocument.Load(null!);
        }
        catch (Exception ex)
        {
            caught = ex;
        }

        Assert.NotNull(caught);
        Assert.IsAssignableFrom<Exception>(caught);
    }

    // -------------------------------------------------------------------------
    // CreateNew does not throw
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsDocument_CreateNew_DoesNotThrow()
    {
        var doc = FodsDocument.CreateNew();
        Assert.NotNull(doc);
    }

    // -------------------------------------------------------------------------
    // Dogfood: try/catch on null-path load verifies exception properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TryCatch_NullLoad_VerifiesExceptionProperties()
    {
        FodsDocumentException? caught = null;
        try
        {
            FodsDocument.Load(null!);
        }
        catch (FodsDocumentException ex)
        {
            caught = ex;
        }

        Assert.NotNull(caught);
        Assert.False(string.IsNullOrEmpty(caught!.Message));
        Assert.IsAssignableFrom<Exception>(caught);
        // FodsDocumentException from null-path does not wrap an inner exception
        Assert.Null(caught.InnerException);
    }
}
