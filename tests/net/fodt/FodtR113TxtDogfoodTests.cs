using Xunit;
using System;
using System.IO;
using FormatFactory.Fodt;

namespace FormatFactory.Fodt.Tests;

public class FodtR113TxtDogfoodTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));
    private static string SamplePath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void PlainText_AfterAppend_ContainsText()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("DogfoodPlain");
        var txt = doc.GetPlainText();
        Assert.Contains("DogfoodPlain", txt);
    }

    [Fact]
    public void Markdown_AfterInsertHeading_ContainsMarker()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.InsertHeading(0, "DogfoodH1", 1);
        var md = doc.ExportToMarkdown();
        Assert.Contains("# DogfoodH1", md);
    }

    [Fact]
    public void Html_AfterAppend_ContainsParagraph()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("DogfoodHtml");
        var html = doc.ExportToHtml();
        Assert.Contains("DogfoodHtml", html);
    }

    [Fact]
    public void TxtFile_SaveReload_StillExports()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("SaveReloadTxt");
        var fodtTmp = Path.GetTempFileName() + ".fodt";
        var txtTmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.Save(fodtTmp);
            var reloaded = FodtDocument.Load(fodtTmp);
            reloaded.ExportToPlainTextFile(txtTmp);
            var text = File.ReadAllText(txtTmp);
            Assert.Contains("SaveReloadTxt", text);
        }
        finally
        {
            if (File.Exists(fodtTmp)) File.Delete(fodtTmp);
            if (File.Exists(txtTmp)) File.Delete(txtTmp);
        }
    }

    [Fact]
    public void Metadata_AfterEdit_StillAvailable()
    {
        var doc = FodtDocument.Load(SamplePath);
        doc.AppendParagraph("MetaCheck");
        var meta = doc.GetDocumentMetadata();
        Assert.NotNull(meta);
    }

    [Fact]
    public void WordCount_AfterAppend_Increases()
    {
        var doc = FodtDocument.Load(SamplePath);
        int before = doc.GetWordCount();
        doc.AppendParagraph("three new words");
        int after = doc.GetWordCount();
        Assert.True(after > before);
    }
}
