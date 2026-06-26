// Tests for NetpbmImage.LoadFromFile dedicated coverage.
// Sprint: ff-sprint-s229-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R236

using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R236: Dedicated tests for NetpbmImage.LoadFromFile(path).
/// Null path → throws exception.
/// Nonexistent file → throws exception.
/// Valid file → returns non-null.
/// Loaded image has positive width.
/// Loaded image has positive height.
/// Loaded image has positive MaxValue.
/// Save-then-load: format preserved.
/// Save-then-load: dimensions preserved.
/// Save-then-load: pixel values preserved.
/// Dogfood: save PGM and PPM, both load successfully.
/// </summary>
public class NetpbmR236LoadFromFileTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".pgm")
    {
        var path = Path.Combine(Path.GetTempPath(), $"netpbm_load_test_{Guid.NewGuid():N}{suffix}");
        _tempFiles.Add(path);
        return path;
    }

    public void Dispose()
    {
        foreach (var f in _tempFiles)
            if (File.Exists(f)) File.Delete(f);
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFromFile_NullPath_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() => NetpbmImage.LoadFromFile(null!));
    }

    [Fact]
    public void LoadFromFile_NonexistentFile_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() => NetpbmImage.LoadFromFile("/no/such/file_xyz_999.pgm"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFromFile_ValidFile_ReturnsNonNull()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void LoadFromFile_LoadedImage_HasPositiveWidth()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.True(loaded.Width > 0);
    }

    [Fact]
    public void LoadFromFile_LoadedImage_HasPositiveHeight()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.True(loaded.Height > 0);
    }

    [Fact]
    public void LoadFromFile_LoadedImage_HasPositiveMaxValue()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.True(loaded.MaxValue > 0);
    }

    [Fact]
    public void LoadFromFile_SaveThenLoad_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.Equal(NetpbmFormat.PGM_P5, loaded.Format);
    }

    [Fact]
    public void LoadFromFile_SaveThenLoad_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.Equal(6, loaded.Width);
        Assert.Equal(8, loaded.Height);
    }

    [Fact]
    public void LoadFromFile_SaveThenLoad_PixelValuesPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(2, 2, 123);
        var path = TempPath();
        img.SaveToFile(path);
        var loaded = NetpbmImage.LoadFromFile(path);
        Assert.Equal(123, loaded.GetPixel(2, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SavePgmAndPpm_BothLoadSuccessfully()
    {
        var pgm = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var ppm = NetpbmImage.Create(4, 4, NetpbmFormat.PPM_P6, maxValue: 255);
        var pgmPath = TempPath(".pgm");
        var ppmPath = TempPath(".ppm");
        pgm.SaveToFile(pgmPath);
        ppm.SaveToFile(ppmPath);
        var loadedPgm = NetpbmImage.LoadFromFile(pgmPath);
        var loadedPpm = NetpbmImage.LoadFromFile(ppmPath);
        Assert.NotNull(loadedPgm);
        Assert.NotNull(loadedPpm);
    }
}
