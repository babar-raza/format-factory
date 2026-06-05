using FormatFactory.Fods;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R115 Train A: ExportSheetToCsvFile — CSV file export for dogfood pipeline integration.
/// </summary>
public class FodsR115ExportCsvFileTests
{
    private static FodsDocument MakeDoc()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.InsertRowWithValues("Sales", 0, new[] { "Region", "Product", "Revenue" });
        doc.InsertRowWithValues("Sales", 1, new[] { "North", "Widget", "12000" });
        doc.InsertRowWithValues("Sales", 2, new[] { "South", "Gadget", "8500" });
        doc.InsertRowWithValues("Sales", 3, new[] { "North", "Gadget", "9200" });
        return doc;
    }

    [Fact]
    public void ExportSheetToCsvFile_WritesFile()
    {
        var doc = MakeDoc();
        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r115-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile("Sales", tmp);
            Assert.True(File.Exists(tmp));
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportSheetToCsvFile_ContentMatchesExportString()
    {
        var doc = MakeDoc();
        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r115-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile("Sales", tmp);
            var written = File.ReadAllText(tmp);
            var expected = doc.ExportSheetToCsv("Sales");
            Assert.Equal(expected, written);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportSheetToCsvFile_DefaultOverload_WritesFirstSheet()
    {
        var doc = MakeDoc();
        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r115-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("Region", content);
            Assert.Contains("North", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportSheetToCsvFile_ThrowsOnNullPath()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToCsvFile("Sales", null!));
    }

    [Fact]
    public void ExportSheetToCsvFile_ThrowsOnUnknownSheet()
    {
        var doc = MakeDoc();
        Assert.Throws<InvalidOperationException>(() =>
            doc.ExportSheetToCsvFile("NoSuch", Path.GetTempFileName()));
    }

    [Fact]
    public void ExportSheetToCsvFile_ContainsHeaderAndData()
    {
        var doc = MakeDoc();
        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r115-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile("Sales", tmp);
            var lines = File.ReadAllLines(tmp);
            Assert.True(lines.Length >= 4); // header + 3 data rows
            Assert.Contains("Region", lines[0]);
            Assert.Contains("North", lines[1]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportSheetToCsvFile_DogfoodPipeline_RoundTrip()
    {
        // Dogfood: create → populate → export CSV → verify content
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.InsertRowWithValues("Report", 0, new[] { "Item", "Value" });
        doc.InsertRowWithValues("Report", 1, new[] { "Alpha", "100" });
        doc.InsertRowWithValues("Report", 2, new[] { "Beta", "200" });

        var tmp = Path.Combine(Path.GetTempPath(), $"fods-dogfood-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile("Report", tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("Item,Value", content);
            Assert.Contains("Alpha,100", content);
            Assert.Contains("Beta,200", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void ExportSheetToCsvFile_SpecialChars_ProperlyQuoted()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Q");
        doc.InsertRowWithValues("Q", 0, new[] { "Name", "Note" });
        doc.InsertRowWithValues("Q", 1, new[] { "Smith, J.", "\"quoted\"" });

        var tmp = Path.Combine(Path.GetTempPath(), $"fods-r115-csv-{Guid.NewGuid()}.csv");
        try
        {
            doc.ExportSheetToCsvFile("Q", tmp);
            var content = File.ReadAllText(tmp);
            // Comma-containing values should be quoted
            Assert.Contains("\"Smith, J.\"", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
