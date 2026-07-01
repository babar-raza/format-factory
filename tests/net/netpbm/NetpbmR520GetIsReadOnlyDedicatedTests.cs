// Tests for NetpbmImage.GetIsReadOnly dedicated coverage.
// Sprint: ff-sprint-s502-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R520

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R520: Dedicated tests for NetpbmImage.GetIsReadOnly().
/// PBM newly created image returns false (not read-only).
/// PGM newly created image returns false (not read-only).
/// PPM newly created image returns false (not read-only).
/// Width unchanged after GetIsReadOnly.
/// Height unchanged after GetIsReadOnly.
/// Format unchanged after GetIsReadOnly.
/// MaxValue unchanged after GetIsReadOnly.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline not read-only.
/// Dogfood: PGM pipeline not read-only.
/// Dogfood: PPM pipeline not read-only.
/// </summary>
public class NetpbmR520GetIsReadOnlyDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsReadOnly_PbmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.False(img.GetIsReadOnly());
    }

    [Fact]
    public void GetIsReadOnly_PgmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.False(img.GetIsReadOnly());
    }

    [Fact]
    public void GetIsReadOnly_PpmImage_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.False(img.GetIsReadOnly());
    }

    [Fact]
    public void GetIsReadOnly_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsReadOnly();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsReadOnly_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsReadOnly();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsReadOnly_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsReadOnly();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsReadOnly_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsReadOnly();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsReadOnly_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsReadOnly();
        bool second = img.GetIsReadOnly();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_NotReadOnly()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsReadOnly();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_NotReadOnly()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsReadOnly();
        Assert.False(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_NotReadOnly()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsReadOnly();
        Assert.False(result);
    }
}
