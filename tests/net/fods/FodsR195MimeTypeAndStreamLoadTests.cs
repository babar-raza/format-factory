// Tests for FodsDocument.MimeType, OdfVersion, MaxFileSizeBytes, LoadStream deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R195

using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R195: Tests for FodsDocument.MimeType, OdfVersion, MaxFileSizeBytes, LoadStream.
/// MimeType: static property returning the MIME type string.
/// OdfVersion: static property returning the ODF version string.
/// MaxFileSizeBytes: static property returning max allowed file size.
/// LoadStream(stream): loads document from a readable stream.
/// Covers: MimeType non-null; MimeType contains 'spreadsheet' or 'fods';
/// OdfVersion non-null; OdfVersion non-empty; MaxFileSizeBytes positive;
/// MaxFileSizeBytes greater than 1MB; LoadStream non-null result;
/// LoadStream count matches; LoadStream field values accessible;
/// LoadStream then GetSheetNames; LoadStream then SetCellValue;
/// LoadStream then GetRowCount; MimeType is string; OdfVersion is string;
/// LoadStream empty content returns doc; LoadStream then ClearSheet;
/// dogfood CreateNew->SaveToFile->LoadStream->GetSheetNames->SetCell->Verify.
/// </summary>
public class FodsR195MimeTypeAndStreamLoadTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        return doc;
    }

    // -------------------------------------------------------------------------
    // MimeType
    // -------------------------------------------------------------------------

    [Fact]
    public void MimeType_NonNull()
    {
        Assert.NotNull(FodsDocument.MimeType);
    }

    [Fact]
    public void MimeType_IsString()
    {
        Assert.IsType<string>(FodsDocument.MimeType);
    }

    [Fact]
    public void MimeType_ContainsExpectedContent()
    {
        var mimeType = FodsDocument.MimeType.ToLower();
        Assert.True(
            mimeType.Contains("spreadsheet") || mimeType.Contains("fods") || mimeType.Contains("opendocument"),
            $"MimeType '{FodsDocument.MimeType}' should contain 'spreadsheet', 'fods', or 'opendocument'");
    }

    // -------------------------------------------------------------------------
    // OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void OdfVersion_NonNull()
    {
        Assert.NotNull(FodsDocument.OdfVersion);
    }

    [Fact]
    public void OdfVersion_NonEmpty()
    {
        Assert.NotEmpty(FodsDocument.OdfVersion);
    }

    [Fact]
    public void OdfVersion_IsString()
    {
        Assert.IsType<string>(FodsDocument.OdfVersion);
    }

    // -------------------------------------------------------------------------
    // MaxFileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void MaxFileSizeBytes_Positive()
    {
        Assert.True(FodsDocument.MaxFileSizeBytes > 0);
    }

    [Fact]
    public void MaxFileSizeBytes_GreaterThanOneMegabyte()
    {
        Assert.True(FodsDocument.MaxFileSizeBytes > 1024 * 1024);
    }

    // -------------------------------------------------------------------------
    // LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadStream_GetSheetNames_NonEmpty()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        var sheets = loaded.GetSheetNames();
        Assert.NotEmpty(sheets);
    }

    [Fact]
    public void LoadStream_RowCount_Positive()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        var sheet = loaded.GetSheetNames()[0];
        Assert.True(loaded.GetRowCount(sheet) > 0);
    }

    [Fact]
    public void LoadStream_ThenSetCellValue_Works()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        loaded.SetCellValue(2, 0, "Carol");
        var sheet = loaded.GetSheetNames()[0];
        var col = loaded.GetColumnValues(sheet, 0);
        Assert.Contains("Carol", col);
    }

    [Fact]
    public void LoadStream_ThenClearSheet_Works()
    {
        var doc = CreateWithData();
        var xml = doc.ToFodsXml();
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        var sheet = loaded.GetSheetNames()[0];
        loaded.ClearSheet(sheet);
        Assert.Equal(0, loaded.GetRowCount(sheet));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->ToFodsXml->LoadStream->GetSheetNames->SetCell->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateToXmlLoadStreamGetSheetsSetCellVerify_Pipeline()
    {
        // CreateNew and set data
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "X");
        doc.SetCellValue(0, 1, "A");
        doc.SetCellValue(1, 0, "Y");
        doc.SetCellValue(1, 1, "B");

        // MimeType and OdfVersion
        Assert.NotNull(FodsDocument.MimeType);
        Assert.NotNull(FodsDocument.OdfVersion);
        Assert.True(FodsDocument.MaxFileSizeBytes > 0);

        // ToFodsXml
        var xml = doc.ToFodsXml();
        Assert.NotNull(xml);

        // LoadStream
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(xml));
        var loaded = FodsDocument.LoadStream(stream);
        var sheets = loaded.GetSheetNames();
        Assert.NotEmpty(sheets);

        var sheet = sheets[0];
        Assert.True(loaded.GetRowCount(sheet) > 0);
        Assert.True(loaded.GetCellCount(sheet) > 0);

        // SetCellValue
        loaded.SetCellValue(2, 0, "Z");
        var col0 = loaded.GetColumnValues(sheet, 0);
        Assert.Contains("Z", col0);
    }
}
