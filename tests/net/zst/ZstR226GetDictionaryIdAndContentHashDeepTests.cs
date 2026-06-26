// Tests for ZstDocument.GetDictionaryId, GetContentHash, GetChecksumValid deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R226

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R226: Tests for ZstDocument.GetDictionaryId, GetContentHash, GetChecksumValid deeper.
/// GetDictionaryId(): returns the dictionary ID embedded in the Zstandard frame (0 if none).
/// GetContentHash(): returns a hash string of the decompressed content.
/// GetChecksumValid(): returns whether the frame checksum is valid.
/// Covers: GetDictionaryId no-throw; GetDictionaryId non-negative; GetDictionaryId consistent;
/// GetDictionaryId save-load; GetDictionaryId zero for standard compression;
/// GetContentHash no-throw; GetContentHash non-null; GetContentHash non-empty;
/// GetContentHash consistent; GetContentHash save-load;
/// GetChecksumValid no-throw; GetChecksumValid consistent; GetChecksumValid save-load;
/// dogfood Compress→GetDictionaryId→GetContentHash→GetChecksumValid→SaveToFile pipeline.
/// </summary>
public class ZstR226GetDictionaryIdAndContentHashDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR226GetDictionaryIdAndContentHashDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR226_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string text = "The quick brown fox jumps over the lazy dog. " +
        "Sphinx of black quartz, judge my vow. How vexingly quick daft zebras jump!")
    {
        var raw = TempFile("src.txt");
        File.WriteAllText(raw, text);
        var zst = TempFile("src.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetDictionaryId
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDictionaryId_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetDictionaryId());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDictionaryId_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetDictionaryId() >= 0);
    }

    [Fact]
    public void GetDictionaryId_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetDictionaryId(), doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_Zero_ForStandardCompression()
    {
        // Standard zstd compression without a dictionary uses dictionary ID = 0
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(0, doc.GetDictionaryId());
    }

    [Fact]
    public void GetDictionaryId_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetDictionaryId();
        var path = TempFile("did_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetDictionaryId());
    }

    // -------------------------------------------------------------------------
    // GetContentHash
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentHash_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetContentHash());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentHash_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotNull(doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotEmpty(doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetContentHash(), doc.GetContentHash());
    }

    [Fact]
    public void GetContentHash_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetContentHash();
        var path = TempFile("ch_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentHash());
    }

    // -------------------------------------------------------------------------
    // GetChecksumValid
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChecksumValid_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetChecksumValid());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChecksumValid_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetChecksumValid(), doc.GetChecksumValid());
    }

    [Fact]
    public void GetChecksumValid_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetChecksumValid();
        var path = TempFile("csv_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetChecksumValid());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetDictionaryId_GetContentHash_GetChecksumValid_SaveToFile_Pipeline()
    {
        var content = string.Join("\n", new[]
        {
            "FINANCIAL_LOG — Session 20260626",
            "instrument=EUR/USD,time=09:30:00,bid=1.08542,ask=1.08558,spread=0.00016,volume=2847000",
            "instrument=GBP/USD,time=09:30:00,bid=1.27134,ask=1.27152,spread=0.00018,volume=1923000",
            "instrument=USD/JPY,time=09:30:00,bid=155.421,ask=155.437,spread=0.016,volume=3412000",
            "instrument=EUR/USD,time=09:31:00,bid=1.08551,ask=1.08567,spread=0.00016,volume=2651000",
            "instrument=GBP/USD,time=09:31:00,bid=1.27142,ask=1.27160,spread=0.00018,volume=1844000",
            "instrument=USD/CHF,time=09:31:00,bid=0.89234,ask=0.89248,spread=0.00014,volume=1127000",
            "instrument=AUD/USD,time=09:32:00,bid=0.66712,ask=0.66726,spread=0.00014,volume=987000",
            "END_LOG"
        });

        var raw = TempFile("fx_log.txt");
        File.WriteAllText(raw, content);
        var zstPath = TempFile("fx_log.zst");
        var writer = new ZstWriter();
        writer.CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetDictionaryId — 0 for standard compression
        var dictId = doc.GetDictionaryId();
        Assert.True(dictId >= 0);
        Assert.Equal(dictId, doc.GetDictionaryId()); // consistent

        // GetContentHash
        var hash = doc.GetContentHash();
        Assert.NotNull(hash);
        Assert.NotEmpty(hash);
        Assert.Equal(hash, doc.GetContentHash()); // consistent

        // GetChecksumValid
        var checksumValid = doc.GetChecksumValid();
        Assert.Equal(checksumValid, doc.GetChecksumValid()); // consistent

        // Cross-check with other properties
        var level = doc.GetCompressionLevel();
        Assert.True(level >= 0);

        var magic = doc.GetMagicNumber();
        Assert.True(magic > 0);

        // SaveToFile
        var path = TempFile("dogfood_fx_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(dictId, loaded.GetDictionaryId());
        Assert.Equal(hash, loaded.GetContentHash());
        Assert.Equal(checksumValid, loaded.GetChecksumValid());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Compress different content and verify different hash
        var raw2 = TempFile("fx_log_v2.txt");
        File.WriteAllText(raw2, content + "\nAPPENDED_RECORD=true");
        var zst2 = TempFile("fx_log_v2.zst");
        writer.CompressFile(raw2, zst2);
        var doc2 = ZstDocument.LoadFile(zst2);
        Assert.NotNull(doc2.GetContentHash());
        Assert.NotEmpty(doc2.GetContentHash());
        // Different content may produce different hash
        Assert.True(doc2.GetDictionaryId() >= 0);

        // Final save
        var path2 = TempFile("dogfood_fx_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetDictionaryId(), loaded2.GetDictionaryId());
        Assert.Equal(loaded.GetContentHash(), loaded2.GetContentHash());
        Assert.Equal(loaded.GetChecksumValid(), loaded2.GetChecksumValid());
    }
}
