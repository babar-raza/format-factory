// Tests for NetpbmImage.GetFormatDescription dedicated coverage.
// Sprint: ff-sprint-s461-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R479

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R479: Dedicated tests for NetpbmImage.GetFormatDescription().
/// PBM returns non-null non-empty string.
/// PGM returns non-null non-empty string.
/// PPM returns non-null non-empty string.
/// Width unchanged after GetFormatDescription.
/// Height unchanged after GetFormatDescription.
/// Format unchanged after GetFormatDescription.
/// MaxValue unchanged after GetFormatDescription.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM description is non-null.
/// Dogfood: 4x4 PPM description is non-null.
/// Dogfood: PBM description is non-null.
/// </summary>
public class NetpbmR479GetFormatDescriptionDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormatDescription_PBM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string desc = img.GetFormatDescription();
        Assert.False(string.IsNullOrEmpty(desc));
    }

    [Fact]
    public void GetFormatDescription_PGM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string desc = img.GetFormatDescription();
        Assert.False(string.IsNullOrEmpty(desc));
    }

    [Fact]
    public void GetFormatDescription_PPM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string desc = img.GetFormatDescription();
        Assert.False(string.IsNullOrEmpty(desc));
    }

    [Fact]
    public void GetFormatDescription_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFormatDescription_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFormatDescription_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFormatDescription_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetFormatDescription();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFormatDescription_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetFormatDescription();
        string second = img.GetFormatDescription();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_DescriptionNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetFormatDescription());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_DescriptionNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetFormatDescription());
    }

    [Fact]
    public void DogfoodPipeline_PBM_DescriptionNotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetFormatDescription());
    }
}
