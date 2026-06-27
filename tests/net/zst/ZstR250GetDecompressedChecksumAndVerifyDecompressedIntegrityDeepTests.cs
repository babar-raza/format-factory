// Tests for ZstDocument.GetDecompressedChecksum, VerifyDecompressedIntegrity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R250

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R250: Tests for ZstDocument.GetDecompressedChecksum, VerifyDecompressedIntegrity deeper.
/// GetDecompressedChecksum(): returns the checksum of the decompressed content (or 0 if not stored).
/// VerifyDecompressedIntegrity(): decompresses and verifies the content checksum matches the stored value.
/// Covers: GetDecompressedChecksum no-throw; GetDecompressedChecksum non-negative; GetDecompressedChecksum consistent;
/// GetDecompressedChecksum save-load;
/// VerifyDecompressedIntegrity no-throw; VerifyDecompressedIntegrity true for valid file;
/// VerifyDecompressedIntegrity consistent; VerifyDecompressedIntegrity save-load;
/// GetDecompressedChecksum larger-file; VerifyDecompressedIntegrity larger-file;
/// dogfood CreateDoc→GetDecompressedChecksum→VerifyDecompressedIntegrity pipeline.
/// </summary>
public class ZstR250GetDecompressedChecksumAndVerifyDecompressedIntegrityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR250GetDecompressedChecksumAndVerifyDecompressedIntegrityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR250_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleZst()
    {
        var path = TempFile("sample.zst");
        var content = System.Text.Encoding.UTF8.GetBytes(
            "col1,col2,col3\nval1,val2,val3\nval4,val5,val6\nval7,val8,val9\n");
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);
        return path;
    }

    private string CreateLargerZst()
    {
        var path = TempFile("larger.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("HEADER:INTEGRITY_TEST_DATA\n");
        for (int i = 0; i < 100; i++)
            sb.Append($"ROW:{i:D4}|hash={Guid.NewGuid().ToString("N")[..8]}|value={i * 17}\n");
        sb.Append("FOOTER:END\n");
        var compressed = ZstWriter.Compress(System.Text.Encoding.UTF8.GetBytes(sb.ToString()));
        File.WriteAllBytes(path, compressed);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetDecompressedChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDecompressedChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.GetDecompressedChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDecompressedChecksum_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.GetDecompressedChecksum() >= 0);
    }

    [Fact]
    public void GetDecompressedChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.GetDecompressedChecksum(), doc.GetDecompressedChecksum());
    }

    [Fact]
    public void GetDecompressedChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var before = doc.GetDecompressedChecksum();
        var path = TempFile("dc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDecompressedChecksum());
    }

    [Fact]
    public void GetDecompressedChecksum_LargerFile_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.Equal(doc.GetDecompressedChecksum(), doc.GetDecompressedChecksum());
    }

    // -------------------------------------------------------------------------
    // VerifyDecompressedIntegrity
    // -------------------------------------------------------------------------

    [Fact]
    public void VerifyDecompressedIntegrity_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var ex = Record.Exception(() => doc.VerifyDecompressedIntegrity());
        Assert.Null(ex);
    }

    [Fact]
    public void VerifyDecompressedIntegrity_True_ForValidFile()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.True(doc.VerifyDecompressedIntegrity());
    }

    [Fact]
    public void VerifyDecompressedIntegrity_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        Assert.Equal(doc.VerifyDecompressedIntegrity(), doc.VerifyDecompressedIntegrity());
    }

    [Fact]
    public void VerifyDecompressedIntegrity_SaveLoad_True()
    {
        var doc = ZstDocument.LoadFile(CreateSampleZst());
        var path = TempFile("vi_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.True(loaded.VerifyDecompressedIntegrity());
    }

    [Fact]
    public void VerifyDecompressedIntegrity_LargerFile_True()
    {
        var doc = ZstDocument.LoadFile(CreateLargerZst());
        Assert.True(doc.VerifyDecompressedIntegrity());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDecompressedChecksum_VerifyDecompressedIntegrity_Pipeline()
    {
        // Digital preservation — JHOVE-style digital object validation log (archival WARC content)
        var path = TempFile("preservation_validation_log.zst");
        var sb = new System.Text.StringBuilder();
        sb.Append("JHOVE_VALIDATION_LOG FORMAT=WARC VERSION=1.1 CREATED=2024-01-15T09:00:00Z\n");
        sb.Append("object_id\tformat\tversion\tvalid\twell_formed\tsize_bytes\tcreated_date\tmodified_date\tmd5\tsha256_prefix\n");

        var rng = new Random(20250401);
        string[] formats = { "PDF/A-1b", "TIFF", "JPEG2000", "PNG", "WAV", "FLAC", "ODF_1.3", "EPUB_3.2" };
        string[] versions = { "1.0", "6.0", "1.0", "1.2", "PCM", "Subset", "ODF_1.3", "3.2" };
        for (int i = 0; i < 200; i++)
        {
            int fmtIdx = rng.Next(formats.Length);
            bool valid = rng.Next(20) != 0; // 95% valid
            bool wellFormed = valid || rng.Next(3) != 0;
            long size = 1024L + rng.Next(50000000);
            string md5 = string.Format("{0:x16}{1:x16}", rng.NextInt64(), rng.NextInt64())[..32];
            string sha256 = string.Format("{0:x16}{1:x16}", rng.NextInt64(), rng.NextInt64())[..32];
            sb.Append($"OBJ-{i:D6}\t{formats[fmtIdx]}\t{versions[fmtIdx]}\t{(valid ? "true" : "false")}\t{(wellFormed ? "true" : "false")}\t{size}\t2024-01-{(rng.Next(31) + 1):D2}\t2024-02-{(rng.Next(28) + 1):D2}\t{md5}\t{sha256}\n");
        }
        sb.Append("VALIDATION_SUMMARY: TOTAL=200 VALID=190 INVALID=10 WELL_FORMED=198\n");

        var content = System.Text.Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(content);
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > doc.CompressedSize);

        // GetDecompressedChecksum
        var checksum = doc.GetDecompressedChecksum();
        Assert.True(checksum >= 0);
        Assert.Equal(checksum, doc.GetDecompressedChecksum()); // consistent

        // VerifyDecompressedIntegrity
        Assert.True(doc.VerifyDecompressedIntegrity());
        Assert.Equal(doc.VerifyDecompressedIntegrity(), doc.VerifyDecompressedIntegrity()); // consistent

        // Other frame properties
        Assert.Equal(0xFD2FB528u, (uint)doc.GetMagicNumber());
        Assert.True(doc.FrameCount >= 1);
        Assert.True(doc.GetWindowSize() > 0);
        Assert.Equal(0, doc.GetSkipFrameCount());
        Assert.True(doc.GetTotalFrameSize() >= doc.CompressedSize);

        // SearchForBytes
        var logHeader = System.Text.Encoding.ASCII.GetBytes("JHOVE_VALIDATION_LOG");
        Assert.True(doc.SearchForBytes(logHeader) >= 0);
        var pdfPattern = System.Text.Encoding.ASCII.GetBytes("PDF/A-1b");
        Assert.True(doc.SearchForBytes(pdfPattern) >= 0);
        var absentPattern = new byte[] { 0xAB, 0xCD, 0xEF, 0x01 };
        Assert.True(doc.SearchForBytes(absentPattern) < 0);

        // SaveToFile
        var outPath = TempFile("preservation_validation_log_out.zst");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(outPath);
        Assert.Equal(checksum, loaded.GetDecompressedChecksum());
        Assert.True(loaded.VerifyDecompressedIntegrity());
        Assert.Equal(doc.CompressedSize, loaded.CompressedSize);
        Assert.True(loaded.SearchForBytes(logHeader) >= 0);

        // Second save/load cycle
        var outPath2 = TempFile("preservation_validation_log_copy.zst");
        loaded.SaveToFile(outPath2);
        var loaded2 = ZstDocument.LoadFile(outPath2);
        Assert.Equal(checksum, loaded2.GetDecompressedChecksum());
        Assert.True(loaded2.VerifyDecompressedIntegrity());

        // Compression efficiency
        Assert.True(doc.CompressionRatio > 1.0);
    }
}
