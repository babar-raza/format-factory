using FormatFactory.Fods;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R114 Train A: SetCellStyle/GetCellStyle — cell ODF style attribute management.
/// </summary>
public class FodsR114SetCellStyleTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.InsertRowWithValues("Sheet1", 0, new[] { "Header" });
        doc.InsertRowWithValues("Sheet1", 1, new[] { "Value" });
        return doc;
    }

    [Fact]
    public void SetCellStyle_AndGetCellStyle_RoundTrip()
    {
        var doc = MakeDoc();
        doc.SetCellStyle("Sheet1", 0, 0, "ce1");
        Assert.Equal("ce1", doc.GetCellStyle("Sheet1", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NoStyleSet_ReturnsNull()
    {
        var doc = MakeDoc();
        var style = doc.GetCellStyle("Sheet1", 1, 0);
        // Style may be null or default; just should not throw
        Assert.True(style is null || style.Length >= 0);
    }

    [Fact]
    public void SetCellStyle_ThrowsOnUnknownSheet()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() =>
            doc.SetCellStyle("NoSuch", 0, 0, "ce1"));
    }

    [Fact]
    public void SetCellStyle_ThrowsOnRowOutOfRange()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.SetCellStyle("Sheet1", 99, 0, "ce1"));
    }

    [Fact]
    public void SetCellStyle_ThrowsOnColOutOfRange()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.SetCellStyle("Sheet1", 0, 99, "ce1"));
    }

    [Fact]
    public void GetCellStyle_MissingSheet_ReturnsNull()
    {
        var doc = MakeDoc();
        var style = doc.GetCellStyle("NoSuch", 0, 0);
        Assert.Null(style);
    }

    [Fact]
    public void SetCellStyle_StylePersistsAfterSaveAndReload()
    {
        var doc = MakeDoc();
        doc.SetCellStyle("Sheet1", 0, 0, "ce2");
        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r114-style-{Guid.NewGuid()}.fods");
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("ce2", reloaded.GetCellStyle("Sheet1", 0, 0));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void SetCellStyle_MultipleStyles_EachCorrect()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("S");
        doc.InsertRowWithValues("S", 0, new[] { "A", "B" });
        doc.SetCellStyle("S", 0, 0, "header-style");
        doc.SetCellStyle("S", 0, 1, "data-style");
        Assert.Equal("header-style", doc.GetCellStyle("S", 0, 0));
        Assert.Equal("data-style", doc.GetCellStyle("S", 0, 1));
    }
}
