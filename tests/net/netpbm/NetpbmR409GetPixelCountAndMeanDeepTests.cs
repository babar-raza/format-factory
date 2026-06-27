using System;
using System.IO;
using Xunit;
namespace FormatFactory.Netpbm.Tests;
public class NetpbmR409GetPixelCountAndMeanDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NetpbmR409GetPixelCountAndMeanDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR409GetPixelCountAndMeanDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreatePgm(int w, int h, int max, int[] pixels)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{w} {h}");
        sb.AppendLine(max.ToString());
        for (int i = 0; i < pixels.Length; i++)
        {
            sb.Append(pixels[i]);
            if ((i + 1) % w == 0) sb.AppendLine();
            else sb.Append(" ");
        }
        return sb.ToString();
    }
    [Fact]
    public void LoadFile_ValidPgm_ReturnsDimensions()
    {
        var pixels = new int[20];
        var content = CreatePgm(5, 4, 255, pixels);
        var path = TempFile("test.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(5, img.Width);
        Assert.Equal(4, img.Height);
    }
    [Fact]
    public void GetPixelCount_ReturnsWidthTimesHeight()
    {
        var content = CreatePgm(7, 6, 255, new int[42]);
        var path = TempFile("count.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(42, img.GetPixelCount());
    }
    [Fact]
    public void GetMeanPixelValue_AllPixelsSame_ReturnsValue()
    {
        var pixels = new int[36];
        Array.Fill(pixels, 175);
        var content = CreatePgm(6, 6, 255, pixels);
        var path = TempFile("mean.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(175, img.GetMeanPixelValue());
    }
    [Fact]
    public void GetDynamicRange_FullRange_ReturnsMaxMinusMin()
    {
        var pixels = new int[] { 0, 100, 200, 255 };
        var content = CreatePgm(4, 1, 255, pixels);
        var path = TempFile("range.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(255, img.GetDynamicRange());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesStats()
    {
        var pixels = new int[] { 10, 20, 30, 40, 50, 60 };
        var content = CreatePgm(3, 2, 255, pixels);
        var path = TempFile("roundtrip.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        var savePath = TempFile("saved.pgm");
        img.SaveFile(savePath);
        var reloaded = NetpbmImage.LoadFile(savePath);
        Assert.Equal(img.GetPixelCount(), reloaded.GetPixelCount());
        Assert.Equal(img.GetMeanPixelValue(), reloaded.GetMeanPixelValue(), 1);
    }
    [Fact]
    public void Dogfood_UkFlagPattern_PixelCountAndMeanCorrect()
    {
        var pixels = new int[100];
        for (int i = 0; i < 100; i++)
        {
            int row = i / 10;
            int col = i % 10;
            pixels[i] = (row < 5) ? (col < 5 ? 0 : 255) : (col < 5 ? 255 : 0);
        }
        var content = CreatePgm(10, 10, 255, pixels);
        var path = TempFile("ukflag.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(100, img.GetPixelCount());
        Assert.Equal(127.5, img.GetMeanPixelValue(), 1);
    }
}