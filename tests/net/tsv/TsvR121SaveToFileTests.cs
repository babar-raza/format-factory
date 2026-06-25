// Tests for TsvDocument.SaveToFile() and ToTsv() round-trip with headers.
// Sprint: FORMAT-FACTORY-TSV-DOCUMENT-R121-20260626
// Ledger: R121-GOVERNED-DOTNET-TSV-SAVETOFILE-001

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R121: TsvDocument.SaveToFile(path) writes the document to disk.
/// ToTsv() serializes to a string. Round-trip Load → SaveToFile → LoadFile
/// preserves all data. HasHeaders controls whether headers are included
/// in SaveToFile and ToTsv output.
/// </summary>
public class TsvR121SaveToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_tsv_r121_{Guid.NewGuid():N}.tsv");

    private static TsvDocument BuildDoc()
    {
        var content = "Name\tCity\tScore\nAlice\tLondon\t95\nBob\tParis\t87\n";
        return TsvDocument.Load(content, hasHeaders: true);
    }

    // ---- SaveToFile: file creation ----

    [Fact]
    public void SaveToFile_ValidPath_CreatesFile()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsTabSeparators()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("\t", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsHeaderRow()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Name", content);
            Assert.Contains("City", content);
            Assert.Contains("Score", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void SaveToFile_FileContainsDataRows()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice", content);
            Assert.Contains("London", content);
            Assert.Contains("Bob", content);
            Assert.Contains("Paris", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- ToTsv: in-memory serialization ----

    [Fact]
    public void ToTsv_ContainsTabs()
    {
        var tsv = BuildDoc().ToTsv();
        Assert.Contains("\t", tsv);
    }

    [Fact]
    public void ToTsv_ContainsHeadersWhenHasHeaders()
    {
        var tsv = BuildDoc().ToTsv();
        Assert.Contains("Name", tsv);
        Assert.Contains("City", tsv);
    }

    [Fact]
    public void ToTsv_ContainsAllDataValues()
    {
        var tsv = BuildDoc().ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("95",    tsv);
        Assert.Contains("Bob",   tsv);
        Assert.Contains("87",    tsv);
    }

    // ---- Round-trip: Load → SaveToFile → LoadFile ----

    [Fact]
    public void RoundTrip_SaveAndReload_HeadersPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(original.Headers!, reloaded.Headers!);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void RoundTrip_SaveAndReload_RowCountPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(original.RowCount, reloaded.RowCount);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void RoundTrip_SaveAndReload_CellValuesPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(original.Rows[0][0], reloaded.Rows[0][0]); // Alice
            Assert.Equal(original.Rows[1][2], reloaded.Rows[1][2]); // 87
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Dogfood: employee roster pipeline ----

    [Fact]
    public void DogfoodPipeline_EmployeeRoster_FullRoundTrip()
    {
        var path = TempPath();
        try
        {
            var content = "EmployeeId\tName\tDepartment\tSalary\n" +
                          "E001\tAlice Johnson\tEngineering\t95000\n" +
                          "E002\tBob Smith\tMarketing\t72000\n" +
                          "E003\tCarol Lee\tFinance\t88000\n";

            var doc = TsvDocument.Load(content, hasHeaders: true);
            doc.SaveToFile(path);
            var reloaded = TsvDocument.LoadFile(path, hasHeaders: true);

            // Structure
            Assert.Equal(3, reloaded.RowCount);
            Assert.Equal(4, reloaded.ColumnCount);

            // Headers
            Assert.Equal("EmployeeId",  reloaded.Headers![0]);
            Assert.Equal("Salary",      reloaded.Headers![3]);

            // Data
            Assert.Equal("Alice Johnson", reloaded.Rows[0][1]);
            Assert.Equal("Finance",       reloaded.Rows[2][2]);
            Assert.Equal("88000",         reloaded.Rows[2][3]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
