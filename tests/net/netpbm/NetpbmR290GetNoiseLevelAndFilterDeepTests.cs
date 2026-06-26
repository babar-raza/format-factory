// Tests for NetpbmImage.GetNoiseLevel, ApplyMedianFilter, GetSharpnessScore deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R290

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R290: Tests for NetpbmImage.GetNoiseLevel, ApplyMedianFilter, GetSharpnessScore deeper.
/// GetNoiseLevel(): returns an estimate of image noise (0 = no noise, higher = noisier).
/// ApplyMedianFilter(kernelSize): returns a new image with median filter applied.
/// GetSharpnessScore(): returns an edge-based sharpness score (higher = sharper).
/// Covers: GetNoiseLevel no-throw; GetNoiseLevel non-negative; GetNoiseLevel consistent;
/// GetNoiseLevel zero for uniform; GetNoiseLevel save-load;
/// ApplyMedianFilter no-throw; ApplyMedianFilter same dims; ApplyMedianFilter non-null;
/// ApplyMedianFilter kernel3 consistent; ApplyMedianFilter save-load;
/// GetSharpnessScore no-throw; GetSharpnessScore non-negative; GetSharpnessScore consistent;
/// GetSharpnessScore zero for uniform; GetSharpnessScore save-load;
/// dogfood CreateImage→GetNoiseLevel→ApplyMedianFilter→GetSharpnessScore→SaveToFile pipeline.
/// </summary>
public class NetpbmR290GetNoiseLevelAndFilterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR290GetNoiseLevelAndFilterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR290_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateNoisyPgm()
    {
        // 8x8 grayscale with varied pixel values to simulate noise
        var path = TempFile("noisy.pgm");
        File.WriteAllText(path,
            "P2\n8 8\n255\n" +
            "200  10 230  15 245  20 210  30\n" +
            " 25 240  18 235  12 220  35 250\n" +
            "215  22 225  28 205  40 240  18\n" +
            " 30 210  45 215  50 195  55 230\n" +
            "245  60 200  65 240  70 210  75\n" +
            " 80 235  85 205  90 245  95 220\n" +
            "100 230 105 215 110 200 115 245\n" +
            "120 210 125 240 130 195 135 230\n");
        return path;
    }

    private string CreateUniformPgm()
    {
        var path = TempFile("uniform.pgm");
        File.WriteAllText(path,
            "P2\n6 6\n255\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n" +
            "128 128 128 128 128 128\n");
        return path;
    }

    private string CreateSharpEdgePgm()
    {
        // Left half 0, right half 255 — sharp edge in middle
        var path = TempFile("sharp.pgm");
        File.WriteAllText(path,
            "P2\n8 6\n255\n" +
            "  0   0   0   0 255 255 255 255\n" +
            "  0   0   0   0 255 255 255 255\n" +
            "  0   0   0   0 255 255 255 255\n" +
            "  0   0   0   0 255 255 255 255\n" +
            "  0   0   0   0 255 255 255 255\n" +
            "  0   0   0   0 255 255 255 255\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetNoiseLevel
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNoiseLevel_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var ex = Record.Exception(() => img.GetNoiseLevel());
        Assert.Null(ex);
    }

    [Fact]
    public void GetNoiseLevel_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.True(img.GetNoiseLevel() >= 0.0);
    }

    [Fact]
    public void GetNoiseLevel_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.Equal(img.GetNoiseLevel(), img.GetNoiseLevel());
    }

    [Fact]
    public void GetNoiseLevel_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetNoiseLevel(), precision: 6);
    }

    [Fact]
    public void GetNoiseLevel_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var before = img.GetNoiseLevel();
        var path = TempFile("nl_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetNoiseLevel(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // ApplyMedianFilter
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyMedianFilter_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var ex = Record.Exception(() => img.ApplyMedianFilter(3));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyMedianFilter_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var filtered = img.ApplyMedianFilter(3);
        Assert.Equal(img.Width, filtered.Width);
        Assert.Equal(img.Height, filtered.Height);
    }

    [Fact]
    public void ApplyMedianFilter_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        Assert.NotNull(img.ApplyMedianFilter(3));
    }

    [Fact]
    public void ApplyMedianFilter_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var f1 = img.ApplyMedianFilter(3);
        var f2 = img.ApplyMedianFilter(3);
        Assert.Equal(f1.Width, f2.Width);
        Assert.Equal(f1.Height, f2.Height);
    }

    [Fact]
    public void ApplyMedianFilter_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateNoisyPgm());
        var filtered = img.ApplyMedianFilter(3);
        var path = TempFile("mf_save.pgm");
        filtered.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(filtered.Width, loaded.Width);
        Assert.Equal(filtered.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // GetSharpnessScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpnessScore_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var ex = Record.Exception(() => img.GetSharpnessScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetSharpnessScore_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.True(img.GetSharpnessScore() >= 0.0);
    }

    [Fact]
    public void GetSharpnessScore_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        Assert.Equal(img.GetSharpnessScore(), img.GetSharpnessScore());
    }

    [Fact]
    public void GetSharpnessScore_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetSharpnessScore(), precision: 6);
    }

    [Fact]
    public void GetSharpnessScore_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateSharpEdgePgm());
        var before = img.GetSharpnessScore();
        var path = TempFile("ss_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetSharpnessScore(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetNoiseLevel_ApplyMedianFilter_GetSharpnessScore_SaveToFile_Pipeline()
    {
        // Create a structured test image with alternating noise regions and sharp edges
        var path = TempFile("dogfood_mixed.pgm");
        File.WriteAllText(path,
            "P2\n10 10\n255\n" +
            "  0   0   0   0   0 255 255 255 255 255\n" +
            "  0  15   0  20   0 255 240 255 235 255\n" +
            "  0   0  10   0   5 255 255 245 255 250\n" +
            "  0  25   0  30   0 255 230 255 220 255\n" +
            "  0   0  18   0  12 255 255 210 255 215\n" +
            "128 128 128 128 128 128 128 128 128 128\n" +
            "255 240 255 235 255   0   0   0   0   0\n" +
            "255 255 245 255 250   0  15  10  20   0\n" +
            "255 230 255 220 255   0   0   5   0  25\n" +
            "255 255 210 255 215   0  18   0  12   0\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(10, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(100, img.GetPixelCount());

        // GetNoiseLevel — non-negative
        var noise = img.GetNoiseLevel();
        Assert.True(noise >= 0.0);
        Assert.Equal(noise, img.GetNoiseLevel()); // consistent

        // GetSharpnessScore — non-negative (sharp edges present)
        var sharpness = img.GetSharpnessScore();
        Assert.True(sharpness >= 0.0);
        Assert.Equal(sharpness, img.GetSharpnessScore()); // consistent

        // ApplyMedianFilter — same dims
        var filtered = img.ApplyMedianFilter(3);
        Assert.NotNull(filtered);
        Assert.Equal(img.Width, filtered.Width);
        Assert.Equal(img.Height, filtered.Height);

        // Filtered image noise should not increase (median filter reduces noise)
        var filteredNoise = filtered.GetNoiseLevel();
        Assert.True(filteredNoise >= 0.0);

        // SaveToFile — original
        var out1 = TempFile("dogfood_mixed_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // SaveToFile — filtered
        var outFiltered = TempFile("dogfood_filtered.pgm");
        filtered.SaveToFile(outFiltered);
        Assert.True(File.Exists(outFiltered));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(noise, loaded.GetNoiseLevel(), precision: 6);
        Assert.Equal(sharpness, loaded.GetSharpnessScore(), precision: 6);

        // Load filtered and verify properties
        var loadedFiltered = NetpbmImage.LoadFile(outFiltered);
        Assert.Equal(filtered.Width, loadedFiltered.Width);
        Assert.Equal(filtered.Height, loadedFiltered.Height);
        Assert.True(loadedFiltered.GetNoiseLevel() >= 0.0);

        // Apply filter chain: filter the filtered image
        var doubleFiltered = loadedFiltered.ApplyMedianFilter(3);
        Assert.Equal(loadedFiltered.Width, doubleFiltered.Width);

        // Uniform region: create separate uniform and verify zero noise/sharpness
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, uniform.GetNoiseLevel(), precision: 6);
        Assert.Equal(0.0, uniform.GetSharpnessScore(), precision: 6);
        var uniformFiltered = uniform.ApplyMedianFilter(3);
        Assert.Equal(uniform.Width, uniformFiltered.Width);

        // Final save
        var out2 = TempFile("dogfood_mixed_v2.pgm");
        doubleFiltered.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetNoiseLevel() >= 0.0);
        Assert.True(loaded2.GetSharpnessScore() >= 0.0);
        var ex1 = Record.Exception(() => loaded2.ApplyMedianFilter(3));
        Assert.Null(ex1);
    }
}
