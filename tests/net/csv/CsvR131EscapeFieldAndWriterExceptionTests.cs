// Tests for CsvWriter.EscapeField RFC 4180 quoting and CsvWriterException hierarchy.
// Sprint: ff-sprint-s130-dotnet-deepening-20260627
// Ledger: PC-CSV-R131

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R131: Tests for CsvWriter.EscapeField RFC 4180 quoting behavior and
/// CsvWriterException exception hierarchy. EscapeField wraps fields in double-quotes
/// when they contain commas, double-quotes, CR, or LF. Embedded double-quotes
/// are doubled (""). CsvWriterException is sealed and derives from System.Exception.
/// Covers: null field → empty; empty field → empty; plain field → unquoted;
/// comma-containing field → quoted; double-quote → doubled and quoted;
/// LF-containing field → quoted; CR-containing field → quoted;
/// CsvWriterException is Exception subclass; message constructor; inner-exception;
/// dogfood WriteRows roundtrip with special characters verifies EscapeField.
/// </summary>
public class CsvR131EscapeFieldAndWriterExceptionTests
{
    // -------------------------------------------------------------------------
    // CsvWriter.EscapeField — RFC 4180 quoting
    // -------------------------------------------------------------------------

    [Fact]
    public void EscapeField_NullValue_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, CsvWriter.EscapeField(null));
    }

    [Fact]
    public void EscapeField_EmptyString_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, CsvWriter.EscapeField(string.Empty));
    }

    [Fact]
    public void EscapeField_PlainField_ReturnsUnquoted()
    {
        Assert.Equal("London", CsvWriter.EscapeField("London"));
    }

    [Fact]
    public void EscapeField_FieldWithComma_ReturnsQuoted()
    {
        var result = CsvWriter.EscapeField("Smith, John");
        Assert.Equal("\"Smith, John\"", result);
    }

    [Fact]
    public void EscapeField_FieldWithDoubleQuote_DoublesAndQuotes()
    {
        // Field: He said "Hello"  →  "He said ""Hello"""
        var result = CsvWriter.EscapeField("He said \"Hello\"");
        Assert.Equal("\"He said \"\"Hello\"\"\"", result);
    }

    [Fact]
    public void EscapeField_FieldWithLineFeed_ReturnsQuoted()
    {
        var result = CsvWriter.EscapeField("line1\nline2");
        Assert.StartsWith("\"", result);
        Assert.EndsWith("\"", result);
        Assert.Contains("line1\nline2", result);
    }

    [Fact]
    public void EscapeField_FieldWithCarriageReturn_ReturnsQuoted()
    {
        var result = CsvWriter.EscapeField("text\rmore");
        Assert.StartsWith("\"", result);
        Assert.EndsWith("\"", result);
    }

    // -------------------------------------------------------------------------
    // CsvWriterException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvWriterException_IsSubclassOfException()
    {
        var ex = new CsvWriterException("test message");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void CsvWriterException_MessageConstructor_PreservesMessage()
    {
        const string msg = "CSV write failure";
        var ex = new CsvWriterException(msg);
        Assert.Equal(msg, ex.Message);
    }

    [Fact]
    public void CsvWriterException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new IOException("disk error");
        var ex = new CsvWriterException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRows with special characters exercises EscapeField
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRows_SpecialChars_ProducesRfc4180Output()
    {
        var rows = new[]
        {
            new[] { "Name", "Address", "Note" },
            new[] { "Alice", "123 Main St, Apt 4", "She said \"hello\"" },
            new[] { "Bob", "London", "plain text" },
        };

        var csv = CsvWriter.WriteRows(rows);

        // Address field contains comma → must be quoted
        Assert.Contains("\"123 Main St, Apt 4\"", csv);
        // Note field contains double-quote → must be doubled
        Assert.Contains("\"She said \"\"hello\"\"\"", csv);
        // Plain text not quoted
        Assert.Contains("plain text", csv);
    }
}
