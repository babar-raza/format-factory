using System;
using System.IO;
using Xunit;
namespace FormatFactory.Netpbm.Tests;
public class NetpbmR405GetPixelCountAndMeanPixelValueDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NetpbmR405GetPixelCountAndMeanPixelValueDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR405GetPixelCountAndMeanPixelValueDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreatePgm(int width, int height, int maxVal, int[] pixels)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine(maxVal.ToString());
        for (int i = 0; i < pixels.Length; i++)
        {
            sb.Append(pixels[i]);
            if ((i + 1) % width == 0) sb.AppendLine();
            else sb.Append(" ");
        }
        return sb.ToString();
    }
    [Fact]
    public void LoadFile_ValidPgm_ReturnsWidthHeight()
    {
        var pixels = new int[] { 0, 128, 255, 100, 50, 200, 10, 240, 150 };
        var content = CreatePgm(3, 3, 255, pixels);
        var path = TempFile("test.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(3, img.Width);
        Assert.Equal(3, img.Height);
    }
    [Fact]
    public void GetPixelCount_ReturnsWidthTimesHeight()
    {
        var pixels = new int[12];
        var content = CreatePgm(4, 3, 255, pixels);
        var path = TempFile("count.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.GetPixelCount());
    }
    [Fact]
    public void GetMeanPixelValue_UniformPixels_ReturnsSameValue()
    {
        var pixels = new int[16];
        Array.Fill(pixels, 128);
        var content = CreatePgm(4, 4, 255, pixels);
        var path = TempFile("mean.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(128, img.GetMeanPixelValue());
    }
    [Fact]
    public void GetDynamicRange_MinMaxPixels_ReturnsRange()
    {
        var pixels = new int[] { 0, 50, 100, 150, 200, 255 };
        var content = CreatePgm(3, 2, 255, pixels);
        var path = TempFile("range.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(255, img.GetDynamicRange());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesDimensions()
    {
        var pixels = new int[] { 10, 20, 30, 40 };
        var content = CreatePgm(2, 2, 255, pixels);
        var path = TempFile("roundtrip.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        var savePath = TempFile("saved.pgm");
        img.SaveFile(savePath);
        var reloaded = NetpbmImage.LoadFile(savePath);
        Assert.Equal(img.Width, reloaded.Width);
        Assert.Equal(img.Height, reloaded.Height);
    }
    [Fact]
    public void Dogfood_UkGovFlagPattern_PixelCountMeanRangeCorrect()
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
        Assert.Equal(255, img.GetDynamicRange());
    }
}