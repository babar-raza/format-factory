using System;
using System.IO;
using Xunit;
namespace FormatFactory.Netpbm.Tests;
public class NetpbmR408GetMeanPixelAndDynamicRangeDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NetpbmR408GetMeanPixelAndDynamicRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR408GetMeanPixelAndDynamicRangeDeepTests_" + Guid.NewGuid().ToString("N"));
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
    public void LoadFile_ValidPgm_ReturnsWidthHeight()
    {
        var pixels = new int[6];
        var content = CreatePgm(3, 2, 255, pixels);
        var path = TempFile("test.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(3, img.Width);
        Assert.Equal(2, img.Height);
    }
    [Fact]
    public void GetMeanPixelValue_GradientImage_ReturnsMidpoint()
    {
        var pixels = new int[] { 0, 50, 100, 150, 200, 255 };
        var content = CreatePgm(3, 2, 255, pixels);
        var path = TempFile("mean.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(125.833, img.GetMeanPixelValue(), 1);
    }
    [Fact]
    public void GetDynamicRange_FullRange_Returns255()
    {
        var pixels = new int[] { 0, 128, 255 };
        var content = CreatePgm(3, 1, 255, pixels);
        var path = TempFile("range.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(255, img.GetDynamicRange());
    }
    [Fact]
    public void GetPixelCount_MatchesDimensions()
    {
        var content = CreatePgm(8, 7, 255, new int[56]);
        var path = TempFile("count.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(56, img.GetPixelCount());
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
        Assert.Equal(img.GetMeanPixelValue(), reloaded.GetMeanPixelValue(), 1);
        Assert.Equal(img.GetDynamicRange(), reloaded.GetDynamicRange());
    }
    [Fact]
    public void Dogfood_UkGovFlag_MeanAndRangeCorrect()
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
        Assert.Equal(127.5, img.GetMeanPixelValue(), 1);
        Assert.Equal(255, img.GetDynamicRange());
    }
}