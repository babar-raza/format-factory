// R86 Train I: Binary write tests for P4/P5/P6
// Tests binary round-trip: write binary → parse → verify pixels match

using FormatFactory.Netpbm;
using Xunit;
using System.IO;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmBinaryWriteTests
{
    // === P4 Binary PBM ===

    [Fact]
    public void WriteBinaryPbm_RoundTrip_PixelsPreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 3,
            Height = 2,
            Pixels = new byte[] { 1, 0, 1, 0, 1, 0 },
            Comments = { "binary pbm test" }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Equal(3, parsed.Width);
            Assert.Equal(2, parsed.Height);
            Assert.Equal(image.Pixels.Length, parsed.Pixels.Length);
            for (int i = 0; i < image.Pixels.Length; i++)
                Assert.Equal(image.Pixels[i], parsed.Pixels[i]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void WriteBinaryPbm_8PixelWidth_RowAlignmentCorrect()
    {
        // 8 pixels wide = exactly 1 byte per row, no padding
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 8,
            Height = 1,
            Pixels = new byte[] { 1, 0, 1, 0, 1, 0, 1, 0 }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Equal(8, parsed.Width);
            for (int i = 0; i < 8; i++)
                Assert.Equal(image.Pixels[i], parsed.Pixels[i]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void WriteBinaryPbm_CommentsPreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P4,
            Width = 1,
            Height = 1,
            Pixels = new byte[] { 1 },
            Comments = { "test comment" }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Contains("test comment", parsed.Comments);
        }
        finally { File.Delete(path); }
    }

    // === P5 Binary PGM ===

    [Fact]
    public void WriteBinaryPgm_RoundTrip_PixelsPreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2,
            Height = 2,
            MaxValue = 255,
            Pixels = new byte[] { 0, 128, 64, 255 }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Equal(2, parsed.Width);
            Assert.Equal(2, parsed.Height);
            Assert.Equal(255, parsed.MaxValue);
            for (int i = 0; i < 4; i++)
                Assert.Equal(image.Pixels[i], parsed.Pixels[i]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void WriteBinaryPgm_MaxValuePreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1,
            Height = 1,
            MaxValue = 200,
            Pixels = new byte[] { 100 }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Equal(200, parsed.MaxValue);
        }
        finally { File.Delete(path); }
    }

    // === P6 Binary PPM ===

    [Fact]
    public void WriteBinaryPpm_RoundTrip_ChannelsPreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 2,
            Height = 1,
            MaxValue = 255,
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 0, 255 },
            BlueChannel = new byte[] { 128, 64 }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Equal(2, parsed.Width);
            Assert.Equal(1, parsed.Height);
            Assert.Equal(255, parsed.RedChannel![0]);
            Assert.Equal(0, parsed.RedChannel[1]);
            Assert.Equal(0, parsed.GreenChannel![0]);
            Assert.Equal(255, parsed.GreenChannel[1]);
            Assert.Equal(128, parsed.BlueChannel![0]);
            Assert.Equal(64, parsed.BlueChannel[1]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void WriteBinaryPpm_MissingChannels_Throws()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1,
            Height = 1,
            MaxValue = 255
        };
        Assert.Throws<NetpbmException>(() => NetpbmWriter.ToBinaryBytes(image));
    }

    [Fact]
    public void WriteBinaryPpm_CommentsPreserved()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P6,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            RedChannel = new byte[] { 100 },
            GreenChannel = new byte[] { 150 },
            BlueChannel = new byte[] { 200 },
            Comments = { "ppm binary test" }
        };
        var path = Path.GetTempFileName();
        try
        {
            NetpbmWriter.Write(image, path);
            var parsed = NetpbmParser.Parse(path);
            Assert.Contains("ppm binary test", parsed.Comments);
        }
        finally { File.Delete(path); }
    }

    // === ToBinaryBytes direct API ===

    [Fact]
    public void ToBinaryBytes_PgmImage_ProducesValidBytes()
    {
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 1,
            Height = 1,
            MaxValue = 255,
            Pixels = new byte[] { 42 }
        };
        byte[] bytes = NetpbmWriter.ToBinaryBytes(image);
        // Header should start with "P5\n"
        Assert.True(bytes.Length > 5);
        Assert.Equal((byte)'P', bytes[0]);
        Assert.Equal((byte)'5', bytes[1]);
    }

    [Fact]
    public void ToBinaryBytes_PbmP1Image_ProducesBinaryOutput()
    {
        // Even a P1 image should produce P4 binary output via ToBinaryBytes
        var image = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 1,
            Height = 1,
            Pixels = new byte[] { 1 }
        };
        byte[] bytes = NetpbmWriter.ToBinaryBytes(image);
        Assert.Equal((byte)'P', bytes[0]);
        Assert.Equal((byte)'4', bytes[1]);
    }
}
