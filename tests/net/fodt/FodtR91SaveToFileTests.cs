// R91 Train H: FODT .NET SaveToFile Round-Trip Tests
// New API: SaveToFile(path) — explicit named alias for Save(path)
// Sprint: FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fodt;
using Xunit;

namespace FormatFactory.Fodt.Tests;

public class FodtR91SaveToFileTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fodt"));

    private static string SampleFodtPath =>
        Path.Combine(SamplesDir, "minimal-document.fodt");

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            Assert.True(new FileInfo(tmp).Length > 0);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_ReloadedDocumentIsValid()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.NotNull(reloaded);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_AfterEdit_ReloadReflectsChange()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var original = doc.GetPlainText();
        if (!string.IsNullOrWhiteSpace(original))
        {
            var firstWord = original.Split([' ', '\n'], StringSplitOptions.RemoveEmptyEntries)[0];
            doc.ReplaceText(firstWord, "R91-EDIT");
        }

        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(doc.ParagraphCount, reloaded.ParagraphCount);
            if (!string.IsNullOrWhiteSpace(original))
                Assert.Contains("R91-EDIT", reloaded.GetPlainText());
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_IsEquivalentToSave()
    {
        var doc1 = FodtDocument.Load(SampleFodtPath);
        var doc2 = FodtDocument.Load(SampleFodtPath);
        var tmp1 = Path.GetTempFileName() + ".fodt";
        var tmp2 = Path.GetTempFileName() + ".fodt";
        try
        {
            doc1.Save(tmp1);
            doc2.SaveToFile(tmp2);
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

    [Fact]
    public void SaveToFile_OverwritesExistingFile()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            File.WriteAllText(tmp, "old-content");
            doc.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.DoesNotContain("old-content", content);
            Assert.Contains("<?xml", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_RoundTrip_ParagraphCountPreserved()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var originalCount = doc.ParagraphCount;
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(originalCount, reloaded.ParagraphCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_TxtExport_WorksAfterReload()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var tmp = Path.GetTempFileName() + ".fodt";
        var txtOut = Path.GetTempFileName() + ".txt";
        try
        {
            doc.SaveToFile(tmp);
            var result = FodtTxtExporter.ExportTxt(tmp, txtOut);
            Assert.True(result.ParagraphsExported >= 0);
            Assert.True(File.Exists(txtOut));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
            if (File.Exists(txtOut)) File.Delete(txtOut);
        }
    }

    [Fact]
    public void SaveToFile_CharCount_PreservedAfterRoundTrip()
    {
        var doc = FodtDocument.Load(SampleFodtPath);
        var originalCharCount = doc.CharCount;
        var tmp = Path.GetTempFileName() + ".fodt";
        try
        {
            doc.SaveToFile(tmp);
            var reloaded = FodtDocument.Load(tmp);
            Assert.Equal(originalCharCount, reloaded.CharCount);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
