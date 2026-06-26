// Tests for NetpbmImage.GetChannelCount, SplitChannels, GetRedChannel deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R276

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R276: Tests for NetpbmImage.GetChannelCount, SplitChannels, GetRedChannel deeper.
/// GetChannelCount(): returns the number of channels (1 for PGM, 3 for PPM).
/// SplitChannels(): returns an array of single-channel images.
/// GetRedChannel(): returns the red channel as a grayscale image (PPM only; PGM returns self).
/// Covers: GetChannelCount no-throw; GetChannelCount positive; GetChannelCount consistent;
/// GetChannelCount 1 for PGM; GetChannelCount save-load;
/// SplitChannels no-throw; SplitChannels non-null; SplitChannels correct length;
/// SplitChannels same dimensions; SplitChannels consistent; SplitChannels save-load;
/// GetRedChannel no-throw; GetRedChannel non-null; GetRedChannel same dimensions;
/// GetRedChannel consistent; GetRedChannel save-load; GetRedChannel channel count 1;
/// dogfood LoadFile→GetChannelCount→SplitChannels→GetRedChannel→SaveToFile pipeline.
/// </summary>
public class NetpbmR276GetChannelCountAndSplitChannelsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR276GetChannelCountAndSplitChannelsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR276_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm()
    {
        var path = TempFile("gray.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("6 4");
        sb.AppendLine("255");
        for (int r = 0; r < 4; r++)
        {
            for (int c = 0; c < 6; c++)
            {
                sb.Append((r * 40 + c * 20) % 256);
                if (c < 5) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreatePpm()
    {
        var path = TempFile("color.ppm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P3");
        sb.AppendLine("4 3");
        sb.AppendLine("255");
        for (int r = 0; r < 3; r++)
        {
            for (int c = 0; c < 4; c++)
            {
                int red = (r * 60 + c * 30) % 256;
                int green = (r * 40 + c * 50) % 256;
                int blue = (r * 80 + c * 20) % 256;
                sb.Append($"{red} {green} {blue}");
                if (c < 3) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetChannelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetChannelCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var ex = Record.Exception(() => img.GetChannelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetChannelCount_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        Assert.True(img.GetChannelCount() > 0);
    }

    [Fact]
    public void GetChannelCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        Assert.Equal(img.GetChannelCount(), img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_1_For_PGM()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        Assert.Equal(1, img.GetChannelCount());
    }

    [Fact]
    public void GetChannelCount_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var before = img.GetChannelCount();
        var path = TempFile("gcc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // SplitChannels
    // -------------------------------------------------------------------------

    [Fact]
    public void SplitChannels_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var ex = Record.Exception(() => img.SplitChannels());
        Assert.Null(ex);
    }

    [Fact]
    public void SplitChannels_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        Assert.NotNull(img.SplitChannels());
    }

    [Fact]
    public void SplitChannels_CorrectLength_PGM()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var channels = img.SplitChannels();
        Assert.Equal(img.GetChannelCount(), channels.Length);
    }

    [Fact]
    public void SplitChannels_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var channels = img.SplitChannels();
        foreach (var ch in channels)
        {
            Assert.Equal(img.GetWidth(), ch.GetWidth());
            Assert.Equal(img.GetHeight(), ch.GetHeight());
        }
    }

    [Fact]
    public void SplitChannels_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var c1 = img.SplitChannels();
        var c2 = img.SplitChannels();
        Assert.Equal(c1.Length, c2.Length);
    }

    [Fact]
    public void SplitChannels_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var channels = img.SplitChannels();
        var path = TempFile("sc_ch0.pgm");
        channels[0].SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(channels[0].GetWidth(), loaded.GetWidth());
        Assert.Equal(channels[0].GetHeight(), loaded.GetHeight());
    }

    // -------------------------------------------------------------------------
    // GetRedChannel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRedChannel_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var ex = Record.Exception(() => img.GetRedChannel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetRedChannel_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        Assert.NotNull(img.GetRedChannel());
    }

    [Fact]
    public void GetRedChannel_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var red = img.GetRedChannel();
        Assert.Equal(img.GetWidth(), red.GetWidth());
        Assert.Equal(img.GetHeight(), red.GetHeight());
    }

    [Fact]
    public void GetRedChannel_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var r1 = img.GetRedChannel();
        var r2 = img.GetRedChannel();
        Assert.Equal(r1.GetWidth(), r2.GetWidth());
    }

    [Fact]
    public void GetRedChannel_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var red = img.GetRedChannel();
        var path = TempFile("rc_save.pgm");
        red.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(red.GetWidth(), loaded.GetWidth());
        Assert.Equal(red.GetHeight(), loaded.GetHeight());
    }

    [Fact]
    public void GetRedChannel_ChannelCount_1()
    {
        var img = NetpbmImage.LoadFile(CreatePgm());
        var red = img.GetRedChannel();
        Assert.Equal(1, red.GetChannelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetChannelCount_SplitChannels_GetRedChannel_SaveToFile_Pipeline()
    {
        // Build a larger PGM
        var rawPath = TempFile("dogfood_gray.pgm");
        var sb = new System.Text.StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("# dogfood channel test");
        sb.AppendLine("10 8");
        sb.AppendLine("255");
        for (int r = 0; r < 8; r++)
        {
            for (int c = 0; c < 10; c++)
            {
                int v = (r * 28 + c * 22) % 256;
                sb.Append(v);
                if (c < 9) sb.Append(' ');
            }
            sb.AppendLine();
        }
        File.WriteAllText(rawPath, sb.ToString());

        var img = NetpbmImage.LoadFile(rawPath);
        Assert.Equal(10, img.GetWidth());
        Assert.Equal(8, img.GetHeight());

        // GetChannelCount — PGM = 1
        var channelCount = img.GetChannelCount();
        Assert.Equal(1, channelCount);
        Assert.Equal(channelCount, img.GetChannelCount()); // consistent

        // SplitChannels
        var channels = img.SplitChannels();
        Assert.NotNull(channels);
        Assert.Equal(channelCount, channels.Length);
        foreach (var ch in channels)
        {
            Assert.Equal(img.GetWidth(), ch.GetWidth());
            Assert.Equal(img.GetHeight(), ch.GetHeight());
        }

        // SplitChannels consistent
        var ch2 = img.SplitChannels();
        Assert.Equal(channels.Length, ch2.Length);

        // GetRedChannel
        var red = img.GetRedChannel();
        Assert.NotNull(red);
        Assert.Equal(img.GetWidth(), red.GetWidth());
        Assert.Equal(img.GetHeight(), red.GetHeight());
        Assert.Equal(1, red.GetChannelCount());

        // GetRedChannel consistent
        var red2 = img.GetRedChannel();
        Assert.Equal(red.GetWidth(), red2.GetWidth());

        // Operations on red channel
        var invRed = red.InvertColors();
        Assert.NotNull(invRed);
        Assert.Equal(red.GetWidth(), invRed.GetWidth());

        var threshRed = red.Threshold(128);
        Assert.NotNull(threshRed);
        Assert.Equal(red.GetWidth(), threshRed.GetWidth());

        // SaveToFile — channel 0
        var ch0Path = TempFile("dogfood_ch0.pgm");
        channels[0].SaveToFile(ch0Path);
        Assert.True(File.Exists(ch0Path));
        var loadedCh0 = NetpbmImage.LoadFile(ch0Path);
        Assert.Equal(img.GetWidth(), loadedCh0.GetWidth());
        Assert.Equal(img.GetHeight(), loadedCh0.GetHeight());
        Assert.Equal(1, loadedCh0.GetChannelCount());

        // SaveToFile — red channel
        var redPath = TempFile("dogfood_red.pgm");
        red.SaveToFile(redPath);
        Assert.True(File.Exists(redPath));
        var loadedRed = NetpbmImage.LoadFile(redPath);
        Assert.Equal(red.GetWidth(), loadedRed.GetWidth());
        Assert.Equal(1, loadedRed.GetChannelCount());

        // Apply operations to loaded
        var gammaRed = loadedRed.ApplyGamma(2.2);
        Assert.NotNull(gammaRed);
        Assert.Equal(loadedRed.GetWidth(), gammaRed.GetWidth());

        // Final save
        var finalPath = TempFile("dogfood_gamma_red.pgm");
        gammaRed.SaveToFile(finalPath);
        Assert.True(File.Exists(finalPath));
        var loaded2 = NetpbmImage.LoadFile(finalPath);
        Assert.Equal(gammaRed.GetWidth(), loaded2.GetWidth());
        Assert.True(loaded2.GetChannelCount() > 0);
    }
}
