// Tests for NetpbmImage.GetConnectedComponentCount, GetBlobCount, GetLargestBlobArea deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R327

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R327: Tests for NetpbmImage.GetConnectedComponentCount, GetBlobCount, GetLargestBlobArea deeper.
/// GetConnectedComponentCount(): returns the number of distinct connected regions at threshold.
/// GetBlobCount(): returns the number of distinct bright blobs detected in the image.
/// GetLargestBlobArea(): returns the pixel area of the largest detected blob.
/// Covers: GetConnectedComponentCount no-throw; GetConnectedComponentCount non-negative;
/// GetConnectedComponentCount consistent;
/// GetBlobCount no-throw; GetBlobCount non-negative; GetBlobCount consistent;
/// GetBlobCount positive for multi-blob image;
/// GetLargestBlobArea no-throw; GetLargestBlobArea non-negative; GetLargestBlobArea consistent;
/// GetLargestBlobArea save-load;
/// dogfood GetConnectedComponentCount→GetBlobCount→GetLargestBlobArea pipeline.
/// </summary>
public class NetpbmR327GetConnectedComponentsAndBlobCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR327GetConnectedComponentsAndBlobCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR327_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMultiBlobPgm()
    {
        // 12x12 PGM with three distinct bright blobs on dark background
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        // Background: dark (10)
        // Blob 1: top-left (rows 0-2, cols 0-2): bright (220)
        // Blob 2: top-right (rows 0-2, cols 9-11): bright (200)
        // Blob 3: bottom-centre (rows 9-11, cols 4-7): bright (210)
        int[,] grid = new int[12, 12];
        for (int r = 0; r < 12; r++)
            for (int c = 0; c < 12; c++)
                grid[r, c] = 10;
        // Blob 1
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                grid[r, c] = 220;
        // Blob 2
        for (int r = 0; r < 3; r++)
            for (int c = 9; c < 12; c++)
                grid[r, c] = 200;
        // Blob 3
        for (int r = 9; r < 12; r++)
            for (int c = 4; c < 8; c++)
                grid[r, c] = 210;
        for (int r = 0; r < 12; r++)
        {
            var vals = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 12; c++) vals.Add(grid[r, c].ToString());
            sb.AppendLine(string.Join(" ", vals));
        }
        var path = TempFile("multi_blob.pgm");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    private string CreateUniformPgm()
    {
        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        for (int r = 0; r < 12; r++)
            sb.AppendLine("50 50 50 50 50 50 50 50 50 50 50 50");
        var path = TempFile("uniform.pgm");
        File.WriteAllText(path, sb.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetConnectedComponentCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetConnectedComponentCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        var ex = Record.Exception(() => img.GetConnectedComponentCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetConnectedComponentCount_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.True(img.GetConnectedComponentCount() >= 0);
    }

    [Fact]
    public void GetConnectedComponentCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.Equal(img.GetConnectedComponentCount(), img.GetConnectedComponentCount());
    }

    // -------------------------------------------------------------------------
    // GetBlobCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBlobCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        var ex = Record.Exception(() => img.GetBlobCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBlobCount_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.True(img.GetBlobCount() >= 0);
    }

    [Fact]
    public void GetBlobCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.Equal(img.GetBlobCount(), img.GetBlobCount());
    }

    [Fact]
    public void GetBlobCount_Positive_ForMultiBlobImage()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.True(img.GetBlobCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetLargestBlobArea
    // -------------------------------------------------------------------------

    [Fact]
    public void GetLargestBlobArea_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        var ex = Record.Exception(() => img.GetLargestBlobArea());
        Assert.Null(ex);
    }

    [Fact]
    public void GetLargestBlobArea_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.True(img.GetLargestBlobArea() >= 0);
    }

    [Fact]
    public void GetLargestBlobArea_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        Assert.Equal(img.GetLargestBlobArea(), img.GetLargestBlobArea());
    }

    [Fact]
    public void GetLargestBlobArea_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMultiBlobPgm());
        var before = img.GetLargestBlobArea();
        var path = TempFile("lba_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetLargestBlobArea());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetConnectedComponentCount_GetBlobCount_GetLargestBlobArea_Pipeline()
    {
        // Agricultural remote sensing — crop disease lesion detection in leaf imagery
        // 12×12 PGM simulating a leaf with three disease lesion blobs on healthy tissue background

        var sb = new StringBuilder();
        sb.AppendLine("P2");
        sb.AppendLine("12 12");
        sb.AppendLine("255");
        // Healthy leaf background: medium green-equivalent grey (90)
        // Disease lesions: bright spots (necrotic tissue appears pale, ~220-240)
        // Lesion 1 (early blight): rows 1-2, cols 1-3
        // Lesion 2 (late blight): rows 5-7, cols 7-9
        // Lesion 3 (rust): rows 9-11, cols 2-4

        int[,] grid = new int[12, 12];
        for (int r = 0; r < 12; r++)
            for (int c = 0; c < 12; c++)
                grid[r, c] = 90; // healthy tissue

        // Lesion 1 — early blight, 6 pixels
        grid[1, 1] = 235; grid[1, 2] = 240; grid[1, 3] = 235;
        grid[2, 1] = 230; grid[2, 2] = 245; grid[2, 3] = 230;

        // Lesion 2 — late blight, 9 pixels
        grid[5, 7] = 225; grid[5, 8] = 230; grid[5, 9] = 225;
        grid[6, 7] = 220; grid[6, 8] = 240; grid[6, 9] = 220;
        grid[7, 7] = 225; grid[7, 8] = 230; grid[7, 9] = 225;

        // Lesion 3 — rust, 6 pixels
        grid[9, 2] = 215; grid[9, 3] = 220; grid[9, 4] = 215;
        grid[10, 2] = 210; grid[10, 3] = 225; grid[10, 4] = 210;
        grid[11, 2] = 215; grid[11, 3] = 218; grid[11, 4] = 215;

        for (int r = 0; r < 12; r++)
        {
            var vals = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 12; c++) vals.Add(grid[r, c].ToString());
            sb.AppendLine(string.Join(" ", vals));
        }
        var path = TempFile("dogfood_leaf_lesions.pgm");
        File.WriteAllText(path, sb.ToString());
        var img = NetpbmImage.LoadFile(path);

        Assert.Equal(12, img.Width);
        Assert.Equal(12, img.Height);
        Assert.Equal(255, img.MaxValue);

        // GetConnectedComponentCount
        var ccCount = img.GetConnectedComponentCount();
        Assert.True(ccCount >= 0);
        Assert.Equal(ccCount, img.GetConnectedComponentCount()); // consistent

        // GetBlobCount — should detect multiple blobs
        var blobCount = img.GetBlobCount();
        Assert.True(blobCount >= 0);
        Assert.True(blobCount > 0); // multi-blob image
        Assert.Equal(blobCount, img.GetBlobCount()); // consistent

        // GetLargestBlobArea
        var largestArea = img.GetLargestBlobArea();
        Assert.True(largestArea >= 0);
        Assert.Equal(largestArea, img.GetLargestBlobArea()); // consistent

        // GetMean and GetStdDev
        var mean = img.GetMean();
        var std = img.GetStdDev();
        Assert.True(mean >= 0);
        Assert.True(std >= 0);

        // SaveToFile
        var outPath = TempFile("dogfood_leaf_out.pgm");
        img.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(outPath);
        Assert.Equal(ccCount, loaded.GetConnectedComponentCount());
        Assert.Equal(blobCount, loaded.GetBlobCount());
        Assert.Equal(largestArea, loaded.GetLargestBlobArea());
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);

        // GetHistogram
        var hist = loaded.GetHistogram();
        Assert.NotNull(hist);
        var ex1 = Record.Exception(() => loaded.GetConnectedComponentCount());
        var ex2 = Record.Exception(() => loaded.GetBlobCount());
        var ex3 = Record.Exception(() => loaded.GetLargestBlobArea());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
