using System;
using System.IO;
using System.IO.Compression;
using Xunit;
namespace FormatFactory.Zst.Tests;
public class ZstR279GetFrameCountAndMagicBytesDeepTests : IDisposable
{
    private readonly string _tempDir;
    public ZstR279GetFrameCountAndMagicBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR279GetFrameCountAndMagicBytesDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private void CreateZstFile(string path, byte[] data)
    {
        using var fs = File.Create(path);
        using var zs = new ZLibStream(fs, CompressionLevel.Optimal);
        zs.Write(data);
    }
    [Fact]
    public void LoadFile_EmptyData_ReturnsFrameCountOne()
    {
        var path = TempFile("empty.zst");
        CreateZstFile(path, Array.Empty<byte>());
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetFrameCount_LargeData_ReturnsCorrectCount()
    {
        var path = TempFile("large.zst");
        var data = new byte[10000];
        new Random(42).NextBytes(data);
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetMagicBytes_ValidZst_ReturnsExpectedBytes()
    {
        var path = TempFile("magic.zst");
        CreateZstFile(path, new byte[] { 0x28, 0xB5, 0x2F, 0xFD });
        var doc = ZstDocument.LoadFile(path);
        var magic = doc.GetMagicBytes();
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, magic);
    }
    [Fact]
    public void GetCompressionRatio_HighlyCompressible_ReturnsLowRatio()
    {
        var path = TempFile("compressible.zst");
        var data = new byte[5000];
        for (int i = 0; i < data.Length; i++) data[i] = 0xAA;
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio < 0.1);
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesMagicBytes()
    {
        var path = TempFile("roundtrip.zst");
        CreateZstFile(path, new byte[] { 1, 2, 3, 4 });
        var doc = ZstDocument.LoadFile(path);
        var savePath = TempFile("saved.zst");
        doc.SaveFile(savePath);
        var reloaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.GetMagicBytes(), reloaded.GetMagicBytes());
    }
    [Fact]
    public void Dogfood_UkGovArchive_MagicBytesAndFrameCountValid()
    {
        var ukData = System.Text.Encoding.UTF8.GetBytes(
            "UK GOVERNMENT DATA ARCHIVE\n" +
            "NHS England|56000000|Health\n" +
            "HMRC|67000000|Tax\n" +
            "DVLA|48000000|Licensing\n" +
            "ONS|67000000|Statistics\n"
        );
        var path = TempFile("ukgov.zst");
        CreateZstFile(path, ukData);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, doc.GetMagicBytes());
    }
}