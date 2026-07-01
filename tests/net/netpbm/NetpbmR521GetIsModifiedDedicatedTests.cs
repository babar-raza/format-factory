// Tests for NetpbmImage.GetIsModified dedicated coverage.
// Sprint: ff-sprint-s503-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R521

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R521: Dedicated tests for NetpbmImage.GetIsModified().
/// PBM newly created image returns false (not modified).
/// PGM newly created image returns false (not modified).
/// PPM newly created image returns false (not modified).
/// Width unchanged after GetIsModified.
/// Height unchanged after GetIsModified.
/// Format unchanged after GetIsModified.
/// MaxValue unchanged after GetIsModified.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline not modified.
/// Dogfood: PGM pipeline not modified.
/// Dogfood: PPM pipeline not modified.
/// </summary>
public class NetpbmR521GetIsModifiedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsModified_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetIsModified());
    }

    [Fact]
    public void GetIsModified_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetIsModified());
    }

    [Fact]
    public void GetIsModified_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetIsModified());
    }

    [Fact]
    public void GetIsModified_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsModified();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsModified_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsModified();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsModified_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsModified();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsModified_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsModified();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsModified_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsModified();
        bool second = img.GetIsModified();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_NotModified()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsModified();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_NotModified()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsModified();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_NotModified()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsModified();
        Assert.False(result);
    }
}
