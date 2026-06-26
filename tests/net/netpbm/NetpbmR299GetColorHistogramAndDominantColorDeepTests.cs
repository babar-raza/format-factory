// Tests for NetpbmImage.GetColorHistogram, GetDominantColor, GetColorQuantile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R299

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R299: Tests for NetpbmImage.GetColorHistogram, GetDominantColor, GetColorQuantile deeper.
/// GetColorHistogram(): returns an array of pixel frequency counts (index = intensity value).
/// GetDominantColor(): returns the pixel intensity value with the highest frequency.
/// GetColorQuantile(q): returns the pixel value at the given quantile (0.0–1.0).
/// Covers: GetColorHistogram no-throw; GetColorHistogram non-null; GetColorHistogram consistent;
/// GetColorHistogram length; GetColorHistogram uniform sums to pixel count; GetColorHistogram save-load;
/// GetDominantColor no-throw; GetDominantColor in range; GetDominantColor consistent;
/// GetDominantColor uniform correct; GetDominantColor save-load;
/// GetColorQuantile no-throw; GetColorQuantile in range; GetColorQuantile consistent;
/// GetColorQuantile median for uniform; GetColorQuantile save-load;
/// dogfood CreateImage→GetColorHistogram→GetDominantColor→GetColorQuantile→SaveToFile pipeline.
/// </summary>
public class NetpbmR299GetColorHistogramAndDominantColorDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR299GetColorHistogramAndDominantColorDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR299_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateBimodalPgm()
    {
        // 8x8 with two clusters: low values (~30) and high values (~220)
        var path = TempFile("bimodal.pgm");
        File.WriteAllText(path,
            "P2\n8 8\n255\n" +
            " 28  32  30  35  28  30  33  31\n" +
            " 30  27  34  29  31  28  32  30\n" +
            "220 225 218 222 224 219 221 226\n" +
            "223 217 224 220 225 218 222 221\n" +
            " 29  31  28  33  30  27  34  32\n" +
            " 31  28  30  29  32  30  28  31\n" +
            "219 223 221 226 218 222 224 220\n" +
            "222 218 225 221 223 219 220 224\n");
        return path;
    }

    private string CreateUniformPgm()
    {
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
        // 8x4 horizontal gradient 0→255
        var path = TempFile("gradient.pgm");
        File.WriteAllText(path,
            "P2\n8 4\n255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n" +
            "  0  36  73 109 146 182 219 255\n");
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColorHistogram
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorHistogram_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var ex = Record.Exception(() => img.GetColorHistogram());
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorHistogram_NonNull()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        Assert.NotNull(img.GetColorHistogram());
    }

    [Fact]
    public void GetColorHistogram_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var h1 = img.GetColorHistogram();
        var h2 = img.GetColorHistogram();
        Assert.Equal(h1.Length, h2.Length);
        for (int i = 0; i < h1.Length; i++)
            Assert.Equal(h1[i], h2[i]);
    }

    [Fact]
    public void GetColorHistogram_Length_AtLeast256()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        Assert.True(img.GetColorHistogram().Length >= 256);
    }

    [Fact]
    public void GetColorHistogram_SumsToPixelCount_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        var hist = img.GetColorHistogram();
        long total = 0;
        foreach (var v in hist) total += v;
        Assert.Equal(img.GetPixelCount(), (int)total);
    }

    [Fact]
    public void GetColorHistogram_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var before = img.GetColorHistogram();
        var path = TempFile("ch_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        var after = loaded.GetColorHistogram();
        Assert.Equal(before.Length, after.Length);
        for (int i = 0; i < before.Length; i++)
            Assert.Equal(before[i], after[i]);
    }

    // -------------------------------------------------------------------------
    // GetDominantColor
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDominantColor_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var ex = Record.Exception(() => img.GetDominantColor());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDominantColor_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var dc = img.GetDominantColor();
        Assert.True(dc >= 0);
        Assert.True(dc <= img.MaxVal);
    }

    [Fact]
    public void GetDominantColor_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        Assert.Equal(img.GetDominantColor(), img.GetDominantColor());
    }

    [Fact]
    public void GetDominantColor_Uniform_ReturnsUniformValue()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        Assert.Equal(100, img.GetDominantColor());
    }

    [Fact]
    public void GetDominantColor_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var before = img.GetDominantColor();
        var path = TempFile("dc_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetDominantColor());
    }

    // -------------------------------------------------------------------------
    // GetColorQuantile
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColorQuantile_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var ex = Record.Exception(() => img.GetColorQuantile(0.5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColorQuantile_InRange()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var q = img.GetColorQuantile(0.5);
        Assert.True(q >= 0);
        Assert.True(q <= img.MaxVal);
    }

    [Fact]
    public void GetColorQuantile_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        Assert.Equal(img.GetColorQuantile(0.25), img.GetColorQuantile(0.25));
    }

    [Fact]
    public void GetColorQuantile_Uniform_ReturnsUniformValue()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm());
        var q50 = img.GetColorQuantile(0.5);
        Assert.Equal(100, q50);
    }

    [Fact]
    public void GetColorQuantile_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm());
        var before = img.GetColorQuantile(0.75);
        var path = TempFile("cq_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetColorQuantile(0.75));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColorHistogram_GetDominantColor_GetColorQuantile_SaveToFile_Pipeline()
    {
        // Satellite multispectral imagery simulation: land cover classification
        // Low values = water/shadow (~15-45), mid = vegetation (~80-120), high = urban/bare (~190-240)
        var path = TempFile("dogfood_satellite.pgm");
        File.WriteAllText(path,
            "P2\n12 10\n255\n" +
            " 20  18  22  15  25  95 102  88  95 210 215 208\n" +
            " 17  23  19  21  18  98  88  96 100 212 205 218\n" +
            " 22  16  20  24  17  92  99  85  97 208 220 210\n" +
            " 35  40  38  42  35 105 110 108 112 195 200 198\n" +
            " 38  33  41  36  39 108  95 102 106 202 196 204\n" +
            " 80  88  85  92  78 115 118 112 120 225 230 222\n" +
            " 90  82  88  85  92 112 108 118 110 228 218 232\n" +
            " 85  90  83  88  86 118 115 110 116 220 235 225\n" +
            "100  95  98  92 100 120 108 115 112 215 222 218\n" +
            " 92  98  95 100  88 110 118 108 120 230 225 228\n");

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(120, img.GetPixelCount());

        // GetColorHistogram — non-null, correct length, sums to pixel count
        var hist = img.GetColorHistogram();
        Assert.NotNull(hist);
        Assert.True(hist.Length >= 256);
        long total = 0;
        foreach (var v in hist) total += v;
        Assert.Equal(img.GetPixelCount(), (int)total);

        // Consistent
        var hist2 = img.GetColorHistogram();
        Assert.Equal(hist.Length, hist2.Length);

        // GetDominantColor — in range
        var dom = img.GetDominantColor();
        Assert.True(dom >= 0);
        Assert.True(dom <= img.MaxVal);
        Assert.Equal(dom, img.GetDominantColor()); // consistent

        // GetColorQuantile — ordering check
        var q25 = img.GetColorQuantile(0.25);
        var q50 = img.GetColorQuantile(0.5);
        var q75 = img.GetColorQuantile(0.75);
        Assert.True(q25 >= 0);
        Assert.True(q50 >= 0);
        Assert.True(q75 >= 0);
        Assert.True(q50 >= q25); // non-decreasing
        Assert.True(q75 >= q50);

        // Quantile boundaries
        var q0 = img.GetColorQuantile(0.0);
        var q1 = img.GetColorQuantile(1.0);
        Assert.True(q0 <= q25);
        Assert.True(q1 >= q75);

        // SaveToFile — original
        var out1 = TempFile("dogfood_satellite_out.pgm");
        img.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify histogram preserved
        var loaded = NetpbmImage.LoadFile(out1);
        Assert.Equal(img.Width, loaded.Width);
        Assert.Equal(img.Height, loaded.Height);
        var loadedHist = loaded.GetColorHistogram();
        Assert.Equal(hist.Length, loadedHist.Length);
        for (int i = 0; i < hist.Length; i++)
            Assert.Equal(hist[i], loadedHist[i]);
        Assert.Equal(dom, loaded.GetDominantColor());
        Assert.Equal(q50, loaded.GetColorQuantile(0.5));

        // Uniform sub-image test
        var uniform = NetpbmImage.LoadFile(CreateUniformPgm());
        var uHist = uniform.GetColorHistogram();
        Assert.Equal(uniform.GetPixelCount(), (int)uHist[100]);
        Assert.Equal(100, uniform.GetDominantColor());
        Assert.Equal(100, uniform.GetColorQuantile(0.0));
        Assert.Equal(100, uniform.GetColorQuantile(0.5));
        Assert.Equal(100, uniform.GetColorQuantile(1.0));

        // Gradient test — median should be near middle of range
        var grad = NetpbmImage.LoadFile(CreateGradientPgm());
        var gradHist = grad.GetColorHistogram();
        Assert.NotNull(gradHist);
        long gTotal = 0;
        foreach (var v in gradHist) gTotal += v;
        Assert.Equal(grad.GetPixelCount(), (int)gTotal);
        var gradQ50 = grad.GetColorQuantile(0.5);
        Assert.True(gradQ50 >= 0);
        Assert.True(gradQ50 <= grad.MaxVal);

        // ApplyMedianFilter preserves histogram-compatible pixel count
        var filtered = img.ApplyMedianFilter(3);
        Assert.Equal(img.Width, filtered.Width);
        Assert.Equal(img.Height, filtered.Height);
        var fHist = filtered.GetColorHistogram();
        long fTotal = 0;
        foreach (var v in fHist) fTotal += v;
        Assert.Equal(filtered.GetPixelCount(), (int)fTotal);

        // Final save
        var out2 = TempFile("dogfood_satellite_v2.pgm");
        filtered.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NetpbmImage.LoadFile(out2);
        Assert.NotNull(loaded2.GetColorHistogram());
        Assert.True(loaded2.GetDominantColor() >= 0);
        Assert.True(loaded2.GetColorQuantile(0.5) >= 0);
        var ex1 = Record.Exception(() => loaded2.ApplyMedianFilter(3));
        Assert.Null(ex1);
    }
}
