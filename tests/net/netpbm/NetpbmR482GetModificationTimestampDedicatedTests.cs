// Tests for NetpbmImage.GetModificationTimestamp dedicated coverage.
// Sprint: ff-sprint-s464-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R482

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R482: Dedicated tests for NetpbmImage.GetModificationTimestamp().
/// Returns non-null string.
/// Width unchanged after GetModificationTimestamp.
/// Height unchanged after GetModificationTimestamp.
/// Format unchanged after GetModificationTimestamp.
/// MaxValue unchanged after GetModificationTimestamp.
/// Idempotent (called twice same result).
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Dogfood: 4x4 PGM modification timestamp non-null.
/// Dogfood: 4x4 PPM modification timestamp non-null.
/// </summary>
public class NetpbmR482GetModificationTimestampDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetModificationTimestamp_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetModificationTimestamp());
    }

    [Fact]
    public void GetModificationTimestamp_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetModificationTimestamp();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetModificationTimestamp_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetModificationTimestamp();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetModificationTimestamp_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetModificationTimestamp();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetModificationTimestamp_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetModificationTimestamp();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetModificationTimestamp_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetModificationTimestamp();
        string second = img.GetModificationTimestamp();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetModificationTimestamp_PBM_NonNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetModificationTimestamp());
    }

    [Fact]
    public void GetModificationTimestamp_PGM_NonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetModificationTimestamp());
    }

    [Fact]
    public void GetModificationTimestamp_PPM_NonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetModificationTimestamp());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_ModTimestampNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetModificationTimestamp());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_ModTimestampNonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetModificationTimestamp());
    }
}
