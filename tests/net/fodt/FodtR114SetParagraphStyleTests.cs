using FormatFactory.Fodt;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R114 Train B: SetParagraphStyle/GetParagraphStyles — paragraph ODF style management.
/// </summary>
public class FodtR114SetParagraphStyleTests
{
    private static FodtDocument MakeDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Introduction");
        doc.AppendParagraph("Body text goes here.");
        doc.AppendParagraph("Conclusion");
        return doc;
    }

    [Fact]
    public void SetParagraphStyle_AndGetParagraphStyles_RoundTrip()
    {
        var doc = MakeDoc();
        doc.SetParagraphStyle(0, "Heading1");
        var styles = doc.GetParagraphStyles();
        Assert.Equal("Heading1", styles[0]);
    }

    [Fact]
    public void GetParagraphStyles_CountMatchesParagraphCount()
    {
        var doc = MakeDoc();
        var styles = doc.GetParagraphStyles();
        Assert.Equal(doc.ParagraphCount, styles.Count);
    }

    [Fact]
    public void SetParagraphStyle_ThrowsOnOutOfRangeIndex()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.SetParagraphStyle(99, "SomeStyle"));
    }

    [Fact]
    public void SetParagraphStyle_ThrowsOnNegativeIndex()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.SetParagraphStyle(-1, "SomeStyle"));
    }

    [Fact]
    public void SetParagraphStyle_PersistsAfterSaveAndReload()
    {
        var doc = MakeDoc();
        doc.SetParagraphStyle(1, "BodyText");
        var tmp = Path.Combine(Path.GetTempPath(), $"fodt-r114-style-{Guid.NewGuid()}.fodt");
        try
        {
            doc.Save(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var styles = reloaded.GetParagraphStyles();
            Assert.Equal("BodyText", styles[1]);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void SetParagraphStyle_MultipleParagraphs_EachCorrect()
    {
        var doc = MakeDoc();
        doc.SetParagraphStyle(0, "Title");
        doc.SetParagraphStyle(1, "BodyText");
        doc.SetParagraphStyle(2, "Footnote");
        var styles = doc.GetParagraphStyles();
        Assert.Equal("Title", styles[0]);
        Assert.Equal("BodyText", styles[1]);
        Assert.Equal("Footnote", styles[2]);
    }

    [Fact]
    public void GetParagraphStyles_EmptyDoc_ReturnsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        var styles = doc.GetParagraphStyles();
        Assert.Empty(styles);
    }

    [Fact]
    public void SetParagraphStyle_ThrowsOnNullStyle()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentNullException>(() =>
            doc.SetParagraphStyle(0, null!));
    }

    [Fact]
    public void GetParagraphStyles_NoStyleSet_ReturnsEmptyStrings()
    {
        var doc = MakeDoc();
        var styles = doc.GetParagraphStyles();
        // Each paragraph may have a default style or empty string — must not throw
        Assert.Equal(3, styles.Count);
        foreach (var s in styles)
            Assert.NotNull(s);
    }
}
