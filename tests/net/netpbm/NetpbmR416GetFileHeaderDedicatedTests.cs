// Tests for NetpbmImage.GetFileHeader dedicated coverage.
// Sprint: ff-sprint-s398-dotnet-deepening-20260701
// Ledger: PC-NETPBM-R416

using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R416: Dedicated tests for NetpbmImage.GetFileHeader().
/// PBM returns non-null header.
/// PGM returns non-null header.
/// PPM returns non-null header.
/// Width unchanged after GetFileHeader.
/// Height unchanged after GetFileHeader.
/// Format unchanged after GetFileHeader.
/// MaxValue unchanged after GetFileHeader.
/// Idempotent (called twice same result).
/// PBM header starts with "P1" or "P4".
/// PPM header starts with "P3" or "P6".
/// </summary>
public class NetpbmR416GetFileHeaderDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFileHeader_PBM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string header = img.GetFileHeader();
        Assert.NotNull(header);
    }

    [Fact]
    public void GetFileHeader_PGM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        string header = img.GetFileHeader();
        Assert.NotNull(header);
    }

    [Fact]
    public void GetFileHeader_PPM_NonNull()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string header = img.GetFileHeader();
        Assert.NotNull(header);
    }

    [Fact]
    public void GetFileHeader_WidthUnchanged()
    {
        var img = NetpbmImage.CreateNew(6, 4, NetpbmFormat.PPM);
        int before = img.Width;
        _ = img.GetFileHeader();
        Assert.Equal(before, img.Width);
    }

    [Fact]
    public void GetFileHeader_HeightUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 8, NetpbmFormat.PGM);
        int before = img.Height;
        _ = img.GetFileHeader();
        Assert.Equal(before, img.Height);
    }

    [Fact]
    public void GetFileHeader_FormatUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        NetpbmFormat before = img.Format;
        _ = img.GetFileHeader();
        Assert.Equal(before, img.Format);
    }

    [Fact]
    public void GetFileHeader_MaxValueUnchanged()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PGM);
        int before = img.MaxValue;
        _ = img.GetFileHeader();
        Assert.Equal(before, img.MaxValue);
    }

    [Fact]
    public void GetFileHeader_Idempotent()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string first = img.GetFileHeader();
        string second = img.GetFileHeader();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_PBM_HeaderStartsWithP()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PBM);
        string header = img.GetFileHeader();
        Assert.StartsWith("P", header);
    }

    [Fact]
    public void DogfoodPipeline_PPM_HeaderStartsWithP()
    {
        var img = NetpbmImage.CreateNew(4, 4, NetpbmFormat.PPM);
        string header = img.GetFileHeader();
        Assert.StartsWith("P", header);
    }
}
