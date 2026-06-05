// R98 Train N: Netpbm .NET SaveToFile for Edit Persistence
// Governed skill: /add-same-format-writer-feature
// Ledger: R98-GOVERNED-DOTNET-NETPBM-SAVETOFILE-001
// Priority: 2 (same-format save after edits — core product value)

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR98SaveToFileTests
{
    [Fact]
    public void SaveToFile_PgmAscii_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30, 40, 50, 60 },
        };
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var content = File.ReadAllText(tmp);
            Assert.StartsWith("P2", content);
            Assert.Contains("3 2", content);
            Assert.Contains("255", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_PgmBinary_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P5,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 0, 128, 64, 255 },
        };
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var bytes = File.ReadAllBytes(tmp);
            // P5 header starts with "P5"
            Assert.Equal((byte)'P', bytes[0]);
            Assert.Equal((byte)'5', bytes[1]);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_PbmAscii_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PBM_P1,
            Width = 2, Height = 2, MaxValue = 1,
            Pixels = new byte[] { 0, 1, 1, 0 },
        };
        var tmp = Path.GetTempFileName() + ".pbm";
        try
        {
            img.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.StartsWith("P1", content);
            Assert.Contains("2 2", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_PpmAscii_Roundtrip()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3,
            Width = 2, Height = 1, MaxValue = 255,
            Pixels = Array.Empty<byte>(),
            RedChannel = new byte[] { 255, 0 },
            GreenChannel = new byte[] { 0, 255 },
            BlueChannel = new byte[] { 0, 0 },
        };
        var tmp = Path.GetTempFileName() + ".ppm";
        try
        {
            img.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.StartsWith("P3", content);
            Assert.Contains("255", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_AfterSetPixel_PersistsEdit()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 2, Height = 2, MaxValue = 255,
            Pixels = new byte[] { 0, 0, 0, 0 },
        };
        img.SetPixel(0, 1, 200);
        img.SetPixel(1, 0, 100);
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("200", content);
            Assert.Contains("100", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_AfterFlipHorizontal_PersistsTransform()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 3, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 10, 20, 30 },
        };
        img.FlipHorizontal();
        Assert.Equal(30, img.GetPixel(0, 0));
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("30", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_AfterInvert_PersistsTransform()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 100 },
        };
        img.Invert();
        Assert.Equal(155, img.GetPixel(0, 0));
        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp);
            var content = File.ReadAllText(tmp);
            Assert.Contains("155", content);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }

    [Fact]
    public void SaveToFile_CloneThenSave_IndependentFiles()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 42 },
        };
        var clone = img.Clone();
        clone.SetPixel(0, 0, 99);

        var tmp1 = Path.GetTempFileName() + ".pgm";
        var tmp2 = Path.GetTempFileName() + ".pgm";
        try
        {
            img.SaveToFile(tmp1);
            clone.SaveToFile(tmp2);
            var c1 = File.ReadAllText(tmp1);
            var c2 = File.ReadAllText(tmp2);
            Assert.Contains("42", c1);
            Assert.Contains("99", c2);
            Assert.DoesNotContain("99", c1);
        }
        finally
        {
            if (File.Exists(tmp1)) File.Delete(tmp1);
            if (File.Exists(tmp2)) File.Delete(tmp2);
        }
    }

    [Fact]
    public void SaveToFile_NullPath_ThrowsArgumentException()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 0 },
        };
        Assert.Throws<ArgumentException>(() => img.SaveToFile(null!));
    }

    [Fact]
    public void SaveToFile_EmptyPath_ThrowsArgumentException()
    {
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PGM_P2,
            Width = 1, Height = 1, MaxValue = 255,
            Pixels = new byte[] { 0 },
        };
        Assert.Throws<ArgumentException>(() => img.SaveToFile(""));
    }
}
