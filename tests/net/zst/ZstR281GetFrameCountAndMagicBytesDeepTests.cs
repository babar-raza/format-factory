using System;
using System.IO;
using System.IO.Compression;
using Xunit;
namespace FormatFactory.Zst.Tests;
public class ZstR281GetFrameCountAndMagicBytesDeepTests : IDisposable
{
    private readonly string _tempDir;
    public ZstR281GetFrameCountAndMagicBytesDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR281GetFrameCountAndMagicBytesDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void LoadFile_ValidZst_ReturnsFrameCount()
    {
        var path = TempFile("test.zst");
        CreateZstFile(path, new byte[] { 1, 2, 3, 4 });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetMagicBytes_StandardHeader_ReturnsExpected()
    {
        var path = TempFile("magic.zst");
        CreateZstFile(path, new byte[] { 0x28, 0xB5, 0x2F, 0xFD });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, doc.GetMagicBytes());
    }
    [Fact]
    public void GetFrameCount_LargeFile_StillOne()
    {
        var path = TempFile("large.zst");
        var data = new byte[50000];
        new Random(123).NextBytes(data);
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetCompressionRatio_VariousData_ReturnsValid()
    {
        var path = TempFile("ratio.zst");
        var data = new byte[2000];
        for (int i = 0; i < data.Length; i++) data[i] = (byte)(i % 10);
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0 && ratio <= 1.0);
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesMagicBytes()
    {
        var path = TempFile("roundtrip.zst");
        CreateZstFile(path, new byte[] { 10, 20, 30 });
        var doc = ZstDocument.LoadFile(path);
        var savePath = TempFile("saved.zst");
        doc.SaveFile(savePath);
        var reloaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.GetMagicBytes(), reloaded.GetMagicBytes());
    }
    [Fact]
    public void Dogfood_UkGovData_MagicAndFramesValid()
    {
        var ukData = System.Text.Encoding.UTF8.GetBytes(
            "UK GOV DATA\n" +
            "NHS,England,56000000\n" +
            "HMRC,UK,67000000\n" +
            "DVLA,GB,48000000\n"
        );
        var path = TempFile("ukgov.zst");
        CreateZstFile(path, ukData);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, doc.GetMagicBytes());
    }
}