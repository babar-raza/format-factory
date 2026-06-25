// Tests for NetpbmDocument computed properties: IsColor, IsGrayscale, IsBitmap, AspectRatio, IsSquare
// Sprint: FORMAT-FACTORY-NETPBM-DOCUMENT-PROPS-20260625
// Ledger: R118-GOVERNED-DOTNET-NETPBM-DOCUMENT-PROPS-001

using System;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR118DocumentPropertiesTests
{
    private static NetpbmDocument MakeDoc(NetpbmFormat format, int width = 4, int height = 4, int maxVal = 255)
    {
        var image = new NetpbmImage { Format = format, Width = width, Height = height, MaxValue = maxVal };
        return NetpbmDocument.FromImage(image);
    }

    // ---- IsColor ----

    [Fact]
    public void IsColor_PpmP3_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PPM_P3).IsColor);

    [Fact]
    public void IsColor_PpmP6_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PPM_P6).IsColor);

    [Fact]
    public void IsColor_PgmP2_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PGM_P2).IsColor);

    [Fact]
    public void IsColor_PbmP1_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PBM_P1, maxVal: 1).IsColor);

    // ---- IsGrayscale ----

    [Fact]
    public void IsGrayscale_PgmP2_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PGM_P2).IsGrayscale);

    [Fact]
    public void IsGrayscale_PgmP5_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PGM_P5).IsGrayscale);

    [Fact]
    public void IsGrayscale_PpmP3_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PPM_P3).IsGrayscale);

    [Fact]
    public void IsGrayscale_PbmP1_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PBM_P1, maxVal: 1).IsGrayscale);

    // ---- IsBitmap ----

    [Fact]
    public void IsBitmap_PbmP1_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PBM_P1, maxVal: 1).IsBitmap);

    [Fact]
    public void IsBitmap_PbmP4_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PBM_P4, maxVal: 1).IsBitmap);

    [Fact]
    public void IsBitmap_PgmP2_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PGM_P2).IsBitmap);

    [Fact]
    public void IsBitmap_PpmP3_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PPM_P3).IsBitmap);

    // ---- AspectRatio ----

    [Fact]
    public void AspectRatio_SquareImage_ReturnsOne()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, width: 4, height: 4);
        Assert.Equal(1.0, doc.AspectRatio, precision: 5);
    }

    [Fact]
    public void AspectRatio_WideImage_ReturnsTwo()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, width: 8, height: 4);
        Assert.Equal(2.0, doc.AspectRatio, precision: 5);
    }

    [Fact]
    public void AspectRatio_TallImage_IsLessThanOne()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, width: 4, height: 8);
        Assert.True(doc.AspectRatio < 1.0);
    }

    // ---- IsSquare ----

    [Fact]
    public void IsSquare_SameDimensions_ReturnsTrue()
        => Assert.True(MakeDoc(NetpbmFormat.PGM_P2, width: 4, height: 4).IsSquare);

    [Fact]
    public void IsSquare_DifferentDimensions_ReturnsFalse()
        => Assert.False(MakeDoc(NetpbmFormat.PGM_P2, width: 4, height: 2).IsSquare);

    // ---- Mutual exclusivity ----

    [Fact]
    public void ExactlyOneOf_IsColor_IsGrayscale_IsBitmap_ForPpm()
    {
        var doc = MakeDoc(NetpbmFormat.PPM_P3);
        int trueCount = (doc.IsColor ? 1 : 0) + (doc.IsGrayscale ? 1 : 0) + (doc.IsBitmap ? 1 : 0);
        Assert.Equal(1, trueCount);
    }

    [Fact]
    public void ExactlyOneOf_IsColor_IsGrayscale_IsBitmap_ForPgm()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2);
        int trueCount = (doc.IsColor ? 1 : 0) + (doc.IsGrayscale ? 1 : 0) + (doc.IsBitmap ? 1 : 0);
        Assert.Equal(1, trueCount);
    }
}
