// Tests for NetpbmImage.GetDataSizeBytes dedicated coverage.
// Sprint: ff-sprint-s455-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R473

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R473: Dedicated tests for NetpbmImage.GetDataSizeBytes().
/// Returns positive value.
/// Width unchanged after GetDataSizeBytes.
/// Height unchanged after GetDataSizeBytes.
/// Format unchanged after GetDataSizeBytes.
/// MaxValue unchanged after GetDataSizeBytes.
/// Idempotent (called twice same result).
/// PBM returns positive.
/// PGM returns positive.
/// PPM returns positive.
/// Dogfood: 4x4 PGM data size is positive.
/// Dogfood: 4x4 PPM data size larger than PGM.
/// </summary>
public class NetpbmR473GetDataSizeBytesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDataSizeBytes_ReturnsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetDataSizeBytes() > 0);
    }

    [Fact]
    public void GetDataSizeBytes_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetDataSizeBytes();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetDataSizeBytes_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetDataSizeBytes();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetDataSizeBytes_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetDataSizeBytes();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetDataSizeBytes_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetDataSizeBytes();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetDataSizeBytes_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        long first = img.GetDataSizeBytes();
        long second = img.GetDataSizeBytes();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDataSizeBytes_PBM_Positive()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.True(img.GetDataSizeBytes() > 0);
    }

    [Fact]
    public void GetDataSizeBytes_PGM_Positive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetDataSizeBytes() > 0);
    }

    [Fact]
    public void GetDataSizeBytes_PPM_Positive()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(img.GetDataSizeBytes() > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_DataSizeIsPositive()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.True(img.GetDataSizeBytes() > 0);
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_LargerThanPGM()
    {
        var pgm = NetpbmImage.CreatePGM(4, 4, 255);
        var ppm = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.True(ppm.GetDataSizeBytes() > pgm.GetDataSizeBytes());
    }
}
