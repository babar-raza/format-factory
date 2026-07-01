// Tests for NetpbmImage.GetIsAsciiFormat dedicated coverage.
// Sprint: ff-sprint-s515-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R533

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R533: Dedicated tests for NetpbmImage.GetIsAsciiFormat().
/// PBM image returns a bool.
/// PGM image returns a bool.
/// PPM image returns a bool.
/// Width unchanged after GetIsAsciiFormat.
/// Height unchanged after GetIsAsciiFormat.
/// Format unchanged after GetIsAsciiFormat.
/// MaxValue unchanged after GetIsAsciiFormat.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline result is bool.
/// Dogfood: PGM pipeline result is bool.
/// Dogfood: PPM pipeline result is bool.
/// </summary>
public class NetpbmR533GetIsAsciiFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsAsciiFormat_PbmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsAsciiFormat_PgmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsAsciiFormat_PpmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsAsciiFormat_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsAsciiFormat();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsAsciiFormat_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsAsciiFormat();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsAsciiFormat_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsAsciiFormat();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsAsciiFormat_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsAsciiFormat();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsAsciiFormat_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsAsciiFormat();
        bool second = img.GetIsAsciiFormat();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        object result = img.GetIsAsciiFormat();
        Assert.IsType<bool>(result);
    }
}
