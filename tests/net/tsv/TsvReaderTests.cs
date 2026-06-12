// FormatFactory.Tsv.Tests — TsvReader unit tests

using FormatFactory.Tsv;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvReaderTests
{
    [Fact]
    public void ReadRows_SimpleTsv_ParsesCorrectly()
    {
        var rows = TsvReader.ReadRows("a\tb\tc\n1\t2\t3\n");
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "a", "b", "c" }, rows[0]);
        Assert.Equal(new[] { "1", "2", "3" }, rows[1]);
    }

    [Fact]
    public void ReadRows_EmptyInput_ReturnsEmptyList()
    {
        var rows = TsvReader.ReadRows("");
        Assert.Empty(rows);
    }

    [Fact]
    public void ReadRows_SingleColumn_NoTabs()
    {
        var rows = TsvReader.ReadRows("hello\nworld\n");
        Assert.Equal(2, rows.Count);
        Assert.Single(rows[0]);
        Assert.Equal("hello", rows[0][0]);
        Assert.Equal("world", rows[1][0]);
    }

    [Fact]
    public void ReadRows_WithBom_StrippedCorrectly()
    {
        var content = "\uFEFFname\tage\nAlice\t30\n";
        var rows = TsvReader.ReadRows(content);
        Assert.Equal(2, rows.Count);
        Assert.Equal("name", rows[0][0]); // BOM stripped, not prepended to first field
    }

    [Fact]
    public void ReadRowsFromFile_WrittenFile_RoundTrips()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_tsv_read_{Guid.NewGuid():N}.tsv");
        try
        {
            File.WriteAllText(path, "x\ty\n1\t2\n", new UTF8Encoding(false));
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(2, rows.Count);
            Assert.Equal(new[] { "x", "y" }, rows[0]);
            Assert.Equal(new[] { "1", "2" }, rows[1]);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ReadRows_ExceedsMaxSize_ThrowsTsvException()
    {
        // Create a string just over 64MB
        var huge = new string('a', 64 * 1024 * 1024 + 1);
        var ex = Assert.Throws<TsvException>(() => TsvReader.ReadRows(huge));
        Assert.Contains("maximum allowed size", ex.Message);
    }

    [Fact]
    public void ReadRows_TrailingEmptyLines_Skipped()
    {
        var rows = TsvReader.ReadRows("a\tb\n1\t2\n\n\n");
        Assert.Equal(2, rows.Count);
    }

    [Fact]
    public void ReadRows_CrLfLineEndings_Normalized()
    {
        var rows = TsvReader.ReadRows("a\tb\r\n1\t2\r\n");
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "a", "b" }, rows[0]);
    }

    [Fact]
    public void ReadRows_SingleRow_NoTrailingNewline()
    {
        var rows = TsvReader.ReadRows("a\tb\tc");
        Assert.Single(rows);
        Assert.Equal(new[] { "a", "b", "c" }, rows[0]);
    }

    [Fact]
    public void ReadRows_NullInput_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => TsvReader.ReadRows((string)null!));
    }

    [Fact]
    public void ReadRowsFromFile_NonExistentFile_ThrowsTsvException()
    {
        var ex = Assert.Throws<TsvException>(() =>
            TsvReader.ReadRowsFromFile("/nonexistent/path/file.tsv"));
        Assert.Contains("File not found", ex.Message);
    }

    [Fact]
    public void ReadRows_Stream_ParsesCorrectly()
    {
        var bytes = Encoding.UTF8.GetBytes("col1\tcol2\nval1\tval2\n");
        using var stream = new MemoryStream(bytes);
        var rows = TsvReader.ReadRows(stream);
        Assert.Equal(2, rows.Count);
        Assert.Equal(new[] { "col1", "col2" }, rows[0]);
    }
}
