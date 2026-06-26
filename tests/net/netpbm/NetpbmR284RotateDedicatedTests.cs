// Tests for NetpbmImage.Rotate dedicated coverage.
// Sprint: ff-sprint-s276-dotnet-deepening-20260630
// Ledger: PC-NETPBM-R284

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R284: Dedicated tests for NetpbmImage.Rotate(degrees).
/// Valid 90-degree rotation returns non-null.
/// Valid 180-degree rotation — width and height may swap or stay.
/// Rotate 0 degrees no exception.
/// Rotate 360 degrees no exception.
/// Format unchanged after rotate.
/// MaxValue unchanged after rotate.
/// Called twice no exception.
/// Dogfood: rotate 90 no exception; pixel count preserved.
/// Dogfood: rotate 180 no exception.
/// </summary>
public class NetpbmR284RotateDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Rotate_NinetyDegrees_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        var ex = Record.Exception(() => img.Rotate(90));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_OneEightyDegrees_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 3, NetpbmFormat.Pgm, 255);
        var ex = Record.Exception(() => img.Rotate(180));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_ZeroDegrees_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var ex = Record.Exception(() => img.Rotate(0));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_ThreeSixtyDegrees_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var ex = Record.Exception(() => img.Rotate(360));
        Assert.Null(ex);
    }

    [Fact]
    public void Rotate_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var fmt = img.Format;
        img.Rotate(90);
        Assert.Equal(fmt, img.Format);
    }

    [Fact]
    public void Rotate_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 200);
        img.Rotate(90);
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void Rotate_OneEightyDegrees_DimensionsPreserved()
    {
        // 180-degree rotation preserves dimensions
        var img = NetpbmImage.CreateNew(5, 3, NetpbmFormat.Pgm, 255);
        int w = img.Width;
        int h = img.Height;
        img.Rotate(180);
        Assert.Equal(w, img.Width);
        Assert.Equal(h, img.Height);
    }

    [Fact]
    public void Rotate_CalledTwice_NoException()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.Pgm, 255);
        var ex = Record.Exception(() => { img.Rotate(90); img.Rotate(90); });
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_RotateNinety_PixelCountPreserved()
    {
        var img = NetpbmImage.CreateNew(4, 3, NetpbmFormat.Pgm, 255);
        img.SetPixel(0, 0, 100);
        img.Rotate(90);
        // Width*Height should be same total pixels = 12
        Assert.Equal(12, img.Width * img.Height);
    }

    [Fact]
    public void DogfoodPipeline_RotateOneEighty_NoException()
    {
        var img = NetpbmImage.CreateNew(5, 4, NetpbmFormat.Pgm, 255);
        for (int r = 0; r < 4; r++)
            for (int c = 0; c < 5; c++)
                img.SetPixel(c, r, c * 10 + r * 30);
        var ex = Record.Exception(() => img.Rotate(180));
        Assert.Null(ex);
    }
}
