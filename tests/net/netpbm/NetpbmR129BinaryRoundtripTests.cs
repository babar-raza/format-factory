// Tests for NetpbmDocument.ToBinaryBytes() round-trip pixel accuracy for PGM/PPM.
// Sprint: FORMAT-FACTORY-NETPBM-BINARY-ROUNDTRIP-20260626
// Ledger: R129-GOVERNED-DOTNET-NETPBM-BINARY-ROUNDTRIP-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R129: NetpbmDocument.ToBinaryBytes() serializes to binary Netpbm (P5/P6).
/// Round-trip: ASCII → ToBinaryBytes → LoadStream → pixel values preserved.
/// Binary PGM (P5) and binary PPM (P6) formats are tested. MaxValue round-trip
/// is also verified (loaded doc reports same MaxValue as original).
/// </summary>
public class NetpbmR129BinaryRoundtripTests
{
    private static NetpbmDocument LoadAsciiPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument LoadAsciiPpm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    private static NetpbmDocument ReloadFromBinary(byte[] binaryBytes)
    {
        using var ms = new MemoryStream(binaryBytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- PGM binary round-trip ----

    [Fact]
    public void ToBinaryBytes_PgmP2_RoundTrip_SameDimensions()
    {
        const string pgm = "P2\n3 2\n255\n10 20 30\n40 50 60\n";
        var doc = LoadAsciiPgm(pgm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(doc.Width, reloaded.Width);
        Assert.Equal(doc.Height, reloaded.Height);
    }

    [Fact]
    public void ToBinaryBytes_PgmP2_RoundTrip_SameFormat()
    {
        const string pgm = "P2\n2 2\n255\n0 128\n200 255\n";
        var doc = LoadAsciiPgm(pgm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(NetpbmFormat.PGM_P5, reloaded.Format);
    }

    [Fact]
    public void ToBinaryBytes_PgmP2_RoundTrip_PixelValuesPreserved()
    {
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var doc = LoadAsciiPgm(pgm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(doc.GetPixel(0, 0), reloaded.GetPixel(0, 0));
        Assert.Equal(doc.GetPixel(0, 1), reloaded.GetPixel(0, 1));
        Assert.Equal(doc.GetPixel(1, 0), reloaded.GetPixel(1, 0));
        Assert.Equal(doc.GetPixel(1, 1), reloaded.GetPixel(1, 1));
    }

    [Fact]
    public void ToBinaryBytes_PgmP2_RoundTrip_MaxValuePreserved()
    {
        const string pgm = "P2\n1 1\n255\n128\n";
        var doc = LoadAsciiPgm(pgm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(doc.MaxValue, reloaded.MaxValue);
    }

    // ---- PPM binary round-trip ----

    [Fact]
    public void ToBinaryBytes_PpmP3_RoundTrip_SameDimensions()
    {
        const string ppm = "P3\n2 2\n255\n100 100 100  200 200 200\n50 50 50  150 150 150\n";
        var doc = LoadAsciiPpm(ppm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(doc.Width, reloaded.Width);
        Assert.Equal(doc.Height, reloaded.Height);
    }

    [Fact]
    public void ToBinaryBytes_PpmP3_RoundTrip_SameFormat()
    {
        const string ppm = "P3\n1 1\n255\n255 0 128\n";
        var doc = LoadAsciiPpm(ppm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        Assert.Equal(NetpbmFormat.PPM_P6, reloaded.Format);
    }

    [Fact]
    public void ToBinaryBytes_PpmP3_RoundTrip_PixelColorPreserved()
    {
        const string ppm = "P3\n1 1\n255\n200 100 50\n";
        var doc = LoadAsciiPpm(ppm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        var (r, g, b) = reloaded.GetPixelColor(0, 0);
        Assert.Equal(200, r);
        Assert.Equal(100, g);
        Assert.Equal(50, b);
    }

    // ---- Binary output is non-null and non-empty ----

    [Fact]
    public void ToBinaryBytes_NonNullResult()
    {
        const string pgm = "P2\n1 1\n255\n0\n";
        var doc = LoadAsciiPgm(pgm);
        Assert.NotNull(doc.ToBinaryBytes());
    }

    [Fact]
    public void ToBinaryBytes_NonEmptyResult()
    {
        const string pgm = "P2\n2 2\n255\n1 2\n3 4\n";
        var doc = LoadAsciiPgm(pgm);
        var binary = doc.ToBinaryBytes();
        Assert.True(binary.Length > 0, "Binary bytes should be non-empty");
    }

    // ---- Dogfood: multi-pixel PPM round-trip ----

    [Fact]
    public void DogfoodPipeline_PpmRoundTrip_AllPixelsMatch()
    {
        const string ppm = "P3\n2 3\n255\n0 0 0  255 255 255\n128 64 32  32 64 128\n255 0 128  0 255 64\n";
        var doc = LoadAsciiPpm(ppm);

        var binary = doc.ToBinaryBytes();
        var reloaded = ReloadFromBinary(binary);

        for (int row = 0; row < doc.Height; row++)
        {
            for (int col = 0; col < doc.Width; col++)
            {
                var orig = doc.GetPixelColor(row, col);
                var got = reloaded.GetPixelColor(row, col);
                Assert.Equal(orig, got);
            }
        }
    }
}
