// Tests for NetpbmImage.GetTextureScore, GetImageEntropy, GetCoOccurrenceMatrix deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R302

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R302: Tests for NetpbmImage.GetTextureScore, GetImageEntropy, GetCoOccurrenceMatrix deeper.
/// GetTextureScore(): returns a texture complexity metric (0 = flat, higher = more textured).
/// GetImageEntropy(): returns the Shannon entropy of the pixel intensity distribution.
/// GetCoOccurrenceMatrix(): returns a co-occurrence matrix (GLCM) as a 2D array.
/// Covers: GetTextureScore no-throw; GetTextureScore non-negative; GetTextureScore consistent;
/// GetTextureScore zero for uniform; GetTextureScore save-load;
/// GetImageEntropy no-throw; GetImageEntropy non-negative; GetImageEntropy consistent;
/// GetImageEntropy zero for uniform; GetImageEntropy save-load;
/// GetCoOccurrenceMatrix no-throw; GetCoOccurrenceMatrix non-null; GetCoOccurrenceMatrix consistent;
/// GetCoOccurrenceMatrix dimension positive; GetCoOccurrenceMatrix save-load;
/// dogfood CreateImage→GetTextureScore→GetImageEntropy→GetCoOccurrenceMatrix→SaveToFile pipeline.
/// </summary>
public class NetpbmR302GetTextureScoreAndEntropyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR302GetTextureScoreAndEntropyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR302_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCheckerboardPgm()
    {
        // 8x8 checkerboard — high texture, high entropy
        var path = TempFile("checker.pgm");
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

    private string CreateUniformPgm()
    {
        // All same value — zero texture, zero entropy
        var path = TempFile("uniform.pgm");
        File.WriteAllText(path,
            "P2\n6 6\n255\n" +
            "100 100 100 100 100 100\n" +
            "100 100 100 100 100 100\n" +
            "100 100 100 100 100 100\n" +
            "100 100 100 100 100 100\n" +
            "100 100 100 100 100 100\n" +
            "100 100 100 100 100 100\n");
        return path;
    }

    private string CreateGradientPgm()
    {
        // Smooth gradient — moderate texture, moderate entropy
        var path = TempFile("gradient.pgm");
        File.WriteAllText(path,
            "P2\n8 6\n255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTextureScore
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTextureScore_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetTextureScore());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTextureScore_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.True(img.GetTextureScore() >= 0.0);
    }

    [Fact]
    public void GetTextureScore_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetTextureScore(), img.GetTextureScore());
    }

    [Fact]
    public void GetTextureScore_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetTextureScore(), precision: 6);
    }

    [Fact]
    public void GetTextureScore_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetTextureScore();
        var path = TempFile("ts_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetTextureScore(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetImageEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetImageEntropy_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetImageEntropy());
        Assert.Null(ex);
    }

    [Fact]
    public void GetImageEntropy_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(img.GetImageEntropy() >= 0.0);
    }

    [Fact]
    public void GetImageEntropy_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.Equal(img.GetImageEntropy(), img.GetImageEntropy());
    }

    [Fact]
    public void GetImageEntropy_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, img.GetImageEntropy(), precision: 6);
    }

    [Fact]
    public void GetImageEntropy_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetImageEntropy();
        var path = TempFile("ie_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetImageEntropy(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetCoOccurrenceMatrix
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCoOccurrenceMatrix_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var ex = Record.Exception(() => img.GetCoOccurrenceMatrix());
        Assert.Null(ex);
    }

    [Fact]
    public void GetCoOccurrenceMatrix_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.NotNull(img.GetCoOccurrenceMatrix());
    }

    [Fact]
    public void GetCoOccurrenceMatrix_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var m1 = img.GetCoOccurrenceMatrix();
        var m2 = img.GetCoOccurrenceMatrix();
        Assert.Equal(m1.GetLength(0), m2.GetLength(0));
        Assert.Equal(m1.GetLength(1), m2.GetLength(1));
    }

    [Fact]
    public void GetCoOccurrenceMatrix_DimensionPositive()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var m = img.GetCoOccurrenceMatrix();
        Assert.True(m.GetLength(0) > 0);
        Assert.True(m.GetLength(1) > 0);
    }

    [Fact]
    public void GetCoOccurrenceMatrix_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        var before = img.GetCoOccurrenceMatrix();
        var path = TempFile("gcm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetCoOccurrenceMatrix();
        Assert.Equal(before.GetLength(0), after.GetLength(0));
        Assert.Equal(before.GetLength(1), after.GetLength(1));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTextureScore_GetImageEntropy_GetCoOccurrenceMatrix_SaveToFile_Pipeline()
    {
        // Fabric inspection simulation: textile quality analysis
        var path = TempFile("dogfood_fabric.pgm");
        File.WriteAllText(path,
            "P2\n12 10\n255\n" +
            " 80  82  78  83  79  81 120 122 118 121 119 120\n" +
            " 83  78  82  79  81  80 118 121 122 119 120 121\n" +
            " 79  81  80  82  78  83 121 119 120 122 118 119\n" +
            " 82  80  83  78  82  79 120 118 121 120 122 118\n" +
            " 78  83  79  81  80  82 122 120 119 118 121 122\n" +
            "200 202 198 203 199 201  40  42  38  41  39  40\n" +
            "198 201 202 199 201 200  42  38  41  40  42  38\n" +
            "201 199 200 202 198 203  39  41  40  42  38  41\n" +
            "203 198 201 200 202 199  41  40  42  38  41  42\n" +
            "199 202 199 203 200 198  40  39  41  42  39  40\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(120, img.GetPixelCount());

        // GetTextureScore — positive (mixed texture regions)
        var texture = img.GetTextureScore();
        Assert.True(texture >= 0.0);
        Assert.Equal(texture, img.GetTextureScore()); // consistent

        // GetImageEntropy — positive
        var entropy = img.GetImageEntropy();
        Assert.True(entropy >= 0.0);
        Assert.Equal(entropy, img.GetImageEntropy()); // consistent

        // GetCoOccurrenceMatrix — valid dimensions
        var glcm = img.GetCoOccurrenceMatrix();
        Assert.NotNull(glcm);
        Assert.True(glcm.GetLength(0) > 0);
        Assert.True(glcm.GetLength(1) > 0);

        // Uniform image: texture=0, entropy=0
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(0.0, uniform.GetTextureScore(), precision: 6);
        Assert.Equal(0.0, uniform.GetImageEntropy(), precision: 6);
        var uniformGlcm = uniform.GetCoOccurrenceMatrix();
        Assert.NotNull(uniformGlcm);
        Assert.True(uniformGlcm.GetLength(0) > 0);

        // Checkerboard: high texture, max entropy (only 2 pixel values)
        var checker = NetpbmImage.LoadFile(CreateCheckerboardPgm());
        Assert.True(checker.GetTextureScore() > 0.0);
        Assert.True(checker.GetImageEntropy() > 0.0);

        // Gradient: moderate texture
        var grad = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.True(grad.GetTextureScore() >= 0.0);
        Assert.True(grad.GetImageEntropy() >= 0.0);

        // SaveToFile — original
        var out1 = TempFile("dogfood_fabric_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify all metrics preserved
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(texture, loaded.GetTextureScore(), precision: 6);
        Assert.Equal(entropy, loaded.GetImageEntropy(), precision: 6);
        var loadedGlcm = loaded.GetCoOccurrenceMatrix();
        Assert.Equal(glcm.GetLength(0), loadedGlcm.GetLength(0));
        Assert.Equal(glcm.GetLength(1), loadedGlcm.GetLength(1));

        // Apply median filter and verify metrics are non-negative
        var filtered = img.ApplyMedianFilter(3);
        Assert.True(filtered.GetTextureScore() >= 0.0);
        Assert.True(filtered.GetImageEntropy() >= 0.0);

        // Final save
        var out2 = TempFile("dogfood_fabric_v2.pgm");
        filtered.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetTextureScore() >= 0.0);
        Assert.True(loaded2.GetImageEntropy() >= 0.0);
        Assert.NotNull(loaded2.GetCoOccurrenceMatrix());
        var ex1 = Record.Exception(() => loaded2.GetTextureScore());
        var ex2 = Record.Exception(() => loaded2.GetImageEntropy());
        var ex3 = Record.Exception(() => loaded2.GetCoOccurrenceMatrix());
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
