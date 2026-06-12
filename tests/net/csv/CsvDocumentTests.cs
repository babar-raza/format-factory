using FormatFactory.Csv;
using Xunit;

namespace FormatFactory.Csv.Tests;

public class CsvDocumentTests
{
    [Fact]
    public void Load_WithHeaders_SplitsCorrectly()
    {
        var doc = CsvDocument.Load("name,age\nAlice,30\nBob,25\n");
        Assert.True(doc.HasHeaders);
        Assert.Equal(new[] { "name", "age" }, doc.Headers);
        Assert.Equal(2, doc.RowCount);
        Assert.Equal(2, doc.ColumnCount);
    }

    [Fact]
    public void Load_WithoutHeaders_NoHeaderRow()
    {
        var doc = CsvDocument.Load("a,b\n1,2\n", hasHeaders: false);
        Assert.False(doc.HasHeaders);
        Assert.Null(doc.Headers);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void ToCsv_Roundtrip()
    {
        var input = "name,age\nAlice,30\nBob,25\n";
        var doc = CsvDocument.Load(input);
        var output = doc.ToCsv();
        var doc2 = CsvDocument.Load(output);
        Assert.Equal(doc.RowCount, doc2.RowCount);
        Assert.Equal(doc.Headers, doc2.Headers);
        Assert.Equal(doc.Rows[0], doc2.Rows[0]);
    }

    [Fact]
    public void GetColumn_ByIndex()
    {
        var doc = CsvDocument.Load("name,age\nAlice,30\nBob,25\n");
        var names = doc.GetColumn(0);
        Assert.Equal(new[] { "Alice", "Bob" }, names);
    }

    [Fact]
    public void GetColumn_ByHeaderName()
    {
        var doc = CsvDocument.Load("name,age\nAlice,30\nBob,25\n");
        var ages = doc.GetColumn("age");
        Assert.Equal(new[] { "30", "25" }, ages);
    }

    [Fact]
    public void GetColumn_UnknownHeader_Throws()
    {
        var doc = CsvDocument.Load("name,age\nAlice,30\n");
        Assert.Throws<CsvReaderException>(() => doc.GetColumn("email"));
    }

    [Fact]
    public void FileRoundtrip()
    {
        var tmp = Path.Combine(Path.GetTempPath(), $"csv_doc_test_{Guid.NewGuid()}.csv");
        try
        {
            var doc = CsvDocument.Load("x,y\n1,2\n3,4\n");
            doc.SaveToFile(tmp);
            var doc2 = CsvDocument.LoadFile(tmp);
            Assert.Equal(doc.RowCount, doc2.RowCount);
            Assert.Equal(doc.Headers, doc2.Headers);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Load_EmptyInput_EmptyDocument()
    {
        var doc = CsvDocument.Load("");
        Assert.Equal(0, doc.RowCount);
        Assert.Equal(0, doc.ColumnCount);
    }

    [Fact]
    public void Load_HeaderOnly_EmptyRows()
    {
        var doc = CsvDocument.Load("a,b,c\n");
        Assert.True(doc.HasHeaders);
        Assert.Equal(0, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);
    }
}
