using System;
using System.IO;
using Xunit;
namespace FormatFactory.Fodt.Tests;
public class FodtR411GetParagraphCountAndPageCountDeepTests : IDisposable
{
    private readonly string _tempDir;
    public FodtR411GetParagraphCountAndPageCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR411GetParagraphCountAndPageCountDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreateFodtContent(string[] paragraphs)
    {
        var body = new System.Text.StringBuilder();
        foreach (var p in paragraphs)
        {
            body.AppendLine($"<text:p>{p}</text:p>");
        }
        return $@"<?xml version=""1.0"" encoding=""UTF-8""?>
<office:document xmlns:office=""urn:oasis:names:tc:opendocument:xmlns:office:1.0""
                 xmlns:text=""urn:oasis:names:tc:opendocument:xmlns:text:1.0""
                 xmlns:style=""urn:oasis:names:tc:opendocument:xmlns:style:1.0"">
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
        var content = CreateFodtContent(new[] { "Para 1", "Para 2", "Para 3" });
        var path = TempFile("test.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(3, doc.ParagraphCount);
    }
    [Fact]
    public void AddParagraph_ThenGetCount_Increments()
    {
        var doc = new FodtDocument();
        doc.AddParagraph("First");
        doc.AddParagraph("Second");
        Assert.Equal(2, doc.ParagraphCount);
    }
    [Fact]
    public void GetPageCount_ValidFodt_ReturnsPageCount()
    {
        var content = CreateFodtContent(new[] { "Page 1 content", "Page 2 content" });
        var path = TempFile("pages.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        var pages = doc.GetPageCount();
        Assert.True(pages >= 1);
    }
    [Fact]
    public void GetDefaultFontName_ValidFodt_ReturnsFont()
    {
        var content = CreateFodtContent(new[] { "Test" });
        var path = TempFile("font.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.NotNull(doc.GetDefaultFontName());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesParagraphs()
    {
        var content = CreateFodtContent(new[] { "Round", "Trip" });
        var path = TempFile("roundtrip.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        var savePath = TempFile("saved.fodt");
        doc.SaveFile(savePath);
        var reloaded = FodtDocument.LoadFile(savePath);
        Assert.Equal(doc.ParagraphCount, reloaded.ParagraphCount);
    }
    [Fact]
    public void Dogfood_UkGovDocument_ParagraphPageCountCorrect()
    {
        var ukParas = new[]
        {
            "NHS England Annual Report 2024",
            "Population served: 56,000,000",
            "Budget allocated: £150,000,000,000",
            "HMRC Tax Collection Summary",
            "Taxpayers: 67,000,000",
            "Revenue collected: £80,000,000,000"
        };
        var content = CreateFodtContent(ukParas);
        var path = TempFile("ukgov.fodt");
        File.WriteAllText(path, content);
        var doc = FodtDocument.LoadFile(path);
        Assert.Equal(6, doc.ParagraphCount);
        Assert.True(doc.GetPageCount() >= 1);
    }
}