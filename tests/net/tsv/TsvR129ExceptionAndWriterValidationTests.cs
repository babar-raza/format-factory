// Tests for TsvException hierarchy and TsvWriter field validation (tab/newline rejection).
// Sprint: ff-sprint-s129-dotnet-deepening-20260627
// Ledger: PC-TSV-R129

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R129: Tests for TsvException exception hierarchy and TsvWriter field validation.
/// TsvException is sealed and derives from System.Exception. TsvWriter.WriteRows
/// rejects fields containing tab or newline characters by throwing TsvException.
/// Covers: Exception subclass; message constructor; inner-exception constructor;
/// message non-null; WriteRows tab-in-field throws TsvException;
/// WriteRows newline-in-field throws TsvException; WriteRows CR-in-field throws TsvException;
/// WriteRows null field treated as empty (no throw); WriteRows valid rows succeeds;
/// dogfood pipeline catch TsvException from tab-field verifies message content.
/// </summary>
public class TsvR129ExceptionAndWriterValidationTests
{
    // -------------------------------------------------------------------------
    // TsvException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvException_IsSubclassOfException()
    {
        var ex = new TsvException("test message");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void TsvException_MessageConstructor_PreservesMessage()
    {
        const string msg = "TSV field validation failure";
        var ex = new TsvException(msg);
        Assert.Equal(msg, ex.Message);
    }

    [Fact]
    public void TsvException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new ArgumentException("inner cause");
        var ex = new TsvException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void TsvException_Message_IsNonNull()
    {
        var ex = new TsvException("any message");
        Assert.NotNull(ex.Message);
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRows field validation
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvWriter_WriteRows_FieldContainsTab_ThrowsTsvException()
    {
        var rows = new List<List<string?>> { new() { "Alice", "field\twith\ttabs", "42" } };
        Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
    }

    [Fact]
    public void TsvWriter_WriteRows_FieldContainsLineFeed_ThrowsTsvException()
    {
        var rows = new List<List<string?>> { new() { "line1\nline2" } };
        Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
    }

    [Fact]
    public void TsvWriter_WriteRows_FieldContainsCarriageReturn_ThrowsTsvException()
    {
        var rows = new List<List<string?>> { new() { "field\rwith\rcr" } };
        Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRows valid scenarios
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvWriter_WriteRows_NullField_TreatedAsEmpty()
    {
        // Null fields should not throw — they are treated as empty strings
        var rows = new List<List<string?>> { new() { "Alice", null, "42" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains("\t\t", result);  // null field becomes empty between tabs
    }

    [Fact]
    public void TsvWriter_WriteRows_ValidRows_ProducesTabDelimited()
    {
        var rows = new List<List<string?>>
        {
            new() { "Name", "Score", "City" },
            new() { "Alice", "95", "London" },
        };
        var result = TsvWriter.WriteRows(rows);
        Assert.Contains("Name\tScore\tCity", result);
        Assert.Contains("Alice\t95\tLondon", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood: catch TsvException and verify message content
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TabInField_CatchTsvException_VerifiesMessage()
    {
        var rows = new List<List<string?>> { new() { "data\twith\ttabs" } };

        TsvException? caught = null;
        try
        {
            TsvWriter.WriteRows(rows);
        }
        catch (TsvException ex)
        {
            caught = ex;
        }

        Assert.NotNull(caught);
        Assert.False(string.IsNullOrEmpty(caught!.Message));
        Assert.IsAssignableFrom<Exception>(caught);
        // Message should mention the tab character
        Assert.Contains("tab", caught.Message, StringComparison.OrdinalIgnoreCase);
    }
}
