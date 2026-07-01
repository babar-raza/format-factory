// Tests for NetpbmImage.GetIsNewlyCreated dedicated coverage.
// Sprint: ff-sprint-s504-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R522

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R522: Dedicated tests for NetpbmImage.GetIsNewlyCreated().
/// PBM newly created image returns true.
/// PGM newly created image returns true.
/// PPM newly created image returns true.
/// Width unchanged after GetIsNewlyCreated.
/// Height unchanged after GetIsNewlyCreated.
/// Format unchanged after GetIsNewlyCreated.
/// MaxValue unchanged after GetIsNewlyCreated.
/// Idempotent (called twice same result).
/// Dogfood: PBM pipeline is newly created.
/// Dogfood: PGM pipeline is newly created.
/// Dogfood: PPM pipeline is newly created.
/// </summary>
public class NetpbmR522GetIsNewlyCreatedDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetIsNewlyCreated_PbmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePbm(4, 4);
        Assert.True(img.GetIsNewlyCreated());
    }

    [Fact]
    public void GetIsNewlyCreated_PgmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePgm(4, 4, 255);
        Assert.True(img.GetIsNewlyCreated());
    }

    [Fact]
    public void GetIsNewlyCreated_PpmImage_ReturnsTrue()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        Assert.True(img.GetIsNewlyCreated());
    }

    [Fact]
    public void GetIsNewlyCreated_WidthUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Width;
        _ = img.GetIsNewlyCreated();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetIsNewlyCreated_HeightUnchanged()
    {
        var img = NetpbmImage.CreatePpm(6, 3, 255);
        int before = img.Height;
        _ = img.GetIsNewlyCreated();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetIsNewlyCreated_FormatUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        string before = img.Format;
        _ = img.GetIsNewlyCreated();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetIsNewlyCreated_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreatePgm(2, 2, 255);
        int before = img.MaxValue;
        _ = img.GetIsNewlyCreated();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetIsNewlyCreated_Idempotent()
    {
        var img = NetpbmImage.CreatePpm(4, 4, 255);
        bool first = img.GetIsNewlyCreated();
        bool second = img.GetIsNewlyCreated();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PbmImage_IsNewlyCreated()
    {
        var img = NetpbmImage.CreatePbm(8, 8);
        bool result = img.GetIsNewlyCreated();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PgmImage_IsNewlyCreated()
    {
        var img = NetpbmImage.CreatePgm(8, 8, 255);
        bool result = img.GetIsNewlyCreated();
        Assert.True(result);
    }

    [Fact]
    public void DogfoodPipeline_PpmImage_IsNewlyCreated()
    {
        var img = NetpbmImage.CreatePpm(8, 8, 255);
        bool result = img.GetIsNewlyCreated();
        Assert.True(result);
    }
}
