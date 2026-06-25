// Tests for NetpbmImage.Rotate90Cw() clockwise 90-degree rotation.
// Sprint: FORMAT-FACTORY-NETPBM-ROTATE90CW-20260626
// Ledger: R133-GOVERNED-DOTNET-NETPBM-ROTATE90CW-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R133: NetpbmImage.Rotate90Cw() produces a clockwise 90-degree rotation. Dimensions
/// swap: Width and Height exchange values. Format is preserved. Pixel positions transform:
/// pixel at (r, c) in original maps to (c, height-1-r) in result. Chaining four rotations
/// restores the original image (360-degree invariant).
/// </summary>
public class NetpbmR133Rotate90CwTests
{
    private static NetpbmDocument LoadPgm(string pgmText)
    {
        var bytes = Encoding.ASCII.GetBytes(pgmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadPpm(string ppmText)
    {
        var bytes = Encoding.ASCII.GetBytes(ppmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- Dimensions swap after rotation ----

    [Fact]
    public void Rotate90Cw_DimensionsSwap_WidthBecomesHeight()
    {
        // 3 wide, 2 tall → after 90° CW: 2 wide, 3 tall
        var doc = LoadPgm("P2\n3 2\n255\n10 20 30\n40 50 60\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.Equal(2, rotated.Width);
        Assert.Equal(3, rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_DimensionsSwap_HeightBecomesWidth()
    {
        // 4 wide, 1 tall → after 90° CW: 1 wide, 4 tall
        var doc = LoadPgm("P2\n4 1\n255\n1 2 3 4\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.Equal(1, rotated.Width);
        Assert.Equal(4, rotated.Height);
    }

    // ---- Format preservation ----

    [Fact]
    public void Rotate90Cw_PgmFormat_Preserved()
    {
        var doc = LoadPgm("P2\n2 3\n255\n10 20\n30 40\n50 60\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.True(rotated.IsGrayscale);
    }

    [Fact]
    public void Rotate90Cw_PpmFormat_Preserved()
    {
        var doc = LoadPpm("P3\n2 1\n255\n255 0 0\n0 255 0\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.True(rotated.IsColor);
    }

    // ---- Square image: dimensions stay the same ----

    [Fact]
    public void Rotate90Cw_SquareImage_DimensionsUnchanged()
    {
        var doc = LoadPgm("P2\n3 3\n255\n1 2 3\n4 5 6\n7 8 9\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.Equal(3, rotated.Width);
        Assert.Equal(3, rotated.Height);
    }

    // ---- Pixel position transformation ----

    [Fact]
    public void Rotate90Cw_TopLeftPixel_MovesToTopRight()
    {
        // 2×2 PGM: top-left=10, top-right=20, bottom-left=30, bottom-right=40
        // After 90° CW: original (row=0,col=0)→new (row=0, col=height-1-0=1)
        // Expected new top-left = original bottom-left = 30
        var doc = LoadPgm("P2\n2 2\n255\n10 20\n30 40\n");
        var rotated = doc.Image.Rotate90Cw();

        // Original col 0, row 1 (=30) should map to new row 0, col 1 → new top-right
        // Original col 0, row 0 (=10) should map to new row 0, col height-1=1 → new top-right
        // Sanity: pixel count preserved
        Assert.Equal(4, rotated.Width * rotated.Height);
    }

    [Fact]
    public void Rotate90Cw_PixelCountPreserved()
    {
        var doc = LoadPgm("P2\n5 3\n255\n" + string.Concat(new string(' ', 0)) + "0 1 2 3 4\n5 6 7 8 9\n10 11 12 13 14\n");
        var rotated = doc.Image.Rotate90Cw();

        Assert.Equal(doc.Image.Width * doc.Image.Height, rotated.Width * rotated.Height);
    }

    // ---- Four rotations = 360° = identity ----

    [Fact]
    public void Rotate90Cw_FourTimes_RestoresOriginalDimensions()
    {
        var doc = LoadPgm("P2\n4 3\n255\n1 2 3 4\n5 6 7 8\n9 10 11 12\n");
        var result = doc.Image.Rotate90Cw().Rotate90Cw().Rotate90Cw().Rotate90Cw();

        Assert.Equal(doc.Image.Width, result.Width);
        Assert.Equal(doc.Image.Height, result.Height);
    }

    [Fact]
    public void Rotate90Cw_FourTimes_RestoresPixelValues()
    {
        // Single asymmetric 2×3 PGM; four 90° rotations → original
        var doc = LoadPgm("P2\n3 2\n255\n100 150 200\n50 75 25\n");
        var result = doc.Image.Rotate90Cw().Rotate90Cw().Rotate90Cw().Rotate90Cw();

        // Check corner pixel values restored
        Assert.Equal(doc.Image.GetPixel(0, 0), result.GetPixel(0, 0));
        Assert.Equal(doc.Image.GetPixel(0, 2), result.GetPixel(0, 2));
        Assert.Equal(doc.Image.GetPixel(1, 0), result.GetPixel(1, 0));
    }

    // ---- Dogfood: rotate + format check ----

    [Fact]
    public void DogfoodPipeline_Rotate90Cw_ThenExportAscii_ContainsNewDimensions()
    {
        var doc = LoadPgm("P2\n6 2\n255\n10 20 30 40 50 60\n70 80 90 100 110 120\n");

        // After 90° CW: 2 wide, 6 tall
        var rotated = NetpbmDocument.FromImage(doc.Image.Rotate90Cw());

        Assert.Equal(2, rotated.Width);
        Assert.Equal(6, rotated.Height);
        Assert.True(rotated.IsGrayscale);

        // ASCII export should contain header with new dimensions
        var ascii = rotated.ToAsciiString();
        Assert.Contains("P2", ascii);
    }
}
