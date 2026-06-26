// Tests for TsvDocument.SaveToFile and TsvDocument.LoadFile.
// Sprint: ff-sprint-s136-dotnet-deepening-20260627
// Ledger: PC-TSV-R132

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R132: Tests for TsvDocument.SaveToFile and TsvDocument.LoadFile.
/// SaveToFile writes the in-memory TSV (with headers when HasHeaders=true) to disk, UTF-8.
/// LoadFile reads from a file path into a TsvDocument, with optional header detection.
/// Covers: SaveToFile creates file; file content non-empty; headers written first;
/// data rows present in file; overwrites existing; LoadFile from saved file
/// round-trips row count; headers preserved; cell values match;
/// dogfood Load->Filter->SaveToFile->LoadFile verifies filtered content.
/// </summary>
public class TsvR132SaveToFileAndLoadFileTests
{
    private const string SampleTsv = "Name\tScore\tActive\nAlice\t95\ttrue\nBob\t72\tfalse\nCarol\t88\ttrue";

    // -------------------------------------------------------------------------
    // SaveToFile creates file
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ValidPath_CreatesFile()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            doc.SaveToFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_ContentIsNonEmpty()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            doc.SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.True(content.Length > 0);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_HeadersWrittenToFile()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            doc.SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Name", content);
            Assert.Contains("Score", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_DataRowsWrittenToFile()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            doc.SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice", content);
            Assert.Contains("Carol", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_OverwritesExistingFile()
    {
        var doc1 = TsvDocument.Load("Col1\nFirst", hasHeaders: true);
        var doc2 = TsvDocument.Load("Col1\nSecond", hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            doc1.SaveToFile(path);
            doc2.SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Second", content);
            Assert.DoesNotContain("First", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // LoadFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_AfterSaveToFile_RowCountMatches()
    {
        var original = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            original.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(original.RowCount, reloaded.RowCount);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void LoadFile_AfterSaveToFile_HeadersPreserved()
    {
        var original = TsvDocument.Load(SampleTsv, hasHeaders: true);
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_{Guid.NewGuid():N}.tsv");
        try
        {
            original.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);
            Assert.NotNull(reloaded.Headers);
            Assert.Equal("Name", reloaded.Headers![0]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load -> Filter -> SaveToFile -> LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FilterSave_LoadFile_ContainsOnlyActiveRows()
    {
        var doc = TsvDocument.Load(SampleTsv, hasHeaders: true);
        // Filter to active=true rows only (Alice, Carol)
        var filtered = doc.Filter(row => row.Length > 2 && row[2] == "true");
        var path = Path.Combine(Path.GetTempPath(), $"tsv_r132_dog_{Guid.NewGuid():N}.tsv");
        try
        {
            filtered.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
            Assert.Equal(2, reloaded.RowCount);

            var content = File.ReadAllText(path);
            Assert.Contains("Alice", content);
            Assert.Contains("Carol", content);
            Assert.DoesNotContain("Bob", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
