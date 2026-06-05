// Example: Netpbm MergeVertical + AdjustContrast
// Demonstrates merging two PGM images vertically and adjusting contrast.

using FormatFactory.Netpbm;

// Create two grayscale images
var dark = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2,
    Width = 4, Height = 2, MaxValue = 255,
    Pixels = new byte[] { 50, 50, 50, 50, 50, 50, 50, 50 }
};

var bright = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P2,
    Width = 4, Height = 2, MaxValue = 255,
    Pixels = new byte[] { 200, 200, 200, 200, 200, 200, 200, 200 }
};

// Merge vertically (dark on top, bright on bottom)
var merged = dark.MergeVertical(bright);
Console.WriteLine($"Merged: {merged.Width}x{merged.Height}");

// Increase contrast by factor of 1.5
var highContrast = merged.AdjustContrast(1.5);
Console.WriteLine($"High contrast: {highContrast.Width}x{highContrast.Height}");
Console.WriteLine($"Top-left pixel: {highContrast.Pixels[0]} (was 50)");
Console.WriteLine($"Bottom-right pixel: {highContrast.Pixels[^1]} (was 200)");
