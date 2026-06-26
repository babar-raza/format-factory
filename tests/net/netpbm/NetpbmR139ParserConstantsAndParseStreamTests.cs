// Tests for NetpbmParser constants and NetpbmParser.ParseStream.
// Sprint: ff-sprint-s134-dotnet-deepening-20260627
// Ledger: PC-NETPBM-R139

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R139: Tests for NetpbmParser constants (DefaultMaxFileSizeBytes, DefaultMaxDimension,
/// DefaultMaxPixels) and NetpbmParser.ParseStream(Stream, ...).
/// DefaultMaxFileSizeBytes = 64 MB; DefaultMaxDimension = 65536; DefaultMaxPixels = 1 billion.
/// ParseStream accepts a Stream of PPM/PGM/PBM content and returns a NetpbmImage.
/// Covers: DefaultMaxFileSizeBytes=64 MB; DefaultMaxDimension=65536; DefaultMaxPixels=1B;
/// all constants are positive; DefaultMaxFileSizeBytes > DefaultMaxDimension;
/// ParseStream null throws ArgumentNullException or exception; ParseStream valid PPM stream
/// returns non-null; ParseStream Width/Height>0; Format from PPM=PPM;
/// dogfood ParseStream on fixture verifies constants usage.
/// </summary>
public class NetpbmR139ParserConstantsAndParseStreamTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "netpbm", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    // -------------------------------------------------------------------------
    // Parser constants
    // -------------------------------------------------------------------------

    [Fact]
    public void NetpbmParser_DefaultMaxFileSizeBytes_Is64MB()
    {
        const long expected = 64L * 1024 * 1024;
        Assert.Equal(expected, NetpbmParser.DefaultMaxFileSizeBytes);
    }

    [Fact]
    public void NetpbmParser_DefaultMaxDimension_Is65536()
    {
        Assert.Equal(65536, NetpbmParser.DefaultMaxDimension);
    }

    [Fact]
    public void NetpbmParser_DefaultMaxPixels_Is1Billion()
    {
        const long expected = 1_000_000_000L;
        Assert.Equal(expected, NetpbmParser.DefaultMaxPixels);
    }

    [Fact]
    public void NetpbmParser_AllConstants_ArePositive()
    {
        Assert.True(NetpbmParser.DefaultMaxFileSizeBytes > 0);
        Assert.True(NetpbmParser.DefaultMaxDimension > 0);
        Assert.True(NetpbmParser.DefaultMaxPixels > 0);
    }

    [Fact]
    public void NetpbmParser_DefaultMaxFileSizeBytes_GreaterThan_DefaultMaxDimension()
    {
        Assert.True(NetpbmParser.DefaultMaxFileSizeBytes > NetpbmParser.DefaultMaxDimension);
    }

    // -------------------------------------------------------------------------
    // ParseStream: null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void NetpbmParser_ParseStream_NullStream_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() => NetpbmParser.ParseStream(null!));
    }

    // -------------------------------------------------------------------------
    // ParseStream: valid PPM stream (fixture-conditional)
    // -------------------------------------------------------------------------

    [Fact]
    public void NetpbmParser_ParseStream_ValidPpmStream_ReturnsNonNull()
    {
        var fixture = FixturePath("sample.ppm");
        if (!File.Exists(fixture))
            return;

        using var fs = File.OpenRead(fixture);
        var image = NetpbmParser.ParseStream(fs);
        Assert.NotNull(image);
    }

    [Fact]
    public void NetpbmParser_ParseStream_ValidPpmStream_WidthHeightPositive()
    {
        var fixture = FixturePath("sample.ppm");
        if (!File.Exists(fixture))
            return;

        using var fs = File.OpenRead(fixture);
        var image = NetpbmParser.ParseStream(fs);
        Assert.True(image.Width > 0);
        Assert.True(image.Height > 0);
    }

    [Fact]
    public void NetpbmParser_ParseStream_ValidPpmStream_FormatIsPpm()
    {
        var fixture = FixturePath("sample.ppm");
        if (!File.Exists(fixture))
            return;

        using var fs = File.OpenRead(fixture);
        var image = NetpbmParser.ParseStream(fs);
        Assert.Equal(NetpbmFormat.PPM, image.Format);
    }

    // -------------------------------------------------------------------------
    // Dogfood: ParseStream on fixture verifies constants vs actual dimensions
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ParseStream_Fixture_DimensionsWithinConstants()
    {
        var fixture = FixturePath("sample.ppm");
        if (!File.Exists(fixture))
            return;

        using var fs = File.OpenRead(fixture);
        var image = NetpbmParser.ParseStream(fs);

        // Fixture dimensions must be within parser constants
        Assert.True(image.Width <= NetpbmParser.DefaultMaxDimension);
        Assert.True(image.Height <= NetpbmParser.DefaultMaxDimension);
        Assert.True((long)image.Width * image.Height <= NetpbmParser.DefaultMaxPixels);
    }
}
