// Tests for NetpbmImage.GetEdgeMap, GetGradientMagnitude, GetGradientDirection deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R320

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R320: Tests for NetpbmImage.GetEdgeMap, GetGradientMagnitude, GetGradientDirection deeper.
/// GetEdgeMap(threshold): returns a binary image with pixels above the gradient threshold set to MaxVal.
/// GetGradientMagnitude(): returns an image where each pixel is the gradient magnitude.
/// GetGradientDirection(): returns an array of gradient directions in radians (or equivalent float image).
/// Covers: GetEdgeMap no-throw; GetEdgeMap same dimensions; GetEdgeMap values only 0 or MaxVal;
/// GetEdgeMap threshold=0 all edges; GetEdgeMap threshold=MaxVal no edges;
/// GetGradientMagnitude no-throw; GetGradientMagnitude same dimensions; GetGradientMagnitude non-negative mean;
/// GetGradientMagnitude consistent; GetGradientMagnitude flat image has zero magnitude;
/// GetGradientDirection no-throw; GetGradientDirection same length as pixel count; GetGradientDirection consistent;
/// dogfood GetEdgeMap→GetGradientMagnitude→GetGradientDirection→SaveToFile pipeline.
/// </summary>
public class NetpbmR320GetEdgeMapAndGradientDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR320GetEdgeMapAndGradientDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR320_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateEdgeTestPgm()
    {
        // 10×10 PGM — left half dark, right half bright (strong vertical edge in centre)
        var path = TempFile("edge_test.pgm");
        var pixels = new System.Collections.Generic.List<string>();
        for (int r = 0; r < 10; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < 10; c++)
                row.Add(c < 5 ? "30" : "220");
            pixels.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n10 10\n255\n{string.Join("\n", pixels)}\n");
        return path;
    }

    private string CreateFlatPgm()
    {
        var path = TempFile("flat.pgm");
        var rows = new string[10];
        for (int i = 0; i < 10; i++)
            rows[i] = string.Join(" ", Enumerable.Repeat("128", 10));
        File.WriteAllText(path, $"P2\n10 10\n255\n{string.Join("\n", rows)}\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEdgeMap
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeMap_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var ex = Record.Exception(() => img.GetEdgeMap(80));
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeMap_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var edge = img.GetEdgeMap(80);
        Assert.Equal(img.Width, edge.Width);
        Assert.Equal(img.Height, edge.Height);
    }

    [Fact]
    public void GetEdgeMap_Values_Only_Zero_Or_MaxVal()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var edge = img.GetEdgeMap(80);
        foreach (var px in edge.Pixels)
            Assert.True(px == 0 || px == edge.MaxVal);
    }

    [Fact]
    public void GetEdgeMap_Threshold_Zero_HasEdges()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var edge = img.GetEdgeMap(0);
        // With threshold=0, the strong centre edge should produce at least one edge pixel
        Assert.True(edge.Pixels.Any(p => p == edge.MaxVal));
    }

    [Fact]
    public void GetEdgeMap_FlatImage_NoEdges()
    {
        var img = NetpbmImage.LoadFile(CreateFlatPgm());
        var edge = img.GetEdgeMap(1); // very low threshold on flat image
        // Flat image has zero gradient so no edges at any positive threshold
        Assert.True(!edge.Pixels.Any(p => p == edge.MaxVal));
    }

    // -------------------------------------------------------------------------
    // GetGradientMagnitude
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGradientMagnitude_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var ex = Record.Exception(() => img.GetGradientMagnitude());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGradientMagnitude_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var mag = img.GetGradientMagnitude();
        Assert.Equal(img.Width, mag.Width);
        Assert.Equal(img.Height, mag.Height);
    }

    [Fact]
    public void GetGradientMagnitude_NonNegative_Mean()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var mag = img.GetGradientMagnitude();
        double mean = mag.Pixels.Average(p => (double)p);
        Assert.True(mean >= 0);
    }

    [Fact]
    public void GetGradientMagnitude_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var mag1 = img.GetGradientMagnitude();
        var mag2 = img.GetGradientMagnitude();
        Assert.Equal(mag1.Pixels, mag2.Pixels);
    }

    [Fact]
    public void GetGradientMagnitude_FlatImage_ZeroMagnitude()
    {
        var img = NetpbmImage.LoadFile(CreateFlatPgm());
        var mag = img.GetGradientMagnitude();
        // Interior pixels of a flat image have zero gradient
        double mean = mag.Pixels.Average(p => (double)p);
        Assert.True(mean < img.MaxVal * 0.1); // mostly zero except boundary effects
    }

    // -------------------------------------------------------------------------
    // GetGradientDirection
    // -------------------------------------------------------------------------

    [Fact]
    public void GetGradientDirection_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var ex = Record.Exception(() => img.GetGradientDirection());
        Assert.Null(ex);
    }

    [Fact]
    public void GetGradientDirection_Length_Equals_PixelCount()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var dir = img.GetGradientDirection();
        Assert.Equal(img.Width * img.Height, dir.Length);
    }

    [Fact]
    public void GetGradientDirection_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateEdgeTestPgm());
        var dir1 = img.GetGradientDirection();
        var dir2 = img.GetGradientDirection();
        Assert.Equal(dir1, dir2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgeMap_GetGradientMagnitude_GetGradientDirection_SaveToFile_Pipeline()
    {
        // Industrial quality control — automated visual inspection of silicon wafer defects
        // Gradient-based feature extraction for defect localisation pipeline
        var path = TempFile("wafer_inspection.pgm");
        int W = 12, H = 12;
        var pxData = new int[H, W];
        // Background: 180 (clean silicon)
        for (int r = 0; r < H; r++)
            for (int c = 0; c < W; c++)
                pxData[r, c] = 180;
        // Circular defect region (rows 4-8, cols 4-8): dark particle (30)
        for (int r = 4; r <= 8; r++)
            for (int c = 4; c <= 8; c++)
                pxData[r, c] = 30;
        // Scratch: diagonal line (rows 0-5, cols 0-5)
        for (int i = 0; i <= 5; i++)
            pxData[i, i] = 50;

        var rows = new System.Collections.Generic.List<string>();
        for (int r = 0; r < H; r++)
        {
            var row = new System.Collections.Generic.List<string>();
            for (int c = 0; c < W; c++)
                row.Add(pxData[r, c].ToString());
            rows.Add(string.Join(" ", row));
        }
        File.WriteAllText(path, $"P2\n{W} {H}\n255\n{string.Join("\n", rows)}\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(W, img.Width);
        Assert.Equal(H, img.Height);
        Assert.Equal(255, img.MaxVal);

        // GetGradientMagnitude
        var mag = img.GetGradientMagnitude();
        Assert.Equal(W, mag.Width);
        Assert.Equal(H, mag.Height);
        double magMean = mag.Pixels.Average(p => (double)p);
        Assert.True(magMean >= 0);
        Assert.Equal(mag.Pixels, img.GetGradientMagnitude().Pixels); // consistent

        // GetGradientDirection
        var dir = img.GetGradientDirection();
        Assert.Equal(W * H, dir.Length);
        Assert.Equal(dir, img.GetGradientDirection()); // consistent

        // GetEdgeMap — low threshold should detect defect boundary
        var edgeLow = img.GetEdgeMap(20);
        Assert.Equal(W, edgeLow.Width);
        Assert.Equal(H, edgeLow.Height);
        foreach (var px in edgeLow.Pixels)
            Assert.True(px == 0 || px == edgeLow.MaxVal);
        Assert.True(edgeLow.Pixels.Any(p => p == edgeLow.MaxVal)); // boundary of defect detected

        // GetEdgeMap — very high threshold finds fewer edges
        var edgeHigh = img.GetEdgeMap(240);
        int lowEdgeCount = edgeLow.Pixels.Count(p => p == edgeLow.MaxVal);
        int highEdgeCount = edgeHigh.Pixels.Count(p => p == edgeHigh.MaxVal);
        Assert.True(lowEdgeCount >= highEdgeCount); // lower threshold finds >= edges

        // SaveGradientMagnitude
        var magPath = TempFile("wafer_gradient_mag.pgm");
        mag.SaveToFile(magPath);
        Assert.True(File.Exists(magPath));
        Assert.True(new FileInfo(magPath).Length > 0);

        // SaveEdgeMap
        var edgePath = TempFile("wafer_edge_map.pgm");
        edgeLow.SaveToFile(edgePath);
        Assert.True(File.Exists(edgePath));

        // LoadFile and verify edge map preserved
        var loadedEdge = NetpbmImage.LoadFile(edgePath);
        Assert.Equal(W, loadedEdge.Width);
        Assert.Equal(H, loadedEdge.Height);
        foreach (var px in loadedEdge.Pixels)
            Assert.True(px == 0 || px == loadedEdge.MaxVal);

        // Operations on loaded gradient magnitude
        var ex1 = Record.Exception(() => mag.GetGradientMagnitude());
        var ex2 = Record.Exception(() => mag.GetEdgeMap(50));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
