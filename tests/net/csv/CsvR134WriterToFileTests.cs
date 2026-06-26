// Tests for CsvWriter.WriteRowsToFile and CsvWriterException.
// Sprint: ff-sprint-s138-dotnet-deepening-20260627
// Ledger: PC-CSV-R134

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R134: Tests for CsvWriter.WriteRowsToFile and CsvWriterException.
/// WriteRowsToFile serializes rows to a CSV file (UTF-8, no BOM, LF line endings).
/// Throws ArgumentNullException for null rows. Throws CsvWriterException for null/empty/whitespace path.
/// Covers: null rows throws ArgumentNullException; null path throws CsvWriterException;
/// empty path throws CsvWriterException; whitespace path throws CsvWriterException;
/// file created; file is non-empty; content matches WriteRows output;
/// round-trip via CsvDocument.LoadFile produces same row count;
/// CsvWriterException is subclass of Exception;
/// dogfood WriteRowsToFile->LoadFile->Filter verifies content.
/// </summary>
public class CsvR134WriterToFileTests
{
    private static List<IEnumerable<string?>> ThreeRows() => new()
    {
        new[] { "Name", "Score", "Active" },
        new[] { "Alice", "95", "true" },
        new[] { "Bob", "72", "false" },
        new[] { "Carol", "88", "true" }
    };

    // -------------------------------------------------------------------------
    // Null/empty guards
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_NullRows_ThrowsArgumentNullException()
    {
        var path = Path.Combine(Path.GetTempPath(), $"csv_r134_{Guid.NewGuid():N}.csv");
        Assert.Throws<ArgumentNullException>(() => CsvWriter.WriteRowsToFile(null!, path));
    }

    [Fact]
    public void WriteRowsToFile_NullPath_ThrowsCsvWriterException()
    {
        Assert.Throws<CsvWriterException>(() => CsvWriter.WriteRowsToFile(ThreeRows(), null!));
    }

    [Fact]
    public void WriteRowsToFile_EmptyPath_ThrowsCsvWriterException()
    {
        Assert.Throws<CsvWriterException>(() => CsvWriter.WriteRowsToFile(ThreeRows(), string.Empty));
    }

    [Fact]
    public void WriteRowsToFile_WhitespacePath_ThrowsCsvWriterException()
    {
        Assert.Throws<CsvWriterException>(() => CsvWriter.WriteRowsToFile(ThreeRows(), "   "));
    }

    // -------------------------------------------------------------------------
    // File creation
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_ValidPath_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"csv_r134_{Guid.NewGuid():N}.csv");
        try
        {
            CsvWriter.WriteRowsToFile(ThreeRows(), path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_ContentMatchesWriteRows()
    {
        var rows = ThreeRows();
        var path = Path.Combine(Path.GetTempPath(), $"csv_r134_{Guid.NewGuid():N}.csv");
        try
        {
            CsvWriter.WriteRowsToFile(rows, path);
            var fileContent = File.ReadAllText(path);
            var inMemory = CsvWriter.WriteRows(rows);
            Assert.Equal(inMemory.Replace("\r\n", "\n"), fileContent.Replace("\r\n", "\n"));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // CsvWriterException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvWriterException_IsSubclassOfException()
    {
        var ex = new CsvWriterException("test error");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    // -------------------------------------------------------------------------
    // Round-trip via CsvDocument.LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_RoundTrip_LoadFile_SameRowCount()
    {
        var path = Path.Combine(Path.GetTempPath(), $"csv_r134_{Guid.NewGuid():N}.csv");
        try
        {
            CsvWriter.WriteRowsToFile(ThreeRows(), path);
            var doc = CsvDocument.LoadFile(path, hasHeaders: true);
            // 4 rows total (1 header + 3 data); LoadFile with hasHeaders=true skips header
            Assert.Equal(3, doc.RowCount);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRowsToFile -> LoadFile -> Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteToFile_LoadFile_Filter_ActiveOnly()
    {
        var path = Path.Combine(Path.GetTempPath(), $"csv_r134_dog_{Guid.NewGuid():N}.csv");
        try
        {
            CsvWriter.WriteRowsToFile(ThreeRows(), path);
            var doc = CsvDocument.LoadFile(path, hasHeaders: true);

            // Filter active=true rows (Alice=95, Carol=88)
            var active = doc.Filter(r => r.Length > 2 && r[2] == "true");
            Assert.Equal(2, active.RowCount);
            Assert.Equal("Alice", active.GetCellValue(0, 0));
            Assert.Equal("Carol", active.GetCellValue(1, 0));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
