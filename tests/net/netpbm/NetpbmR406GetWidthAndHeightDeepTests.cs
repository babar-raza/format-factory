using System;
using System.IO;
using Xunit;
namespace FormatFactory.Netpbm.Tests;
public class NetpbmR406GetWidthAndHeightDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NetpbmR406GetWidthAndHeightDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR406GetWidthAndHeightDeepTests_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }
    public void Dispose() { if (Directory.Exists(_tempDir)) Directory.Delete(_tempDir, recursive: true); }
    private string TempFile(string name) => Path.Combine(_tempDir, name);
    private string CreatePgm(int width, int height, int[] pixels)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int i = 0; i < pixels.Length; i++)
        {
            sb.Append(pixels[i]);
            if ((i + 1) % width == 0) sb.AppendLine();
            else sb.Append(" ");
        }
        return sb.ToString();
    }
    private string CreatePpm(int width, int height, int[] pixels)
    {
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        for (int i = 0; i < pixels.Length; i += 3)
        {
            sb.AppendLine($"{pixels[i]} {pixels[i+1]} {pixels[i+2]}");
        }
        return sb.ToString();
    }
    [Fact]
    public void LoadFile_Pgm_ReturnsCorrectWidthHeight()
    {
        var pixels = new int[20];
        var content = CreatePgm(5, 4, pixels);
        var path = TempFile("test.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(5, img.Width);
        Assert.Equal(4, img.Height);
    }
    [Fact]
    public void LoadFile_Ppm_ReturnsCorrectWidthHeight()
    {
        var pixels = new int[30];
        var content = CreatePpm(5, 2, pixels);
        var path = TempFile("test.ppm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(5, img.Width);
        Assert.Equal(2, img.Height);
    }
    [Fact]
    public void GetPixelCount_Pgm_ReturnsWidthTimesHeight()
    {
        var content = CreatePgm(10, 8, new int[80]);
        var path = TempFile("count.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(80, img.GetPixelCount());
    }
    [Fact]
    public void GetMeanPixelValue_ConstantImage_ReturnsConstant()
    {
        var pixels = new int[16];
        Array.Fill(pixels, 128);
        var content = CreatePgm(4, 4, pixels);
        var path = TempFile("mean.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(128, img.GetMeanPixelValue());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesDimensions()
    {
        var content = CreatePgm(3, 3, new[] { 10, 20, 30, 40, 50, 60, 70, 80, 90 });
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
    public void Dogfood_UkFlagPattern_WidthHeightPixelCountCorrect()
    {
        var pixels = new int[200];
        for (int i = 0; i < 200; i++)
        {
            int row = i / 20;
            int col = i % 20;
            pixels[i] = (row < 10) ? (col < 10 ? 0 : 255) : (col < 10 ? 255 : 0);
        }
        var content = CreatePgm(20, 10, pixels);
        var path = TempFile("ukflag.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(20, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(200, img.GetPixelCount());
    }
}