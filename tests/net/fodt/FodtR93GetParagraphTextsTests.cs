// R93 Train L: FODT .NET GetParagraphTexts + ReplaceText Round-Trip Tests
// Governed skill: /add-dotnet-api
// Ledger: R93-GOVERNED-DOTNET-FODT-GETPARAGRAPHTEXTS-001
// Sprint: FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR93GetParagraphTextsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    private static string HeadingsFodtPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void GetParagraphTexts_ReturnsNonNullList()
    {
        var doc = FodtDocument.Load(MinimalFodtPath);
        var texts = doc.GetParagraphTexts();
        Assert.NotNull(texts);
    }

    [Fact]
    public void GetParagraphTexts_CountMatchesParagraphCount()
    {
        var doc = FodtDocument.Load(MinimalFodtPath);
        var texts = doc.GetParagraphTexts();
        Assert.Equal(doc.ParagraphCount, texts.Count);
    }

    [Fact]
    public void GetParagraphTexts_AllStrings_NotNull()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var texts = doc.GetParagraphTexts();
        foreach (var t in texts)
            Assert.NotNull(t);
    }

    [Fact]
    public void GetParagraphTexts_ReturnsReadOnlyList()
    {
        var doc = FodtDocument.Load(MinimalFodtPath);
        var texts = doc.GetParagraphTexts();
        Assert.IsAssignableFrom<IReadOnlyList<string>>(texts);
    }

    [Fact]
    public void ReplaceText_ThenGetParagraphTexts_ReflectsChange()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var beforeTexts = doc.GetParagraphTexts().ToList();
        // Find a non-empty paragraph to replace
        var originalText = beforeTexts.FirstOrDefault(t => t.Length > 0);
        if (originalText == null) return; // Skip if no non-empty paragraphs

        var newText = "R93_REPLACED_TEXT_" + Guid.NewGuid().ToString("N")[..8];
        int replaced = doc.ReplaceText(originalText, newText);
        Assert.True(replaced > 0, "Expected at least one replacement");

        var afterTexts = doc.GetParagraphTexts();
        Assert.Contains(newText, afterTexts);
    }

    [Fact]
    public void ReplaceText_SaveFile_Reload_PreservesReplacement()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var texts = doc.GetParagraphTexts().ToList();
        var originalText = texts.FirstOrDefault(t => t.Length > 2);
        if (originalText == null) return;

        var newText = "R93_ROUNDTRIP_" + Guid.NewGuid().ToString("N")[..8];
        doc.ReplaceText(originalText, newText);

        var tmpPath = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmpPath);
            var reloaded = FodtDocument.Load(tmpPath);
            var reloadedTexts = reloaded.GetParagraphTexts();
            Assert.Contains(newText, reloadedTexts);
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }

    [Fact]
    public void GetParagraphTexts_StableAcrossMultipleCalls()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var texts1 = doc.GetParagraphTexts();
        var texts2 = doc.GetParagraphTexts();
        Assert.Equal(texts1.Count, texts2.Count);
        for (int i = 0; i < texts1.Count; i++)
            Assert.Equal(texts1[i], texts2[i]);
    }

    [Fact]
    public void GetParagraphTexts_HeadingsAndParagraphsDoc_ContainsContent()
    {
        var doc = FodtDocument.Load(HeadingsFodtPath);
        var texts = doc.GetParagraphTexts();
        Assert.True(texts.Count > 0, "Expected paragraphs in headings-and-paragraphs.fodt");
        Assert.True(texts.Any(t => t.Length > 0), "Expected at least one non-empty paragraph");
    }
}
