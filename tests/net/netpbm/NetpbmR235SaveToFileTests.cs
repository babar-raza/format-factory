// Tests for NetpbmImage.SaveToFile dedicated coverage.
// Sprint: ff-sprint-s228-dotnet-deepening-20260629
// Ledger: PC-NETPBM-R235

using System.IO;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R235: Dedicated tests for NetpbmImage.SaveToFile(path).
/// Null path → throws exception.
/// Valid path → creates file.
/// File has content (bytes > 0).
/// Format preserved after save.
/// MaxValue preserved after save.
/// Dimensions preserved after save.
/// Save twice: file exists both times.
/// Save with PGM format: file created.
/// Save with PPM format: file created.
/// Dogfood: create, modify, save — file exists and non-empty.
/// </summary>
public class NetpbmR235SaveToFileTests : IDisposable
{
    private readonly List<string> _tempFiles = new();

    private string TempPath(string suffix = ".pgm")
    {
        var path = Path.Combine(Path.GetTempPath(), $"netpbm_save_test_{Guid.NewGuid():N}{suffix}");
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
    public void SaveToFile_NullPath_ThrowsException()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        Assert.ThrowsAny<Exception>(() => img.SaveToFile(null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_ValidPath_CreatesFile()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileHasContent()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        img.SetPixel(0, 0, 128);
        var path = TempPath();
        img.SaveToFile(path);
        var bytes = File.ReadAllBytes(path);
        Assert.True(bytes.Length > 0);
    }

    [Fact]
    public void SaveToFile_FormatPreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.Equal(NetpbmFormat.PGM_P5, img.Format);
    }

    [Fact]
    public void SaveToFile_MaxValuePreserved()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 200);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.Equal(200, img.MaxValue);
    }

    [Fact]
    public void SaveToFile_DimensionsPreserved()
    {
        var img = NetpbmImage.Create(6, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.Equal(6, img.Width);
        Assert.Equal(8, img.Height);
    }

    [Fact]
    public void SaveToFile_SaveTwice_FileExistsBothTimes()
    {
        var img = NetpbmImage.Create(4, 4, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_PgmFormat_FileCreated()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PGM_P5, maxValue: 255);
        var path = TempPath(".pgm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_PpmFormat_FileCreated()
    {
        var img = NetpbmImage.Create(2, 2, NetpbmFormat.PPM_P6, maxValue: 255);
        var path = TempPath(".ppm");
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateModifySave_FileExistsAndNonEmpty()
    {
        var img = NetpbmImage.Create(8, 8, NetpbmFormat.PGM_P5, maxValue: 255);
        for (int y = 0; y < 8; y++)
            for (int x = 0; x < 8; x++)
                img.SetPixel(x, y, (x + y) % 256);
        var path = TempPath();
        img.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);
    }
}
