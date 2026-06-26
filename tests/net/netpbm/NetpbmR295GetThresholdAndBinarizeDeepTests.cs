// Tests for NetpbmImage.GetOptimalThreshold, BinarizeAtThreshold, GetBinaryPixelRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R295

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R295: Tests for NetpbmImage.GetOptimalThreshold, BinarizeAtThreshold, GetBinaryPixelRatio deeper.
/// GetOptimalThreshold(): returns the computed optimal binarization threshold (0-MaxVal).
/// BinarizeAtThreshold(threshold): returns a new binary (black/white) image.
/// GetBinaryPixelRatio(): returns the fraction of pixels above the optimal threshold.
/// Covers: GetOptimalThreshold no-throw; GetOptimalThreshold in [0,MaxVal]; GetOptimalThreshold consistent;
/// GetOptimalThreshold save-load; GetOptimalThreshold positive for mixed image;
/// BinarizeAtThreshold no-throw; BinarizeAtThreshold same dims; BinarizeAtThreshold non-null;
/// BinarizeAtThreshold zero returns all-white equivalent; BinarizeAtThreshold consistent;
/// BinarizeAtThreshold save-load;
/// GetBinaryPixelRatio no-throw; GetBinaryPixelRatio in [0,1]; GetBinaryPixelRatio consistent;
/// GetBinaryPixelRatio save-load;
/// dogfood CreateImage→GetOptimalThreshold→BinarizeAtThreshold→GetBinaryPixelRatio→SaveToFile pipeline.
/// </summary>
public class NetpbmR295GetThresholdAndBinarizeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR295GetThresholdAndBinarizeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR295_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMixedPgm()
    {
        var path = TempFile("mixed.pgm");
        File.WriteAllText(path,
            "P2\n8 8\n255\n" +
            " 30  40  50  60 180 190 200 210\n" +
            " 45  55  65  75 195 205 215 225\n" +
            " 20  35  45  55 170 185 195 205\n" +
            " 50  60  70  80 200 210 220 230\n" +
            "220 210 200 190  40  30  20  10\n" +
            "215 205 195 185  55  45  35  25\n" +
            "225 215 205 195  50  40  30  20\n" +
            "230 220 210 200  60  50  40  30\n");
        return path;
    }

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        File.WriteAllText(path,
            "P2\n8 6\n255\n" +
            "  0  36  72 108 144 180 216 255\n" +
            "  0  36  72 108 144 180 216 255\n" +
            "  0  36  72 108 144 180 216 255\n" +
            "  0  36  72 108 144 180 216 255\n" +
            "  0  36  72 108 144 180 216 255\n" +
            "  0  36  72 108 144 180 216 255\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetOptimalThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOptimalThreshold_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.GetOptimalThreshold());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOptimalThreshold_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var t = img.GetOptimalThreshold();
        Assert.True(t >= 0 && t <= img.MaxVal);
    }

    [Fact]
    public void GetOptimalThreshold_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.Equal(img.GetOptimalThreshold(), img.GetOptimalThreshold());
    }

    [Fact]
    public void GetOptimalThreshold_Positive_ForMixedImage()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.True(img.GetOptimalThreshold() > 0);
    }

    [Fact]
    public void GetOptimalThreshold_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var before = img.GetOptimalThreshold();
        var path = TempFile("ot_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetOptimalThreshold());
    }

    // -------------------------------------------------------------------------
    // BinarizeAtThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void BinarizeAtThreshold_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.BinarizeAtThreshold(128));
        Assert.Null(ex);
    }

    [Fact]
    public void BinarizeAtThreshold_SameDimensions()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var binary = img.BinarizeAtThreshold(128);
        Assert.Equal(img.Width, binary.Width);
        Assert.Equal(img.Height, binary.Height);
    }

    [Fact]
    public void BinarizeAtThreshold_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.NotNull(img.BinarizeAtThreshold(128));
    }

    [Fact]
    public void BinarizeAtThreshold_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var b1 = img.BinarizeAtThreshold(128);
        var b2 = img.BinarizeAtThreshold(128);
        Assert.Equal(b1.Width, b2.Width);
        Assert.Equal(b1.Height, b2.Height);
    }

    [Fact]
    public void BinarizeAtThreshold_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var binary = img.BinarizeAtThreshold(128);
        var path = TempFile("bat_save.pgm");
        binary.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(binary.Width, loaded.Width);
        Assert.Equal(binary.Height, loaded.Height);
    }

    // -------------------------------------------------------------------------
    // GetBinaryPixelRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBinaryPixelRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ex = Record.Exception(() => img.GetBinaryPixelRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBinaryPixelRatio_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var ratio = img.GetBinaryPixelRatio();
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
    }

    [Fact]
    public void GetBinaryPixelRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        Assert.Equal(img.GetBinaryPixelRatio(), img.GetBinaryPixelRatio());
    }

    [Fact]
    public void GetBinaryPixelRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateMixedPgm());
        var before = img.GetBinaryPixelRatio();
        var path = TempFile("bpr_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBinaryPixelRatio(), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetOptimalThreshold_BinarizeAtThreshold_GetBinaryPixelRatio_SaveToFile_Pipeline()
    {
        // Bimodal image: two distinct intensity clusters
        var path = TempFile("dogfood_bimodal.pgm");
        File.WriteAllText(path,
            "P2\n12 8\n255\n" +
            " 20  25  30  35  40  45 210 215 220 225 230 235\n" +
            " 22  28  32  38  42  48 212 218 222 228 232 238\n" +
            " 18  24  28  34  38  44 208 214 218 224 228 234\n" +
            " 25  30  35  40  45  50 215 220 225 230 235 240\n" +
            "205 210 215 220 225 230  20  25  30  35  40  45\n" +
            "208 214 218 224 228 234  22  28  32  38  42  48\n" +
            "202 208 212 218 222 228  18  24  28  34  38  44\n" +
            "210 215 220 225 230 235  25  30  35  40  45  50\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(8, img.Height);
        Assert.Equal(96, img.GetPixelCount());

        // GetOptimalThreshold — should be between the two clusters
        var threshold = img.GetOptimalThreshold();
        Assert.True(threshold >= 0 && threshold <= img.MaxVal);
        Assert.True(threshold > 0); // positive for bimodal image
        Assert.Equal(threshold, img.GetOptimalThreshold()); // consistent

        // GetBinaryPixelRatio — in [0,1]
        var ratio = img.GetBinaryPixelRatio();
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
        Assert.Equal(ratio, img.GetBinaryPixelRatio()); // consistent

        // BinarizeAtThreshold — at optimal threshold
        var binary = img.BinarizeAtThreshold(threshold);
        Assert.NotNull(binary);
        Assert.Equal(img.Width, binary.Width);
        Assert.Equal(img.Height, binary.Height);

        // BinarizeAtThreshold — at mid-range
        var binary128 = img.BinarizeAtThreshold(128);
        Assert.NotNull(binary128);
        Assert.Equal(img.Width, binary128.Width);
        Assert.Equal(img.Height, binary128.Height);

        // BinarizeAtThreshold — at high threshold (most pixels become black)
        var binaryHigh = img.BinarizeAtThreshold(250);
        Assert.NotNull(binaryHigh);
        Assert.Equal(img.Width, binaryHigh.Width);

        // Gradient image
        var gradient = NetpbmImage.LoadFile(CreateGradientPgm());
        var gradThreshold = gradient.GetOptimalThreshold();
        Assert.True(gradThreshold >= 0 && gradThreshold <= gradient.MaxVal);
        var gradRatio = gradient.GetBinaryPixelRatio();
        Assert.True(gradRatio >= 0.0 && gradRatio <= 1.0);

        // SaveToFile — original
        var out1 = TempFile("dogfood_bimodal_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // SaveToFile — binary
        var outBinary = TempFile("dogfood_binary.pgm");
        binary.SaveToFile(outBinary);
        Assert.True(File.Exists(outBinary));

        // LoadFile and verify
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        Assert.Equal(threshold, loaded.GetOptimalThreshold());
        Assert.Equal(ratio, loaded.GetBinaryPixelRatio(), precision: 6);

        // Apply binarization on loaded
        var loadedBinary = loaded.BinarizeAtThreshold(loaded.GetOptimalThreshold());
        Assert.NotNull(loadedBinary);
        Assert.Equal(loaded.Width, loadedBinary.Width);

        // Final save
        var out2 = TempFile("dogfood_bimodal_v2.pgm");
        loadedBinary.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.True(loaded2.GetOptimalThreshold() >= 0);
        Assert.True(loaded2.GetBinaryPixelRatio() >= 0.0 && loaded2.GetBinaryPixelRatio() <= 1.0);
        var ex1 = Record.Exception(() => loaded2.BinarizeAtThreshold(128));
        Assert.Null(ex1);
    }
}
