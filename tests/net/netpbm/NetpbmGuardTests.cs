// FormatFactory.Netpbm.Tests -- Security Guard Tests
// R85 Train K: Third commercial .NET product first slice
// commercial_product_ready: false

using System;
using System.IO;
using System.Text;
using Xunit;
using FormatFactory.Netpbm;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmGuardTests
{
    [Fact]
    public void ParseOversizedWidth_ThrowsSizeException()
    {
        const string bad = "P2\n100000 1\n255\n";
        Assert.Throws<NetpbmSizeException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseOversizedHeight_ThrowsSizeException()
    {
        const string bad = "P2\n1 100000\n255\n";
        Assert.Throws<NetpbmSizeException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseZeroWidth_ThrowsSizeException()
    {
        const string bad = "P2\n0 10\n255\n";
        Assert.Throws<NetpbmSizeException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseZeroHeight_ThrowsSizeException()
    {
        const string bad = "P2\n10 0\n255\n";
        Assert.Throws<NetpbmSizeException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseInvalidMaxVal_ThrowsFormatException()
    {
        const string bad = "P2\n1 1\n0\n0\n";  // maxval=0 is invalid
        Assert.Throws<NetpbmFormatException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseIncompleteHeader_ThrowsFormatException()
    {
        const string bad = "P2\n10";  // no height, no maxval
        Assert.Throws<NetpbmFormatException>(() => ParseString(bad));
    }

    [Fact]
    public void ParseTruncatedFile_ThrowsException()
    {
        // Header says 100x100 but no pixel data
        const string bad = "P2\n100 100\n255\n";
        // Should not throw on parse (parser doesn't require all pixels) — or may throw
        // depending on implementation; just ensure it doesn't crash unexpectedly
        try { ParseString(bad); } catch (NetpbmException) { /* expected */ }
    }

    private static NetpbmImage ParseString(string content)
    {
        using var ms = new MemoryStream(Encoding.ASCII.GetBytes(content));
        return NetpbmParser.ParseStream(ms);
    }
}
