// R88 Train I: FODT .NET text analysis API tests (GetPlainText, WordCount)
// Sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR88TextAnalysisTests
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string MinimalFodt =
        Path.Combine(FixturesDir, "fodt-minimal-roundtrip.fodt");

    // ---- GetPlainText ----

    [Fact]
    public void GetPlainText_MinimalFixture_ReturnsNonNull()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var text = doc.GetPlainText();
        Assert.NotNull(text);
    }

    [Fact]
    public void GetPlainText_WithParagraphs_JoinsWithNewlines()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var text = doc.GetPlainText();
        if (doc.Paragraphs.Count >= 2)
        {
            Assert.Contains("\n", text);
        }
    }

    [Fact]
    public void GetPlainText_ContainsParagraphText()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var text = doc.GetPlainText();
        foreach (var para in doc.Paragraphs)
        {
            if (!string.IsNullOrEmpty(para.Text))
            {
                Assert.Contains(para.Text, text);
            }
        }
    }

    // ---- WordCount ----

    [Fact]
    public void WordCount_MinimalFixture_NonNegative()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        Assert.True(doc.WordCount >= 0);
    }

    [Fact]
    public void WordCount_MatchesManualCount()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var text = doc.GetPlainText();
        int expected = string.IsNullOrWhiteSpace(text)
            ? 0
            : text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
        Assert.Equal(expected, doc.WordCount);
    }

    // ---- MimeType / OdfVersion ----

    [Fact]
    public void MimeType_MinimalFixture_IsTextOrNull()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var mime = doc.MimeType;
        if (mime != null)
        {
            Assert.Contains("text", mime);
        }
    }

    [Fact]
    public void OdfVersion_MinimalFixture_IsVersionOrNull()
    {
        var doc = FodtDocument.Load(MinimalFodt);
        var ver = doc.OdfVersion;
        if (ver != null)
        {
            Assert.Matches(@"^\d+\.\d+", ver);
        }
    }
}
