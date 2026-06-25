// Tests for NetpbmDocument format detection properties and ToAsciiString output.
// Sprint: FORMAT-FACTORY-NETPBM-FORMAT-DETECTION-20260626
// Ledger: R132-GOVERNED-DOTNET-NETPBM-FORMAT-DETECTION-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R132: NetpbmDocument format detection properties — IsColor, IsGrayscale, IsBitmap
/// correctly classify P1/P2/P3 documents. AspectRatio and IsSquare derive from Width/Height.
/// ToAsciiString() produces a valid ASCII PNM header string for any format.
/// </summary>
public class NetpbmR132FormatDetectionTests
{
    private static NetpbmDocument LoadAscii(string pnmText)
    {
        var bytes = Encoding.ASCII.GetBytes(pnmText);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- IsGrayscale ----

    [Fact]
    public void IsGrayscale_PgmP2_IsTrue()
    {
        var doc = LoadAscii("P2\n2 2\n255\n128 128\n128 128\n");
        Assert.True(doc.IsGrayscale);
    }

    [Fact]
    public void IsGrayscale_PpmP3_IsFalse()
    {
        var doc = LoadAscii("P3\n1 1\n255\n100 150 200\n");
        Assert.False(doc.IsGrayscale);
    }

    // ---- IsColor ----

    [Fact]
    public void IsColor_PpmP3_IsTrue()
    {
        var doc = LoadAscii("P3\n1 1\n255\n255 0 0\n");
        Assert.True(doc.IsColor);
    }

    [Fact]
    public void IsColor_PgmP2_IsFalse()
    {
        var doc = LoadAscii("P2\n1 1\n255\n200\n");
        Assert.False(doc.IsColor);
    }

    // ---- IsBitmap ----

    [Fact]
    public void IsBitmap_PbmP1_IsTrue()
    {
        var doc = LoadAscii("P1\n1 1\n0\n");
        Assert.True(doc.IsBitmap);
    }

    [Fact]
    public void IsBitmap_PgmP2_IsFalse()
    {
        var doc = LoadAscii("P2\n1 1\n255\n128\n");
        Assert.False(doc.IsBitmap);
    }

    // ---- Mutual exclusion ----

    [Fact]
    public void FormatProperties_PgmP2_ExactlyOneIsTrue()
    {
        var doc = LoadAscii("P2\n1 1\n255\n64\n");
        var trueCount = (doc.IsGrayscale ? 1 : 0) + (doc.IsColor ? 1 : 0) + (doc.IsBitmap ? 1 : 0);
        Assert.Equal(1, trueCount);
    }

    // ---- AspectRatio ----

    [Fact]
    public void AspectRatio_SquareImage_IsOne()
    {
        var doc = LoadAscii("P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n");
        Assert.Equal(1.0, doc.AspectRatio, precision: 4);
    }

    [Fact]
    public void AspectRatio_WideImage_IsGreaterThanOne()
    {
        // 4 wide, 2 tall → ratio = 2.0
        var doc = LoadAscii("P2\n4 2\n255\n0 0 0 0\n0 0 0 0\n");
        Assert.True(doc.AspectRatio > 1.0, $"Expected > 1.0, got {doc.AspectRatio}");
    }

    // ---- IsSquare ----

    [Fact]
    public void IsSquare_SquarePgm_IsTrue()
    {
        var doc = LoadAscii("P2\n5 5\n255\n" + string.Concat(Enumerable.Repeat("128 ", 25)) + "\n");
        Assert.True(doc.IsSquare);
    }

    [Fact]
    public void IsSquare_RectangularPgm_IsFalse()
    {
        var doc = LoadAscii("P2\n3 2\n255\n0 0 0\n0 0 0\n");
        Assert.False(doc.IsSquare);
    }

    // ---- ToAsciiString ----

    [Fact]
    public void ToAsciiString_PgmDoc_ContainsMagicNumber()
    {
        var doc = LoadAscii("P2\n2 1\n255\n100 200\n");
        var ascii = doc.ToAsciiString();
        Assert.StartsWith("P2", ascii);
    }

    [Fact]
    public void ToAsciiString_PpmDoc_ContainsP3Header()
    {
        var doc = LoadAscii("P3\n1 1\n255\n255 0 0\n");
        var ascii = doc.ToAsciiString();
        Assert.StartsWith("P3", ascii);
    }

    // ---- Dogfood: load PGM, verify detection + ascii export ----

    [Fact]
    public void DogfoodPipeline_PgmDetection_ConsistentProperties()
    {
        var doc = LoadAscii("P2\n4 4\n255\n" + string.Concat(Enumerable.Repeat("64 ", 16)) + "\n");

        // Detection
        Assert.True(doc.IsGrayscale);
        Assert.False(doc.IsColor);
        Assert.False(doc.IsBitmap);

        // Geometry
        Assert.Equal(1.0, doc.AspectRatio, precision: 4);
        Assert.True(doc.IsSquare);

        // ASCII export round-trip contains header
        var ascii = doc.ToAsciiString();
        Assert.Contains("P2", ascii);
        Assert.Contains("4", ascii); // width/height
    }
}
