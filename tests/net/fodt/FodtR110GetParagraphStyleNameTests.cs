// R110 Wave 4: FODT GetParagraphStyleName tests
// Ledger: R110-GOVERNED-DOTNET-FODT-GETPARAGRAPHSTYLENAME-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR110GetParagraphStyleNameTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void GetParagraphStyleName_ValidIndex_ReturnsStringOrNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.GetParagraphCount() == 0) return;
        // May return null or a style name string — both are valid
        var style = doc.GetParagraphStyleName(0);
        // No assertion on value — just that it runs without error
    }

    [Fact]
    public void GetParagraphStyleName_NegativeIndex_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetParagraphStyleName(-1));
    }

    [Fact]
    public void GetParagraphStyleName_OutOfRange_ReturnsNull()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Null(doc.GetParagraphStyleName(99999));
    }

    [Fact]
    public void GetParagraphStyleName_AllParagraphs_NoException()
    {
        var doc = FodtDocument.Load(MinimalPath);
        for (int i = 0; i < doc.GetParagraphCount(); i++)
        {
            // Should not throw for any valid index
            _ = doc.GetParagraphStyleName(i);
        }
    }

    [Fact]
    public void GetParagraphStyleName_AfterAppend_NewParagraphHasNoStyle()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("New paragraph R110");
        int lastIdx = doc.GetParagraphCount() - 1;
        // AppendParagraph creates a bare text:p with no style-name attribute
        Assert.Null(doc.GetParagraphStyleName(lastIdx));
    }

    [Fact]
    public void GetParagraphStyleName_AfterInsertHeading_HeadingMayHaveStyle()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.InsertHeading(0, "Styled Heading R110", 1);
        // InsertHeading doesn't set style-name, so should be null
        Assert.Null(doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void GetParagraphStyleName_IndexZero_Stable()
    {
        var doc = FodtDocument.Load(MinimalPath);
        if (doc.GetParagraphCount() == 0) return;
        var style1 = doc.GetParagraphStyleName(0);
        var style2 = doc.GetParagraphStyleName(0);
        Assert.Equal(style1, style2);
    }

    [Fact]
    public void GetParagraphStyleName_ConsistentWithParagraphCount()
    {
        var doc = FodtDocument.Load(MinimalPath);
        int count = doc.GetParagraphCount();
        // Last valid index should work
        if (count > 0)
            _ = doc.GetParagraphStyleName(count - 1);
        // One beyond should return null
        Assert.Null(doc.GetParagraphStyleName(count));
    }
}
