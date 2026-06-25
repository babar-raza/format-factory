// Tests for CsvDocument.SaveToFile(), ToCsv() with headers, and hasHeaders=false mode.
// Sprint: FORMAT-FACTORY-CSV-DOCUMENT-R122-20260626
// Ledger: R122-GOVERNED-DOTNET-CSV-SAVETOFILE-001

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R122: CsvDocument.SaveToFile(path) writes the document to disk.
/// ToCsv() serializes to string including headers when present.
/// CsvDocument.Load(content, hasHeaders:false) treats all rows as data rows.
/// Round-trip Load → SaveToFile → LoadFile preserves row count and cell values.
/// </summary>
public class CsvR122SaveToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_csv_r122_{Guid.NewGuid():N}.csv");

    private static CsvDocument BuildDoc() =>
        CsvDocument.Load(
            "Name,City,Score\nAlice,London,95\nBob,Paris,87\n",
            hasHeaders: true);

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
    public void SaveToFile_FileContainsCommas()
    {
        var path = TempPath();
        try
        {
            BuildDoc().SaveToFile(path);
            var content = File.ReadAllText(path);
            Assert.Contains(",", content);
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
            Assert.Contains("Bob",   content);
            Assert.Contains("87",    content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- ToCsv: in-memory serialization ----

    [Fact]
    public void ToCsv_ContainsCommas()
    {
        var csv = BuildDoc().ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_ContainsHeaders()
    {
        var csv = BuildDoc().ToCsv();
        Assert.Contains("Name",  csv);
        Assert.Contains("City",  csv);
        Assert.Contains("Score", csv);
    }

    [Fact]
    public void ToCsv_ContainsAllDataValues()
    {
        var csv = BuildDoc().ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("95",    csv);
        Assert.Contains("Bob",   csv);
        Assert.Contains("87",    csv);
    }

    // ---- hasHeaders=false mode ----

    [Fact]
    public void Load_HasHeadersFalse_NoHeadersProperty()
    {
        var doc = CsvDocument.Load("Alice,London,95\nBob,Paris,87\n", hasHeaders: false);
        Assert.False(doc.HasHeaders);
        Assert.Null(doc.Headers);
    }

    [Fact]
    public void Load_HasHeadersFalse_AllRowsAreDataRows()
    {
        var doc = CsvDocument.Load("Alice,London,95\nBob,Paris,87\n", hasHeaders: false);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void Load_HasHeadersFalse_FirstRowValuesAccessible()
    {
        var doc = CsvDocument.Load("Alice,London,95\nBob,Paris,87\n", hasHeaders: false);
        Assert.Equal("Alice",  doc.Rows[0][0]);
        Assert.Equal("London", doc.Rows[0][1]);
        Assert.Equal("95",     doc.Rows[0][2]);
    }

    // ---- Round-trip: Load → SaveToFile → LoadFile ----

    [Fact]
    public void RoundTrip_SaveAndReload_RowCountPreserved()
    {
        var path = TempPath();
        try
        {
            var original = BuildDoc();
            original.SaveToFile(path);
            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
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
            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);
            Assert.Equal(original.Rows[0][0], reloaded.Rows[0][0]); // Alice
            Assert.Equal(original.Rows[1][2], reloaded.Rows[1][2]); // 87
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Dogfood: product catalog pipeline ----

    [Fact]
    public void DogfoodPipeline_ProductCatalog_FullRoundTrip()
    {
        var path = TempPath();
        try
        {
            var original = CsvDocument.Load(
                "SKU,ProductName,Category,Price\n" +
                "P001,Widget Pro,Electronics,29.99\n" +
                "P002,Gadget Mini,Accessories,9.99\n" +
                "P003,Super Cable,Electronics,4.99\n",
                hasHeaders: true);

            original.SaveToFile(path);
            var reloaded = CsvDocument.LoadFile(path, hasHeaders: true);

            // Structure
            Assert.Equal(3, reloaded.RowCount);
            Assert.Equal(4, reloaded.ColumnCount);

            // Headers
            Assert.Equal("SKU",         reloaded.Headers![0]);
            Assert.Equal("Price",        reloaded.Headers![3]);

            // Data
            Assert.Equal("Widget Pro",  reloaded.Rows[0][1]);
            Assert.Equal("Accessories", reloaded.Rows[1][2]);
            Assert.Equal("4.99",        reloaded.Rows[2][3]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
