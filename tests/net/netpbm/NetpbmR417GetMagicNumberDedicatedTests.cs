// Tests for NetpbmImage.GetMagicNumber dedicated coverage.
// Sprint: ff-sprint-s399-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R417

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R417: Dedicated tests for NetpbmImage.GetMagicNumber().
/// PBM returns "P1" or "P4".
/// PGM returns "P2" or "P5".
/// PPM returns "P3" or "P6".
/// Width unchanged after GetMagicNumber.
/// Height unchanged after GetMagicNumber.
/// Format unchanged after GetMagicNumber.
/// MaxValue unchanged after GetMagicNumber.
/// Idempotent (called twice same result).
/// Result starts with "P".
/// Result non-null non-empty.
/// </summary>
public class NetpbmR417GetMagicNumberDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMagicNumber_PBM_ContainsPBMMagic()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string magic = img.GetMagicNumber();
        Assert.True(magic == "P1" || magic == "P4");
    }

    [Fact]
    public void GetMagicNumber_PGM_ContainsPGMMagic()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string magic = img.GetMagicNumber();
        Assert.True(magic == "P2" || magic == "P5");
    }

    [Fact]
    public void GetMagicNumber_PPM_ContainsPPMMagic()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string magic = img.GetMagicNumber();
        Assert.True(magic == "P3" || magic == "P6");
    }

    [Fact]
    public void GetMagicNumber_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetMagicNumber_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetMagicNumber_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetMagicNumber_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetMagicNumber();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetMagicNumber_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string first = img.GetMagicNumber();
        string second = img.GetMagicNumber();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ResultStartsWithP()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string magic = img.GetMagicNumber();
        Assert.StartsWith("P", magic);
    }

    [Fact]
    public void DogfoodPipeline_ResultNonNullNonEmpty()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string magic = img.GetMagicNumber();
        Assert.False(string.IsNullOrEmpty(magic));
    }
}
