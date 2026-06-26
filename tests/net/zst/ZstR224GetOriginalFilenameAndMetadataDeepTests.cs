// Tests for ZstDocument.GetOriginalFilename, GetContentChecksum, GetCreationTime deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R224

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R224: Tests for ZstDocument.GetOriginalFilename, GetContentChecksum, GetCreationTime deeper.
/// GetOriginalFilename(): returns the original filename stored in Zstandard metadata.
/// GetContentChecksum(): returns the checksum of the decompressed content.
/// GetCreationTime(): returns the creation timestamp from the archive metadata.
/// Covers: GetOriginalFilename no-throw; GetOriginalFilename non-null; GetOriginalFilename consistent;
/// GetOriginalFilename save-load;
/// GetContentChecksum no-throw; GetContentChecksum non-null; GetContentChecksum consistent;
/// GetContentChecksum save-load; GetContentChecksum non-empty;
/// GetCreationTime no-throw; GetCreationTime consistent; GetCreationTime save-load;
/// GetCreationTime non-negative;
/// dogfood Compress→GetOriginalFilename→GetContentChecksum→GetCreationTime→SaveToFile pipeline.
/// </summary>
public class ZstR224GetOriginalFilenameAndMetadataDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR224GetOriginalFilenameAndMetadataDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR224_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateZstFile(string filename = "data.txt")
    {
        var raw = TempFile(filename);
        File.WriteAllText(raw, "Sample content for Zstandard metadata tests. " +
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 The quick brown fox jumps over the lazy dog.");
        var zst = TempFile(filename + ".zst");
        new ZstWriter().CompressFile(raw, zst);
        return zst;
    }

    // -------------------------------------------------------------------------
    // GetOriginalFilename
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOriginalFilename_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetOriginalFilename());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOriginalFilename_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotNull(doc.GetOriginalFilename());
    }

    [Fact]
    public void GetOriginalFilename_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetOriginalFilename(), doc.GetOriginalFilename());
    }

    [Fact]
    public void GetOriginalFilename_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetOriginalFilename();
        var path = TempFile("ofn_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetOriginalFilename());
    }

    // -------------------------------------------------------------------------
    // GetContentChecksum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContentChecksum_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetContentChecksum());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContentChecksum_NonNull()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotNull(doc.GetContentChecksum());
    }

    [Fact]
    public void GetContentChecksum_NonEmpty()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.NotEmpty(doc.GetContentChecksum());
    }

    [Fact]
    public void GetContentChecksum_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetContentChecksum(), doc.GetContentChecksum());
    }

    [Fact]
    public void GetContentChecksum_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetContentChecksum();
        var path = TempFile("ccs_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetContentChecksum());
    }

    // -------------------------------------------------------------------------
    // GetCreationTime
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCreationTime_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var ex = Record.Exception(() => doc.GetCreationTime());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCreationTime_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.True(doc.GetCreationTime() >= 0);
    }

    [Fact]
    public void GetCreationTime_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        Assert.Equal(doc.GetCreationTime(), doc.GetCreationTime());
    }

    [Fact]
    public void GetCreationTime_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateZstFile());
        var before = doc.GetCreationTime();
        var path = TempFile("ct_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCreationTime());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOriginalFilename_GetContentChecksum_GetCreationTime_SaveToFile_Pipeline()
    {
        var srcName = "scientific_data.csv";
        var raw = TempFile(srcName);
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("ExperimentId,Temperature,Pressure,Concentration,Yield,Purity");
        for (int i = 1; i <= 50; i++)
            sb.AppendLine($"EXP{i:D3},{20 + i * 0.5},{1013 - i * 2},{0.1 + i * 0.02},{65 + i * 0.6},{95 + i * 0.08}");
        File.WriteAllText(raw, sb.ToString());

        var zstPath = TempFile(srcName + ".zst");
        new ZstWriter().CompressFile(raw, zstPath);

        var doc = ZstDocument.LoadFile(zstPath);
        Assert.True(doc.GetCompressedSize() > 0);
        Assert.True(doc.GetDecompressedSize() > 0);

        // GetOriginalFilename
        var filename = doc.GetOriginalFilename();
        Assert.NotNull(filename);
        Assert.Equal(filename, doc.GetOriginalFilename()); // consistent

        // GetContentChecksum
        var checksum = doc.GetContentChecksum();
        Assert.NotNull(checksum);
        Assert.NotEmpty(checksum);
        Assert.Equal(checksum, doc.GetContentChecksum()); // consistent

        // GetCreationTime
        var creationTime = doc.GetCreationTime();
        Assert.True(creationTime >= 0);
        Assert.Equal(creationTime, doc.GetCreationTime()); // consistent

        // Cross-checks
        Assert.True(doc.GetCompressionRatio() > 0);
        Assert.True(doc.GetBlockCount() >= 1);

        // SaveToFile
        var path = TempFile("dogfood_scientific_out.zst");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(filename, loaded.GetOriginalFilename());
        Assert.Equal(checksum, loaded.GetContentChecksum());
        Assert.Equal(creationTime, loaded.GetCreationTime());
        Assert.Equal(doc.GetCompressedSize(), loaded.GetCompressedSize());

        // Final save
        var path2 = TempFile("dogfood_scientific_v2.zst");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = ZstDocument.LoadFile(path2);
        Assert.Equal(loaded.GetOriginalFilename(), loaded2.GetOriginalFilename());
        Assert.Equal(loaded.GetContentChecksum(), loaded2.GetContentChecksum());
        Assert.Equal(loaded.GetCreationTime(), loaded2.GetCreationTime());
    }
}
