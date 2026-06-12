// FormatFactory.Tsv.Tests — TsvWriter unit tests

using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvWriterTests
{
    [Fact]
    public void WriteRows_SimpleRows_ProducesCorrectTsv()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "a", "b", "c" },
            new[] { "1", "2", "3" },
        };
        var result = TsvWriter.WriteRows(rows);
        Assert.Equal("a\tb\tc\n1\t2\t3\n", result);
    }

    [Fact]
    public void WriteRows_EmptyCollection_ReturnsEmptyString()
    {
        var result = TsvWriter.WriteRows(new List<IEnumerable<string?>>());
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void WriteRows_NullField_TreatedAsEmpty()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { "a", null, "c" } };
        var result = TsvWriter.WriteRows(rows);
        Assert.Equal("a\t\tc\n", result);
    }

    [Fact]
    public void WriteRowsToFile_CreatesFileWithoutBom()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_tsv_write_{Guid.NewGuid():N}.tsv");
        try
        {
            var rows = new List<IEnumerable<string?>> { new[] { "x", "y" } };
            TsvWriter.WriteRowsToFile(rows, path);
            Assert.True(File.Exists(path));
            var bytes = File.ReadAllBytes(path);
            // No BOM
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "File must not have a UTF-8 BOM");
            var content = File.ReadAllText(path);
            Assert.Contains("x\ty", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteRows_Roundtrip_ReadBack()
    {
        var original = new List<IEnumerable<string?>>
        {
            new[] { "Name", "Age", "City" },
            new[] { "Alice", "30", "NYC" },
            new[] { "Bob", "25", "LA" },
        };
        var tsv = TsvWriter.WriteRows(original);
        var parsed = TsvReader.ReadRows(tsv);
        Assert.Equal(3, parsed.Count);
        Assert.Equal(new[] { "Name", "Age", "City" }, parsed[0]);
        Assert.Equal(new[] { "Alice", "30", "NYC" }, parsed[1]);
        Assert.Equal(new[] { "Bob", "25", "LA" }, parsed[2]);
    }

    [Fact]
    public void WriteRows_FieldContainsTab_ThrowsTsvException()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "has\ttab" } };
        var ex = Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
        Assert.Contains("tab character", ex.Message);
    }

    [Fact]
    public void WriteRows_FieldContainsNewline_ThrowsTsvException()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "has\nnewline" } };
        var ex = Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
        Assert.Contains("newline character", ex.Message);
    }

    [Fact]
    public void WriteRows_FieldContainsCR_ThrowsTsvException()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "has\rreturn" } };
        var ex = Assert.Throws<TsvException>(() => TsvWriter.WriteRows(rows));
        Assert.Contains("newline character", ex.Message);
    }

    [Fact]
    public void WriteRowsToFile_NullPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvWriter.WriteRowsToFile(new List<IEnumerable<string?>>(), null!));
    }

    [Fact]
    public void WriteRows_NullInput_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => TsvWriter.WriteRows(null!));
    }
}
