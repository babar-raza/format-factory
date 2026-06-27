// Tests for NetpbmImage.GetSharpnessScore dedicated coverage.
// Sprint: ff-sprint-s382-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R395

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R395: Dedicated tests for NetpbmImage.GetSharpnessScore().
/// Valid image returns ok.
/// Result is non-negative.
/// Width unchanged after GetSharpnessScore.
/// Height unchanged after GetSharpnessScore.
/// Format unchanged after GetSharpnessScore.
/// MaxValue unchanged after GetSharpnessScore.
/// Uniform image returns 0.0 (no edges).
/// Idempotent (called twice same result).
/// Dogfood: high-contrast edge image returns positive.
/// Dogfood: gradient image returns non-negative.
/// </summary>
public class NetpbmR395GetSharpnessScoreDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSharpnessScore_ValidImage_ReturnsOk()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        double score = img.GetSharpnessScore();
        Assert.True(score >= 0.0);
    }

    [Fact]
    public void GetSharpnessScore_ResultIsNonNegative()
    {
        var img = NetpbmImage.CreateNew(6, 6, NetpbmFormat.PPM);
        double score = img.GetSharpnessScore();
        Assert.True(score >= 0.0);
    }

    [Fact]
    public void GetSharpnessScore_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.PGM);
        int before = img.Width;
        _ = img.GetSharpnessScore();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetSharpnessScore_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(3, 7, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetSharpnessScore();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetSharpnessScore_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetSharpnessScore();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetSharpnessScore_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetSharpnessScore();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetSharpnessScore_UniformImage_ReturnsZero()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, 128);
        double score = img.GetSharpnessScore();
        Assert.Equal(0.0, score, 6);
    }

    [Fact]
    public void GetSharpnessScore_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        img.SetPixel(0, 0, 0);
        img.SetPixel(0, 1, 255);
        double first = img.GetSharpnessScore();
        double second = img.GetSharpnessScore();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HighContrastEdgeImage_ReturnsPositive()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        for (int r = 0; r < img.Height; r++)
            for (int c = 0; c < img.Width; c++)
                img.SetPixel(r, c, (r + c) % 2 == 0 ? 0 : 255);
        double score = img.GetSharpnessScore();
        Assert.True(score > 0.0);
    }

    [Fact]
    public void DogfoodPipeline_GradientImage_ReturnsNonNegative()
    {
        var img = NetpbmImage.CreateNew(8, 1, NetpbmFormat.PGM);
        for (int c = 0; c < img.Width; c++)
            img.SetPixel(0, c, c * 32);
        double score = img.GetSharpnessScore();
        Assert.True(score >= 0.0);
    }
}
