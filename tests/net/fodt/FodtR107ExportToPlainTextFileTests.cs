// R107 Wave 2: FODT ExportToPlainTextFile tests
// Ledger: R107-FODT-EXPORTTOPLAINTEXTFILE

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR107ExportToPlainTextFileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void ExportToPlainTextFile_CreatesFile()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_ContentMatchesGetPlainText()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Equal(doc.GetPlainText(), content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_EmptyDoc_CreatesEmptyFile()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Equal("", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_Overwrite_Succeeds()
    {
        var doc = FodtDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            File.WriteAllText(tmp, "old content");
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.DoesNotContain("old content", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_NullPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile(null!));
    }

    [Fact]
    public void ExportToPlainTextFile_EmptyPath_Throws()
    {
        var doc = FodtDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile(""));
    }

    [Fact]
    public void ExportToPlainTextFile_AfterEdit_ReflectsChanges()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.AppendParagraph("UNIQUE_MARKER_R107");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("UNIQUE_MARKER_R107", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportToPlainTextFile_RoundtripParagraphs()
    {
        var doc = FodtDocument.Load(MinimalPath);
        doc.RemoveAllParagraphs();
        doc.AppendParagraph("Line1");
        doc.AppendParagraph("Line2");
        doc.AppendParagraph("Line3");
        var tmp = Path.GetTempFileName() + ".txt";
        try
        {
            doc.ExportToPlainTextFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Equal("Line1\nLine2\nLine3", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
