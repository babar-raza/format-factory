// Tests for NetpbmImage.GetBrightnessMap() — per-pixel brightness array.
// Sprint: FORMAT-FACTORY-NETPBM-BRIGHTNESS-MAP-20260626
// Ledger: R130-GOVERNED-DOTNET-NETPBM-BRIGHTNESS-MAP-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R130: NetpbmImage.GetBrightnessMap() returns a double[] with one entry per pixel.
/// Length == Width * Height. Values in range [0.0, 1.0]. All-white PGM → all 1.0.
/// All-black PGM → all 0.0. Mixed PGM → values between. PPM channels produce
/// luminance-based brightness values.
/// </summary>
public class NetpbmR130BrightnessMapTests
{
    private static NetpbmDocument LoadPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- Length == PixelCount ----

    [Fact]
    public void BrightnessMap_Length_EqualsTotalPixelCount()
    {
        const string pgm = "P2\n3 4\n255\n0 0 0\n0 0 0\n0 0 0\n0 0 0\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        Assert.Equal(doc.PixelCount, map.Length);
    }

    [Fact]
    public void BrightnessMap_SinglePixel_LengthIsOne()
    {
        const string pgm = "P2\n1 1\n255\n128\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        Assert.Single(map);
    }

    [Fact]
    public void BrightnessMap_WidthTimesHeight_MatchesLength()
    {
        const string pgm = "P2\n5 2\n255\n0 64 128 192 255\n255 192 128 64 0\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        Assert.Equal(doc.Width * doc.Height, map.Length);
    }

    // ---- All values in [0.0, 1.0] ----

    [Fact]
    public void BrightnessMap_AllValues_InUnitRange()
    {
        const string pgm = "P2\n4 2\n255\n0 64 128 255\n200 100 50 10\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        foreach (var v in map)
        {
            Assert.True(v >= 0.0 && v <= 1.0,
                $"Brightness value {v} is outside [0.0, 1.0]");
        }
    }

    // ---- All-white PGM → all 1.0 ----

    [Fact]
    public void BrightnessMap_AllWhitePgm_AllValuesAreOne()
    {
        const string pgm = "P2\n3 3\n255\n255 255 255\n255 255 255\n255 255 255\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        foreach (var v in map)
            Assert.Equal(1.0, v, precision: 5);
    }

    // ---- All-black PGM → all 0.0 ----

    [Fact]
    public void BrightnessMap_AllBlackPgm_AllValuesAreZero()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        foreach (var v in map)
            Assert.Equal(0.0, v, precision: 5);
    }

    // ---- Mid-gray pixel → approximately 0.5 ----

    [Fact]
    public void BrightnessMap_MidGray_ValueNearHalf()
    {
        const string pgm = "P2\n1 1\n255\n128\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        Assert.True(map[0] >= 0.49 && map[0] <= 0.51,
            $"Expected ~0.5 for mid-gray pixel 128/255, got {map[0]}");
    }

    // ---- PPM: returns luminance-based values ----

    [Fact]
    public void BrightnessMap_AllWhitePpm_AllValuesAreOne()
    {
        const string ppm = "P3\n2 2\n255\n255 255 255  255 255 255\n255 255 255  255 255 255\n";
        var doc = LoadPpm(ppm);

        var map = doc.Image.GetBrightnessMap();
        foreach (var v in map)
            Assert.Equal(1.0, v, precision: 5);
    }

    [Fact]
    public void BrightnessMap_Ppm_LengthMatchesPixelCount()
    {
        const string ppm = "P3\n4 3\n255\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n";
        var doc = LoadPpm(ppm);

        var map = doc.Image.GetBrightnessMap();
        Assert.Equal(doc.PixelCount, map.Length);
    }

    // ---- Dogfood: values consistent with GetBrightness average ----

    [Fact]
    public void DogfoodPipeline_BrightnessMapAverage_MatchesGetBrightness()
    {
        const string pgm = "P2\n4 2\n255\n0 64 128 255\n200 100 50 10\n";
        var doc = LoadPgm(pgm);

        var map = doc.Image.GetBrightnessMap();
        var avgFromMap = 0.0;
        foreach (var v in map)
            avgFromMap += v;
        avgFromMap /= map.Length;

        var brightnessFromApi = doc.Image.GetBrightness();

        Assert.True(Math.Abs(avgFromMap - brightnessFromApi) < 0.01,
            $"Map average {avgFromMap} should be close to GetBrightness {brightnessFromApi}");
    }
}
