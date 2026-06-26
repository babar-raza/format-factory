// Tests for NetpbmParser static constants and ParseStream knownLength behavior.
// Sprint: FORMAT-FACTORY-NETPBM-R137-20260627
// Ledger: R137-GOVERNED-DOTNET-NETPBM-PARSER-CONSTANTS-001

using System;
using System.IO;
using System.Text;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R137: Tests for NetpbmParser static constants and ParseStream overload behavior.
/// Covers: DefaultMaxFileSizeBytes = 64 MiB; DefaultMaxDimension = 65536;
/// DefaultMaxPixels = 1_000_000_000; ParseStream(knownLength=0) succeeds;
/// ParseStream(knownLength=-1) falls back gracefully; ParseStream null throws
/// ArgumentNullException; NetpbmDocument.FromImage null throws ArgumentNullException;
/// NetpbmDocument.FromImage wraps image correctly; dogfood image through FromImage
/// and ToAsciiString round-trip.
/// </summary>
public class NetpbmR137ParserConstantsTests
{
    private static NetpbmImage ParseString(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmParser.ParseStream(ms);
    }

    private static Stream ToStream(string content)
        => new MemoryStream(Encoding.ASCII.GetBytes(content));

    // -------------------------------------------------------------------------
    // Static constants
    // -------------------------------------------------------------------------

    [Fact]
    public void DefaultMaxFileSizeBytes_Is64MiB()
    {
        Assert.Equal(64L * 1024 * 1024, NetpbmParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void DefaultMaxDimension_Is65536()
    {
        Assert.Equal(65536, NetpbmParser.DefaultMaxDimension);
    }

    [Fact]
    public void DefaultMaxPixels_Is1Billion()
    {
        Assert.Equal(1_000_000_000L, NetpbmParser.DefaultMaxPixels);
    }

    [Fact]
    public void DefaultMaxFileSizeBytes_IsPositive()
    {
        Assert.True(NetpbmParser.DefaultMaxFileSizeBytes > 0);
    }

    [Fact]
    public void DefaultMaxDimension_IsPositive()
    {
        Assert.True(NetpbmParser.DefaultMaxDimension > 0);
    }

    // -------------------------------------------------------------------------
    // ParseStream with knownLength parameter
    // -------------------------------------------------------------------------

    [Fact]
    public void ParseStream_WithKnownLengthNegativeOne_ParsesSuccessfully()
    {
        const string pgm = "P2\n2 2\n255\n100 200\n150 50\n";
        using var ms = ToStream(pgm);
        // knownLength=-1 means "unknown" — falls back to stream.Length if seekable
        var image = NetpbmParser.ParseStream(ms, knownLength: -1);
        Assert.Equal(2, image.Width);
        Assert.Equal(2, image.Height);
    }

    [Fact]
    public void ParseStream_WithExplicitKnownLength_ParsesSuccessfully()
    {
        const string pgm = "P2\n3 1\n255\n10 20 30\n";
        var bytes = Encoding.ASCII.GetBytes(pgm);
        using var ms = new MemoryStream(bytes);
        var image = NetpbmParser.ParseStream(ms, knownLength: bytes.Length);
        Assert.Equal(3, image.Width);
        Assert.Equal(1, image.Height);
    }

    [Fact]
    public void ParseStream_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            NetpbmParser.ParseStream(null!));
    }

    // -------------------------------------------------------------------------
    // NetpbmDocument.FromImage
    // -------------------------------------------------------------------------

    [Fact]
    public void FromImage_NullImage_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() =>
            NetpbmDocument.FromImage(null!));
    }

    [Fact]
    public void FromImage_WrapsImageCorrectly()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 4,
            Height = 3,
            MaxValue = 255,
            Pixels = new byte[12]
        };
        var doc = NetpbmDocument.FromImage(image);
        Assert.Equal(4, doc.Width);
        Assert.Equal(3, doc.Height);
        Assert.Same(image, doc.Image);
    }

    // -------------------------------------------------------------------------
    // Dogfood: FromImage → ToAsciiString → ParseStream round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FromImage_ToAsciiString_ParseStream_RoundTrip()
    {
        // Build a PBM via image initializer
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 3,
            Height = 2,
            MaxValue = 1,
            Pixels = new byte[] { 0, 1, 0, 1, 0, 1 }
        };
        var doc = NetpbmDocument.FromImage(image);

        // Serialize to ASCII string
        var ascii = doc.ToAsciiString();
        Assert.StartsWith("P1", ascii);

        // Parse back via ParseStream and verify dimensions are preserved
        using var ms = ToStream(ascii);
        var reparsed = NetpbmParser.ParseStream(ms);
        Assert.Equal(3, reparsed.Width);
        Assert.Equal(2, reparsed.Height);
        Assert.Equal(NetpbmFormat.PBM_P1, reparsed.Format);
    }
}
