// R109 Lane D: FODT ExportToHtmlFile tests
// Ledger: R109-GOVERNED-DOTNET-FODT-EXPORTTOHTMLFILE-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR109ExportToHtmlFileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void ExportToHtmlFile_CreatesFile()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_ContainsHtmlTags()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("<!DOCTYPE html>", content);
            Assert.Contains("<html>", content);
            Assert.Contains("</html>", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_MatchesExportToHtml()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var expected = doc.ExportToHtml();
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            var actual = File.ReadAllText(tmp);
            Assert.Equal(expected, actual);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_NullPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile(null!));
    }

    [Fact]
    public void ExportToHtmlFile_EmptyPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile(""));
        Assert.Throws<ArgumentException>(() => doc.ExportToHtmlFile("   "));
    }

    [Fact]
    public void ExportToHtmlFile_OverwritesExisting()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            File.WriteAllText(tmp, "old content");
            doc.ExportToHtmlFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.DoesNotContain("old content", content);
            Assert.Contains("<html>", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_AfterEdit_ReflectsChanges()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("R109 HTML test paragraph");
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("R109 HTML test paragraph", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToHtmlFile_HeadingsRenderedAsH()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".html";
        try
        {
            doc.ExportToHtmlFile(tmp);
            var content = File.ReadAllText(tmp);
            // If document has headings, they should be h1-h6
            if (doc.GetHeadingCount() > 0)
            {
                Assert.Matches("<h[1-6]>", content);
            }
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
