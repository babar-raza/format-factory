// Tests for TsvReader.ReadRowsFromFile dedicated coverage.
// Sprint: ff-sprint-s145-dotnet-deepening-20260628
// Ledger: PC-TSV-R134

using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R134: Dedicated tests for TsvReader.ReadRowsFromFile.
/// ReadRowsFromFile reads rows from a TSV file at a given path.
/// Throws TsvException for null/empty/whitespace path, nonexistent file.
/// Skips empty trailing lines; splits by tab; strips BOM.
/// Covers: null path throws; empty path throws; whitespace path throws;
/// nonexistent path throws; valid file returns rows; single row split by tab;
/// empty trailing line skipped; multiple rows each correct;
/// dogfood WriteRows->ReadRowsFromFile round-trip;
/// dogfood ReadRowsFromFile->TsvDocument.LoadFile row counts match.
/// </summary>
public class TsvR134ReadRowsFromFileDedicatedTests
{
    private static string WriteTemp(string content)
    {
        var path = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ".tsv");
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        return path;
    }

    // -------------------------------------------------------------------------
    // Guard tests — invalid path
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_NullPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() => TsvReader.ReadRowsFromFile(null!));
    }

    [Fact]
    public void ReadRowsFromFile_EmptyPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() => TsvReader.ReadRowsFromFile(string.Empty));
    }

    [Fact]
    public void ReadRowsFromFile_WhitespacePath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() => TsvReader.ReadRowsFromFile("   "));
    }

    [Fact]
    public void ReadRowsFromFile_NonexistentPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvReader.ReadRowsFromFile(Path.Combine(Path.GetTempPath(), "does-not-exist-xyz.tsv")));
    }

    // -------------------------------------------------------------------------
    // Functional tests — valid file
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRowsFromFile_ValidFile_ReturnsRows()
    {
        var path = WriteTemp("Alice\t30\nBob\t25\n");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(2, rows.Count);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_SingleRow_SplitsByTab()
    {
        var path = WriteTemp("Name\tAge\tCity\n");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Single(rows);
            Assert.Equal(3, rows[0].Length);
            Assert.Equal("Name", rows[0][0]);
            Assert.Equal("Age", rows[0][1]);
            Assert.Equal("City", rows[0][2]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_EmptyTrailingLine_Skipped()
    {
        var path = WriteTemp("A\tB\n\n");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Single(rows); // empty trailing line skipped
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void ReadRowsFromFile_MultipleRows_EachRowCorrect()
    {
        var path = WriteTemp("Alice\t95\nBob\t82\nCarol\t73\n");
        try
        {
            var rows = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(3, rows.Count);
            Assert.Equal("Alice", rows[0][0]);
            Assert.Equal("82", rows[1][1]);
            Assert.Equal("Carol", rows[2][0]);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_WriteRows_ReadRowsFromFile_RoundTrip()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Alice", "Engineering", "95000" },
            new[] { "Bob", "Marketing", "72000" },
        };
        var content = TsvWriter.WriteRows(rows);
        var path = WriteTemp(content);
        try
        {
            var loaded = TsvReader.ReadRowsFromFile(path);
            Assert.Equal(2, loaded.Count);
            Assert.Equal("Alice", loaded[0][0]);
            Assert.Equal("72000", loaded[1][2]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void DogfoodPipeline_ReadRowsFromFile_ThenTsvDocumentLoadFile_RowCountsMatch()
    {
        var path = WriteTemp("Name\tScore\nAlice\t99\nBob\t88\n");
        try
        {
            var rawRows = TsvReader.ReadRowsFromFile(path);
            var doc = TsvDocument.LoadFile(path, hasHeaders: true);
            // rawRows includes header row; doc.Rows excludes it
            Assert.Equal(rawRows.Count - 1, doc.Rows.Count);
        }
        finally { File.Delete(path); }
    }
}
