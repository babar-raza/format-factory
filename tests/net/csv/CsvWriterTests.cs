// FormatFactory.Csv.Tests — CsvWriter unit tests
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Csv;
using Xunit;

namespace FormatFactory.Csv.Tests;

public class CsvWriterTests
{
    // -------------------------------------------------------------------------
    // EscapeField
    // -------------------------------------------------------------------------

    [Fact]
    public void EscapeField_Null_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, CsvWriter.EscapeField(null));
    }

    [Fact]
    public void EscapeField_Empty_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, CsvWriter.EscapeField(string.Empty));
    }

    [Fact]
    public void EscapeField_PlainValue_ReturnsUnchanged()
    {
        Assert.Equal("hello", CsvWriter.EscapeField("hello"));
    }

    [Fact]
    public void EscapeField_ContainsComma_WrapsInQuotes()
    {
        Assert.Equal("\"a,b\"", CsvWriter.EscapeField("a,b"));
    }

    [Fact]
    public void EscapeField_ContainsDoubleQuote_DoublesAndWraps()
    {
        Assert.Equal("\"say \"\"hi\"\"\"", CsvWriter.EscapeField("say \"hi\""));
    }

    [Fact]
    public void EscapeField_ContainsNewline_WrapsInQuotes()
    {
        Assert.Equal("\"line1\nline2\"", CsvWriter.EscapeField("line1\nline2"));
    }

    [Fact]
    public void EscapeField_ContainsCR_WrapsInQuotes()
    {
        var escaped = CsvWriter.EscapeField("a\rb");
        Assert.StartsWith("\"", escaped);
        Assert.EndsWith("\"", escaped);
    }

    // -------------------------------------------------------------------------
    // WriteRows — in-memory
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_SingleRow_ProducesOneLine()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "a", "b", "c" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("a,b,c\n", result);
    }

    [Fact]
    public void WriteRows_MultipleRows_EachOnNewLine()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "h1", "h2" },
            new[] { "v1", "v2" },
        };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("h1,h2\nv1,v2\n", result);
    }

    [Fact]
    public void WriteRows_NullField_TreatedAsEmpty()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { "a", null, "c" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("a,,c\n", result);
    }

    [Fact]
    public void WriteRows_EmptyRows_ReturnsEmptyString()
    {
        var result = CsvWriter.WriteRows(new List<IEnumerable<string?>>());
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void WriteRows_FieldWithComma_Quoted()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "a,b", "c" } };
        var result = CsvWriter.WriteRows(rows);
        Assert.Equal("\"a,b\",c\n", result);
    }

    // -------------------------------------------------------------------------
    // WriteRowsToFile — physical file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_csv_test_{Guid.NewGuid():N}.csv");
        try
        {
            var rows = new List<IEnumerable<string?>> { new[] { "x", "y" } };
            CsvWriter.WriteRowsToFile(rows, path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Contains("x,y", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteRowsToFile_NoUtf8Bom()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_csv_bom_{Guid.NewGuid():N}.csv");
        try
        {
            CsvWriter.WriteRowsToFile(new List<IEnumerable<string?>> { new[] { "a" } }, path);
            var bytes = File.ReadAllBytes(path);
            // UTF-8 BOM is 0xEF 0xBB 0xBF
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "File must not have a UTF-8 BOM");
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteRowsToFile_NullPath_Throws()
    {
        Assert.Throws<CsvWriterException>(() =>
            CsvWriter.WriteRowsToFile(new List<IEnumerable<string?>>(), null!));
    }
}
