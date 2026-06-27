using System;
using System.IO;
using System.IO.Compression;
using Xunit;
namespace FormatFactory.Zst.Tests;
public class ZstR278GetFrameCountAndCompressionRatioDeepTests : IDisposable
{
    private readonly string _tempDir;
    public ZstR278GetFrameCountAndCompressionRatioDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR278GetFrameCountAndCompressionRatioDeepTests_" + Guid.NewGuid().ToString("N"));
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
        CreateZstFile(path, new byte[] { 1, 2, 3, 4, 5 });
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetFrameCount_MultipleWrites_ReturnsCorrectCount()
    {
        var path = TempFile("multi.zst");
        using (var fs = File.Create(path))
        using (var zs = new ZLibStream(fs, CompressionLevel.Optimal))
        {
            zs.Write(new byte[] { 1, 2, 3 });
            zs.Write(new byte[] { 4, 5, 6 });
        }
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
    }
    [Fact]
    public void GetCompressionRatio_CompressedData_ReturnsRatio()
    {
        var path = TempFile("ratio.zst");
        var data = new byte[1000];
        for (int i = 0; i < data.Length; i++) data[i] = (byte)(i % 256);
        CreateZstFile(path, data);
        var doc = ZstDocument.LoadFile(path);
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0 && ratio <= 1.0);
    }
    [Fact]
    public void GetMagicBytes_ValidZst_ReturnsMagicBytes()
    {
        var path = TempFile("magic.zst");
        CreateZstFile(path, new byte[] { 0x28, 0xB5, 0x2F, 0xFD });
        var doc = ZstDocument.LoadFile(path);
        var magic = doc.GetMagicBytes();
        Assert.NotNull(magic);
        Assert.Equal(4, magic.Length);
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesFrameCount()
    {
        var path = TempFile("roundtrip.zst");
        CreateZstFile(path, new byte[] { 10, 20, 30, 40 });
        var doc = ZstDocument.LoadFile(path);
        var savePath = TempFile("saved.zst");
        doc.SaveFile(savePath);
        var reloaded = ZstDocument.LoadFile(savePath);
        Assert.Equal(doc.GetFrameCount(), reloaded.GetFrameCount());
    }
    [Fact]
    public void Dogfood_UkGovDataArchive_FrameCountAndRatioCorrect()
    {
        var ukData = System.Text.Encoding.UTF8.GetBytes(
            "NHS England,56000000,150000000000\n" +
            "HMRC,67000000,80000000000\n" +
            "DVLA,48000000,5000000000\n" +
            "ONS,67000000,3000000000\n"
        );
        var path = TempFile("ukgov.zst");
        CreateZstFile(path, ukData);
        var doc = ZstDocument.LoadFile(path);
        Assert.Equal(1, doc.GetFrameCount());
        var ratio = doc.GetCompressionRatio();
        Assert.True(ratio > 0 && ratio <= 1.0);
    }
}