// Tests for NetpbmImage.GetFormatExtension dedicated coverage.
// Sprint: ff-sprint-s397-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R415

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R415: Dedicated tests for NetpbmImage.GetFormatExtension().
/// PBM returns ".pbm" (case-insensitive).
/// PGM returns ".pgm" (case-insensitive).
/// PPM returns ".ppm" (case-insensitive).
/// Width unchanged after GetFormatExtension.
/// Height unchanged after GetFormatExtension.
/// Format unchanged after GetFormatExtension.
/// MaxValue unchanged after GetFormatExtension.
/// Idempotent (called twice same result).
/// Result starts with '.'.
/// Result is non-null/non-empty.
/// </summary>
public class NetpbmR415GetFormatExtensionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormatExtension_PBM_ReturnsPbmExtension()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string ext = img.GetFormatExtension();
        Assert.Contains("pbm", ext, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void GetFormatExtension_PGM_ReturnsPgmExtension()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string ext = img.GetFormatExtension();
        Assert.Contains("pgm", ext, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void GetFormatExtension_PPM_ReturnsPpmExtension()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string ext = img.GetFormatExtension();
        Assert.Contains("ppm", ext, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void GetFormatExtension_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetFormatExtension();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFormatExtension_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetFormatExtension();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFormatExtension_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetFormatExtension();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFormatExtension_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetFormatExtension();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFormatExtension_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string first = img.GetFormatExtension();
        string second = img.GetFormatExtension();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ResultStartsWithDot()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string ext = img.GetFormatExtension();
        Assert.StartsWith(".", ext);
    }

    [Fact]
    public void DogfoodPipeline_ResultNonNullNonEmpty()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string ext = img.GetFormatExtension();
        Assert.False(string.IsNullOrEmpty(ext));
    }
}
