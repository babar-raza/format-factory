// Tests for NetpbmImage.GetCreationTimestamp dedicated coverage.
// Sprint: ff-sprint-s463-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R481

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R481: Dedicated tests for NetpbmImage.GetCreationTimestamp().
/// Returns non-null string.
/// Width unchanged after GetCreationTimestamp.
/// Height unchanged after GetCreationTimestamp.
/// Format unchanged after GetCreationTimestamp.
/// MaxValue unchanged after GetCreationTimestamp.
/// Idempotent (called twice same result).
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Dogfood: 4x4 PGM timestamp non-null.
/// Dogfood: 4x4 PPM timestamp non-null.
/// </summary>
public class NetpbmR481GetCreationTimestampDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCreationTimestamp_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetCreationTimestamp());
    }

    [Fact]
    public void GetCreationTimestamp_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetCreationTimestamp();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetCreationTimestamp_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetCreationTimestamp();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetCreationTimestamp_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetCreationTimestamp();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetCreationTimestamp_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetCreationTimestamp();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetCreationTimestamp_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetCreationTimestamp();
        string second = img.GetCreationTimestamp();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetCreationTimestamp_PBM_NonNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetCreationTimestamp());
    }

    [Fact]
    public void GetCreationTimestamp_PGM_NonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetCreationTimestamp());
    }

    [Fact]
    public void GetCreationTimestamp_PPM_NonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetCreationTimestamp());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_TimestampNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetCreationTimestamp());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_TimestampNonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetCreationTimestamp());
    }
}
