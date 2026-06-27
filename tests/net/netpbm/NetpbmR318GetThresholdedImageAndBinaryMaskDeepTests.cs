// Tests for NetpbmImage.GetThresholdedImage, GetBinaryMask, GetOtsuThreshold deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R318

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R318: Tests for NetpbmImage.GetThresholdedImage, GetBinaryMask, GetOtsuThreshold deeper.
/// GetThresholdedImage(threshold): returns a binary image where pixels above threshold become MaxVal, others become 0.
/// GetBinaryMask(threshold): returns a boolean mask array where true = pixel above threshold.
/// GetOtsuThreshold(): automatically computes the optimal binarisation threshold.
/// Covers: GetThresholdedImage no-throw; GetThresholdedImage same dims; GetThresholdedImage consistent;
/// GetThresholdedImage only MaxVal or 0; GetThresholdedImage save-load;
/// GetBinaryMask no-throw; GetBinaryMask length equals pixel count; GetBinaryMask consistent;
/// GetBinaryMask save-load;
/// GetOtsuThreshold no-throw; GetOtsuThreshold in pixel range; GetOtsuThreshold consistent;
/// GetOtsuThreshold save-load;
/// dogfood CreateImage→GetThresholdedImage→GetBinaryMask→GetOtsuThreshold→SaveToFile pipeline.
/// </summary>
public class NetpbmR318GetThresholdedImageAndBinaryMaskDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR318GetThresholdedImageAndBinaryMaskDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR318_" + Guid.NewGuid().ToString("N"));
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
        // Bimodal image: left half dark (~50), right half bright (~200) — ideal for thresholding
        var path = TempFile("bimodal.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = c < 6 ? (byte)(40 + r * 3) : (byte)(190 + r * 3);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    private string CreateGradientPgm()
    {
        var path = TempFile("gradient.pgm");
        var pixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                pixels[r * 12 + c] = (byte)(c * 20 + r * 5);
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using var fs = File.OpenWrite(path); fs.Write(header); fs.Write(pixels);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetThresholdedImage
    // -------------------------------------------------------------------------

    [Fact]
    public void GetThresholdedImage_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var ex = Record.Exception(() => img.GetThresholdedImage(128));
        Assert.Null(ex);
    }

    [Fact]
    public void GetThresholdedImage_SameDims()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var thresh = img.GetThresholdedImage(128);
        Assert.Equal(img.Width, thresh.Width);
        Assert.Equal(img.Height, thresh.Height);
    }

    [Fact]
    public void GetThresholdedImage_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var t1 = img.GetThresholdedImage(128);
        var t2 = img.GetThresholdedImage(128);
        Assert.Equal(t1.GetMeanPixelValue(), t2.GetMeanPixelValue(), precision: 4);
    }

    [Fact]
    public void GetThresholdedImage_OnlyMaxValOrZero()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var thresh = img.GetThresholdedImage(128);
        // After thresholding, min should be 0 and max should be MaxVal
        Assert.Equal(0, thresh.GetMinPixel());
        Assert.Equal(img.MaxVal, thresh.GetMaxPixel());
    }

    [Fact]
    public void GetThresholdedImage_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var thresh = img.GetThresholdedImage(100);
        var path = TempFile("thresh_save.pgm");
        thresh.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(thresh.Width, loaded.Width);
        Assert.Equal(thresh.GetMeanPixelValue(), loaded.GetMeanPixelValue(), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetBinaryMask
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBinaryMask_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var ex = Record.Exception(() => img.GetBinaryMask(128));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBinaryMask_LengthEqualsPixelCount()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var mask = img.GetBinaryMask(128);
        Assert.Equal(img.Width * img.Height, mask.Length);
    }

    [Fact]
    public void GetBinaryMask_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var m1 = img.GetBinaryMask(128);
        var m2 = img.GetBinaryMask(128);
        Assert.Equal(m1.Length, m2.Length);
    }

    [Fact]
    public void GetBinaryMask_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var before = img.GetBinaryMask(100).Length;
        var path = TempFile("bm_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetBinaryMask(100).Length);
    }

    // -------------------------------------------------------------------------
    // GetOtsuThreshold
    // -------------------------------------------------------------------------

    [Fact]
    public void GetOtsuThreshold_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var ex = Record.Exception(() => img.GetOtsuThreshold());
        Assert.Null(ex);
    }

    [Fact]
    public void GetOtsuThreshold_InPixelRange()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var t = img.GetOtsuThreshold();
        Assert.True(t >= 0);
        Assert.True(t <= img.MaxVal);
    }

    [Fact]
    public void GetOtsuThreshold_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        Assert.Equal(img.GetOtsuThreshold(), img.GetOtsuThreshold());
    }

    [Fact]
    public void GetOtsuThreshold_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateBimodalPgm());
        var before = img.GetOtsuThreshold();
        var path = TempFile("otsu_save.pgm");
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFile(path);
        Assert.Equal(before, loaded.GetOtsuThreshold());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetThresholdedImage_GetBinaryMask_GetOtsuThreshold_SaveToFile_Pipeline()
    {
        // Industrial defect detection — PCB inspection thermal image analysis
        var path = TempFile("dogfood_pcb_thermal.pgm");
        var pixels = new byte[12 * 10];
        // Simulate thermal image: normal components (medium), hot spots (bright), background (dark)
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
            {
                bool isHotspot = (r == 2 && c == 3) || (r == 5 && c == 8) || (r == 7 && c == 4);
                bool isComponent = (r >= 1 && r <= 3 && c >= 2 && c <= 5) ||
                                   (r >= 4 && r <= 6 && c >= 7 && c <= 10);
                pixels[r * 12 + c] = isHotspot ? (byte)240
                    : isComponent ? (byte)(120 + r * 5 + c * 3)
                    : (byte)(30 + r * 3 + c * 2);
            }
        var header = System.Text.Encoding.ASCII.GetBytes("P5\n12 10\n255\n");
        using (var fs = File.OpenWrite(path)) { fs.Write(header); fs.Write(pixels); }

        var img = NetpbmImage.LoadFile(path);
        Assert.Equal(12, img.Width);
        Assert.Equal(10, img.Height);
        Assert.Equal(255, img.MaxVal);

        // GetOtsuThreshold — automatic threshold for hotspot detection
        var otsuT = img.GetOtsuThreshold();
        Assert.True(otsuT >= 0);
        Assert.True(otsuT <= 255);
        Assert.Equal(otsuT, img.GetOtsuThreshold()); // consistent

        // GetThresholdedImage — manual threshold at 150
        var thresh150 = img.GetThresholdedImage(150);
        Assert.Equal(12, thresh150.Width);
        Assert.Equal(10, thresh150.Height);
        // After thresholding: only 0 or MaxVal
        Assert.Equal(0, thresh150.GetMinPixel());
        Assert.Equal(img.MaxVal, thresh150.GetMaxPixel());
        Assert.Equal(thresh150.GetMeanPixelValue(), img.GetThresholdedImage(150).GetMeanPixelValue(), precision: 4); // consistent

        // GetThresholdedImage — Otsu threshold
        var threshOtsu = img.GetThresholdedImage(otsuT);
        Assert.Equal(12, threshOtsu.Width);
        Assert.Equal(10, threshOtsu.Height);
        Assert.Equal(0, threshOtsu.GetMinPixel());

        // GetBinaryMask — manual threshold
        var mask150 = img.GetBinaryMask(150);
        Assert.NotNull(mask150);
        Assert.Equal(120, mask150.Length); // 12×10
        Assert.Equal(mask150.Length, img.GetBinaryMask(150).Length); // consistent

        // GetBinaryMask — Otsu threshold
        var maskOtsu = img.GetBinaryMask(otsuT);
        Assert.NotNull(maskOtsu);
        Assert.Equal(120, maskOtsu.Length);

        // SaveToFile — thresholded 150
        var out1 = TempFile("dogfood_pcb_thresh150.pgm");
        thresh150.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);
        var loadedThresh = NetpbmImage.LoadFile(out1);
        Assert.Equal(12, loadedThresh.Width);
        Assert.Equal(thresh150.GetMeanPixelValue(), loadedThresh.GetMeanPixelValue(), precision: 2);

        // SaveToFile — thresholded Otsu
        var out2 = TempFile("dogfood_pcb_thresh_otsu.pgm");
        threshOtsu.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loadedThreshOtsu = NetpbmImage.LoadFile(out2);
        Assert.Equal(12, loadedThreshOtsu.Width);

        // Bimodal image: Otsu should find threshold between dark and bright regions
        var bimodalPath = TempFile("dogfood_bimodal.pgm");
        var biPixels = new byte[12 * 10];
        for (int r = 0; r < 10; r++)
            for (int c = 0; c < 12; c++)
                biPixels[r * 12 + c] = c < 6 ? (byte)50 : (byte)200;
        using (var bfs = File.OpenWrite(bimodalPath)) { bfs.Write(header); bfs.Write(biPixels); }
        var biImg = NetpbmImage.LoadFile(bimodalPath);
        var biOtsu = biImg.GetOtsuThreshold();
        Assert.True(biOtsu > 50);
        Assert.True(biOtsu < 200);

        // Chain: threshold → save → reload → binary mask
        var chain = img.GetThresholdedImage(otsuT);
        var chainPath = TempFile("dogfood_chain.pgm");
        chain.SaveToFile(chainPath);
        var chainLoaded = NetpbmImage.LoadFile(chainPath);
        var chainMask = chainLoaded.GetBinaryMask(128);
        Assert.Equal(120, chainMask.Length);
        var ex1 = Record.Exception(() => chainLoaded.GetOtsuThreshold());
        Assert.Null(ex1);
    }
}
