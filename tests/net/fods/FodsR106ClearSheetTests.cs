// R106 Wave 2: FODS ClearSheet tests
// Ledger: R106-GOVERNED-DOTNET-FODS-CLEARSHEET-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR106ClearSheetTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void ClearSheet_RemovesAllRows()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        Assert.True(doc.GetRowCount(sheet) > 0);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
    }

    [Fact]
    public void ClearSheet_EmptySheet_NoOp()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Empty");
        doc.ClearSheet("Empty");
        Assert.Equal(0, doc.GetRowCount("Empty"));
    }

    [Fact]
    public void ClearSheet_Nonexistent_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() => doc.ClearSheet("NoSuchSheet"));
    }

    [Fact]
    public void ClearSheet_NullName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ClearSheet(null!));
    }

    [Fact]
    public void ClearSheet_ThenInsertRow_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
        doc.InsertRow(sheet, 0);
        Assert.Equal(1, doc.GetRowCount(sheet));
    }

    [Fact]
    public void ClearSheet_PreservesOtherSheets()
    {
        var doc = FodsDocument.Load(MinimalPath);
        doc.AddSheet("Keep");
        doc.InsertRow("Keep", 0);
        var first = doc.GetSheetNames()[0];
        doc.ClearSheet(first);
        Assert.Equal(0, doc.GetRowCount(first));
        Assert.Equal(1, doc.GetRowCount("Keep"));
    }

    [Fact]
    public void ClearSheet_ThenExportHtml_EmptyTable()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("<table", html);
        Assert.DoesNotContain("<td", html);
    }

    [Fact]
    public void ClearSheet_ClearTwice_NoError()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        doc.ClearSheet(sheet);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
    }
}
