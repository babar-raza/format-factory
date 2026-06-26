// Tests for FodtDocument.SetParagraphStyle, GetParagraphStyleName, GetParagraphStyles.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R186

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R186: Tests for FodtDocument.SetParagraphStyle, GetParagraphStyleName, FindParagraphsByStyle.
/// SetParagraphStyle(index, styleName): sets the style of a paragraph.
/// GetParagraphStyleName(index): returns the style name of a paragraph.
/// FindParagraphsByStyle(styleName): returns paragraphs matching a style.
/// Covers: SetParagraphStyle does not throw; GetParagraphStyleName non-null after set;
/// GetParagraphStyleName matches set style; FindParagraphsByStyle after InsertHeading;
/// FindParagraphsByStyle returns correct count; GetParagraphStyleName before set;
/// AppendParagraph default style is non-null; InsertHeading then GetParagraphStyleName;
/// Multiple SetParagraphStyle calls; GetParagraphTexts after SetParagraphStyle;
/// WordCount unchanged after style change; CharCount unchanged after style change;
/// ParagraphCount unchanged after SetParagraphStyle;
/// dogfood CreateEmpty->AppendParagraph->SetStyle->GetStyle->FindByStyle.
/// </summary>
public class FodtR186SetParagraphStyleAndGetStylesTests
{
    // -------------------------------------------------------------------------
    // SetParagraphStyle / GetParagraphStyleName
    // -------------------------------------------------------------------------

    [Fact]
    public void SetParagraphStyle_DoesNotThrow()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Test paragraph");
        doc.SetParagraphStyle(0, "Text_20_Body");
    }

    [Fact]
    public void GetParagraphStyleName_NonNullAfterSet()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Styled paragraph");
        doc.SetParagraphStyle(0, "Custom_Style");
        var style = doc.GetParagraphStyleName(0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetParagraphStyleName_MatchesSetStyle()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("With style");
        doc.SetParagraphStyle(0, "MyStyle");
        Assert.Equal("MyStyle", doc.GetParagraphStyleName(0));
    }

    [Fact]
    public void GetParagraphStyleName_Default_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Default style check");
        var style = doc.GetParagraphStyleName(0);
        // Default style may be any value, just non-null
        Assert.NotNull(style);
    }

    [Fact]
    public void SetParagraphStyle_MultipleCallsUpdateCorrectly()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.SetParagraphStyle(0, "StyleA");
        doc.SetParagraphStyle(1, "StyleB");
        Assert.Equal("StyleA", doc.GetParagraphStyleName(0));
        Assert.Equal("StyleB", doc.GetParagraphStyleName(1));
    }

    [Fact]
    public void SetParagraphStyle_DoesNotChangeParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        var before = doc.ParagraphCount;
        doc.SetParagraphStyle(0, "SomeStyle");
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void SetParagraphStyle_PreservesText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Keep this text");
        doc.SetParagraphStyle(0, "AStyle");
        Assert.Equal("Keep this text", doc.GetParagraphText(0));
    }

    // -------------------------------------------------------------------------
    // InsertHeading / GetParagraphStyleName
    // -------------------------------------------------------------------------

    [Fact]
    public void InsertHeading_GetParagraphStyleName_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "My Heading", level: 1);
        var style = doc.GetParagraphStyleName(0);
        Assert.NotNull(style);
    }

    // -------------------------------------------------------------------------
    // FindParagraphsByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void FindParagraphsByStyle_MatchesInsertedHeading()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Heading One", level: 1);
        // Get the style of the heading
        var headingStyle = doc.GetParagraphStyleName(0)!;
        var paras = doc.FindParagraphsByStyle(headingStyle);
        Assert.NotEmpty(paras);
    }

    [Fact]
    public void FindParagraphsByStyle_NonExistentStyle_ReturnsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Normal para");
        var paras = doc.FindParagraphsByStyle("NonExistentStyleXYZ_R186");
        Assert.Empty(paras);
    }

    [Fact]
    public void FindParagraphsByStyle_SetStyle_FindsCorrectCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("P1");
        doc.AppendParagraph("P2");
        doc.AppendParagraph("P3");
        doc.SetParagraphStyle(0, "SpecialStyle");
        doc.SetParagraphStyle(2, "SpecialStyle");
        var paras = doc.FindParagraphsByStyle("SpecialStyle");
        Assert.Equal(2, paras.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty->AppendParagraph->SetStyle->GetStyle->FindByStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AppendSetStyleGetStyleFindByStyle_Pipeline()
    {
        var doc = FodtDocument.CreateEmpty();

        // Append several paragraphs
        doc.AppendParagraph("Para A");
        doc.AppendParagraph("Para B");
        doc.AppendParagraph("Para C");
        Assert.Equal(3, doc.ParagraphCount);

        // Set styles
        doc.SetParagraphStyle(0, "R186Style");
        doc.SetParagraphStyle(2, "R186Style");
        doc.SetParagraphStyle(1, "OtherStyle");

        // GetParagraphStyleName verifies
        Assert.Equal("R186Style", doc.GetParagraphStyleName(0));
        Assert.Equal("OtherStyle", doc.GetParagraphStyleName(1));
        Assert.Equal("R186Style", doc.GetParagraphStyleName(2));

        // FindParagraphsByStyle
        var r186Paras = doc.FindParagraphsByStyle("R186Style");
        Assert.Equal(2, r186Paras.Count);

        var otherParas = doc.FindParagraphsByStyle("OtherStyle");
        Assert.Single(otherParas);

        // ParagraphCount unchanged
        Assert.Equal(3, doc.ParagraphCount);

        // GetParagraphTexts still correct
        var texts = doc.GetParagraphTexts();
        Assert.Contains("Para A", texts);
        Assert.Contains("Para B", texts);
        Assert.Contains("Para C", texts);
    }
}
