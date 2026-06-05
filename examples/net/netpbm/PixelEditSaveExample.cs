// Netpbm .NET Pixel Edit + Save Example
// Creates a PGM image, edits pixels, saves, and demonstrates Rotate180.
//
// This example shows the Format Factory Netpbm .NET object model workflow:
//   1. Create image from scratch
//   2. Edit individual pixels
//   3. Apply transforms (Rotate180)
//   4. Save to file

using FormatFactory.Netpbm;

// Step 1: Create a 4x4 PGM grayscale image
var img = new NetpbmImage
{
    Format = NetpbmFormat.PGM_P5,
    Width = 4,
    Height = 4,
    MaxValue = 255,
    Pixels = new byte[16],
};

// Step 2: Draw a gradient pattern
for (int r = 0; r < img.Height; r++)
{
    for (int c = 0; c < img.Width; c++)
    {
        img.SetPixel(r, c, (byte)(r * 64 + c * 16));
    }
}

Console.WriteLine($"Image: {img.Width}x{img.Height} {img.Format}");
Console.WriteLine($"Pixel (0,0): {img.GetPixel(0, 0)}");
Console.WriteLine($"Pixel (3,3): {img.GetPixel(3, 3)}");

// Step 3: Save original
img.SaveToFile("gradient.pgm");
Console.WriteLine("Saved gradient.pgm");

// Step 4: Rotate 180 degrees
var rotated = img.Rotate180();
Console.WriteLine($"Rotated: {rotated.Width}x{rotated.Height}");
Console.WriteLine($"Rotated pixel (0,0): {rotated.GetPixel(0, 0)}");

// Step 5: Save rotated version
rotated.SaveToFile("gradient-rotated.pgm");
Console.WriteLine("Saved gradient-rotated.pgm");

// Cleanup
File.Delete("gradient.pgm");
File.Delete("gradient-rotated.pgm");
Console.WriteLine("Done.");
