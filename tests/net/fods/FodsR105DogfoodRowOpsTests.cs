// R105 Wave 4: FODS .NET dogfood — DeleteRows + InsertRow pipeline
// Ledger: R105-DOGFOOD-FODS-ROW-OPS-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR105DogfoodRowOpsTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Dogfood_InsertRowThenExportHtml()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("<table", html);
    }

    [Fact]
    public void Dogfood_DeleteRowsThenVerifyCount()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        if (before > 0)
        {
            doc.DeleteRows(sheet, 0, 1);
            Assert.Equal(before - 1, doc.GetRowCount(sheet));
        }
    }

    [Fact]
    public void Dogfood_InsertDeleteRoundtrip()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
        doc.DeleteRows(sheet, 0, 1);
        Assert.Equal(before, doc.GetRowCount(sheet));
    }

    [Fact]
    public void Dogfood_InsertMultipleThenExport()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        for (int i = 0; i < 3; i++)
            doc.InsertRow(sheet, 0);
        Assert.Equal(before + 3, doc.GetRowCount(sheet));
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("<tr", html);
    }

    [Fact]
    public void Dogfood_InsertRowThenExportContainsNewRow()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int before = doc.GetRowCount(sheet);
        doc.InsertRow(sheet, 0);
        Assert.Equal(before + 1, doc.GetRowCount(sheet));
        var html = doc.ExportSheetToHtml(sheet);
        Assert.Contains("<tr", html);
    }

    [Fact]
    public void Dogfood_DeleteAllRowsThenInsert()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.GetSheetNames()[0];
        int count = doc.GetRowCount(sheet);
        if (count > 0)
            doc.DeleteRows(sheet, 0, count);
        Assert.Equal(0, doc.GetRowCount(sheet));
        doc.InsertRow(sheet, 0);
        Assert.Equal(1, doc.GetRowCount(sheet));
    }
}
