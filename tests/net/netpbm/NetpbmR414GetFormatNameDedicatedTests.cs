// Tests for NetpbmImage.GetFormatName dedicated coverage.
// Sprint: ff-sprint-s396-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R414

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R414: Dedicated tests for NetpbmImage.GetFormatName().
/// PBM returns non-null/non-empty string.
/// PGM returns non-null/non-empty string.
/// PPM returns non-null/non-empty string.
/// Width unchanged after GetFormatName.
/// Height unchanged after GetFormatName.
/// Format unchanged after GetFormatName.
/// MaxValue unchanged after GetFormatName.
/// Idempotent (called twice same result).
/// PBM name contains "PBM" or "pbm".
/// PPM name contains "PPM" or "ppm".
/// </summary>
public class NetpbmR414GetFormatNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormatName_PBM_NonNullNonEmpty()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string name = img.GetFormatName();
        Assert.False(string.IsNullOrEmpty(name));
    }

    [Fact]
    public void GetFormatName_PGM_NonNullNonEmpty()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string name = img.GetFormatName();
        Assert.False(string.IsNullOrEmpty(name));
    }

    [Fact]
    public void GetFormatName_PPM_NonNullNonEmpty()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string name = img.GetFormatName();
        Assert.False(string.IsNullOrEmpty(name));
    }

    [Fact]
    public void GetFormatName_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetFormatName();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFormatName_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetFormatName();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFormatName_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetFormatName();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFormatName_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetFormatName();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFormatName_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string first = img.GetFormatName();
        string second = img.GetFormatName();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PBM_NameContainsPBM()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string name = img.GetFormatName();
        Assert.Contains("PBM", name, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void DogfoodPipeline_PPM_NameContainsPPM()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string name = img.GetFormatName();
        Assert.Contains("PPM", name, StringComparison.OrdinalIgnoreCase);
    }
}
