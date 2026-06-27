// Tests for FodsDocument.ExportToXml dedicated coverage.
// Sprint: ff-sprint-s298-dotnet-deepening-20260630
// Ledger: PC-FODS-R326

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R326: Dedicated tests for FodsDocument.ExportToXml(filePath).
/// Null path throws exception.
/// Whitespace path throws exception.
/// Valid call no exception.
/// Output file exists after export.
/// Output file is non-empty.
/// SheetCount unchanged after ExportToXml.
/// Export twice no exception.
/// Dogfood: document with data exports to xml.
/// Dogfood: export two different paths no exception.
/// </summary>
public class FodsR326ExportToXmlDedicatedTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string GetTempPath()
    {
        var path = Path.Combine(Path.GetTempPath(), $"fods_r326_{Guid.NewGuid():N}.xml");
        _tempFiles.Add(path);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            if (File.Exists(f)) File.Delete(f);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NullPath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToXml(null!));
    }

    [Fact]
    public void ExportToXml_WhitespacePath_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.ExportToXml("   "));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_ValidCall_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToXml(path));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportToXml_OutputFileExists()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        doc.ExportToXml(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExportToXml_OutputFileNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path = GetTempPath();
        doc.ExportToXml(path);
        var info = new FileInfo(path);
        Assert.True(info.Length > 0);
    }

    [Fact]
    public void ExportToXml_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        string path = GetTempPath();
        doc.ExportToXml(path);
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void ExportToXml_ExportTwice_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToXml(path1);
        var ex = Record.Exception(() => doc.ExportToXml(path2));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DocumentWithData_ExportsToXml()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "95");
        string path = GetTempPath();
        var ex = Record.Exception(() => doc.ExportToXml(path));
        Assert.Null(ex);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void DogfoodPipeline_ExportTwoDifferentPaths_NoException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Export");
        doc.SetCellValue("Export", 0, 0, "Value");
        string path1 = GetTempPath();
        string path2 = GetTempPath();
        doc.ExportToXml(path1);
        var ex = Record.Exception(() => doc.ExportToXml(path2));
        Assert.Null(ex);
        Assert.True(File.Exists(path1));
        Assert.True(File.Exists(path2));
    }
}
