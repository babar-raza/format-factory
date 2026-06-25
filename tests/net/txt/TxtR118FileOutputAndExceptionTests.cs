// Tests for TxtWriter.WriteLinesToFile() advanced cases and TxtWriterException.
// Sprint: FORMAT-FACTORY-TXT-WRITER-R118-20260626
// Ledger: R118-GOVERNED-DOTNET-TXT-FILEOUTPUT-EXCEPTION-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Txt.Tests;

/// <summary>
/// R118: TxtWriter.WriteLinesToFile(lines, path) writes joined lines to disk.
/// Encoding is UTF-8 without BOM; line endings are normalized to LF.
/// Null entries become empty lines. Invalid paths throw TxtWriterException.
/// Parent directories are created automatically.
/// </summary>
public class TxtR118FileOutputAndExceptionTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_txt_r118_{Guid.NewGuid():N}.txt");

    // ---- File existence ----

    [Fact]
    public void WriteLinesToFile_ValidPath_CreatesFile()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "alpha", "beta" }, path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Content fidelity ----

    [Fact]
    public void WriteLinesToFile_MultipleLines_AllPresentInFile()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "first", "second", "third" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("first", content);
            Assert.Contains("second", content);
            Assert.Contains("third", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_NullEntry_BecomeEmptyLineInFile()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new string?[] { "before", null, "after" }, path);
            var content = File.ReadAllText(path);
            Assert.Contains("before", content);
            Assert.Contains("after", content);
            // null line produces consecutive newlines
            Assert.Contains("\n\n", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_EmptyList_CreatesFileWithNoContent()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new List<string?>(), path);
            Assert.True(File.Exists(path));
            Assert.Equal(string.Empty, File.ReadAllText(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Encoding ----

    [Fact]
    public void WriteLinesToFile_Encoding_NoUtf8Bom()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "hello" }, path);
            var bytes = File.ReadAllBytes(path);
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "Output must not contain a UTF-8 BOM");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteLinesToFile_LineEndings_LfNotCrLf()
    {
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "line one", "line two" }, path);
            var content = File.ReadAllText(path);
            Assert.DoesNotContain("\r\n", content);
            Assert.Contains("\n", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Round-trip consistency ----

    [Fact]
    public void WriteLinesToFile_RoundTrip_ContentMatchesWriteLines()
    {
        var lines = new[] { "paragraph one", "paragraph two", "paragraph three" };
        var path = TempPath();
        try
        {
            TxtWriter.WriteLinesToFile(lines, path);
            var fileContent = File.ReadAllText(path);
            var inMemory = TxtWriter.WriteLines(lines);
            Assert.Equal(inMemory.Replace("\r\n", "\n"), fileContent.Replace("\r\n", "\n"));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- TxtWriterException ----

    [Fact]
    public void WriteLinesToFile_NullPath_ThrowsTxtWriterException()
    {
        Assert.Throws<TxtWriterException>(() =>
            TxtWriter.WriteLinesToFile(new[] { "data" }, null!));
    }

    [Fact]
    public void WriteLinesToFile_EmptyPath_ThrowsTxtWriterException()
    {
        Assert.Throws<TxtWriterException>(() =>
            TxtWriter.WriteLinesToFile(new[] { "data" }, string.Empty));
    }

    [Fact]
    public void WriteLinesToFile_WhitespacePath_ThrowsTxtWriterException()
    {
        Assert.Throws<TxtWriterException>(() =>
            TxtWriter.WriteLinesToFile(new[] { "data" }, "   "));
    }

    // ---- Dogfood: multi-section document pipeline ----

    [Fact]
    public void DogfoodPipeline_MultiSectionDocument_AllLinesVerified()
    {
        var path = TempPath();
        try
        {
            var sections = new List<string>
            {
                "==== Introduction ====",
                "This document describes the Format Factory pipeline.",
                "",
                "==== Configuration ====",
                "Output format: Plain text",
                "Encoding: UTF-8 no BOM",
                "Line endings: LF",
                "",
                "==== Footer ====",
                "Generated by FormatFactory.Txt.TxtWriter",
            };

            TxtWriter.WriteLinesToFile(sections, path);
            var content = File.ReadAllText(path);

            Assert.Contains("Introduction", content);
            Assert.Contains("Configuration", content);
            Assert.Contains("Footer", content);
            Assert.Contains("Plain text", content);
            Assert.Contains("UTF-8 no BOM", content);
            Assert.Contains("FormatFactory.Txt.TxtWriter", content);

            // Verify LF-only
            Assert.DoesNotContain("\r\n", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
