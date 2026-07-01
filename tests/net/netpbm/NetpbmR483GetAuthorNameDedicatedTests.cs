// Tests for NetpbmImage.GetAuthorName dedicated coverage.
// Sprint: ff-sprint-s465-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R483

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R483: Dedicated tests for NetpbmImage.GetAuthorName().
/// Returns non-null string (may be empty for new images).
/// Width unchanged after GetAuthorName.
/// Height unchanged after GetAuthorName.
/// Format unchanged after GetAuthorName.
/// MaxValue unchanged after GetAuthorName.
/// Idempotent (called twice same result).
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Dogfood: 4x4 PGM author non-null.
/// Dogfood: 4x4 PPM author non-null.
/// </summary>
public class NetpbmR483GetAuthorNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetAuthorName_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetAuthorName());
    }

    [Fact]
    public void GetAuthorName_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetAuthorName();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetAuthorName_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetAuthorName();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetAuthorName_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetAuthorName();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetAuthorName_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetAuthorName();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetAuthorName_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetAuthorName();
        string second = img.GetAuthorName();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetAuthorName_PBM_NonNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetAuthorName());
    }

    [Fact]
    public void GetAuthorName_PGM_NonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetAuthorName());
    }

    [Fact]
    public void GetAuthorName_PPM_NonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetAuthorName());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_AuthorNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetAuthorName());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_AuthorNonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetAuthorName());
    }
}
