using FormatFactory.Csv;
using Xunit;

namespace FormatFactory.Csv.Tests;

public class CsvReaderTests
{
    [Fact]
    public void ReadRows_SimpleInput_ReturnsCorrectRows()
    {
        var rows = CsvReader.ReadRows("a,b,c\n1,2,3\n");
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "a", "b", "c" }, rows[0]);
        Assert.Equal(new[] { "1", "2", "3" }, rows[1]);
    }

    [Fact]
    public void ReadRows_EmptyInput_ReturnsEmpty()
    {
        var rows = CsvReader.ReadRows("");
        Assert.Empty(rows);
    }

    [Fact]
    public void ReadRows_QuotedFieldWithComma_ParsesCorrectly()
    {
        var rows = CsvReader.ReadRows("\"a,b\",c\n");
        Assert.Single(rows);
        Assert.Equal("a,b", rows[0][0]);
        Assert.Equal("c", rows[0][1]);
    }

    [Fact]
    public void ReadRows_QuotedFieldWithNewline_ParsesCorrectly()
    {
        var rows = CsvReader.ReadRows("\"line1\nline2\",b\n");
        Assert.Single(rows);
        Assert.Equal("line1\nline2", rows[0][0]);
        Assert.Equal("b", rows[0][1]);
    }

    [Fact]
    public void ReadRows_EscapedQuotes_ParsesCorrectly()
    {
        var rows = CsvReader.ReadRows("\"she said \"\"hello\"\"\",b\n");
        Assert.Single(rows);
        Assert.Equal("she said \"hello\"", rows[0][0]);
    }

    [Fact]
    public void ReadRows_BomStripped()
    {
        var rows = CsvReader.ReadRows("\uFEFFa,b\n");
        Assert.Single(rows);
        Assert.Equal("a", rows[0][0]);
    }

    [Fact]
    public void ReadRows_CrLfLineEndings()
    {
        var rows = CsvReader.ReadRows("a,b\r\n1,2\r\n");
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "a", "b" }, rows[0]);
        Assert.Equal(new[] { "1", "2" }, rows[1]);
    }

    [Fact]
    public void ReadRows_SingleColumn()
    {
        var rows = CsvReader.ReadRows("a\nb\nc\n");
        Assert.Equal(3, rows.Count);
        Assert.Equal(new[] { "a" }, rows[0]);
    }

    [Fact]
    public void ReadRows_NullInput_Throws()
    {
        Assert.Throws<CsvReaderException>(() => CsvReader.ReadRows((string)null!));
    }

    [Fact]
    public void ReadRowsFromFile_EmptyPath_Throws()
    {
        Assert.Throws<CsvReaderException>(() => CsvReader.ReadRowsFromFile(""));
    }

    [Fact]
    public void ReadRows_NoTrailingNewline_StillParses()
    {
        var rows = CsvReader.ReadRows("a,b\n1,2");
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "1", "2" }, rows[1]);
    }

    [Fact]
    public void ReadRows_EmptyFields_PreservedAsEmpty()
    {
        var rows = CsvReader.ReadRows(",,,\n");
        Assert.Single(rows);
        Assert.Equal(4, rows[0].Length);
        Assert.All(rows[0], f => Assert.Equal("", f));
    }
}
