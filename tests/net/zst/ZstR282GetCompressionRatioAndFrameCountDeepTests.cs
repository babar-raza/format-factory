using System;
using System.IO;
using System.IO.Compression;
using Xunit;
namespace FormatFactory.Zst.Tests;
public class ZstR282GetCompressionRatioAndFrameCountDeepTests : IDisposable
{
    private readonly string _tempDir;
    public ZstR282GetCompressionRatioAndFrameCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR282GetCompressionRatioAndFrameCountDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void LoadFile_EmptyFrame_ReturnsFrameCount()
    {
        var path = TempFile("empty.zst");
        CreateZstFile(path, Array.Empty<byte>());
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetCompressionRatio_RepeatingPattern_ReturnsLowRatio()
    {
        var path = TempFile("repeat.zst");
        var data = new byte[10000];
        for (int i = 0; i < data.Length; i++) data[i] = 0x55;
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio < 0.05);
    }
    [Fact]
    public void GetFrameCount_SingleFrame_ReturnsOne()
    {
        var path = TempFile("single.zst");
        CreateZstFile(path, new byte[] { 1, 2, 3, 4, 5 });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetMagicBytes_ValidFile_ReturnsExpected()
    {
        var path = TempFile("magic.zst");
        CreateZstFile(path, new byte[] { 0x28, 0xB5, 0x2F, 0xFD });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, doc.GetMagicBytes());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesFrameCount()
    {
        var path = TempFile("roundtrip.zst");
        CreateZstFile(path, new byte[100]);
        var doc = ZstDocument.LoadFile(path);
        var savePath = TempFile("saved.zst");
        doc.SaveFile(savePath);
        var reloaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.GetFrameCount(), reloaded.GetFrameCount());
    }
    [Fact]
    public void Dogfood_UkGovData_CompressionRatioAndFramesValid()
    {
        var ukData = System.Text.Encoding.UTF8.GetBytes(
            "UK GOVERNMENT DATA SET\n" +
            "NHS England,Population,56000000\n" +
            "HMRC,Revenue,80000000000\n" +
            "DVLA,Licences,48000000\n" +
            "ONS,Statistics,67000000\n" +
            "DEFRA,Environment,8000000000\n"
        );
        var path = TempFile("ukgov.zst");
        CreateZstFile(path, ukData);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
        Assert.True(doc.GetCompressionRatio() > 0 && doc.GetCompressionRatio() <= 1.0);
    }
}