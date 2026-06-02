// R91 Train I: Netpbm .NET SetPixelColor Tests
// API: SetPixelColor(row, col, r, g, b) + SetPixel(row, col, value) round-trip
// Sprint: FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.IO;
using System.Linq;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR91SetPixelColorTests
{
    // -------------------------------------------------------------------------
    // PPM SetPixelColor tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixelColor_PPM_UpdatesInMemory()
    {
        var ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var path = WriteTempFile(ppm, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.SetPixelColor(0, 0, 255, 128, 64);
            var (r, g, b) = img.GetPixelColor(0, 0);
            Assert.Equal(255, r);
            Assert.Equal(128, g);
            Assert.Equal(64, b);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void SetPixelColor_PPM_RoundTrip_P3()
    {
        var ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var src = WriteTempFile(ppm, ".ppm");
        var dst = Path.GetTempFileName() + ".ppm";
        try
        {
            var img = NetpbmParser.Parse(src);
            img.SetPixelColor(1, 1, 100, 150, 200);
            NetpbmWriter.Write(img, dst);

            var reloaded = NetpbmParser.Parse(dst);
            var (r, g, b) = reloaded.GetPixelColor(1, 1);
            Assert.Equal(100, r);
            Assert.Equal(150, g);
            Assert.Equal(200, b);
        }
        finally
        {
            File.Delete(src);
            if (File.Exists(dst)) File.Delete(dst);
        }
    }

    [Fact]
    public void SetPixelColor_PPM_MultiplePixels_AllPersist()
    {
        var ppm = "P3\n3 3\n255\n" + string.Join("\n", new string[9].Select(_ => "0 0 0")) + "\n";
        var src = WriteTempFile(ppm, ".ppm");
        var dst = Path.GetTempFileName() + ".ppm";
        try
        {
            var img = NetpbmParser.Parse(src);
            img.SetPixelColor(0, 0, 10, 20, 30);
            img.SetPixelColor(1, 1, 40, 50, 60);
            img.SetPixelColor(2, 2, 70, 80, 90);
            NetpbmWriter.Write(img, dst);

            var reloaded = NetpbmParser.Parse(dst);
            var (r0, g0, b0) = reloaded.GetPixelColor(0, 0);
            Assert.Equal(10, r0); Assert.Equal(20, g0); Assert.Equal(30, b0);

            var (r1, g1, b1) = reloaded.GetPixelColor(1, 1);
            Assert.Equal(40, r1); Assert.Equal(50, g1); Assert.Equal(60, b1);

            var (r2, g2, b2) = reloaded.GetPixelColor(2, 2);
            Assert.Equal(70, r2); Assert.Equal(80, g2); Assert.Equal(90, b2);
        }
        finally
        {
            File.Delete(src);
            if (File.Exists(dst)) File.Delete(dst);
        }
    }

    [Fact]
    public void SetPixelColor_PPM_OutOfRange_ThrowsArgumentOutOfRange()
    {
        var ppm = "P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n";
        var path = WriteTempFile(ppm, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<ArgumentOutOfRangeException>(() => img.SetPixelColor(9, 0, 0, 0, 0));
            Assert.Throws<ArgumentOutOfRangeException>(() => img.SetPixelColor(0, 9, 0, 0, 0));
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // PGM SetPixel tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_PGM_UpdatesInMemory()
    {
        var pgm = "P2\n3 1\n255\n0 0 0\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.SetPixel(0, 1, 128);
            Assert.Equal(128, img.GetPixel(0, 1));
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void SetPixel_PGM_RoundTrip()
    {
        var pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var src = WriteTempFile(pgm, ".pgm");
        var dst = Path.GetTempFileName() + ".pgm";
        try
        {
            var img = NetpbmParser.Parse(src);
            img.SetPixel(1, 1, 200);
            NetpbmWriter.Write(img, dst);

            var reloaded = NetpbmParser.Parse(dst);
            Assert.Equal(200, reloaded.GetPixel(1, 1));
        }
        finally
        {
            File.Delete(src);
            if (File.Exists(dst)) File.Delete(dst);
        }
    }

    // -------------------------------------------------------------------------
    // PBM SetPixel tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixel_PBM_UpdatesInMemory()
    {
        var pbm = "P1\n3 1\n0 0 0\n";
        var path = WriteTempFile(pbm, ".pbm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.SetPixel(0, 0, 1);
            Assert.Equal(1, img.GetPixel(0, 0));
            Assert.Equal(0, img.GetPixel(0, 1));
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void SetPixel_PBM_InvalidValue_ThrowsArgumentOutOfRange()
    {
        var pbm = "P1\n2 1\n0 0\n";
        var path = WriteTempFile(pbm, ".pbm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<ArgumentOutOfRangeException>(() => img.SetPixel(0, 0, 2));
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Cross-format guards
    // -------------------------------------------------------------------------

    [Fact]
    public void SetPixelColor_OnPGM_ThrowsInvalidOperation()
    {
        var pgm = "P2\n2 1\n255\n0 0\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<InvalidOperationException>(() => img.SetPixelColor(0, 0, 0, 0, 0));
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void SetPixel_OnPPM_ThrowsInvalidOperation()
    {
        var ppm = "P3\n2 1\n255\n0 0 0  0 0 0\n";
        var path = WriteTempFile(ppm, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<InvalidOperationException>(() => img.SetPixel(0, 0, 0));
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    private static string WriteTempFile(string content, string ext)
    {
        var path = Path.GetTempFileName() + ext;
        File.WriteAllText(path, content);
        return path;
    }
}
