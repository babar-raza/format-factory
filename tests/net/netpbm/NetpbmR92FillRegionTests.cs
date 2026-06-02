// R92 Train N: Netpbm .NET FillRegion Tests
// API: FillRegion(top, left, regionHeight, regionWidth, value/r/g/b)
// Sprint: FORMAT-FACTORY-R92-DECLARATION-MATERIALIZER-WORK-ITEM-GRADING-ACCELERATION-POC-MAINSTREAM-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR92FillRegionTests
{
    private static string WriteTempFile(string content, string ext)
    {
        var path = Path.GetTempFileName() + ext;
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // PGM FillRegion tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_PGM_FillsSpecifiedRegion()
    {
        var pgm = "P2\n4 4\n255\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.FillRegion(1, 1, 2, 2, value: 200);
            // Filled pixels
            Assert.Equal(200, img.GetPixel(1, 1));
            Assert.Equal(200, img.GetPixel(1, 2));
            Assert.Equal(200, img.GetPixel(2, 1));
            Assert.Equal(200, img.GetPixel(2, 2));
            // Untouched pixels
            Assert.Equal(0, img.GetPixel(0, 0));
            Assert.Equal(0, img.GetPixel(3, 3));
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void FillRegion_PGM_WholeImageFill()
    {
        var pgm = "P2\n3 3\n255\n10 20 30\n40 50 60\n70 80 90\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.FillRegion(0, 0, 3, 3, value: 128);
            for (int r = 0; r < 3; r++)
                for (int c = 0; c < 3; c++)
                    Assert.Equal(128, img.GetPixel(r, c));
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void FillRegion_PBM_FillsWithBinaryValue()
    {
        var pbm = "P1\n4 4\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";
        var path = WriteTempFile(pbm, ".pbm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.FillRegion(0, 0, 2, 4, value: 1);
            // First two rows all black
            for (int c = 0; c < 4; c++)
                Assert.Equal(1, img.GetPixel(0, c));
            // Remaining rows untouched
            Assert.Equal(0, img.GetPixel(2, 0));
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // PPM FillRegion tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_PPM_FillsRegionWithColor()
    {
        var ppm = "P3\n4 4\n255\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n0 0 0  0 0 0  0 0 0  0 0 0\n";
        var path = WriteTempFile(ppm, ".ppm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.FillRegion(0, 0, 2, 2, r: 255, g: 128, b: 64);
            var (pr, pg, pb) = img.GetPixelColor(0, 0);
            Assert.Equal(255, pr);
            Assert.Equal(128, pg);
            Assert.Equal(64, pb);
            // Outside region untouched
            var (ur, ug, ub) = img.GetPixelColor(3, 3);
            Assert.Equal(0, ur);
            Assert.Equal(0, ug);
            Assert.Equal(0, ub);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void FillRegion_ThrowsIfRegionExceedsBounds()
    {
        var pgm = "P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                img.FillRegion(2, 2, 2, 2, value: 100)); // exceeds bounds
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void FillRegion_PBM_ThrowsForInvalidFillValue()
    {
        var pbm = "P1\n3 3\n0 0 0\n0 0 0\n0 0 0\n";
        var path = WriteTempFile(pbm, ".pbm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                img.FillRegion(0, 0, 2, 2, value: 5)); // PBM only allows 0 or 1
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void FillRegion_SinglePixel()
    {
        var pgm = "P2\n5 5\n255\n" + string.Join("\n", new string[5].Select(_ => "10 10 10 10 10")) + "\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            img.FillRegion(2, 3, 1, 1, value: 99);
            Assert.Equal(99, img.GetPixel(2, 3));
            Assert.Equal(10, img.GetPixel(2, 2)); // neighbor untouched
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void FillRegion_ThrowsForNegativeTop()
    {
        var pgm = "P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n";
        var path = WriteTempFile(pgm, ".pgm");
        try
        {
            var img = NetpbmParser.Parse(path);
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                img.FillRegion(-1, 0, 2, 2, value: 100));
        }
        finally { File.Delete(path); }
    }
}
