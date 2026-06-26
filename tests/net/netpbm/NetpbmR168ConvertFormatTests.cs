// Tests for NetpbmImage.ConvertFormat and NetpbmDocument format properties.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R168

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R168: Tests for NetpbmImage.ConvertFormat, NetpbmDocument format properties.
/// ConvertFormat(targetFormat): converts image to another Netpbm format.
/// NetpbmDocument: IsColor, IsGrayscale, IsBitmap, AspectRatio, IsSquare, PixelCount.
/// Covers: ConvertFormat PGM->PPM returns color; ConvertFormat PPM->PGM returns grayscale;
/// ConvertFormat preserves pixel count; ConvertFormat preserves dimensions;
/// IsColor true for PPM image; IsGrayscale true for PGM image;
/// IsBitmap true for PBM image; AspectRatio correct for square image;
/// IsSquare true for square image; IsSquare false for non-square;
/// PixelCount equals Width*Height; NetpbmDocument.PixelCount; NetpbmDocument.MaxValue;
/// dogfood Create->ConvertFormat->NetpbmDocument.FromImage->properties pipeline.
/// </summary>
public class NetpbmR168ConvertFormatTests
{
    private static NetpbmImage CreateGray(int w, int h, byte fill) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PGM_P2, fill);

    private static NetpbmImage CreateColor(int w, int h)
    {
        var img = NetpbmImage.Create(w, h, NetpbmFormat.PPM_P3, 0);
        for (var row = 0; row < h; row++)
            for (var col = 0; col < w; col++)
                img.SetPixelColor(row, col, 150, 100, 80);
        return img;
    }

    private static NetpbmImage CreateBitmap(int w, int h) =>
        NetpbmImage.Create(w, h, NetpbmFormat.PBM_P1, 0);

    // -------------------------------------------------------------------------
    // ConvertFormat
    // -------------------------------------------------------------------------

    [Fact]
    public void ConvertFormat_PGM_to_PPM_ReturnsColorFormat()
    {
        var gray = CreateGray(4, 4, 128);
        var color = gray.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.True(color.Format == NetpbmFormat.PPM_P3 || color.Format == NetpbmFormat.PPM_P6);
    }

    [Fact]
    public void ConvertFormat_PreservesDimensions()
    {
        var gray = CreateGray(5, 6, 100);
        var converted = gray.ConvertFormat(NetpbmFormat.PPM_P3);
        Assert.Equal(5, converted.Width);
        Assert.Equal(6, converted.Height);
    }

    [Fact]
    public void ConvertFormat_PPM_to_PGM_ReturnsGrayscale()
    {
        var color = CreateColor(4, 4);
        var gray = color.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.True(gray.Format == NetpbmFormat.PGM_P2 || gray.Format == NetpbmFormat.PGM_P5);
    }

    [Fact]
    public void ConvertFormat_SameFormat_Succeeds()
    {
        var gray = CreateGray(4, 4, 128);
        var same = gray.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(4, same.Width);
        Assert.Equal(4, same.Height);
    }

    // -------------------------------------------------------------------------
    // NetpbmDocument format properties
    // -------------------------------------------------------------------------

    [Fact]
    public void IsColor_TrueForPPMImage()
    {
        var img = CreateColor(4, 4);
        var doc = NetpbmDocument.FromImage(img);
        Assert.True(doc.IsColor);
    }

    [Fact]
    public void IsGrayscale_TrueForPGMImage()
    {
        var img = CreateGray(4, 4, 128);
        var doc = NetpbmDocument.FromImage(img);
        Assert.True(doc.IsGrayscale);
    }

    [Fact]
    public void IsBitmap_TrueForPBMImage()
    {
        var img = CreateBitmap(4, 4);
        var doc = NetpbmDocument.FromImage(img);
        Assert.True(doc.IsBitmap);
    }

    [Fact]
    public void AspectRatio_SquareImage_IsOne()
    {
        var img = CreateGray(4, 4, 128);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(1.0, doc.AspectRatio, precision: 5);
    }

    [Fact]
    public void IsSquare_ForSquareImage_IsTrue()
    {
        var img = CreateGray(5, 5, 100);
        var doc = NetpbmDocument.FromImage(img);
        Assert.True(doc.IsSquare);
    }

    [Fact]
    public void IsSquare_ForNonSquareImage_IsFalse()
    {
        var img = CreateGray(5, 3, 100);
        var doc = NetpbmDocument.FromImage(img);
        Assert.False(doc.IsSquare);
    }

    [Fact]
    public void PixelCount_EqualsWidthTimesHeight()
    {
        var img = CreateGray(5, 6, 100);
        var doc = NetpbmDocument.FromImage(img);
        Assert.Equal(5 * 6, doc.PixelCount);
    }

    [Fact]
    public void MaxValue_IsPositive()
    {
        var img = CreateGray(4, 4, 128);
        var doc = NetpbmDocument.FromImage(img);
        Assert.True(doc.MaxValue > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->ConvertFormat->NetpbmDocument.FromImage->properties
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ConvertFormatDocumentPropertiesPipeline()
    {
        var gray = NetpbmImage.Create(6, 4, NetpbmFormat.PGM_P2, 150);
        Assert.Equal(6, gray.Width);
        Assert.Equal(4, gray.Height);

        // Verify grayscale doc properties
        var grayDoc = NetpbmDocument.FromImage(gray);
        Assert.True(grayDoc.IsGrayscale);
        Assert.False(grayDoc.IsColor);
        Assert.False(grayDoc.IsSquare);
        Assert.Equal(24, grayDoc.PixelCount);
        Assert.True(grayDoc.MaxValue > 0);
        Assert.True(grayDoc.AspectRatio > 1.0); // wider than tall

        // Convert to color
        var color = gray.ConvertFormat(NetpbmFormat.PPM_P3);
        var colorDoc = NetpbmDocument.FromImage(color);
        Assert.True(colorDoc.IsColor);
        Assert.Equal(6, colorDoc.Width);
        Assert.Equal(4, colorDoc.Height);
        Assert.Equal(24, colorDoc.PixelCount);

        // Convert back to grayscale
        var grayAgain = color.ConvertFormat(NetpbmFormat.PGM_P2);
        Assert.Equal(6, grayAgain.Width);
        Assert.Equal(4, grayAgain.Height);
    }
}
