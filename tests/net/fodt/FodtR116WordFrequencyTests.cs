using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R116 Train A: GetWordFrequency — document word frequency analysis.
/// </summary>
public class FodtR116WordFrequencyTests
{
    [Fact]
    public void GetWordFrequency_CountsWords()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("hello world hello");
        var freq = doc.GetWordFrequency();
        Assert.Equal(2, freq["hello"]);
        Assert.Equal(1, freq["world"]);
    }

    [Fact]
    public void GetWordFrequency_CaseInsensitive()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello HELLO hello");
        var freq = doc.GetWordFrequency();
        Assert.Equal(3, freq["hello"]);
    }

    [Fact]
    public void GetWordFrequency_EmptyDoc_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        var freq = doc.GetWordFrequency();
        Assert.Empty(freq);
    }

    [Fact]
    public void GetWordFrequency_MinLengthFilter()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("a bb ccc dddd");
        var freq = doc.GetWordFrequency(minLength: 3);
        Assert.False(freq.ContainsKey("a"));
        Assert.False(freq.ContainsKey("bb"));
        Assert.True(freq.ContainsKey("ccc"));
        Assert.True(freq.ContainsKey("dddd"));
    }

    [Fact]
    public void GetWordFrequency_MultipleParagraphs_Aggregated()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("the quick fox");
        doc.AppendParagraph("the lazy dog");
        var freq = doc.GetWordFrequency();
        Assert.Equal(2, freq["the"]);
        Assert.Equal(1, freq["fox"]);
    }

    [Fact]
    public void GetWordFrequency_PunctuationStripped()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello, world! Hello.");
        var freq = doc.GetWordFrequency();
        Assert.Equal(2, freq["hello"]);
        Assert.Equal(1, freq["world"]);
    }

    [Fact]
    public void GetWordFrequency_DogfoodPipeline()
    {
        // Build doc → add content → get word frequency → verify top word
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Format Factory", 1);
        doc.AppendParagraph("Format Factory is a file format processing library.");
        doc.AppendParagraph("Format Factory handles many file formats.");
        var freq = doc.GetWordFrequency(minLength: 4);
        Assert.True(freq.TryGetValue("format", out int fcount) && fcount >= 3);
        Assert.True(freq.TryGetValue("factory", out int factCount) && factCount >= 2);
    }

    [Fact]
    public void GetWordFrequency_WithHeadings()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "test heading test", 1);
        var freq = doc.GetWordFrequency();
        // Headings are paragraphs too
        Assert.True(freq.ContainsKey("test"));
    }
}
