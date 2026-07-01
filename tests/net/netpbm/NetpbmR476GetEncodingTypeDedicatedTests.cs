// Tests for NetpbmImage.GetEncodingType dedicated coverage.
// Sprint: ff-sprint-s458-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R476

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R476: Dedicated tests for NetpbmImage.GetEncodingType().
/// PBM returns non-null non-empty string.
/// PGM returns non-null non-empty string.
/// PPM returns non-null non-empty string.
/// Width unchanged after GetEncodingType.
/// Height unchanged after GetEncodingType.
/// Format unchanged after GetEncodingType.
/// MaxValue unchanged after GetEncodingType.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PGM encoding type is non-null.
/// Dogfood: 4x4 PPM encoding type is non-null.
/// Dogfood: PBM encoding type is non-null.
/// </summary>
public class NetpbmR476GetEncodingTypeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetEncodingType_PBM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        string enc = img.GetEncodingType();
        Assert.False(string.IsNullOrEmpty(enc));
    }

    [Fact]
    public void GetEncodingType_PGM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string enc = img.GetEncodingType();
        Assert.False(string.IsNullOrEmpty(enc));
    }

    [Fact]
    public void GetEncodingType_PPM_ReturnsNonNullNonEmpty()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        string enc = img.GetEncodingType();
        Assert.False(string.IsNullOrEmpty(enc));
    }

    [Fact]
    public void GetEncodingType_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetEncodingType();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetEncodingType_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetEncodingType();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetEncodingType_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetEncodingType();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetEncodingType_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetEncodingType();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetEncodingType_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetEncodingType();
        string second = img.GetEncodingType();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_EncodingTypeNotNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetEncodingType());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_EncodingTypeNotNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetEncodingType());
    }

    [Fact]
    public void DogfoodPipeline_PBM_EncodingTypeNotNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetEncodingType());
    }
}
