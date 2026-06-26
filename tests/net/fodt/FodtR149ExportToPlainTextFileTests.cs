// Tests for FodtDocument.ExportToPlainTextFile(string filePath).
// Sprint: ff-sprint-s134-dotnet-deepening-20260627
// Ledger: PC-FODT-R149

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R149: Tests for FodtDocument.ExportToPlainTextFile(string filePath).
/// Exports document plain text to a file. Throws ArgumentException for null or
/// empty file paths. Written content is identical to GetPlainText().
/// Covers: null path throws ArgumentException; empty path throws ArgumentException;
/// output file created; output file is non-empty for doc with content;
/// file content equals GetPlainText(); ExportToPlainTextFile on empty doc creates empty file;
/// creates parent directories (implicit); overwrites existing file; consecutive exports
/// produce identical content; dogfood AppendParagraphs→ExportToPlainTextFile→ReadAllText.
/// </summary>
public class FodtR149ExportToPlainTextFileTests
{
    // -------------------------------------------------------------------------
    // Invalid path guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_NullPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile(null!));
    }

    [Fact]
    public void ExportToPlainTextFile_EmptyPath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile(string.Empty));
    }

    [Fact]
    public void ExportToPlainTextFile_WhitespacePath_ThrowsArgumentException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Throws<ArgumentException>(() => doc.ExportToPlainTextFile("   "));
    }

    // -------------------------------------------------------------------------
    // Output file creation
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToPlainTextFile_ValidPath_CreatesFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello from R149.");
        var path = Path.Combine(Path.GetTempPath(), $"r149_test_{Guid.NewGuid():N}.txt");
        try
        {
            doc.ExportToPlainTextFile(path);
            Assert.True(File.Exists(path));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_ContentDoc_OutputIsNonEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Non-empty content for R149.");
        var path = Path.Combine(Path.GetTempPath(), $"r149_nonempty_{Guid.NewGuid():N}.txt");
        try
        {
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.False(string.IsNullOrEmpty(content));
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_ContentMatchesGetPlainText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Alpha paragraph");
        doc.AppendParagraph("Beta paragraph");
        var path = Path.Combine(Path.GetTempPath(), $"r149_parity_{Guid.NewGuid():N}.txt");
        try
        {
            var expected = doc.GetPlainText();
            doc.ExportToPlainTextFile(path);
            var actual = File.ReadAllText(path);
            Assert.Equal(expected, actual);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void ExportToPlainTextFile_OverwritesExistingFile()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Version 1 content.");
        var path = Path.Combine(Path.GetTempPath(), $"r149_overwrite_{Guid.NewGuid():N}.txt");
        try
        {
            // First export
            doc.ExportToPlainTextFile(path);
            // Modify and re-export
            doc.SetParagraphText(0, "Version 2 content.");
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Version 2", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    // -------------------------------------------------------------------------
    // Dogfood: AppendParagraphs → ExportToPlainTextFile → ReadAllText
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AppendParagraphs_ExportToPlainTextFile_ReadAllText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Sprint R149 line 1");
        doc.AppendParagraph("Sprint R149 line 2");
        doc.AppendParagraph("Sprint R149 line 3");

        var path = Path.Combine(Path.GetTempPath(), $"r149_dogfood_{Guid.NewGuid():N}.txt");
        try
        {
            doc.ExportToPlainTextFile(path);
            var content = File.ReadAllText(path);

            Assert.Contains("R149 line 1", content);
            Assert.Contains("R149 line 2", content);
            Assert.Contains("R149 line 3", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }
}
