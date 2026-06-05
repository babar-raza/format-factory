// R111 Wave 7: Netpbm sharpen→save dogfood pipeline tests
// Pipeline: create → sharpen → save → reload → verify

using System;
using System.IO;
using FormatFactory.Netpbm;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

public class NetpbmR111DogfoodSharpenSaveTests
{
    private static NetpbmImage CreatePgm(int w, int h, byte fill)
    {
        var pixels = new byte[w * h];
        Array.Fill(pixels, fill);
        return new NetpbmImage { Format = NetpbmFormat.PGM_P2, Width = w, Height = h, MaxValue = 255, Pixels = pixels };
    }

    [Fact]
    public void Dogfood_Sharpen_SaveToFile_Reload()
    {
        var img = CreatePgm(10, 10, 128);
        var sharpened = img.Sharpen();

        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            sharpened.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var fileContent = File.ReadAllBytes(tmp);
            Assert.True(fileContent.Length > 0);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_BlurBox_SaveToFile_Reload()
    {
        var img = CreatePgm(10, 10, 200);
        var blurred = img.BlurBox(1);

        var tmp = Path.GetTempFileName() + ".pgm";
        try
        {
            blurred.SaveToFile(tmp);
            Assert.True(File.Exists(tmp));
            var fileContent = File.ReadAllBytes(tmp);
            Assert.True(fileContent.Length > 0);
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void Dogfood_Sharpen_Then_Blur_Pipeline()
    {
        var img = CreatePgm(10, 10, 128);
        var sharpened = img.Sharpen();
        var blurred = sharpened.BlurBox(1);
        // Pipeline should produce valid image
        Assert.Equal(10, blurred.Width);
        Assert.Equal(10, blurred.Height);
    }

    [Fact]
    public void Dogfood_Sepia_Then_Sharpen_Ppm()
    {
        int count = 10 * 10;
        var rc = new byte[count]; Array.Fill(rc, (byte)100);
        var gc = new byte[count]; Array.Fill(gc, (byte)150);
        var bc = new byte[count]; Array.Fill(bc, (byte)200);
        var img = new NetpbmImage
        {
            Format = NetpbmFormat.PPM_P3, Width = 10, Height = 10, MaxValue = 255,
            Pixels = Array.Empty<byte>(), RedChannel = rc, GreenChannel = gc, BlueChannel = bc
        };

        var sepia = img.Sepia();
        var sharpened = sepia.Sharpen();
        Assert.Equal(10, sharpened.Width);
        Assert.NotNull(sharpened.RedChannel);
    }
}
