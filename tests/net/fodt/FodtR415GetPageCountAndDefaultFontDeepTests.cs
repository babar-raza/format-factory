using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fodt.Tests;
public class FodtR415GetPageCountAndDefaultFontDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodtR415GetPageCountAndDefaultFontDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR415GetPageCountAndDefaultFontDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFodt(string[] paragraphs, string font = "Liberation Sans")
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
      <style:text-properties fo:font-family=\"{font}\" fo:font-size=\"12pt\"/>
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
        var content = CreateFodt(new[] { "Para 1", "Para 2", "Para 3" });
        var path = TempFile("test.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(3, doc.ParagraphCount);
    }
    [Fact]
    public void GetPageCount_ValidDoc_ReturnsAtLeastOne()
    {
        var content = CreateFodt(new[] { "Page 1", "Page 2 content" });
        var path = TempFile("pages.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.True(doc.GetPageCount() >= 1);
    }
    [Fact]
    public void GetDefaultFontName_WithStyle_ReturnsFont()
    {
        var content = CreateFodt(new[] { "Test" }, "Source Sans Pro");
        var path = TempFile("font.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal("Source Sans Pro", doc.GetDefaultFontName());
    }
    [Fact]
    public void AddParagraph_ThenGetPageCount_Updates()
    {
        var doc = new FodtDocument();
        doc.AddParagraph("First");
        doc.AddParagraph("Second");
        var pages = doc.GetPageCount();
        Assert.True(pages >= 1);
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesPagesAndFont()
    {
        var content = CreateFodt(new[] { "Save", "Load" }, "Montserrat");
        var path = TempFile("roundtrip.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        var savePath = TempFile("saved.fodt");
        doc.SaveFile(savePath);
        var reloaded = FodtDocument.LoadFile(savePath);
        Assert.Equal(doc.GetPageCount(), reloaded.GetPageCount());
        Assert.Equal(doc.GetDefaultFontName(), reloaded.GetDefaultFontName());
    }
    [Fact]
    public void Dogfood_UkGovReport_PagesAndFontCorrect()
    {
        var ukParas = new[]
        {
            "UK GOVERNMENT ANNUAL REPORT 2024",
            "NHS England - Population Served: 56,000,000",
            "Budget Allocation: £150,000,000,000",
            "HMRC - Registered Taxpayers: 67,000,000",
            "Annual Revenue: £800,000,000,000",
            "DVLA - Active Licences: 48,000,000",
            "ONS - Population Estimate: 67,000,000",
            "DEFRA - Environmental Budget: £8,000,000,000"
        };
        var content = CreateFodt(ukParas, "Open Sans");
        var path = TempFile("ukgov.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(8, doc.ParagraphCount);
        Assert.Equal("Open Sans", doc.GetDefaultFontName());
        Assert.True(doc.GetPageCount() >= 1);
    }
}