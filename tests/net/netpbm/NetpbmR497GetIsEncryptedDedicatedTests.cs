// Tests for NetpbmImage.GetIsEncrypted dedicated coverage.
// Sprint: ff-sprint-s479-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R497

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R497: Dedicated tests for NetpbmImage.GetIsEncrypted().
/// PBM returns false (Netpbm format has no encryption).
/// PGM returns false (Netpbm format has no encryption).
/// PPM returns false (Netpbm format has no encryption).
/// Width unchanged after GetIsEncrypted.
/// Height unchanged after GetIsEncrypted.
/// Format unchanged after GetIsEncrypted.
/// MaxValue unchanged after GetIsEncrypted.
/// Idempotent (called twice same result).
/// Dogfood: 4x4 PBM not encrypted.
/// Dogfood: 4x4 PGM not encrypted.
/// Dogfood: 4x4 PPM not encrypted.
/// </summary>
public class NetpbmR497GetIsEncryptedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsEncrypted_PBM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsEncrypted());
    }

    [Fact]
    public void GetIsEncrypted_PGM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsEncrypted());
    }

    [Fact]
    public void GetIsEncrypted_PPM_ReturnsFalse()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsEncrypted());
    }

    [Fact]
    public void GetIsEncrypted_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Width;
        _ = img.GetIsEncrypted();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsEncrypted_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.Height;
        _ = img.GetIsEncrypted();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsEncrypted_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        string before = img.Format;
        _ = img.GetIsEncrypted();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsEncrypted_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        int before = img.MaxValue;
        _ = img.GetIsEncrypted();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsEncrypted_Idempotent()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        bool first = img.GetIsEncrypted();
        bool second = img.GetIsEncrypted();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_FourByFourPBM_NotEncrypted()
    {
        var img = NetpbmImage.CreatePBM(4, 4);
        Assert.False(img.GetIsEncrypted());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPGM_NotEncrypted()
    {
        var img = NetpbmImage.CreatePGM(4, 4, 255);
        Assert.False(img.GetIsEncrypted());
    }

    [Fact]
    public void DogfoodPipeline_FourByFourPPM_NotEncrypted()
    {
        var img = NetpbmImage.CreatePPM(4, 4, 255);
        Assert.False(img.GetIsEncrypted());
    }
}
