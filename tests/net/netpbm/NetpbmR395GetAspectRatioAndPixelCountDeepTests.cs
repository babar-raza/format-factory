// Tests for NetpbmImage.GetAspectRatio, GetPixelCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R395

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R395: Tests for NetpbmImage.GetAspectRatio, GetPixelCount deeper.
/// GetAspectRatio(): returns the width-to-height ratio of the image.
/// GetPixelCount(): returns the total number of pixels (width × height).
/// Covers: GetAspectRatio no-throw; GetAspectRatio positive; GetAspectRatio one for square;
/// GetAspectRatio consistent; GetAspectRatio save-load;
/// GetPixelCount no-throw; GetPixelCount positive; GetPixelCount equals width times height;
/// GetPixelCount consistent; GetPixelCount save-load; dogfood pipeline.
/// </summary>
public class NetpbmR395GetAspectRatioAndPixelCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR395GetAspectRatioAndPixelCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR395_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreatePgm(string name, int width, int height, int fillVal = 128)
    {
        var path = TempFile(name);
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine($"{width} {height}");
        sb.AppendLine("255");
        var rng = new Random(42);
        for (int y = 0; y < height; y++)
        {
            var row = new StringBuilder();
            for (int x = 0; x < width; x++)
            {
                if (x > 0) row.Append(' ');
                row.Append(fillVal == -1 ? rng.Next(0, 256) : fillVal);
            }
            sb.AppendLine(row.ToString());
        }
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetAspectRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAspectRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        var ex = Record.Exception(() => img.GetAspectRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetAspectRatio_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        Assert.True(img.GetAspectRatio() > 0.0);
    }

    [Fact]
    public void GetAspectRatio_One_ForSquare()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("square.pgm", 40, 40));
        Assert.Equal(1.0, img.GetAspectRatio(), precision: 6);
    }

    [Fact]
    public void GetAspectRatio_Two_ForDoubleWide()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("wide.pgm", 80, 40));
        Assert.Equal(2.0, img.GetAspectRatio(), precision: 6);
    }

    [Fact]
    public void GetAspectRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        Assert.Equal(img.GetAspectRatio(), img.GetAspectRatio());
    }

    [Fact]
    public void GetAspectRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        var before = img.GetAspectRatio();
        var path = TempFile("ar_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetAspectRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetPixelCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetPixelCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        var ex = Record.Exception(() => img.GetPixelCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetPixelCount_Positive()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        Assert.True(img.GetPixelCount() > 0);
    }

    [Fact]
    public void GetPixelCount_Equals_Width_Times_Height()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        Assert.Equal(80 * 40, img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        Assert.Equal(img.GetPixelCount(), img.GetPixelCount());
    }

    [Fact]
    public void GetPixelCount_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreatePgm("rect.pgm", 80, 40));
        var before = img.GetPixelCount();
        var path = TempFile("pc_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetPixelCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetAspectRatio_GetPixelCount_Pipeline()
    {
        // Media — Ofcom / BBC: UHD and HD Broadcast Format Compliance Testing
        // PGM proxy images representing frame samples from broadcast formats
        // Aspect ratio and pixel count validate format specification compliance

        // Frame 1: HD 720p (1280x720 → 16:9)
        var path1 = TempFile("bbc_hd_720p_frame.pgm");
        CreatePgm("bbc_hd_720p_frame.pgm", 128, 72); // scaled proxy of 1280x720
        var img1 = NetpbmImage.LoadFile(path1);

        // Frame 2: 4:3 SD frame (640x480)
        var path2 = TempFile("bbc_sd_4x3_frame.pgm");
        CreatePgm("bbc_sd_4x3_frame.pgm", 80, 60); // scaled proxy of 640x480
        var img2 = NetpbmImage.LoadFile(path2);

        // Frame 3: Square thumbnail (512x512)
        var path3 = TempFile("bbc_square_thumb.pgm");
        CreatePgm("bbc_square_thumb.pgm", 64, 64);
        var img3 = NetpbmImage.LoadFile(path3);

        // Frame 4: Ultrawide cinematic (21:9 proxy — 126x54)
        var path4 = TempFile("bbc_ultrawide_frame.pgm");
        CreatePgm("bbc_ultrawide_frame.pgm", 126, 54);
        var img4 = NetpbmImage.LoadFile(path4);

        // Aspect ratios
        var ar1 = img1.GetAspectRatio();
        var ar2 = img2.GetAspectRatio();
        var ar3 = img3.GetAspectRatio();
        var ar4 = img4.GetAspectRatio();

        Assert.True(ar1 > 0.0);
        Assert.True(ar2 > 0.0);
        Assert.Equal(1.0, ar3, precision: 6); // square
        Assert.True(ar4 > 0.0);

        // 16:9 is wider than 4:3
        Assert.True(ar1 > ar2);

        // Ultrawide is wider than 16:9
        Assert.True(ar4 > ar1);

        // Consistency
        Assert.Equal(ar1, img1.GetAspectRatio());
        Assert.Equal(ar2, img2.GetAspectRatio());

        // Pixel counts
        var pc1 = img1.GetPixelCount();
        var pc2 = img2.GetPixelCount();
        var pc3 = img3.GetPixelCount();
        var pc4 = img4.GetPixelCount();

        Assert.Equal(128 * 72, pc1);
        Assert.Equal(80 * 60, pc2);
        Assert.Equal(64 * 64, pc3);
        Assert.Equal(126 * 54, pc4);

        // All positive
        Assert.True(pc1 > 0);
        Assert.True(pc2 > 0);
        Assert.True(pc3 > 0);

        // Consistency
        Assert.Equal(pc1, img1.GetPixelCount());
        Assert.Equal(pc3, img3.GetPixelCount());

        // SaveToFile
        var out1 = TempFile("bbc_hd_720p_out.pgm");
        img1.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        var loaded1 = NetpbmImage.LoadFile(out1);
        Assert.Equal(ar1, loaded1.GetAspectRatio(), precision: 6);
        Assert.Equal(pc1, loaded1.GetPixelCount());

        var out2 = TempFile("bbc_sd_4x3_out.pgm");
        img2.SaveToFile(out2);
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.Equal(ar2, loaded2.GetAspectRatio(), precision: 6);
        Assert.Equal(pc2, loaded2.GetPixelCount());

        var out3 = TempFile("bbc_square_out.pgm");
        img3.SaveToFile(out3);
        var loaded3 = NetpbmImage.LoadFile(out3);
        Assert.Equal(1.0, loaded3.GetAspectRatio(), precision: 6);
        Assert.Equal(pc3, loaded3.GetPixelCount());

        var ex1 = Record.Exception(() => loaded1.GetAspectRatio());
        var ex2 = Record.Exception(() => loaded2.GetPixelCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
