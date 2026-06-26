// Tests for FodtDocumentException exception class hierarchy and throwing scenarios.
// Sprint: FORMAT-FACTORY-FODT-R145-20260627
// Ledger: R145-GOVERNED-DOTNET-FODT-DOCUMENT-EXCEPTION-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R145: Tests for FodtDocumentException — the base exception for FODT document errors.
/// FodtDocumentException is thrown when FodtDocument.Load receives null or empty path,
/// or a non-existent path. It extends System.Exception with standard constructors.
/// Covers: FodtDocumentException is subclass of Exception; message constructor preserves
/// message; inner-exception constructor preserves both message and inner; Load null path
/// throws FodtDocumentException; Load empty path throws FodtDocumentException;
/// Load non-existent path throws FodtDocumentException; CreateEmpty does not throw;
/// exception caught as base Exception type; exception message non-null; dogfood
/// try/catch on null-path load verifies exception properties.
/// </summary>
public class FodtR145DocumentExceptionTests
{
    // -------------------------------------------------------------------------
    // Exception class hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocumentException_IsSubclassOfException()
    {
        var ex = new FodtDocumentException("test message");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void FodtDocumentException_MessageConstructor_PreservesMessage()
    {
        const string msg = "document load failed: R145 test";
        var ex = new FodtDocumentException(msg);
        Assert.Equal(msg, ex.Message);
    }

    [Fact]
    public void FodtDocumentException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new InvalidOperationException("inner cause");
        var ex = new FodtDocumentException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void FodtDocumentException_MessageIsNotNull()
    {
        var ex = new FodtDocumentException("non-null");
        Assert.NotNull(ex.Message);
    }

    // -------------------------------------------------------------------------
    // FodtDocument.Load throwing scenarios
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_Load_NullPath_ThrowsFodtDocumentException()
    {
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load((string)null!));
    }

    [Fact]
    public void FodtDocument_Load_EmptyPath_ThrowsFodtDocumentException()
    {
        Assert.Throws<FodtDocumentException>(() => FodtDocument.Load(string.Empty));
    }

    [Fact]
    public void FodtDocument_Load_NonExistentPath_ThrowsFodtDocumentException()
    {
        Assert.Throws<FodtDocumentException>(() =>
            FodtDocument.Load("/nonexistent/r145-fodt-test.fodt"));
    }

    // -------------------------------------------------------------------------
    // Exception caught as base type
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocumentException_CanBeCaughtAsBaseException()
    {
        Exception? caught = null;
        try
        {
            FodtDocument.Load((string)null!);
        }
        catch (Exception ex)
        {
            caught = ex;
        }
        Assert.NotNull(caught);
        Assert.IsType<FodtDocumentException>(caught);
    }

    // -------------------------------------------------------------------------
    // CreateEmpty does NOT throw
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_CreateEmpty_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc);
    }

    // -------------------------------------------------------------------------
    // Dogfood: try/catch on null-path load, verify exception properties
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TryCatch_NullLoad_VerifiesExceptionProperties()
    {
        FodtDocumentException? caught = null;
        try
        {
            FodtDocument.Load((string)null!);
        }
        catch (FodtDocumentException ex)
        {
            caught = ex;
        }

        Assert.NotNull(caught);
        Assert.NotNull(caught!.Message);
        Assert.False(string.IsNullOrEmpty(caught.Message));

        // Verify we can construct a new exception with the original as inner
        var wrapped = new FodtDocumentException("wrapped: " + caught.Message, caught);
        Assert.Equal(caught, wrapped.InnerException);
    }
}
