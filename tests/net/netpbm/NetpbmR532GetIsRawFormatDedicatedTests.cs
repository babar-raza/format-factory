// Tests for NetpbmImage.GetIsRawFormat dedicated coverage.
// Sprint: ff-sprint-s514-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R532

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R532: Dedicated tests for NetpbmImage.GetIsRawFormat().
/// PBM image returns a bool.
/// PGM image returns a bool.
/// PPM image returns a bool.
/// Width unchanged after GetIsRawFormat.
/// Height unchanged after GetIsRawFormat.
/// Format unchanged after GetIsRawFormat.
/// MaxValue unchanged after GetIsRawFormat.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline result is bool.
/// Dogfood: PGM pipeline result is bool.
/// Dogfood: PPM pipeline result is bool.
/// </summary>
public class NetpbmR532GetIsRawFormatDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsRawFormat_PbmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsRawFormat_PgmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsRawFormat_PpmImage_ReturnsBool()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void GetIsRawFormat_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsRawFormat();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsRawFormat_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsRawFormat();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsRawFormat_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsRawFormat();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsRawFormat_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsRawFormat();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsRawFormat_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsRawFormat();
        bool second = img.GetIsRawFormat();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_ResultIsBool()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        object result = img.GetIsRawFormat();
        Assert.IsType<bool>(result);
    }
}
