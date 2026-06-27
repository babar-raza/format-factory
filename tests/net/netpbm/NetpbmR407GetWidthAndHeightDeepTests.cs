using System;
using System.IO;
using Xunit;
namespace FormatFactory.Netpbm.Tests;
public class NetpbmR407GetWidthAndHeightDeepTests : IDisposable
{
    private readonly string _tempDir;
    public NetpbmR407GetWidthAndHeightDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR407GetWidthAndHeightDeepTests_" + Guid.NewGuid().ToString("N"));
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
        var pixels = new int[12];
        var content = CreatePgm(4, 3, 255, pixels);
        var path = TempFile("test.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(4, img.Width);
        Assert.Equal(3, img.Height);
    }
    [Fact]
    public void GetPixelCount_EqualsWidthTimesHeight()
    {
        var pixels = new int[30];
        var content = CreatePgm(6, 5, 255, pixels);
        var path = TempFile("count.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(30, img.GetPixelCount());
    }
    [Fact]
    public void GetMeanPixelValue_AllSame_ReturnsThatValue()
    {
        var pixels = new int[25];
        Array.Fill(pixels, 200);
        var content = CreatePgm(5, 5, 255, pixels);
        var path = TempFile("mean.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(200, img.GetMeanPixelValue());
    }
    [Fact]
    public void GetDynamicRange_VariedPixels_ReturnsMaxMinusMin()
    {
        var pixels = new int[] { 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 };
        var content = CreatePgm(5, 2, 255, pixels);
        var path = TempFile("range.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(90, img.GetDynamicRange());
    }
    [Fact]
    public void SaveLoad_RoundTrip_PreservesDimensionsAndPixels()
    {
        var pixels = new int[] { 10, 20, 30, 40, 50, 60 };
        var content = CreatePgm(3, 2, 255, pixels);
        var path = TempFile("roundtrip.pgm");
        File.WriteAllText(path, content);
        var img = NetpbmImage.LoadFile(path);
        var savePath = TempFile("saved.pgm");
        img.SaveFile(savePath);
        var reloaded = NetpbmImage.LoadFile(savePath);
        Assert.Equal(img.Width, reloaded.Width);
        Assert.Equal(img.Height, reloaded.Height);
        Assert.Equal(img.GetMeanPixelValue(), reloaded.GetMeanPixelValue());
    }
    [Fact]
    public void Dogfood_UkGovFlag_DimensionsAndStatsCorrect()
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
        Assert.Equal(10, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(100, img.GetPixelCount());
        Assert.Equal(127.5, img.GetMeanPixelValue(), 1);
        Assert.Equal(255, img.GetDynamicRange());
    }
}