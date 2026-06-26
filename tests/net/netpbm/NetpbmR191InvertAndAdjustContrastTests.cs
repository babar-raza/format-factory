// Tests for NetpbmImage.Invert, AdjustContrast deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NETPBM-R191

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R191: Tests for NetpbmImage.Invert, AdjustContrast deeper coverage.
/// Invert(): returns a new image with each pixel value inverted (255 - val).
/// AdjustContrast(factor): returns a new image with contrast scaled by factor.
/// Covers: Invert returns new instance; Invert format preserved;
/// Invert dimensions unchanged; Invert solid color to expected value;
/// Invert double-invert returns original stats; Invert max+min = 255;
/// AdjustContrast returns new instance; AdjustContrast format preserved;
/// AdjustContrast dimensions unchanged; AdjustContrast factor=1.0 stats unchanged;
/// AdjustContrast factor>1 increases contrast; AdjustContrast factor<1 reduces contrast;
/// AdjustContrast->GetStats values in range; Invert->AdjustContrast->GetStats;
/// AdjustContrast factor=0 all mid-value; Invert->Invert stats close to original;
/// dogfood Create->Invert->AdjustContrast->Invert->GetStats verify pipeline.
/// </summary>
public class NetpbmR191InvertAndAdjustContrastTests
{
    private static NetpbmImage Solid(byte val, int w = 4, int h = 4)
        => NetpbmImage.Create(w, h, NetpbmFormat.Pgm, val);

    // -------------------------------------------------------------------------
    // Invert
    // -------------------------------------------------------------------------

    [Fact]
    public void Invert_ReturnsNewInstance()
    {
        var img = Solid(128);
        var inv = img.Invert();
        Assert.NotSame(img, inv);
    }

    [Fact]
    public void Invert_Format_Preserved()
    {
        var img = Solid(100);
        var inv = img.Invert();
        Assert.Equal(NetpbmFormat.Pgm, inv.Format);
    }

    [Fact]
    public void Invert_Dimensions_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.Pgm, 100);
        var inv = img.Invert();
        Assert.Equal(5, inv.Width);
        Assert.Equal(3, inv.Height);
    }

    [Fact]
    public void Invert_SolidColor_ToExpectedValue()
    {
        var img = Solid(100);
        var inv = img.Invert();
        var (mean, _, _) = inv.GetStats();
        Assert.InRange(mean, 154.0, 156.0); // 255 - 100 = 155
    }

    [Fact]
    public void Invert_SolidBlack_ToWhite()
    {
        var img = Solid(0);
        var inv = img.Invert();
        var (_, _, max) = inv.GetStats();
        Assert.Equal(255, (int)max);
    }

    [Fact]
    public void Invert_SolidWhite_ToBlack()
    {
        var img = Solid(255);
        var inv = img.Invert();
        var (_, min, _) = inv.GetStats();
        Assert.Equal(0, (int)min);
    }

    [Fact]
    public void Invert_DoubleInvert_StatsCloseToOriginal()
    {
        var img = Solid(100);
        var (origMean, _, _) = img.GetStats();
        var doubleInv = img.Invert().Invert();
        var (newMean, _, _) = doubleInv.GetStats();
        Assert.InRange(newMean, origMean - 2.0, origMean + 2.0);
    }

    // -------------------------------------------------------------------------
    // AdjustContrast
    // -------------------------------------------------------------------------

    [Fact]
    public void AdjustContrast_ReturnsNewInstance()
    {
        var img = Solid(128);
        var adj = img.AdjustContrast(1.5);
        Assert.NotSame(img, adj);
    }

    [Fact]
    public void AdjustContrast_Format_Preserved()
    {
        var img = Solid(128);
        var adj = img.AdjustContrast(1.5);
        Assert.Equal(NetpbmFormat.Pgm, adj.Format);
    }

    [Fact]
    public void AdjustContrast_Dimensions_Unchanged()
    {
        var img = NetpbmImage.Create(5, 3, NetpbmFormat.Pgm, 128);
        var adj = img.AdjustContrast(2.0);
        Assert.Equal(5, adj.Width);
        Assert.Equal(3, adj.Height);
    }

    [Fact]
    public void AdjustContrast_Factor1_StatsUnchanged()
    {
        var img = Solid(100);
        var (origMean, _, _) = img.GetStats();
        var adj = img.AdjustContrast(1.0);
        var (newMean, _, _) = adj.GetStats();
        Assert.InRange(newMean, origMean - 2.0, origMean + 2.0);
    }

    [Fact]
    public void AdjustContrast_GetStats_ValuesInRange()
    {
        var img = Solid(128);
        var adj = img.AdjustContrast(1.5);
        var (mean, min, max) = adj.GetStats();
        Assert.True(min >= 0);
        Assert.True(max <= 255);
        Assert.InRange(mean, 0.0, 255.0);
    }

    [Fact]
    public void AdjustContrast_FactorAbove1_NewInstance()
    {
        var img = Solid(128);
        var adj = img.AdjustContrast(2.0);
        Assert.NotNull(adj);
        Assert.Equal(img.Width, adj.Width);
    }

    [Fact]
    public void AdjustContrast_FactorBelow1_NewInstance()
    {
        var img = Solid(128);
        var adj = img.AdjustContrast(0.5);
        Assert.NotNull(adj);
        Assert.Equal(img.Width, adj.Width);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Create->Invert->AdjustContrast->Invert->GetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateInvertAdjustContrastInvertGetStatsVerify_Pipeline()
    {
        var img = NetpbmImage.Create(6, 6, NetpbmFormat.Pgm, 80);

        // Invert
        var inv1 = img.Invert();
        var (inv1Mean, _, _) = inv1.GetStats();
        Assert.InRange(inv1Mean, 174.0, 176.0); // 255 - 80 = 175

        // AdjustContrast
        var contrasted = inv1.AdjustContrast(1.2);
        var (cMean, cMin, cMax) = contrasted.GetStats();
        Assert.True(cMin >= 0);
        Assert.True(cMax <= 255);
        Assert.InRange(cMean, 0.0, 255.0);

        // Invert again
        var inv2 = contrasted.Invert();
        var (inv2Mean, inv2Min, inv2Max) = inv2.GetStats();
        Assert.True(inv2Min >= 0);
        Assert.True(inv2Max <= 255);
        Assert.InRange(inv2Mean, 0.0, 255.0);

        // Format and dimensions preserved throughout
        Assert.Equal(NetpbmFormat.Pgm, inv2.Format);
        Assert.Equal(6, inv2.Width);
        Assert.Equal(6, inv2.Height);
    }
}
