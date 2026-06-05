// Example: Merge two PGM images side-by-side and adjust brightness
// Requires: FormatFactory.Netpbm NuGet package (commercial .NET track)
//
// Usage:
//   var left = new NetpbmImage { Format = PGM_P5, ... };
//   var merged = left.MergeHorizontal(right);
//   var bright = merged.AdjustBrightness(30);
//   bright.SaveToFile("output.pgm");

using System;
using FormatFactory.Netpbm;

// Create two small PGM images
var left = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P5,
    Width = 4, Height = 4, MaxValue = 255,
    Pixels = new byte[]
    {
         50, 100, 150, 200,
         50, 100, 150, 200,
         50, 100, 150, 200,
         50, 100, 150, 200,
    }
};

var right = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P5,
    Width = 4, Height = 4, MaxValue = 255,
    Pixels = new byte[]
    {
        200, 150, 100,  50,
        200, 150, 100,  50,
        200, 150, 100,  50,
        200, 150, 100,  50,
    }
};

Console.WriteLine($"Left:  {left.Width}x{left.Height}");
Console.WriteLine($"Right: {right.Width}x{right.Height}");

// Merge horizontally
var merged = left.MergeHorizontal(right);
Console.WriteLine($"Merged: {merged.Width}x{merged.Height}");

// Adjust brightness (+30)
var bright = merged.AdjustBrightness(30);
Console.WriteLine($"Brightness adjusted: +30");

// Save to file
bright.SaveToFile("merged-bright.pgm");
Console.WriteLine("Saved to merged-bright.pgm");

// Also demonstrate negative brightness (darken)
var dark = merged.AdjustBrightness(-50);
dark.SaveToFile("merged-dark.pgm");
Console.WriteLine("Saved to merged-dark.pgm");
