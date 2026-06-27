using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fodt.Tests;
public class FodtR412GetParagraphCountAndDefaultFontDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodtR412GetParagraphCountAndDefaultFontDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR412GetParagraphCountAndDefaultFontDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFodt(string[] paragraphs, string fontName = "Liberation Sans")
    {
        var body = new System.Text.StringBuilder();
        foreach (var p in paragraphs)
        {
            body.AppendLine($"<text:p text:style-name=\"Standard\">{p}</text:p>");
        }
        return $@"<?xml version=""1.0"" encoding=""UTF-8""?>
<office:document xmlns:office=""urn:oasis:names:tc:opendocument:xmlns:office:1.0""
                 xmlns:text=""urn:oasis:names:tc:opendocument:xmlns:text:1.0""
                 xmlns:style=""urn:oasis:names:tc:opendocument:xmlns:style:1.0""
                 xmlns:fo=""urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"">
  <office:styles>
    <style:style style:name=\"Standard\" style:family=\"paragraph\">
      <style:text-properties fo:font-name=\"{fontName}\" fo:font-size=\"12pt\"/>
    </style:style>
  </office:styles>
  <office:body>
    <office:text>
      {body}
    </office:text>
  </office:body>
</office:document>";
    }
    [Fact]
    public void LoadFile_ValidFodt_ReturnsParagraphCount()
    {
        var content = CreateFodt(new[] { "First", "Second", "Third", "Fourth" });
        var path = TempFile("test.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(4, doc.ParagraphCount);
    }
    [Fact]
    public void AddParagraph_MultipleCalls_IncrementsCount()
    {
        var doc = new FodtDocument();
        for (int i = 0; i < 5; i++)
        {
            doc.AddParagraph($"Paragraph {i}");
        }
        Assert.Equal(5, doc.ParagraphCount);
    }
    [Fact]
    public void GetPageCount_ValidFodt_ReturnsAtLeastOne()
    {
        var content = CreateFodt(new[] { "Page 1", "Page 2 content here" });
        var path = TempFile("pages.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.True(doc.GetPageCount() >= 1);
    }
    [Fact]
    public void GetDefaultFontName_WithStyles_ReturnsFont()
    {
        var content = CreateFodt(new[] { "Test" }, "Arial");
        var path = TempFile("font.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal("Arial", doc.GetDefaultFontName());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesParagraphCount()
    {
        var content = CreateFodt(new[] { "Save", "Load", "Test" });
        var path = TempFile("roundtrip.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        var savePath = TempFile("saved.fodt");
        doc.SaveFile(savePath);
        var reloaded = FodtDocument.LoadFile(savePath);
        Assert.Equal(doc.ParagraphCount, reloaded.ParagraphCount);
    }
    [Fact]
    public void Dogfood_UkGovReport_ParagraphCountAndFontCorrect()
    {
        var ukParas = new[]
        {
            "UK GOVERNMENT ANNUAL REPORT 2024",
            "NHS England - Population Served: 56,000,000",
            "Budget: £150,000,000,000",
            "HMRC - Taxpayers: 67,000,000",
            "Revenue Collected: £800,000,000,000",
            "DVLA - Licenses Issued: 48,000,000",
            "ONS - UK Population Estimate: 67,000,000"
        };
        var content = CreateFodt(ukParas, "Calibri");
        var path = TempFile("ukgov.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(7, doc.ParagraphCount);
        Assert.Equal("Calibri", doc.GetDefaultFontName());
    }
}