// Tests for NetpbmImage.GetComment dedicated coverage.
// Sprint: ff-sprint-s466-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R484

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R484: Dedicated tests for NetpbmImage.GetComment().
/// Returns non-null string (may be empty for new images).
/// Width unchanged after GetComment.
/// Height unchanged after GetComment.
/// Format unchanged after GetComment.
/// MaxValue unchanged after GetComment.
/// Idempotent (called twice same result).
/// PBM returns non-null.
/// PGM returns non-null.
/// PPM returns non-null.
/// Dogfood: 4x4 PGM comment non-null.
/// Dogfood: 4x4 PPM comment non-null.
/// </summary>
public class NetpbmR484GetCommentDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetComment_ReturnsNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetComment());
    }

    [Fact]
    public void GetComment_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetComment();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetComment_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetComment();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetComment_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetComment();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetComment_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetComment();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetComment_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string first = img.GetComment();
        string second = img.GetComment();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetComment_PBM_NonNull()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.NotNull(img.GetComment());
    }

    [Fact]
    public void GetComment_PGM_NonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetComment());
    }

    [Fact]
    public void GetComment_PPM_NonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetComment());
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_CommentNonNull()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.NotNull(img.GetComment());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_CommentNonNull()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.NotNull(img.GetComment());
    }
}
