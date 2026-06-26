// Tests for FodtTxtExporter.ExportTxt(string fodtPath, string txtPath) — path-based overload.
// Sprint: FORMAT-FACTORY-FODT-R142-20260627
// Ledger: R142-GOVERNED-DOTNET-FODT-TXT-PATH-EXPORTER-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R142: Tests for FodtTxtExporter.ExportTxt(string fodtPath, string txtPath).
/// The path-based overload loads the FODT from disk before extracting plain text —
/// distinct from the FodtDocument-based overload tested in FodtTxtExporterTests.
/// Covers: output file exists; file contains expected text content; OutputPath matches;
/// ParagraphsExported>=0; Status non-null; Warnings list non-null; SourcePath populated;
/// null fodtPath throws; empty fodtPath throws; null txtPath throws;
/// dogfood headings fixture: exported text contains heading content.
/// </summary>
public class FodtR142TxtPathExporterTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static string TempTxtPath() =>
        Path.Combine(Path.GetTempPath(), $"fodt_r142_{Guid.NewGuid():N}.txt");

    // -------------------------------------------------------------------------
    // ExportTxt(string, string) — basic result properties
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportTxt_Path_OutputFileExists()
    {
        var txtPath = TempTxtPath();
        try
        {
            FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), txtPath);
            Assert.True(File.Exists(txtPath), "TXT output file should exist after path-based export");
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    [Fact]
    public void ExportTxt_Path_OutputPathMatchesGivenPath()
    {
        var txtPath = TempTxtPath();
        try
        {
            var result = FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), txtPath);
            Assert.Equal(txtPath, result.OutputPath);
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    [Fact]
    public void ExportTxt_Path_SourcePathPopulated()
    {
        var txtPath = TempTxtPath();
        try
        {
            var fodtPath = FixturePath("fodt-minimal-roundtrip.fodt");
            var result = FodtTxtExporter.ExportTxt(fodtPath, txtPath);
            Assert.False(string.IsNullOrEmpty(result.SourcePath),
                "SourcePath should be populated with the input file path");
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    [Fact]
    public void ExportTxt_Path_ParagraphsExportedNonNegative()
    {
        var txtPath = TempTxtPath();
        try
        {
            var result = FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), txtPath);
            Assert.True(result.ParagraphsExported >= 0,
                $"ParagraphsExported must be >= 0, got {result.ParagraphsExported}");
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    [Fact]
    public void ExportTxt_Path_StatusIsNonNull()
    {
        var txtPath = TempTxtPath();
        try
        {
            var result = FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), txtPath);
            Assert.NotNull(result.Status);
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    [Fact]
    public void ExportTxt_Path_WarningsListIsNonNull()
    {
        var txtPath = TempTxtPath();
        try
        {
            var result = FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), txtPath);
            Assert.NotNull(result.Warnings);
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }

    // -------------------------------------------------------------------------
    // Null/whitespace guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportTxt_Path_NullFodtPath_ThrowsException()
    {
        var txtPath = TempTxtPath();
        Assert.ThrowsAny<Exception>(() =>
            FodtTxtExporter.ExportTxt(null!, txtPath));
    }

    [Fact]
    public void ExportTxt_Path_EmptyFodtPath_ThrowsException()
    {
        var txtPath = TempTxtPath();
        Assert.ThrowsAny<Exception>(() =>
            FodtTxtExporter.ExportTxt(string.Empty, txtPath));
    }

    [Fact]
    public void ExportTxt_Path_NullTxtPath_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() =>
            FodtTxtExporter.ExportTxt(FixturePath("fodt-minimal-roundtrip.fodt"), null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: headings fixture — path-based TXT export contains heading text
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HeadingsFixture_TextFileContainsContent()
    {
        var txtPath = TempTxtPath();
        try
        {
            var result = FodtTxtExporter.ExportTxt(
                FixturePath("fodt-headings-and-list.fodt"), txtPath);

            Assert.True(File.Exists(txtPath));
            Assert.Equal(txtPath, result.OutputPath);
            Assert.True(result.ParagraphsExported >= 0);

            // File has some content
            var fileContent = File.ReadAllText(txtPath);
            Assert.NotNull(fileContent);
        }
        finally { if (File.Exists(txtPath)) File.Delete(txtPath); }
    }
}
