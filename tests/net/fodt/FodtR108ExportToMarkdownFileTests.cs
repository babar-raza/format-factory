// R108 Lane D: FODT ExportToMarkdownFile tests
// Ledger: R108-GOVERNED-DOTNET-FODT-EXPORTTOMARKDOWNFILE-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR108ExportToMarkdownFileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void ExportToMarkdownFile_CreatesFile()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_MatchesExportToMarkdown()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            var fromFile = File.ReadAllText(tmp);
            var fromMethod = doc.ExportToMarkdown();
            Assert.Equal(fromMethod, fromFile);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_AfterEdit_ContainsNewText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("R108 markdown test");
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("R108 markdown test", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_EmptyDoc_CreatesFile()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            doc.ExportToMarkdownFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_NullPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile(null!));
    }

    [Fact]
    public void ExportToMarkdownFile_EmptyPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToMarkdownFile(""));
    }

    [Fact]
    public void ExportToMarkdownFile_OverwritesExisting()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".md";
        try
        {
            File.WriteAllText(tmp, "old content");
            doc.ExportToMarkdownFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.DoesNotContain("old content", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToMarkdownFile_SaveReloadExport_Roundtrip()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("PERSIST_MD");
        var tmpFodt = Path.GetTempFileName() + ".fodt";
        var tmpMd = Path.GetTempFileName() + ".md";
        try
        {
            doc.Save(tmpFodt);
            var reloaded = FodtDocument.Load(tmpFodt);
            reloaded.ExportToMarkdownFile(tmpMd);
            var content = File.ReadAllText(tmpMd);
            Assert.Contains("PERSIST_MD", content);
        }
        finally
        {
            if (File.Exists(tmpFodt)) File.Delete(tmpFodt);
            if (File.Exists(tmpMd)) File.Delete(tmpMd);
        }
    }
}
