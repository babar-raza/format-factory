// Tests for TxtWriterException constructors and TxtWriter.WriteLinesToFile parent-dir creation.
// Sprint: FORMAT-FACTORY-TXT-EXCEPTION-PARENTDIR-R120-20260627
// Ledger: R120-GOVERNED-DOTNET-TXT-EXCEPTION-PARENTDIR-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Txt.Tests;

/// <summary>
/// R120: TxtWriterException(string) preserves Message; TxtWriterException(string, Exception)
/// also preserves InnerException. TxtWriter.WriteLinesToFile auto-creates parent directories
/// when they do not yet exist. TxtWriter.WriteLines(null) throws ArgumentNullException (not
/// TxtWriterException). TxtWriterException is a subclass of Exception.
/// </summary>
public class TxtR120ExceptionAndParentDirTests
{
    private static string TempPath(string sub = "")
        => Path.Combine(Path.GetTempPath(), $"ff_txt_r120_{Guid.NewGuid():N}{sub}");

    // ---- TxtWriterException(message) ----

    [Fact]
    public void TxtWriterException_MessageConstructor_MessagePreserved()
    {
        var ex = new TxtWriterException("test message");
        Assert.Equal("test message", ex.Message);
    }

    [Fact]
    public void TxtWriterException_MessageConstructor_IsException()
    {
        var ex = new TxtWriterException("msg");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void TxtWriterException_MessageConstructor_InnerExceptionIsNull()
    {
        var ex = new TxtWriterException("msg");
        Assert.Null(ex.InnerException);
    }

    // ---- TxtWriterException(message, inner) ----

    [Fact]
    public void TxtWriterException_InnerConstructor_MessagePreserved()
    {
        var inner = new InvalidOperationException("inner");
        var ex    = new TxtWriterException("outer", inner);
        Assert.Equal("outer", ex.Message);
    }

    [Fact]
    public void TxtWriterException_InnerConstructor_InnerExceptionPreserved()
    {
        var inner = new IOException("disk full");
        var ex    = new TxtWriterException("write failed", inner);
        Assert.Same(inner, ex.InnerException);
    }

    [Fact]
    public void TxtWriterException_InnerConstructor_IsException()
    {
        var ex = new TxtWriterException("msg", new Exception("x"));
        Assert.IsAssignableFrom<Exception>(ex);
    }

    // ---- WriteLines(null) ----

    [Fact]
    public void WriteLines_NullLines_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => TxtWriter.WriteLines(null!));
    }

    // ---- WriteLinesToFile: parent directory auto-creation ----

    [Fact]
    public void WriteLinesToFile_NestedNonExistentDir_CreatesFileSuccessfully()
    {
        var dir  = Path.Combine(TempPath(), "sub1", "sub2");
        var path = Path.Combine(dir, "output.txt");
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "created in nested dir" }, path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, recursive: true);
        }
    }

    [Fact]
    public void WriteLinesToFile_NestedDir_ContentCorrect()
    {
        var dir  = Path.Combine(TempPath(), "sub");
        var path = Path.Combine(dir, "result.txt");
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "hello", "world" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("hello", content);
            Assert.Contains("world", content);
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, recursive: true);
        }
    }

    // ---- Dogfood: exception wrapping an I/O failure and nested output ----

    [Fact]
    public void DogfoodPipeline_ExceptionWrapsIoError_InnerPreservedAndOutputWritten()
    {
        // Simulate catching an IO error and wrapping it
        IOException ioError;
        try { throw new IOException("simulated disk full"); }
        catch (IOException ex) { ioError = ex; }

        var wrapping = new TxtWriterException("write failed: disk full", ioError);
        Assert.Equal("write failed: disk full", wrapping.Message);
        Assert.Same(ioError, wrapping.InnerException);

        // Also verify actual file write works in nested dir
        var dir  = Path.Combine(TempPath(), "dogfood", "logs");
        var path = Path.Combine(dir, "run.txt");
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "Log start", "Log end" }, path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Contains("Log start", content);
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, recursive: true);
        }
    }
}
