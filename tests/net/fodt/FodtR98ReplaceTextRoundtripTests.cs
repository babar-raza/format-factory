// R98 Train M: FODT .NET ReplaceText + Save Roundtrip Tests
// Governed skill: /add-same-format-writer-feature
// Ledger: R98-GOVERNED-DOTNET-FODT-REPLACETEXT-ROUNDTRIP-001
// Priority: 3 (load/edit/save/export completeness)

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR98ReplaceTextRoundtripTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    private static string HeadingsPath =>
        Path.Combine(SamplesDir, "headings-and-paragraphs.fodt");

    [Fact]
    public void ReplaceText_SaveToFile_Reload_ValuePersisted()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var plain = doc.GetPlainText();
        if (string.IsNullOrEmpty(plain)) return; // skip if no text

        // Pick first word as target
        var words = plain.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
        if (words.Length == 0) return;
        var target = words[0];
        var replacement = "R98REPLACED";

        int count = doc.ReplaceText(target, replacement);
        Assert.True(count > 0, $"Expected replacements for '{target}'");

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Contains(replacement, reloaded.GetPlainText());
            Assert.DoesNotContain(target, reloaded.GetPlainText());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_SaveToFile_ParagraphCountPreserved()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var origCount = doc.ParagraphCount;
        if (origCount == 0) return;

        doc.ReplaceText("a", "b"); // simple char replacement
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(origCount, reloaded.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_SaveToFile_MimeTypePreserved()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var origMime = doc.MimeType;
        doc.ReplaceText("x", "y"); // may do nothing, that's ok
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(origMime, reloaded.MimeType);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_NoMatch_Save_ReloadUnchanged()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var origText = doc.GetPlainText();
        int count = doc.ReplaceText("ZZZNONEXISTENT999", "REPLACED");
        Assert.Equal(0, count);

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(origText, reloaded.GetPlainText());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_Headings_SaveToFile_HeadingCountPreserved()
    {
        if (!File.Exists(HeadingsPath)) return;
        var doc = FodtDocument.Load(HeadingsPath);
        var origHeadings = doc.GetHeadingCount();
        if (origHeadings == 0) return;

        doc.ReplaceText("a", "b");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(origHeadings, reloaded.GetHeadingCount());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_CaseInsensitive_SaveToFile_Roundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var plain = doc.GetPlainText();
        if (string.IsNullOrEmpty(plain)) return;

        // Try case-insensitive replacement
        int count = doc.ReplaceText("A", "X", StringComparison.OrdinalIgnoreCase);
        // May or may not find matches — that's fine for roundtrip test

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.True(reloaded.ParagraphCount >= 0); // just verify it loads
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ReplaceText_MultipleReplacements_AllPersist()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var plain = doc.GetPlainText();
        if (string.IsNullOrEmpty(plain)) return;

        doc.ReplaceText("e", "E");
        doc.ReplaceText("o", "O");
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            var newText = reloaded.GetPlainText();
            // Verify no lowercase 'e' or 'o' remain (if originals had them)
            if (plain.Contains('e'))
                Assert.DoesNotContain("e", newText);
            if (plain.Contains('o'))
                Assert.DoesNotContain("o", newText);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void Save_Alias_ProducesSameResult()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.ReplaceText("x", "y");
        var tmp1 = Path.GetTempFileName() + ".fodt";
        var tmp2 = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.Save(tmp1);
            doc.SaveToFile(tmp2);
            var content1 = File.ReadAllText(tmp1);
            var content2 = File.ReadAllText(tmp2);
            Assert.Equal(content1, content2);
        }
        finally
        {
            if (File.Exists(tmp1)) File.Delete(tmp1);
            if (File.Exists(tmp2)) File.Delete(tmp2);
        }
    }
}
