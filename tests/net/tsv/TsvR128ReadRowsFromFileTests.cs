// Tests for TsvReader.ReadRowsFromFile(string path) path-based TSV reading.
// Sprint: FORMAT-FACTORY-TSV-R128-20260627
// Ledger: R128-GOVERNED-DOTNET-TSV-READROWS-FROM-FILE-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R128: Tests for TsvReader.ReadRowsFromFile(string path) — reads TSV rows from a file.
/// Returns a List of string[] where each element is one TSV row split on tab delimiter.
/// Null path throws TsvException. Non-existent path throws TsvException.
/// Empty file returns empty list. Single-row file returns one row.
/// Headers-line is treated as a data row (no built-in header handling).
/// Multiple rows match in-memory ReadRows(string) parity.
/// Covers: valid file returns correct row count; tab splitting correct;
/// null path throws TsvException; non-existent path throws TsvException;
/// empty file returns empty list; single-row single-column file;
/// header + data rows all returned; parity with ReadRows(string);
/// dogfood WriteRowsToFile → ReadRowsFromFile roundtrip.
/// </summary>
public class TsvR128ReadRowsFromFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"tsv_r128_{Guid.NewGuid():N}.tsv");

    private static string WriteTempFile(string content)
    {
        var path = TempPath();
        File.WriteAllText(path, content, Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // Basic row reading
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_ValidFile_ReturnsCorrectRowCount()
    {
        var path = WriteTempFile("Alice\t25\tNYC\nBob\t30\tLA\nCarol\t28\tParis");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(3, rows.Count);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_TabSplitting_ColumnsCorrect()
    {
        var path = WriteTempFile("Name\tAge\tCity\nAlice\t25\tNYC");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(2, rows.Count);
            Assert.Equal("Name",  rows[0][0]);
            Assert.Equal("Age",   rows[0][1]);
            Assert.Equal("City",  rows[0][2]);
            Assert.Equal("Alice", rows[1][0]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_SingleRow_SingleColumn()
    {
        var path = WriteTempFile("hello");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(1, rows.Count);
            Assert.Equal("hello", rows[0][0]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_EmptyFile_ReturnsEmptyList()
    {
        var path = WriteTempFile(string.Empty);
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Empty(rows);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Error guards
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_NullPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() => TsvReader.ReadRowsFromFile(null!));
    }

    [Fact]
    public void ReadRowsFromFile_NonExistentPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvReader.ReadRowsFromFile("/nonexistent/r128-tsv-test.tsv"));
    }

    // -------------------------------------------------------------------------
    // Parity with ReadRows(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_ParityWithReadRowsString()
    {
        const string content = "Product\tRegion\tRevenue\nWidget\tWest\t1000\nGadget\tEast\t800";
        var path = WriteTempFile(content);
        try
        {
            var fromFile   = TsvReader.ReadRowsFromFile(path);
            var fromString = TsvReader.ReadRows(content);

            Assert.Equal(fromString.Count, fromFile.Count);
            for (var r = 0; r < fromString.Count; r++)
            {
                Assert.Equal(fromString[r].Length, fromFile[r].Length);
                for (var c = 0; c < fromString[r].Length; c++)
                    Assert.Equal(fromString[r][c], fromFile[r][c]);
            }
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood: TsvWriter.WriteRowsToFile → TsvReader.ReadRowsFromFile roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRowsToFile_ThenReadRowsFromFile_Roundtrip()
    {
        var original = new[]
        {
            new[] { "Name",  "Score", "City"   },
            new[] { "Alice", "95",    "NYC"     },
            new[] { "Bob",   "80",    "London"  },
            new[] { "Carol", "88",    "Paris"   },
        };
        var path = TempPath();
        try
        {
            TsvWriter.WriteRowsToFile(original, path);
            var read = TsvReader.ReadRowsFromFile(path);

            Assert.Equal(original.Length, read.Count);
            for (var r = 0; r < original.Length; r++)
            {
                Assert.Equal(original[r].Length, read[r].Length);
                for (var c = 0; c < original[r].Length; c++)
                    Assert.Equal(original[r][c], read[r][c]);
            }
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
