// Tests for NdjsonException hierarchy and NdjsonReader.MaxSize constant.
// Sprint: ff-sprint-s129-dotnet-deepening-20260627
// Ledger: PC-NDJSON-R134

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R134: Tests for NdjsonException exception hierarchy and NdjsonReader.MaxSize constant.
/// NdjsonException is sealed and derives from System.Exception. MaxSize is a const long
/// equal to 64 MB (64 * 1024 * 1024 = 67,108,864 bytes).
/// Covers: Exception subclass; message constructor preserves message; inner-exception
/// constructor preserves both; message non-null; NdjsonReader.MaxSize value correct;
/// MaxSize equals 64 MB; ReadRecords null throws ArgumentNullException;
/// ReadRecordsFromFile empty path throws NdjsonException;
/// NdjsonWriter.WriteRecords null throws ArgumentNullException;
/// dogfood pipeline NdjsonException catch verifies properties.
/// </summary>
public class NdjsonR134ExceptionAndMaxSizeTests
{
    // -------------------------------------------------------------------------
    // NdjsonException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonException_IsSubclassOfException()
    {
        var ex = new NdjsonException("test message");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void NdjsonException_MessageConstructor_PreservesMessage()
    {
        const string msg = "NDJSON parse failure";
        var ex = new NdjsonException(msg);
        Assert.Equal(msg, ex.Message);
    }

    [Fact]
    public void NdjsonException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new FormatException("inner cause");
        var ex = new NdjsonException("outer message", inner);
        Assert.Equal("outer message", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void NdjsonException_Message_IsNonNull()
    {
        var ex = new NdjsonException("anything");
        Assert.NotNull(ex.Message);
    }

    // -------------------------------------------------------------------------
    // NdjsonReader.MaxSize constant
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonReader_MaxSize_Is64MB()
    {
        const long expected = 64L * 1024 * 1024;
        Assert.Equal(expected, NdjsonReader.MaxSize);
    }

    [Fact]
    public void NdjsonReader_MaxSize_IsPositive()
    {
        Assert.True(NdjsonReader.MaxSize > 0);
    }

    // -------------------------------------------------------------------------
    // ReadRecords null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonReader_ReadRecords_NullString_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => NdjsonReader.ReadRecords((string)null!));
    }

    // -------------------------------------------------------------------------
    // ReadRecordsFromFile error paths
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonReader_ReadRecordsFromFile_EmptyPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecordsFromFile(string.Empty));
    }

    [Fact]
    public void NdjsonReader_ReadRecordsFromFile_NonexistentPath_ThrowsNdjsonException()
    {
        Assert.Throws<NdjsonException>(() =>
            NdjsonReader.ReadRecordsFromFile("/tmp/no_such_file_r134.ndjson"));
    }

    // -------------------------------------------------------------------------
    // NdjsonWriter null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void NdjsonWriter_WriteRecords_NullRecords_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => NdjsonWriter.WriteRecords(null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: catch NdjsonException from invalid JSON line
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_InvalidJsonLine_CatchesNdjsonException_VerifiesProperties()
    {
        // A line with valid JSON followed by an invalid line
        const string badContent = "{\"id\":1}\nNOT_VALID_JSON";

        NdjsonException? caught = null;
        try
        {
            NdjsonReader.ReadRecords(badContent);
        }
        catch (NdjsonException ex)
        {
            caught = ex;
        }

        Assert.NotNull(caught);
        Assert.False(string.IsNullOrEmpty(caught!.Message));
        Assert.IsAssignableFrom<Exception>(caught);
        // Inner exception from JsonDocument.Parse
        Assert.NotNull(caught.InnerException);
    }
}
