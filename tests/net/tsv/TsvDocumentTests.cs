// FormatFactory.Tsv.Tests — TsvDocument unit tests

using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvDocumentTests
{
    [Fact]
    public void Load_WithHeaders_SetsHeadersAndRows()
    {
        var doc = TsvDocument.Load("Name\tAge\nAlice\t30\nBob\t25\n", hasHeaders: true);
        Assert.True(doc.HasHeaders);
        Assert.NotNull(doc.Headers);
        Assert.Equal(new[] { "Name", "Age" }, doc.Headers);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal("Alice", doc.Rows[0][0]);
        Assert.Equal("25", doc.Rows[1][1]);
    }

    [Fact]
    public void Load_WithoutHeaders_NoHeadersSet()
    {
        var doc = TsvDocument.Load("a\tb\n1\t2\n", hasHeaders: false);
        Assert.False(doc.HasHeaders);
        Assert.Null(doc.Headers);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal(new[] { "a", "b" }, doc.Rows[0]);
    }

    [Fact]
    public void RowCount_ReturnsCorrectCount()
    {
        var doc = TsvDocument.Load("h1\th2\nr1\tr2\nr3\tr4\n");
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void ColumnCount_FromHeaders()
    {
        var doc = TsvDocument.Load("c1\tc2\tc3\nv1\tv2\tv3\n");
        Assert.Equal(3, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_NoHeaders_FromFirstRow()
    {
        var doc = TsvDocument.Load("a\tb\n", hasHeaders: false);
        Assert.Equal(2, doc.ColumnCount);
    }

    [Fact]
    public void ColumnCount_EmptyDocument_ReturnsZero()
    {
        var doc = TsvDocument.Load("", hasHeaders: false);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void ToTsv_Roundtrip_WithHeaders()
    {
        var input = "Name\tAge\nAlice\t30\nBob\t25\n";
        var doc = TsvDocument.Load(input);
        var output = doc.ToTsv();
        Assert.Equal(input, output);
    }

    [Fact]
    public void ToTsv_Roundtrip_WithoutHeaders()
    {
        var input = "a\tb\n1\t2\n";
        var doc = TsvDocument.Load(input, hasHeaders: false);
        var output = doc.ToTsv();
        Assert.Equal(input, output);
    }

    [Fact]
    public void FileIo_Roundtrip()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_tsv_doc_{Guid.NewGuid():N}.tsv");
        try
        {
            var doc = TsvDocument.Load("Name\tScore\nAlice\t100\n");
            doc.SaveToFile(path);
            Assert.True(File.Exists(path));

            var loaded = TsvDocument.LoadFile(path);
            Assert.Equal(doc.Headers, loaded.Headers);
            Assert.Equal(doc.RowCount, loaded.RowCount);
            Assert.Equal(doc.Rows[0][0], loaded.Rows[0][0]);
            Assert.Equal(doc.Rows[0][1], loaded.Rows[0][1]);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void Load_EmptyWithHeaders_HeaderOnly()
    {
        var doc = TsvDocument.Load("h1\th2\n");
        Assert.True(doc.HasHeaders);
        Assert.NotNull(doc.Headers);
        Assert.Equal(new[] { "h1", "h2" }, doc.Headers);
        Assert.Empty(doc.Rows);
        Assert.Equal(0, doc.RowCount);
        Assert.Equal(2, doc.ColumnCount);
    }
}
