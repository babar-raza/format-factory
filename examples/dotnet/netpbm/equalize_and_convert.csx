// Netpbm Equalize + ConvertFormat Example — FormatFactory.Netpbm
// Demonstrates: Create a PGM image, equalize histogram, convert ASCII to binary format.

#r "../../../src/net/netpbm/bin/Debug/net10.0/FormatFactory.Netpbm.dll"
using FormatFactory.Netpbm;

// 1. Create a gradient PGM image (8x8, values 0-252)
var pixels = new byte[64];
for (int i = 0; i < 64; i++) pixels[i] = (byte)(i * 4);
var img = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2,
    Width = 8,
    Height = 8,
    MaxValue = 255,
    Pixels = pixels
};
Console.WriteLine($"Original: {img.Format}, {img.Width}x{img.Height}");

// 2. Equalize the histogram — spreads pixel values across full range
var equalized = img.Equalize();
Console.WriteLine($"Equalized: min={equalized.Pixels.Min()}, max={equalized.Pixels.Max()}");

// 3. Convert from ASCII (P2) to binary (P5) format
var binary = equalized.ConvertFormat(NetpbmFormat.PGM_P5);
Console.WriteLine($"Converted: {binary.Format}");

// 4. Chain operations: crop → overlay → equalize → convert
var bg = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2, Width = 10, Height = 10, MaxValue = 255,
    Pixels = Enumerable.Repeat((byte)50, 100).ToArray()
};
var fg = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2, Width = 4, Height = 4, MaxValue = 255,
    Pixels = Enumerable.Repeat((byte)220, 16).ToArray()
};
var result = bg.Crop(0, 0, 6, 6).Overlay(fg, 1, 1).Equalize().ConvertFormat(NetpbmFormat.PGM_P5);
Console.WriteLine($"Pipeline result: {result.Format}, {result.Width}x{result.Height}");
