// Tests for NetpbmImage.GetContrastRatio, GetDynamicRange deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R403

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R403: Tests for NetpbmImage.GetContrastRatio, GetDynamicRange deeper.
/// GetContrastRatio(): returns the ratio of max to min pixel intensity (or similar contrast measure).
/// GetDynamicRange(): returns the difference between the maximum and minimum pixel values in the image.
/// Covers: GetContrastRatio no-throw; GetContrastRatio non-negative;
/// GetContrastRatio consistent; GetContrastRatio save-load;
/// GetDynamicRange no-throw; GetDynamicRange non-negative;
/// GetDynamicRange 0 for uniform; GetDynamicRange consistent;
/// GetDynamicRange save-load; dogfood pipeline.
/// </summary>
public class NetpbmR403GetContrastRatioAndDynamicRangeDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NetpbmR403GetContrastRatioAndDynamicRangeDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NetpbmR403_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHighContrastPgm(string name)
    {
        // 4x4 image: black pixels (0) and white pixels (255) — maximum contrast
        var path = TempFile(name);
        var lines = new[]
        {
            "P2", "4 4", "255",
            "0 255 0 255",
            "255 0 255 0",
            "0 255 0 255",
            "255 0 255 0"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateUniformPgm(string name)
    {
        // All pixels = 128 (mid-grey)
        var path = TempFile(name);
        var lines = new[]
        {
            "P2", "4 4", "255",
            "128 128 128 128",
            "128 128 128 128",
            "128 128 128 128",
            "128 128 128 128"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateGradientPgm(string name)
    {
        // 8x1 gradient from 10 to 220
        var path = TempFile(name);
        var lines = new[]
        {
            "P2", "8 1", "255",
            "10 40 70 100 130 160 190 220"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetContrastRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetContrastRatio_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("hc.pgm"));
        var ex = Record.Exception(() => img.GetContrastRatio());
        Assert.Null(ex);
    }

    [Fact]
    public void GetContrastRatio_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("hc2.pgm"));
        Assert.True(img.GetContrastRatio() >= 0);
    }

    [Fact]
    public void GetContrastRatio_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("hc3.pgm"));
        Assert.Equal(img.GetContrastRatio(), img.GetContrastRatio());
    }

    [Fact]
    public void GetContrastRatio_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateHighContrastPgm("hc4.pgm"));
        var before = img.GetContrastRatio();
        var path = TempFile("cr_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetContrastRatio(), precision: 5);
    }

    // -------------------------------------------------------------------------
    // GetDynamicRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDynamicRange_NoThrow()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("grad.pgm"));
        var ex = Record.Exception(() => img.GetDynamicRange());
        Assert.Null(ex);
    }

    [Fact]
    public void GetDynamicRange_NonNegative()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("grad2.pgm"));
        Assert.True(img.GetDynamicRange() >= 0);
    }

    [Fact]
    public void GetDynamicRange_Zero_ForUniform()
    {
        var img = NetpbmImage.LoadFile(CreateUniformPgm("uni.pgm"));
        Assert.Equal(0, img.GetDynamicRange());
    }

    [Fact]
    public void GetDynamicRange_Correct_ForGradient()
    {
        // Gradient 10..220 → dynamic range = 210
        var img = NetpbmImage.LoadFile(CreateGradientPgm("grad3.pgm"));
        Assert.Equal(210, img.GetDynamicRange());
    }

    [Fact]
    public void GetDynamicRange_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("grad4.pgm"));
        Assert.Equal(img.GetDynamicRange(), img.GetDynamicRange());
    }

    [Fact]
    public void GetDynamicRange_SaveLoad_Consistent()
    {
        var img = NetpbmImage.LoadFile(CreateGradientPgm("grad5.pgm"));
        var before = img.GetDynamicRange();
        var path = TempFile("dr_save.pgm");
        img.SaveToFile(path);
        Assert.Equal(before, NetpbmImage.LoadFile(path).GetDynamicRange());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetContrastRatio_GetDynamicRange_Pipeline()
    {
        // Science — STFC / RAL Space: UK Met Office Satellite Image Processing 2024
        // Meteosat Third Generation (MTG) Level-1C calibrated radiance images
        // Contrast ratio and dynamic range used for cloud-top temperature retrieval quality control
        // Images from MTG-I1 rapid scan service: visible (VIS0.6), near-IR (NIR1.3), thermal-IR (IR10.5)

        // Image 1: VIS0.6 — high-contrast visible channel (bright clouds against dark ocean)
        var path1 = TempFile("mtg_vis06_rapid_scan_20240901T1200Z.pgm");
        var sb1 = new System.Text.StringBuilder();
        sb1.AppendLine("P2");
        sb1.AppendLine("16 8");
        sb1.AppendLine("255");
        // High contrast: cloud regions (200-250) vs ocean (5-30)
        sb1.AppendLine("8 12 220 245 240 235 15 18 22 10 230 248 243 237 14 9");
        sb1.AppendLine("10 15 225 248 235 240 12 8 19 13 228 245 238 242 11 7");
        sb1.AppendLine("5 8 212 238 248 230 9 14 7 11 215 241 250 232 8 5");
        sb1.AppendLine("12 18 228 242 237 245 16 10 14 8 220 238 246 240 12 10");
        sb1.AppendLine("7 11 215 240 243 233 11 7 9 13 218 242 248 235 9 6");
        sb1.AppendLine("9 14 222 246 239 241 8 12 11 16 225 244 241 237 10 8");
        sb1.AppendLine("6 9 208 232 245 228 14 10 6 8 210 236 244 229 7 5");
        sb1.AppendLine("11 16 218 240 242 236 10 6 12 10 222 239 247 234 11 8");
        File.WriteAllText(path1, sb1.ToString());

        var img1 = NetpbmImage.LoadFile(path1);
        var cr1 = img1.GetContrastRatio();
        var dr1 = img1.GetDynamicRange();
        Assert.True(cr1 >= 0);
        Assert.True(dr1 > 0); // high contrast image has significant dynamic range
        Assert.Equal(cr1, img1.GetContrastRatio()); // consistent
        Assert.Equal(dr1, img1.GetDynamicRange()); // consistent

        // Image 2: IR10.5 — thermal infrared (cloud-top temperatures)
        // Cold cloud tops (low values = cold = 30-80), warm surface (high values = warm = 180-220)
        var path2 = TempFile("mtg_ir105_rapid_scan_20240901T1200Z.pgm");
        var sb2 = new System.Text.StringBuilder();
        sb2.AppendLine("P2");
        sb2.AppendLine("16 4");
        sb2.AppendLine("255");
        sb2.AppendLine("185 192 45 38 52 41 198 203 208 195 35 42 55 38 201 188");
        sb2.AppendLine("190 197 52 43 39 48 205 198 195 202 42 49 38 45 196 192");
        sb2.AppendLine("188 195 41 35 48 44 202 197 199 205 48 35 42 51 199 185");
        sb2.AppendLine("193 200 48 41 44 52 197 204 203 198 39 46 49 43 202 190");
        File.WriteAllText(path2, sb2.ToString());

        var img2 = NetpbmImage.LoadFile(path2);
        var cr2 = img2.GetContrastRatio();
        var dr2 = img2.GetDynamicRange();
        Assert.True(cr2 >= 0);
        Assert.True(dr2 > 0);

        // Image 3: NIR1.3 — water vapour channel (near-uniform low values over moist atmosphere)
        // Water vapour channel is near-uniform for clear air; small dynamic range expected
        var path3 = TempFile("mtg_nir13_clear_20240901T1200Z.pgm");
        var sb3 = new System.Text.StringBuilder();
        sb3.AppendLine("P2");
        sb3.AppendLine("8 4");
        sb3.AppendLine("100");
        sb3.AppendLine("48 52 50 49 51 47 53 50");
        sb3.AppendLine("50 49 51 52 48 50 49 51");
        sb3.AppendLine("51 50 49 48 52 51 50 49");
        sb3.AppendLine("49 51 52 50 50 49 51 48");
        File.WriteAllText(path3, sb3.ToString());

        var img3 = NetpbmImage.LoadFile(path3);
        var cr3 = img3.GetContrastRatio();
        var dr3 = img3.GetDynamicRange();
        Assert.True(cr3 >= 0);
        Assert.True(dr3 >= 0);
        Assert.True(dr3 < dr1); // water vapour channel has less dynamic range than visible

        // SaveToFile and LoadFile verification
        var save1 = TempFile("mtg_vis06_saved.pgm");
        img1.SaveToFile(save1);
        Assert.True(File.Exists(save1));
        Assert.True(new FileInfo(save1).Length > 0);

        var loaded1 = NetpbmImage.LoadFile(save1);
        Assert.Equal(dr1, loaded1.GetDynamicRange());
        Assert.Equal(cr1, loaded1.GetContrastRatio(), precision: 5);

        var save2 = TempFile("mtg_ir105_saved.pgm");
        img2.SaveToFile(save2);
        var loaded2 = NetpbmImage.LoadFile(save2);
        Assert.Equal(dr2, loaded2.GetDynamicRange());

        var ex1 = Record.Exception(() => loaded1.GetContrastRatio());
        var ex2 = Record.Exception(() => loaded1.GetDynamicRange());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
