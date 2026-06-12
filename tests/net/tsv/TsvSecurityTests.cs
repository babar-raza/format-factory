// AUTH-HARDEN-002: Security and malformed-input tests for FormatFactory.Tsv

using System.Text;
using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvSecurityTests
{
    [Fact]
    public void ReadRows_EmbeddedNullBytes_PreservedInFields()
    {
        // Null bytes in field values — TSV reader should not crash
        var input = "a\tb\nval\x00ue\tother\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(2, rows.Count);
        Assert.Equal("val\x00ue", rows[1][0]); // Null byte preserved in field
        Assert.Equal("other", rows[1][1]);
    }

    [Fact]
    public void ReadRows_ExtremelyLongField_ParsesCorrectly()
    {
        // Single field with 1MB of data — well under 64MB guard
        var longField = new string('X', 1_000_000);
        var input = $"header\n{longField}\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(2, rows.Count);
        Assert.Equal(longField, rows[1][0]);
    }

    [Fact]
    public void ReadRows_ExtremelyWideRow_10000Columns()
    {
        // 10,000 tab-separated columns
        var fields = new string[10_000];
        for (int i = 0; i < fields.Length; i++)
            fields[i] = $"c{i}";

        var headerLine = string.Join("\t", fields);
        var input = headerLine + "\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Single(rows);
        Assert.Equal(10_000, rows[0].Length);
        Assert.Equal("c0", rows[0][0]);
        Assert.Equal("c9999", rows[0][9999]);
    }

    [Fact]
    public void ReadRows_Utf8BomVariation_StrippedCorrectly()
    {
        // UTF-8 BOM (EF BB BF) before content
        var bomBytes = new byte[] { 0xEF, 0xBB, 0xBF };
        var contentBytes = Encoding.UTF8.GetBytes("name\tage\nAlice\t30\n");
        var combined = new byte[bomBytes.Length + contentBytes.Length];
        Buffer.BlockCopy(bomBytes, 0, combined, 0, bomBytes.Length);
        Buffer.BlockCopy(contentBytes, 0, combined, bomBytes.Length, contentBytes.Length);

        using var stream = new MemoryStream(combined);
        var rows = TsvReader.ReadRows(stream);

        Assert.Equal(2, rows.Count);
        Assert.Equal("name", rows[0][0]); // BOM must not appear in first field
    }

    [Fact]
    public void ReadRows_MixedLineEndings_CrLfCrLf()
    {
        // Mix of \r\n, \n, and lone \r
        var input = "a\tb\r\n1\t2\n3\t4\r5\t6\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(4, rows.Count);
        Assert.Equal(new[] { "a", "b" }, rows[0]);
        Assert.Equal(new[] { "1", "2" }, rows[1]);
        Assert.Equal(new[] { "3", "4" }, rows[2]);
        Assert.Equal(new[] { "5", "6" }, rows[3]);
    }

    [Fact]
    public void ReadRows_EmptyFields_PreservedCorrectly()
    {
        // Adjacent tabs = empty fields
        var input = "\t\t\n\t\t\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(2, rows.Count);
        Assert.Equal(3, rows[0].Length);
        Assert.All(rows[0], f => Assert.Equal("", f));
    }

    [Fact]
    public void ReadRows_OnlyTabs_ParsesAsEmptyFields()
    {
        var input = "\t\t\t\t\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Single(rows);
        Assert.Equal(5, rows[0].Length); // 4 tabs = 5 fields
        Assert.All(rows[0], f => Assert.Equal("", f));
    }

    [Fact]
    public void ReadRows_UnicodeContent_ParsedCorrectly()
    {
        var input = "name\tvalue\n\u4E16\u754C\t\u2764\n\u00E9\u00E8\t\u00FC\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(3, rows.Count);
        Assert.Equal("\u4E16\u754C", rows[1][0]); // Chinese characters
        Assert.Equal("\u2764", rows[1][1]);         // Heart symbol
        Assert.Equal("\u00E9\u00E8", rows[2][0]);   // French accented chars
    }

    [Fact]
    public void ReadRows_JaggedRows_DifferentColumnCounts()
    {
        // Rows with different numbers of columns — should not crash
        var input = "a\tb\tc\n1\n2\t3\n4\t5\t6\t7\n";
        var rows = TsvReader.ReadRows(input);

        Assert.Equal(4, rows.Count);
        Assert.Equal(3, rows[0].Length); // header: 3 columns
        Assert.Single(rows[1]);          // 1 column
        Assert.Equal(2, rows[2].Length); // 2 columns
        Assert.Equal(4, rows[3].Length); // 4 columns
    }

    [Fact]
    public void ReadRows_NullStreamInput_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => TsvReader.ReadRows((Stream)null!));
    }
}
