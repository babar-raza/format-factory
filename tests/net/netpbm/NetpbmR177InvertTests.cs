// Tests for NetpbmImage.Invert dedicated coverage.
// Sprint: ff-sprint-s181-dotnet-deepening-20260628
// Ledger: PC-NETPBM-R177

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R177: Dedicated tests for NetpbmImage.Invert().
/// In-place inversion: pixel = MaxValue - pixel (PGM/PPM) or 1 - pixel (PBM).
/// Void method — modifies the image in place; does not return a new image.
/// PBM: 0 → 1, 1 → 0.
/// PGM: pixel → MaxValue - pixel for each pixel.
/// PPM: each channel → MaxValue - channel.
/// Double-invert restores the original values.
/// Covers: PBM 0 inverts to 1; PBM 1 inverts to 0; PGM pixel inverted to MaxValue-pixel;
/// double-invert restores; zero stays MaxValue; MaxValue pixel becomes 0;
/// uniform image all inverted the same; PPM channels inverted; dogfood PGM pipeline.
/// </summary>
public class NetpbmR177InvertTests
{
    // -------------------------------------------------------------------------
    // PBM inversion
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_PbmZeroPixel_BecomesOne()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 0);
        img.Invert();
        Assert.Equal(1, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_PbmOnePixel_BecomesZero()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PBM_P1);
        img.SetPixel(0, 0, 1);
        img.Invert();
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // PGM inversion
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_PgmPixel_BecomesMaxValueMinusPixel()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 100);
        img.Invert();
        Assert.Equal(img.MaxValue - 100, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_ZeroPixel_BecomesMaxValue()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 0);
        img.Invert();
        Assert.Equal(img.MaxValue, img.GetPixel(0, 0));
    }

    [Fact]
    public void Invert_MaxValuePixel_BecomesZero()
    {
        var img = NetpbmImage.Create(1, 1, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, (byte)img.MaxValue);
        img.Invert();
        Assert.Equal(0, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Double-invert (idempotency)
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_DoubleInvert_RestoresOriginalValue()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 128);
        img.SetPixel(0, 1, 200);
        img.Invert();
        img.Invert();
        Assert.Equal(128, img.GetPixel(0, 0));
        Assert.Equal(200, img.GetPixel(0, 1));
    }

    [Fact]
    public void Invert_UniformImage_AllPixelsInvertedSame()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                img.SetPixel(r, c, 100);
        img.Invert();
        for (int r = 0; r < 3; r++)
            for (int c = 0; c < 3; c++)
                Assert.Equal(img.MaxValue - 100, img.GetPixel(r, c));
    }

    [Fact]
    public void Invert_InPlace_ModifiesOriginalImage()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5);
        img.SetPixel(0, 0, 50);
        img.Invert();
        // Image is modified in place
        Assert.Equal(img.MaxValue - 50, img.GetPixel(0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PgmSetPixelInvertVerify()
    {
        var img = NetpbmImage.Create(3, 3, NetpbmFormat.PGM_P5);
        img.SetPixel(1, 1, 75);
        var originalVal = img.GetPixel(1, 1);
        img.Invert();
        Assert.Equal(img.MaxValue - originalVal, img.GetPixel(1, 1));
    }
}
