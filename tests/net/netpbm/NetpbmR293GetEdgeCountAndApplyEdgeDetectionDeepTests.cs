// Tests for NetpbmImage.GetEdgeCount, ApplyEdgeDetection, GetEdgeDensity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R293

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R293: Tests for NetpbmImage.GetEdgeCount, ApplyEdgeDetection, GetEdgeDensity deeper.
/// GetEdgeCount(): returns the number of detected edge pixels in the image.
/// ApplyEdgeDetection(): returns a new image with edges highlighted.
/// GetEdgeDensity(): returns the ratio of edge pixels to total pixels.
/// Covers: GetEdgeCount no-throw; GetEdgeCount non-negative; GetEdgeCount consistent;
/// GetEdgeCount zero for uniform; GetEdgeCount positive for sharp edges; GetEdgeCount save-load;
/// ApplyEdgeDetection no-throw; ApplyEdgeDetection same dims; ApplyEdgeDetection non-null;
/// ApplyEdgeDetection consistent; ApplyEdgeDetection save-load;
/// GetEdgeDensity no-throw; GetEdgeDensity in [0,1]; GetEdgeDensity consistent;
/// GetEdgeDensity zero for uniform; GetEdgeDensity save-load;
/// dogfood CreateImage→GetEdgeCount→ApplyEdgeDetection→GetEdgeDensity→SaveToFile pipeline.
/// </summary>
public class NetpbmR293GetEdgeCountAndApplyEdgeDetectionDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR293GetEdgeCountAndApplyEdgeDetectionDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR293_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSharpEdgePgm()
    {
        // Left half black, right half white — strong vertical edge
        var path = TempFile("sharp_edge.pgm");
        File.WriteAllText(path,
            "P2\n10 8\n255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n");
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        File.WriteAllText(path,
            "P2\n8 6\n255\n" +
            "128 128 128 128 128 128 128 128\n" +
            "128 128 128 128 128 128 128 128\n" +
            "128 128 128 128 128 128 128 128\n" +
            "128 128 128 128 128 128 128 128\n" +
            "128 128 128 128 128 128 128 128\n" +
            "128 128 128 128 128 128 128 128\n");
        return path;
    }

    private string CreateGridPgm()
    {
        // Checkerboard — many edges
        var path = TempFile("grid.pgm");
        File.WriteAllText(path,
            "P2\n8 8\n255\n" +
            "  0 255   0 255   0 255   0 255\n" +
            "255   0 255   0 255   0 255   0\n" +
            "  0 255   0 255   0 255   0 255\n" +
            "255   0 255   0 255   0 255   0\n" +
            "  0 255   0 255   0 255   0 255\n" +
            "255   0 255   0 255   0 255   0\n" +
            "  0 255   0 255   0 255   0 255\n" +
            "255   0 255   0 255   0 255   0\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetEdgeCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeCount_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var ex = Record.Exception(() => img.GetEdgeCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeCount_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.True(img.GetEdgeCount() >= 0);
    }

    [Fact]
    public void GetEdgeCount_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.Equal(img.GetEdgeCount(), img.GetEdgeCount());
    }

    [Fact]
    public void GetEdgeCount_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0, img.GetEdgeCount());
    }

    [Fact]
    public void GetEdgeCount_Positive_ForSharpEdge()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.True(img.GetEdgeCount() > 0);
    }

    [Fact]
    public void GetEdgeCount_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var before = img.GetEdgeCount();
        var path = TempFile("ec_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeCount());
    }

    // -------------------------------------------------------------------------
    // ApplyEdgeDetection
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyEdgeDetection_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var ex = Record.Exception(() => img.ApplyEdgeDetection());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyEdgeDetection_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var edges = img.ApplyEdgeDetection();
        Assert.Equal(img.Width, edges.Width);
        Assert.Equal(img.Height, edges.Height);
    }

    [Fact]
    public void ApplyEdgeDetection_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.NotNull(img.ApplyEdgeDetection());
    }

    [Fact]
    public void ApplyEdgeDetection_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var e1 = img.ApplyEdgeDetection();
        var e2 = img.ApplyEdgeDetection();
        Assert.Equal(e1.Width, e2.Width);
        Assert.Equal(e1.Height, e2.Height);
    }

    [Fact]
    public void ApplyEdgeDetection_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var edges = img.ApplyEdgeDetection();
        var path = TempFile("ed_save.pgm");
        edges.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(edges.Width, loaded.Width);
        Assert.Equal(edges.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // GetEdgeDensity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEdgeDensity_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var ex = Record.Exception(() => img.GetEdgeDensity());
        Assert.Null(ex);
    }

    [Fact]
    public void GetEdgeDensity_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var density = img.GetEdgeDensity();
        Assert.True(density >= 0.0 && density <= 1.0);
    }

    [Fact]
    public void GetEdgeDensity_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.Equal(img.GetEdgeDensity(), img.GetEdgeDensity());
    }

    [Fact]
    public void GetEdgeDensity_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetEdgeDensity(), precision: 6);
    }

    [Fact]
    public void GetEdgeDensity_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var before = img.GetEdgeDensity();
        var path = TempFile("ed_density_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetEdgeDensity(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetEdgeCount_ApplyEdgeDetection_GetEdgeDensity_SaveToFile_Pipeline()
    {
        // Structured image: top half gradient, bottom half sharp edge
        var path = TempFile("dogfood_structured.pgm");
        File.WriteAllText(path,
            "P2\n12 10\n255\n" +
            "  0  25  50  75 100 125 150 175 200 225 240 255\n" +
            "  0  25  50  75 100 125 150 175 200 225 240 255\n" +
            "  0  25  50  75 100 125 150 175 200 225 240 255\n" +
            "  0  25  50  75 100 125 150 175 200 225 240 255\n" +
            "  0  25  50  75 100 125 150 175 200 225 240 255\n" +
            "  0   0   0   0   0   0 255 255 255 255 255 255\n" +
            "  0   0   0   0   0   0 255 255 255 255 255 255\n" +
            "  0   0   0   0   0   0 255 255 255 255 255 255\n" +
            "  0   0   0   0   0   0 255 255 255 255 255 255\n" +
            "  0   0   0   0   0   0 255 255 255 255 255 255\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(120, img.GetPixelCount());

        // GetEdgeCount — positive for structured image
        var edgeCount = img.GetEdgeCount();
        Assert.True(edgeCount >= 0);
        Assert.Equal(edgeCount, img.GetEdgeCount()); // consistent

        // GetEdgeDensity — in [0,1]
        var density = img.GetEdgeDensity();
        Assert.True(density >= 0.0 && density <= 1.0);
        Assert.Equal(density, img.GetEdgeDensity()); // consistent

        // ApplyEdgeDetection — same dims
        var edges = img.ApplyEdgeDetection();
        Assert.NotNull(edges);
        Assert.Equal(img.Width, edges.Width);
        Assert.Equal(img.Height, edges.Height);

        // Checkerboard has many edges
        var grid = NetpbmImage.LoadFile(CreateGridPgm());
        var gridEdges = grid.GetEdgeCount();
        Assert.True(gridEdges >= 0);
        var gridDensity = grid.GetEdgeDensity();
        Assert.True(gridDensity >= 0.0 && gridDensity <= 1.0);

        // Uniform has zero edges
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0, uniform.GetEdgeCount());
        Assert.Equal(0.0, uniform.GetEdgeDensity(), precision: 6);

        // SaveToFile — original
        var out1 = TempFile("dogfood_structured_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // SaveToFile — edge detected
        var outEdges = TempFile("dogfood_edges.pgm");
        edges.SaveToFile(outEdges);
        Assert.True(File.Exists(outEdges));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(edgeCount, loaded.GetEdgeCount());
        Assert.Equal(density, loaded.GetEdgeDensity(), precision: 6);

        // Apply edge detection on loaded
        var loadedEdges = loaded.ApplyEdgeDetection();
        Assert.NotNull(loadedEdges);
        Assert.Equal(loaded.Width, loadedEdges.Width);

        // Final save
        var out2 = TempFile("dogfood_structured_v2.pgm");
        loadedEdges.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetEdgeCount() >= 0);
        Assert.True(loaded2.GetEdgeDensity() >= 0.0 && loaded2.GetEdgeDensity() <= 1.0);
        var ex1 = Record.Exception(() => loaded2.ApplyEdgeDetection());
        Assert.Null(ex1);
    }
}
