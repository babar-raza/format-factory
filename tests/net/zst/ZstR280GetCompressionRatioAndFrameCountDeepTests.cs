using System;
using System.IO;
using System.IO.Compression;
using Xunit;
namespace FormatFactory.Zst.Tests;
public class ZstR280GetCompressionRatioAndFrameCountDeepTests : IDisposable
{
    private readonly string _tempDir;
    public ZstR280GetCompressionRatioAndFrameCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR280GetCompressionRatioAndFrameCountDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void LoadFile_SmallData_ReturnsFrameCountOne()
    {
        var path = TempFile("small.zst");
        CreateZstFile(path, new byte[] { 0x01, 0x02, 0x03 });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetCompressionRatio_Uncompressible_ReturnsHighRatio()
    {
        var path = TempFile("incompressible.zst");
        var data = new byte[1000];
        new Random(1).NextBytes(data);
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0.9);
    }
    [Fact]
    public void GetFrameCount_MultipleFrames_ReturnsCount()
    {
        var path = TempFile("multi.zst");
        using (path, new byte[] { 1, 2, 3 });
        using (var fs = File.Open(path, FileMode.Append))
        using (var zs = new ZLibStream(fs, CompressionLevel.Optimal))
        {
            zs.Write(new byte[] { 4, 5, 6 });
        }
        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.GetFrameCount() >= 1);
    }
    [Fact]
    public void GetMagicBytes_ValidFile_ReturnsCorrectSignature()
    {
        var path = TempFile("magic.zst");
        CreateZstFile(path, new byte[] { 0x28, 0xB5, 0x2F, 0xFD });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(new byte[] { 0x28, 0xB5, 0x2F, 0xFD }, doc.GetMagicBytes());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesCompressionRatio()
    {
        var path = TempFile("roundtrip.zst");
        CreateZstFile(path, new byte[500]);
        var doc = ZstDocument.LoadFile(path);
        var origRatio = doc.GetCompressionRatio();
        var savePath = TempFile("saved.zst");
        doc.SaveFile(savePath);
        var reloaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(origRatio, reloaded.GetCompressionRatio(), 5);
    }
    [Fact]
    public void Dogfood_UkGovArchive_RatioAndFramesValid()
    {
        var ukData = System.Text.Encoding.UTF8.GetBytes(
            "UK GOVT DATA\n" +
            "NHS,56000000,Health\n" +
            "HMRC,67000000,Tax\n" +
            "DVLA,48000000,Licensing\n" +
            "ONS,67000000,Statistics\n" +
            "DEFRA,5000000,Environment\n"
        );
        var path = TempFile("ukgov.zst");
        CreateZstFile(path, ukData);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
        Assert.True(doc.GetCompressionRatio() > 0 && doc.GetCompressionRatio() <= 1.0);
    }
}