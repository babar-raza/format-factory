// Tests for ZstDocument.GetFrameHeaderSize, GetContentType, GetOriginalFileName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R240

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R240: Tests for ZstDocument.GetFrameHeaderSize, GetContentType, GetOriginalFileName deeper.
/// GetFrameHeaderSize(): returns the size in bytes of the Zstandard frame header.
/// GetContentType(): returns a string description of the detected content type of the compressed data.
/// GetOriginalFileName(): returns the original file name stored in the frame metadata, if any.
/// Covers: GetFrameHeaderSize no-throw; GetFrameHeaderSize positive; GetFrameHeaderSize consistent;
/// GetFrameHeaderSize save-load; GetFrameHeaderSize leq CompressedSize;
/// GetContentType no-throw; GetContentType non-null; GetContentType consistent;
/// GetContentType save-load;
/// GetOriginalFileName no-throw; GetOriginalFileName consistent;
/// dogfood Compress→GetFrameHeaderSize→GetContentType→GetOriginalFileName→SaveToFile pipeline.
/// </summary>
public class ZstR240GetFrameHeaderSizeAndContentTypeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR240GetFrameHeaderSizeAndContentTypeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR240_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTextZst()
    {
        var content = "HEADER_SIZE_TEST\n" + string.Join("\n", Enumerable.Repeat(
            "content_type_test_alpha_beta_gamma_delta_epsilon_zeta_eta_theta", 80));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("text.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFrameHeaderSize
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameHeaderSize_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var ex = Record.Exception(() => doc.GetFrameHeaderSize());
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameHeaderSize_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.True(doc.GetFrameHeaderSize() > 0);
    }

    [Fact]
    public void GetFrameHeaderSize_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.Equal(doc.GetFrameHeaderSize(), doc.GetFrameHeaderSize());
    }

    [Fact]
    public void GetFrameHeaderSize_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var before = doc.GetFrameHeaderSize();
        var path = TempFile("fhs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameHeaderSize());
    }

    [Fact]
    public void GetFrameHeaderSize_LeqCompressedSize()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.True(doc.GetFrameHeaderSize() <= doc.CompressedSize);
    }

    // -------------------------------------------------------------------------
    // GetContentType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentType_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var ex = Record.Exception(() => doc.GetContentType());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentType_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.NotNull(doc.GetContentType());
    }

    [Fact]
    public void GetContentType_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.Equal(doc.GetContentType(), doc.GetContentType());
    }

    [Fact]
    public void GetContentType_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var before = doc.GetContentType();
        var path = TempFile("ct_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentType());
    }

    // -------------------------------------------------------------------------
    // GetOriginalFileName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOriginalFileName_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        var ex = Record.Exception(() => doc.GetOriginalFileName());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOriginalFileName_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateTextZst());
        Assert.Equal(doc.GetOriginalFileName(), doc.GetOriginalFileName());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFrameHeaderSize_GetContentType_GetOriginalFileName_SaveToFile_Pipeline()
    {
        // Supply chain analytics — compressed logistics event stream (EDI 856 ASN data)
        var sb = new StringBuilder();
        sb.AppendLine("isa_id,po_number,asn_date,ship_date,carrier,tracking_number,origin_dc,dest_dc,sku_count,total_units,total_weight_kg,freight_terms");
        string[] carriers = { "DHL", "FedEx", "UPS", "TNT", "DSV" };
        string[] terms = { "CPT", "DAP", "DDP", "EXW", "FCA" };
        string[] dcs = { "DC-LHR", "DC-AMS", "DC-CDG", "DC-DUS", "DC-MXP" };
        var rng = new Random(20241001);
        for (int i = 0; i < 350; i++)
        {
            string carrier = carriers[i % 5];
            string origin = dcs[rng.Next(0, 5)];
            string dest = dcs[rng.Next(0, 5)];
            int skus = rng.Next(1, 25);
            int units = rng.Next(50, 2000);
            double weight = units * (0.2 + rng.NextDouble() * 2.0);
            sb.AppendLine($"ISA{i:D9},PO{i + 100000:D7},2024-10-{(i % 28 + 1):D2},2024-10-{((i + 2) % 28 + 1):D2},{carrier},{carrier[0]}TR{i:D10},{origin},{dest},{skus},{units},{weight:F1},{terms[i % 5]}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_edi856.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetFrameHeaderSize
        var headerSize = doc.GetFrameHeaderSize();
        Assert.True(headerSize > 0);
        Assert.True(headerSize <= doc.CompressedSize);
        Assert.Equal(headerSize, doc.GetFrameHeaderSize()); // consistent

        // GetContentType
        var contentType = doc.GetContentType();
        Assert.NotNull(contentType);
        Assert.Equal(contentType, doc.GetContentType()); // consistent

        // GetOriginalFileName
        var origName = doc.GetOriginalFileName();
        Assert.Equal(origName, doc.GetOriginalFileName()); // consistent

        // GetMagicNumber cross-check
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());

        // SaveToFile
        var out1 = TempFile("dogfood_edi856_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(headerSize, loaded.GetFrameHeaderSize());
        Assert.Equal(contentType, loaded.GetContentType());
        Assert.Equal(origName, loaded.GetOriginalFileName());

        // Round-trip decompression
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("DHL", text);
        Assert.Contains("FedEx", text);
        Assert.Contains("DC-LHR", text);

        // Recompress
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_edi856_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetFrameHeaderSize() > 0);
        Assert.NotNull(loaded2.GetContentType());
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
        var ex1 = Record.Exception(() => loaded2.ValidateChecksum());
        Assert.Null(ex1);
    }
}
