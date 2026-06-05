// FormatFactory.Txt.Tests — TxtWriter unit tests
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Txt;
using Xunit;

namespace FormatFactory.Txt.Tests;

public class TxtWriterTests
{
    // -------------------------------------------------------------------------
    // WriteLines — in-memory
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteLines_SimpleLines_JoinedWithLf()
    {
        var result = TxtWriter.WriteLines(new[] { "line1", "line2" });
        Assert.Equal("line1\nline2", result);
    }

    [Fact]
    public void WriteLines_NullLine_TreatedAsEmpty()
    {
        var result = TxtWriter.WriteLines(new string?[] { "a", null, "b" });
        Assert.Equal("a\n\nb", result);
    }

    [Fact]
    public void WriteLines_EmptyList_ReturnsEmpty()
    {
        var result = TxtWriter.WriteLines(new List<string?>());
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void WriteLines_SingleLine_NoTrailingLf()
    {
        var result = TxtWriter.WriteLines(new[] { "hello" });
        Assert.Equal("hello", result);
        Assert.DoesNotContain("\n", result);
    }

    [Fact]
    public void WriteLines_CrLf_NormalizedToLf()
    {
        var result = TxtWriter.WriteLines(new[] { "a\r\nb", "c" });
        Assert.DoesNotContain("\r", result);
        Assert.Contains("\n", result);
    }

    // -------------------------------------------------------------------------
    // WriteLinesToFile — physical file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteLinesToFile_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_txt_test_{Guid.NewGuid():N}.txt");
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "hello", "world" }, path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Contains("hello", content);
            Assert.Contains("world", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteLinesToFile_NoUtf8Bom()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_txt_bom_{Guid.NewGuid():N}.txt");
        try
        {
            TxtWriter.WriteLinesToFile(new[] { "x" }, path);
            var bytes = File.ReadAllBytes(path);
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "File must not have a UTF-8 BOM");
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteLinesToFile_NullPath_Throws()
    {
        Assert.Throws<TxtWriterException>(() =>
            TxtWriter.WriteLinesToFile(new[] { "x" }, null!));
    }
}
