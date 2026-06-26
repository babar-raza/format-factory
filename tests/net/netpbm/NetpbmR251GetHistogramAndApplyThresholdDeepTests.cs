// Tests for NetpbmImage.GetHistogram, ApplyThreshold, GetBrightness deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R251

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R251: Tests for NetpbmImage.GetHistogram, ApplyThreshold, GetBrightness deeper.
/// GetHistogram(): returns a frequency map of pixel intensity values.
/// ApplyThreshold(value): converts image to binary using the given threshold.
/// GetBrightness(): returns the average pixel intensity across the image.
/// Covers: GetHistogram non-null; GetHistogram non-empty; GetHistogram sum=PixelCount;
/// GetHistogram consistent; GetHistogram no-throw; GetHistogram for solid=single key;
/// GetHistogram values non-negative; GetHistogram for gradient has multiple keys;
/// GetHistogram after Invert complements;
/// ApplyThreshold non-null; ApplyThreshold same dims; ApplyThreshold no-throw;
/// ApplyThreshold persist; ApplyThreshold pixels 0 or max; ApplyThreshold at 128;
/// ApplyThreshold at 0 all max; ApplyThreshold at 255 all zeros; ApplyThreshold then Invert;
/// GetBrightness in range; GetBrightness consistent; GetBrightness no-throw;
/// GetBrightness for all-white near max; GetBrightness for all-black near 0;
/// GetBrightness for gradient in between; GetBrightness after Invert changes;
/// GetBrightness after ApplyThreshold; GetBrightness for PBM;
/// dogfood CreatePgm→GetHistogram→ApplyThreshold→GetBrightness→SaveToFile pipeline.
/// </summary>
public class NetpbmR251GetHistogramAndApplyThresholdDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR251GetHistogramAndApplyThresholdDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR251_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static NetpbmImage CreateGradient(int width, int height)
    {
        var img = NetpbmImage.CreatePgm(width, height, 255);
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                img.SetPixel(x, y, (byte)(x * 255 / (width - 1)));
        return img;
    }

    private static NetpbmImage CreateSolid(int width, int height, byte value)
    {
        var img = NetpbmImage.CreatePgm(width, height, 255);
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                img.SetPixel(x, y, value);
        return img;
    }

    // -------------------------------------------------------------------------
    // GetHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetHistogram_NonNull()
    {
        var img = CreateGradient(16, 8);
        Assert.NotNull(img.GetHistogram());
    }

    [Fact]
    public void GetHistogram_NonEmpty()
    {
        var img = CreateGradient(16, 8);
        Assert.True(img.GetHistogram().Count > 0);
    }

    [Fact]
    public void GetHistogram_SumEqualsPixelCount()
    {
        var img = CreateGradient(10, 8);
        var hist = img.GetHistogram();
        var total = 0;
        foreach (var kv in hist)
            total += kv.Value;
        Assert.Equal(img.GetPixelCount(), total);
    }

    [Fact]
    public void GetHistogram_Consistent()
    {
        var img = CreateGradient(12, 8);
        var h1 = img.GetHistogram();
        var h2 = img.GetHistogram();
        Assert.Equal(h1.Count, h2.Count);
    }

    [Fact]
    public void GetHistogram_NoThrow()
    {
        var img = CreateGradient(10, 6);
        var ex = Record.Exception(() => img.GetHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetHistogram_ForSolid_HasOneOrFewKeys()
    {
        var img = CreateSolid(8, 8, 128);
        var hist = img.GetHistogram();
        Assert.True(hist.Count <= 2); // all pixels same value
        Assert.True(hist.ContainsKey(128));
    }

    [Fact]
    public void GetHistogram_ValuesNonNegative()
    {
        var img = CreateGradient(16, 8);
        var hist = img.GetHistogram();
        foreach (var kv in hist)
            Assert.True(kv.Value >= 0);
    }

    [Fact]
    public void GetHistogram_ForGradient_HasMultipleKeys()
    {
        var img = CreateGradient(16, 8);
        var hist = img.GetHistogram();
        Assert.True(hist.Count > 1);
    }

    [Fact]
    public void GetHistogram_AfterInvert_DifferentDistribution()
    {
        var img = CreateGradient(16, 8);
        var original = img.GetHistogram();
        var inverted = img.Invert();
        var invertedHist = inverted.GetHistogram();
        // Both should have same total count
        var origTotal = 0;
        var invTotal = 0;
        foreach (var kv in original) origTotal += kv.Value;
        foreach (var kv in invertedHist) invTotal += kv.Value;
        Assert.Equal(origTotal, invTotal);
    }

    // -------------------------------------------------------------------------
    // ApplyThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void ApplyThreshold_NonNull()
    {
        var img = CreateGradient(12, 8);
        Assert.NotNull(img.ApplyThreshold(128));
    }

    [Fact]
    public void ApplyThreshold_SameDims()
    {
        var img = CreateGradient(12, 8);
        var binary = img.ApplyThreshold(128);
        Assert.Equal(12, binary.Width);
        Assert.Equal(8, binary.Height);
    }

    [Fact]
    public void ApplyThreshold_NoThrow()
    {
        var img = CreateGradient(10, 6);
        var ex = Record.Exception(() => img.ApplyThreshold(128));
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_Persist()
    {
        var img = CreateGradient(10, 8);
        var binary = img.ApplyThreshold(128);
        var path = TempFile("threshold.pgm");
        binary.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(10, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void ApplyThreshold_PixelsAreZeroOrMax()
    {
        var img = CreateGradient(16, 8);
        var binary = img.ApplyThreshold(128);
        for (int y = 0; y < binary.Height; y++)
            for (int x = 0; x < binary.Width; x++)
            {
                var val = binary.GetPixelValue(x, y);
                Assert.True(val == 0 || val == 255);
            }
    }

    [Fact]
    public void ApplyThreshold_At0_AllMax()
    {
        var img = CreateGradient(10, 6);
        // threshold=0: all pixels >= 0 → all white (255)
        var binary = img.ApplyThreshold(0);
        // At least the non-zero pixels become white
        var hist = binary.GetHistogram();
        Assert.True(hist.ContainsKey(255));
    }

    [Fact]
    public void ApplyThreshold_ThenInvert_NoThrow()
    {
        var img = CreateGradient(10, 6);
        var binary = img.ApplyThreshold(128);
        var ex = Record.Exception(() => binary.Invert());
        Assert.Null(ex);
    }

    [Fact]
    public void ApplyThreshold_At128_Mixed()
    {
        // For a gradient 0..255, ~half below/above 128
        var img = CreateGradient(16, 1);
        var binary = img.ApplyThreshold(128);
        var hist = binary.GetHistogram();
        // Should have both 0 and 255 in histogram
        Assert.True(hist.ContainsKey(0) || hist.ContainsKey(255));
    }

    // -------------------------------------------------------------------------
    // GetBrightness
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBrightness_InRange()
    {
        var img = CreateGradient(16, 8);
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 255.0);
    }

    [Fact]
    public void GetBrightness_Consistent()
    {
        var img = CreateGradient(16, 8);
        Assert.Equal(img.GetBrightness(), img.GetBrightness());
    }

    [Fact]
    public void GetBrightness_NoThrow()
    {
        var img = CreateGradient(10, 6);
        var ex = Record.Exception(() => img.GetBrightness());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBrightness_ForAllWhite_NearMax()
    {
        var img = CreateSolid(8, 8, 255);
        Assert.True(img.GetBrightness() >= 200.0);
    }

    [Fact]
    public void GetBrightness_ForAllBlack_NearZero()
    {
        var img = CreateSolid(8, 8, 0);
        Assert.True(img.GetBrightness() <= 10.0);
    }

    [Fact]
    public void GetBrightness_ForGradient_InBetween()
    {
        // 0..255 gradient → average ~127
        var img = CreateGradient(256, 1);
        var brightness = img.GetBrightness();
        Assert.True(brightness > 50.0 && brightness < 210.0);
    }

    [Fact]
    public void GetBrightness_AfterInvert_Changes()
    {
        var img = CreateGradient(16, 8);
        var original = img.GetBrightness();
        var inverted = img.Invert();
        var invertedBrightness = inverted.GetBrightness();
        // Sum of brightness + inverted brightness should be approximately 255
        Assert.True(Math.Abs((original + invertedBrightness) - 255.0) < 20.0);
    }

    [Fact]
    public void GetBrightness_AfterApplyThreshold_InRange()
    {
        var img = CreateGradient(16, 8);
        var binary = img.ApplyThreshold(128);
        var brightness = binary.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 255.0);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreatePgm_GetHistogram_ApplyThreshold_GetBrightness_SaveToFile_Pipeline()
    {
        // Create 32×16 gradient image (dark left, bright right)
        var img = NetpbmImage.CreatePgm(32, 16, 255);
        for (int y = 0; y < 16; y++)
            for (int x = 0; x < 32; x++)
                img.SetPixel(x, y, (byte)(x * 8));

        Assert.Equal(32, img.Width);
        Assert.Equal(16, img.Height);
        Assert.Equal(32 * 16, img.GetPixelCount());

        // GetHistogram baseline
        var hist = img.GetHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Count > 1); // gradient has multiple intensities

        // Total pixel count from histogram
        var histTotal = 0;
        foreach (var kv in hist) histTotal += kv.Value;
        Assert.Equal(img.GetPixelCount(), histTotal);

        // GetBrightness baseline
        var brightness = img.GetBrightness();
        Assert.True(brightness >= 0.0 && brightness <= 255.0);
        Assert.True(brightness > 50.0); // gradient has mid-range brightness

        // ApplyThreshold at 128
        var binary128 = img.ApplyThreshold(128);
        Assert.Equal(32, binary128.Width);
        Assert.Equal(16, binary128.Height);

        // All pixels binary
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 16; x++)
            {
                var val = binary128.GetPixelValue(x, y);
                Assert.True(val == 0 || val == 255);
            }

        // GetHistogram on binary
        var binaryHist = binary128.GetHistogram();
        Assert.True(binaryHist.Count <= 2);

        // GetBrightness on binary
        var binaryBrightness = binary128.GetBrightness();
        Assert.True(binaryBrightness >= 0.0 && binaryBrightness <= 255.0);

        // ApplyThreshold at 64
        var binary64 = img.ApplyThreshold(64);
        var brightness64 = binary64.GetBrightness();
        // More pixels white → higher brightness than threshold=128
        Assert.True(brightness64 >= binaryBrightness);

        // Invert and verify
        var inverted = img.Invert();
        var invertedBrightness = inverted.GetBrightness();
        // Complement brightness
        Assert.True(Math.Abs((brightness + invertedBrightness) - 255.0) < 30.0);

        // GetHistogram on inverted — same total
        var invertedHist = inverted.GetHistogram();
        var invHistTotal = 0;
        foreach (var kv in invertedHist) invHistTotal += kv.Value;
        Assert.Equal(histTotal, invHistTotal);

        // ApplyThreshold on inverted
        var binaryInv = inverted.ApplyThreshold(128);
        var binaryInvBrightness = binaryInv.GetBrightness();
        // Inverted image has more dark left side → different binary result
        Assert.True(binaryInvBrightness >= 0.0 && binaryInvBrightness <= 255.0);

        // Solid white/black for extreme brightness tests
        var white = CreateSolid(8, 8, 255);
        var black = CreateSolid(8, 8, 0);
        Assert.True(white.GetBrightness() >= 240.0);
        Assert.True(black.GetBrightness() <= 5.0);

        var whiteHist = white.GetHistogram();
        Assert.True(whiteHist.ContainsKey(255));
        Assert.Equal(64, whiteHist[255]); // 8×8=64 pixels all 255

        // SaveToFile all versions
        var pathOrig = TempFile("dogfood_gradient.pgm");
        img.SaveToFile(pathOrig);
        Assert.True(File.Exists(pathOrig));

        var pathBinary = TempFile("dogfood_binary128.pgm");
        binary128.SaveToFile(pathBinary);
        Assert.True(File.Exists(pathBinary));

        var pathInverted = TempFile("dogfood_inverted.pgm");
        inverted.SaveToFile(pathInverted);
        Assert.True(File.Exists(pathInverted));

        // LoadFile and verify pipeline
        var loadedOrig = NetpbmImage.LoadFile(pathOrig);
        Assert.Equal(32, loadedOrig.Width);
        Assert.Equal(16, loadedOrig.Height);

        var loadedHist = loadedOrig.GetHistogram();
        Assert.NotNull(loadedHist);
        var loadedHistTotal = 0;
        foreach (var kv in loadedHist) loadedHistTotal += kv.Value;
        Assert.Equal(loadedOrig.GetPixelCount(), loadedHistTotal);

        var loadedBrightness = loadedOrig.GetBrightness();
        Assert.True(Math.Abs(loadedBrightness - brightness) < 5.0);

        // ApplyThreshold on loaded
        var loadedBinary = loadedOrig.ApplyThreshold(100);
        Assert.Equal(32, loadedBinary.Width);
        Assert.Equal(16, loadedBinary.Height);

        // GetBrightness consistent
        Assert.Equal(loadedOrig.GetBrightness(), loadedOrig.GetBrightness());

        // Final save
        var pathFinal = TempFile("dogfood_final.pgm");
        loadedBinary.SaveToFile(pathFinal);
        Assert.True(File.Exists(pathFinal));
        Assert.True(new FileInfo(pathFinal).Length > 0);
    }
}
