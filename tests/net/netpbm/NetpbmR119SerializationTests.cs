// Tests for NetpbmDocument serialization: ToAsciiString(), ToBinaryBytes(), SourcePath tracking.
// Sprint: FORMAT-FACTORY-NETPBM-SERIALIZATION-20260626
// Ledger: R119-GOVERNED-DOTNET-NETPBM-SERIALIZATION-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R119: NetpbmDocument serialization APIs — ToAsciiString() produces parseable PNM headers,
/// ToBinaryBytes() produces valid binary magic bytes, and SourcePath tracking works correctly.
/// </summary>
public class NetpbmR119SerializationTests
{
    private static NetpbmDocument MakeDoc(NetpbmFormat format, int width = 2, int height = 2, int maxVal = 255)
    {
        var image = new NetpbmImage { Format = format, Width = width, Height = height, MaxValue = maxVal };
        return NetpbmDocument.FromImage(image);
    }

    // ---- ToAsciiString: magic header ----

    [Fact]
    public void ToAsciiString_PbmP1_StartsWithP1()
    {
        var doc = MakeDoc(NetpbmFormat.PBM_P1, maxVal: 1);
        var str = doc.ToAsciiString();
        Assert.StartsWith("P1", str);
    }

    [Fact]
    public void ToAsciiString_PgmP2_StartsWithP2()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2);
        var str = doc.ToAsciiString();
        Assert.StartsWith("P2", str);
    }

    [Fact]
    public void ToAsciiString_PpmP3_StartsWithP3()
    {
        var doc = MakeDoc(NetpbmFormat.PPM_P3);
        var str = doc.ToAsciiString();
        Assert.StartsWith("P3", str);
    }

    // ---- ToAsciiString: dimensions in header ----

    [Fact]
    public void ToAsciiString_ContainsWidth()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, width: 5, height: 3);
        var str = doc.ToAsciiString();
        Assert.Contains("5", str);
    }

    [Fact]
    public void ToAsciiString_ContainsHeight()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, width: 5, height: 3);
        var str = doc.ToAsciiString();
        Assert.Contains("3", str);
    }

    [Fact]
    public void ToAsciiString_ContainsMaxVal_ForPgm()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2, maxVal: 200);
        var str = doc.ToAsciiString();
        Assert.Contains("200", str);
    }

    // ---- ToBinaryBytes: magic bytes ----

    [Fact]
    public void ToBinaryBytes_PbmP4_HasP4MagicBytes()
    {
        var doc = MakeDoc(NetpbmFormat.PBM_P4, maxVal: 1);
        var bytes = doc.ToBinaryBytes();
        Assert.True(bytes.Length >= 2);
        Assert.Equal((byte)'P', bytes[0]);
        Assert.Equal((byte)'4', bytes[1]);
    }

    [Fact]
    public void ToBinaryBytes_PgmP5_HasP5MagicBytes()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P5);
        var bytes = doc.ToBinaryBytes();
        Assert.True(bytes.Length >= 2);
        Assert.Equal((byte)'P', bytes[0]);
        Assert.Equal((byte)'5', bytes[1]);
    }

    [Fact]
    public void ToBinaryBytes_PpmP6_HasP6MagicBytes()
    {
        var doc = MakeDoc(NetpbmFormat.PPM_P6);
        var bytes = doc.ToBinaryBytes();
        Assert.True(bytes.Length >= 2);
        Assert.Equal((byte)'P', bytes[0]);
        Assert.Equal((byte)'6', bytes[1]);
    }

    [Fact]
    public void ToBinaryBytes_NonEmpty()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P5, width: 4, height: 4);
        var bytes = doc.ToBinaryBytes();
        Assert.NotEmpty(bytes);
    }

    // ---- SourcePath tracking ----

    [Fact]
    public void SourcePath_FromImage_IsNull()
    {
        var doc = MakeDoc(NetpbmFormat.PGM_P2);
        Assert.Null(doc.SourcePath);
    }

    [Fact]
    public void SourcePath_LoadStream_IsNull()
    {
        // Create a minimal P2 PGM in memory
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var bytes = Encoding.ASCII.GetBytes(pgm);
        using var ms = new MemoryStream(bytes);
        var doc = NetpbmDocument.LoadStream(ms);
        Assert.Null(doc.SourcePath);
    }

    // ---- LoadStream round-trip ----

    [Fact]
    public void LoadStream_PgmAscii_DimensionsCorrect()
    {
        const string pgm = "P2\n3 2\n255\n128 64 32\n16 8 4\n";
        var bytes = Encoding.ASCII.GetBytes(pgm);
        using var ms = new MemoryStream(bytes);
        var doc = NetpbmDocument.LoadStream(ms);
        Assert.Equal(3, doc.Width);
        Assert.Equal(2, doc.Height);
        Assert.Equal(NetpbmFormat.PGM_P2, doc.Format);
    }

    [Fact]
    public void LoadStream_PgmAscii_IsGrayscale()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var bytes = Encoding.ASCII.GetBytes(pgm);
        using var ms = new MemoryStream(bytes);
        var doc = NetpbmDocument.LoadStream(ms);
        Assert.True(doc.IsGrayscale);
        Assert.False(doc.IsColor);
        Assert.False(doc.IsBitmap);
    }

    // ---- Dogfood pipeline: FromImage → serialize → LoadStream → verify ----

    [Fact]
    public void DogfoodPipeline_FromImage_Serialize_LoadStream_RoundTrip()
    {
        // Build a small PGM document from an image
        var image = new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = 4, Height = 3, MaxValue = 255 };
        var doc = NetpbmDocument.FromImage(image);

        // Serialize to ASCII string
        var ascii = doc.ToAsciiString();
        Assert.StartsWith("P2", ascii);

        // Re-load from the ASCII string bytes
        var roundTripBytes = Encoding.ASCII.GetBytes(ascii);
        using var ms = new MemoryStream(roundTripBytes);
        var doc2 = NetpbmDocument.LoadStream(ms);

        // Dimensions should match
        Assert.Equal(doc.Width, doc2.Width);
        Assert.Equal(doc.Height, doc2.Height);
        Assert.Equal(doc.IsGrayscale, doc2.IsGrayscale);
        Assert.Equal(doc.PixelCount, doc2.PixelCount);
    }
}
